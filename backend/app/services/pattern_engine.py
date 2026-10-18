"""
Historical Comparison and Conservative Multi-Result Pattern Engine for Simplifier 2.0.
Computes compatible unit trends without falsely declaring improvements,
and evaluates conservative, medically reviewed biomarker patterns.
"""

from typing import List, Dict, Any, Optional
import math
from collections import Counter

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

    duplicates=Counter(item.get("canonical_name") for item in latest_past.measurements)
    current_counts=Counter(item.get("canonical_name") for item in current_measurements)
    trends = []
    for curr in current_measurements:
        if curr.get("requires_verification") or curr.get("status") == "needs_review": continue
        canonical = curr.get("canonical_name")
        if not canonical or canonical not in past_map or duplicates[canonical]>1 or current_counts[canonical]>1:
            continue

        past = past_map[canonical]
        if past.get("requires_verification") or past.get("status") == "needs_review": continue
        if (curr.get("reference_range") or "") != (past.get("reference_range") or ""): continue
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
            if not math.isfinite(curr_val) or not math.isfinite(past_val): continue
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

def detect_conservative_medical_patterns(measurements: List[Dict[str, Any]], lang: str = "en") -> List[Dict[str, Any]]:
    """Use reliable source classifications, never fixed thresholds or example values."""
    reliable = {item.get('canonical_name'):item for item in measurements if not item.get('requires_verification') and item.get('status') in ['high','low','normal','within_range']}
    patterns=[]
    if all(reliable.get(name,{}).get('status') == 'high' for name in ['glucose_fasting','hba1c']):
        texts = {
            'en':['Blood Sugar Regulation Pattern','Both glucose and HbA1c are above their applicable laboratory intervals. These results alone do not establish a diagnosis.','Discuss these measurements and your fasting status with your clinician.','Recent dietary changes, temporary illness, stress or sleep changes may affect interpretation.','Symptoms, medicines, test conditions and clinical history remain necessary.','Do these results need confirmation or further assessment?'],
            'hi':['रक्त शर्करा का संयुक्त संकेत','ग्लूकोज और HbA1c दोनों लागू प्रयोगशाला सीमा से ऊपर हैं। केवल इनसे निदान तय नहीं होता।','माप और खाली पेट जाँच की स्थिति डॉक्टर से साझा करें।','हाल का भोजन, बीमारी, तनाव या नींद में बदलाव व्याख्या को प्रभावित कर सकते हैं।','लक्षण, दवाएँ, जाँच की स्थिति और चिकित्सा इतिहास आवश्यक हैं।','क्या इन नतीजों की पुष्टि या आगे जाँच की ज़रूरत है?'],
            'mr':['रक्तातील साखरेचा संयुक्त संकेत','ग्लुकोज आणि HbA1c दोन्ही लागू प्रयोगशाळा मर्यादेपेक्षा जास्त आहेत. फक्त यावरून निदान ठरत नाही.','मोजमाप आणि उपाशीपोटी तपासणीची स्थिती डॉक्टरांशी बोला.','अलीकडील अन्न, आजार, ताण किंवा झोपेतील बदल अर्थ लावण्यावर परिणाम करू शकतात.','लक्षणे, औषधे, तपासणीची परिस्थिती आणि वैद्यकीय इतिहास आवश्यक आहेत.','या निकालांची पुष्टी किंवा अधिक तपासणी हवी आहे का?']
        }.get(lang)
        if texts is None: return detect_conservative_medical_patterns(measurements,'en')
        patterns.append(dict(zip(['pattern_name','summary','what_this_means','alternative_explanations','missing_evidence','questions_for_doctor'],texts),finding_level='attention_recommended'))
    vitamin=reliable.get('vitamin_d')
    if vitamin and vitamin.get('status')=='low':
        reading=f"{vitamin.get('value','')} {vitamin.get('unit','')}".strip()
        interval=vitamin.get('reference_range','')
        texts={
            'en':['Vitamin D result to discuss',f"Reported vitamin D: {reading}; laboratory interval: {interval}. The source classifies this reading as low.",'Ask your clinician about the meaning of this result in your circumstances.','Diet, medicines, health conditions and test methods may affect this result.','Clinical history and applicable test conditions are not established here.','Is confirmation or an individualized management plan appropriate?'],
            'hi':['विटामिन डी पर चर्चा करें',f"विटामिन डी: {reading}; प्रयोगशाला सीमा: {interval}। स्रोत के अनुसार माप कम है।",'अपनी परिस्थिति में इस परिणाम का अर्थ डॉक्टर से पूछें।','भोजन, दवाएँ, स्वास्थ्य स्थिति और जाँच विधि प्रभाव डाल सकते हैं।','चिकित्सा इतिहास और जाँच की पूरी स्थिति यहाँ ज्ञात नहीं है।','क्या पुष्टि या व्यक्तिगत उपचार योजना आवश्यक है?'],
            'mr':['व्हिटॅमिन डीबद्दल चर्चा करा',f"व्हिटॅमिन डी: {reading}; प्रयोगशाळा मर्यादा: {interval}. स्रोतानुसार मोजमाप कमी आहे.",'तुमच्या परिस्थितीत या निकालाचा अर्थ डॉक्टरांना विचारा.','आहार, औषधे, आरोग्यस्थिती आणि तपासणीची पद्धत परिणाम करू शकतात.','वैद्यकीय इतिहास आणि तपासणीची संपूर्ण माहिती येथे ज्ञात नाही.','पुष्टी किंवा वैयक्तिक उपचार योजनेची गरज आहे का?']
        }.get(lang)
        if texts is None: return detect_conservative_medical_patterns(measurements,'en')
        patterns.append(dict(zip(['pattern_name','summary','what_this_means','alternative_explanations','missing_evidence','questions_for_doctor'],texts),finding_level='attention_recommended'))
    return patterns


def compute_personal_baselines(
    current_measurements: List[Dict[str, Any]],
    historical_records: List[Any],
    min_reports: int = 4
) -> List[Dict[str, Any]]:
    """
    Computes history-aware descriptive personal baselines across longitudinal reports.
    Requirements:
    - Only triggered when at least 4 medically comparable reports exist for the canonical test.
    - Strictly checks measurement unit compatibility and canonical test identity.
    - Descriptive only: calculates median, observed min, observed max.
    - Explicitly labeled: "Your usual readings across previous reports" (NEVER labeled 'normal' or 'healthy').
    - Keeps the laboratory reference range strictly separate.
    """
    if not historical_records or len(historical_records) < (min_reports - 1):
        # We need at least (min_reports - 1) previous reports plus current, or min_reports historical
        return []

    import statistics

    baselines = []
    current_counts=Counter(item.get("canonical_name") for item in current_measurements)

    for curr in current_measurements:
        if curr.get("requires_verification") or curr.get("status") == "needs_review": continue
        canonical = curr.get("canonical_name")
        if not canonical or current_counts[canonical]>1:
            continue

        curr_unit = (curr.get("unit") or "").strip().lower()
        
        # Collect numeric values from historical records with compatible unit
        past_values = []
        incompatible_unit_count = 0
        dates_observed = []

        for record in historical_records:
            record_date = getattr(record, "report_date", None) or (record.get("report_date") if isinstance(record, dict) else "Past Report")
            measurements = getattr(record, "measurements", []) if hasattr(record, "measurements") else (record.get("measurements", []) if isinstance(record, dict) else [])
            if sum(item.get("canonical_name")==canonical for item in measurements) != 1: continue
            for item in measurements:
                if item.get("canonical_name") == canonical and not item.get("requires_verification") and item.get("status") != "needs_review" and (item.get("reference_range") or "") == (curr.get("reference_range") or ""):
                    past_u = (item.get("unit") or "").strip().lower()
                    if past_u == curr_unit:
                        try:
                            v = float(item.get("value"))
                            if not math.isfinite(v): continue
                            past_values.append(v)
                            dates_observed.append(record_date)
                        except (ValueError, TypeError):
                            pass
                    else:
                        incompatible_unit_count += 1

        # Check if we have at least min_reports (including current value if parsed)
        try:
            curr_val = float(curr.get("value"))
            if not math.isfinite(curr_val): continue
            all_series = past_values + [curr_val]
        except (ValueError, TypeError):
            all_series = past_values

        if len(all_series) >= min_reports:
            med = round(float(statistics.median(all_series)), 2)
            obs_min = round(float(min(all_series)), 2)
            obs_max = round(float(max(all_series)), 2)
            curr_v_float = float(curr.get("value", 0))

            # Direction relative to personal baseline median
            diff_from_median = round(curr_v_float - med, 2)
            if abs(diff_from_median) < 0.05:
                relation_to_baseline = "Matches your usual median reading"
            elif diff_from_median > 0:
                relation_to_baseline = f"{diff_from_median} above your usual median reading"
            else:
                relation_to_baseline = f"{abs(diff_from_median)} below your usual median reading"

            baselines.append({
                "canonical_name": canonical,
                "name": curr.get("name"),
                "report_count": len(all_series),
                "unit": curr.get("unit"),
                "median_value": med,
                "observed_min": obs_min,
                "observed_max": obs_max,
                "current_value": curr.get("value"),
                "relation_to_baseline": relation_to_baseline,
                "label": "Your usual readings across previous reports",
                "descriptive_summary": (
                    f"Across your last {len(all_series)} reports, your readings have typically ranged from "
                    f"{obs_min} to {obs_max} {curr.get('unit')} (median: {med} {curr.get('unit')})."
                ),
                "clinical_distinction_note": (
                    "This represents your personal historical baseline across previous records. "
                    "It is descriptive of past observations and does not replace the standard laboratory reference range."
                )
            })

    return baselines
