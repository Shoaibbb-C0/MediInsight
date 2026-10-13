import React, { useState, useEffect } from 'react';
import { Button } from '../common/WarmUI';
import { TRANSLATIONS } from '../../fixtures/translations';

export function InlineNutritionSection({
  reportId = 'rep_demo_fixture',
  language = 'en',
  isExpanded = false,
  onToggleExpand = () => {}
}) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

  // Helper to build initial robust fallback plan
  const buildInitialPlan = (repId, lang) => ({
    plan_id: `plan_initial_${repId}`,
    report_id: repId,
    dietary_preference: 'vegetarian',
    allergies: [],
    dietitian_referral_recommended: false,
    clinical_basis_summary:
      lang === 'hi'
        ? 'रक्त शर्करा को संतुलित रखने के लिए घुलनशील फाइबर और प्रोटीन का समन्वय।'
        : lang === 'mr'
        ? 'रक्तातील साखर नियंत्रित ठेवण्यासाठी विद्राव्य फायबर व प्रथिनांचा समतोल.'
        : 'High-fiber complex carbohydrates paired with plant protein to maintain steady glycemic response.',
    safety_guidance: [
      lang === 'hi'
        ? 'दिनभर पर्याप्त पानी पिएं और अचानक अत्यधिक बदलाव से बचें।'
        : lang === 'mr'
        ? 'दिवसभर पुरेसे पाणी प्या आणि आहारात अचानक टोकाचे बदल टाळा.'
        : 'Stay adequately hydrated with 2.5L clean water daily.',
      lang === 'hi'
        ? 'यह सामान्य स्वास्थ्य शिक्षा है, यह डॉक्टर की दवा का विकल्प नहीं है।'
        : lang === 'mr'
        ? 'हे सामान्य आरोग्य शिक्षणासाठी आहे, डॉक्टरांच्या औषधांचा पर्याय नाही.'
        : 'This guide is for educational wellness and complements your doctor’s advice.'
    ],
    days: Array.from({ length: 7 }, (_, i) => ({
      day_number: i + 1,
      day_name: lang === 'hi' ? `दिन ${i + 1}` : lang === 'mr' ? `दिवस ${i + 1}` : `Day ${i + 1}`,
      focus_theme:
        lang === 'hi'
          ? `दिन ${i + 1}: संतुलित पोषण एवं ऊर्जा`
          : lang === 'mr'
          ? `दिवस ${i + 1}: संतुलित पोषण आणि ऊर्जा`
          : `Day ${i + 1}: Wholesome Foundation & Vitality`,
      breakfast: {
        id: `bf_${i + 1}`,
        name: lang === 'hi' ? 'दलिया और मेथी का नाश्ता' : lang === 'mr' ? 'दलिया आणि मेथीची खिचडी' : 'Broken Wheat Daliya with Vegetables',
        dish_name: lang === 'hi' ? 'दलिया और मेथी का नाश्ता' : lang === 'mr' ? 'दलिया आणि मेथीची खिचडी' : 'Broken Wheat Daliya with Vegetables',
        portion_guidance: '1 medium bowl (250g)',
        why_recommended: 'Slow-release complex carbohydrates that prevent post-meal sugar spikes.',
        allergens: ['gluten'],
        alternatives: [
          {
            id: `bf_alt_${i + 1}`,
            name: lang === 'hi' ? 'जौ का उपमा' : lang === 'mr' ? 'जव उपमा' : 'Vegetable Barley Upma',
            dish_name: lang === 'hi' ? 'जौ का उपमा' : lang === 'mr' ? 'जव उपमा' : 'Vegetable Barley Upma',
            portion_guidance: '1 medium bowl',
            why_it_fits: 'Barley beta-glucan assists in optimal glucose stabilization.',
            why_recommended: 'Barley beta-glucan assists in optimal glucose stabilization.'
          },
          {
            id: `bf_alt2_${i + 1}`,
            name: lang === 'hi' ? 'बेसन का चीला' : lang === 'mr' ? 'बेसनाचे धिरडे' : 'Spiced Besan Chilla with Mint Chutney',
            dish_name: lang === 'hi' ? 'बेसन का चीला' : lang === 'mr' ? 'बेसनाचे धिरडे' : 'Spiced Besan Chilla with Mint Chutney',
            portion_guidance: '2 savory pancakes',
            why_it_fits: 'Gluten-free plant protein from Bengal gram.',
            why_recommended: 'Gluten-free plant protein from Bengal gram.'
          }
        ]
      },
      lunch: {
        id: `lu_${i + 1}`,
        name: lang === 'hi' ? 'पीली मूंग दाल, मेथी रोटी और सलाद' : lang === 'mr' ? 'मुगाचे वरण, मेथी चपाती आणि कोशिंबीर' : 'Yellow Moong Dal with Whole Wheat Roti & Salad',
        dish_name: lang === 'hi' ? 'पीली मूंग दाल, मेथी रोटी और सलाद' : lang === 'mr' ? 'मुगाचे वरण, मेथी चपाती आणि कोशिंबीर' : 'Yellow Moong Dal with Whole Wheat Roti & Salad',
        portion_guidance: '1 bowl dal, 2 medium rotis, 1 cup kachumber salad',
        why_recommended: 'Easily digestible protein and fiber for steady glycemic control.',
        allergens: ['gluten'],
        alternatives: [
          {
            id: `lu_alt_${i + 1}`,
            name: lang === 'hi' ? 'राजमा और भूरे चावल' : lang === 'mr' ? 'राजमा आणि ब्राऊन राइस' : 'Light Kidney Beans (Rajma) with Brown Rice',
            dish_name: lang === 'hi' ? 'राजमा और भूरे चावल' : lang === 'mr' ? 'राजमा आणि ब्राऊन राइस' : 'Light Kidney Beans (Rajma) with Brown Rice',
            portion_guidance: '1 cup rajma with 1 cup cooked brown rice',
            why_it_fits: 'Rich in soluble fiber and sustained energy.',
            why_recommended: 'Rich in soluble fiber and sustained energy.'
          },
          {
            id: `lu_alt2_${i + 1}`,
            name: lang === 'hi' ? 'पालक दाल और ज्वार रोटी' : lang === 'mr' ? 'पालक वरण आणि ज्वारीची भाकरी' : 'Spinach Dal Tadka with Jowar Roti',
            dish_name: lang === 'hi' ? 'पालक दाल और ज्वार रोटी' : lang === 'mr' ? 'पालक वरण आणि ज्वारीची भाकरी' : 'Spinach Dal Tadka with Jowar Roti',
            portion_guidance: '1 bowl dal, 1 jowar roti',
            why_it_fits: 'Abundant dietary folate and millet fiber.',
            why_recommended: 'Abundant dietary folate and millet fiber.'
          }
        ]
      },
      dinner: {
        id: `di_${i + 1}`,
        name: lang === 'hi' ? 'लौकी की सब्जी और बाजरा रोटी' : lang === 'mr' ? 'दुधी भोपळ्याची भाजी आणि बाजरीची भाकरी' : 'Bottle Gourd (Lauki) Curry with Bajra Roti',
        dish_name: lang === 'hi' ? 'लौकी की सब्जी और बाजरा रोटी' : lang === 'mr' ? 'दुधी भोपळ्याची भाजी आणि बाजरीची भाकरी' : 'Bottle Gourd (Lauki) Curry with Bajra Roti',
        portion_guidance: '1 bowl subzi, 1-2 bajra rotis',
        why_recommended: 'Light evening meal that supports natural overnight metabolic balance.',
        allergens: [],
        alternatives: [
          {
            id: `di_alt_${i + 1}`,
            name: lang === 'hi' ? 'पालक पनीर और मल्टीग्रेन रोटी' : lang === 'mr' ? 'पालक पनीर आणि चपाती' : 'Palak Paneer with Multigrain Roti',
            dish_name: lang === 'hi' ? 'पालक पनीर और मल्टीग्रेन रोटी' : lang === 'mr' ? 'पालक पनीर आणि चपाती' : 'Palak Paneer with Multigrain Roti',
            portion_guidance: '1 bowl curry, 2 small rotis',
            why_it_fits: 'High protein and calcium supporting muscle recovery.',
            why_recommended: 'High protein and calcium supporting muscle recovery.'
          },
          {
            id: `di_alt2_${i + 1}`,
            name: lang === 'hi' ? 'मूंग दाल खिचड़ी' : lang === 'mr' ? 'मुगाची मऊ खिचडी' : 'Comfort Moong Dal Khichdi with Curd',
            dish_name: lang === 'hi' ? 'मूंग दाल खिचड़ी' : lang === 'mr' ? 'मुगाची मऊ खिचडी' : 'Comfort Moong Dal Khichdi with Curd',
            portion_guidance: '1 medium warm bowl',
            why_it_fits: 'Complete amino acid profile and gentle digestion.',
            why_recommended: 'Complete amino acid profile and gentle digestion.'
          }
        ]
      },
      snack: {
        id: `sn_${i + 1}`,
        name: lang === 'hi' ? 'भुने हुए चने और ग्रीन टी' : lang === 'mr' ? 'भाजलेले चणे आणि ग्रीन टी' : 'Roasted Chana with Green Tea',
        dish_name: lang === 'hi' ? 'भुने हुए चने और ग्रीन टी' : lang === 'mr' ? 'भाजलेले चणे आणि ग्रीन टी' : 'Roasted Chana with Green Tea',
        portion_guidance: 'Handful (30-40g)',
        why_recommended: 'Satisfies crunch with non-starchy complex protein.',
        allergens: [],
        alternatives: [
          {
            id: `sn_alt_${i + 1}`,
            name: lang === 'hi' ? 'अंकुरित मूंग चाट' : lang === 'mr' ? 'मोड आलेले मूग चाट' : 'Sprouted Moong Salad with Lemon',
            dish_name: lang === 'hi' ? 'अंकुरित मूंग चाट' : lang === 'mr' ? 'मोड आलेले मूग चाट' : 'Sprouted Moong Salad with Lemon',
            portion_guidance: '1 small cup',
            why_it_fits: 'Live enzymes and crisp fiber.',
            why_recommended: 'Live enzymes and crisp fiber.'
          },
          {
            id: `sn_alt2_${i + 1}`,
            name: lang === 'hi' ? 'हल्दी-नमक में भुने मखाने' : lang === 'mr' ? 'हळद-मीठ घालून भाजलेले मखाणे' : 'Roasted Fox Nuts (Makhana) with Turmeric',
            dish_name: lang === 'hi' ? 'हल्दी-नमक में भुने मखाने' : lang === 'mr' ? 'हळद-मीठ घालून भाजलेले मखाणे' : 'Roasted Fox Nuts (Makhana) with Turmeric',
            portion_guidance: '1 small bowl (25-30g)',
            why_it_fits: 'Low sodium and heart-friendly crunch.',
            why_recommended: 'Low sodium and heart-friendly crunch.'
          }
        ]
      }
    }))
  });

  // State
  const [viewMode, setViewMode] = useState('plan'); // 'plan' | 'questionnaire'
  const [activeDay, setActiveDay] = useState(1);
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(() => buildInitialPlan(reportId, language));
  const [questions, setQuestions] = useState([]);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [swappingMeal, setSwappingMeal] = useState(null);
  const [swapLoading, setSwapLoading] = useState(false);

  // Sync plan on language or report change
  useEffect(() => {
    let isMounted = true;
    const fetchPlan = async () => {
      setLoading(true);
      try {
        const res = await fetch(`/api/v1/reports/${reportId}/nutrition/plan?lang=${language}`);
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            setPlan(data);
            setViewMode('plan');
          }
        }
      } catch (err) {
        console.warn('Fallback loading plan:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    if (reportId) {
      fetchPlan();
    }

    return () => {
      isMounted = false;
    };
  }, [reportId, language]);

  const loadQuestions = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/reports/${reportId}/nutrition/questions?lang=${language}`);
      if (res.ok) {
        const data = await res.json();
        setQuestions(data.questions || []);
        setViewMode('questionnaire');
        setCurrentQIndex(0);
      } else {
        setViewMode('questionnaire');
      }
    } catch {
      setViewMode('questionnaire');
    } finally {
      setLoading(false);
    }
  };

  const handleOptionSelect = (qId, optionId, isMulti = false) => {
    setAnswers((prev) => {
      if (!isMulti) {
        return { ...prev, [qId]: optionId };
      }
      const existing = Array.isArray(prev[qId]) ? prev[qId] : [];
      if (optionId === 'none') {
        return { ...prev, [qId]: ['none'] };
      }
      const filtered = existing.filter((id) => id !== 'none');
      if (filtered.includes(optionId)) {
        const next = filtered.filter((id) => id !== optionId);
        return { ...prev, [qId]: next.length ? next : ['none'] };
      } else {
        return { ...prev, [qId]: [...filtered, optionId] };
      }
    });
  };

  const handleNextQuestion = () => {
    if (currentQIndex < questions.length - 1) {
      setCurrentQIndex((prev) => prev + 1);
    } else {
      generatePlanFromAnswers();
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQIndex > 0) {
      setCurrentQIndex((prev) => prev - 1);
    }
  };

  const generatePlanFromAnswers = async () => {
    setLoading(true);
    try {
      const allergySelection = answers.nq_allergies || answers.q_food_allergies || ['none'];
      const rawAllergies = Array.isArray(allergySelection)
        ? allergySelection
        : [allergySelection.replace('allergy_', '')];
      const cleanAllergies = rawAllergies.filter((a) => a !== 'none' && a !== 'allergy_none');

      const restrictionsSelection = answers.nq_special_restrictions || [];
      const cleanRestrictions = Array.isArray(restrictionsSelection)
        ? restrictionsSelection.filter((r) => r !== 'none')
        : [];

      const conditionsSelection = answers.nq_health_conditions || [];
      const cleanConditions = Array.isArray(conditionsSelection)
        ? conditionsSelection.filter((c) => c !== 'none')
        : [];

      const payload = {
        report_id: reportId,
        dietary_preference: answers.nq_dietary_pref || answers.q_diet_pattern || 'vegetarian',
        allergies: cleanAllergies.length ? cleanAllergies : ['none'],
        food_restrictions: cleanRestrictions,
        known_conditions: cleanConditions,
        meals_per_day: answers.nq_routine || answers.q_meal_routine || '3_meals',
        budget: answers.nq_cooking || answers.q_budget_cooking || 'moderate',
        preferred_cuisine: answers.nq_cuisine_pref || 'indian_regional',
        primary_goal: answers.nq_primary_goal || answers.q_primary_goal || 'understand_lab_choices'
      };

      const res = await fetch(`/api/v1/reports/${reportId}/nutrition/generate?lang=${language}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const newPlan = await res.json();
        setPlan(newPlan);
        setViewMode('plan');
        setActiveDay(1);
      }
    } catch (err) {
      console.warn('Generate plan failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSwapClick = (dayNumber, mealType, mealData) => {
    const dishName = mealData.name || mealData.dish_name || 'Current meal';
    setSwappingMeal({
      day_number: dayNumber,
      meal_type: mealType,
      current_dish_name: dishName,
      alternatives: mealData.alternatives || []
    });
  };

  const executeMealSwap = async (altItem) => {
    if (!swappingMeal || !plan) return;
    setSwapLoading(true);
    const newMealId = altItem.id || altItem.meal_id;
    try {
      const res = await fetch(`/api/v1/reports/nutrition/swap?lang=${language}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan_id: plan.plan_id,
          day_number: swappingMeal.day_number,
          meal_type: swappingMeal.meal_type,
          new_meal_id: newMealId
        })
      });

      if (res.ok) {
        const updated = await res.json();
        setPlan(updated);
        setSwappingMeal(null);
      } else {
        // Optimistic local state update
        const updatedPlan = JSON.parse(JSON.stringify(plan));
        const dayIdx = swappingMeal.day_number - 1;
        const currentMeal = updatedPlan.days[dayIdx][swappingMeal.meal_type];
        const oldName = currentMeal.name || currentMeal.dish_name;
        const oldId = currentMeal.id || currentMeal.meal_id;
        const newName = altItem.name || altItem.dish_name;

        currentMeal.name = newName;
        currentMeal.dish_name = newName;
        currentMeal.id = newMealId;
        currentMeal.meal_id = newMealId;
        currentMeal.portion_guidance = altItem.portion_guidance || currentMeal.portion_guidance;
        currentMeal.why_recommended = altItem.why_recommended || altItem.why_it_fits || currentMeal.why_recommended;

        // Push old meal into alternatives
        currentMeal.alternatives = [
          {
            id: oldId,
            meal_id: oldId,
            name: oldName,
            dish_name: oldName,
            portion_guidance: currentMeal.portion_guidance,
            why_recommended: 'Previously assigned balanced option.',
            why_it_fits: 'Previously assigned balanced option.'
          }
        ];
        setPlan(updatedPlan);
        setSwappingMeal(null);
      }
    } catch (e) {
      console.warn('Swap error:', e);
      setSwappingMeal(null);
    } finally {
      setSwapLoading(false);
    }
  };

  const handleDownloadPdf = () => {
    window.open(`/api/v1/reports/${reportId}/nutrition/pdf?lang=${language}`, '_blank');
  };

  const currentDayData = plan?.days?.find((d) => d.day_number === activeDay) || plan?.days?.[0];

  return (
    <section
      id="nutrition-plan-section"
      className="bg-clarity-surface rounded-3xl border border-clarity-border p-6 sm:p-8 shadow-soft mb-8 transition-all"
    >
      {/* SECTION HEADER & TOGGLE */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-clarity-border/70 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">🥗</span>
            <h2 className="text-xl sm:text-2xl font-bold text-clarity-teal">
              {t.yourFoodPlanHeading || 'Your food plan, made for you'}
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-clarity-muted">
            {t.nutritionSubtitle}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {!isExpanded ? (
            <Button
              variant="mint"
              size="md"
              onClick={onToggleExpand}
              className="justify-center"
            >
              {t.buildNutritionAction || 'Build My Weekly Nutrition Plan'} &darr;
            </Button>
          ) : (
            <Button
              variant="secondary"
              size="sm"
              onClick={onToggleExpand}
              className="justify-center"
            >
              {language === 'hi' ? 'छिपाएं' : language === 'mr' ? 'लपवा' : 'Minimize'} &uarr;
            </Button>
          )}
        </div>
      </div>

      {/* EXPANDED CONTENT FLOW */}
      {isExpanded && (
        <div className="animate-in fade-in space-y-6">
          {/* QUESTIONNAIRE MODE */}
          {viewMode === 'questionnaire' ? (
            <div className="py-2">
              {loading ? (
                <div className="py-12 text-center text-clarity-teal">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-clarity-teal border-t-transparent mb-3" />
                  <p className="text-sm font-semibold">{t.readingReport}</p>
                </div>
              ) : questions.length > 0 ? (
                <div className="space-y-6">
                  {/* Progress Header */}
                  <div className="flex items-center justify-between text-xs text-clarity-muted">
                    <span className="font-semibold text-clarity-teal">
                      {t.questionProgress} {currentQIndex + 1} / {questions.length}
                    </span>
                    <button
                      type="button"
                      onClick={() => generatePlanFromAnswers()}
                      className="text-clarity-coral hover:underline font-semibold"
                    >
                      {t.skipAllQuestions || 'Skip to plan'}
                    </button>
                  </div>

                  {/* Active Question Box */}
                  <div className="p-5 sm:p-6 rounded-2xl bg-clarity-ivory/80 border border-clarity-border">
                    <h3 className="text-base sm:text-lg font-bold text-clarity-charcoal mb-2">
                      {questions[currentQIndex]?.text || questions[currentQIndex]?.question_text}
                    </h3>
                    <p className="text-xs text-clarity-muted mb-5 leading-relaxed">
                      {questions[currentQIndex]?.context_reason}
                    </p>

                    <div className="space-y-3">
                      {questions[currentQIndex]?.options?.map((opt) => {
                        const qId = questions[currentQIndex].id || questions[currentQIndex].question_id;
                        const optId = opt.id || opt.option_id;
                        const optText = opt.text || opt.option_label;
                        const isMulti = questions[currentQIndex].is_multi_select;
                        const userAns = answers[qId];
                        const isSelected = isMulti
                          ? Array.isArray(userAns) && userAns.includes(optId)
                          : userAns === optId;

                        return (
                          <button
                            key={optId}
                            type="button"
                            onClick={() => handleOptionSelect(qId, optId, isMulti)}
                            className={`w-full text-left p-4 rounded-xl border transition-all text-sm flex items-center justify-between ${
                              isSelected
                                ? 'bg-clarity-mint/20 border-clarity-teal text-clarity-teal font-semibold shadow-xs'
                                : 'bg-clarity-surface border-clarity-border text-clarity-charcoal hover:border-clarity-mint'
                            }`}
                          >
                            <span>{optText}</span>
                            <div
                              className={`w-4 h-4 ${
                                isMulti ? 'rounded-md' : 'rounded-full'
                              } border flex items-center justify-center shrink-0 ml-3 ${
                                isSelected ? 'border-clarity-teal bg-clarity-teal text-white' : 'border-clarity-border'
                              }`}
                            >
                              {isSelected && (
                                <span className="text-[10px] font-bold">✓</span>
                              )}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Navigation Buttons */}
                  <div className="flex justify-between items-center pt-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={handlePreviousQuestion}
                      disabled={currentQIndex === 0}
                    >
                      &larr; Back
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={handleNextQuestion}
                    >
                      {currentQIndex === questions.length - 1 ? t.generatePlanBtn : t.nextQuestion} &rarr;
                    </Button>
                  </div>
                </div>
              ) : null}
            </div>
          ) : (
            /* 7-DAY PLAN VIEW */
            <div className="space-y-6">
              {/* High-Risk Clinical Warning Banner */}
              {plan.dietitian_referral_recommended && (
                <div className="p-4 sm:p-5 rounded-2xl bg-amber-50 border border-amber-300 text-amber-950 flex items-start gap-3 shadow-soft">
                  <span className="text-xl shrink-0 mt-0.5">⚠️</span>
                  <div>
                    <h4 className="font-bold text-sm text-amber-950">
                      {t.dietitianNoticeTitle}
                    </h4>
                    <p className="text-xs text-amber-900 mt-1 leading-relaxed">
                      {plan.dietitian_referral_reason || t.dietitianNoticeBody}
                    </p>
                  </div>
                </div>
              )}

              {/* SECTION B: CLINICAL BASIS CARD */}
              {plan.clinical_basis_summary && (
                <div className="p-4 sm:p-5 rounded-2xl bg-clarity-mint/15 border border-clarity-mint/40">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-clarity-teal mb-2">
                    {language === 'hi' ? 'इस योजना का मुख्य आधार' : language === 'mr' ? 'या नियोजनाचा मुख्य पाया' : 'What shaped your plan'}
                  </h4>
                  <p className="text-xs sm:text-sm text-clarity-charcoal leading-relaxed">
                    {plan.clinical_basis_summary}
                  </p>
                  <div className="mt-3 pt-2.5 border-t border-clarity-border/40 text-xs text-clarity-muted flex flex-wrap gap-4">
                    <span>
                      <strong>{language === 'hi' ? 'आहार शैली: ' : language === 'mr' ? 'आहार पद्धत: ' : 'Preference: '}</strong>
                      {plan.dietary_preference}
                    </span>
                    <span>
                      <strong>{language === 'hi' ? 'एलर्जी बाहर रखी गई: ' : language === 'mr' ? 'वगळलेली ॲलर्जी: ' : 'Allergy Exclusions: '}</strong>
                      {plan.allergies?.length ? plan.allergies.join(', ') : (language === 'hi' ? 'कोई नहीं' : language === 'mr' ? 'काहीही नाही' : 'None reported')}
                    </span>
                  </div>
                </div>
              )}

              {/* SECTION C & D: 7-DAY NAVIGATION TABS */}
              <div className="flex gap-2 overflow-x-auto pb-2 border-b border-clarity-border/80 scrollbar-none">
                {plan.days?.map((d) => (
                  <button
                    key={d.day_number}
                    type="button"
                    onClick={() => setActiveDay(d.day_number)}
                    className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold whitespace-nowrap transition-all ${
                      activeDay === d.day_number
                        ? 'bg-clarity-teal text-white shadow-soft'
                        : 'bg-clarity-ivory text-clarity-muted hover:text-clarity-charcoal hover:bg-clarity-mint/20'
                    }`}
                  >
                    {t.dayTab} {d.day_number}
                  </button>
                ))}
              </div>

              {/* Day Focus Theme */}
              {currentDayData && (
                <div className="flex items-center justify-between">
                  <h3 className="text-sm sm:text-base font-bold text-clarity-teal">
                    {currentDayData.focus_theme || currentDayData.day_name}
                  </h3>
                  <span className="text-xs text-clarity-muted">
                    {language === 'hi' ? 'दैनिक पोषण कार्यक्रम' : language === 'mr' ? 'दैनंदिन आहार वेळापत्रक' : 'Daily Meal Schedule'}
                  </span>
                </div>
              )}

              {/* SECTION E: MEAL CARDS (Breakfast, Lunch, Dinner, Snack) */}
              {currentDayData && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { key: 'breakfast', label: t.breakfast, icon: '🌅', meal: currentDayData.breakfast },
                    { key: 'lunch', label: t.lunch, icon: '☀️', meal: currentDayData.lunch },
                    { key: 'dinner', label: t.dinner, icon: '🌙', meal: currentDayData.dinner },
                    { key: 'snack', label: t.snack, icon: '🍵', meal: currentDayData.snack }
                  ].map(({ key, label, icon, meal }) => {
                    if (!meal) return null;
                    const dishName = meal.name || meal.dish_name;
                    return (
                      <div
                        key={key}
                        className="p-4 sm:p-5 rounded-2xl bg-clarity-surface border border-clarity-border shadow-soft flex flex-col justify-between"
                      >
                        <div>
                          <div className="flex justify-between items-start mb-2">
                            <span className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-clarity-muted">
                              <span>{icon}</span> {label}
                            </span>
                            {meal.alternatives?.length > 0 && (
                              <button
                                type="button"
                                onClick={() => handleSwapClick(currentDayData.day_number, key, meal)}
                                className="text-xs font-semibold text-clarity-coral hover:underline inline-flex items-center gap-1"
                              >
                                <span>⇄</span> {t.swapMeal}
                              </button>
                            )}
                          </div>
                          <h4 className="font-bold text-sm sm:text-base text-clarity-charcoal mb-1">
                            {dishName}
                          </h4>
                          <p className="text-xs text-clarity-muted mb-2">
                            <strong>{t.portionGuidance}:</strong> {meal.portion_guidance}
                          </p>
                          <p className="text-xs text-clarity-charcoal leading-relaxed bg-clarity-ivory/60 p-2.5 rounded-xl border border-clarity-border/60">
                            {meal.why_recommended}
                          </p>
                        </div>

                        {meal.allergens?.length > 0 && (
                          <div className="mt-3 pt-2 border-t border-clarity-border/40 text-[10px] text-amber-900 flex items-center gap-1.5">
                            <span>⚠️ {t.allergens}:</span>
                            <span className="font-medium">{meal.allergens.join(', ')}</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* HYDRATION & REPEAT NOTE */}
              {currentDayData?.hydration_guidance && (
                <div className="p-4 bg-teal-50/50 rounded-2xl border border-teal-200/60 text-xs text-clarity-charcoal leading-relaxed flex items-center gap-3">
                  <span className="text-lg">💧</span>
                  <div>
                    <strong>{language === 'hi' ? 'दैनिक जल सेवन: ' : language === 'mr' ? 'दैनिक पाणी पिणे: ' : 'Daily Hydration: '}</strong>
                    {currentDayData.hydration_guidance}
                  </div>
                </div>
              )}

              {/* ACTIONS FOOTER */}
              <div className="pt-4 border-t border-clarity-border flex flex-wrap items-center justify-between gap-3">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => loadQuestions()}
                >
                  ⚙️ {t.recalculatePlanBtn}
                </Button>

                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleDownloadPdf}
                >
                  📥 {t.downloadNutritionPdf}
                </Button>
              </div>

              {/* MEDICAL DISCLAIMER */}
              <p className="text-[11px] text-clarity-muted leading-relaxed italic bg-clarity-ivory/50 p-3 rounded-xl border border-clarity-border/40">
                {plan.disclaimer || t.generalDietDisclaimer}
              </p>
            </div>
          )}
        </div>
      )}

      {/* SWAP MEAL OVERLAY */}
      {swappingMeal && (
        <div className="fixed inset-0 z-60 flex items-center justify-center p-4 bg-clarity-charcoal/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-5 max-w-md w-full shadow-elevated">
            <div className="flex justify-between items-center mb-3">
              <h4 className="font-bold text-base text-clarity-teal">
                {t.availableAlternatives}
              </h4>
              <button
                type="button"
                onClick={() => setSwappingMeal(null)}
                className="text-clarity-muted hover:text-clarity-charcoal text-sm p-1"
              >
                ✕
              </button>
            </div>
            <p className="text-xs text-clarity-muted mb-4">
              Replacing: <strong>{swappingMeal.current_dish_name}</strong>
            </p>

            <div className="space-y-3 max-h-64 overflow-y-auto mb-4">
              {swappingMeal.alternatives?.map((alt, idx) => {
                const altName = alt.name || alt.dish_name;
                const altWhy = alt.why_recommended || alt.why_it_fits;
                return (
                  <div
                    key={alt.id || alt.meal_id || idx}
                    className="p-3.5 rounded-xl border border-clarity-border bg-clarity-ivory hover:border-clarity-teal transition-all flex flex-col justify-between gap-2"
                  >
                    <div>
                      <h5 className="font-bold text-sm text-clarity-charcoal">
                        {altName}
                      </h5>
                      <p className="text-xs text-clarity-muted mt-0.5">
                        {alt.portion_guidance}
                      </p>
                      <p className="text-[11px] text-clarity-charcoal mt-1">
                        {altWhy}
                      </p>
                    </div>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => executeMealSwap(alt)}
                      disabled={swapLoading}
                    >
                      {swapLoading ? 'Updating...' : t.selectAlternative}
                    </Button>
                  </div>
                );
              })}
            </div>

            <div className="flex justify-end">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setSwappingMeal(null)}
              >
                {t.cancelSwap}
              </Button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
