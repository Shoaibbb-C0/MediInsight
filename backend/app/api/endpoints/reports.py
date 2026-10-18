import os
import uuid
import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
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
from app.services.pattern_engine import (
    compute_historical_trends,
    detect_conservative_medical_patterns,
    compute_personal_baselines
)
from app.fixtures.synthetic_data import (
    SYNTHETIC_EXTRACTION_FIXTURE,
    SYNTHETIC_QUESTIONNAIRE_FIXTURE,
    generate_synthetic_simplified_report
)

from app.services.questionnaire_engine import select_adaptive_questions
from app.services.report_synthesizer import synthesize_smart_report

router = APIRouter()

# Durable owner-scoped state
from app.core.store import OwnedStore
from app.core.auth import owner_context, production
REPORTS_DB = OwnedStore("reports")


def get_report_record(report_id: str):
    """Only the explicitly named demonstration may use synthetic measurements."""
    if report_id == "rep_demo_fixture" and production():
        raise HTTPException(404, "Demonstration reports are disabled in production.")
    if report_id == "rep_demo_fixture" and report_id not in REPORTS_DB:
        import copy
        REPORTS_DB[report_id] = {"report_id": report_id, "extractions": copy.deepcopy(SYNTHETIC_EXTRACTION_FIXTURE), "answers": [], "is_synthetic_fixture": True}
    record = REPORTS_DB.get(report_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Report not found. Upload a report or explicitly choose the demonstration.")
    return record


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
    
    contents = await file.read(settings.MAX_FILE_SIZE_MB * 1024 * 1024 + 1)
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
        )
    
    report_id = f"rep_{uuid.uuid4().hex[:10]}"
    try:
        extracted_biomarkers = engine.process_document(contents, filename)
    except (ValueError, RuntimeError, ImportError):
        raise HTTPException(422,"Document extraction could not complete. Check file quality and OCR/model availability. No values were substituted.") from None
    
    is_fixture = False
    if not extracted_biomarkers:
        raise HTTPException(status_code=422, detail="No reliable laboratory measurements could be extracted. Try a clearer report. No demonstration values were substituted.")

    # Run Abnormality Engine on all extracted items
    for b in extracted_biomarkers:
        classified_status, _, _ = classify_measurement(
            value_str=b.value,
            range_str=b.reference_range,
            canonical_name=b.canonical_name,
            unit=b.unit
        )
        b.status = "needs_review" if b.requires_verification else classified_status.lower()

    page_count = 1
    if ext == "pdf":
        import pymupdf
        with pymupdf.open(stream=contents, filetype="pdf") as source_document:
            page_count = len(source_document)
    REPORTS_DB[report_id] = {
        "report_id": report_id,
        "user_id": owner_context.get(),
        "filename": filename,
        "file_type": ext,
        "page_count": page_count,
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
        page_count=page_count,
        status="partial" if any(item.requires_verification for item in extracted_biomarkers) else "processed",
        is_synthetic_fixture=is_fixture,
        created_at=REPORTS_DB[report_id]["created_at"]
    )

@router.post("/capture", response_model=UploadResponse)
async def upload_captured_pages(files: List[UploadFile] = File(...)):
    """Combine explicitly selected camera pages; never discard later pages."""
    import io
    import pymupdf
    from app.services.image_processor import check_image_safety_and_dimensions
    if not 1 <= len(files) <= 10: raise HTTPException(422, "Select between 1 and 10 captured pages.")
    total = 0
    document = pymupdf.open()
    try:
        for file in files:
            if (file.filename or '').split('.')[-1].lower() not in ['jpg','jpeg','png','webp']:
                raise HTTPException(422, "Captured pages must be images.")
            data = await file.read(settings.MAX_FILE_SIZE_MB * 1024 * 1024 + 1)
            total += len(data)
            if total > settings.MAX_FILE_SIZE_MB * 1024 * 1024: raise HTTPException(413, "Captured pages exceed the upload limit.")
            image = check_image_safety_and_dimensions(data).convert('RGB')
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=90)
            scale = min(612/image.width, 792/image.height)
            page = document.new_page(width=image.width*scale, height=image.height*scale)
            page.insert_image(page.rect, stream=output.getvalue())
        combined = document.tobytes(deflate=True)
        return await upload_report(UploadFile(filename='camera-report.pdf', file=io.BytesIO(combined)))
    except (ValueError, OSError):
        raise HTTPException(422, "A captured page is unreadable. Retake it and try again.") from None
    finally:
        document.close()

@router.get("/history/list")
async def report_history(lang: str = "en"):
    records=[]
    for report_id in REPORTS_DB:
        record=REPORTS_DB[report_id]
        if record.get("is_synthetic_fixture"): continue
        summary=await get_simplified_report(report_id,lang)
        records.append({"id":report_id,"date":record["created_at"],"filename":record["filename"],"fileType":record["file_type"],"measurements":record["extractions"],"answers":record.get("answers",[]),"report":summary})
    return {"reports":sorted(records,key=lambda record:record['date'],reverse=True)}

@router.delete("/{report_id}")
async def delete_report(report_id: str):
    get_report_record(report_id)
    for key in list(NUTRITION_PLANS_DB):
        plan=NUTRITION_PLANS_DB[key]
        if plan.get('report_id')==report_id: del NUTRITION_PLANS_DB[key]
    del REPORTS_DB[report_id]
    return {'deleted':True}

@router.get("/{report_id}/extractions", response_model=List[ExtractedBiomarker])
async def get_extractions(report_id: str):
    return get_report_record(report_id)["extractions"]

@router.post("/{report_id}/verify")
async def verify_biomarker(report_id: str, submission: VerificationSubmission):
    record = get_report_record(report_id)
    extractions = record["extractions"]
    for item in extractions:
        if item["id"] == submission.biomarker_id:
            item["corrected_value"] = submission.corrected_value
            item["value"] = submission.corrected_value
            item["requires_verification"] = not bool(item.get("unit") and item.get("reference_range"))
            item["correction_provenance"] = "patient_edited"
            
            # Reclassify with abnormality engine
            new_status, _, _ = classify_measurement(
                value_str=submission.corrected_value,
                range_str=item.get("reference_range"),
                canonical_name=item.get("canonical_name"),
                unit=item.get("unit")
            )
            item["requires_verification"] = item["requires_verification"] or new_status == "NEEDS_REVIEW"
            item["status"] = "needs_review" if item["requires_verification"] else new_status.lower()
            REPORTS_DB[report_id] = record
            return {"status": "success", "updated_biomarker": item}
    
    raise HTTPException(status_code=404, detail="Biomarker not found in report.")

@router.get("/{report_id}/questions", response_model=QuestionnaireResponse)
async def get_questionnaire(report_id: str, lang: str = "en"):
    """Retrieve adaptive questions tailored to detected abnormalities and patient history in requested language."""
    record = get_report_record(report_id)
    extractions = record["extractions"]
    user_id = owner_context.get() if record else "local_default_patient"
    patient_history = patient_history_service.get_profile(user_id)
    
    adaptive_qs = select_adaptive_questions(
        abnormal_biomarkers=extractions,
        patient_history=patient_history.model_dump(),
        lang=lang
    )
    
    return QuestionnaireResponse(
        report_id=report_id,
        questions=adaptive_qs,
        is_synthetic_fixture=record.get("is_synthetic_fixture", False)
    )

@router.post("/{report_id}/questions/submit")
async def submit_questionnaire(report_id: str, submission: QuestionnaireSubmission):
    record = get_report_record(report_id)
    if submission.report_id != report_id: raise HTTPException(422, "Report identity does not match.")
    allowed_questions = {item['id']:{option['id'] for option in item['options']} for item in select_adaptive_questions(record['extractions'],lang='en')}
    if len({answer.question_id for answer in submission.answers}) != len(submission.answers) or any(answer.question_id not in allowed_questions or answer.selected_option_id not in allowed_questions[answer.question_id] for answer in submission.answers):
        raise HTTPException(422, "Select valid answers for this report.")
    record["answers"] = submission.answers
    record["questionnaire_completed"] = True
    REPORTS_DB[report_id] = record
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
    record = get_report_record(report_id)
    extractions = record["extractions"]
    answers = record.get("answers", []) if record else []

    # Historical comparison
    from app.services.patient_history import HistoricalReportRecord
    past_records=[]
    if not record.get("is_synthetic_fixture"):
        for old_id in REPORTS_DB:
            old=REPORTS_DB[old_id]
            if old_id==report_id or old.get("is_synthetic_fixture") or old.get("created_at","") >= record.get("created_at",""): continue
            comparable=[item for item in old['extractions'] if not item.get('requires_verification') and any(now.get('canonical_name')==item.get('canonical_name') and now.get('unit')==item.get('unit') and now.get('reference_range')==item.get('reference_range') for now in extractions)]
            if comparable: past_records.append(HistoricalReportRecord(report_id=old_id,user_id=owner_context.get(),report_date=old['created_at'],title=old['filename'],measurements=comparable))
        past_records.sort(key=lambda item:item.report_date,reverse=True)
    trends = compute_historical_trends(extractions, past_records)
    baselines = compute_personal_baselines(extractions, past_records, min_reports=4)

    # Medical patterns
    patterns = detect_conservative_medical_patterns(extractions,lang)

    # Test purposes & knowledge
    from app.services.multilingual_registry import get_localized_biomarker
    test_purposes = []
    for b in extractions:
        purpose_info = explain_test_purpose(b.get("canonical_name"))
        localized_info = get_localized_biomarker(b.get("canonical_name"),lang)
        test_purposes.append({
            "test_name": localized_info.get("name",b.get("name")),
            "why_checked": localized_info.get("why_checked", purpose_info["general_purpose"]) if lang=="en" else localized_info.get("why_checked", "इस परीक्षण का उद्देश्य डॉक्टर से पूछें।" if lang=="hi" else "या चाचणीचा उद्देश डॉक्टरांना विचारा."),
            "actual_reason": purpose_info["actual_reason_status"] if lang=="en" else ("जाँच कराने का विशिष्ट कारण रिपोर्ट में नहीं दिया गया।" if lang=="hi" else "चाचणी करण्याचे विशिष्ट कारण अहवालात दिलेले नाही.")
        })

    is_fixture = record.get("is_synthetic_fixture", False) if record else True

    # Call Multilingual Smart Report Synthesizer
    return synthesize_smart_report(
        report_id=report_id,
        extractions=extractions,
        answers=answers,
        historical_trends=trends,
        clinical_patterns=patterns,
        test_purposes=test_purposes,
        personal_baselines=baselines,
        is_synthetic_fixture=is_fixture,
        lang=lang
    )

from fastapi.responses import Response
from app.services.pdf_generator import generate_pdf_report

from app.services.nutrition_planner import generate_seven_day_plan, swap_meal_in_plan
from app.services.nutrition_questionnaire import get_localized_nutrition_questions
from app.services.nutrition_pdf_generator import generate_nutrition_pdf
from app.schemas.nutrition import NutritionPreferencesSubmission, SwapMealRequest

# Durable owner-scoped nutrition plans
NUTRITION_PLANS_DB = OwnedStore("nutrition")

# Feature 2: Smart Nutrition Questionnaire
@router.get("/{report_id}/nutrition/questions")
async def get_nutrition_questions(report_id: str, lang: str = "en"):
    """Retrieve adaptive nutrition questions in requested language."""
    get_report_record(report_id)
    questions = get_localized_nutrition_questions(lang=lang)
    return {"report_id": report_id, "questions": questions}

# Feature 2: Generate 7-Day Plan
@router.post("/{report_id}/nutrition/generate")
async def generate_nutrition_plan_endpoint(
    report_id: str,
    submission: NutritionPreferencesSubmission,
    lang: str = "en"
):
    """Generates a structured 7-day personalized food plan based on report findings and preferences."""
    record = get_report_record(report_id)
    extractions = record["extractions"]
    
    if not record.get('is_synthetic_fixture') and (not {'age_group','dietary_preference','allergies','known_conditions'}.issubset(submission.model_fields_set) or not submission.allergies):
        raise HTTPException(422, "Answer age, dietary preference, allergies and medical safety questions before generating a plan.")
    # Mandatory allergy validation: user must explicitly specify allergies or ['none']
    if not submission.allergies:
        submission.allergies = ["none"]

    submission.user_id = owner_context.get()
    try:
        plan = generate_seven_day_plan(report_id, extractions, submission, lang=lang)
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from None
    plan_dict = plan.model_dump()
    NUTRITION_PLANS_DB[plan.plan_id] = plan_dict
    NUTRITION_PLANS_DB[f"latest_{report_id}"] = plan_dict
    return plan_dict

def localize_saved_plan(plan_dict, lang):
    if plan_dict.get("language") == lang:
        return plan_dict
    import copy
    from app.services.nutrition_planner import build_meal_item, DAY_THEMES, HYDRATION_MAP
    from app.services.nutrition_database import get_food_by_id
    localized = copy.deepcopy(plan_dict)
    localized["language"] = lang
    inputs=plan_dict.get('planning_inputs') or {}
    if inputs:
        source=inputs.get('_clinical_signals')
        if source is None: source=get_report_record(plan_dict['report_id'])['extractions']
        text_plan=generate_seven_day_plan(plan_dict['report_id'],source,NutritionPreferencesSubmission(**inputs),lang).model_dump()
        for key in ['plan_title','clinical_basis_summary','safety_guidance','dietitian_referral_recommended','dietitian_referral_reason','disclaimer']:
            localized[key]=text_plan[key]
    for index, day in enumerate(localized.get("days", [])):
        day["focus_theme"] = DAY_THEMES[index].get(lang, DAY_THEMES[index]["en"])
        day["hydration_guidance"] = HYDRATION_MAP.get(lang, HYDRATION_MAP["en"])
        for meal_type in ("breakfast", "lunch", "snack", "dinner"):
            meal = day.get(meal_type)
            food = get_food_by_id(meal.get("id")) if meal else None
            if food:
                day[meal_type] = build_meal_item(food, lang, localized.get("dietary_preference", "vegetarian"), localized.get("allergies", []), localized.get("food_restrictions", []), localized.get("foods_avoided_freetext")).model_dump()
    return localized


# Feature 2: Get Latest Plan
@router.get("/{report_id}/nutrition/plan")
async def get_latest_nutrition_plan(report_id: str, lang: str = "en"):
    """Retrieves the latest saved nutrition plan for this report."""
    key = f"latest_{report_id}"
    if key in NUTRITION_PLANS_DB:
        return localize_saved_plan(NUTRITION_PLANS_DB[key], lang)
    
    get_report_record(report_id)
    raise HTTPException(status_code=404, detail="No saved food plan. Complete the food preferences first.")

# Feature 2: Swap Meal
@router.post("/nutrition/swap")
async def swap_meal_endpoint(payload: SwapMealRequest, lang: str = "en"):
    """Replaces a specific meal on a given day with an alternative dish."""
    plan_id = payload.plan_id
    plan_dict = NUTRITION_PLANS_DB.get(plan_id)
    if not plan_dict:
        # Check by latest
        for k, v in NUTRITION_PLANS_DB.items():
            if v.get("plan_id") == plan_id:
                plan_dict = v
                break
    if not plan_dict:
        raise HTTPException(status_code=404, detail="Nutrition plan not found")

    try:
        updated = swap_meal_in_plan(localize_saved_plan(plan_dict,lang),payload.day_number,payload.meal_type,payload.new_meal_id,lang)
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from None
    NUTRITION_PLANS_DB[plan_id] = updated
    if "report_id" in updated:
        NUTRITION_PLANS_DB[f"latest_{updated['report_id']}"] = updated
    return updated

# Feature 2: Download Nutrition Plan PDF
@router.get("/{report_id}/nutrition/pdf")
async def download_nutrition_plan_pdf(report_id: str, lang: str = "en"):
    """Downloads professional 7-day nutrition guide PDF."""
    key = f"latest_{report_id}"
    plan_dict = NUTRITION_PLANS_DB.get(key)
    if not plan_dict:
        raise HTTPException(status_code=404, detail="Generate and save a food plan before downloading it.")

    pdf_bytes = generate_nutrition_pdf(localize_saved_plan(plan_dict, lang), lang=lang)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Simplifier_Nutrition_Plan_{report_id}_{lang}.pdf"}
    )

# Backward-compatible endpoint for existing components
@router.get("/{report_id}/nutrition", deprecated=True)
async def get_report_nutrition(report_id: str):
    """Compatibility alias: never bypass saved-plan safety preferences."""
    return await get_latest_nutrition_plan(report_id)

# Feature 3: Production-Grade Doctor Discovery & Specialty Recommendations
from app.services.location_service import resolve_patient_location
from app.services.doctor_database import search_providers
from app.services.specialty_recommender import generate_specialty_recommendations
from app.services.appointment_service import (
    create_appointment,
    reschedule_appointment as reschedule_app_svc,
    cancel_appointment as cancel_app_svc,
    get_user_appointments
)
from app.schemas.doctor import (
    DoctorDiscoveryResponse,
    DirectBookingRequest,
    RescheduleBookingRequest,
    CancelBookingRequest
)

@router.get("/{report_id}/doctors", response_model=DoctorDiscoveryResponse)
async def get_doctor_discovery(
    report_id: str,
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    specialty_id: Optional[str] = None,
    lang: str = "en",
    radius_m: int = Query(10000, ge=1000, le=50000),
    sort_by: str = Query("top_rated", pattern="^(top_rated|nearest)$")
):
    """
    Production-grade doctor discovery:
    1. Recommends specialties grounded in report findings and patient answers.
    2. Resolves patient location (browser coords or city/PIN).
    3. Searches real onboarded and external directory providers.
    4. Computes true Haversine distance where coordinates are available.
    """
    record = get_report_record(report_id)
    extractions = record["extractions"]
    answers = record.get("answers", []) if record else []

    # 1. Specialty recommendations
    recs = generate_specialty_recommendations(extractions, answers=answers, lang=lang)
    
    from app.services.provider_discovery import discover_providers
    selected_spec = specialty_id or next((rec.specialty_id for rec in recs if not rec.is_fallback), "general_physician")
    specialty_terms = {"general_physician":"general physician", "endocrinology":"endocrinology clinic", "nephrology":"nephrology clinic", "cardiology":"cardiology clinic", "hematology":"hematology clinic", "gastroenterology":"gastroenterology clinic", "rheumatology":"rheumatology clinic"}
    if selected_spec not in specialty_terms: raise HTTPException(422,"Unsupported specialty.")
    # Explicit demonstrations retain their existing labelled fixture workflow.
    if report_id == "rep_demo_fixture" and not city and lat is None and lng is None:
        resolved_loc = resolve_patient_location(city_or_pincode="Mumbai")
        providers = search_providers(specialty_id=selected_spec, city="Mumbai")
        return DoctorDiscoveryResponse(report_id=report_id,sort_by=sort_by,recommended_specialties=recs,selected_specialty_id=selected_spec,resolved_location=resolved_loc,providers=providers,total_count=len(providers),is_demo_mode=True,live_provider_api_configured=False,disclaimer="Demonstration listings only. No real consultation is booked.")
    if not city and lat is None and lng is None:
        return DoctorDiscoveryResponse(report_id=report_id,sort_by=sort_by,recommended_specialties=recs,selected_specialty_id=selected_spec,resolved_location={"query":"","display_name":"Choose your location","city":"","coordinates":None},providers=[],total_count=0,is_demo_mode=False,live_provider_api_configured=bool(os.getenv("GOOGLE_MAPS_SERVER_KEY")),location_required=True,disclaimer="Choose a location. Google Maps listings do not verify physician credentials or appointment availability.")
    result = await discover_providers(city,lat,lng,radius_m,specialty_terms[selected_spec],lang,sort_by)
    return DoctorDiscoveryResponse(report_id=report_id,sort_by=sort_by,recommended_specialties=recs,selected_specialty_id=selected_spec,providers=result["providers"],resolved_location=result["resolved_location"],searched_radius_m=result["searched_radius_m"],total_count=len(result["providers"]),is_demo_mode=False,live_provider_api_configured=True,disclaimer="Provider information from Google Maps, not independently verified physician credentials. Contact the clinic to confirm consultation details. No appointment is confirmed here.")

# Feature 3: Atomic Direct Appointment Booking
@router.post("/doctors/book")
async def book_doctor_appointment(
    payload: DirectBookingRequest,
    user_id: str = "local_default_patient"
):
    """Atomically books a server-authoritative slot with double-booking prevention."""
    if production(): raise HTTPException(503,"Real appointment scheduling is not configured. Contact the clinic.")
    result = create_appointment(user_id=owner_context.get(), request=payload)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# Feature 3: Atomic Reschedule
@router.post("/doctors/reschedule")
async def reschedule_doctor_appointment(
    payload: RescheduleBookingRequest,
    user_id: str = "local_default_patient"
):
    """Atomically reschedules an appointment reservation to another slot."""
    if production(): raise HTTPException(503,"Real appointment scheduling is not configured. Contact the clinic.")
    result = reschedule_app_svc(user_id=owner_context.get(), request=payload)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# Feature 3: Atomic Cancel
@router.post("/doctors/cancel")
async def cancel_doctor_appointment(
    payload: CancelBookingRequest,
    user_id: str = "local_default_patient"
):
    """Atomically cancels a reserved appointment and releases the slot."""
    if production(): raise HTTPException(503,"Real appointment scheduling is not configured. Contact the clinic.")
    result = cancel_app_svc(user_id=owner_context.get(), request=payload)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# Feature 3: My Appointments
@router.get("/doctors/my-appointments")
async def get_patient_appointments(user_id: str = "local_default_patient"):
    """Returns patient-scoped appointment history with isolation."""
    return {"appointments": get_user_appointments(owner_context.get())}

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
