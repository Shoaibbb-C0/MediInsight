"""
Abnormality Detection and Reference Range Classification Engine for Simplifier 2.0.
Accurately categorizes quantitative and qualitative medical laboratory measurements
strictly preserving exact original numbers, units, printed flags, and provenance.
"""

import re
from typing import Tuple, Optional, Dict, Any

def parse_range_bounds(range_str: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parses standard laboratory intervals:
    e.g. '70 - 99 mg/dL', '0.7 - 1.3', '< 5.7 %', '> 40 mg/dL', '<= 200'
    """
    if not range_str:
        return None, None
        
    s = range_str.strip()
    
    # Check "< 5.7" or "<= 200"
    m_less = re.search(r"[<≤]\s*(\d+(?:\.\d+)?)", s)
    if m_less:
        return None, float(m_less.group(1))
        
    # Check "> 40" or ">= 40"
    m_greater = re.search(r"[>≥]\s*(\d+(?:\.\d+)?)", s)
    if m_greater:
        return float(m_greater.group(1)), None
        
    # Check standard interval "A - B" or "A to B"
    m_range = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)", s)
    if m_range:
        return float(m_range.group(1)), float(m_range.group(2))
        
    return None, None

def classify_measurement(
    value_str: str,
    range_str: Optional[str] = None,
    printed_flag: Optional[str] = None,
    is_qualitative: bool = False
) -> Tuple[str, str]:
    """
    Classifies a measurement as:
    - 'HIGH'
    - 'LOW'
    - 'WITHIN_RANGE'
    - 'NEEDS_REVIEW'
    
    Returns: (status, classification_reason)
    """
    if is_qualitative:
        # For qualitative tests (e.g. Negative/Non-reactive/Normal)
        clean = (value_str or "").strip().lower()
        if clean in ["negative", "non-reactive", "normal", "nil"]:
            return "WITHIN_RANGE", "Qualitative result is non-reactive/normal"
        elif clean in ["positive", "reactive", "abnormal", "detected"]:
            return "NEEDS_REVIEW", "Qualitative result reported as reactive/detected"
        return "NEEDS_REVIEW", "Qualitative reading requires clinician review"

    if not value_str or value_str.strip() == "":
        return "NEEDS_REVIEW", "Measurement value missing or unreadable"

    try:
        val = float(value_str)
    except (ValueError, TypeError):
        # Non-numeric text in numeric assay
        return "NEEDS_REVIEW", f"Unable to parse numeric reading from '{value_str}'"

    # Priority 1: Valid applicable laboratory-printed range
    low_bound, high_bound = parse_range_bounds(range_str) if range_str else (None, None)

    if low_bound is not None and high_bound is not None:
        if val < low_bound:
            return "LOW", f"{val} is below the printed laboratory reference range ({low_bound} - {high_bound})"
        elif val > high_bound:
            return "HIGH", f"{val} is above the printed laboratory reference range ({low_bound} - {high_bound})"
        else:
            return "WITHIN_RANGE", f"{val} is within the printed laboratory reference range ({low_bound} - {high_bound})"

    if high_bound is not None:
        if val > high_bound:
            return "HIGH", f"{val} exceeds target upper threshold (< {high_bound})"
        else:
            return "WITHIN_RANGE", f"{val} is within target threshold (< {high_bound})"

    if low_bound is not None:
        if val < low_bound:
            return "LOW", f"{val} is below target lower threshold (> {low_bound})"
        else:
            return "WITHIN_RANGE", f"{val} meets target lower threshold (> {low_bound})"

    # Priority 2: Use printed high/low flag if explicit
    if printed_flag:
        flag_upper = printed_flag.strip().upper()
        if "H" in flag_upper or "HIGH" in flag_upper:
            return "HIGH", "Report includes explicit printed HIGH indicator"
        if "L" in flag_upper or "LOW" in flag_upper:
            return "LOW", "Report includes explicit printed LOW indicator"

    return "NEEDS_REVIEW", "No applicable laboratory reference interval available; needs clinician context"
