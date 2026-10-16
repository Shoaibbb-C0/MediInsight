import pytest
from app.services.abnormality_engine import classify_measurement, parse_range_bounds
from app.services.medical_knowledge import explain_test_purpose, get_test_knowledge
from app.services.patient_history import PatientProfile, PatientHistoryService
from app.services.pattern_engine import compute_historical_trends, detect_conservative_medical_patterns

def test_parse_range_bounds():
    assert parse_range_bounds("70 - 99 mg/dL") == (70.0, 99.0, "interval")
    assert parse_range_bounds("< 5.7 %") == (None, 5.7, "<")
    assert parse_range_bounds("<= 200") == (None, 200.0, "<=")
    assert parse_range_bounds("> 40 mg/dL") == (40.0, None, ">")
    assert parse_range_bounds(">= 60") == (60.0, None, ">=")
    assert parse_range_bounds("invalid text") == (None, None, None)

def test_abnormality_classification_quantitative():
    # Glucose above range
    status, reason, details = classify_measurement("115", "70 - 99 mg/dL")
    assert status == "HIGH"
    assert details["source"] == "printed_interval"
    
    # Normal in range
    status, reason, details = classify_measurement("85", "70 - 99 mg/dL")
    assert status == "WITHIN_RANGE"
    assert details["source"] == "printed_interval"
    
    # Low below range
    status, reason, details = classify_measurement("15.2", "30 - 100 ng/mL")
    assert status == "LOW"
    assert details["source"] == "printed_interval"

    # Missing range without canonical metadata falls back safely to needs review
    status, reason, details = classify_measurement("120", None)
    assert status == "NEEDS_REVIEW"
    assert details["source"] == "range_unavailable"

    # Missing range with validated canonical metadata and matching unit uses fallback
    status, reason, details = classify_measurement("120", None, canonical_name="glucose_fasting", unit="mg/dL")
    assert status == "HIGH"
    assert details["is_fallback"] is True
    assert details["source"] == "fallback_interval"

    # Missing range with mismatched unit does NOT apply fallback
    status, reason, details = classify_measurement("6.5", None, canonical_name="glucose_fasting", unit="mmol/L")
    assert status == "NEEDS_REVIEW"

def test_abnormality_classification_qualitative():
    status, _, details = classify_measurement("Negative", is_qualitative=True)
    assert status == "WITHIN_RANGE"
    status, _, details = classify_measurement("Reactive", is_qualitative=True)
    assert status == "NEEDS_REVIEW"

def test_test_purpose_distinguishes_printed_vs_unknown():
    # When report notes reason
    res = explain_test_purpose("glucose_fasting", printed_reason="Routine annual physical")
    assert "Documented on report: 'Routine annual physical'" in res["actual_reason_status"]
    
    # When unnoted
    res2 = explain_test_purpose("glucose_fasting", printed_reason=None)
    assert "not noted" in res2["actual_reason_status"]

def test_historical_trends_unit_compatibility():
    service = PatientHistoryService()
    assert service.get_user_history("local_default_patient") == []
    history = service.get_user_history("demo_patient")
    
    current_compatible = [
        {"canonical_name": "glucose_fasting", "name": "Glucose", "value": "118", "unit": "mg/dL"}
    ]
    trends = compute_historical_trends(current_compatible, history)
    assert len(trends) == 1
    assert trends[0]["direction"] == "higher"
    assert trends[0]["difference"] == 14.0

    # Incompatible unit case
    current_incompatible = [
        {"canonical_name": "glucose_fasting", "name": "Glucose", "value": "6.5", "unit": "mmol/L"}
    ]
    trends_incomp = compute_historical_trends(current_incompatible, history)
    assert trends_incomp[0]["status"] == "INCOMPATIBLE_UNITS"

def test_conservative_medical_pattern_detection():
    # Both Glucose & HbA1c elevated
    measurements = [
        {"canonical_name": "glucose_fasting", "value": "120", "status": "high"},
        {"canonical_name": "hba1c", "value": "6.3", "status": "high"}
    ]
    patterns = detect_conservative_medical_patterns(measurements)
    assert len(patterns) >= 1
    p = patterns[0]
    assert p["pattern_name"] == "Blood Sugar Regulation Pattern"
    assert "Recent dietary changes" in p["alternative_explanations"]
    assert "missing_evidence" in p
