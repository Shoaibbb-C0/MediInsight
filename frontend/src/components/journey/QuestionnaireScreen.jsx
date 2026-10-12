import React, { useState } from 'react';
import { Button } from '../common/WarmUI';
import { TRANSLATIONS } from '../../fixtures/translations';

export function QuestionnaireScreen({
  questions = [],
  onSubmitAnswers,
  onBack,
  onSkipAll,
  language = 'en'
}) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [immediateWarning, setImmediateWarning] = useState(null);

  if (!questions || questions.length === 0) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center">
        <h2 className="text-xl font-bold text-clarity-teal mb-2">
          {language === 'hi' ? 'अतिरिक्त संदर्भ प्रश्नों की आवश्यकता नहीं है' : language === 'mr' ? 'अतिरिक्त प्रश्नांची आवश्यकता नाही' : 'No context questions needed'}
        </h2>
        <p className="text-sm text-clarity-muted mb-6">
          {language === 'hi' ? 'सभी परिणाम सामान्य सीमा में हैं या आवश्यक जानकारी उपलब्ध है।' : language === 'mr' ? 'सर्व निकाल सामान्य मर्यादेत आहेत किंवा आवश्यक माहिती उपलब्ध आहे.' : 'All results are within standard range or baseline history is complete.'}
        </p>
        <Button variant="primary" onClick={() => onSubmitAnswers([])}>
          {t.finishQuestions} &rarr;
        </Button>
      </div>
    );
  }

  const currentQ = questions[currentStep] || questions[0];
  const selectedOptionId = answers[currentQ?.id];

  const handleSelectOption = (optionId) => {
    setAnswers((prev) => ({
      ...prev,
      [currentQ.id]: optionId,
    }));

    // Immediate safety check: if serious warning option selected
    if (currentQ.urgent_warning_symptom && optionId.includes('concerning')) {
      setImmediateWarning(t.urgentAlertGuidance);
    } else {
      setImmediateWarning(null);
    }
  };

  const handleNext = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      finishQuestionnaire();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkipCurrent = () => {
    // Advance without recording an answer for this question
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      finishQuestionnaire();
    }
  };

  const finishQuestionnaire = () => {
    const payload = Object.entries(answers).map(([qId, optId]) => ({
      question_id: qId,
      selected_option_id: optId,
    }));
    onSubmitAnswers(payload);
  };

  return (
    <div className="max-w-xl mx-auto px-4 py-8">
      {/* Header with step progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-clarity-muted mb-1">
          <span>{t.stepQuestionnaire}</span>
          <span>
            {language === 'hi' ? `प्रश्न ${currentStep + 1} / ${questions.length}` : language === 'mr' ? `प्रश्न ${currentStep + 1} / ${questions.length}` : `Question ${currentStep + 1} of ${questions.length}`}
          </span>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-clarity-border/60 h-2 rounded-full overflow-hidden mb-4">
          <div
            className="bg-clarity-teal h-full transition-all duration-300"
            style={{ width: `${((currentStep + 1) / questions.length) * 100}%` }}
          />
        </div>

        <h1 className="text-xl sm:text-2xl font-bold text-clarity-teal leading-snug">
          {currentQ.text}
        </h1>
        {currentQ.context_reason && (
          <p className="text-xs sm:text-sm text-clarity-muted mt-2 leading-relaxed">
            {currentQ.context_reason}
          </p>
        )}
      </div>

      {/* Immediate Red-Flag Warning Alert Banner */}
      {immediateWarning && (
        <div className="mb-6 p-4 rounded-2xl bg-red-50 border border-red-300 text-xs sm:text-sm text-[#9E3624] flex items-start gap-3 shadow-soft animate-in fade-in">
          <svg className="w-5 h-5 shrink-0 mt-0.5 text-clarity-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <div className="font-bold mb-1">{t.urgentAlertTitle}</div>
            <p className="leading-relaxed">{immediateWarning}</p>
          </div>
        </div>
      )}

      {/* Options List */}
      <div className="space-y-3 mb-8">
        {currentQ.options?.map((opt) => {
          const isSelected = selectedOptionId === opt.id;
          return (
            <div
              key={opt.id}
              onClick={() => handleSelectOption(opt.id)}
              className={`p-4 rounded-2xl border text-sm sm:text-base font-medium cursor-pointer transition-all flex items-center justify-between ${
                isSelected
                  ? 'bg-clarity-mint/30 border-clarity-teal text-clarity-teal shadow-soft'
                  : 'bg-clarity-surface border-clarity-border hover:border-clarity-teal/40 text-clarity-charcoal'
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-5 h-5 rounded-full border flex items-center justify-center shrink-0 ${
                    isSelected
                      ? 'border-clarity-teal bg-clarity-teal text-white'
                      : 'border-clarity-muted/50 bg-white'
                  }`}
                >
                  {isSelected && (
                    <div className="w-2 h-2 rounded-full bg-white" />
                  )}
                </div>
                <span>{opt.text}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Action Footer */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-clarity-border">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          {currentStep > 0 && (
            <Button size="sm" variant="secondary" onClick={handlePrevious}>
              &larr; {language === 'hi' ? 'पिछला' : language === 'mr' ? 'मागे' : 'Previous'}
            </Button>
          )}
          <button
            type="button"
            onClick={handleSkipCurrent}
            className="text-xs text-clarity-muted hover:text-clarity-charcoal font-medium underline px-2 py-1"
          >
            {t.skipThisQuestion}
          </button>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
          <button
            type="button"
            onClick={onSkipAll}
            className="text-xs text-clarity-muted hover:text-clarity-charcoal font-medium underline"
          >
            {t.skipAllQuestions}
          </button>
          <Button
            size="md"
            variant="primary"
            onClick={handleNext}
            className="w-full sm:w-auto"
          >
            {currentStep < questions.length - 1 ? t.nextQuestion : t.finishQuestions} &rarr;
          </Button>
        </div>
      </div>
    </div>
  );
}
