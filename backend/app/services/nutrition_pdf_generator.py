"""
Professional 7-Day Nutrition Plan PDF Generator for Simplifier 2.0.
Generates an elegant, beautifully formatted multi-page educational meal plan PDF
in English, Hindi, and Marathi with Devanagari typography, meal alternatives,
rationale, hydration, and safety precautions.
"""

import io
import os
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Use existing font initialization
from app.services.pdf_generator import init_pdf_fonts, DEVANAGARI_FONT_REGISTERED

def generate_nutrition_pdf(plan_data: Dict[str, Any], lang: str = "en") -> bytes:
    """
    Generates a high-quality downloadable 7-day nutrition guide PDF
    matching the screen representation and structured constraints.
    """
    init_pdf_fonts()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    is_devanagari = lang in ["hi", "mr"]
    font_main = 'DevanagariFont' if is_devanagari else 'Helvetica'
    font_bold = 'DevanagariFont-Bold' if is_devanagari else 'Helvetica-Bold'
    font_italic = 'DevanagariFont' if is_devanagari else 'Helvetica-Oblique'

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'NutriTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#183C43')
    )
    subtitle_style = ParagraphStyle(
        'NutriSub',
        parent=styles['Normal'],
        fontName=font_main,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#68726F')
    )
    day_heading_style = ParagraphStyle(
        'DayHeading',
        parent=styles['Heading2'],
        fontName=font_bold,
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#183C43'),
        spaceBefore=8,
        spaceAfter=4
    )
    meal_type_style = ParagraphStyle(
        'MealType',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#183C43')
    )
    meal_name_style = ParagraphStyle(
        'MealName',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#272D2B')
    )
    meal_desc_style = ParagraphStyle(
        'MealDesc',
        parent=styles['Normal'],
        fontName=font_main,
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#68726F')
    )
    body_style = ParagraphStyle(
        'NutriBody',
        parent=styles['Normal'],
        fontName=font_main,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#272D2B')
    )
    disclaimer_style = ParagraphStyle(
        'NutriDisclaimer',
        parent=styles['Italic'],
        fontName=font_italic,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#68726F')
    )

    story = []

    # Title & Metadata
    main_title = plan_data.get("plan_title", "Personalized 7-Day Educational Food Guide")
    sub_title = "Tailored meal ideas and practical alternatives based on your report findings."
    if lang == "hi":
        sub_title = "आपकी लैब रिपोर्ट के आधार पर संतुलित एवं सहज ७-दिवसीय आहार विचार।"
    elif lang == "mr":
        sub_title = "तुमच्या लॅब निकालांवर आधारित ७ दिवसांचे संतुलित व सोपे आहार नियोजन."

    story.append(Paragraph(main_title, title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(sub_title, subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#183C43'), spaceAfter=8))

    # Patient Context / Clinical Rationale Card
    basis_summary = plan_data.get("clinical_basis_summary", "")
    if basis_summary:
        sec_title = "What Shaped This Plan" if lang == "en" else "इस योजना का मुख्य आधार" if lang == "hi" else "या नियोजनाचा मुख्य पाया"
        story.append(Paragraph(f"<b>{sec_title}:</b> {basis_summary}", body_style))
        story.append(Spacer(1, 6))

    pref_txt = plan_data.get("dietary_preference", "").title()
    allergies_list = plan_data.get("allergies", [])
    allergies_txt = ", ".join(allergies_list) if allergies_list else ("None reported" if lang == "en" else "कोई नहीं" if lang == "hi" else "कोणतीही नाही")
    meta_line = f"<b>Preference:</b> {pref_txt} &bull; <b>Allergy Exclusions:</b> {allergies_txt}"
    story.append(Paragraph(meta_line, subtitle_style))
    story.append(Spacer(1, 8))

    # 7 Days Schedule
    days = plan_data.get("days", [])
    for d in days:
        day_title = f"{d.get('focus_theme', d.get('day_name'))}"
        story.append(Paragraph(day_title, day_heading_style))

        # Meal rows table
        table_rows = [
            [Paragraph("Meal", meal_type_style), Paragraph("Suggested Dish", meal_type_style), Paragraph("Portion & Guidance", meal_type_style)]
        ]

        # Breakfast
        bf = d.get("breakfast", {})
        table_rows.append([
            Paragraph("Breakfast", meal_type_style),
            Paragraph(f"<b>{bf.get('name')}</b><br/>{bf.get('description', '')}", meal_desc_style),
            Paragraph(f"{bf.get('portion_guidance', '')}<br/><i>Why: {bf.get('why_recommended', '')}</i>", meal_desc_style)
        ])

        # Lunch
        lu = d.get("lunch", {})
        table_rows.append([
            Paragraph("Lunch", meal_type_style),
            Paragraph(f"<b>{lu.get('name')}</b><br/>{lu.get('description', '')}", meal_desc_style),
            Paragraph(f"{lu.get('portion_guidance', '')}<br/><i>Why: {lu.get('why_recommended', '')}</i>", meal_desc_style)
        ])

        # Dinner
        di = d.get("dinner", {})
        table_rows.append([
            Paragraph("Dinner", meal_type_style),
            Paragraph(f"<b>{di.get('name')}</b><br/>{di.get('description', '')}", meal_desc_style),
            Paragraph(f"{di.get('portion_guidance', '')}<br/><i>Why: {di.get('why_recommended', '')}</i>", meal_desc_style)
        ])

        # Snack if present
        sn = d.get("snack")
        if sn:
            table_rows.append([
                Paragraph("Snack", meal_type_style),
                Paragraph(f"<b>{sn.get('name')}</b><br/>{sn.get('description', '')}", meal_desc_style),
                Paragraph(f"{sn.get('portion_guidance', '')}<br/><i>Why: {sn.get('why_recommended', '')}</i>", meal_desc_style)
            ])

        t = Table(table_rows, colWidths=[65, 235, 240])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EBF5F2')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E3DFD5')),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

    # Safety Precautions & Referrals
    safety_title = "Important Safety Guidance" if lang == "en" else "महत्वपूर्ण सुरक्षा निर्देश" if lang == "hi" else "महत्त्वाच्या सुरक्षितता सूचना"
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>{safety_title}</b>", day_heading_style))
    for s_note in plan_data.get("safety_guidance", []):
        story.append(Paragraph(f"• {s_note}", body_style))
        story.append(Spacer(1, 1))

    # Dietitian referral if flagged
    if plan_data.get("dietitian_referral_recommended"):
        ref_msg = plan_data.get("dietitian_referral_reason", "Dietitian consultation recommended.")
        story.append(Paragraph(f"<b>⚠️ Clinical Note:</b> {ref_msg}", body_style))
        story.append(Spacer(1, 2))

    # Disclaimer
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#E3DFD5'), spaceBefore=4, spaceAfter=4))
    story.append(Paragraph(plan_data.get("disclaimer", ""), disclaimer_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
