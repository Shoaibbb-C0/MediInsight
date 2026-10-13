import React, { useState, useEffect } from 'react';
import { Button } from '../common/WarmUI';
import { TRANSLATIONS } from '../../fixtures/translations';

export function InlineNutritionModal({
  isOpen,
  onClose,
  reportId = 'rep_demo_fixture',
  language = 'en'
}) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

  // Helper to build initial plan
  const buildInitialPlan = (repId, lang) => ({
    plan_id: `plan_initial_${repId}`,
    report_id: repId,
    dietary_pattern: 'vegetarian',
    dietitian_referral_recommended: false,
    clinical_rationale: [
      lang === 'hi'
        ? 'रक्त शर्करा को संतुलित रखने के लिए घुलनशील फाइबर और प्रोटीन का समन्वय।'
        : lang === 'mr'
        ? 'रक्तातील साखर नियंत्रित ठेवण्यासाठी विद्राव्य फायबर व प्रथिनांचा समतोल.'
        : 'High-fiber complex carbohydrates paired with protein to maintain steady glucose response.'
    ],
    safety_guidance: [
      lang === 'hi'
        ? 'दिनभर पर्याप्त पानी पिएं और अचानक अत्यधिक बदलाव से बचें।'
        : lang === 'mr'
        ? 'दिवसभर पुरेसे पाणी प्या आणि आहारात अचानक टोकाचे बदल टाळा.'
        : 'Stay adequately hydrated with 2.5L clean water daily.'
    ],
    days: Array.from({ length: 7 }, (_, i) => ({
      day_number: i + 1,
      breakfast: {
        meal_id: `bf_${i + 1}`,
        dish_name: lang === 'hi' ? 'दलिया और मेथी का नाश्ता' : lang === 'mr' ? 'दलिया आणि मेथीची खिचडी' : 'Broken Wheat Daliya with Vegetables',
        portion_guidance: '1 medium bowl (250g)',
        why_recommended: 'Slow-release complex carbohydrates that prevent post-meal sugar spikes.',
        allergens: ['gluten'],
        preparation_notes: 'Cook with minimal cold-pressed oil, mustard seeds, and curry leaves.',
        alternatives: [
          {
            meal_id: `bf_alt_${i + 1}`,
            dish_name: lang === 'hi' ? 'जौ का उपमा' : lang === 'mr' ? 'जव उपमा' : 'Vegetable Barley Upma',
            portion_guidance: '1 medium bowl',
            why_recommended: 'Barley beta-glucan assists in optimal glucose stabilization.'
          }
        ]
      },
      lunch: {
        meal_id: `lu_${i + 1}`,
        dish_name: lang === 'hi' ? 'पीली मूंग दाल, मेथी रोटी और सलाद' : lang === 'mr' ? 'मुगाचे वरण, मेथी चपाती आणि कोशिंबीर' : 'Yellow Moong Dal with Whole Wheat Roti & Salad',
        portion_guidance: '1 bowl dal, 2 medium rotis, 1 cup kachumber salad',
        why_recommended: 'Easily digestible protein and fiber for steady glycemic control.',
        allergens: ['gluten'],
        preparation_notes: 'Add cumin and turmeric for digestive ease.',
        alternatives: [
          {
            meal_id: `lu_alt_${i + 1}`,
            dish_name: lang === 'hi' ? 'राजमा और भूरे चावल' : lang === 'mr' ? 'राजमा आणि ब्राऊन राइस' : 'Light Kidney Beans (Rajma) with Brown Rice',
            portion_guidance: '1 cup rajma with 1 cup cooked brown rice',
            why_recommended: 'Rich in soluble fiber and sustained energy.'
          }
        ]
      },
      dinner: {
        meal_id: `di_${i + 1}`,
        dish_name: lang === 'hi' ? 'लौकी की सब्जी और बाजरा रोटी' : lang === 'mr' ? 'दुधी भोपळ्याची भाजी आणि बाजरीची भाकरी' : 'Bottle Gourd (Lauki) Curry with Bajra Roti',
        portion_guidance: '1 bowl subzi, 1-2 bajra rotis',
        why_recommended: 'Light evening meal that supports natural overnight metabolic balance.',
        allergens: [],
        preparation_notes: 'Lightly seasoned with ginger and coriander.',
        alternatives: [
          {
            meal_id: `di_alt_${i + 1}`,
            dish_name: lang === 'hi' ? 'पालक पनीर और मल्टीग्रेन रोटी' : lang === 'mr' ? 'पालक पनीर आणि चपाती' : 'Palak Paneer with Multigrain Roti',
            portion_guidance: '1 bowl curry, 2 small rotis',
            why_recommended: 'High protein and calcium supporting muscle recovery.'
          }
        ]
      },
      snack: {
        meal_id: `sn_${i + 1}`,
        dish_name: lang === 'hi' ? 'भुने हुए चने और ग्रीन टी' : lang === 'mr' ? 'भाजलेले चणे आणि ग्रीन टी' : 'Roasted Chana with Green Tea',
        portion_guidance: 'Handful (30-40g)',
        why_recommended: 'Satisfies crunch with non-starchy complex protein.',
        allergens: [],
        preparation_notes: 'Dry roasted without hydrogenated fats.',
        alternatives: [
          {
            meal_id: `sn_alt_${i + 1}`,
            dish_name: lang === 'hi' ? 'अंकुरित मूंग चाट' : lang === 'mr' ? 'मोड आलेले मूग चाट' : 'Sprouted Moong Salad with Lemon',
            portion_guidance: '1 small cup',
            why_recommended: 'Live enzymes and crisp fiber.'
          }
        ]
      }
    }))
  });

  // View mode: 'plan' | 'questionnaire'
  const [viewMode, setViewMode] = useState('plan');
  const [activeDay, setActiveDay] = useState(1);
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(() => buildInitialPlan(reportId, language));

  // Questionnaire state
  const [questions, setQuestions] = useState([]);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [answers, setAnswers] = useState({});

  // Swap modal/drawer state
  const [swappingMeal, setSwappingMeal] = useState(null); // { day_number, meal_type, current_meal_name, alternatives }
  const [swapLoading, setSwapLoading] = useState(false);

  // Load existing plan or questions when opened
  useEffect(() => {
    if (!isOpen) return;

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
        } else {
          // If no plan yet, open questionnaire
          loadQuestions();
        }
      } catch (err) {
        console.warn('Fallback loading plan:', err);
        // Fallback local synthetic 7-day plan if offline
        createFallbackPlan();
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchPlan();

    return () => {
      isMounted = false;
    };
  }, [isOpen, reportId, language]);

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
        createFallbackPlan();
      }
    } catch {
      createFallbackPlan();
    } finally {
      setLoading(false);
    }
  };

  const createFallbackPlan = () => {
    const fallback = {
      plan_id: `plan_fallback_${reportId}`,
      report_id: reportId,
      dietary_pattern: 'vegetarian',
      dietitian_referral_recommended: false,
      clinical_rationale: [
        language === 'hi'
          ? 'रक्त शर्करा को संतुलित रखने के लिए घुलनशील फाइबर और प्रोटीन का समन्वय।'
          : language === 'mr'
          ? 'रक्तातील साखर नियंत्रित ठेवण्यासाठी विद्राव्य फायबर व प्रथिनांचा समतोल.'
          : 'High-fiber complex carbohydrates paired with protein to maintain steady glucose response.'
      ],
      safety_guidance: [
        language === 'hi'
          ? 'दिनभर पर्याप्त पानी पिएं और अचानक अत्यधिक बदलाव से बचें।'
          : language === 'mr'
          ? 'दिवसभर पुरेसे पाणी प्या आणि आहारात अचानक टोकाचे बदल टाळा.'
          : 'Stay adequately hydrated with 2.5L clean water daily.'
      ],
      days: Array.from({ length: 7 }, (_, i) => ({
        day_number: i + 1,
        breakfast: {
          meal_id: `bf_${i + 1}`,
          dish_name: language === 'hi' ? 'दलिया और मेथी का नाश्ता' : language === 'mr' ? 'दलिया आणि मेथीची खिचडी' : 'Broken Wheat Daliya with Vegetables',
          portion_guidance: '1 medium bowl (250g)',
          why_recommended: 'Slow-release complex carbohydrates that prevent post-meal sugar spikes.',
          allergens: ['gluten'],
          preparation_notes: 'Cook with minimal cold-pressed oil, mustard seeds, and curry leaves.',
          alternatives: [
            {
              meal_id: `bf_alt_${i + 1}`,
              dish_name: language === 'hi' ? 'जौ का उपमा' : language === 'mr' ? 'जव उपमा' : 'Vegetable Barley Upma',
              portion_guidance: '1 medium bowl',
              why_recommended: 'Barley beta-glucan assists in optimal glucose stabilization.'
            }
          ]
        },
        lunch: {
          meal_id: `lu_${i + 1}`,
          dish_name: language === 'hi' ? 'पीली मूंग दाल, मेथी रोटी और सलाद' : language === 'mr' ? 'मुगाचे वरण, मेथी चपाती आणि कोशिंबीर' : 'Yellow Moong Dal with Whole Wheat Roti & Salad',
          portion_guidance: '1 bowl dal, 2 medium rotis, 1 cup kachumber salad',
          why_recommended: 'Easily digestible protein and fiber for steady glycemic control.',
          allergens: ['gluten'],
          preparation_notes: 'Add cumin and turmeric for digestive ease.',
          alternatives: [
            {
              meal_id: `lu_alt_${i + 1}`,
              dish_name: language === 'hi' ? 'राजमा और भूरे चावल (ब्राउन राइस)' : language === 'mr' ? 'राजमा आणि ब्राऊन राइस' : 'Light Kidney Beans (Rajma) with Brown Rice',
              portion_guidance: '1 cup rajma with 1 cup cooked brown rice',
              why_recommended: 'Rich in soluble fiber and sustained energy.'
            }
          ]
        },
        dinner: {
          meal_id: `di_${i + 1}`,
          dish_name: language === 'hi' ? 'लौकी की सब्जी और बाजरा रोटी' : language === 'mr' ? 'दुधी भोपळ्याची भाजी आणि बाजरीची भाकरी' : 'Bottle Gourd (Lauki) Curry with Bajra Roti',
          portion_guidance: '1 bowl subzi, 1-2 bajra rotis',
          why_recommended: 'Light evening meal that supports natural overnight metabolic balance.',
          allergens: [],
          preparation_notes: 'Lightly seasoned with ginger and coriander.',
          alternatives: [
            {
              meal_id: `di_alt_${i + 1}`,
              dish_name: language === 'hi' ? 'पालक पनीर और मल्टीग्रेन रोटी' : language === 'mr' ? 'पालक पनीर आणि चपाती' : 'Palak Paneer with Multigrain Roti',
              portion_guidance: '1 bowl curry, 2 small rotis',
              why_recommended: 'High protein and calcium supporting muscle recovery.'
            }
          ]
        },
        snack: {
          meal_id: `sn_${i + 1}`,
          dish_name: language === 'hi' ? 'भुने हुए चने और ग्रीन टी' : language === 'mr' ? 'भाजलेले चणे आणि ग्रीन टी' : 'Roasted Chana with Green Tea',
          portion_guidance: 'Handful (30-40g)',
          why_recommended: 'Satisfies crunch with non-starchy complex protein.',
          allergens: [],
          preparation_notes: 'Dry roasted without hydrogenated fats.',
          alternatives: [
            {
              meal_id: `sn_alt_${i + 1}`,
              dish_name: language === 'hi' ? 'अंकुरित मूंग चाट' : language === 'mr' ? 'मोड आलेले मूग चाट' : 'Sprouted Moong Salad with Lemon',
              portion_guidance: '1 small cup',
              why_recommended: 'Live enzymes and crisp fiber.'
            }
          ]
        }
      }))
    };
    setPlan(fallback);
    setViewMode('plan');
  };

  const handleOptionSelect = (qId, optionId) => {
    setAnswers((prev) => ({
      ...prev,
      [qId]: optionId,
    }));
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
      const payload = {
        report_id: reportId,
        dietary_pattern: answers.q_diet_pattern || 'vegetarian',
        allergies: answers.q_food_allergies && answers.q_food_allergies !== 'allergy_none'
          ? [answers.q_food_allergies.replace('allergy_', '')]
          : [],
        meal_routine: answers.q_meal_routine || 'routine_3meals',
        budget_and_cooking: answers.q_budget_cooking || 'budget_mod_home',
        primary_goal: answers.q_primary_goal || 'goal_balance',
      };

      const res = await fetch(`/api/v1/reports/${reportId}/nutrition/generate?lang=${language}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const newPlan = await res.json();
        setPlan(newPlan);
        setViewMode('plan');
        setActiveDay(1);
      } else {
        createFallbackPlan();
      }
    } catch {
      createFallbackPlan();
    } finally {
      setLoading(false);
    }
  };

  const handleSwapClick = (dayNumber, mealType, mealData) => {
    setSwappingMeal({
      day_number: dayNumber,
      meal_type: mealType,
      current_dish_name: mealData.dish_name,
      alternatives: mealData.alternatives || [],
    });
  };

  const executeMealSwap = async (newMealId) => {
    if (!swappingMeal || !plan) return;
    setSwapLoading(true);
    try {
      const res = await fetch(`/api/v1/reports/nutrition/swap?lang=${language}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan_id: plan.plan_id,
          day_number: swappingMeal.day_number,
          meal_type: swappingMeal.meal_type,
          new_meal_id: newMealId,
        }),
      });

      if (res.ok) {
        const updated = await res.json();
        setPlan(updated);
        setSwappingMeal(null);
      } else {
        // Local simulation fallback
        const updatedPlan = JSON.parse(JSON.stringify(plan));
        const dayIdx = swappingMeal.day_number - 1;
        const currentMeal = updatedPlan.days[dayIdx][swappingMeal.meal_type];
        const selectedAlt = currentMeal.alternatives.find((a) => a.meal_id === newMealId);
        if (selectedAlt) {
          const oldName = currentMeal.dish_name;
          const oldId = currentMeal.meal_id;
          currentMeal.dish_name = selectedAlt.dish_name;
          currentMeal.portion_guidance = selectedAlt.portion_guidance;
          currentMeal.why_recommended = selectedAlt.why_recommended;
          currentMeal.meal_id = selectedAlt.meal_id;
          currentMeal.alternatives = [
            {
              meal_id: oldId,
              dish_name: oldName,
              portion_guidance: selectedAlt.portion_guidance,
              why_recommended: 'Previously assigned balanced option.',
            },
          ];
        }
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

  if (!isOpen) return null;

  const currentDayData = plan?.days?.find((d) => d.day_number === activeDay) || plan?.days?.[0];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-clarity-charcoal/50 backdrop-blur-sm animate-in fade-in">
      <div className="bg-clarity-surface rounded-3xl border border-clarity-border shadow-elevated max-w-4xl w-full p-5 sm:p-8 max-h-[92vh] overflow-y-auto flex flex-col justify-between">
        {/* Header */}
        <div>
          <div className="flex justify-between items-start mb-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl">🥗</span>
                <h2 className="text-xl sm:text-2xl font-bold text-clarity-teal">
                  {t.nutritionTitle}
                </h2>
              </div>
              <p className="text-xs sm:text-sm text-clarity-muted mt-1">
                {t.nutritionSubtitle}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-clarity-muted hover:text-clarity-charcoal p-2 rounded-full hover:bg-clarity-ivory"
              aria-label="Close nutrition"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* QUESTIONNAIRE MODE */}
          {viewMode === 'questionnaire' && (
            <div className="py-4 animate-in fade-in">
              {loading ? (
                <div className="py-16 text-center text-clarity-teal">
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
                      onClick={() => generatePlanFromAnswers()}
                      className="text-clarity-coral hover:underline font-semibold"
                    >
                      {t.skipAllQuestions}
                    </button>
                  </div>

                  {/* Active Question Box */}
                  <div className="p-5 sm:p-6 rounded-2xl bg-clarity-ivory/80 border border-clarity-border">
                    <h3 className="text-base sm:text-lg font-bold text-clarity-charcoal mb-2">
                      {questions[currentQIndex]?.question_text}
                    </h3>
                    <p className="text-xs text-clarity-muted mb-5">
                      {questions[currentQIndex]?.context_reason}
                    </p>

                    <div className="space-y-3">
                      {questions[currentQIndex]?.options?.map((opt) => {
                        const isSelected = answers[questions[currentQIndex].question_id] === opt.option_id;
                        return (
                          <button
                            key={opt.option_id}
                            type="button"
                            onClick={() => handleOptionSelect(questions[currentQIndex].question_id, opt.option_id)}
                            className={`w-full text-left p-4 rounded-xl border transition-all text-sm flex items-center justify-between ${
                              isSelected
                                ? 'bg-clarity-mint/20 border-clarity-teal text-clarity-teal font-semibold shadow-xs'
                                : 'bg-clarity-surface border-clarity-border text-clarity-charcoal hover:border-clarity-mint'
                            }`}
                          >
                            <span>{opt.option_label}</span>
                            <div className={`w-4 h-4 rounded-full border flex items-center justify-center shrink-0 ml-3 ${
                              isSelected ? 'border-clarity-teal bg-clarity-teal' : 'border-clarity-border'
                            }`}>
                              {isSelected && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
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
          )}

          {/* PLAN VIEW MODE */}
          {viewMode === 'plan' && plan && (
            <div className="space-y-6 animate-in fade-in">
              {/* Dietitian Referral / Safety Notice Banner */}
              {plan.dietitian_referral_recommended && (
                <div className="p-4 rounded-2xl bg-amber-50 border border-amber-300 text-amber-950 flex items-start gap-3 shadow-soft">
                  <span className="text-xl shrink-0 mt-0.5">⚠️</span>
                  <div>
                    <h4 className="font-bold text-sm text-amber-950">
                      {t.dietitianNoticeTitle}
                    </h4>
                    <p className="text-xs text-amber-900 mt-1 leading-relaxed">
                      {t.dietitianNoticeBody}
                    </p>
                  </div>
                </div>
              )}

              {/* Clinical rationale points */}
              {plan.clinical_rationale?.length > 0 && (
                <div className="p-4 rounded-2xl bg-clarity-mint/15 border border-clarity-mint/40">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-clarity-teal mb-2">
                    {t.whyRecommended}
                  </h4>
                  <ul className="text-xs space-y-1.5 text-clarity-charcoal">
                    {plan.clinical_rationale.map((r, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-clarity-teal font-bold">&bull;</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Day Tabs (Day 1 - Day 7) */}
              <div className="flex gap-1.5 overflow-x-auto pb-2 border-b border-clarity-border/80 scrollbar-none">
                {plan.days?.map((d) => (
                  <button
                    key={d.day_number}
                    onClick={() => setActiveDay(d.day_number)}
                    className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold whitespace-nowrap transition-all ${
                      activeDay === d.day_number
                        ? 'bg-clarity-teal text-white shadow-soft'
                        : 'bg-clarity-ivory text-clarity-muted hover:text-clarity-charcoal hover:bg-clarity-mint/20'
                    }`}
                  >
                    {t.dayTab} {d.day_number}
                  </button>
                ))}
              </div>

              {/* Active Day Meals Grid */}
              {currentDayData && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { key: 'breakfast', label: t.breakfast, icon: '🌅', meal: currentDayData.breakfast },
                    { key: 'lunch', label: t.lunch, icon: '☀️', meal: currentDayData.lunch },
                    { key: 'snack', label: t.snack, icon: '🍵', meal: currentDayData.snack },
                    { key: 'dinner', label: t.dinner, icon: '🌙', meal: currentDayData.dinner },
                  ].map(({ key, label, icon, meal }) => {
                    if (!meal) return null;
                    return (
                      <div
                        key={key}
                        className="p-4 rounded-2xl bg-clarity-surface border border-clarity-border shadow-soft flex flex-col justify-between"
                      >
                        <div>
                          <div className="flex justify-between items-start mb-2">
                            <span className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-clarity-muted">
                              <span>{icon}</span> {label}
                            </span>
                            {meal.alternatives?.length > 0 && (
                              <button
                                onClick={() => handleSwapClick(currentDayData.day_number, key, meal)}
                                className="text-[11px] font-semibold text-clarity-coral hover:underline flex items-center gap-1"
                              >
                                <span>⇄</span> {t.swapMeal}
                              </button>
                            )}
                          </div>
                          <h4 className="font-bold text-sm sm:text-base text-clarity-charcoal mb-1">
                            {meal.dish_name || meal.name}
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

              {/* Actions Footer */}
              <div className="pt-4 border-t border-clarity-border flex flex-wrap items-center justify-between gap-3">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => loadQuestions()}
                >
                  ⚙️ {t.recalculatePlanBtn}
                </Button>
                <div className="flex items-center gap-3">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={handleDownloadPdf}
                  >
                    📥 {t.downloadNutritionPdf}
                  </Button>
                </div>
              </div>

              {/* General Disclaimer */}
              <p className="text-[11px] text-clarity-muted leading-relaxed italic bg-clarity-ivory/50 p-3 rounded-xl border border-clarity-border/40">
                {t.generalDietDisclaimer}
              </p>
            </div>
          )}
        </div>

        {/* SWAP MEAL DIALOG OVERLAY */}
        {swappingMeal && (
          <div className="fixed inset-0 z-60 flex items-center justify-center p-4 bg-clarity-charcoal/60 backdrop-blur-xs animate-in fade-in">
            <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-5 max-w-md w-full shadow-elevated">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-bold text-base text-clarity-teal">
                  {t.availableAlternatives}
                </h4>
                <button
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
                {swappingMeal.alternatives?.map((alt) => (
                  <div
                    key={alt.meal_id}
                    className="p-3.5 rounded-xl border border-clarity-border bg-clarity-ivory hover:border-clarity-teal transition-all flex flex-col justify-between gap-2"
                  >
                    <div>
                      <h5 className="font-bold text-sm text-clarity-charcoal">
                        {alt.dish_name || alt.name}
                      </h5>
                      <p className="text-xs text-clarity-muted mt-0.5">
                        {alt.portion_guidance}
                      </p>
                      <p className="text-[11px] text-clarity-charcoal mt-1">
                        {alt.why_recommended || alt.why_it_fits}
                      </p>
                    </div>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => executeMealSwap(alt.meal_id)}
                      disabled={swapLoading}
                    >
                      {swapLoading ? 'Updating...' : t.selectAlternative}
                    </Button>
                  </div>
                ))}
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
      </div>
    </div>
  );
}
