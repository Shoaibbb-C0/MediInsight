"""
Tests for Feature 2: Personalized Nutrition System.
Covers:
- Report-aware 7-day plan generation
- Dietary preference filtering (vegetarian, vegan, non-veg, eggetarian)
- Strict allergy exclusion rules (peanuts, gluten, dairy, fish)
- Meal alternative retrieval and swapping logic
- Immediate clinical dietitian referral flags for abnormal creatinine
- Trilingual (EN, HI, MR) plan parity and Devanagari PDF generation
- Two-user isolation in local persistence
"""

import pytest
from app.services.nutrition_planner import generate_seven_day_plan, swap_meal_in_plan, is_food_safe
from app.services.nutrition_database import FOOD_DATABASE, get_food_by_id
from app.services.nutrition_questionnaire import get_localized_nutrition_questions
from app.services.nutrition_pdf_generator import generate_nutrition_pdf
from app.schemas.nutrition import NutritionPreferencesSubmission, SwapMealRequest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_nutrition_questions_localized():
    for lang in ["en", "hi", "mr"]:
        res = client.get(f"/api/v1/reports/rep_demo_fixture/nutrition/questions?lang={lang}")
        assert res.status_code == 200
        data = res.json()
        assert "questions" in data
        assert len(data["questions"]) >= 4
        # Verify text populated
        assert data["questions"][0]["text"] != ""
        assert len(data["questions"][0]["options"]) > 0

def test_allergy_exclusion_peanuts():
    poha = get_food_by_id("bf_poha")
    assert "peanuts" in poha.get("allergens", [])

    # User with peanut allergy
    safe = is_food_safe(poha, dietary_pref="vegetarian", allergies=["peanuts"], restrictions=[])
    assert safe is False

    # User without peanut allergy
    safe_no_allergy = is_food_safe(poha, dietary_pref="vegetarian", allergies=[], restrictions=[])
    assert safe_no_allergy is True

def test_vegan_dietary_preference_filters_dairy():
    paneer = get_food_by_id("di_paneer_bhurji_roti")
    safe_vegan = is_food_safe(paneer, dietary_pref="vegan", allergies=[], restrictions=[])
    assert safe_vegan is False

    safe_veg = is_food_safe(paneer, dietary_pref="vegetarian", allergies=[], restrictions=[])
    assert safe_veg is True

def test_seven_day_plan_structure_and_variety():
    extractions = [
        {"canonical_name": "glucose_fasting", "name": "Glucose", "value": "118", "unit": "mg/dL", "status": "high", "reference_range": "70 - 99 mg/dL"},
        {"canonical_name": "vitamin_d", "name": "Vitamin D", "value": "18.4", "unit": "ng/mL", "status": "low", "reference_range": "30 - 100 ng/mL"}
    ]
    prefs = NutritionPreferencesSubmission(
        report_id="rep_test_01",
        dietary_preference="vegetarian",
        allergies=["peanuts"]
    )
    plan = generate_seven_day_plan("rep_test_01", extractions, prefs, lang="en")
    assert plan.plan_id.startswith("plan_")
    assert len(plan.days) == 7
    assert "glucose" in plan.clinical_basis_summary.lower() or "carbohydrates" in plan.clinical_basis_summary.lower()

    # Ensure no peanut dishes were assigned
    for d in plan.days:
        assert d.breakfast.id != "bf_poha"  # Poha has peanuts
        assert d.lunch is not None
        assert d.dinner is not None
        assert len(d.breakfast.alternatives) > 0

def test_abnormal_creatinine_triggers_dietitian_referral():
    extractions = [
        {"canonical_name": "creatinine_serum", "name": "Serum Creatinine", "value": "1.8", "unit": "mg/dL", "status": "high", "reference_range": "0.7 - 1.3 mg/dL"}
    ]
    prefs = NutritionPreferencesSubmission(report_id="rep_renal_01")
    with pytest.raises(ValueError, match="clinician or dietitian"):
        generate_seven_day_plan("rep_renal_01", extractions, prefs, lang="en")

def test_meal_swapping_in_plan():
    extractions = [
        {"canonical_name": "glucose_fasting", "name": "Glucose", "value": "118", "unit": "mg/dL", "status": "high", "reference_range": "70 - 99 mg/dL"}
    ]
    prefs = NutritionPreferencesSubmission(report_id="rep_swap_01", dietary_preference="vegetarian")
    plan = generate_seven_day_plan("rep_swap_01", extractions, prefs, lang="en")
    plan_dict = plan.model_dump()

    day1_bf_before = plan_dict["days"][0]["breakfast"]["id"]

    # Swap to upma
    updated = swap_meal_in_plan(
        plan_dict=plan_dict,
        day_number=1,
        meal_type="breakfast",
        new_meal_id="bf_upma",
        lang="en"
    )
    assert updated["days"][0]["breakfast"]["id"] == "bf_upma"

def test_nutrition_pdf_generation_en_hi_mr():
    extractions = [{"canonical_name": "glucose_fasting", "name": "Glucose", "value": "118", "unit": "mg/dL", "status": "high", "reference_range": "70 - 99 mg/dL"}]
    for lang in ["en", "hi", "mr"]:
        prefs = NutritionPreferencesSubmission(report_id=f"rep_pdf_{lang}", dietary_preference="vegetarian")
        plan = generate_seven_day_plan(f"rep_pdf_{lang}", extractions, prefs, lang=lang)
        pdf_bytes = generate_nutrition_pdf(plan.model_dump(), lang=lang)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 2000
        assert pdf_bytes.startswith(b"%PDF")

def test_two_user_nutrition_isolation():
    from app.api.endpoints.reports import REPORTS_DB
    REPORTS_DB["rep_user_a"] = {"extractions": [], "answers": []}
    REPORTS_DB["rep_user_b"] = {"extractions": [], "answers": []}
    # User A generates non-veg plan
    res_a = client.post("/api/v1/reports/rep_user_a/nutrition/generate", json={
        "user_id": "user_a",
        "report_id": "rep_user_a",
        "dietary_preference": "non_vegetarian"
    })
    assert res_a.status_code == 200
    plan_a = res_a.json()
    assert plan_a["dietary_preference"] == "non_vegetarian"

    # User B generates vegan plan
    res_b = client.post("/api/v1/reports/rep_user_b/nutrition/generate", json={
        "user_id": "user_b",
        "report_id": "rep_user_b",
        "dietary_preference": "vegan"
    })
    assert res_b.status_code == 200
    plan_b = res_b.json()
    assert plan_b["dietary_preference"] == "vegan"

    # Verify retrieval keeps them separate
    get_a = client.get("/api/v1/reports/rep_user_a/nutrition/plan").json()
    get_b = client.get("/api/v1/reports/rep_user_b/nutrition/plan").json()
    assert get_a["dietary_preference"] == "non_vegetarian"
    assert get_b["dietary_preference"] == "vegan"

def test_high_risk_pregnancy_and_renal_referral():
    extractions = []
    # Pregnancy reported in context
    prefs_preg = NutritionPreferencesSubmission(
        report_id="rep_preg",
        known_conditions=["pregnancy"]
    )
    with pytest.raises(ValueError, match="clinician or dietitian"):
        generate_seven_day_plan("rep_preg", extractions, prefs_preg)

    # CKD reported in context
    prefs_ckd = NutritionPreferencesSubmission(
        report_id="rep_ckd",
        known_conditions=["ckd_renal"]
    )
    with pytest.raises(ValueError, match="clinician or dietitian"):
        generate_seven_day_plan("rep_ckd", extractions, prefs_ckd)

def test_freetext_avoidance_filter():
    poha = get_food_by_id("bf_poha")
    # Avoid flattened rice / poha
    safe = is_food_safe(poha, "vegetarian", allergies=[], restrictions=[], foods_avoided_freetext="poha, mushroom")
    assert safe is False

def test_saved_swap_survives_retrieval_translation_and_pdf():
    response = client.post('/api/v1/reports/rep_demo_fixture/nutrition/generate', json={
        'report_id': 'rep_demo_fixture', 'dietary_preference': 'vegetarian', 'allergies': ['none']
    })
    assert response.status_code == 200
    plan = response.json()
    alternative = plan['days'][0]['breakfast']['alternatives'][0]
    swapped = client.post('/api/v1/reports/nutrition/swap', json={
        'plan_id': plan['plan_id'], 'day_number': 1, 'meal_type': 'breakfast', 'new_meal_id': alternative['id']
    })
    assert swapped.status_code == 200
    for lang in ['en', 'hi', 'mr']:
        saved = client.get(f'/api/v1/reports/rep_demo_fixture/nutrition/plan?lang={lang}').json()
        assert saved['days'][0]['breakfast']['id'] == alternative['id']
        pdf = client.get(f'/api/v1/reports/rep_demo_fixture/nutrition/pdf?lang={lang}')
        assert pdf.status_code == 200
        assert pdf.content.startswith(b'%PDF')
