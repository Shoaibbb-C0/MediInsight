import pytest
from app.services.questionnaire_engine import select_adaptive_questions, QUESTION_BANK
from app.services.report_synthesizer import synthesize_smart_report

def test_select_adaptive_questions_for_hemoglobin():
    abnormal = [
        {"canonical_name": "hemoglobin", "status": "low"}
    ]
    qs = select_adaptive_questions(abnormal)
    assert len(qs) >= 2
    q_ids = [q["id"] for q in qs]
    assert "q_hemo_fatigue" in q_ids
    assert "q_glucose_fasting" not in q_ids

def test_select_adaptive_questions_for_glucose():
    abnormal = [
        {"canonical_name": "glucose_fasting", "status": "high"}
    ]
    qs = select_adaptive_questions(abnormal)
    assert len(qs) >= 2
    q_ids = [q["id"] for q in qs]
    assert "q_glucose_fasting" in q_ids
    assert "q_hemo_fatigue" not in q_ids

def test_no_duplicate_questions_with_multiple_abnormalities():
    abnormal = [
        {"canonical_name": "glucose_fasting", "status": "high"},
        {"canonical_name": "hba1c", "status": "high"},
        {"canonical_name": "vitamin_d", "status": "low"}
    ]
    qs = select_adaptive_questions(abnormal, max_questions=4)
    q_ids = [q["id"] for q in qs]
    # Verify no duplicates
    assert len(q_ids) == len(set(q_ids))
    assert len(qs) <= 4

def test_skip_all_questions_honors_unknown_context():
    extractions = [
        {"canonical_name": "glucose_fasting", "name": "Glucose", "value": "118", "unit": "mg/dL", "status": "high", "reference_range": "70 - 99 mg/dL"}
    ]
    # Empty answers list represents skipped questionnaire
    report = synthesize_smart_report(
        report_id="rep_skip_test",
        extractions=extractions,
        answers=[],
        historical_trends=[],
        clinical_patterns=[],
        test_purposes=[]
    )
    assert "skipped" in report["what_your_answers_tell_us"]["insights"][0]
    assert "heres_what_we_found" in report
    assert "results_needing_attention" in report
    assert "what_to_discuss_with_doctor" in report

def test_urgent_bleeding_symptom_triggers_immediate_safety_alert():
    extractions = [
        {"canonical_name": "hemoglobin", "name": "Hemoglobin", "value": "9.5", "unit": "g/dL", "status": "low", "reference_range": "12.0 - 17.5 g/dL"}
    ]
    answers = [
        {"question_id": "q_hemo_bleeding_signs", "selected_option_id": "bleed_concerning"}
    ]
    report = synthesize_smart_report(
        report_id="rep_urgent_test",
        extractions=extractions,
        answers=answers,
        historical_trends=[],
        clinical_patterns=[],
        test_purposes=[]
    )
    assert report["safety_alert"] is not None
    assert report["safety_alert"]["is_urgent"] is True
    assert "urgent medical evaluation" in report["safety_alert"]["guidance"]
