"""
Abnormality Detection and Reference Range Classification Engine for Simplifier 2.0.
Accurately categorizes quantitative and qualitative medical laboratory measurements
strictly preserving exact original numbers, units, printed flags, and provenance.
Enforces strict precedence:
1. Valid printed laboratory interval on the report
2. Validated assay-specific fallback from TEST_METADATA (explicitly tagged)
3. Range unavailable / Needs Review
Handles one-sided limits (<, <=, >, >=), standard intervals (A - B, A to B),
and qualitative values (Negative, Positive, etc.).
"""

import re
from typing import Tuple, Optional, Dict, Any

# Validated standard reference ranges for known assays with compatible canonical units
VALIDATED_ASSAY_FALLBACKS: Dict[str, Dict[str, Any]] = {
    "glucose_fasting": {
        "unit": "mg/dL",
        "range_str": "70 - 99 mg/dL",
        "low": 70.0,
        "high": 99.0,
        "operator": "interval"
    },
    "hba1c": {
        "unit": "%",
        "range_str": "< 5.7 %",
        "low": None,
        "high": 5.7,
        "operator": "<"
    },
    "creatinine_serum": {
        "unit": "mg/dL",
        "range_str": "0.7 - 1.3 mg/dL",
        "low": 0.7,
        "high": 1.3,
        "operator": "interval"
    },
    "bun": {
        "unit": "mg/dL",
        "range_str": "7 - 20 mg/dL",
        "low": 7.0,
        "high": 20.0,
        "operator": "interval"
    },
    "cholesterol_total": {
        "unit": "mg/dL",
        "range_str": "< 200 mg/dL",
        "low": None,
        "high": 200.0,
        "operator": "<"
    },
    "triglycerides": {
        "unit": "mg/dL",
        "range_str": "< 150 mg/dL",
        "low": None,
        "high": 150.0,
        "operator": "<"
    },
    "cholesterol_hdl": {
        "unit": "mg/dL",
        "range_str": "> 40 mg/dL",
        "low": 40.0,
        "high": None,
        "operator": ">"
    },
    "cholesterol_ldl": {
        "unit": "mg/dL",
        "range_str": "< 100 mg/dL",
        "low": None,
        "high": 100.0,
        "operator": "<"
    },
    "hemoglobin": {
        "unit": "g/dL",
        "range_str": "12.0 - 17.5 g/dL",
        "low": 12.0,
        "high": 17.5,
        "operator": "interval"
    },
    "wbc": {
        "unit": "10^3/uL",
        "range_str": "4.0 - 11.0 10^3/uL",
        "low": 4.0,
        "high": 11.0,
        "operator": "interval"
    },
    "platelets": {
        "unit": "10^3/uL",
        "range_str": "150 - 450 10^3/uL",
        "low": 150.0,
        "high": 450.0,
        "operator": "interval"
    },
    "rbc": {
        "unit": "mil/uL",
        "range_str": "4.2 - 5.8 mil/uL",
        "low": 4.2,
        "high": 5.8,
        "operator": "interval"
    },
    "tsh": {
        "unit": "uIU/mL",
        "range_str": "0.4 - 4.2 uIU/mL",
        "low": 0.4,
        "high": 4.2,
        "operator": "interval"
    },
    "vitamin_d": {
        "unit": "ng/mL",
        "range_str": "30 - 100 ng/mL",
        "low": 30.0,
        "high": 100.0,
        "operator": "interval"
    },
    "vitamin_b12": {
        "unit": "pg/mL",
        "range_str": "200 - 900 pg/mL",
        "low": 200.0,
        "high": 900.0,
        "operator": "interval"
    },
    "calcium_serum": {
        "unit": "mg/dL",
        "range_str": "8.5 - 10.5 mg/dL",
        "low": 8.5,
        "high": 10.5,
        "operator": "interval"
    },
}

def parse_range_bounds(range_str: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Parses standard laboratory intervals and one-sided thresholds:
    e.g.:
      '70 - 99 mg/dL' -> (70.0, 99.0, 'interval')
      '0.7 to 1.3'    -> (0.7, 1.3, 'interval')
      '< 5.7 %'       -> (None, 5.7, '<')
      '<= 200'        -> (None, 200.0, '<=')
      '> 40 mg/dL'    -> (40.0, None, '>')
      '>= 60'         -> (60.0, None, '>=')
      
    Returns: (low_bound, high_bound, operator_type)
    """
    if not range_str:
        return None, None, None
        
    s = range_str.strip()

    # Check standard interval "A - B" or "A to B"
    m_range = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)", s, re.IGNORECASE)
    if m_range:
        return float(m_range.group(1)), float(m_range.group(2)), "interval"
    
    # Check "<=" or "≤"
    m_le = re.search(r"(?:<=|≤)\s*(\d+(?:\.\d+)?)", s)
    if m_le:
        return None, float(m_le.group(1)), "<="

    # Check "<"
    m_less = re.search(r"<\s*(\d+(?:\.\d+)?)", s)
    if m_less:
        return None, float(m_less.group(1)), "<"
        
    # Check ">=" or "≥"
    m_ge = re.search(r"(?:>=|≥)\s*(\d+(?:\.\d+)?)", s)
    if m_ge:
        return float(m_ge.group(1)), None, ">="

    # Check ">"
    m_greater = re.search(r">\s*(\d+(?:\.\d+)?)", s)
    if m_greater:
        return float(m_greater.group(1)), None, ">"
        
    return None, None, None


def classify_measurement(
    value_str: str,
    range_str: Optional[str] = None,
    printed_flag: Optional[str] = None,
    is_qualitative: bool = False,
    canonical_name: Optional[str] = None,
    unit: Optional[str] = None
) -> Tuple[str, str, Dict[str, Any]]:
    """
    Classifies a measurement as:
    - 'HIGH'
    - 'LOW'
    - 'WITHIN_RANGE'
    - 'NEEDS_REVIEW'
    
    Enforces strict precedence:
    1. Valid printed lab interval on the report
    2. Validated assay-specific fallback from metadata (if units match)
    3. Printed flags if available
    4. Needs review / range unavailable

    Returns: (status, classification_reason, details_dict)
    """
    details: Dict[str, Any] = {
        "source": "unspecified",
        "applied_range": range_str,
        "is_fallback": False,
        "low_bound": None,
        "high_bound": None,
        "operator": None,
    }

    if is_qualitative:
        clean = (value_str or "").strip().lower()
        if clean in ["negative", "non-reactive", "non reactive", "normal", "nil", "absent", "not detected"]:
            details["source"] = "qualitative_non_reactive"
            return "WITHIN_RANGE", "Qualitative result is non-reactive/normal", details
        elif clean in ["positive", "reactive", "abnormal", "detected", "present"]:
            details["source"] = "qualitative_reactive"
            return "NEEDS_REVIEW", "Qualitative result reported as reactive/detected; requires clinical review", details
        details["source"] = "qualitative_unclear"
        return "NEEDS_REVIEW", "Qualitative reading requires clinician review", details

    if not value_str or str(value_str).strip() == "":
        details["source"] = "missing_value"
        return "NEEDS_REVIEW", "Measurement value missing or unreadable", details

    try:
        val = float(value_str)
    except (ValueError, TypeError):
        # Non-numeric string in numeric assay
        details["source"] = "unparseable_value"
        return "NEEDS_REVIEW", f"Unable to parse numeric reading from '{value_str}'", details

    # Step 1: Check printed range
    low_bound, high_bound, op = parse_range_bounds(range_str) if range_str else (None, None, None)
    is_fallback = False

    # Step 2: If printed range is missing or unparseable, check assay fallback with unit validation
    if low_bound is None and high_bound is None and canonical_name and canonical_name in VALIDATED_ASSAY_FALLBACKS:
        fallback_meta = VALIDATED_ASSAY_FALLBACKS[canonical_name]
        expected_unit = fallback_meta["unit"].lower().strip()
        actual_unit = (unit or "").lower().strip()

        # If unit matches or is unspecified, apply validated fallback
        if not actual_unit or actual_unit == expected_unit:
            low_bound = fallback_meta["low"]
            high_bound = fallback_meta["high"]
            op = fallback_meta["operator"]
            is_fallback = True
            details["applied_range"] = fallback_meta["range_str"]
            details["is_fallback"] = True

    details["low_bound"] = low_bound
    details["high_bound"] = high_bound
    details["operator"] = op

    # Evaluate against parsed bounds
    if low_bound is not None and high_bound is not None:
        source_label = "fallback reference range" if is_fallback else "printed laboratory reference range"
        details["source"] = "fallback_interval" if is_fallback else "printed_interval"
        if val < low_bound:
            return "LOW", f"{val} is below the {source_label} ({low_bound} - {high_bound})", details
        elif val > high_bound:
            return "HIGH", f"{val} is above the {source_label} ({low_bound} - {high_bound})", details
        else:
            return "WITHIN_RANGE", f"{val} is within the {source_label} ({low_bound} - {high_bound})", details

    if high_bound is not None:
        source_label = "fallback threshold" if is_fallback else "target upper threshold"
        details["source"] = "fallback_upper_bound" if is_fallback else "printed_upper_bound"
        if op == "<=":
            if val > high_bound:
                return "HIGH", f"{val} exceeds {source_label} (<= {high_bound})", details
            return "WITHIN_RANGE", f"{val} is within {source_label} (<= {high_bound})", details
        else:  # default "<"
            if val >= high_bound:
                return "HIGH", f"{val} exceeds or meets {source_label} (< {high_bound})", details
            return "WITHIN_RANGE", f"{val} is within {source_label} (< {high_bound})", details

    if low_bound is not None:
        source_label = "fallback threshold" if is_fallback else "target lower threshold"
        details["source"] = "fallback_lower_bound" if is_fallback else "printed_lower_bound"
        if op == ">=":
            if val < low_bound:
                return "LOW", f"{val} is below {source_label} (>= {low_bound})", details
            return "WITHIN_RANGE", f"{val} meets {source_label} (>= {low_bound})", details
        else:  # default ">"
            if val <= low_bound:
                return "LOW", f"{val} is at or below {source_label} (> {low_bound})", details
            return "WITHIN_RANGE", f"{val} meets {source_label} (> {low_bound})", details

    # Step 3: Check explicit printed high/low flags
    if printed_flag:
        flag_upper = str(printed_flag).strip().upper()
        if "H" in flag_upper or "HIGH" in flag_upper:
            details["source"] = "printed_flag_high"
            return "HIGH", "Report includes explicit printed HIGH indicator", details
        if "L" in flag_upper or "LOW" in flag_upper:
            details["source"] = "printed_flag_low"
            return "LOW", "Report includes explicit printed LOW indicator", details

    # Step 4: Range unavailable / Needs Review
    details["source"] = "range_unavailable"
    return "NEEDS_REVIEW", "No applicable laboratory reference interval available; needs clinician context", details
