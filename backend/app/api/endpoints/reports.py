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
async def get_questionnaire(report_id: str):
    return QuestionnaireResponse(
        report_id=report_id,
        questions=SYNTHETIC_QUESTIONNAIRE_FIXTURE,
        is_synthetic_fixture=True
    )

@router.post("/{report_id}/questions/submit")
async def submit_questionnaire(report_id: str, submission: QuestionnaireSubmission):
    if report_id in REPORTS_DB:
        REPORTS_DB[report_id]["answers"] = submission.answers
        REPORTS_DB[report_id]["questionnaire_completed"] = True
    return {"status": "success", "message": "Questionnaire completed."}

@router.get("/{report_id}/summary")
async def get_simplified_report(report_id: str):
    """
    Returns prioritized patient report:
    1. Attention Items (High / Low / Needs Review)
    2. Changes since previous report (Historical Trends)
    3. Multi-result medical patterns
    4. What these tests commonly check (Purpose & Knowledge)
    5. Within-range tests (accessible without cluttering)
    """
    record = REPORTS_DB.get(report_id)
    extractions = record.get("extractions", SYNTHETIC_EXTRACTION_FIXTURE) if record else SYNTHETIC_EXTRACTION_FIXTURE
    answers = record.get("answers", []) if record else []

    # 1. Prioritization: High / Low / Needs Review first
    high_items = [b for b in extractions if b.get("status") in ["high", "low", "needs_review"]]
    normal_items = [b for b in extractions if b.get("status") in ["normal", "within_range"]]

    # 2. Historical comparison
    past_records = patient_history_service.get_user_history("local_default_patient")
    trends = compute_historical_trends(extractions, past_records)

    # 3. Medical patterns
    patterns = detect_conservative_medical_patterns(extractions)

    # 4. Test purposes & knowledge
    test_purposes = []
    for b in extractions:
        purpose_info = explain_test_purpose(b.get("canonical_name"))
        test_purposes.append({
            "test_name": b.get("name"),
            "why_checked": purpose_info["general_purpose"],
            "actual_reason": purpose_info["actual_reason_status"]
        })

    # Base synthesis
    base_report = generate_synthetic_simplified_report(report_id=report_id, answers=answers)

    # Format response incorporating Phase 3 findings
    return {
        "report_id": report_id,
        "patient_summary": base_report["patient_summary"],
        "key_findings": base_report["key_findings"],
        "prioritized_attention": [
            {
                "name": b["name"],
                "value": f"{b['value']} {b['unit']}",
                "status": b["status"],
                "reference_range": b["reference_range"],
                "provenance": b.get("correction_provenance", "initial_ocr"),
                "plain_summary": f"{b['name']} is {b['status'].upper()} compared to standard lab reference."
            }
            for b in high_items
        ],
        "within_range_results": [
            {
                "name": b["name"],
                "value": f"{b['value']} {b['unit']}",
                "status": "normal",
                "reference_range": b["reference_range"]
            }
            for b in normal_items
        ],
        "historical_changes": trends,
        "clinical_patterns": patterns,
        "test_purposes": test_purposes,
        "lifestyle_tips": base_report["lifestyle_tips"],
        "suggested_doctor_questions": base_report["suggested_doctor_questions"],
        "disclaimer": base_report["disclaimer"],
        "is_synthetic_fixture": record.get("is_synthetic_fixture", False) if record else True
    }

# Profile Endpoints
@router.get("/profile/me", response_model=PatientProfile)
async def get_patient_profile():
    return patient_history_service.get_profile("local_default_patient")

@router.put("/profile/me", response_model=PatientProfile)
async def update_patient_profile(profile: PatientProfile):
    return patient_history_service.update_profile(profile)
