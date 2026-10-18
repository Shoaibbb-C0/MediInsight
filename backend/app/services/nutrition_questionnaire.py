"""
Nutrition Questionnaire Service for Simplifier 2.0.
Version: 2.0.0
Provides adaptive dietary questions tailored to findings and preferences,
supporting back, next, skip, don't know, and resume later in EN, HI, MR.
"""

from typing import List, Dict, Any, Optional

NUTRITION_QUESTIONS = [
    {
        "id": "nq_dietary_pref",
        "category": "dietary_pref",
        "text_en": "What describes your everyday dietary preference?",
        "text_hi": "आपकी सामान्य खानपान शैली कौन सी है?",
        "text_mr": "तुमची नेहमीची खाण्यापिण्याची पद्धत कोणती आहे?",
        "context_reason_en": "Ensures all suggested meals align with your personal lifestyle and eating habits.",
        "context_reason_hi": "यह सुनिश्चित करता है कि सभी भोजन विचार आपकी व्यक्तिगत जीवनशैली के अनुकूल हों।",
        "context_reason_mr": "हे सुनिश्चित करते की सर्व जेवणाचे पर्याय तुमच्या जीवनशैलीशी सुसंगत असतील.",
        "is_multi_select": False,
        "options": [
            {"id": "vegetarian", "text_en": "Vegetarian (Plant foods & Dairy)", "text_hi": "शाकाहारी (सब्जियां, अनाज एवं डेयरी)", "text_mr": "शाकाहारी (भाज्या, धान्य व दुग्धजन्य पदार्थ)"},
            {"id": "non_vegetarian", "text_en": "Non-Vegetarian (Includes Poultry, Fish, Meat)", "text_hi": "मांसाहारी (अंडा, चिकन, मछली आदि)", "text_mr": "मांसाहारी (अंडी, चिकन, मासे समाविष्ट)"},
            {"id": "eggetarian", "text_en": "Eggetarian (Vegetarian + Eggs)", "text_hi": "एगेटेरियन (शाकाहारी + अंडे)", "text_mr": "अंडी खाणारे शाकाहारी"},
            {"id": "vegan", "text_en": "Vegan (Strictly 100% Plant-Based)", "text_hi": "वीगन (पूर्णतः वनस्पति-आधारित, बिना डेयरी)", "text_mr": "व्हिगन (पूर्णतः वनस्पती आधारित)"}
        ]
    },
    {
        "id": "nq_allergies",
        "category": "allergies",
        "text_en": "Do you have any confirmed food allergies?",
        "text_hi": "क्या आपको किसी विशेष खाद्य पदार्थ से एलर्जी है?",
        "text_mr": "तुम्हाला कोणत्याही विशिष्ट अन्नपदार्थाची ऍलर्जी आहे का?",
        "context_reason_en": "Crucial for safety: these ingredients are strictly excluded from all recommendations and alternatives.",
        "context_reason_hi": "सुरक्षा के लिए अत्यंत महत्वपूर्ण: ये सामग्री सभी व्यंजनों और विकल्पों से पूरी तरह बाहर रखी जाएगी।",
        "context_reason_mr": "सुरक्षिततेसाठी अत्यंत महत्त्वाचे: हे पदार्थ सर्व शिफारसींमधून वगळले जातील.",
        "is_multi_select": True,
        "options": [
            {"id": "none", "text_en": "No known food allergies", "text_hi": "कोई ज्ञात खाद्य एलर्जी नहीं", "text_mr": "कोणतीही ऍलर्जी नाही"},
            {"id": "peanuts", "text_en": "Peanuts / Groundnuts", "text_hi": "मूंगफली (पीनट्स)", "text_mr": "शेंगदाणे"},
            {"id": "dairy", "text_en": "Dairy / Milk (Lactose)", "text_hi": "दूध एवं डेयरी उत्पाद", "text_mr": "दुग्धजन्य पदार्थ / दूध"},
            {"id": "gluten", "text_en": "Gluten / Wheat", "text_hi": "ग्लूटेन / गेहूं", "text_mr": "ग्लूटेन / गहू"},
            {"id": "eggs", "text_en": "Eggs", "text_hi": "अंडे", "text_mr": "अंडी"},
            {"id": "fish", "text_en": "Fish / Seafood", "text_hi": "मछली / सी-फूड", "text_mr": "मासे / सी-फूड"}
        ]
    },
    {
        "id": "nq_routine",
        "category": "routine",
        "text_en": "How many meals do you typically eat each day?",
        "text_hi": "आप सामान्यतः दिन में कितनी बार भोजन करते हैं?",
        "text_mr": "तुम्ही दिवसातून साधारणपणे किती वेळा जेवता?",
        "context_reason_en": "Helps structure your daily schedule to match your natural appetite without forced eating.",
        "context_reason_hi": "आपकी प्राकृतिक भूख और दिनचर्या के अनुसार भोजन का समय तय करने में मदद करता है।",
        "context_reason_mr": "तुमच्या भुकेनुसार आणि दिनक्रमानुसार योग्य वेळापत्रक आखण्यास मदत करते.",
        "is_multi_select": False,
        "options": [
            {"id": "3_meals", "text_en": "3 traditional meals (Breakfast, Lunch, Dinner)", "text_hi": "३ पारंपरिक भोजन (नाश्ता, दोपहर व रात का खाना)", "text_mr": "३ मुख्य जेवणे (नाश्ता, दुपारचे व रात्रीचे जेवण)"},
            {"id": "3_meals_snacks", "text_en": "3 meals plus light healthy snacks", "text_hi": "३ मुख्य भोजन एवं हल्का शाम का नाश्ता", "text_mr": "३ मुख्य जेवणे आणि हलका स्नॅक"},
            {"id": "2_meals", "text_en": "2 larger meals (Intermittent pattern)", "text_hi": "२ बड़े भोजन (इंटरमिटेंट उपवास शैली)", "text_mr": "२ मुख्य जेवणे"}
        ]
    },
    {
        "id": "nq_cooking",
        "category": "budget",
        "text_en": "What is your typical cooking and preparation routine?",
        "text_hi": "आपकी भोजन पकाने की सामान्य व्यवस्था क्या है?",
        "text_mr": "तुमची जेवण बनवण्याची साधारण सोय कशी आहे?",
        "context_reason_en": "Focuses on realistic recipes that fit your everyday kitchen reality.",
        "context_reason_hi": "यह सुनिश्चित करता है कि सुझाव आपकी रसोई की वास्तविक स्थिति के अनुकूल और आसान हों।",
        "context_reason_mr": "पाककृती सोप्या आणि तुमच्या रोजच्या स्वयंपाकाशी जुळणाऱ्या असाव्यात.",
        "is_multi_select": False,
        "options": [
            {"id": "home_cooked", "text_en": "Fresh everyday home cooking (Standard family kitchen)", "text_hi": "ताजा घर का बना खाना (सामान्य घरेलू रसोई)", "text_mr": "ताज्या घरगुती जेवणाची सोय आहे"},
            {"id": "quick_prep", "text_en": "Quick 15–20 minute prep (Busy work schedule)", "text_hi": "त्वरित १५-२० मिनट में बनने वाला खाना (व्यस्त दिनचर्या)", "text_mr": "१५-२० मिनिटांत तयार होणारे झटपट जेवण"},
            {"id": "eating_out_often", "text_en": "Often eat tiffin, mess, or outside food", "text_hi": "टिफिन, मेस या बाहर का खाना अधिक होता है", "text_mr": "टिफीन, मेस किंवा बाहेरचे जेवण जास्त असते"}
        ]
    },
    {
        "id": "nq_primary_goal",
        "category": "goals",
        "text_en": "What is your primary educational wellness goal?",
        "text_hi": "इस आहार योजना से आपका मुख्य उद्देश्य क्या है?",
        "text_mr": "या आहार मार्गदर्शकाकडून तुमची मुख्य अपेक्षा काय आहे?",
        "context_reason_en": "Frames the educational rationale to match what matters most to you.",
        "context_reason_hi": "आपके लिए सबसे महत्वपूर्ण विषय पर पोषण संबंधी व्याख्या को केंद्रित करता है।",
        "context_reason_mr": "तुमच्या गरजेनुसार पोषणविषयक माहिती केंद्रित करण्यास मदत करते.",
        "is_multi_select": False,
        "options": [
            {"id": "understand_lab_choices", "text_en": "Understand everyday food choices relevant to my lab results", "text_hi": "लैब रिपोर्ट के अनुसार संतुलित भोजन के विकल्प समझना", "text_mr": "लॅब निकालांनुसार योग्य अन्नपदार्थ समजून घेणे"},
            {"id": "balanced_wellness", "text_en": "Build a sustainable, balanced family meal routine", "text_hi": "दीर्घकालिक स्वस्थ एवं संतुलित पारिवारिक दिनचर्या बनाना", "text_mr": "दीर्घकालीन संतुलित व निरोगी कौटुंबिक आहार दिनचर्या"},
            {"id": "support_energy", "text_en": "Support daytime stamina and natural energy", "text_hi": "दिन भर ऊर्जा और ताजगी बनाए रखना", "text_mr": "दिवसभरातील उत्साह आणि ऊर्जा टिकवून ठेवणे"}
        ]
    },
    {
        "id": "nq_cuisine_pref",
        "category": "dietary_pref",
        "text_en": "What regional or culinary style do you most enjoy at home?",
        "text_hi": "घर पर आप किस प्रकार के क्षेत्रीय खानपान को सबसे अधिक पसंद करते हैं?",
        "text_mr": "घरी तुम्ही कोणत्या प्रादेशिक किंवा जेवणाच्या पद्धतीला प्राधान्य देता?",
        "context_reason_en": "Keeps meal ideas familiar, culturally grounded, and enjoyable to eat.",
        "context_reason_hi": "यह सुनिश्चित करता है कि भोजन आपके जाने-पहचाने पारंपरिक स्वाद और संस्कृति के अनुकूल हो।",
        "context_reason_mr": "अन्नपदार्थ तुमच्या नेहमीच्या आवडीचे आणि पारंपरिक पद्धतीचे राहतील.",
        "is_multi_select": False,
        "options": [
            {"id": "indian_regional", "text_en": "Everyday Indian Regional (Mix of Roti, Sabzi, Dal, Rice)", "text_hi": "दैनिक भारतीय घरेलू (रोटी, सब्जी, दाल, चावल)", "text_mr": "नेहमीचे भारतीय घरगुती (पोळी, भाजी, डाळ, भात)"},
            {"id": "north_indian", "text_en": "North Indian (Rotis, Paneer, Dals, Seasonal Sabzi)", "text_hi": "उत्तर भारतीय (रोटी, पनीर, दालें, ताजी सब्जियां)", "text_mr": "उत्तर भारतीय (चपाती, पनीर, डाळी, भाज्या)"},
            {"id": "south_indian", "text_en": "South Indian (Idli, Dosa, Sambar, Rasam, Rice)", "text_hi": "दक्षिण भारतीय (इडली, डोसा, सांभर, रसम, चावल)", "text_mr": "दक्षिण भारतीय (इडली, डोसा, सांबार, रसम, भात)"},
            {"id": "global_balanced", "text_en": "Balanced Global / Contemporary (Salads, Soups, Bowls)", "text_hi": "संतुलित वैश्विक / आधुनिक (सलाद, सूप, कटोरे)", "text_mr": "संतुलित आधुनिक (सॅलड, सूप, बाऊल्स)"}
        ]
    },
    {
        "id": "nq_special_restrictions",
        "category": "restrictions",
        "text_en": "Do you observe any specific food restrictions or preferences?",
        "text_hi": "क्या आप किसी विशेष खाद्य प्रतिबंध का पालन करते हैं?",
        "text_mr": "तुम्ही काही विशिष्ट अन्न निर्बंध पाळता का?",
        "context_reason_en": "Respects personal dietary ethics and digestive comfort.",
        "context_reason_hi": "आपकी व्यक्तिगत आहार परंपरा और पाचन प्राथमिकताओं का पूरा सम्मान करता है।",
        "context_reason_mr": "तुमच्या वैयक्तिक आहार परंपरांचा आणि पचन सवयींचा आदर करतो.",
        "is_multi_select": True,
        "options": [
            {"id": "none", "text_en": "None (No special restrictions)", "text_hi": "कोई विशेष प्रतिबंध नहीं", "text_mr": "कोणतेही विशेष निर्बंध नाहीत"},
            {"id": "no_onion_garlic", "text_en": "No Onion / Garlic (Sattvic style)", "text_hi": "बिना प्याज व लहसुन (सात्विक शैली)", "text_mr": "कांदा-लसूण विरहित (सात्विक पद्धत)"},
            {"id": "low_spice", "text_en": "Mild / Low Spice (Gentle digestion)", "text_hi": "हल्का / कम मसालेदार (सुपाच्य)", "text_mr": "कमी तिखट / सौम्य मसालेदार"},
            {"id": "no_beef_pork", "text_en": "No Beef / Pork", "text_hi": "बीफ / पोर्क मुक्त", "text_mr": "बीफ / पोर्क मुक्त"}
        ]
    },
    {
        "id": "nq_health_conditions",
        "category": "restrictions",
        "text_en": "Do any of the following apply to your current health context?",
        "text_hi": "क्या आपकी वर्तमान स्थिति में इनमें से कुछ लागू होता है?",
        "text_mr": "तुमच्या सध्याच्या आरोग्याशी संबंधित खालीलपैकी काही लागू आहे का?",
        "context_reason_en": "Medical safety check: high-risk clinical conditions require specialized dietitian assessment rather than automated meal algorithms.",
        "context_reason_hi": "सुरक्षा जाँच: उच्च जोखिम वाली स्वास्थ्य स्थितियों में स्वचालित सुझावों के बजाय पेशेवर डायटीशियन की सलाह आवश्यक होती है।",
        "context_reason_mr": "सुरक्षा तपासणी: गंभीर किंवा जोखमीच्या वैद्यकीय स्थितींमध्ये तज्ज्ञ डायटीशियनचा सल्ला घेणे आवश्यक असते.",
        "is_multi_select": True,
        "options": [
            {"id": "none", "text_en": "None of these apply", "text_hi": "इनमें से कोई नहीं", "text_mr": "यापैकी काहीही नाही"},
            {"id": "ckd_renal", "text_en": "Kidney condition or elevated creatinine", "text_hi": "गुर्दे (किडनी) की बीमारी या उच्च क्रिएटिनिन", "text_mr": "मूत्रपिंड (किडनी) विकार किंवा वाढलेले क्रिएटीनिन"},
            {"id": "pregnancy", "text_en": "Pregnancy or breastfeeding", "text_hi": "गर्भावस्था अथवा स्तनपान", "text_mr": "गरोदरपण किंवा स्तनपान"},
            {"id": "type2_diabetes", "text_en": "Diagnosed Type 1 or Type 2 Diabetes on medication", "text_hi": "दवा पर निर्भर मधुमेह (डायबिटीज)", "text_mr": "औषधोपचारावर सुरू असलेला मधुमेह"}
        ]
    }
]

NUTRITION_QUESTIONS.insert(0, {
    "id":"nq_age_group", "category":"safety", "is_multi_select":False,
    "text_en":"Which age group is this plan for?", "text_hi":"यह योजना किस आयु वर्ग के लिए है?", "text_mr":"ही योजना कोणत्या वयोगटासाठी आहे?",
    "context_reason_en":"Children need age-specific clinician guidance.", "context_reason_hi":"बच्चों के लिए आयु के अनुसार डॉक्टर का मार्गदर्शन चाहिए।", "context_reason_mr":"मुलांसाठी वयानुसार डॉक्टरांचे मार्गदर्शन आवश्यक आहे.",
    "options":[{"id":"child","text_en":"Under 18","text_hi":"18 से कम","text_mr":"18 पेक्षा कमी"},{"id":"adult","text_en":"18–64","text_hi":"18–64","text_mr":"18–64"},{"id":"older_adult","text_en":"65 or older","text_hi":"65 या अधिक","text_mr":"65 किंवा अधिक"}]
})
NUTRITION_QUESTIONS.append({
    "id":"nq_budget", "category":"budget", "is_multi_select":False,
    "text_en":"Which food budget is practical for you?", "text_hi":"भोजन के लिए कौन सा बजट सुविधाजनक है?", "text_mr":"जेवणासाठी कोणते बजेट सोयीचे आहे?",
    "context_reason_en":"Uses relative staple-food affordability, not invented prices.", "context_reason_hi":"स्थानीय कीमतों का दावा किए बिना परिचित सस्ते विकल्प चुनता है।", "context_reason_mr":"स्थानिक किमतींचा दावा न करता परिचित किफायतशीर पर्याय निवडतो.",
    "options":[{"id":"modest","text_en":"Prefer low-cost staples","text_hi":"कम खर्च वाले परिचित पदार्थ","text_mr":"कमी खर्चाचे परिचित पदार्थ"},{"id":"moderate","text_en":"Moderate","text_hi":"मध्यम","text_mr":"मध्यम"},{"id":"flexible","text_en":"Flexible","text_hi":"लचीला","text_mr":"लवचिक"}]
})

def get_localized_nutrition_questions(lang: str = "en") -> List[Dict[str, Any]]:
    """Returns localized questions for the Smart Nutrition Questionnaire."""
    localized_list = []
    text_key = f"text_{lang}" if lang in ["hi", "mr"] else "text_en"
    context_key = f"context_reason_{lang}" if lang in ["hi", "mr"] else "context_reason_en"

    for q in NUTRITION_QUESTIONS:
        localized_options = []
        for opt in q["options"]:
            opt_text = opt.get(f"text_{lang}") or opt.get("text_en")
            localized_options.append({
                "id": opt["id"],
                "text": opt_text
            })
        localized_list.append({
            "id": q["id"],
            "category": q["category"],
            "text": q.get(text_key, q["text_en"]),
            "context_reason": q.get(context_key, q["context_reason_en"]),
            "is_multi_select": q["is_multi_select"],
            "options": localized_options
        })
    return localized_list
