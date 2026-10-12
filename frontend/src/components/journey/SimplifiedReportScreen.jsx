import React from 'react';
import { Button, StatusBadge } from '../common/WarmUI';

export function SimplifiedReportScreen({ report, onRestart }) {
  if (!report) return null;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Synthetic fixture badge */}
      {report.is_synthetic_fixture && (
        <div className="mb-4 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-100/70 border border-amber-300 text-[#855B18] text-xs font-semibold">
          <span>Phase 1 Synthetic Fixture (Development Test Data)</span>
        </div>
      )}

      {/* Screen Title */}
      <div className="mb-6">
        <span className="text-xs font-bold uppercase tracking-wider text-clarity-muted">
          Step 3 of 3: Simplified Summary
        </span>
        <h1 className="text-2xl sm:text-4xl font-bold text-clarity-teal mt-1">
          Here's what we found
        </h1>
        <p className="text-sm text-clarity-muted mt-1">
          A calm breakdown of your laboratory findings, explained in plain language.
        </p>
      </div>

      {/* Patient Summary Card */}
      <div className="bg-clarity-surface rounded-3xl border border-clarity-border p-6 sm:p-8 shadow-soft mb-8">
        <h2 className="text-base font-bold text-clarity-teal uppercase tracking-wider mb-3">
          Overall Summary
        </h2>
        <p className="text-base sm:text-lg text-clarity-charcoal leading-relaxed">
          {report.patient_summary}
        </p>
      </div>

      {/* Key Findings List */}
      <div className="space-y-4 mb-8">
        <h2 className="text-lg font-bold text-clarity-teal">
          Detailed Findings
        </h2>

        {report.key_findings.map((item, idx) => (
          <div
            key={idx}
            className="bg-clarity-surface rounded-2xl border border-clarity-border p-5 sm:p-6 shadow-soft transition-all"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
              <h3 className="text-base sm:text-lg font-bold text-clarity-charcoal">
                {item.biomarker_name}
              </h3>
              <div>
                <StatusBadge status={item.status} />
              </div>
            </div>

            <p className="text-sm font-medium text-clarity-teal mb-2">
              {item.plain_english_summary}
            </p>

            <p className="text-sm text-clarity-muted leading-relaxed mb-3">
              <strong className="text-clarity-charcoal font-semibold">What this means: </strong>
              {item.what_this_means}
            </p>

            <div className="p-3 bg-clarity-mint/20 rounded-xl text-xs sm:text-sm text-clarity-teal border border-clarity-mint/40 flex items-start gap-2">
              <svg className="w-4 h-4 mt-0.5 shrink-0 text-clarity-teal" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{item.reassurance}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Everyday Healthy Habits (Nutrition Preview) */}
      {report.lifestyle_tips && report.lifestyle_tips.length > 0 && (
        <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-6 shadow-soft mb-8">
          <h2 className="text-base font-bold text-clarity-teal mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Gentle everyday habits to consider
          </h2>
          <ul className="space-y-2 text-sm text-clarity-charcoal">
            {report.lifestyle_tips.map((tip, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-clarity-teal font-bold">&bull;</span>
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Suggested Questions for Your Doctor */}
      {report.suggested_doctor_questions && (
        <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-6 shadow-soft mb-8">
          <h2 className="text-base font-bold text-clarity-teal mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-clarity-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            Helpful questions to ask your physician
          </h2>
          <div className="space-y-2.5">
            {report.suggested_doctor_questions.map((q, idx) => (
              <div key={idx} className="p-3 bg-clarity-ivory/60 rounded-xl border border-clarity-border/60 text-sm text-clarity-charcoal flex items-start gap-2">
                <span className="font-bold text-clarity-teal">{idx + 1}.</span>
                <span>"{q}"</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Medical Disclaimer */}
      <div className="p-4 bg-clarity-ivory rounded-2xl border border-clarity-border text-xs text-clarity-muted leading-relaxed mb-8">
        <strong>Important Medical Notice: </strong>
        {report.disclaimer}
      </div>

      {/* Bottom Action */}
      <div className="flex justify-center">
        <Button variant="secondary" onClick={onRestart}>
          Understand another report
        </Button>
      </div>
    </div>
  );
}
