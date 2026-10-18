"""
Extraction Service for Simplifier 2.0.
Performs PDF text extraction, OCR on images, table reconstruction, and ML inference.
"""

import os
import re
import joblib
import numpy as np
from typing import List, Dict, Any, Optional
import pymupdf  # PyMuPDF
from PIL import Image
import io
from functools import lru_cache

@lru_cache(maxsize=1)
def get_ocr_runtime():
    from rapidocr import RapidOCR
    return RapidOCR()


from app.schemas.report import ExtractedBiomarker, BoundingBox
from app.services.image_processor import check_image_safety_and_dimensions, deskew_and_enhance, assess_image_quality

# Canonical test metadata lookup
TEST_METADATA = {
    "glucose_fasting": {"name": "Fasting Blood Glucose", "unit": "mg/dL", "ref": "70 - 99 mg/dL"},
    "hba1c": {"name": "HbA1c (Glycated Hemoglobin)", "unit": "%", "ref": "< 5.7 %"},
    "creatinine_serum": {"name": "Serum Creatinine", "unit": "mg/dL", "ref": "0.7 - 1.3 mg/dL"},
    "bun": {"name": "Blood Urea Nitrogen", "unit": "mg/dL", "ref": "7 - 20 mg/dL"},
    "cholesterol_total": {"name": "Total Cholesterol", "unit": "mg/dL", "ref": "< 200 mg/dL"},
    "triglycerides": {"name": "Triglycerides", "unit": "mg/dL", "ref": "< 150 mg/dL"},
    "cholesterol_hdl": {"name": "HDL Cholesterol", "unit": "mg/dL", "ref": "> 40 mg/dL"},
    "cholesterol_ldl": {"name": "LDL Cholesterol", "unit": "mg/dL", "ref": "< 100 mg/dL"},
    "hemoglobin": {"name": "Hemoglobin", "unit": "g/dL", "ref": "12.0 - 17.5 g/dL"},
    "wbc": {"name": "White Blood Cell Count", "unit": "10^3/uL", "ref": "4.0 - 11.0 10^3/uL"},
    "platelets": {"name": "Platelet Count", "unit": "10^3/uL", "ref": "150 - 450 10^3/uL"},
    "rbc": {"name": "Red Blood Cell Count", "unit": "mil/uL", "ref": "4.2 - 5.8 mil/uL"},
    "tsh": {"name": "TSH (Thyroid Stimulating Hormone)", "unit": "uIU/mL", "ref": "0.4 - 4.2 uIU/mL"},
    "vitamin_d": {"name": "Vitamin D (25-OH)", "unit": "ng/mL", "ref": "30 - 100 ng/mL"},
    "vitamin_b12": {"name": "Vitamin B12", "unit": "pg/mL", "ref": "200 - 900 pg/mL"},
    "calcium_serum": {"name": "Serum Calcium", "unit": "mg/dL", "ref": "8.5 - 10.5 mg/dL"},
}

class ExtractionEngine:
    def __init__(self, model_path: str = None):
        if not model_path:
            # Look in ml/models/ or backend relative
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml/models"))
            model_path = os.path.join(base_dir, "biomarker_extractor_v1.joblib")
            
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            self.model = None

    def rows(self, items):
        """Reconstruct a table row from columns sharing the same vertical baseline."""
        groups=[]
        for item in sorted(items,key=lambda item:(item["page"],item["bbox"]["y"],item["bbox"]["x"])):
            target=next((row for row in reversed(groups) if row[0]["page"]==item["page"] and abs(row[0]["bbox"]["y"]-item["bbox"]["y"]) < max(3,item["bbox"]["height"]*.45)),None)
            if target is None: groups.append([item])
            else: target.append(item)
        result=[]
        for group in groups:
            group.sort(key=lambda item:item["bbox"]["x"])
            left=min(item["bbox"]["x"] for item in group);top=min(item["bbox"]["y"] for item in group)
            right=max(item["bbox"]["x"]+item["bbox"]["width"] for item in group);bottom=max(item["bbox"]["y"]+item["bbox"]["height"] for item in group)
            result.append({"text":" ".join(item["text"] for item in group),"page":group[0]["page"],"bbox":{"x":left,"y":top,"width":right-left,"height":bottom-top},"ocr_score":min(item.get("ocr_score",1) for item in group)})
        return result

    def pdf_items(self,page,page_number):
        return [{"text":word[4],"page":page_number,"bbox":{"x":word[0],"y":word[1],"width":word[2]-word[0],"height":word[3]-word[1]}} for word in page.get_text("words")]

    def extract_from_pdf(self,pdf_bytes):
        try:
            with pymupdf.open(stream=pdf_bytes,filetype="pdf") as doc:
                if len(doc)>10 or doc.is_encrypted: raise ValueError("Use an unencrypted PDF with at most 10 pages.")
                return self.rows([item for number,page in enumerate(doc,1) for item in self.pdf_items(page,number)])
        except (RuntimeError,pymupdf.FileDataError): raise ValueError("The PDF could not be read.") from None

    def ocr_items(self,image,page_number):
        # RapidOCR 3 returns an object with boxes/txts/scores, not the older tuple API.
        output=get_ocr_runtime()(image)
        if output is None or output.txts is None: return []
        result=[]
        for points,text,score in zip(output.boxes,output.txts,output.scores):
            x=float(min(point[0] for point in points));y=float(min(point[1] for point in points))
            result.append({"text":text,"page":page_number,"ocr_score":float(score),"bbox":{"x":x,"y":y,"width":float(max(point[0] for point in points))-x,"height":float(max(point[1] for point in points))-y}})
        return result

    def parse_numeric_measurement(self,text):
        match=re.search(r"(?<![A-Za-z0-9])[-+]?\d+(?:\.\d+)?(?![A-Za-z0-9])",text)
        return match.group(0) if match else None

    def determine_status(self,canonical,value_str,range_str=None,unit=None):
        from app.services.abnormality_engine import classify_measurement
        return classify_measurement(value_str,range_str,canonical_name=canonical,unit=unit)[0].lower()

    def process_document(self,file_bytes,filename):
        if self.model is None: raise ValueError("The trained extraction model is unavailable.")
        items=[]
        if filename.lower().endswith('.pdf'):
            try:
                with pymupdf.open(stream=file_bytes,filetype='pdf') as doc:
                    if doc.is_encrypted or not 1 <= len(doc) <= 10: raise ValueError("Use an unencrypted PDF with 1–10 pages.")
                    for number,page in enumerate(doc,1):
                        digital=self.pdf_items(page,number)
                        if len(digital)>=3: items.extend(digital)
                        else:
                            if page.rect.width * page.rect.height * 2.5**2 > 25_000_000: raise ValueError("PDF page exceeds the safe raster size.")
                            pix=page.get_pixmap(dpi=180,alpha=False)
                            image=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)
                            items.extend(self.ocr_items(image,number))
            except (RuntimeError,pymupdf.FileDataError): raise ValueError("The PDF is corrupted or unsupported.") from None
        else:
            image=check_image_safety_and_dimensions(file_bytes).convert('RGB')
            items=self.ocr_items(deskew_and_enhance(np.asarray(image)),1)
        unit_pattern=r"(?:mmol/L|[uµμ]mol/L|mg/dL|mg/L|g/dL|g/L|ng/mL|pg/mL|[uµμ]IU/mL|mIU/L|fL|pg|(?:[x×]?\s*10\^?[369]/[uµμ]L)|(?:[x×]?\s*10\^?[369]/L)|mil/[uµμ]L|cells?/[uµμ]L|/cumm|/mm3|%)"
        value_pattern=r"(?<![A-Za-z0-9])(?P<value>[<>]=?\s*[-+]?\d+(?:\.\d+)?|[-+]?\d+(?:\.\d+)?)\s*(?P<unit>"+unit_pattern+r")"
        extracted=[];seen=set()
        for row in self.rows(items):
            text=row['text'];quantitative=re.search(value_pattern,text,re.IGNORECASE)
            qualitative=re.search(r"\b(?:non[- ]?reactive|negative|positive|reactive|not detected|trace)\b",text,re.IGNORECASE)
            measurement=quantitative or qualitative
            if measurement is None: continue
            name=text[:measurement.start()].strip(' :|')
            if not name or name.lower() in ['result','results','reference range','normal range']: continue
            probabilities=self.model.predict_proba([text])[0];index=int(np.argmax(probabilities));confidence=float(probabilities[index]);canonical=str(self.model.classes_[index])
            if canonical not in TEST_METADATA or confidence < .55: continue
            value=measurement.group('value').strip() if quantitative else measurement.group(0)
            unit=measurement.group('unit') if quantitative else ''
            tail=text[measurement.end():]
            interval=re.search(r"(?:[-+]?\d+(?:\.\d+)?\s*[-–]\s*[-+]?\d+(?:\.\d+)?|[<>]=?\s*[-+]?\d+(?:\.\d+)?)",tail)
            reference=interval.group(0) if interval else ''
            ambiguous = bool(re.search(r'male|female|child|adult|pregnan|age|year', tail, re.I)) or len(re.findall(r'\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?', tail))>1
            if ambiguous: reference=tail.strip(' ()')
            uncertain=bool(ambiguous or confidence<.75 or row.get('ocr_score',1)<.9 or not reference or not quantitative or value.startswith(('<','>')))
            status='needs_review' if uncertain else self.determine_status(canonical,value,reference,unit)
            identity=(row['page'],text)
            if identity in seen:continue
            seen.add(identity)
            extracted.append(ExtractedBiomarker(id=f'bio_{len(extracted)+1}',name=name,canonical_name=canonical,value=value,unit=unit,reference_range=reference,status=status,confidence=confidence,requires_verification=uncertain,source_box=BoundingBox(**row['bbox']),source_page=row['page'],source_line=text,original_extracted_value=value,correction_provenance='pending_verification' if uncertain else 'source_extracted'))
        return extracted

engine = ExtractionEngine()
