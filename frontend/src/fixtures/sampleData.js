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
    confidence: 0.58,
    requires_verification: true,
    source_box: { x: 45.0, y: 180.0, width: 420.0, height: 30.0 },
    original_extracted_value: "6.3",
    corrected_value: null,
    correction_provenance: "pending_verification"
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
    confidence: 0.62,
    requires_verification: true,
    source_box: { x: 45.0, y: 260.0, width: 420.0, height: 30.0 },
    original_extracted_value: "215",
    corrected_value: null,
    correction_provenance: "pending_verification"
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
    id: "q_fasting",
    text: "Were you strictly fasting for 8 to 12 hours before this morning blood test?",
    context_reason: "Your fasting glucose and HbA1c are slightly above standard reference ranges. Eating before the test can naturally elevate glucose values.",
    options: [
      { id: "yes_fasted", text: "Yes, I fasted for 10+ hours (water only)" },
      { id: "had_snack", text: "I had a tea, coffee, or light bite a few hours before" },
      { id: "not_sure", text: "I don't remember exactly" }
    ]
  },
  {
    id: "q_symptoms",
    text: "Have you noticed any persistent fatigue, unusual thirst, or frequent urination recently?",
    context_reason: "Understanding daily symptoms helps tailor the plain-language summary for your doctor discussion.",
    options: [
      { id: "no_symptoms", text: "No noticeable symptoms — feeling fine" },
      { id: "mild_tiredness", text: "Occasional tiredness in the afternoons" },
      { id: "yes_thirst_fatigue", text: "Yes, increased thirst and tiredness" }
    ]
  },
  {
    id: "q_sun_diet",
    text: "How often do you spend 15–20 minutes outdoors in direct sunlight each week?",
    context_reason: "Your Vitamin D level is slightly low (18.4 ng/mL). Sunlight and dietary habits are the primary natural sources.",
    options: [
      { id: "rarely", text: "Rarely (mostly indoors or covered)" },
      { id: "few_days", text: "2 to 3 days a week" },
      { id: "daily", text: "Almost every day" }
    ]
  }
];

export function generateLocalReport(reportId, answers = []) {
  const hadSnack = answers.some(a => a.question_id === 'q_fasting' && a.selected_option_id === 'had_snack');
  const fastingNote = hadSnack
    ? "Because you mentioned having a snack or beverage before the test, your blood sugar reading may partly reflect that recent food intake."
    : "Since you were properly fasting, this provides a clear baseline reading for your metabolic routine.";

  return {
    report_id: reportId || "rep_local_demo",
    is_synthetic_fixture: true,
    patient_summary: `Your lab results look generally reassuring with a couple of areas to keep an eye on. Your kidney markers are completely in healthy balance. Your blood sugar and cholesterol levels are slightly above typical target ranges. ${fastingNote}`,
    key_findings: [
      {
        biomarker_name: "Blood Sugar (Glucose & HbA1c)",
        status: "high",
        plain_english_summary: "Slightly elevated blood sugar indicators (Glucose 118 mg/dL, HbA1c 6.3%).",
        what_this_means: "This falls into an early watch zone often called prediabetes. It means the body is processing sugar a little slower than usual, but with small daily adjustments it can often be guided back into normal range.",
        reassurance: "This is very common and gives you an early, empowering window of time to make gentle routine tweaks."
      },
      {
        biomarker_name: "Vitamin D (25-OH)",
        status: "low",
        plain_english_summary: "Lower than optimal sunshine vitamin (18.4 ng/mL).",
        what_this_means: "Vitamin D supports bone strength, immune defense, and calm energy. Low levels are extremely common among people who work indoors.",
        reassurance: "Your physician can easily suggest a short course of supplements or morning sunlight habits to replenish this safely."
      },
      {
        biomarker_name: "Kidney Health (Serum Creatinine)",
        status: "normal",
        plain_english_summary: "Creatinine is 0.9 mg/dL — comfortably within the normal range.",
        what_this_means: "Your kidneys are filtering everyday waste effectively and working smoothly.",
        reassurance: "Great sign of solid baseline organ health."
      }
    ],
    lifestyle_tips: [
      "Take a gentle 10-15 minute walk after heavier meals to help muscles absorb natural glucose.",
      "Enjoy 15 minutes of early morning sun exposure, or talk to your doctor about vitamin D3 drops.",
      "Prioritize staying well-hydrated throughout the day with plain water."
    ],
    suggested_doctor_questions: [
      "Given my HbA1c of 6.3%, what lifestyle changes should we start with before considering medication?",
      "Would you recommend a specific dose of Vitamin D supplement for 2-3 months?",
      "When would you like me to repeat this routine metabolic panel?"
    ],
    disclaimer: "Simplifier is an educational tool designed to help you prepare for discussions with your physician. It does not provide medical diagnosis or replace personalized medical counsel."
  };
}
