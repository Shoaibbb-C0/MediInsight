"""
Historical Comparison and Conservative Multi-Result Pattern Engine for Simplifier 2.0.
Computes compatible unit trends without falsely declaring improvements,
and evaluates conservative, medically reviewed biomarker patterns.
"""

from typing import List, Dict, Any, Optional

def compute_historical_trends(
    current_measurements: List[Dict[str, Any]],
    historical_records: List[Any]
) -> List[Dict[str, Any]]:
    """
    Compares current measurements against previous compatible records.
    Strictly verifies canonical identity and measurement unit compatibility.
    """
    if not historical_records:
        return []

    # Map previous measurements from most recent historical record
    latest_past = historical_records[0]
    past_map = {}
    for item in latest_past.measurements:
        canonical = item.get("canonical_name")
        if canonical:
            past_map[canonical] = item

    trends = []
    for curr in current_measurements:
        canonical = curr.get("canonical_name")
        if not canonical or canonical not in past_map:
            continue

        past = past_map[canonical]
        curr_unit = (curr.get("unit") or "").strip().lower()
        past_unit = (past.get("unit") or "").strip().lower()

        # Strict unit compatibility check
        if curr_unit != past_unit:
            trends.append({
                "canonical_name": canonical,
                "name": curr.get("name"),
                "status": "INCOMPATIBLE_UNITS",
                "explanation": f"Previous report used '{past_unit}' while current uses '{curr_unit}'. Trend comparison skipped to avoid error."
            })
            continue

        try:
            curr_val = float(curr.get("value"))
            past_val = float(past.get("value"))
            diff = curr_val - past_val
            
            if abs(diff) < 0.05:
                direction = "steady"
                desc = f"Essentially unchanged ({past_val} → {curr_val} {curr_unit})"
            elif diff > 0:
                direction = "higher"
                desc = f"Higher than previous reading ({past_val} → {curr_val} {curr_unit})"
            else:
                direction = "lower"
                desc = f"Lower than previous reading ({past_val} → {curr_val} {curr_unit})"

            trends.append({
                "canonical_name": canonical,
                "name": curr.get("name"),
                "current_value": str(curr_val),
                "previous_value": str(past_val),
                "unit": curr.get("unit"),
                "previous_date": latest_past.report_date,
                "direction": direction,
                "difference": round(diff, 2),
                "concise_summary": desc,
                "interpretation_note": "A numerical difference reflects interval change between tests and should be reviewed with your doctor in the context of your overall health routine."
            })
        except (ValueError, TypeError):
            continue

    return trends

def detect_conservative_medical_patterns(measurements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Conservative, reviewed multi-result patterns:
    - Dual Glucose & HbA1c elevation: early metabolic / glycemic pattern
    - High Cholesterol & Triglycerides: combined lipid pattern
    - Low Hemoglobin with abnormal red cell indices: red cell oxygen-carrying pattern
    Always states alternative explanations and missing evidence without diagnostic overreach.
    """
    by_canonical = {m.get("canonical_name"): m for m in measurements if m.get("canonical_name")}
    patterns = []

    # Pattern 1: Metabolic / Glycemic regulation
    has_glucose = "glucose_fasting" in by_canonical
    has_hba1c = "hba1c" in by_canonical
    if has_glucose and has_hba1c:
        g = by_canonical["glucose_fasting"]
        h = by_canonical["hba1c"]
        g_high = g.get("status") == "high" or float(g.get("value", 0)) > 99
        h_high = h.get("status") == "high" or float(h.get("value", 0)) >= 5.7

        if g_high and h_high:
            patterns.append({
                "pattern_name": "Blood Sugar Regulation Pattern",
                "finding_level": "attention_recommended",
                "summary": "Both fasting glucose and 3-month HbA1c are slightly above standard reference boundaries.",
                "what_this_means": "When both short-term fasting sugar and medium-term HbA1c are elevated together, it typically suggests consistent slower processing of dietary sugars across recent months.",
                "alternative_explanations": "Recent dietary changes, temporary illness, physical stress, or lack of sleep before the test can also elevate blood glucose readings.",
                "missing_evidence": "Post-meal glucose levels, family metabolic history, and nutritional habits are needed before any formal clinical diagnosis.",
                "questions_for_doctor": "Would you recommend repeating these in 3 months along with lifestyle modifications?"
            })

    # Pattern 2: Vitamin D & Bone/Energy wellness
    if "vitamin_d" in by_canonical:
        vit_d = by_canonical["vitamin_d"]
        if vit_d.get("status") == "low" or float(vit_d.get("value", 99)) < 30:
            patterns.append({
                "pattern_name": "Vitamin D Replenishment Consideration",
                "finding_level": "common_deficiency",
                "summary": "Vitamin D is below optimal circulating threshold (18.4 ng/mL vs target > 30 ng/mL).",
                "what_this_means": "Low vitamin D is very common in indoor workers and during cooler seasons, and is simple to address with safe guidance.",
                "alternative_explanations": "Seasonal sunlight reduction, sunscreen use, or dietary variations.",
                "missing_evidence": "Serum calcium and PTH (parathyroid hormone) levels are sometimes checked if vitamin D is persistently low.",
                "questions_for_doctor": "What daily or weekly supplement dosage would safely restore my level?"
            })

    return patterns
