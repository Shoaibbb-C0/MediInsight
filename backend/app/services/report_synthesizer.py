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
    personal_baselines: Optional[List[Dict[str, Any]]] = None,
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
            context_insights.append("Context questions were skipped or unanswered. Only available report evidence is summarized; clinical interpretation needs your history.")
    else:
        # Fasting context
        fasting_opt = answer_map.get("q_glucose_fasting")
        if fasting_opt == "fasting_strictly":
            if lang == "hi":
                context_insights.append("क्योंकि आपने पूरी तरह खाली पेट (१०+ घंटे) रक्त दिया था, इसलिए आपकी फास्टिंग शुगर आपके मेटाबॉलिक स्तर का सटीक आधार दर्शाती है।")
            elif lang == "mr":
                context_insights.append("तुम्ही पूर्णपणे उपाशीपोटी (१०+ तास) रक्त तपासणी केली असल्याने, तुमच्या ग्लुकोजची पातळी अचूक मूलभूत चयापचय स्थिती दर्शवते.")
            else:
                context_insights.append("You reported fasting overnight. This helps your clinician assess whether the fasting interval applies; it does not confirm a diagnosis.")
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
                context_insights.append("आपने थकान और चक्कर आने की सूचना दी है, जिसके कई कारण हो सकते हैं। इसे डॉक्टर को बताएँ।")
            elif lang == "mr":
                context_insights.append("तुम्हाला जाणवणारा थकवा आणि चक्कर हिमोग्लोबिन कमी असल्यामुळे पेशींना ऑक्सिजन कमी मिळण्याशी संबंधित असू शकते.")
            else:
                context_insights.append("You noted noticeable fatigue and lightheadedness, which can have several causes and should be discussed with your clinician.")

        # Sunlight
        sun_opt = answer_map.get("q_vitd_sun_habits")
        if sun_opt == "sun_rarely":
            if lang == "hi":
                context_insights.append("आपने बताया कि आप सीधी धूप में बहुत कम समय बिताते हैं। यह डॉक्टर के लिए उपयोगी संदर्भ है, लेकिन कम विटामिन डी का कारण सिद्ध नहीं करता।")
            elif lang == "mr":
                context_insights.append("तुम्ही कोवळ्या उन्हात फार कमी वेळ घालवत असल्याने, हा डॉक्टरांसाठी उपयुक्त संदर्भ आहे, पण व्हिटॅमिन डी कमी होण्याचे कारण सिद्ध करत नाही.")
            else:
                context_insights.append("You shared that you rarely spend time in direct sunlight. This is relevant context for your clinician, but does not establish the cause of a low vitamin D reading.")

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
            f"Your remaining {len(normal_items)} test{'s' if len(normal_items) != 1 else ''} are within the applicable laboratory intervals; this does not rule out illness."
        )

    summary_text = {
        'en':f"{len(abnormal_items)} readings need attention; {len(normal_items)} are within the applicable lab intervals. {len(unreliable_extractions)} readings remain unverified. This does not establish a diagnosis or rule out illness.",
        'hi':f"जाँच में {len(abnormal_items)} मापों पर ध्यान चाहिए; {len(normal_items)} लागू प्रयोगशाला सीमा में हैं। {len(unreliable_extractions)} माप अपुष्ट हैं। इससे निदान तय नहीं होता और बीमारी से इंकार नहीं किया जा सकता।",
        'mr':f"तपासणीत {len(abnormal_items)} मोजमापांकडे लक्ष हवे; {len(normal_items)} लागू प्रयोगशाळा मर्यादेत आहेत. {len(unreliable_extractions)} मोजमाप अपुष्ट आहेत. यावरून निदान ठरत नाही किंवा आजार नाकारता येत नाही."
    }[lang]
    if lang in ['hi','mr']:
        for trend in historical_trends:
            if 'current_value' in trend:
                movement=f"{trend.get('previous_value')} → {trend.get('current_value')} {trend.get('unit','')}"
                trend['concise_summary']=('माप में संख्यात्मक बदलाव: ' if lang=='hi' else 'मोजमापातील संख्यात्मक बदल: ')+movement
                trend['interpretation_note']='इस अंतर का अर्थ डॉक्टर से समझें।' if lang=='hi' else 'या फरकाचा अर्थ डॉक्टरांकडून समजून घ्या.'
            else: trend['explanation']='तुलना के लिए इकाइयाँ मेल नहीं खातीं।' if lang=='hi' else 'तुलनेसाठी एकके जुळत नाहीत.'
        for baseline in personal_baselines or []:
            baseline['label']='पिछली तुलनीय रिपोर्ट के माप' if lang=='hi' else 'मागील तुलनीय अहवालांतील मोजमाप'
            baseline['relation_to_baseline']='यह ऐतिहासिक विवरण है, चिकित्सीय सामान्य सीमा नहीं।' if lang=='hi' else 'हे ऐतिहासिक वर्णन आहे, वैद्यकीय सामान्य मर्यादा नाही.'

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
            why_outside = {"en":"Requires review with healthcare provider.","hi":"स्वास्थ्य विशेषज्ञ से समीक्षा आवश्यक है।","mr":"आरोग्य तज्ज्ञांकडून तपासणी आवश्यक आहे."}.get(lang)
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
            "flag_reason": {"en":"Low optical recognition confidence or ambiguous formatting. Excluded from interpretation for safety.","hi":"अस्पष्ट पाठ या स्वरूप के कारण यह माप व्याख्या से अलग रखा गया है।","mr":"अस्पष्ट मजकूर किंवा रचनेमुळे हे मोजमाप विश्लेषणातून वगळले आहे."}.get(lang)
        })

    # Localized Doctor Questions
    doctor_questions = []
    if lang == "hi":
        doctor_questions = [
            "इन परीक्षण परिणामों और मेरी दिनचर्या को देखते हुए सबसे पहले क्या बदलाव करने चाहिए?",
            "क्या कोई जाँच दोबारा करनी चाहिए और कब?",
            "क्या दवा या भोजन में बदलाव से पहले इन नतीजों की और जाँच आवश्यक है?"
        ]
        safe_steps = [
            "अपने चिकित्सक से इन परिणामों पर सामान्य परामर्श का समय निर्धारित करें।",
            "पर्याप्त मात्रा में पानी पिएं और बिना डॉक्टर की सलाह के कोई नया सप्लीमेंट शुरू न करें।",
            "यदि सीने में दर्द, सांस लेने में तकलीफ या रक्तस्राव हो, तो तुरंत आपातकालीन चिकित्सा सहायता लें।"
        ]
    elif lang == "mr":
        doctor_questions = [
            "या निकालांनुसार आणि माझ्या जीवनशैलीनुसार सुरुवातीला कोणते बदल करावेत?",
            "कोणती चाचणी पुन्हा करावी आणि कधी?",
            "औषध किंवा आहार बदलण्यापूर्वी या निकालांची आणखी तपासणी आवश्यक आहे का?"
        ]
        safe_steps = [
            "या चाचण्यांच्या निकालांवर डॉक्टरांशी चर्चा करण्यासाठी सर्वसाधारण भेट ठरवा.",
            "शरीरात पुरेसे पाणी ठेवा आणि डॉक्टरांच्या सल्ल्याशिवाय स्वतःहून औषधे किंवा सप्लिमेंट्स सुरू करू नका.",
            "छातीत दुखणे, धाप लागणे किंवा रक्तस्राव यांसारखा त्रास झाल्यास तात्काळ वैद्यकीय मदत घ्या."
        ]
    else:
        doctor_questions = [
            "Based on these numbers and how I am feeling, what lifestyle adjustments should we start with?",
            "Should any tests be repeated, and at what interval?",
            "Do any of these reported findings need further assessment before changing medicines or food habits?"
        ]
        safe_steps = [
            "Discuss the results and the appropriate urgency with your clinician.",
            "Follow clinician advice on fluids, medicines and supplements.",
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
        "personal_baselines": personal_baselines or [],
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
        ]
    }
