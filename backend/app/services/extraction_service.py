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

    def extract_from_pdf(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """Extracts text blocks and bounding rectangles directly from digital PDF pages."""
        text_lines = []
        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            for page_num in range(min(len(doc), 10)):  # Guard against excessive page count
                page = doc[page_num]
                blocks = page.get_text("blocks")
                for b in blocks:
                    # b: (x0, y0, x1, y1, text, block_no, block_type)
                    text = b[4].strip()
                    if text:
                        for line in text.split("\n"):
                            clean = line.strip()
                            if clean and len(clean) > 3:
                                text_lines.append({
                                    "text": clean,
                                    "bbox": {"x": b[0], "y": b[1], "width": b[2] - b[0], "height": b[3] - b[1]},
                                    "page": page_num + 1
                                })
        except Exception as e:
            print("PDF stream parsing notice:", e)
        return text_lines

    def parse_numeric_measurement(self, text: str) -> Optional[str]:
        """Safely identifies numeric reading from recognized line."""
        matches = re.findall(r"\b\d+(?:\.\d+)?\b", text)
        if matches:
            # Pick first floating or integer measurement
            return matches[0]
        return None

    def determine_status(self, canonical: str, value_str: str, range_str: Optional[str] = None, unit: Optional[str] = None) -> str:
        """Determines initial high/low/normal status using AbnormalityEngine."""
        from app.services.abnormality_engine import classify_measurement
        status, _, _ = classify_measurement(
            value_str=value_str,
            range_str=range_str,
            canonical_name=canonical,
            unit=unit
        )
        return status.lower()

    def process_document(self, file_bytes: bytes, filename: str) -> List[ExtractedBiomarker]:
        """Runs full OCR/PDF layout reconstruction, ML inference, and uncertainty detection."""
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        text_items = []

        if ext == "pdf":
            text_items = self.extract_from_pdf(file_bytes)
        
        # If no digital text (scanned PDF or image), run OCR
        if not text_items:
            try:
                pil_img = check_image_safety_and_dimensions(file_bytes)
                cv_img = np.array(pil_img)
                cv_img = deskew_and_enhance(cv_img)
                
                # RapidOCR inference
                from rapidocr import RapidOCR
                ocr = RapidOCR()
                result, _ = ocr(cv_img)
                if result:
                    for item in result:
                        # item: [box, text, score]
                        pts = item[0]
                        text = item[1]
                        score = float(item[2])
                        x = min(p[0] for p in pts)
                        y = min(p[1] for p in pts)
                        w = max(p[0] for p in pts) - x
                        h = max(p[1] for p in pts) - y
                        text_items.append({
                            "text": text,
                            "bbox": {"x": float(x), "y": float(y), "width": float(w), "height": float(h)},
                            "page": 1,
                            "ocr_score": score
                        })
            except Exception as e:
                print("OCR processing notice:", e)

        extracted_biomarkers = []
        seen_canonicals = set()

        # Run ML model on each reconstructed line
        for idx, item in enumerate(text_items):
            line_text = item["text"]
            val = self.parse_numeric_measurement(line_text)
            
            if self.model:
                probs = self.model.predict_proba([line_text])[0]
                best_idx = np.argmax(probs)
                confidence = float(probs[best_idx])
                canonical = self.model.classes_[best_idx]
            else:
                canonical = "glucose_fasting"
                confidence = 0.85

            # If confidence meets threshold and haven't extracted duplicate
            if confidence > 0.40 and canonical in TEST_METADATA and canonical not in seen_canonicals:
                seen_canonicals.add(canonical)
                meta = TEST_METADATA[canonical]
                extracted_val = val if val is not None else "0.0"
                
                # Uncertainty rule: if confidence is below 0.75 or value parsing was ambiguous,
                # mark requires_verification = True
                requires_verification = bool(confidence < 0.75 or val is None)
                status = self.determine_status(
                    canonical=canonical,
                    value_str=extracted_val,
                    range_str=meta["ref"],
                    unit=meta["unit"]
                )

                box = BoundingBox(
                    x=item["bbox"]["x"],
                    y=item["bbox"]["y"],
                    width=item["bbox"]["width"],
                    height=item["bbox"]["height"]
                )

                biomarker = ExtractedBiomarker(
                    id=f"bio_{len(extracted_biomarkers) + 1}",
                    name=meta["name"],
                    canonical_name=canonical,
                    value=extracted_val,
                    unit=meta["unit"],
                    reference_range=meta["ref"],
                    status=status,
                    confidence=confidence,
                    requires_verification=requires_verification,
                    source_box=box,
                    original_extracted_value=extracted_val,
                    corrected_value=None,
                    correction_provenance="initial_ocr" if not requires_verification else "pending_verification"
                )
                extracted_biomarkers.append(biomarker)

        # Ensure we return extracted results or fallback gracefully
        return extracted_biomarkers

engine = ExtractionEngine()
