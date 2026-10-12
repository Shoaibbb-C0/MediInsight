import React, { useState } from 'react';
import { Button } from '../common/WarmUI';

export function QuestionnaireScreen({ questions = [], onSubmitAnswers, onBack }) {
  const [answers, setAnswers] = useState({});
  const [validationError, setValidationError] = useState(null);

  const handleSelectOption = (questionId, optionId) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: optionId,
    }));
    setValidationError(null);
  };

  const handleContinue = () => {
    // Check if at least first required context question is addressed
    if (questions.length > 0 && Object.keys(answers).length === 0) {
      setValidationError('Please select an answer for at least one question to help personalize your health summary.');
      return;
    }

    const payload = Object.entries(answers).map(([qId, optId]) => ({
      question_id: qId,
      selected_option_id: optId,
    }));

    onSubmitAnswers(payload);
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      {/* Step Indicator */}
      <div className="mb-6">
        <span className="text-xs font-bold uppercase tracking-wider text-clarity-muted">
          Step 2 of 3: Personalized context
        </span>
        <h1 className="text-2xl sm:text-3xl font-bold text-clarity-teal mt-1">
          A few questions about you
        </h1>
        <p className="text-sm text-clarity-muted mt-2">
          Your answers help us clarify your numbers and provide an explanation tailored to how you are actually feeling.
        </p>
      </div>

      {validationError && (
        <div className="mb-6 p-3.5 bg-red-50 border border-red-200 rounded-2xl text-xs sm:text-sm text-[#9E3624] flex items-center gap-2">
          <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{validationError}</span>
        </div>
      )}

      {/* Questions Stack */}
      <div className="space-y-6">
        {questions.map((q, qIndex) => {
          const selectedOption = answers[q.id];

          return (
            <div
              key={q.id}
              className="bg-clarity-surface rounded-2xl border border-clarity-border p-5 sm:p-6 shadow-soft"
            >
              <div className="flex items-start gap-3 mb-2">
                <span className="w-6 h-6 rounded-full bg-clarity-mint text-clarity-teal font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                  {qIndex + 1}
                </span>
                <div>
                  <h2 className="font-bold text-base sm:text-lg text-clarity-teal">
                    {q.text}
                  </h2>
                  {q.context_reason && (
                    <p className="text-xs text-clarity-muted mt-1 leading-relaxed">
                      {q.context_reason}
                    </p>
                  )}
                </div>
              </div>

              {/* Options */}
              <div className="mt-4 space-y-2.5 pl-0 sm:pl-9">
                {q.options.map((opt) => {
                  const isChecked = selectedOption === opt.id;
                  return (
                    <button
                      key={opt.id}
                      onClick={() => handleSelectOption(q.id, opt.id)}
                      className={`w-full text-left p-3.5 rounded-xl border text-sm font-medium transition-all flex items-center justify-between ${
                        isChecked
                          ? 'border-clarity-teal bg-clarity-mint/20 text-clarity-teal font-semibold shadow-xs'
                          : 'border-clarity-border/80 hover:border-clarity-teal/40 bg-white text-clarity-charcoal'
                      }`}
                    >
                      <span>{opt.text}</span>
                      <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                        isChecked ? 'border-clarity-teal bg-clarity-teal' : 'border-clarity-muted/50'
                      }`}>
                        {isChecked && (
                          <div className="w-1.5 h-1.5 rounded-full bg-white" />
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Continuation footer */}
      <div className="mt-8 pt-4 border-t border-clarity-border flex flex-col sm:flex-row items-center justify-between gap-4">
        <Button variant="ghost" onClick={onBack}>
          &larr; Back to verification
        </Button>

        <Button
          size="lg"
          variant="primary"
          onClick={handleContinue}
          className="w-full sm:w-auto px-8"
        >
          See my health explanation &rarr;
        </Button>
      </div>
    </div>
  );
}
