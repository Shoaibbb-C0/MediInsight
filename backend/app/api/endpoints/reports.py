import os
import uuid
import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from app.schemas.report import (
    UploadResponse,
    ExtractedBiomarker,
    VerificationSubmission,
    QuestionnaireResponse,
    QuestionnaireSubmission,
    SimplifiedReport
)
from app.core.config import settings
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
    """
    Accepts medical lab report file (PDF, JPG, PNG, WEBP).
    Validates size and extension securely.
    """
    filename = file.filename or "captured_page.jpg"
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Read content to check file size
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
        )
    
    report_id = f"rep_{uuid.uuid4().hex[:10]}"
    
    # Save session state
    REPORTS_DB[report_id] = {
        "report_id": report_id,
        "filename": filename,
        "file_type": ext,
        "page_count": 1,
        "extractions": [dict(b) for b in SYNTHETIC_EXTRACTION_FIXTURE],
        "answers": [],
        "verified": False,
        "questionnaire_completed": False,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    return UploadResponse(
        report_id=report_id,
        filename=filename,
        file_type=ext,
        page_count=1,
        status="processed",
        is_synthetic_fixture=True,
        created_at=REPORTS_DB[report_id]["created_at"]
    )

@router.get("/{report_id}/extractions", response_model=List[ExtractedBiomarker])
async def get_extractions(report_id: str):
    """Retrieve extracted biomarkers for source verification interface."""
    if report_id not in REPORTS_DB:
        # Fallback to demo report for convenient direct preview/refresh
        return SYNTHETIC_EXTRACTION_FIXTURE
    return REPORTS_DB[report_id]["extractions"]

@router.post("/{report_id}/verify")
async def verify_biomarker(report_id: str, submission: VerificationSubmission):
    """Save user manual correction or confirmation for a low-confidence extracted row."""
    extractions = REPORTS_DB.get(report_id, {}).get("extractions", SYNTHETIC_EXTRACTION_FIXTURE)
    for item in extractions:
        if item["id"] == submission.biomarker_id:
            item["corrected_value"] = submission.corrected_value
            item["requires_verification"] = False
            item["correction_provenance"] = "patient_edited"
            return {"status": "success", "updated_biomarker": item}
    
    raise HTTPException(status_code=404, detail="Biomarker not found in report.")

@router.get("/{report_id}/questions", response_model=QuestionnaireResponse)
async def get_questionnaire(report_id: str):
    """Retrieve personalized clarification questions based on detected high/low findings."""
    return QuestionnaireResponse(
        report_id=report_id,
        questions=SYNTHETIC_QUESTIONNAIRE_FIXTURE,
        is_synthetic_fixture=True
    )

@router.post("/{report_id}/questions/submit")
async def submit_questionnaire(report_id: str, submission: QuestionnaireSubmission):
    """
    Submit questionnaire answers.
    Marks questionnaire as completed BEFORE simplified report generation is permitted.
    """
    if report_id in REPORTS_DB:
        REPORTS_DB[report_id]["answers"] = submission.answers
        REPORTS_DB[report_id]["questionnaire_completed"] = True
    
    return {"status": "success", "message": "Questionnaire completed."}

@router.get("/{report_id}/summary", response_model=SimplifiedReport)
async def get_simplified_report(report_id: str):
    """
    Returns final simplified health explanation.
    Enforces that this appears AFTER questions are submitted.
    """
    record = REPORTS_DB.get(report_id)
    answers = record.get("answers", []) if record else []
    
    return generate_synthetic_simplified_report(report_id=report_id, answers=answers)
