"""
Personalized Insight & Smart Report Synthesizer for Simplifier 2.0.
Integrates patient questionnaire answers, historical records, and warning signs
into the final 7-part Smart Report structure.
Supports multilingual output (en, hi, mr) with clinical translation tracking.
"""

from typing import List, Dict, Any, Optional
from app.services.multilingual_registry import (
    get_localized_ui,
    get_localized_biomarker,
    TRANSLATION_REVIEW_REGISTRY
)

def synthesize_smart_report(
    report_id: str,
    extractions: List[Dict[str, Any]],
    answers: List[Dict[str, Any]],
    historical_trends: List[Dict[str, Any]],
    clinical_patterns: List[Dict[str, Any]],
    test_purposes: List[Dict[str, Any]],
    is_synthetic_fixture: bool = False,
    lang: str = "en"
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
    ui = get_localized_ui(lang)
    lang_info = TRANSLATION_REVIEW_REGISTRY["languages"].get(lang, TRANSLATION_REVIEW_REGISTRY["languages"]["en"])

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
            "title": ui["urgentAlertTitle"],
            "guidance": ui["urgentAlertGuidance"]
        }

    # Separate measurements: reliable vs unreliable/uncertain
    # Unreliable measurements (requires_verification == True) are EXCLUDED from definitive interpretation
    reliable_extractions = []
    unreliable_extractions = []
    for b in extractions:
        if b.get("requires_verification"):
            unreliable_extractions.append(b)
        else:
            reliable_extractions.append(b)

    # Group reliable measurements by status
    abnormal_items = [b for b in reliable_extractions if b.get("status") in ["high", "low", "needs_review"]]
    normal_items = [b for b in reliable_extractions if b.get("status") in ["normal", "within_range"]]

    # Section E: What your answers tell us
    context_insights = []
    if not answers:
        if lang == "hi":
            context_insights.append("आपने संदर्भ प्रश्नों के उत्तर नहीं दिए। हमने आपके परीक्षणों की व्याख्या तटस्थ नैदानिक आधार पर की है।")
        elif lang == "mr":
            context_insights.append("तुम्ही संदर्भातील प्रश्न वगळले आहेत. आम्ही चाचण्यांचे विश्लेषण मूलभूत वैद्यकीय निकषांवर आधारित केले आहे.")
        else:
            context_insights.append("You skipped or haven't answered context questions yet. We have interpreted your measurements with neutral baseline medical assumptions.")
    else:
        # Fasting context
        fasting_opt = answer_map.get("q_glucose_fasting")
        if fasting_opt == "fasting_strictly":
            if lang == "hi":
                context_insights.append("क्योंकि आपने पूरी तरह खाली पेट (१०+ घंटे) रक्त दिया था, इसलिए आपकी फास्टिंग शुगर आपके मेटाबॉलिक स्तर का सटीक आधार दर्शाती है।")
            elif lang == "mr":
                context_insights.append("तुम्ही पूर्णपणे उपाशीपोटी (१०+ तास) रक्त तपासणी केली असल्याने, तुमच्या ग्लुकोजची पातळी अचूक मूलभूत चयापचय स्थिती दर्शवते.")
            else:
                context_insights.append("Since you strictly fasted overnight, your blood glucose reading provides an accurate baseline reflection of resting sugar regulation.")
        elif fasting_opt == "fasting_had_bite":
            if lang == "hi":
                context_insights.append("क्योंकि आपने जाँच से पहले चाय या हल्का नाश्ता लिया था, इसलिए बढ़ी हुई शुगर हालिया भोजन के कारण भी हो सकती है।")
            elif lang == "mr":
                context_insights.append("तपासणीपूर्वी तुम्ही चहा किंवा नाश्ता घेतल्याने, वाढलेली साखर तात्पुरती अन्नामुळे वाढलेली असू शकते.")
            else:
                context_insights.append("Because you mentioned having a snack or beverage before the test, your elevated glucose may partly reflect recent dietary sugar absorption rather than an abnormal fasting baseline.")

        # Symptoms
        symptom_opt = answer_map.get("q_hemo_fatigue")
        if symptom_opt == "fatigue_yes":
            if lang == "hi":
                context_insights.append("आपने थकान और चक्कर आने की सूचना दी है, जो कम हीमोग्लोबिन के कारण ऑक्सीजन प्रवाह में कमी से मेल खाता है।")
            elif lang == "mr":
                context_insights.append("तुम्हाला जाणवणारा थकवा आणि चक्कर हिमोग्लोबिन कमी असल्यामुळे पेशींना ऑक्सिजन कमी मिळण्याशी संबंधित असू शकते.")
            else:
                context_insights.append("You noted noticeable fatigue and lightheadedness, which correlates with reduced oxygen-carrying capacity from your low hemoglobin reading.")

        # Sunlight
        sun_opt = answer_map.get("q_vitd_sun_habits")
        if sun_opt == "sun_rarely":
            if lang == "hi":
                context_insights.append("आपने बताया कि आप सीधी धूप में बहुत कम समय बिताते हैं। यह आपके विटामिन डी के कम स्तर का एक सीधा और सहज कारण है।")
            elif lang == "mr":
                context_insights.append("तुम्ही कोवळ्या उन्हात फार कमी वेळ घालवत असल्याने, व्हिटॅमिन डी कमी असण्याचे हे एक स्वाभाविक कारण आहे.")
            else:
                context_insights.append("You shared that you rarely spend time in direct sunlight. This provides a clear, everyday lifestyle explanation for your lower Vitamin D reading.")

    # High / Low summary count
    if lang == "hi":
        summary_text = (
            f"आपकी जाँच में {len(abnormal_items)} परिणाम सामान्य प्रयोगशाला सीमा से बाहर मिले हैं। "
            f"आपके शेष {len(normal_items)} परीक्षण पूरी तरह संतुलित और सामान्य स्थिति में हैं।"
        )
    elif lang == "mr":
        summary_text = (
            f"तपासणीत {len(abnormal_items)} निकाल नेहमीच्या संदर्भ मर्यादेपेक्षा बाहेर आढळले आहेत. "
            f"उर्वरित {len(normal_items)} चाचण्या पूर्णपणे चांगल्या आणि संतुलित स्थितीत आहेत."
        )
    else:
        summary_text = (
            f"We found {len(abnormal_items)} result{'s' if len(abnormal_items) != 1 else ''} outside standard lab ranges. "
            f"Your remaining {len(normal_items)} test{'s' if len(normal_items) != 1 else ''} look reassuringly in healthy balance."
        )

    # Localized attention items
    prioritized_attention = []
    for b in abnormal_items:
        loc = get_localized_biomarker(b.get("canonical_name"), lang=lang)
        display_name = loc.get("name", b["name"]) if loc else b["name"]
        what_it_measures = loc.get("what_it_measures", "Checked to assess systemic organ regulation.") if loc else "Checked to assess systemic organ regulation."
        
        status_key = b.get("status", "needs_review").lower()
        if status_key == "high":
            why_outside = loc.get("high_explanation", f"{display_name} is higher than standard reference.") if loc else f"{display_name} is higher than standard reference."
            status_label = ui["high"]
        elif status_key == "low":
            why_outside = loc.get("low_explanation", f"{display_name} is lower than standard reference.") if loc else f"{display_name} is lower than standard reference."
            status_label = ui["low"]
        else:
            why_outside = "Requires review with healthcare provider."
            status_label = ui["needsReview"]

        prioritized_attention.append({
            "name": display_name,
            "original_name": b["name"],
            "canonical_name": b.get("canonical_name"),
            "value": f"{b['value']} {b['unit']}",
            "numeric_value": b['value'],
            "unit": b['unit'],
            "status": b["status"],
            "status_label": status_label,
            "reference_range": b["reference_range"],
            "provenance": b.get("correction_provenance", "initial_ocr"),
            "plain_summary": f"{display_name}: {b['value']} {b['unit']} ({status_label})",
            "what_it_measures": what_it_measures,
            "why_outside_range": why_outside
        })

    # Within-range normal items
    within_range_results = []
    for b in normal_items:
        loc = get_localized_biomarker(b.get("canonical_name"), lang=lang)
        display_name = loc.get("name", b["name"]) if loc else b["name"]
        within_range_results.append({
            "name": display_name,
            "original_name": b["name"],
            "canonical_name": b.get("canonical_name"),
            "value": f"{b['value']} {b['unit']}",
            "status": "normal",
            "status_label": ui["normal"],
            "reference_range": b["reference_range"]
        })

    # Unreliable flagged items (excluded from main interpretation)
    unreliable_flagged_results = []
    for b in unreliable_extractions:
        loc = get_localized_biomarker(b.get("canonical_name"), lang=lang)
        display_name = loc.get("name", b["name"]) if loc else b["name"]
        unreliable_flagged_results.append({
            "name": display_name,
            "original_name": b["name"],
            "extracted_text": b.get("original_extracted_value") or b.get("value"),
            "status": "unreliable_ocr",
            "confidence": b.get("confidence", 0.0),
            "flag_reason": "Low optical recognition confidence or ambiguous formatting. Excluded from interpretation for safety."
        })

    # Localized Doctor Questions
    doctor_questions = []
    if lang == "hi":
        doctor_questions = [
            "इन परीक्षण परिणामों और मेरी दिनचर्या को देखते हुए सबसे पहले क्या बदलाव करने चाहिए?",
            "क्या इनमें से किसी विशिष्ट जाँच को २ से ३ महीने बाद दोबारा दोहराने की सलाह देंगे?",
            "क्या मेरे विटामिन डी या मेटाबॉलिक स्वास्थ्य के लिए कोई सप्लीमेंट या सुरक्षित आहार सुझाव हैं?"
        ]
        safe_steps = [
            "अपने चिकित्सक से इन परिणामों पर सामान्य परामर्श का समय निर्धारित करें।",
            "पर्याप्त मात्रा में पानी पिएं और बिना डॉक्टर की सलाह के कोई नया सप्लीमेंट शुरू न करें।",
            "यदि सीने में दर्द, सांस लेने में तकलीफ या रक्तस्राव हो, तो तुरंत आपातकालीन चिकित्सा सहायता लें।"
        ]
    elif lang == "mr":
        doctor_questions = [
            "या निकालांनुसार आणि माझ्या जीवनशैलीनुसार सुरुवातीला कोणते बदल करावेत?",
            "यापैकी कोणतीही विशिष्ट तपासणी २ ते ३ महिन्यांनी पुन्हा करून घेण्याची गरज आहे का?",
            "माझ्या व्हिटॅमिन डी किंवा मेटाबॉलिक पातळीसाठी आपण कोणते सप्लिमेंट्स किंवा आहार सुचवाल?"
        ]
        safe_steps = [
            "या चाचण्यांच्या निकालांवर डॉक्टरांशी चर्चा करण्यासाठी सर्वसाधारण भेट ठरवा.",
            "शरीरात पुरेसे पाणी ठेवा आणि डॉक्टरांच्या सल्ल्याशिवाय स्वतःहून औषधे किंवा सप्लिमेंट्स सुरू करू नका.",
            "छातीत दुखणे, धाप लागणे किंवा रक्तस्राव यांसारखा त्रास झाल्यास तात्काळ वैद्यकीय मदत घ्या."
        ]
    else:
        doctor_questions = [
            "Based on these numbers and how I am feeling, what lifestyle adjustments should we start with?",
            "Would you like me to repeat any of these specific assays in 2 to 3 months?",
            "Are there any specific supplements or dietary habits you recommend for my Vitamin D and metabolic levels?"
        ]
        safe_steps = [
            "Schedule a non-urgent routine consultation to review these lab results with your physician.",
            "Maintain steady hydration and avoid making radical unsupervised supplement changes.",
            "If any new severe chest discomfort, breathlessness, or bleeding occurs, seek medical attention immediately."
        ]

    return {
        "report_id": report_id,
        "language": lang,
        "translation_review": lang_info,
        "is_synthetic_fixture": is_synthetic_fixture,
        "safety_alert": safety_alert,
        "patient_summary": summary_text,
        "heres_what_we_found": {
            "summary": summary_text,
            "total_reliable_tests": len(reliable_extractions),
            "total_unreliable_excluded": len(unreliable_extractions),
            "outside_range_count": len(abnormal_items),
            "within_range_count": len(normal_items)
        },
        "prioritized_attention": prioritized_attention,
        "within_range_results": within_range_results,
        "unreliable_flagged_results": unreliable_flagged_results,
        "historical_changes": historical_trends,
        "clinical_patterns": clinical_patterns,
        "test_purposes": test_purposes,
        "context_insights": context_insights,
        "suggested_doctor_questions": doctor_questions,
        "safe_next_steps": safe_steps,
        "disclaimer": ui["disclaimer"],
        "disclaimer_title": ui["disclaimerTitle"],
        # Backward compatibility for existing schemas and tests
        "results_needing_attention": [
            {
                "name": item["name"],
                "value": item["value"],
                "status": item["status"],
                "reference_range": item["reference_range"],
                "provenance": item.get("provenance", "initial_ocr"),
                "short_explanation": item["plain_summary"],
                "what_it_measures": item["what_it_measures"],
                "why_outside_range": item["why_outside_range"]
            }
            for item in prioritized_attention
        ],
        "what_your_answers_tell_us": {
            "answered_count": len(answers),
            "insights": context_insights,
            "missing_info": "Complete clinical history and formal exam remain unknown."
        },
        "what_to_discuss_with_doctor": {
            "suggested_questions": doctor_questions,
            "safe_next_steps": safe_steps
        },
        "key_findings": [
            {
                "biomarker_name": item["name"],
                "status": item["status"],
                "plain_english_summary": item["plain_summary"],
                "what_this_means": item["why_outside_range"],
                "reassurance": "This is an empowering early baseline to discuss with your doctor."
            }
            for item in prioritized_attention
        ] or [
            {
                "biomarker_name": "Routine Metabolic Panel",
                "status": "normal",
                "plain_english_summary": ui["allNormal"],
                "what_this_means": "Balanced counts and organ filtration.",
                "reassurance": "Reassuring baseline checkup."
            }
        ]
    }
