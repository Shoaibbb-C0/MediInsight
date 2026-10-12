import React, { useState } from 'react';
import { Button } from '../common/WarmUI';

export function QuestionnaireScreen({
  questions = [],
  onSubmitAnswers,
  onBack,
  onSkipAll
}) {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [immediateWarning, setImmediateWarning] = useState(null);

  if (!questions || questions.length === 0) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center">
        <h2 className="text-xl font-bold text-clarity-teal mb-2">No context questions needed</h2>
        <p className="text-sm text-clarity-muted mb-6">All results are within standard range or baseline history is complete.</p>
        <Button variant="primary" onClick={() => onSubmitAnswers([])}>
          See my report summary &rarr;
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
      setImmediateWarning(
        "Notice: You reported noticeable visible bleeding or dark stools. If this is active or severe, please contact a physician or local urgent healthcare provider right away rather than waiting."
      );
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
          <span>A few questions about you</span>
          <span>Question {currentStep + 1} of {questions.length}</span>
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

      {/* Immediate Safety Alert Banner */}
      {immediateWarning && (
        <div className="mb-6 p-4 bg-red-50 border-2 border-red-300 rounded-2xl text-xs sm:text-sm text-[#9E3624] flex items-start gap-2.5 animate-in fade-in">
          <svg className="w-5 h-5 shrink-0 mt-0.5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <strong className="block font-bold">Important Medical Guidance:</strong>
            <span>{immediateWarning}</span>
          </div>
        </div>
      )}

      {/* Options (One question per step) */}
      <div className="space-y-3 mb-8">
        {currentQ.options.map((opt) => {
          const isSelected = selectedOptionId === opt.id;
          return (
            <button
              key={opt.id}
              onClick={() => handleSelectOption(opt.id)}
              className={`w-full text-left p-4 rounded-2xl border text-sm font-semibold transition-all flex items-center justify-between ${
                isSelected
                  ? 'border-clarity-teal bg-clarity-mint/25 text-clarity-teal shadow-xs ring-2 ring-clarity-teal/20'
                  : 'border-clarity-border hover:border-clarity-teal/50 bg-white text-clarity-charcoal'
              }`}
            >
              <span>{opt.text}</span>
              <div className={`w-5 h-5 rounded-full border flex items-center justify-center shrink-0 ml-3 ${
                isSelected ? 'border-clarity-teal bg-clarity-teal' : 'border-clarity-muted/50'
              }`}>
                {isSelected && (
                  <div className="w-2 h-2 rounded-full bg-white" />
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Navigation Controls */}
      <div className="pt-4 border-t border-clarity-border flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          {currentStep > 0 ? (
            <Button size="sm" variant="ghost" onClick={handlePrevious}>
              &larr; Back
            </Button>
          ) : (
            <Button size="sm" variant="ghost" onClick={onBack}>
              &larr; Verification
            </Button>
          )}

          <button
            type="button"
            onClick={handleSkipCurrent}
            className="text-xs text-clarity-muted hover:text-clarity-charcoal underline ml-2"
          >
            Skip this question
          </button>
        </div>

        <div className="flex items-center gap-2">
          {onSkipAll && (
            <button
              type="button"
              onClick={onSkipAll}
              className="text-xs text-clarity-muted hover:text-clarity-charcoal mr-2"
            >
              Skip all questions
            </button>
          )}

          <Button
            size="md"
            variant="primary"
            onClick={handleNext}
            className="px-6"
          >
            {currentStep < questions.length - 1 ? 'Next question \u2192' : 'See final report \u2192'}
          </Button>
        </div>
      </div>
    </div>
  );
}
