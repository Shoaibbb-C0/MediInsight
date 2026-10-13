"""
Central Multilingual Localization Registry for Simplifier 2.0.
Languages: English (en), Hindi (hi), Marathi (mr).
Supports UI labels, medical knowledge, test descriptions, pattern explanations,
questionnaire questions/options, and PDF generation with clinical review gating.
"""

from typing import Dict, Any, Optional

TRANSLATION_REVIEW_REGISTRY = {
    "version": "2.2.0",
    "languages": {
        "en": {"name": "English", "review_status": "CLINICALLY_REVIEWED", "reviewer": "Simplifier Medical Advisory Board"},
        "hi": {"name": "हिंदी (Hindi)", "review_status": "PROFESSIONAL_TRANSLATION_REVIEW_PENDING", "reviewer": "Native Medical Linguist"},
        "mr": {"name": "मराठी (Marathi)", "review_status": "PROFESSIONAL_TRANSLATION_REVIEW_PENDING", "reviewer": "Native Medical Linguist"}
    }
}

UI_STRINGS = {
    "en": {
        "home": "Home",
        "reports": "My Reports",
        "profile": "Profile",
        "tagline": "Warm Health Clarity",
        "privateBadge": "Private & confidential — Your medical files never leave your control",
        "heroTitle": "Understand your lab reports without the confusion.",
        "heroSubtitle": "Turn complex blood tests and clinical values into clear, calm health insights you can actually discuss with your family and doctor.",
        "uploadButton": "Upload a report",
        "cameraButton": "Take a photo",
        "trySample": "Try an example health report →",
        "readingReport": "Reading your report carefully...",
        "readingSubtitle": "Extracting laboratory lines and checking measurement confidence.",
        "stepQuestionnaire": "Step 1 of 2: A few questions about you",
        "stepReport": "Step 2 of 2: Simplified Summary",
        "heresWhatWeFound": "Here's what we found",
        "overallSummary": "Overall Summary",
        "whatNeedsAttention": "What needs attention",
        "healthyResults": "Healthy / Within-Range Results",
        "unreliableFlagged": "Excluded / Low-Confidence Results",
        "unreliableNotice": "These values had low optical recognition confidence or ambiguous formatting. To safeguard medical accuracy, they are excluded from definitive analysis until reviewed on your printed report.",
        "whatChanged": "What has changed since your last report",
        "whatTestsCheck": "What these tests commonly check",
        "clinicalPatterns": "Observed health patterns",
        "whatAnswersTell": "What your answers tell us",
        "suggestedDoctorQuestions": "Helpful questions to ask your physician",
        "safeNextSteps": "Safe next steps",
        "seeAllResults": "See all results",
        "hideResults": "Hide",
        "nutritionPrompt": "Would you like food guidance relevant to your results?",
        "showNutrition": "Show my guidance",
        "doctorPrompt": "Would you like help finding the right doctor?",
        "findDoctor": "Find a doctor",
        "notNow": "Not now",
        "downloadPdf": "Download Summary PDF",
        "keepCopy": "Keep a copy for your consultation",
        "keepCopySub": "Formatted with your exact measurements, ranges, and doctor discussion points.",
        "disclaimerTitle": "Important Medical Notice",
        "disclaimer": "Simplifier is an educational tool designed to help you prepare for discussions with your physician. It does not provide medical diagnosis or replace personalized medical counsel.",
        "translationReviewNotice": "Clinical translation note: English terms and values are preserved alongside reviewed translations for clinical accuracy.",
        "understandAnother": "Understand another report",
        "allNormal": "Great news — none of your reported laboratory lines fall outside standard reference boundaries.",
        "nextQuestion": "Next question",
        "finishQuestions": "See my report",
        "skipAllQuestions": "Skip all questions",
        "skipThisQuestion": "Skip this question",
        "preferredLanguage": "Preferred Language",
        "savePreferences": "Save Preferences",
        "verifiedMatch": "Laboratory extract",
        "needsReview": "Needs Review",
        "high": "Slightly High",
        "low": "Slightly Low",
        "normal": "Healthy Range",
        "urgentAlertTitle": "Important Safety Reminder: Noticeable Bleeding Reported",
        "urgentAlertGuidance": "Because you reported visible bleeding or dark black stools alongside low blood counts, please contact a healthcare provider promptly today or seek urgent medical evaluation rather than waiting for routine follow-up.",
        "reportAtAGlance": "Report at a Glance",
        "whatWasChecked": "What Was This Report Checking?",
        "resultsNeedingAttention": "Results That Need Attention",
        "whatHistoryAdds": "What Your History Adds",
        "personalBaselineLabel": "Your usual readings across previous reports",
        "shortNextSteps": "Short Next Steps",
        "takeActionTitle": "Next Steps for Your Health",
        "buildNutritionAction": "Build My Weekly Nutrition Plan",
        "buildNutritionDesc": "Get a grounded 7-day meal schedule tailored to your results.",
        "findDoctorAction": "Find a Doctor Near Me",
        "findDoctorDesc": "Discover clinics and specialists relevant to your findings.",
        "fullResultsTitle": "Full Test Results & Export",
        "exportPdfBtn": "Download Matching PDF"
    },
    "hi": {
        "home": "होम",
        "reports": "मेरी रिपोर्ट्स",
        "profile": "प्रोफ़ाइल",
        "tagline": "सहज स्वास्थ्य स्पष्टता",
        "privateBadge": "निजी एवं गोपनीय — आपकी मेडिकल फ़ाइलें आपके नियंत्रण में हैं",
        "heroTitle": "बिना किसी उलझन के अपनी लैब रिपोर्ट को समझें।",
        "heroSubtitle": "जटिल रक्त परीक्षणों और प्रयोगशाला संख्याओं को शांत, स्पष्ट स्वास्थ्य जानकारियों में बदलें ताकि आप अपने डॉक्टर से खुलकर चर्चा कर सकें।",
        "uploadButton": "रिपोर्ट अपलोड करें",
        "cameraButton": "फ़ोटो लें",
        "trySample": "नमूना रिपोर्ट देखें →",
        "readingReport": "आपकी रिपोर्ट को ध्यानपूर्वक पढ़ा जा रहा है...",
        "readingSubtitle": "परीक्षणों के नाम, मान और संदर्भ सीमाओं की जाँच की जा रही है।",
        "stepQuestionnaire": "चरण 1 का 2: आपके स्वास्थ्य संदर्भ से जुड़े प्रश्न",
        "stepReport": "चरण 2 का 2: सरल स्वास्थ्य सारांश",
        "heresWhatWeFound": "जाँच में क्या सामने आया",
        "overallSummary": "समग्र सारांश",
        "whatNeedsAttention": "किन बातों पर ध्यान देने की आवश्यकता है",
        "healthyResults": "सामान्य / संतुलित परिणाम",
        "unreliableFlagged": "अस्पष्ट / अनिश्चित मान (समीक्षा आवश्यक)",
        "unreliableNotice": "इन परिणामों की पहचान में स्पष्टता कम थी। चिकित्सीय सटीकता के लिए, इन्हें मुख्य विश्लेषण से अलग रखा गया है ताकि आप अपनी मूल रिपोर्ट में देखकर डॉक्टर से पूछ सकें।",
        "whatChanged": "पिछली रिपोर्ट से क्या बदलाव आया",
        "whatTestsCheck": "ये परीक्षण आमतौर पर क्या जाँचते हैं",
        "clinicalPatterns": "देखे गए स्वास्थ्य रुझान",
        "whatAnswersTell": "आपके उत्तरों से क्या स्पष्ट होता है",
        "suggestedDoctorQuestions": "डॉक्टर से पूछने हेतु उपयोगी प्रश्न",
        "safeNextSteps": "सुरक्षित अगले कदम",
        "seeAllResults": "सभी परिणाम देखें",
        "hideResults": "छुपाएं",
        "nutritionPrompt": "क्या आप अपने परिणामों से संबंधित आहार मार्गदर्शन देखना चाहते हैं?",
        "showNutrition": "मेरा आहार मार्गदर्शन दिखाएं",
        "doctorPrompt": "क्या आप सही डॉक्टर खोजने में मदद चाहते हैं?",
        "findDoctor": "डॉक्टर खोजें",
        "notNow": "अभी नहीं",
        "downloadPdf": "सारांश PDF डाउनलोड करें",
        "keepCopy": "परामर्श के लिए रिपोर्ट की प्रति सुरक्षित रखें",
        "keepCopySub": "मूल मानों, संदर्भ सीमाओं और डॉक्टर चर्चा बिंदुओं के साथ मुद्रित।",
        "disclaimerTitle": "महत्वपूर्ण चिकित्सीय सूचना",
        "disclaimer": "सिम्प्लीफायर एक शैक्षिक उपकरण है जो आपके डॉक्टर से परामर्श की तैयारी में मदद करता है। यह चिकित्सीय निदान या नुस्खे का स्थान नहीं लेता।",
        "translationReviewNotice": "अनुवाद समीक्षा सूचना: मूल परीक्षण मान एवं इकाइयाँ चिकित्सीय शुद्धता हेतु अंग्रेजी में भी सुरक्षित रखी गई हैं।",
        "understandAnother": "अन्य रिपोर्ट समझें",
        "allNormal": "शुभ समाचार — आपके सभी परीक्षण परिणाम सामान्य प्रयोगशाला सीमा के भीतर हैं।",
        "nextQuestion": "अगला प्रश्न",
        "finishQuestions": "मेरी रिपोर्ट देखें",
        "skipAllQuestions": "सभी प्रश्न छोड़ें",
        "skipThisQuestion": "यह प्रश्न छोड़ें",
        "preferredLanguage": "पसंदीदा भाषा",
        "savePreferences": "प्राथमिकताएं सहेजें",
        "verifiedMatch": "प्रयोगशाला अर्क",
        "needsReview": "जाँच आवश्यक",
        "high": "सामान्य से अधिक",
        "low": "सामान्य से कम",
        "normal": "संतुलित स्तर",
        "urgentAlertTitle": "महत्वपूर्ण सुरक्षा चेतावनी: रक्तस्राव की सूचना",
        "urgentAlertGuidance": "क्योंकि आपने रक्तस्राव या काले मल की सूचना दी है, कृपया आज ही तुरंत किसी चिकित्सक से संपर्क करें और नियमित परामर्श की प्रतीक्षा न करें।",
        "reportAtAGlance": "एक नज़र में रिपोर्ट",
        "whatWasChecked": "यह रिपोर्ट क्या जाँच रही थी?",
        "resultsNeedingAttention": "परिणाम जिन पर ध्यान देने की आवश्यकता है",
        "whatHistoryAdds": "आपका पिछला इतिहास क्या बताता है",
        "personalBaselineLabel": "पिछली रिपोर्टों में आपका सामान्य रुझान",
        "shortNextSteps": "संक्षिप्त अगले कदम",
        "takeActionTitle": "आपके स्वास्थ्य हेतु व्यावहारिक कदम",
        "buildNutritionAction": "मेरी साप्ताहिक आहार योजना तैयार करें",
        "buildNutritionDesc": "अपने परिणामों के आधार पर ७ दिनों का व्यावहारिक आहार कार्यक्रम पाएं।",
        "findDoctorAction": "नज़दीकी डॉक्टर खोजें",
        "findDoctorDesc": "अपनी रिपोर्ट के अनुसार उपयुक्त विशेषज्ञ और क्लीनिक खोजें।",
        "fullResultsTitle": "पूर्ण परीक्षण परिणाम एवं निर्यात",
        "exportPdfBtn": "सारांश PDF डाउनलोड करें"
    },
    "mr": {
        "home": "मुख्य पृष्ठ",
        "reports": "माझे अहवाल",
        "profile": "माझी माहिती",
        "tagline": "सहज आरोग्य स्पष्टता",
        "privateBadge": "खाजगी आणि सुरक्षित — तुमचे वैद्यकीय दस्तऐवज सुरक्षित आहेत",
        "heroTitle": "कोणत्याही गोंधळाशिवाय तुमचे लॅब रिपोर्ट समजून घ्या.",
        "heroSubtitle": "रक्त तपासणी आणि वैद्यकीय आकडेवारी सोप्या भाषेत समजून घ्या, जेणेकरून तुम्ही डॉक्टरांशी सहज चर्चा करू शकाल.",
        "uploadButton": "अहवाल अपलोड करा",
        "cameraButton": "फोटो काढा",
        "trySample": "नमुना अहवाल पहा →",
        "readingReport": "तुमचा अहवाल काळजीपूर्वक वाचत आहोत...",
        "readingSubtitle": "चाचण्यांचे निकाल आणि संदर्भ मूल्यांची तपासणी सुरू आहे.",
        "stepQuestionnaire": "टप्पा १/२: तुमच्या आरोग्याशी संबंधित काही प्रश्न",
        "stepReport": "टप्पा २/२: सोपा आरोग्य अहवाल",
        "heresWhatWeFound": "तपासणीत काय आढळले",
        "overallSummary": "एकूण सारांश",
        "whatNeedsAttention": "कशावर लक्ष देणे आवश्यक आहे",
        "healthyResults": "संतुलित / सामान्य निकाल",
        "unreliableFlagged": "अस्पष्ट / संशयित निकाल (पुनरावलोकन आवश्यक)",
        "unreliableNotice": "हे निकाल ओळखताना स्पष्टता कमी होती. वैद्यकीय सुरक्षिततेसाठी, मूळ रिपोर्ट तपासून डॉक्टरांशी बोलण्याकरिता हे वेगळे ठेवले आहेत.",
        "whatChanged": "मागील अहवालापेक्षा काय बदलले आहे",
        "whatTestsCheck": "या चाचण्या सामान्यतः काय तपासतात",
        "clinicalPatterns": "दिसून आलेले आरोग्य कल",
        "whatAnswersTell": "तुमच्या उत्तरांवरून काय समजते",
        "suggestedDoctorQuestions": "डॉक्टरांना विचारण्यासाठी महत्त्वाचे प्रश्न",
        "safeNextSteps": "सुरक्षित पुढची पावले",
        "seeAllResults": "सर्व निकाल पहा",
        "hideResults": "लपवा",
        "nutritionPrompt": "तुम्हाला तुमच्या निकालांनुसार आहारविषयक मार्गदर्शन हवे आहे का?",
        "showNutrition": "माझे आहार मार्गदर्शन दाखवा",
        "doctorPrompt": "योग्य डॉक्टर शोधण्यात मदत हवी आहे का?",
        "findDoctor": "डॉक्टर शोधा",
        "notNow": "आत्ता नको",
        "downloadPdf": "अहवाल PDF डाउनलोड करा",
        "keepCopy": "डॉक्टरांच्या सल्ल्यासाठी प्रत जतन करा",
        "keepCopySub": "तुमची अचूक मोजमापे, प्रमाण आणि डॉक्टरांशी चर्चेच्या मुद्द्यांसह तयार.",
        "disclaimerTitle": "महत्त्वाची वैद्यकीय सूचना",
        "disclaimer": "सिम्प्लीफायर हे डॉक्टरांशी चर्चा करण्यासाठी तयार केलेले शैक्षणिक साधन आहे. हे वैद्यकीय निदान किंवा उपचारांचा पर्याय नाही.",
        "translationReviewNotice": "वैद्यकीय भाषांतर नोंद: वैद्यकीय अचूकतेसाठी मूळ चाचण्यांची नावे व मूल्ये इंग्रजीमध्येही जतन केली आहेत.",
        "understandAnother": "दुसरा अहवाल समजून घ्या",
        "allNormal": "आनंदाची बातमी — तुमचे सर्व तपासणी निकाल सामान्य संदर्भ मर्यादेत आहेत.",
        "nextQuestion": "पुढील प्रश्न",
        "finishQuestions": "माझा अहवाल पहा",
        "skipAllQuestions": "सर्व प्रश्न वगळा",
        "skipThisQuestion": "हा प्रश्न वगळा",
        "preferredLanguage": "निवडलेली भाषा",
        "savePreferences": "पसंती जतन करा",
        "verifiedMatch": "प्रयोगशाळा नोंदी",
        "needsReview": "पुनरावलोकन आवश्यक",
        "high": "नेहमीपेक्षा जास्त",
        "low": "नेहमीपेक्षा कमी",
        "normal": "संतुलित प्रमाण",
        "urgentAlertTitle": "महत्त्वाची सुरक्षा सूचना: रक्तस्त्रावाची नोंद",
        "urgentAlertGuidance": "तुम्ही रक्तस्त्रावाची नोंद केली असल्याने, कृपया तातडीने डॉक्टरांशी संपर्क साधा.",
        "reportAtAGlance": "एका दृष्टिक्षेपात अहवाल",
        "whatWasChecked": "हा अहवाल नेमके काय तपासत होता?",
        "resultsNeedingAttention": "लक्ष देण्यासारखे निकाल",
        "whatHistoryAdds": "तुमचा मागील इतिहास काय सांगतो",
        "personalBaselineLabel": "मागील अहवालांमधील तुमची नेहमीची पातळी",
        "shortNextSteps": "पुढील महत्त्वाची पावले",
        "takeActionTitle": "आरोग्यासाठी कृती योजना",
        "buildNutritionAction": "माझा ७-दिवसीय आहार प्लॅन तयार करा",
        "buildNutritionDesc": "तुमच्या चाचणी निकालानुसार संतुलित आहार योजना मिळवा.",
        "findDoctorAction": "माझ्या जवळील डॉक्टर शोधा",
        "findDoctorDesc": "योग्य तज्ज्ञ डॉक्टर आणि दवाखाने शोधा.",
        "fullResultsTitle": "संपूर्ण चाचणी निकाल आणि डाउनलोड",
        "exportPdfBtn": "अहवाल PDF डाउनलोड करा"
    }
}

BIOMARKER_LOCALIZATION = {
    "glucose_fasting": {
        "en": {
            "name": "Fasting Blood Glucose",
            "what_it_measures": "Measures sugar circulating in your blood after an overnight fast (8–12 hours without food).",
            "why_checked": "To assess body sugar balance, insulin regulation, or routine metabolic health.",
            "high_explanation": "Higher readings mean glucose takes longer to move into cells. May reflect early insulin resistance or recent food intake.",
            "low_explanation": "Lower readings can occur with prolonged fasting, strenuous exertion, or certain medicines."
        },
        "hi": {
            "name": "फास्टिंग ब्लड ग्लूकोज (खाली पेट रक्त शर्करा)",
            "what_it_measures": "रात भर भूखे रहने के बाद (८-१२ घंटे बिना भोजन) आपके रक्त में मौजूद शर्करा की मात्रा मापता है।",
            "why_checked": "शरीर में शुगर नियंत्रण, इंसुलिन संतुलन और मेटाबॉलिक स्वास्थ्य की जाँच हेतु।",
            "high_explanation": "अधिक मान का अर्थ है कि कोशिकाओं तक शुगर पहुँचने में सामान्य से अधिक समय लग रहा है।",
            "low_explanation": "कम मान लंबे उपवास, अत्यधिक श्रम या दवाओं के कारण हो सकता है।"
        },
        "mr": {
            "name": "फास्टिंग ब्लड ग्लुकोज (उपाशीपोटी रक्तातील साखर)",
            "what_it_measures": "रात्रभर उपाशी राहिल्यानंतर (८-१२ तास अन्न न घेता) रक्तातील साखरेचे प्रमाण मोजते.",
            "why_checked": "शरीरातील साखरेचे संतुलन आणि चयापचय (मेटाबॉलिक) आरोग्य तपासण्यासाठी.",
            "high_explanation": "जास्त प्रमाण दर्शवते की शरीरातील पेशींपर्यंत साखर शोषण्यास नेहमीपेक्षा जास्त वेळ लागत आहे.",
            "low_explanation": "कमी प्रमाण दीर्घकाळ उपाशी राहण्यामुळे किंवा अतिश्रमामुळे होऊ शकते."
        }
    },
    "hba1c": {
        "en": {
            "name": "HbA1c (Glycated Hemoglobin)",
            "what_it_measures": "Reflects your average blood sugar levels over the past 2 to 3 months.",
            "why_checked": "Provides a steady window into long-term blood sugar regulation without day-to-day fluctuation.",
            "high_explanation": "Between 5.7% and 6.4% suggests early watch zone (prediabetes); 6.5% or above indicates doctor evaluation is helpful.",
            "low_explanation": "Lower levels are uncommon and usually related to red blood cell turnover."
        },
        "hi": {
            "name": "एचबीए1सी (ग्लाइकेटेड हीमोग्लोबिन)",
            "what_it_measures": "पिछले २ से ३ महीनों के दौरान आपके रक्त में औसत शुगर स्तर को दर्शाता है।",
            "why_checked": "दैनिक उतार-चढ़ाव के बिना दीर्घकालिक शुगर नियंत्रण का सही अनुमान लगाने के लिए।",
            "high_explanation": "५.७% से ६.४% शुरुआती निगरानी क्षेत्र दर्शाता है; ६.५% या अधिक पर डॉक्टर से परामर्श आवश्यक है।",
            "low_explanation": "कम मान बहुत कम मामलों में देखा जाता है।"
        },
        "mr": {
            "name": "एचबीए१सी (ग्लायकेटेड हिमोग्लोबिन)",
            "what_it_measures": "मागील २ ते ३ महिन्यांतील रक्तातील साखरेची सरासरी पातळी दर्शवते.",
            "why_checked": "दररोजच्या आहारातील चढ-उतारांशिवाय दीर्घकालीन साखरेच्या नियंत्रणाचा अंदाज घेण्यासाठी.",
            "high_explanation": "५.७% ते ६.४% ही सुरुवातीची काळजी घेण्याची पातळी आहे; ६.५% पेक्षा जास्त असल्यास डॉक्टरांचा सल्ला आवश्यक.",
            "low_explanation": "कमी पातळी फार क्वचित आढळते."
        }
    },
    "creatinine_serum": {
        "en": {
            "name": "Serum Creatinine",
            "what_it_measures": "Natural muscle waste product filtered out of blood primarily by healthy kidneys.",
            "why_checked": "To assess how smoothly your kidneys are filtering waste from the bloodstream.",
            "high_explanation": "Kidneys may be filtering slightly slower, or could reflect temporary dehydration or high muscle mass.",
            "low_explanation": "Lower levels are generally harmless, often seen in smaller body mass or pregnancy."
        },
        "hi": {
            "name": "सीरम क्रिएटिनिन (गुर्दे की कार्यप्रणाली)",
            "what_it_measures": "मांसपेशियों की सामान्य गतिविधि से बनने वाला अपशिष्ट जिसे स्वस्थ गुर्दे छानकर बाहर निकालते हैं।",
            "why_checked": "यह देखने के लिए कि आपके गुर्दे रक्त से अपशिष्ट को कितनी सुचारू रूप से छान रहे हैं।",
            "high_explanation": "गुर्दे छानने में धीमे हो सकते हैं, या यह पानी की कमी (डिहाइड्रेशन) का संकेत हो सकता है।",
            "low_explanation": "कम स्तर आमतौर पर पूरी तरह सुरक्षित और सामान्य होता है।"
        },
        "mr": {
            "name": "सीरम क्रिएटिनिन (मूत्रपिंड कार्यक्षमता)",
            "what_it_measures": "स्नायूंच्या दैनंदिन कार्यातून निर्माण होणारे घटक जे निरोगी मूत्रपिंड रक्तामधून गाळून बाहेर टाकतात.",
            "why_checked": "तुमचे मूत्रपिंड रक्तातील कचरा किती कार्यक्षमतेने गाळत आहेत हे तपासण्यासाठी.",
            "high_explanation": "गाळण्याची गती मंदावली असू शकते किंवा शरीरात पाण्याचे प्रमाण कमी असू शकते.",
            "low_explanation": "कमी पातळी सामान्यतः पूर्णपणे सुरक्षित असते."
        }
    },
    "cholesterol_total": {
        "en": {
            "name": "Total Cholesterol",
            "what_it_measures": "The overall sum of circulating blood fats (lipids) in your bloodstream.",
            "why_checked": "To monitor heart wellness and guide positive daily dietary habits.",
            "high_explanation": "Elevated cholesterol can contribute to artery plaque over time if lifestyle balance is not maintained.",
            "low_explanation": "Very low levels are uncommon and usually evaluated in general wellness."
        },
        "hi": {
            "name": "कुल कोलेस्ट्रॉल (रक्त वसा)",
            "what_it_measures": "रक्तप्रवाह में मौजूद सभी प्रकार के लिपिड (वसा) का कुल योग।",
            "why_checked": "हृदय के स्वास्थ्य और संतुलित खानपान की निगरानी के लिए।",
            "high_explanation": "बढ़ा हुआ कोलेस्ट्रॉल धमनियों में जमाव बढ़ा सकता है, जिसे जीवनशैली सुधारकर नियंत्रित किया जा सकता है।",
            "low_explanation": "अत्यधिक कम स्तर बहुत दुर्लभ होता है।"
        },
        "mr": {
            "name": "एकूण कोलेस्टेरॉल (रक्तातील चरबी)",
            "what_it_measures": "रक्ताभिसरण संस्थेमधील चरबीच्या घटकांचे एकूण प्रमाण.",
            "why_checked": "हृदयाचे आरोग्य आणि संतुलित आहाराचे नियोजन तपासण्यासाठी.",
            "high_explanation": "जास्त कोलेस्टेरॉल रक्तवाहिन्यांवर ताण आणू शकते, जे योग्य दिनचर्येने संतुलित करता येते.",
            "low_explanation": "अतिशय कमी प्रमाण क्वचित आढळते."
        }
    },
    "vitamin_d": {
        "en": {
            "name": "Vitamin D (25-OH)",
            "what_it_measures": "Circulating sunshine vitamin that supports calcium absorption, bone strength, and immunity.",
            "why_checked": "Investigating fatigue, bone health, low sunlight exposure, or routine screening.",
            "high_explanation": "Elevated levels almost always occur from high-dose supplements.",
            "low_explanation": "Extremely common in individuals who spend most daylight hours indoors or use sunscreen."
        },
        "hi": {
            "name": "विटामिन डी (सनशाइन विटामिन)",
            "what_it_measures": "हड्डियों की मजबूती, कैल्शियम अवशोषण और रोग प्रतिरोधक क्षमता का मुख्य आधार।",
            "why_checked": "थकान, हड्डियों की मजबूती या धूप की कमी की स्थिति जाँचने हेतु।",
            "high_explanation": "अधिक स्तर लगभग हमेशा अधिक सप्लीमेंट लेने के कारण होता है।",
            "low_explanation": "घर या दफ्तर के अंदर रहने वाले लोगों में कम स्तर होना बेहद आम है।"
        },
        "mr": {
            "name": "व्हिटॅमिन डी (सूर्यप्रकाश जीवनसत्व)",
            "what_it_measures": "हाडांची बळकटी, कॅल्शियम शोषण आणि प्रतिकारशक्तीसाठी आवश्यक जीवनसत्व.",
            "why_checked": "थकवा, हाडांचे आरोग्य किंवा सूर्यप्रकाशाच्या अभावाची तपासणी करण्यासाठी.",
            "high_explanation": "जास्त प्रमाण प्रामुख्याने अधिक सप्लिमेंट्स घेतल्याने होते.",
            "low_explanation": "ऑफिसमध्ये किंवा घरात जास्त वेळ घालवणाऱ्या व्यक्तींमध्ये कमी प्रमाण असणे अत्यंत सामान्य आहे."
        }
    },
    "hemoglobin": {
        "en": {
            "name": "Hemoglobin",
            "what_it_measures": "Oxygen-carrying protein in red blood cells that delivers oxygen throughout your body.",
            "why_checked": "Screens for anemia, tiredness, blood loss, or vitality.",
            "high_explanation": "Can occur with dehydration, smoking, or living at higher altitudes.",
            "low_explanation": "Indicates anemia, which can cause tiredness and reduced physical stamina."
        },
        "hi": {
            "name": "हीमोग्लोबिन (रक्त ऑक्सीजन वाहक)",
            "what_it_measures": "लाल रक्त कोशिकाओं में ऑक्सीजन ले जाने वाला मुख्य प्रोटीन।",
            "why_checked": "एनीमिया (खून की कमी), कमजोरी या थकान के कारणों की जाँच के लिए।",
            "high_explanation": "पानी की कमी या अधिक ऊंचाई पर रहने के कारण बढ़ सकता है।",
            "low_explanation": "एनीमिया दर्शाता है, जिससे जल्दी थकान और कमजोरी महसूस हो सकती है।"
        },
        "mr": {
            "name": "हिमोग्लोबिन (ऑक्सिजन वाहक प्रथिन)",
            "what_it_measures": "तांबड्या पेशींमधील प्रथिन जे फुप्फुसातून संपूर्ण शरीराला प्राणवायू पुरवते.",
            "why_checked": "अशक्तपणा, थकवा किंवा ॲनिमियाची तपासणी करण्यासाठी.",
            "high_explanation": "शरीरात पाणी कमी असल्यामुळे किंवा डोंगराळ भागात राहिल्याने वाढू शकते.",
            "low_explanation": "ॲनिमिया (रक्तक्षय) दर्शवते, ज्यामुळे थकवा जाणवू शकतो."
        }
    }
}

QUESTION_LOCALIZATION = {
    "q_glucose_fasting": {
        "en": {
            "text": "Was your blood sample strictly collected before breakfast (fasting 8 to 12 hours, water only)?",
            "context_reason": "Eating or drinking anything with sugar or milk within a few hours before testing can naturally raise blood sugar readings.",
            "options": {
                "fasting_strictly": "Yes, strictly fasted (water only for 10+ hours)",
                "fasting_had_bite": "I had coffee, tea, or a light snack beforehand",
                "fasting_unsure": "I cannot remember the exact hours"
            }
        },
        "hi": {
            "text": "क्या आपका रक्त नमूना नाश्ते से पहले (८ से १२ घंटे केवल पानी पीकर उपवास) लिया गया था?",
            "context_reason": "जाँच से कुछ घंटे पहले चाय, दूध या हल्का नाश्ता लेने से भी ब्लड शुगर का स्तर अस्थायी रूप से बढ़ सकता है।",
            "options": {
                "fasting_strictly": "हाँ, पूरी तरह खाली पेट (१०+ घंटे केवल पानी)",
                "fasting_had_bite": "मैंने पहले चाय, कॉफ़ी या हल्का नाश्ता लिया था",
                "fasting_unsure": "मुझे ठीक से समय याद नहीं है"
            }
        },
        "mr": {
            "text": "तुमचा रक्ताचा नमुना सकाळच्या नाश्त्यापूर्वी (८ ते १२ तास फक्त पाणी पिऊन) घेतला होता का?",
            "context_reason": "तपासणीपूर्वी चहा, दूध किंवा हलका नाश्ता घेतल्यास रक्तातील साखरेचे प्रमाण नैसर्गिकरीत्या वाढू शकते.",
            "options": {
                "fasting_strictly": "होय, पूर्णपणे उपाशीपोटी (१०+ तास फक्त पाणी)",
                "fasting_had_bite": "मी आधी चहा, कॉफी किंवा हलका खाऊ घेतला होता",
                "fasting_unsure": "मला नेमके तास आठवत नाहीत"
            }
        }
    },
    "q_glucose_diabetes_history": {
        "en": {
            "text": "Have you previously been told you have prediabetes, diabetes, or insulin resistance?",
            "context_reason": "Helps distinguish an established management plan from an initial screening observation.",
            "options": {
                "diabetes_diag_yes": "Yes, I have an existing prediabetes or diabetes diagnosis",
                "diabetes_diag_no": "No, I've never been told this before",
                "diabetes_diag_unsure": "Unsure / testing for the first time"
            }
        },
        "hi": {
            "text": "क्या आपको पहले कभी प्रीडायबिटीज या डायबिटीज होने के बारे में बताया गया है?",
            "context_reason": "यह समझने में मदद करता है कि क्या यह कोई ज्ञात स्थिति है या पहली बार सामने आई जाँच है।",
            "options": {
                "diabetes_diag_yes": "हाँ, मुझे पहले से प्रीडायबिटीज या डायबिटीज की जानकारी है",
                "diabetes_diag_no": "नहीं, मुझे पहले कभी ऐसा नहीं बताया गया",
                "diabetes_diag_unsure": "निश्चित नहीं / पहली बार परीक्षण कराया"
            }
        },
        "mr": {
            "text": "तुम्हाला यापूर्वी कधी प्रीडायबेटीस किंवा मधुमेहाचे निदान झाले होते का?",
            "context_reason": "यावरून हे समजते की हा आधीपासून सुरू असलेला उपचार आहे की पहिली तपासणी.",
            "options": {
                "diabetes_diag_yes": "होय, मला आधीपासून प्रीडायबेटीस किंवा मधुमेह आहे",
                "diabetes_diag_no": "नाही, मला यापूर्वी कधीही असे सांगितले नव्हते",
                "diabetes_diag_unsure": "माहित नाही / पहिल्यांदाच तपासणी केली"
            }
        }
    },
    "q_glucose_symptoms": {
        "en": {
            "text": "Have you experienced unusual constant thirst, unexplained weight loss, or waking frequently at night to urinate?",
            "context_reason": "These classic indicators help your physician determine if elevated glucose is causing active symptoms.",
            "options": {
                "gluc_sym_none": "None of these symptoms",
                "gluc_sym_thirst": "Yes, noticeably more thirsty and frequent urination",
                "gluc_sym_weightloss": "Yes, unprompted weight changes or fatigue"
            }
        },
        "hi": {
            "text": "क्या आपको अत्यधिक प्यास लगना, बिना कारण वजन घटना या रात में बार-बार पेशाब आने का अनुभव हुआ है?",
            "context_reason": "ये सामान्य संकेत डॉक्टर को यह समझने में मदद करते हैं कि क्या बढ़े हुए शुगर स्तर से कोई लक्षण हो रहे हैं।",
            "options": {
                "gluc_sym_none": "इनमें से कोई लक्षण नहीं",
                "gluc_sym_thirst": "हाँ, अधिक प्यास और बार-बार पेशाब आना",
                "gluc_sym_weightloss": "हाँ, वजन में बदलाव या कमजोरी"
            }
        },
        "mr": {
            "text": "तुम्हाला सतत जास्त तहान लागणे, विनाकारण वजन कमी होणे किंवा रात्री वारंवार लघवीला जावे लागणे असा त्रास होतो का?",
            "context_reason": "ही सामान्य लक्षणे डॉक्टरांना वाढलेल्या साखरेचा दैनंदिन प्रभाव समजून घेण्यास मदत करतात.",
            "options": {
                "gluc_sym_none": "यापैकी कोणतीही लक्षणे नाहीत",
                "gluc_sym_thirst": "होय, जास्त तहान आणि वारंवार लघवी होणे",
                "gluc_sym_weightloss": "होय, वजनात बदल किंवा थकवा"
            }
        }
    },
    "q_vitd_sun_habits": {
        "en": {
            "text": "How often do you spend 15 to 20 minutes outdoors in direct sunlight each week without sunscreen?",
            "context_reason": "Sunlight is the body's primary natural source of Vitamin D. Low levels are very common with indoor work.",
            "options": {
                "sun_rarely": "Rarely (mostly indoors or covered)",
                "sun_moderate": "2 to 3 days a week",
                "sun_daily": "Almost every day"
            }
        },
        "hi": {
            "text": "आप सप्ताह में कितनी बार बिना सनस्क्रीन के १५ से २० मिनट सीधी धूप में बिताते हैं?",
            "context_reason": "धूप शरीर में विटामिन डी का मुख्य प्राकृतिक स्रोत है। दफ्तर में काम करने वालों में इसका स्तर कम होना आम है।",
            "options": {
                "sun_rarely": "बहुत कम (ज्यादातर घर या ऑफिस के अंदर)",
                "sun_moderate": "सप्ताह में २ से ३ दिन",
                "sun_daily": "लगभग हर दिन"
            }
        },
        "mr": {
            "text": "तुम्ही आठवड्यातून किती वेळा थेट सकाळच्या कोवळ्या उन्हात १५ ते २० मिनिटे वेळ घालवता?",
            "context_reason": "सूर्यप्रकाश हे शरीरासाठी व्हिटॅमिन डीचे मुख्य नैसर्गिक साधन आहे.",
            "options": {
                "sun_rarely": "फार क्वचित (मुख्यतः घरात किंवा सावलीत)",
                "sun_moderate": "आठवड्यातून २ ते ३ दिवस",
                "sun_daily": "जवळजवळ दररोज"
            }
        }
    },
    "q_hemo_fatigue": {
        "en": {
            "text": "Have you noticed feeling unusually tired, dizzy, or short of breath during routine daily activities?",
            "context_reason": "Low hemoglobin means fewer red blood cells carry oxygen. Knowing your daily energy level helps tailor physician talking points.",
            "options": {
                "fatigue_yes": "Yes, I've had noticeable tiredness or mild lightheadedness",
                "fatigue_no": "No, I'm feeling quite normal and energetic",
                "fatigue_unsure": "A little tired, but not sure if it's unusual"
            }
        },
        "hi": {
            "text": "क्या आपको सामान्य कार्यों के दौरान असामान्य थकान, चक्कर आना या सांस फूलने का अनुभव हुआ है?",
            "context_reason": "कम हीमोग्लोबिन से शरीर में ऑक्सीजन का प्रवाह धीमा हो सकता है। ऊर्जा का स्तर जानने से डॉक्टर चर्चा में मदद मिलती है।",
            "options": {
                "fatigue_yes": "हाँ, मुझे ध्यान देने योग्य थकान या चक्कर महसूस हुए हैं",
                "fatigue_no": "नहीं, मैं पूरी तरह ऊर्जावान महसूस कर रहा हूँ",
                "fatigue_unsure": "हल्की थकान, लेकिन निश्चित नहीं"
            }
        },
        "mr": {
            "text": "दैनंदिन कामे करताना तुम्हाला नेहमीपेक्षा जास्त थकवा, चक्कर येणे किंवा धाप लागणे असा त्रास होतो का?",
            "context_reason": "हिमोग्लोबिन कमी असल्यास पेशींना ऑक्सिजन कमी मिळतो. तुमच्या ऊर्जेची माहिती डॉक्टरांच्या सल्ल्यासाठी उपयोगी ठरते.",
            "options": {
                "fatigue_yes": "होय, मला थकवा किंवा किंचित चक्कर जाणवते",
                "fatigue_no": "नाही, मला नेहमीसारखे उत्साही वाटते",
                "fatigue_unsure": "थोडा थकवा आहे, पण निश्चित सांगता येत नाही"
            }
        }
    },
    "q_hemo_bleeding_signs": {
        "en": {
            "text": "Have you noticed any recent unusual bleeding, heavy menstrual cycles, or dark black stools?",
            "context_reason": "Physical bleeding is a common direct cause of dropped hemoglobin.",
            "options": {
                "bleed_none": "No unusual bleeding or dark stools",
                "bleed_heavy_periods": "Yes, heavier than usual menstrual cycles",
                "bleed_concerning": "Yes, visible bleeding or dark black stools"
            }
        },
        "hi": {
            "text": "क्या आपने हाल ही में कोई असामान्य रक्तस्राव, भारी मासिक धर्म या काला मल देखा है?",
            "context_reason": "रक्त की कमी होना हीमोग्लोबिन घटने का एक प्रत्यक्ष कारण हो सकता है।",
            "options": {
                "bleed_none": "कोई असामान्य रक्तस्राव नहीं",
                "bleed_heavy_periods": "हाँ, सामान्य से अधिक मासिक धर्म",
                "bleed_concerning": "हाँ, स्पष्ट रक्तस्राव या काले रंग का मल"
            }
        },
        "mr": {
            "text": "तुम्हाला अलीकडे कोणताही असामान्य रक्तस्राव, जास्त मासिक पाळी किंवा काळ्या रंगाचे शौच असा त्रास झाला आहे का?",
            "context_reason": "शरीरातून रक्त जाणे हे हिमोग्लोबिन कमी होण्याचे थेट कारण असू शकते.",
            "options": {
                "bleed_none": "कोणताही असामान्य रक्तस्राव नाही",
                "bleed_heavy_periods": "होय, नेहमीपेक्षा जास्त मासिक पाळी",
                "bleed_concerning": "होय, उघड रक्तस्राव किंवा काळ्या रंगाचे शौच"
            }
        }
    },
    "q_general_checkup_reason": {
        "en": {
            "text": "What was the main reason for completing this routine blood work?",
            "context_reason": "Understanding why your doctor ordered the test helps frame what these healthy results mean for your routine.",
            "options": {
                "reason_annual": "Annual preventive checkup or company wellness screen",
                "reason_symptoms": "I was investigating mild fatigue or non-specific symptoms",
                "reason_followup": "Routine follow-up on a previous test"
            }
        },
        "hi": {
            "text": "यह नियमित रक्त परीक्षण कराने का मुख्य कारण क्या था?",
            "context_reason": "परीक्षण का कारण समझने से इन सामान्य परिणामों के अर्थ को सही परिप्रेक्ष्य में रखने में मदद मिलती है।",
            "options": {
                "reason_annual": "वार्षिक स्वास्थ्य परीक्षण या कंपनी वेलनेस चेकअप",
                "reason_symptoms": "हल्की थकान या लक्षणों की जाँच हेतु",
                "reason_followup": "पिछली जाँच का नियमित फॉलो-अप"
            }
        },
        "mr": {
            "text": "ही नियमित रक्त तपासणी करण्याचे मुख्य कारण काय होते?",
            "context_reason": "चाचणीचे कारण समजल्यास हे चांगले निकाल तुमच्या दिनचर्येसाठी काय दर्शवतात हे स्पष्ट होते.",
            "options": {
                "reason_annual": "वार्षिक आरोग्य तपासणी किंवा कंपनी वेलनेस चेकअप",
                "reason_symptoms": "अशक्तपणा किंवा किरकोळ त्रासाची खात्री करण्यासाठी",
                "reason_followup": "मागील तपासणीचा नियमित पाठपुरावा"
            }
        }
    }
}

def get_localized_ui(lang: str = "en") -> Dict[str, str]:
    """Returns UI text map with English safe fallback."""
    target = lang.lower()
    if target in UI_STRINGS:
        return UI_STRINGS[target]
    return UI_STRINGS["en"]

def get_localized_biomarker(canonical_name: str, lang: str = "en") -> Dict[str, Any]:
    """Retrieves localized biomarker explanations with English fallback."""
    entry = BIOMARKER_LOCALIZATION.get(canonical_name, {})
    target = lang.lower()
    return entry.get(target) or entry.get("en", {})

def get_localized_question(q_id: str, lang: str = "en") -> Dict[str, Any]:
    """Retrieves localized question text, context reason, and option labels."""
    entry = QUESTION_LOCALIZATION.get(q_id, {})
    target = lang.lower()
    return entry.get(target) or entry.get("en", {})
