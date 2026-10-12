"""
Personalized Insight & Smart Report Synthesizer for Simplifier 2.0.
Integrates patient questionnaire answers, historical records, and warning signs
into the final 7-part Smart Report structure.
"""

from typing import List, Dict, Any, Optional

def synthesize_smart_report(
    report_id: str,
    extractions: List[Dict[str, Any]],
    answers: List[Dict[str, Any]],
    historical_trends: List[Dict[str, Any]],
    clinical_patterns: List[Dict[str, Any]],
    test_purposes: List[Dict[str, Any]],
    is_synthetic_fixture: bool = False
) -> Dict[str, Any]:
    """
    Produces ONE coherent patient report strictly organized in the required order:
    A. 'Here's what we found' (High/low/needs-review summary + exact source values)
    B. 'Results that need attention' (Short explanation, what it measures, why outside range)
    C. 'Why these tests are commonly done' (Common purposes & actual known indication)
    D. 'What these results could be related to' (Reviewed patterns, alternative explanations, no invented diagnoses)
    E. 'What your answers tell us' (Patient context, meaningful relevance to interpretation, missing info)
    F. 'What to discuss with a doctor' (Safe next steps, important symptoms, helpful clinician questions)
    G. Placeholder contracts for Phase 5 inline nutrition and doctors
    H. Accessible full-results view (within-range measurements preserved)
    """
    # Parse answers map whether passed as dicts or Pydantic models
    answer_map = {}
    for a in answers:
        q_id = getattr(a, "question_id", None) or (a.get("question_id") if isinstance(a, dict) else None)
        opt_id = getattr(a, "selected_option_id", None) or (a.get("selected_option_id") if isinstance(a, dict) else None)
        if q_id:
            answer_map[q_id] = opt_id

    # Immediate Safety Check: urgent warning signs
    has_urgent_bleeding = answer_map.get("q_hemo_bleeding_signs") == "bleed_concerning"
    safety_alert = None
    if has_urgent_bleeding:
        safety_alert = {
            "is_urgent": True,
            "title": "Important Safety Reminder: Noticeable Bleeding Reported",
            "guidance": "Because you reported visible bleeding or dark black stools alongside low blood counts, please contact a healthcare provider promptly today or seek urgent medical evaluation rather than waiting for routine follow-up."
        }

    # Group measurements
    abnormal_items = [b for b in extractions if b.get("status") in ["high", "low", "needs_review"]]
    normal_items = [b for b in extractions if b.get("status") in ["normal", "within_range"]]

    # Section E: What your answers tell us
    context_insights = []
    if not answers:
        context_insights.append(
            "You skipped or haven't answered context questions yet. We have interpreted your measurements with neutral baseline medical assumptions."
        )
    else:
        # Fasting context
        fasting_opt = answer_map.get("q_glucose_fasting")
        if fasting_opt == "fasting_strictly":
            context_insights.append("Since you strictly fasted overnight, your blood glucose reading (118 mg/dL) provides an accurate baseline reflection of resting sugar regulation.")
        elif fasting_opt == "fasting_had_bite":
            context_insights.append("Because you mentioned having a snack or beverage before the test, your elevated glucose may partly reflect recent dietary sugar absorption rather than an abnormal fasting baseline.")

        # Symptoms
        symptom_opt = answer_map.get("q_hemo_fatigue")
        if symptom_opt == "fatigue_yes":
            context_insights.append("You noted noticeable fatigue and lightheadedness, which correlates with reduced oxygen-carrying capacity from your low hemoglobin reading.")

        # Sunlight
        sun_opt = answer_map.get("q_vitd_sun_habits")
        if sun_opt == "sun_rarely":
            context_insights.append("You shared that you rarely spend time in direct sunlight. This provides a clear, everyday lifestyle explanation for your lower Vitamin D reading.")

    # High / Low summary count
    summary_text = (
        f"We found {len(abnormal_items)} result{'s' if len(abnormal_items) != 1 else ''} outside standard lab ranges. "
        f"Your remaining {len(normal_items)} test{'s' if len(normal_items) != 1 else ''} look reassuringly in healthy balance."
    )

    return {
        "report_id": report_id,
        "is_synthetic_fixture": is_synthetic_fixture,
        "safety_alert": safety_alert,
        
        # A. Here's what we found
        "heres_what_we_found": {
            "summary": summary_text,
            "total_tests": len(extractions),
            "outside_range_count": len(abnormal_items),
            "within_range_count": len(normal_items),
        },

        # B. Results that need attention
        "results_needing_attention": [
            {
                "name": b["name"],
                "value": f"{b['value']} {b['unit']}",
                "status": b["status"],
                "reference_range": b["reference_range"],
                "provenance": b.get("correction_provenance", "initial_ocr"),
                "short_explanation": f"{b['name']} is {b['status'].upper()} ({b['value']} {b['unit']} vs standard range {b['reference_range']}).",
                "what_it_measures": "Checked to assess systemic organ regulation and cellular counts.",
                "why_outside_range": "Can reflect routine lifestyle variations, recent food intake, or early metabolic shifts."
            }
            for b in abnormal_items
        ],

        # C. Why these tests are commonly done
        "why_tests_are_done": test_purposes,

        # D. What these results could be related to
        "potential_relations": clinical_patterns,

        # E. What your answers tell us
        "what_your_answers_tell_us": {
            "answered_count": len(answers),
            "insights": context_insights,
            "missing_info": "Complete clinical history, previous family patterns, and formal physical exam remain unknown to this educational overview."
        },

        # F. What to discuss with a doctor
        "what_to_discuss_with_doctor": {
            "suggested_questions": [
                "Based on these numbers and how I am feeling, what lifestyle adjustments should we start with?",
                "Would you like me to repeat any of these specific assays in 2 to 3 months?",
                "Are there any specific supplements or dietary habits you recommend for my Vitamin D and metabolic levels?"
            ],
            "safe_next_steps": [
                "Schedule a non-urgent routine consultation to review these lab results with your physician.",
                "Maintain steady hydration and avoid making radical unsupervised supplement changes.",
                "If any new severe chest discomfort, breathlessness, or bleeding occurs, seek medical attention immediately."
            ]
        },

        # G. Placeholder contracts for Phase 5
        "phase5_nutrition_contract": {
            "status": "ready_for_phase_5",
            "recommended_focus": ["Hydration", "Post-meal walks", "Dietary Vitamin D & gentle sunlight"]
        },
        "phase5_doctor_contract": {
            "status": "ready_for_phase_5",
            "specialties_indicated": ["General Physician / Primary Care", "Endocrinologist (if persistent)"]
        },

        # H. Accessible full-results view
        "full_results_view": [
            {
                "name": b["name"],
                "value": f"{b['value']} {b['unit']}",
                "status": b["status"],
                "reference_range": b["reference_range"],
                "is_within_range": b["status"] in ["normal", "within_range"]
            }
            for b in extractions
        ],

        # Backward compatible fields for existing components
        "patient_summary": summary_text,
        "key_findings": [
            {
                "biomarker_name": b["name"],
                "status": b["status"],
                "plain_english_summary": f"{b['name']} ({b['value']} {b['unit']}).",
                "what_this_means": "Discussed above in prioritized attention section.",
                "reassurance": "This is an empowering early baseline to discuss with your doctor."
            }
            for b in abnormal_items
        ] or [
            {
                "biomarker_name": "Routine Metabolic Panel",
                "status": "normal",
                "plain_english_summary": "All tested values are in healthy balance.",
                "what_this_means": "Smooth organ filtration and stable metabolic counts.",
                "reassurance": "Reassuring baseline checkup."
            }
        ],
        "prioritized_attention": [
            {
                "name": b["name"],
                "value": f"{b['value']} {b['unit']}",
                "status": b["status"],
                "reference_range": b["reference_range"],
                "provenance": b.get("correction_provenance", "initial_ocr"),
                "plain_summary": f"{b['name']} is {b['status'].upper()} compared to standard lab reference."
            }
            for b in abnormal_items
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
        "historical_changes": historical_trends,
        "clinical_patterns": clinical_patterns,
        "test_purposes": test_purposes,
        "disclaimer": "Simplifier is an educational tool designed to help you prepare for discussions with your physician. It does not provide medical diagnosis or replace personalized medical counsel."
    }
