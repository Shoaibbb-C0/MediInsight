import pytest
from app.services.nutrition_engine import generate_inline_nutrition
from app.services.doctor_engine import recommend_specialties, DEMO_DOCTORS, book_appointment, cancel_appointment
from app.services.pdf_generator import generate_pdf_report

def test_inline_nutrition_for_glucose_and_vitd():
    abnormal = [
        {"canonical_name": "glucose_fasting", "name": "Glucose", "status": "high"},
        {"canonical_name": "vitamin_d", "name": "Vitamin D", "status": "low"}
    ]
    nut = generate_inline_nutrition(abnormal)
    assert nut["status"] == "ready"
    assert len(nut["sections"]) >= 2
    topics = [s["topic"] for s in nut["sections"]]
    assert any("Blood Sugar" in t for t in topics)
    assert any("Vitamin D" in t for t in topics)
    assert "disclaimer" in nut

def test_doctor_specialty_recommendation_and_booking():
    abnormal = [
        {"canonical_name": "glucose_fasting", "name": "Glucose", "status": "high"}
    ]
    recs = recommend_specialties(abnormal)
    assert len(recs) >= 2
    specialties = [r["specialty"] for r in recs]
    assert any("Endocrinologist" in s for s in specialties)
    assert any("General Physician" in s for s in specialties)

    # Test booking appointment
    b = book_appointment(doctor_id=DEMO_DOCTORS[0]["id"], slot="Tomorrow at 10:00 AM", patient_name="John Doe")
    assert b["status"] == "CONFIRMED (Simulated Demo Appointment)"
    assert b["booking_id"].startswith("bk_")

    # Test cancel appointment
    success = cancel_appointment(b["booking_id"])
    assert success is True

def test_pdf_report_generation():
    dummy_report = {
        "patient_summary": "Your laboratory panels look reassuring overall.",
        "prioritized_attention": [
            {"name": "Fasting Blood Glucose", "value": "118 mg/dL", "reference_range": "70 - 99 mg/dL", "status": "high"}
        ],
        "suggested_doctor_questions": [
            "What dietary adjustments would help restore this glucose reading?"
        ],
        "disclaimer": "Educational summary only."
    }
    pdf_bytes = generate_pdf_report(dummy_report)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
