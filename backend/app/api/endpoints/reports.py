import os
import uuid
import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List, Optional
from app.schemas.report import (
    UploadResponse,
    ExtractedBiomarker,
    VerificationSubmission,
    QuestionnaireResponse,
    QuestionnaireSubmission,
    SimplifiedReport
)
from app.core.config import settings
from app.services.extraction_service import engine
from app.services.abnormality_engine import classify_measurement
from app.services.medical_knowledge import get_test_knowledge, explain_test_purpose
from app.services.patient_history import patient_history_service, PatientProfile
from app.services.pattern_engine import compute_historical_trends, detect_conservative_medical_patterns
from app.fixtures.synthetic_data import (
    SYNTHETIC_EXTRACTION_FIXTURE,
    SYNTHETIC_QUESTIONNAIRE_FIXTURE,
    generate_synthetic_simplified_report
)

from app.services.questionnaire_engine import select_adaptive_questions
from app.services.report_synthesizer import synthesize_smart_report

router = APIRouter()

# In-memory session store for local dev mode
REPORTS_DB = {}

@router.post("/upload", response_model=UploadResponse)
async def upload_report(file: UploadFile = File(...)):
    """Accepts medical lab report file, extracts biomarkers, and registers report."""
    filename = file.filename or "captured_page.jpg"
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
        )
    
    report_id = f"rep_{uuid.uuid4().hex[:10]}"
    extracted_biomarkers = engine.process_document(contents, filename)
    
    is_fixture = False
    if not extracted_biomarkers:
        extracted_biomarkers = [ExtractedBiomarker(**b) for b in SYNTHETIC_EXTRACTION_FIXTURE]
        is_fixture = True

    # Run Abnormality Engine on all extracted items
    for b in extracted_biomarkers:
        classified_status, _ = classify_measurement(
            value_str=b.value,
            range_str=b.reference_range
        )
        b.status = classified_status.lower()

    REPORTS_DB[report_id] = {
        "report_id": report_id,
        "filename": filename,
        "file_type": ext,
        "page_count": 1,
        "extractions": [b.model_dump() for b in extracted_biomarkers],
        "answers": [],
        "verified": False,
        "questionnaire_completed": False,
        "is_synthetic_fixture": is_fixture,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    return UploadResponse(
        report_id=report_id,
        filename=filename,
        file_type=ext,
        page_count=1,
        status="processed",
        is_synthetic_fixture=is_fixture,
        created_at=REPORTS_DB[report_id]["created_at"]
    )

@router.get("/{report_id}/extractions", response_model=List[ExtractedBiomarker])
async def get_extractions(report_id: str):
    if report_id not in REPORTS_DB:
        return SYNTHETIC_EXTRACTION_FIXTURE
    return REPORTS_DB[report_id]["extractions"]

@router.post("/{report_id}/verify")
async def verify_biomarker(report_id: str, submission: VerificationSubmission):
    extractions = REPORTS_DB.get(report_id, {}).get("extractions", SYNTHETIC_EXTRACTION_FIXTURE)
    for item in extractions:
        if item["id"] == submission.biomarker_id:
            item["corrected_value"] = submission.corrected_value
            item["value"] = submission.corrected_value
            item["requires_verification"] = False
            item["correction_provenance"] = "patient_edited"
            
            # Reclassify with abnormality engine
            new_status, _ = classify_measurement(
                value_str=submission.corrected_value,
                range_str=item.get("reference_range")
            )
            item["status"] = new_status.lower()
            return {"status": "success", "updated_biomarker": item}
    
    raise HTTPException(status_code=404, detail="Biomarker not found in report.")

@router.get("/{report_id}/questions", response_model=QuestionnaireResponse)
async def get_questionnaire(report_id: str, lang: str = "en"):
    """Retrieve adaptive questions tailored to detected abnormalities and patient history in requested language."""
    record = REPORTS_DB.get(report_id)
    extractions = record.get("extractions", SYNTHETIC_EXTRACTION_FIXTURE) if record else SYNTHETIC_EXTRACTION_FIXTURE
    user_id = record.get("user_id", "local_default_patient") if record else "local_default_patient"
    patient_history = patient_history_service.get_profile(user_id)
    
    adaptive_qs = select_adaptive_questions(
        abnormal_biomarkers=extractions,
        patient_history=patient_history.model_dump(),
        lang=lang
    )
    
    return QuestionnaireResponse(
        report_id=report_id,
        questions=adaptive_qs,
        is_synthetic_fixture=False
    )

@router.post("/{report_id}/questions/submit")
async def submit_questionnaire(report_id: str, submission: QuestionnaireSubmission):
    if report_id in REPORTS_DB:
        REPORTS_DB[report_id]["answers"] = submission.answers
        REPORTS_DB[report_id]["questionnaire_completed"] = True
    return {"status": "success", "message": "Questionnaire completed."}

@router.get("/{report_id}/summary")
async def get_simplified_report(report_id: str, lang: str = "en"):
    """
    Returns prioritized patient smart report in requested language:
    1. Attention Items (High / Low / Needs Review)
    2. Excluded / Unreliable results (Uncertain OCR/layout)
    3. Changes since previous report (Historical Trends)
    4. Multi-result medical patterns
    5. What these tests commonly check (Purpose & Knowledge)
    6. Patient context insights from questionnaire
    7. Doctor discussion questions
    """
    record = REPORTS_DB.get(report_id)
    extractions = record.get("extractions", SYNTHETIC_EXTRACTION_FIXTURE) if record else SYNTHETIC_EXTRACTION_FIXTURE
    answers = record.get("answers", []) if record else []

    # Historical comparison
    past_records = patient_history_service.get_user_history("local_default_patient")
    trends = compute_historical_trends(extractions, past_records)

    # Medical patterns
    patterns = detect_conservative_medical_patterns(extractions)

    # Test purposes & knowledge
    test_purposes = []
    for b in extractions:
        purpose_info = explain_test_purpose(b.get("canonical_name"))
        test_purposes.append({
            "test_name": b.get("name"),
            "why_checked": purpose_info["general_purpose"],
            "actual_reason": purpose_info["actual_reason_status"]
        })

    is_fixture = record.get("is_synthetic_fixture", False) if record else True

    # Call Phase 4/5 Multilingual Smart Report Synthesizer
    return synthesize_smart_report(
        report_id=report_id,
        extractions=extractions,
        answers=answers,
        historical_trends=trends,
        clinical_patterns=patterns,
        test_purposes=test_purposes,
        is_synthetic_fixture=is_fixture,
        lang=lang
    )

from fastapi.responses import Response
from app.services.nutrition_engine import generate_inline_nutrition
from app.services.doctor_engine import recommend_specialties, DEMO_DOCTORS, book_appointment, reschedule_appointment, cancel_appointment
from app.services.pdf_generator import generate_pdf_report

# Phase 5: Inline Nutrition Endpoint
@router.get("/{report_id}/nutrition")
async def get_report_nutrition(report_id: str):
    """Retrieve inline personalized nutritional suggestions based on findings."""
    record = REPORTS_DB.get(report_id)
    extractions = record.get("extractions", SYNTHETIC_EXTRACTION_FIXTURE) if record else SYNTHETIC_EXTRACTION_FIXTURE
    abnormal = [b for b in extractions if b.get("status") in ["high", "low", "needs_review"]]
    return generate_inline_nutrition(abnormal)

# Phase 5: Inline Doctor Discovery Endpoints
@router.get("/{report_id}/doctors")
async def get_doctor_discovery(report_id: str):
    """Retrieve recommended specialties and clearly labeled demo doctors."""
    record = REPORTS_DB.get(report_id)
    extractions = record.get("extractions", SYNTHETIC_EXTRACTION_FIXTURE) if record else SYNTHETIC_EXTRACTION_FIXTURE
    abnormal = [b for b in extractions if b.get("status") in ["high", "low", "needs_review"]]
    specialties = recommend_specialties(abnormal)
    return {
        "recommended_specialties": specialties,
        "available_doctors": DEMO_DOCTORS,
        "is_demo_mode": True,
        "disclaimer": "Demo physician directory. Bookings in development mode are simulated for testing purposes."
    }

@router.post("/doctors/book")
async def book_doctor_appointment(payload: dict):
    doctor_id = payload.get("doctor_id", "doc_01")
    slot = payload.get("slot", "Tomorrow at 10:00 AM")
    patient_name = payload.get("patient_name", "Anonymous Patient")
    return book_appointment(doctor_id, slot, patient_name)

@router.post("/doctors/cancel")
async def cancel_doctor_appointment(payload: dict):
    booking_id = payload.get("booking_id")
    success = cancel_appointment(booking_id)
    return {"status": "success" if success else "failed", "cancelled": success}

# Phase 5: Professional PDF Export Endpoint
@router.get("/{report_id}/pdf")
async def download_report_pdf(report_id: str, lang: str = "en"):
    """Generates downloadable clinical summary PDF in the user's selected language."""
    summary_data = await get_simplified_report(report_id, lang=lang)
    pdf_bytes = generate_pdf_report(summary_data, lang=lang)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Simplifier_Report_{report_id}_{lang}.pdf"}
    )
