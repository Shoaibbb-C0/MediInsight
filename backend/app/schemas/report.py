from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float

class ExtractedBiomarker(BaseModel):
    id: str
    name: str
    canonical_name: str
    value: str
    unit: str
    reference_range: str
    status: str = Field(..., description="'normal', 'high', 'low', 'borderline'")
    confidence: float = Field(..., ge=0.0, le=1.0)
    requires_verification: bool = False
    source_page: Optional[int] = None
    source_line: Optional[str] = None
    source_box: Optional[BoundingBox] = None
    original_extracted_value: Optional[str] = None
    corrected_value: Optional[str] = None
    correction_provenance: Optional[str] = None  # e.g., 'patient_edited', 'verified_match'

class UploadResponse(BaseModel):
    report_id: str
    filename: str
    file_type: str
    page_count: int
    status: str
    is_synthetic_fixture: bool = False
    created_at: str

class VerificationSubmission(BaseModel):
    biomarker_id: str
    corrected_value: str
    patient_note: Optional[str] = None

class QuestionOption(BaseModel):
    id: str
    text: str

class PersonalizedQuestion(BaseModel):
    id: str
    text: str
    context_reason: str
    options: List[QuestionOption]

class QuestionnaireResponse(BaseModel):
    report_id: str
    questions: List[PersonalizedQuestion]
    is_synthetic_fixture: bool = False

class QuestionnaireAnswer(BaseModel):
    question_id: str
    selected_option_id: str

class QuestionnaireSubmission(BaseModel):
    report_id: str
    answers: List[QuestionnaireAnswer]

class SimpleExplanationItem(BaseModel):
    biomarker_name: str
    status: str
    plain_english_summary: str
    what_this_means: str
    reassurance: str

class SimplifiedReport(BaseModel):
    report_id: str
    patient_summary: str
    key_findings: List[SimpleExplanationItem]
    lifestyle_tips: List[str]
    suggested_doctor_questions: List[str]
    disclaimer: str
    is_synthetic_fixture: bool = False
