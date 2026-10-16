"""
Professional Multilingual PDF Generator for Simplifier 2.0.
Generates publication-quality downloadable PDF summaries for medical lab reports
in English, Hindi (Devanagari), and Marathi (Devanagari).
Preserves exact clinical values, reference ranges, and doctor discussion points.
"""

import io
import re
import os
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph as ReportParagraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def Paragraph(text, style, *args, **kwargs):
    # Bundled Devanagari fonts lack Latin letters. Keep source names and units
    # readable with explicit Latin runs while preserving paragraph markup.
    if style.fontName.startswith("DevanagariFont"):
        parts = re.split(r"(<[^>]+>|&(?:#\d+|\w+);)", str(text))
        font = "Helvetica-Bold" if style.fontName.endswith("Bold") else "Helvetica"
        text = "".join(part if part.startswith(("<", "&")) else re.sub(r"[A-Za-z][A-Za-z0-9 /()._-]*", lambda match: f'<font name="{font}">{match.group(0)}</font>', part) for part in parts)
    return ReportParagraph(text, style, *args, **kwargs)


# Register Devanagari fonts
DEVANAGARI_FONT_REGISTERED = False
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"

def init_pdf_fonts():
    global DEVANAGARI_FONT_REGISTERED, FONT_REGULAR, FONT_BOLD, FONT_ITALIC
    if DEVANAGARI_FONT_REGISTERED:
        return

    # Check bundled Noto Sans Devanagari first
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static/fonts"))
    noto_reg = os.path.join(base_dir, "NotoSansDevanagari-Regular.ttf")
    noto_bold = os.path.join(base_dir, "NotoSansDevanagari-Bold.ttf")

    if os.path.exists(noto_reg) and os.path.exists(noto_bold):
        try:
            pdfmetrics.registerFont(TTFont('DevanagariFont', noto_reg))
            pdfmetrics.registerFont(TTFont('DevanagariFont-Bold', noto_bold))
            DEVANAGARI_FONT_REGISTERED = True
            return
        except Exception as e:
            print("Notice: Error loading bundled NotoSansDevanagari font:", e)

    # Windows fallback: Nirmala UI / Nirmala TTC
    nirmala_path = "C:/Windows/Fonts/Nirmala.ttc"
    if os.path.exists(nirmala_path):
        try:
            pdfmetrics.registerFont(TTFont('DevanagariFont', nirmala_path, subfontIndex=0))
            pdfmetrics.registerFont(TTFont('DevanagariFont-Bold', nirmala_path, subfontIndex=0))
            DEVANAGARI_FONT_REGISTERED = True
            return
        except Exception as e:
            print("Notice: Error loading Windows Nirmala font:", e)

    DEVANAGARI_FONT_REGISTERED = False

def generate_pdf_report(report_data: Dict[str, Any], lang: str = "en") -> bytes:
    """
    Generates a beautifully formatted multi-page PDF summarizing abnormal findings,
    reference ranges, patient context, clinician discussion points, and disclaimer
    in the requested language (en, hi, mr).
    """
    init_pdf_fonts()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    is_devanagari = lang in ["hi", "mr"] and DEVANAGARI_FONT_REGISTERED
    font_main = 'DevanagariFont' if is_devanagari else 'Helvetica'
    font_bold = 'DevanagariFont-Bold' if is_devanagari else 'Helvetica-Bold'
    font_italic = 'DevanagariFont' if is_devanagari else 'Helvetica-Oblique'

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#D24726')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName=font_main,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#62626A')
    )
    heading2_style = ParagraphStyle(
        'DocHeading2',
        parent=styles['Heading2'],
        fontName=font_bold,
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#D24726'),
        spaceBefore=10,
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName=font_main,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1C1C1E')
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName=font_main,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1C1C1E')
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#D24726')
    )
    disclaimer_style = ParagraphStyle(
        'DocDisclaimer',
        parent=styles['Italic'],
        fontName=font_italic,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#62626A')
    )
    alert_style = ParagraphStyle(
        'DocAlert',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#9E3624')
    )

    story = []

    # Localized Titles
    if lang == "hi":
        main_title = "SIMPLIFIER 2.0 — प्रयोगशाला स्वास्थ्य सारांश"
        doc_sub = "आपके डॉक्टर से परामर्श की तैयारी हेतु एक शांत, शैक्षिक व्याख्या।"
        sec_overview = "समग्र अवलोकन"
        sec_attention = "जिन बातों पर ध्यान देने की आवश्यकता है"
        sec_questions = "डॉक्टर से पूछने हेतु उपयोगी प्रश्न"
        col_test = "परीक्षण का नाम"
        col_val = "परिणाम"
        col_ref = "सामान्य सीमा"
        col_status = "स्थिति"
        all_normal_txt = "आपके सभी परीक्षण परिणाम सामान्य संदर्भ सीमाओं के भीतर हैं।"
    elif lang == "mr":
        main_title = "SIMPLIFIER 2.0 — प्रयोगशाळा आरोग्य सारांश"
        doc_sub = "डॉक्टरांशी सविस्तर चर्चेसाठी तयार केलेला सोपा, शैक्षणिक अहवाल."
        sec_overview = "एकूण सारांश"
        sec_attention = "कशावर लक्ष देणे आवश्यक आहे"
        sec_questions = "डॉक्टरांशी चर्चेसाठी महत्त्वाचे प्रश्न"
        col_test = "चाचणीचे नाव"
        col_val = "निकाल"
        col_ref = "संदर्भ मर्यादा"
        col_status = "स्थिती"
        all_normal_txt = "तुमचे सर्व निकाल सामान्य संदर्भ मर्यादेत संतुलित आहेत."
    else:
        main_title = "SIMPLIFIER 2.0 — Laboratory Health Summary"
        doc_sub = "A patient-friendly educational explanation prepared for physician discussion."
        sec_overview = "Overview"
        sec_attention = "Results Needing Attention"
        sec_questions = "Helpful Questions to Discuss With Your Doctor"
        col_test = "Test Name"
        col_val = "Result"
        col_ref = "Standard Range"
        col_status = "Status"
        all_normal_txt = "All tested values are within typical standard laboratory reference bounds."

    # Header
    story.append(Paragraph(main_title, title_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph(doc_sub, subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#D24726'), spaceAfter=10))

    provenance = f"Report ID: {report_data.get('report_id', '—')}"
    if report_data.get("is_synthetic_fixture"):
        provenance += " · DEMONSTRATION DATA"
    story.append(Paragraph(provenance, subtitle_style))
    story.append(Spacer(1, 8))

    # Urgent safety alert if present
    safety = report_data.get("safety_alert")
    if safety:
        story.append(Paragraph(f"⚠️ {safety.get('title')}: {safety.get('guidance')}", alert_style))
        story.append(Spacer(1, 8))

    # Overview
    story.append(Paragraph(sec_overview, heading2_style))
    summary_text = report_data.get("patient_summary", "Laboratory report overview.")
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 8))

    # Prioritized Findings Table
    story.append(Paragraph(sec_attention, heading2_style))
    attention_items = report_data.get("prioritized_attention", [])

    if attention_items:
        table_data = [[
            Paragraph(col_test, table_cell_bold),
            Paragraph(col_val, table_cell_bold),
            Paragraph(col_ref, table_cell_bold),
            Paragraph(col_status, table_cell_bold)
        ]]
        for item in attention_items:
            test_name = item.get("name", item.get("original_name", "Unknown"))
            val_str = item.get("value", "")
            ref_str = item.get("reference_range", "")
            status_str = item.get("status_label") or item.get("status", "").upper()

            table_data.append([
                Paragraph(test_name, table_cell_bold),
                Paragraph(val_str, table_cell_style),
                Paragraph(ref_str, table_cell_style),
                Paragraph(status_str, table_cell_style)
            ])
        t = Table(table_data, colWidths=[210, 110, 130, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFF3EE')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E5E8')),
        ]))
        story.append(t)
    else:
        story.append(Paragraph(all_normal_txt, body_style))

    story.append(Spacer(1, 10))

    # Patient History & Personal Baselines if present
    baselines = report_data.get("personal_baselines", [])
    hist_changes = report_data.get("historical_changes", [])
    if baselines or hist_changes:
        if lang == "hi":
            sec_hist = "आपका पिछला इतिहास एवं आधार रेखा"
        elif lang == "mr":
            sec_hist = "तुमचा मागील इतिहास आणि आधारभूत कल"
        else:
            sec_hist = "What Your History Adds"
        story.append(Paragraph(sec_hist, heading2_style))

        for base in baselines:
            base_txt = f"<b>{base.get('name')}:</b> {base.get('descriptive_summary')} <i>({base.get('relation_to_baseline')})</i>"
            story.append(Paragraph(base_txt, body_style))
            story.append(Spacer(1, 2))

        for ch in hist_changes:
            ch_txt = f"• {ch.get('name')}: {ch.get('concise_summary')}"
            story.append(Paragraph(ch_txt, body_style))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 6))

    # Patient Context / Insights if present
    insights = report_data.get("context_insights", [])
    if insights:
        if lang == "hi":
            story.append(Paragraph("आपके उत्तरों के आधार पर संदर्भ", heading2_style))
        elif lang == "mr":
            story.append(Paragraph("तुमच्या उत्तरांवर आधारित संदर्भ", heading2_style))
        else:
            story.append(Paragraph("Context from Your Responses", heading2_style))
        for ins in insights:
            story.append(Paragraph(f"• {ins}", body_style))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 6))

    # Doctor Questions
    doctor_questions = report_data.get("suggested_doctor_questions", [])
    if doctor_questions:
        story.append(Paragraph(sec_questions, heading2_style))
        for idx, q in enumerate(doctor_questions, 1):
            story.append(Paragraph(f"{idx}. {q}", body_style))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 8))

    # Excluded Unreliable Results note if any
    unreliable = report_data.get("unreliable_flagged_results", [])
    if unreliable:
        if lang == "hi":
            note_title = "नोट: कम स्पष्टता वाले परिणाम मुख्य व्याख्या से अलग रखे गए हैं"
        elif lang == "mr":
            note_title = "नोंद: अस्पष्ट निकालांचे विश्लेषण तात्पुरते वगळले आहे"
        else:
            note_title = "Excluded / Low-Confidence Optical Extractions"
        story.append(Paragraph(f"<b>{note_title}:</b>", body_style))
        for item in unreliable:
            item_name = item.get("name", "Unknown Assay")
            story.append(Paragraph(f"• {item_name}: {item.get('flag_reason')}", subtitle_style))
            story.append(Spacer(1, 1))
        story.append(Spacer(1, 6))

    within_range = report_data.get("within_range_results", [])
    if within_range:
        label = "Within-range results" if lang == "en" else "संदर्भ सीमा में परिणाम" if lang == "hi" else "संदर्भ मर्यादेतील निकाल"
        story.append(Paragraph(label, heading2_style))
        for item in within_range:
            story.append(Paragraph(f"{item.get('name')}: {item.get('value')} · {item.get('reference_range', '')}", body_style))
        story.append(Spacer(1, 8))

    # Medical Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#E5E5E8'), spaceBefore=8, spaceAfter=6))
    disclaimer_text = report_data.get("disclaimer", "Simplifier is an educational tool designed to assist patients in understanding their laboratory slips and preparing for consultations with medical professionals.")
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
