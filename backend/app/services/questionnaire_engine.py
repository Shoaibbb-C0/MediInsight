"""
Versioned, Medically Reviewed Contextual Question Bank for Simplifier 2.0.
Maps specific abnormal findings, previous history, and reported symptoms
to deterministic, medically sensible clarifying questions.
Version: 2.1.0
"""

from typing import List, Dict, Any, Optional

QUESTION_BANK_VERSION = "2.1.0"

# Reviewed Question Bank
QUESTION_BANK = {
    # Low Hemoglobin / Anemia Context
    "q_hemo_fatigue": {
        "id": "q_hemo_fatigue",
        "category": "symptom",
        "target_canonical": "hemoglobin",
        "text": "Have you noticed feeling unusually tired, dizzy, or short of breath during routine daily activities?",
        "context_reason": "Low hemoglobin means fewer red blood cells carry oxygen. Knowing your daily energy level helps tailor physician talking points.",
        "urgent_warning_symptom": False,
        "options": [
            {"id": "fatigue_yes", "text": "Yes, I've had noticeable tiredness or mild lightheadedness"},
            {"id": "fatigue_no", "text": "No, I'm feeling quite normal and energetic"},
            {"id": "fatigue_unsure", "text": "A little tired, but not sure if it's unusual"}
        ]
    },
    "q_hemo_anemia_history": {
        "id": "q_hemo_anemia_history",
        "category": "history",
        "target_canonical": "hemoglobin",
        "text": "Have you previously been diagnosed with anemia or told your iron levels were low?",
        "context_reason": "Knowing whether low hemoglobin is a new finding or a chronic baseline helps frame the explanation safely.",
        "urgent_warning_symptom": False,
        "options": [
            {"id": "anemia_prev_yes", "text": "Yes, I have a history of anemia / low iron"},
            {"id": "anemia_prev_no", "text": "No, this is the first time I've seen a low reading"},
            {"id": "anemia_prev_unsure", "text": "Not sure / cannot recall"}
        ]
    },
    "q_hemo_bleeding_signs": {
        "id": "q_hemo_bleeding_signs",
        "category": "safety",
        "target_canonical": "hemoglobin",
        "text": "Have you noticed any recent unusual bleeding, heavy menstrual cycles, or dark black stools?",
        "context_reason": "Physical bleeding is a common direct cause of dropped hemoglobin.",
        "urgent_warning_symptom": True,  # Flags safety guidance if severe
        "options": [
            {"id": "bleed_none", "text": "No unusual bleeding or dark stools"},
            {"id": "bleed_heavy_periods", "text": "Yes, heavier than usual menstrual cycles"},
            {"id": "bleed_concerning", "text": "Yes, visible bleeding or dark black stools"}
        ]
    },

    # Elevated Glucose / HbA1c Context
    "q_glucose_fasting": {
        "id": "q_glucose_fasting",
        "category": "test_protocol",
        "target_canonical": "glucose_fasting",
        "text": "Was your blood sample strictly collected before breakfast (fasting 8 to 12 hours, water only)?",
        "context_reason": "Eating or drinking anything with sugar or milk within a few hours before testing can naturally raise blood sugar readings.",
        "urgent_warning_symptom": False,
        "options": [
            {"id": "fasting_strictly", "text": "Yes, strictly fasted (water only for 10+ hours)"},
            {"id": "fasting_had_bite", "text": "I had coffee, tea, or a light snack beforehand"},
            {"id": "fasting_unsure", "text": "I cannot remember the exact hours"}
        ]
    },
    "q_glucose_diabetes_history": {
        "id": "q_glucose_diabetes_history",
        "category": "history",
        "target_canonical": "glucose_fasting",
        "text": "Have you previously been told you have prediabetes, diabetes, or insulin resistance?",
        "context_reason": "Helps distinguish an established management plan from an initial screening observation.",
        "urgent_warning_symptom": False,
        "options": [
            {"id": "diabetes_diag_yes", "text": "Yes, I have an existing prediabetes or diabetes diagnosis"},
            {"id": "diabetes_diag_no", "text": "No, I've never been told this before"},
            {"id": "diabetes_diag_unsure", "text": "Unsure / testing for the first time"}
        ]
    },
    "q_glucose_symptoms": {
        "id": "q_glucose_symptoms",
        "category": "symptom",
        "target_canonical": "glucose_fasting",
        "text": "Have you experienced unusual constant thirst, unexplained weight loss, or waking frequently at night to urinate?",
        "context_reason": "These classic indicators help your physician determine if elevated glucose is causing active symptoms.",
        "urgent_warning_symptom": False,
        "options": [
            {"id": "gluc_sym_none", "text": "None of these symptoms"},
            {"id": "gluc_sym_thirst", "text": "Yes, noticeably more thirsty and frequent urination"},
            {"id": "gluc_sym_weightloss", "text": "Yes, unprompted weight changes or fatigue"}
        ]
    },

    # Vitamin D Context
    "q_vitd_sun_habits": {
        "id": "q_vitd_sun_habits",
        "category": "lifestyle",
        "target_canonical": "vitamin_d",
        "text": "How often do you spend 15 to 20 minutes outdoors in direct sunlight each week without sunscreen?",
        "context_reason": "Sunlight is the body's primary natural source of Vitamin D. Low levels are very common with indoor work.",
        "urgent_warning_symptom": False,
        "options": [
            {"id": "sun_rarely", "text": "Rarely (mostly indoors or covered)"},
            {"id": "sun_moderate", "text": "2 to 3 days a week"},
            {"id": "sun_daily", "text": "Almost every day"}
        ]
    },

    # General Wellness Context (When no abnormal findings are detected)
    "q_general_checkup_reason": {
        "id": "q_general_checkup_reason",
        "category": "general",
        "target_canonical": "general",
        "text": "What was the main reason for completing this routine blood work?",
        "context_reason": "Understanding why your doctor ordered the test helps frame what these healthy results mean for your routine.",
        "urgent_warning_symptom": False,
        "options": [
            {"id": "reason_annual", "text": "Annual preventive checkup or company wellness screen"},
            {"id": "reason_symptoms", "text": "I was investigating mild fatigue or non-specific symptoms"},
            {"id": "reason_followup", "text": "Routine follow-up on a previous test"}
        ]
    }
}

def select_adaptive_questions(
    abnormal_biomarkers: List[Dict[str, Any]],
    patient_history: Optional[Dict[str, Any]] = None,
    already_answered_ids: Optional[List[str]] = None,
    max_questions: int = 4,
    lang: str = "en"
) -> List[Dict[str, Any]]:
    """
    Selects 3 to 5 deterministic, non-duplicated, clinically informative questions
    based on actual abnormal findings, known history, and missing information.
    Applies requested language (en, hi, mr) with English fallback.
    """
    from app.services.multilingual_registry import get_localized_question

    already_answered = set(already_answered_ids or [])
    selected_raw = []
    selected_ids = set()
    hist = patient_history or {}

    # Identify abnormal canonical names
    abnormal_canonicals = {
        b.get("canonical_name") for b in abnormal_biomarkers
        if b.get("status") in ["high", "low"] and not b.get("requires_verification")
    }

    # Check known conditions and symptoms from patient history
    known_conditions = [c.lower() for c in (hist.get("known_conditions") or [])]
    reported_symptoms = [s.lower() for s in (hist.get("reported_symptoms") or [])]
    testing_reason = hist.get("testing_reason")

    # 1. Glucose / HbA1c questions - only ask fasting if fasting status not known
    if "glucose_fasting" in abnormal_canonicals or "hba1c" in abnormal_canonicals:
        # Fasting status materially affects glucose interpretation
        if "q_glucose_fasting" not in already_answered and "q_glucose_fasting" not in selected_ids:
            selected_raw.append(QUESTION_BANK["q_glucose_fasting"])
            selected_ids.add("q_glucose_fasting")
            
        # Only ask diabetes history if NOT already documented in patient history
        has_diabetes_known = any("diabetes" in cond or "prediabetes" in cond for cond in known_conditions)
        if not has_diabetes_known and "q_glucose_diabetes_history" not in already_answered and "q_glucose_diabetes_history" not in selected_ids and len(selected_raw) < max_questions:
            selected_raw.append(QUESTION_BANK["q_glucose_diabetes_history"])
            selected_ids.add("q_glucose_diabetes_history")

    # 2. Hemoglobin questions - bleeding signs are critical safety context
    if "hemoglobin" in abnormal_canonicals:
        if "q_hemo_bleeding_signs" not in already_answered and "q_hemo_bleeding_signs" not in selected_ids and len(selected_raw) < max_questions:
            selected_raw.append(QUESTION_BANK["q_hemo_bleeding_signs"])
            selected_ids.add("q_hemo_bleeding_signs")

        has_fatigue_reported = any("fatigue" in s or "tired" in s for s in reported_symptoms)
        if not has_fatigue_reported and "q_hemo_fatigue" not in already_answered and "q_hemo_fatigue" not in selected_ids and len(selected_raw) < max_questions:
            selected_raw.append(QUESTION_BANK["q_hemo_fatigue"])
            selected_ids.add("q_hemo_fatigue")

    # 3. Vitamin D questions
    if "vitamin_d" in abnormal_canonicals and len(selected_raw) < max_questions:
        q_key = "q_vitd_sun_habits"
        if q_key not in already_answered and q_key not in selected_ids:
            selected_raw.append(QUESTION_BANK[q_key])
            selected_ids.add(q_key)

    # Note: If no abnormalities or if context is already fully known, return empty list (0 questions).
    # We do NOT force a filler general question if everything is normal or context is known.

    final_questions = []
    for q in selected_raw[:max_questions]:
        q_dict = dict(q)
        loc = get_localized_question(q["id"], lang=lang)
        if loc:
            q_dict["text"] = loc.get("text", q["text"])
            q_dict["context_reason"] = loc.get("context_reason", q.get("context_reason"))
            if "options" in loc and isinstance(loc["options"], dict):
                localized_options = []
                for opt in q.get("options", []):
                    localized_options.append({
                        "id": opt["id"],
                        "text": loc["options"].get(opt["id"], opt["text"])
                    })
                q_dict["options"] = localized_options
        final_questions.append(q_dict)

    return final_questions
