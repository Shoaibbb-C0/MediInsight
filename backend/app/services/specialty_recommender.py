"""
Clinical Specialty Recommendation Engine for Feature 3.
Deterministically maps verified Smart Report findings to appropriate specialties.
Explains the observed report finding and relevance without unsupported diagnostic claims.
Always provides General Physician as an accessible, safe entry point.
Urgent red-flag symptoms trigger immediate urgent care warning notices.
Supports English, Hindi, and Marathi.
"""

from typing import List, Dict, Any, Optional
from app.schemas.doctor import SpecialtyRecommendation

SPECIALTY_MAPPINGS_CONFIG = {
    "glucose_fasting": {
        "specialty_id": "endocrinology",
        "specialty_name": {
            "en": "Endocrinologist / Diabetologist",
            "hi": "एंडोक्रिनोलॉजिस्ट / डायबेटोलॉजिस्ट (हार्मोन व शुगर विशेषज्ञ)",
            "mr": "एंडोक्रिनोलॉजिस्ट / मधुमेह तज्ज्ञ"
        },
        "why": {
            "en": "Specializes in endocrine metabolism, insulin regulation, and blood glucose management.",
            "hi": "हार्मोनल संतुलन, इंसुलिन कार्यप्रणाली और रक्त शर्करा प्रबंधन में विशेषज्ञता रखते हैं।",
            "mr": "हार्मोनल समतोल, इन्सुलिनचे कार्य आणि रक्तातील साखरेच्या व्यवस्थापनामध्ये तज्ज्ञ."
        }
    },
    "hba1c": {
        "specialty_id": "endocrinology",
        "specialty_name": {
            "en": "Endocrinologist / Diabetologist",
            "hi": "एंडोक्रिनोलॉजिस्ट / डायबेटोलॉजिस्ट (हार्मोन व शुगर विशेषज्ञ)",
            "mr": "एंडोक्रिनोलॉजिस्ट / मधुमेह तज्ज्ञ"
        },
        "why": {
            "en": "Assists with long-term glycemic control, prediabetes management, and insulin sensitivity.",
            "hi": "दीर्घकालिक शुगर स्तर, प्रीडायबिटीज और इंसुलिन संवेदनशीलता के प्रबंधन में सहायता करते हैं।",
            "mr": "दीर्घकालीन साखरेची पातळी आणि प्रीडायबेटिसच्या व्यवस्थापनात मदत करतात."
        }
    },
    "creatinine_serum": {
        "specialty_id": "nephrology",
        "specialty_name": {
            "en": "Nephrologist (Kidney Specialist)",
            "hi": "नेफ्रोलॉजिस्ट (गुर्दा रोग विशेषज्ञ)",
            "mr": "नेफ्रोलॉजिस्ट (मूत्रपिंड तज्ज्ञ)"
        },
        "why": {
            "en": "Expert in glomerular filtration, fluid balance, and kidney health.",
            "hi": "गुर्दे की निस्पंदन क्षमता, द्रव संतुलन और किडनी के समग्र स्वास्थ्य के विशेषज्ञ।",
            "mr": "मूत्रपिंडाची गाळण क्षमता आणि आरोग्य व्यवस्थापनाचे तज्ज्ञ."
        }
    },
    "cholesterol_total": {
        "specialty_id": "cardiology",
        "specialty_name": {
            "en": "Cardiologist / Preventive Heart Specialist",
            "hi": "हृदय रोग विशेषज्ञ (कार्डियोलॉजिस्ट)",
            "mr": "हृदयरोग तज्ज्ञ (कार्डिओलॉजिस्ट)"
        },
        "why": {
            "en": "Focuses on arterial wellness, circulating lipid profiles, and cardiovascular risk reduction.",
            "hi": "धमनियों के स्वास्थ्य, रक्त वसा प्रोफाइल और हृदय संबंधी जोखिमों को कम करने पर ध्यान केंद्रित करते हैं।",
            "mr": "रक्तवाहिन्यांचे आरोग्य, रक्तातील चरबीचे प्रमाण आणि हृदयाच्या काळजीवर भर देतात."
        }
    },
    "hemoglobin": {
        "specialty_id": "hematology",
        "specialty_name": {
            "en": "Hematologist / Blood Specialist",
            "hi": "हेमेटोलॉजिस्ट (रक्त विकार विशेषज्ञ)",
            "mr": "हेमॅटोलॉजिस्ट (रक्त विकार तज्ज्ञ)"
        },
        "why": {
            "en": "Specializes in red blood cell production, iron metabolism, and anemia etiologies.",
            "hi": "लाल रक्त कोशिकाओं के निर्माण, आयरन चयापचय और एनीमिया के कारणों की गहन जाँच करते हैं।",
            "mr": "लाल रक्तपेशींची निर्मिती, लोहाचे शोषण आणि ॲनिमियाच्या कारणांची तपासणी करतात."
        }
    },
    "vitamin_d": {
        "specialty_id": "general_physician",
        "specialty_name": {
            "en": "General Physician / Family Medicine",
            "hi": "जनरल फिजिशियन (सामान्य चिकित्सा विशेषज्ञ)",
            "mr": "जनरल फिजिशियन (कुटुंब आरोग्य तज्ज्ञ)"
        },
        "why": {
            "en": "Guides safe oral vitamin D replenishment, routine sunlight habits, and general bone wellness.",
            "hi": "विटामिन डी सप्लीमेंट, दैनिक धूप की आदतों और समग्र स्वास्थ्य का सुरक्षित मार्गदर्शन करते हैं।",
            "mr": "व्हिटॅमिन डी सप्लिमेंट्स आणि दैनंदिन आरोग्याविषयी योग्य मार्गदर्शन करतात."
        }
    }
}

GENERAL_PHYSICIAN_INFO = {
    "specialty_id": "general_physician",
    "specialty_name": {
        "en": "General Physician & Internal Medicine",
        "hi": "जनरल फिजिशियन (आंतरिक चिकित्सा विशेषज्ञ)",
        "mr": "जनरल फिजिशियन व अंतर्गत औषधोपचार तज्ज्ञ"
    },
    "why": {
        "en": "The most versatile and accessible first step. Evaluates your whole medical history, rules out transient lab fluctuations, and coordinates care if a specialist is truly warranted.",
        "hi": "परामर्श का सबसे सुलभ और सुरक्षित पहला कदम। आपके संपूर्ण स्वास्थ्य इतिहास की समीक्षा करते हैं और आवश्यकता होने पर ही विशेषज्ञ की सलाह देते हैं।",
        "mr": "सल्लामसलतीची सर्वात सोपी आणि योग्य पहिली पायरी. संपूर्ण आरोग्याची तपासणी करून आवश्यक असल्यास पुढील तज्ज्ञांचे मार्गदर्शन सुचवतात."
    }
}

def generate_specialty_recommendations(
    extractions: List[Dict[str, Any]],
    answers: Optional[List[Dict[str, Any]]] = None,
    lang: str = "en"
) -> List[SpecialtyRecommendation]:
    """
    Evaluates findings and returns transparent, prioritized specialty suggestions.
    Checks urgent red-flag symptoms (e.g. bleeding + low counts) to display critical notice.
    """
    lang = lang if lang in ["en", "hi", "mr"] else "en"
    recs: List[SpecialtyRecommendation] = []
    seen_ids = set()

    # 1. Immediate Red Flag check
    urgent_warning = None
    if answers:
        for a in answers:
            q_id = a.get("question_id") if isinstance(a, dict) else getattr(a, "question_id", None)
            opt_id = a.get("selected_option_id") if isinstance(a, dict) else getattr(a, "selected_option_id", None)
            if q_id == "q_hemo_bleeding_signs" and opt_id == "bleed_concerning":
                urgent_warning = (
                    "URGENT: Because you reported visible bleeding or dark stools, seek prompt clinical evaluation today rather than waiting for a routine appointment."
                    if lang == "en" else
                    "महत्वपूर्ण: क्योंकि आपने रक्तस्राव की सूचना दी है, कृपया आज ही तुरंत किसी चिकित्सक से संपर्क करें।"
                    if lang == "hi" else
                    "तातडीची सूचना: तुम्ही रक्तस्रावाची नोंद केल्याने, नियमित वेळेची वाट न पाहता आजच डॉक्टरांशी संपर्क साधा."
                )

    # 2. Extract abnormal biomarkers
    abnormal = [
        b for b in extractions
        if b.get("status") in ["high", "low", "needs_review"] and not b.get("requires_verification")
    ]

    for b in abnormal:
        can = b.get("canonical_name")
        cfg = SPECIALTY_MAPPINGS_CONFIG.get(can)
        if cfg and cfg["specialty_id"] not in seen_ids:
            seen_ids.add(cfg["specialty_id"])
            recs.append(
                SpecialtyRecommendation(
                    specialty_id=cfg["specialty_id"],
                    specialty_name=cfg["specialty_name"][lang],
                    why_suggesting=cfg["why"][lang],
                    observed_finding=f"{b.get('name')} ({b.get('value')} {b.get('unit', '')})",
                    is_fallback=False,
                    urgent_warning=urgent_warning
                )
            )

    # 3. Always include General Physician as first-line holistic fallback
    if "general_physician" not in seen_ids:
        recs.append(
            SpecialtyRecommendation(
                specialty_id=GENERAL_PHYSICIAN_INFO["specialty_id"],
                specialty_name=GENERAL_PHYSICIAN_INFO["specialty_name"][lang],
                why_suggesting=GENERAL_PHYSICIAN_INFO["why"][lang],
                observed_finding=None,
                is_fallback=True,
                urgent_warning=urgent_warning
            )
        )

    return recs
