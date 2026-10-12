export const LOCAL_SYNTHETIC_BIOMARKERS = [
  {
    id: "bio_1",
    name: "Fasting Blood Glucose",
    canonical_name: "glucose_fasting",
    value: "118",
    unit: "mg/dL",
    reference_range: "70 - 99 mg/dL",
    status: "high",
    confidence: 0.96,
    requires_verification: false,
    source_box: { x: 45.0, y: 140.0, width: 420.0, height: 28.0 },
    original_extracted_value: "118",
    corrected_value: null,
    correction_provenance: "verified_match"
  },
  {
    id: "bio_2",
    name: "HbA1c (Glycated Hemoglobin)",
    canonical_name: "hba1c",
    value: "6.3",
    unit: "%",
    reference_range: "< 5.7 %",
    status: "high",
    confidence: 0.95,
    requires_verification: false,
    source_box: { x: 45.0, y: 180.0, width: 420.0, height: 30.0 },
    original_extracted_value: "6.3",
    corrected_value: null,
    correction_provenance: "verified_match"
  },
  {
    id: "bio_3",
    name: "Serum Creatinine",
    canonical_name: "creatinine_serum",
    value: "0.9",
    unit: "mg/dL",
    reference_range: "0.7 - 1.3 mg/dL",
    status: "normal",
    confidence: 0.99,
    requires_verification: false,
    source_box: { x: 45.0, y: 220.0, width: 420.0, height: 28.0 },
    original_extracted_value: "0.9",
    corrected_value: null,
    correction_provenance: "verified_match"
  },
  {
    id: "bio_4",
    name: "Total Cholesterol",
    canonical_name: "cholesterol_total",
    value: "215",
    unit: "mg/dL",
    reference_range: "< 200 mg/dL",
    status: "high",
    confidence: 0.93,
    requires_verification: false,
    source_box: { x: 45.0, y: 260.0, width: 420.0, height: 30.0 },
    original_extracted_value: "215",
    corrected_value: null,
    correction_provenance: "verified_match"
  },
  {
    id: "bio_5",
    name: "Vitamin D (25-OH)",
    canonical_name: "vitamin_d",
    value: "18.4",
    unit: "ng/mL",
    reference_range: "30 - 100 ng/mL",
    status: "low",
    confidence: 0.94,
    requires_verification: false,
    source_box: { x: 45.0, y: 300.0, width: 420.0, height: 28.0 },
    original_extracted_value: "18.4",
    corrected_value: null,
    correction_provenance: "verified_match"
  }
];

export const LOCAL_SYNTHETIC_QUESTIONS = [
  {
    id: "q_glucose_fasting",
    text: "Were you strictly fasting for 8 to 12 hours before this morning blood test?",
    context_reason: "Your fasting glucose is slightly above standard reference ranges. Eating before testing can naturally raise glucose values.",
    options: [
      { id: "fasting_strictly", text: "Yes, strictly fasted (water only for 10+ hours)" },
      { id: "fasting_had_bite", text: "I had a tea, coffee, or light bite a few hours before" },
      { id: "fasting_unsure", text: "I don't remember exactly" }
    ]
  },
  {
    id: "q_glucose_symptoms",
    text: "Have you noticed any persistent fatigue, unusual thirst, or frequent urination recently?",
    context_reason: "Understanding daily symptoms helps tailor the plain-language summary for your doctor discussion.",
    options: [
      { id: "gluc_sym_none", text: "None of these symptoms — feeling fine" },
      { id: "gluc_sym_thirst", text: "Yes, increased thirst and frequent urination" },
      { id: "gluc_sym_weightloss", text: "Yes, fatigue or unexplained weight changes" }
    ]
  },
  {
    id: "q_vitd_sun_habits",
    text: "How often do you spend 15–20 minutes outdoors in direct sunlight each week?",
    context_reason: "Your Vitamin D level is slightly low (18.4 ng/mL). Sunlight and dietary habits are the primary natural sources.",
    options: [
      { id: "sun_rarely", text: "Rarely (mostly indoors or covered)" },
      { id: "sun_moderate", text: "2 to 3 days a week" },
      { id: "sun_daily", text: "Almost every day" }
    ]
  }
];

export function generateLocalReport(reportId, answers = [], lang = 'en') {
  const hadSnack = answers.some(a => a.selected_option_id === 'fasting_had_bite');

  let fastingNote = "";
  let summary = "";
  if (lang === 'hi') {
    fastingNote = hadSnack
      ? "क्योंकि आपने जाँच से पहले चाय या नाश्ता लिया था, इसलिए आपकी शुगर का स्तर भोजन के कारण भी बढ़ सकता है।"
      : "क्योंकि आपने पूरी तरह खाली पेट जाँच कराई थी, यह आपकी नियमित मेटाबॉलिक स्थिति का सटीक आधार है।";
    summary = `आपकी जाँच में ३ परिणाम सामान्य संदर्भ सीमा से बाहर हैं। आपके गुर्दे के परीक्षण (क्रिएटिनिन) पूरी तरह स्वस्थ और संतुलित हैं। रक्तातील साखर आणि कोलेस्ट्रॉल किंचित जास्त आहेत. ${fastingNote}`;
  } else if (lang === 'mr') {
    fastingNote = hadSnack
      ? "तपासणीपूर्वी तुम्ही चहा किंवा हलका नाश्ता घेतल्याने, वाढलेली साखर तात्पुरती अन्नामुळे असू शकते."
      : "तुम्ही पूर्णपणे उपाशीपोटी तपासणी केल्याने, हा तुमच्या चयापचयाचा अचूक पाया आहे.";
    summary = `तुमच्या तपासणीत ३ निकाल नेहमीच्या संदर्भ मर्यादेपेक्षा किंचित बाहेर आढळले आहेत. मूत्रपिंडाचे निकाल (क्रिएटिनिन) पूर्णपणे निरोगी आणि संतुलित आहेत. ${fastingNote}`;
  } else {
    fastingNote = hadSnack
      ? "Because you mentioned having a snack or beverage before the test, your blood sugar reading may partly reflect that recent food intake."
      : "Since you were properly fasting, this provides a clear baseline reading for your metabolic routine.";
    summary = `Your lab results look generally reassuring with a couple of areas to keep an eye on. Your kidney markers are completely in healthy balance. Your blood sugar and cholesterol levels are slightly above typical target ranges. ${fastingNote}`;
  }

  const attentionItems = [
    {
      name: lang === 'hi' ? "फास्टिंग ब्लड ग्लूकोज (खाली पेट रक्त शर्करा)" : lang === 'mr' ? "फास्टिंग ब्लड ग्लुकोज (उपाशीपोटी रक्तातील साखर)" : "Fasting Blood Glucose",
      value: "118 mg/dL",
      reference_range: "70 - 99 mg/dL",
      status: "high",
      status_label: lang === 'hi' ? "सामान्य से अधिक" : lang === 'mr' ? "किंचित जास्त" : "Slightly High",
      why_outside_range: lang === 'hi' ? "कोशिकाओं तक शुगर पहुँचने में सामान्य से अधिक समय लग रहा है।" : lang === 'mr' ? "शरीरातील पेशींपर्यंत साखर शोषण्यास नेहमीपेक्षा जास्त वेळ लागत आहे." : "Higher readings mean glucose takes longer to move into cells. May reflect early insulin resistance or recent food intake."
    },
    {
      name: lang === 'hi' ? "एचबीए1सी (ग्लाइकेटेड हीमोग्लोबिन)" : lang === 'mr' ? "एचबीए१सी (ग्लायकेटेड हिमोग्लोबिन)" : "HbA1c (Glycated Hemoglobin)",
      value: "6.3 %",
      reference_range: "< 5.7 %",
      status: "high",
      status_label: lang === 'hi' ? "सामान्य से अधिक" : lang === 'mr' ? "किंचित जास्त" : "Slightly High",
      why_outside_range: lang === 'hi' ? "शुरुआती निगरानी क्षेत्र (प्रीडायबिटीज) दर्शाता है।" : lang === 'mr' ? "सुरुवातीची काळजी घेण्याची पातळी दर्शवते." : "Between 5.7% and 6.4% suggests early watch zone (prediabetes); responsive to simple daily habits."
    },
    {
      name: lang === 'hi' ? "विटामिन डी (सनशाइन विटामिन)" : lang === 'mr' ? "व्हिटॅमिन डी (सूर्यप्रकाश जीवनसत्व)" : "Vitamin D (25-OH)",
      value: "18.4 ng/mL",
      reference_range: "30 - 100 ng/mL",
      status: "low",
      status_label: lang === 'hi' ? "सामान्य से कम" : lang === 'mr' ? "किंचित कमी" : "Slightly Low",
      why_outside_range: lang === 'hi' ? "धूप की कमी के कारण कम स्तर होना बेहद आम है।" : lang === 'mr' ? "सूर्यप्रकाशाच्या अभावामुळे कमी प्रमाण असणे अत्यंत सामान्य आहे." : "Low vitamin D is extremely common in indoor lifestyle and easy to restore with gentle advice."
    }
  ];

  const withinRangeItems = [
    {
      name: lang === 'hi' ? "सीरम क्रिएटिनिन (गुर्दे की कार्यप्रणाली)" : lang === 'mr' ? "सीरम क्रिएटिनिन (मूत्रपिंड कार्यक्षमता)" : "Serum Creatinine",
      value: "0.9 mg/dL",
      reference_range: "0.7 - 1.3 mg/dL",
      status: "normal",
      status_label: lang === 'hi' ? "संतुलित स्तर" : lang === 'mr' ? "संतुलित प्रमाण" : "Healthy Range"
    }
  ];

  return {
    report_id: reportId || "rep_local_demo",
    language: lang,
    is_synthetic_fixture: true,
    patient_summary: summary,
    prioritized_attention: attentionItems,
    within_range_results: withinRangeItems,
    unreliable_flagged_results: [],
    context_insights: [fastingNote],
    suggested_doctor_questions: lang === 'hi' ? [
      "मेरी ६.३% एचबीए1सी को देखते हुए कौन से जीवनशैली बदलाव पहले करने चाहिए?",
      "विटामिन डी के लिए क्या आप कोई विशिष्ट सप्लीमेंट खुराक सुझाएंगे?"
    ] : lang === 'mr' ? [
      "६.३% एचबीए१सी पातळी लक्षात घेता जीवनशैलीत कोणते बदल करावेत?",
      "व्हिटॅमिन डी पूर्ववत करण्यासाठी आपण कोणते सप्लिमेंट्स सुचवाल?"
    ] : [
      "Given my HbA1c of 6.3%, what lifestyle changes should we start with before considering medication?",
      "Would you recommend a specific dose of Vitamin D supplement for 2-3 months?"
    ],
    safe_next_steps: lang === 'hi' ? [
      "अपने डॉक्टर से इन नतीजों पर सामान्य चर्चा का समय तय करें।",
      "भरपूर पानी पिएं और बिना सलाह कोई दवा शुरू न करें।"
    ] : lang === 'mr' ? [
      "डॉक्टरांशी चर्चेसाठी सर्वसाधारण भेट ठरवा.",
      "पुरेसे पाणी प्या आणि डॉक्टरांच्या सल्ल्याशिवाय औषधे सुरू करू नका."
    ] : [
      "Schedule a non-urgent routine consultation to review these lab results with your physician.",
      "Maintain steady hydration and avoid making radical unsupervised supplement changes."
    ],
    disclaimer: "Simplifier is an educational tool designed to help you prepare for discussions with your physician. It does not provide medical diagnosis or replace personalized medical counsel."
  };
}
