import React, { useState, useEffect } from 'react';
import { useDialogFocus } from '../common/useDialogFocus';
import { Button } from '../common/WarmUI';
import { TRANSLATIONS } from '../../fixtures/translations';

export function InlineNutritionSection({
  reportId = 'rep_demo_fixture',
  language = 'en',
  isExpanded = false,
  onToggleExpand = () => {}
}) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

  // State
  const [viewMode, setViewMode] = useState('plan'); // 'plan' | 'questionnaire'
  const [activeDay, setActiveDay] = useState(1);
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [swappingMeal, setSwappingMeal] = useState(null);
  const [swapLoading, setSwapLoading] = useState(false);
  const [serviceError, setServiceError] = useState(false);
  const dialogRef = useDialogFocus(Boolean(swappingMeal), () => setSwappingMeal(null));

  // Sync plan on language or report change
  useEffect(() => {
    let isMounted = true;
    const fetchPlan = async () => {
      setLoading(true);
      setServiceError(false);
      setPlan(null);
      try {
        const res = await fetch(`/api/v1/reports/${reportId}/nutrition/plan?lang=${language}`);
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            setPlan(data);
            setViewMode('plan');
          }
        } else if (res.status !== 404) { if (isMounted) setServiceError(true); }
      } catch (err) {
        if (isMounted) setServiceError(true);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    if (reportId && isExpanded) {
      fetchPlan();
    }

    return () => {
      isMounted = false;
    };
  }, [reportId, language, isExpanded]);

  const loadQuestions = async () => {
    setLoading(true);
    setServiceError(false);
    try {
      const res = await fetch(`/api/v1/reports/${reportId}/nutrition/questions?lang=${language}`);
      if (res.ok) {
        const data = await res.json();
        setQuestions(data.questions || []);
        setViewMode('questionnaire');
        setCurrentQIndex(0);
      } else { setServiceError(true); }
    } catch { setServiceError(true);
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
    const unansweredSafetyQuestion = questions.findIndex(question => ['nq_allergies', 'nq_dietary_pref'].includes(question.id) && !answers[question.id]);
    if (unansweredSafetyQuestion >= 0) { setCurrentQIndex(unansweredSafetyQuestion); return; }
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
        budget: answers.nq_budget || answers.q_budget_cooking || 'moderate',
        cooking_availability: answers.nq_cooking || 'home_cooked',
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
      } else { setServiceError(true); }
    } catch (err) {
      setServiceError(true);
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
      } else { setServiceError(true); }
    } catch { setServiceError(true);
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
              {language === 'hi' ? 'आपका 7-दिन का आहार' : language === 'mr' ? 'तुमचा 7-दिवसांचा आहार' : 'Your 7-day food plan'}
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

      {serviceError && <p role="alert" className="bg-red-50 text-red-900 rounded-xl p-4 mb-5">{language === 'hi' ? 'आहार सेवा उपलब्ध नहीं। बदलाव सहेजे नहीं गए। फिर कोशिश करें।' : language === 'mr' ? 'आहार सेवा उपलब्ध नाही. बदल जतन झाले नाहीत. पुन्हा प्रयत्न करा.' : 'Nutrition service unavailable. Changes were not saved. Please try again.'}</p>}
      {isExpanded && !plan && viewMode !== 'questionnaire' && <div className="py-6"><h3 className="font-bold text-2xl mb-3">{language === 'hi' ? 'आपका 7-दिन का आहार' : language === 'mr' ? 'तुमचा 7-दिवसांचा आहार' : 'Your 7-day food plan'}</h3><p className="text-clarity-muted mb-5">{language === 'hi' ? 'योजना बनाने से पहले एलर्जी और आहार की पसंद बताएँ।' : language === 'mr' ? 'योजना तयार करण्यापूर्वी ॲलर्जी आणि आहाराची आवड सांगा.' : 'Tell us your allergies and food preferences before generating your weekly plan.'}</p><Button onClick={loadQuestions} disabled={loading}>{t.recalculatePlanBtn}</Button></div>}
      {/* EXPANDED CONTENT FLOW */}
      {isExpanded && (plan || viewMode === 'questionnaire') && (
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
                            aria-pressed={isSelected}
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
              <div className="grid grid-cols-4 sm:grid-cols-7 gap-2 pb-3 border-b border-clarity-border/80">
                {plan.days?.map((d) => (
                  <button
                    key={d.day_number}
                    type="button"
                    onClick={() => setActiveDay(d.day_number)}
                    aria-pressed={activeDay === d.day_number}
                    className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold whitespace-nowrap transition-all ${
                      activeDay === d.day_number
                        ? 'bg-clarity-teal text-white shadow-soft'
                        : 'bg-clarity-ivory text-clarity-muted hover:text-clarity-charcoal hover:bg-clarity-mint/20'
                    }`}
                  >
                    {(language === 'hi' ? ['सोम', 'मंगल', 'बुध', 'गुरु', 'शुक्र', 'शनि', 'रवि'] : language === 'mr' ? ['सोम', 'मंगळ', 'बुध', 'गुरु', 'शुक्र', 'शनि', 'रवि'] : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])[d.day_number - 1]}
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
        <div ref={dialogRef} role="dialog" aria-modal="true" aria-label={t.availableAlternatives} className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-clarity-charcoal/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-5 max-w-md w-full shadow-elevated">
            <div className="flex justify-between items-center mb-3">
              <h4 className="font-bold text-base text-clarity-teal">
                {t.availableAlternatives}
              </h4>
              <button
                type="button"
                onClick={() => setSwappingMeal(null)}
                className="text-clarity-muted hover:text-clarity-charcoal text-sm p-1"
                aria-label={language === 'hi' ? 'बंद करें' : language === 'mr' ? 'बंद करा' : 'Close'}
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
