import pytest
from app.services.pattern_engine import compute_personal_baselines
from app.services.patient_history import HistoricalReportRecord

def test_personal_baseline_requires_four_reports():
    # Only 2 previous reports + current = 3 total -> should NOT produce baseline
    past_records = [
        HistoricalReportRecord(
            report_id="rep_1",
            report_date="2026-01-01",
            title="Checkup 1",
            measurements=[{"canonical_name": "glucose_fasting", "value": "100", "unit": "mg/dL"}]
        ),
        HistoricalReportRecord(
            report_id="rep_2",
            report_date="2026-03-01",
            title="Checkup 2",
            measurements=[{"canonical_name": "glucose_fasting", "value": "105", "unit": "mg/dL"}]
        )
    ]
    curr = [{"canonical_name": "glucose_fasting", "name": "Glucose", "value": "110", "unit": "mg/dL"}]
    
    baselines = compute_personal_baselines(curr, past_records, min_reports=4)
    assert len(baselines) == 0

def test_personal_baseline_computes_with_four_compatible_reports():
    # 3 past records + 1 current = 4 total reports
    past_records = [
        HistoricalReportRecord(
            report_id="rep_1",
            report_date="2025-06-01",
            title="Checkup 1",
            measurements=[{"canonical_name": "glucose_fasting", "value": "95", "unit": "mg/dL"}]
        ),
        HistoricalReportRecord(
            report_id="rep_2",
            report_date="2025-09-01",
            title="Checkup 2",
            measurements=[{"canonical_name": "glucose_fasting", "value": "105", "unit": "mg/dL"}]
        ),
        HistoricalReportRecord(
            report_id="rep_3",
            report_date="2025-12-01",
            title="Checkup 3",
            measurements=[{"canonical_name": "glucose_fasting", "value": "100", "unit": "mg/dL"}]
        )
    ]
    curr = [{"canonical_name": "glucose_fasting", "name": "Glucose", "value": "110", "unit": "mg/dL"}]
    
    baselines = compute_personal_baselines(curr, past_records, min_reports=4)
    assert len(baselines) == 1
    b = baselines[0]
    assert b["canonical_name"] == "glucose_fasting"
    assert b["report_count"] == 4
    # series: [95, 105, 100, 110] -> sorted: [95, 100, 105, 110] -> median: 102.5
    assert b["median_value"] == 102.5
    assert b["observed_min"] == 95.0
    assert b["observed_max"] == 110.0
    assert b["label"] == "Your usual readings across previous reports"
    assert "does not replace the standard laboratory reference range" in b["clinical_distinction_note"]

def test_personal_baseline_excludes_incompatible_units():
    # 3 past records, but one has incompatible unit mmol/L
    past_records = [
        HistoricalReportRecord(
            report_id="rep_1",
            report_date="2025-06-01",
            title="Checkup 1",
            measurements=[{"canonical_name": "glucose_fasting", "value": "95", "unit": "mg/dL"}]
        ),
        HistoricalReportRecord(
            report_id="rep_2",
            report_date="2025-09-01",
            title="Checkup 2",
            measurements=[{"canonical_name": "glucose_fasting", "value": "5.5", "unit": "mmol/L"}]
        ),
        HistoricalReportRecord(
            report_id="rep_3",
            report_date="2025-12-01",
            title="Checkup 3",
            measurements=[{"canonical_name": "glucose_fasting", "value": "100", "unit": "mg/dL"}]
        )
    ]
    curr = [{"canonical_name": "glucose_fasting", "name": "Glucose", "value": "110", "unit": "mg/dL"}]
    
    baselines = compute_personal_baselines(curr, past_records, min_reports=4)
    # Only 2 compatible past records + 1 current = 3 compatible -> does not meet min 4
    assert len(baselines) == 0
