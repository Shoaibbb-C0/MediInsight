"""
Professional PDF Report Generator for Simplifier 2.0.
Generates a downloadable, beautifully styled multi-page PDF summarizing abnormal findings,
values, ranges, patient context, clinician discussion points, and source appendix.
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, Any

def generate_pdf_report(report_data: Dict[str, Any]) -> bytes:
    """Generates standard downloadable PDF from report structure using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#183C43')
    )
    heading2_style = ParagraphStyle(
        'DocHeading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#183C43'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#272D2B')
    )
    disclaimer_style = ParagraphStyle(
        'DocDisclaimer',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#68726F')
    )

    story = []

    # Header
    story.append(Paragraph("SIMPLIFIER 2.0 — Laboratory Health Summary", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("A patient-friendly educational explanation prepared for physician discussion.", body_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#183C43'), spaceAfter=14))

    # Overall Summary
    story.append(Paragraph("Overview", heading2_style))
    summary_text = report_data.get("patient_summary", "Laboratory report overview.")
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 10))

    # Prioritized Findings Table
    story.append(Paragraph("Results Needing Attention", heading2_style))
    attention_items = report_data.get("prioritized_attention", [])
    
    if attention_items:
        table_data = [["Test Name", "Result", "Standard Range", "Status"]]
        for item in attention_items:
            table_data.append([
                item.get("name", "Unknown"),
                item.get("value", ""),
                item.get("reference_range", ""),
                item.get("status", "").upper()
            ])
        t = Table(table_data, colWidths=[200, 110, 140, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EBF5F2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#183C43')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E3DFD5')),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("All tested values are within typical standard laboratory reference bounds.", body_style))

    story.append(Spacer(1, 12))

    # Clinician Discussion Questions
    doctor_questions = report_data.get("suggested_doctor_questions", [])
    if doctor_questions:
        story.append(Paragraph("Helpful Questions to Discuss With Your Doctor", heading2_style))
        for idx, q in enumerate(doctor_questions, 1):
            story.append(Paragraph(f"{idx}. {q}", body_style))
            story.append(Spacer(1, 3))
        story.append(Spacer(1, 10))

    # Medical Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#E3DFD5'), spaceBefore=10, spaceAfter=8))
    story.append(Paragraph(
        "Notice: Simplifier is an educational tool designed to assist patients in understanding their laboratory slips and preparing for consultations with medical professionals. It is not an automated medical diagnosis, clinical prognosis, or prescription.",
        disclaimer_style
    ))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
