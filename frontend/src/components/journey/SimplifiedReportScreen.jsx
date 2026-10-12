import React, { useState } from 'react';
import { Button, StatusBadge } from '../common/WarmUI';
import { InlineNutritionModal } from './InlineNutritionModal';
import { InlineDoctorModal } from './InlineDoctorModal';
import { TRANSLATIONS } from '../../fixtures/translations';

export function SimplifiedReportScreen({ report, onRestart, language = 'en' }) {
  if (!report) return null;

  const t = TRANSLATIONS[language] || TRANSLATIONS.en;
  const [showAllResults, setShowAllResults] = useState(false);
  const [isNutritionOpen, setIsNutritionOpen] = useState(false);
  const [isDoctorOpen, setIsDoctorOpen] = useState(false);

  // Groupings
  const attentionItems = report.prioritized_attention || [];
  const withinRangeItems = report.within_range_results || [];
  const unreliableItems = report.unreliable_flagged_results || [];
  const historicalChanges = report.historical_changes || [];
  const clinicalPatterns = report.clinical_patterns || [];
  const testPurposes = report.test_purposes || [];
  const contextInsights = report.context_insights || [];
  const suggestedQuestions = report.suggested_doctor_questions || [];
  const safeNextSteps = report.safe_next_steps || [];

  const handleDownloadPdf = () => {
    const reportId = report.report_id || 'demo_report';
    window.open(`/api/v1/reports/${reportId}/pdf?lang=${language}`, '_blank');
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Synthetic fixture badge if applicable */}
      {report.is_synthetic_fixture && (
        <div className="mb-4 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-100/70 border border-amber-300 text-[#855B18] text-xs font-semibold">
          <span>{language === 'hi' ? 'नैदानिक परीक्षण मोड (प्रदर्शन डेटा)' : language === 'mr' ? 'वैद्यकीय प्रात्यक्षिक मोड' : 'Clinical Verification Mode (Development Data)'}</span>
        </div>
      )}

      {/* Screen Title */}
      <div className="mb-6">
        <span className="text-xs font-bold uppercase tracking-wider text-clarity-muted">
          {t.stepReport}
        </span>
        <h1 className="text-2xl sm:text-4xl font-bold text-clarity-teal mt-1">
          {t.heresWhatWeFound}
        </h1>
        <p className="text-sm text-clarity-muted mt-1">
          {t.heroSubtitle}
        </p>
      </div>

      {/* Urgent Safety Banner if Present */}
      {report.safety_alert && (
        <div className="mb-8 p-5 rounded-3xl bg-red-50 border border-red-300 text-sm text-[#9E3624] flex items-start gap-3 shadow-soft">
          <svg className="w-6 h-6 shrink-0 mt-0.5 text-clarity-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <div className="font-bold text-base mb-1">{report.safety_alert.title}</div>
            <p className="leading-relaxed">{report.safety_alert.guidance}</p>
          </div>
        </div>
      )}

      {/* Patient Overall Summary Card */}
      <div className="bg-clarity-surface rounded-3xl border border-clarity-border p-6 sm:p-8 shadow-soft mb-8">
        <h2 className="text-xs font-bold uppercase tracking-wider text-clarity-muted mb-2">
          {t.overallSummary}
        </h2>
        <p className="text-base sm:text-lg text-clarity-charcoal leading-relaxed">
          {report.patient_summary}
        </p>
      </div>

      {/* SECTION 1: WHAT NEEDS ATTENTION (Prioritized Abnormal First) */}
      <div className="space-y-4 mb-8">
        <div className="flex items-center justify-between">
          <h2 className="text-lg sm:text-xl font-bold text-clarity-teal flex items-center gap-2">
            <svg className="w-5 h-5 text-clarity-coral shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>{t.whatNeedsAttention} ({attentionItems.length})</span>
          </h2>
          <span className="text-xs text-clarity-muted">
            {language === 'hi' ? 'प्राथमिकता निष्कर्ष' : language === 'mr' ? 'प्राधान्य निकाल' : 'Prioritized findings'}
          </span>
        </div>

        {attentionItems.length === 0 ? (
          <div className="p-4 bg-emerald-50 rounded-2xl border border-emerald-200 text-sm text-[#195643]">
            {t.allNormal}
          </div>
        ) : (
          attentionItems.map((item, idx) => (
            <div
              key={idx}
              className="bg-clarity-surface rounded-2xl border border-clarity-border p-5 sm:p-6 shadow-soft"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <h3 className="text-base sm:text-lg font-bold text-clarity-charcoal">
                  {item.name}
                </h3>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-clarity-teal">{item.value}</span>
                  <StatusBadge status={item.status} label={item.status_label} />
                </div>
              </div>

              <p className="text-sm text-clarity-charcoal leading-relaxed mb-2">
                {item.why_outside_range || item.plain_summary}
              </p>

              <div className="text-xs text-clarity-muted pt-2 border-t border-clarity-border/40 flex flex-wrap justify-between gap-2">
                <span>
                  {language === 'hi' ? 'सामान्य संदर्भ सीमा: ' : language === 'mr' ? 'संदर्भ मर्यादा: ' : 'Reference range: '}
                  <strong>{item.reference_range}</strong>
                </span>
                <span>
                  {language === 'hi' ? 'स्रोत: प्रयोगशाला अर्क' : language === 'mr' ? 'स्रोत: प्रयोगशाळा नोंदी' : 'Source: Laboratory extract'}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* SECTION 2: EXCLUDED / UNRELIABLE LOW-CONFIDENCE OCR RESULTS */}
      {unreliableItems.length > 0 && (
        <div className="bg-amber-50/70 rounded-3xl border border-amber-200 p-6 shadow-soft mb-8">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h2 className="text-sm sm:text-base font-bold text-amber-950 mb-1">
                {t.unreliableFlagged} ({unreliableItems.length})
              </h2>
              <p className="text-xs sm:text-sm text-amber-900 leading-relaxed mb-3">
                {t.unreliableNotice}
              </p>
              <div className="space-y-2">
                {unreliableItems.map((u, idx) => (
                  <div key={idx} className="p-3 bg-white/80 rounded-xl border border-amber-200/80 text-xs flex justify-between items-center">
                    <span className="font-semibold text-clarity-charcoal">{u.name}</span>
                    <span className="text-amber-800 bg-amber-100 px-2 py-0.5 rounded font-mono font-bold">
                      {language === 'hi' ? 'अस्पष्ट स्कैन' : language === 'mr' ? 'अस्पष्ट स्कॅन' : 'Excluded for safety'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SECTION 3: WHAT HAS CHANGED (Historical Trends) */}
      {historicalChanges.length > 0 && (
        <div className="bg-clarity-surface rounded-3xl border border-clarity-border p-6 sm:p-8 shadow-soft mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-clarity-teal flex items-center gap-2">
              <svg className="w-5 h-5 text-clarity-teal" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
              {t.whatChanged}
            </h2>
            <span className="text-xs text-clarity-muted">
              {language === 'hi' ? 'पिछली रिपोर्ट से तुलना' : language === 'mr' ? 'मागील नोंदींशी तुलना' : 'Compared to previous tests'}
            </span>
          </div>

          <div className="space-y-3">
            {historicalChanges.map((tItem, idx) => (
              <div key={idx} className="p-3.5 bg-clarity-ivory/60 rounded-xl border border-clarity-border flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <span className="font-semibold text-sm text-clarity-charcoal">{tItem.name}</span>
                  <p className="text-xs text-clarity-muted mt-0.5">{tItem.concise_summary}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-clarity-teal px-2 py-1 rounded bg-clarity-mint/30">
                    {tItem.direction?.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <p className="text-[11px] text-clarity-muted mt-4 italic">
            {language === 'hi' ? 'संख्यात्मक अंतर केवल परीक्षणों के बीच का बदलाव दर्शाता है। यह स्वतः सुधार या गिरावट घोषित नहीं करता।' : language === 'mr' ? 'संख्यात्मक फरक केवळ तपासण्यांमधील अंतर दर्शवतो. डॉक्टरांच्या सल्ल्याशिवाय कोणताही निष्कर्ष काढू नये.' : 'Note: Numerical shifts reflect interval differences between tests. A trend alone does not automatically declare condition improvement or worsening without physician evaluation.'}
          </p>
        </div>
      )}

      {/* SECTION 4: CONTEXT FROM QUESTIONNAIRE ANSWERS */}
      {contextInsights.length > 0 && (
        <div className="bg-clarity-surface rounded-3xl border border-clarity-border p-6 sm:p-8 shadow-soft mb-8">
          <h2 className="text-lg font-bold text-clarity-teal mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-clarity-teal" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {t.whatAnswersTell}
          </h2>
          <div className="space-y-2">
            {contextInsights.map((insight, idx) => (
              <div key={idx} className="p-3.5 bg-clarity-ivory/60 rounded-xl border border-clarity-border/60 text-xs sm:text-sm text-clarity-charcoal leading-relaxed">
                &bull; {insight}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION 5: CLINICAL PATTERNS */}
      {clinicalPatterns.length > 0 && (
        <div className="bg-clarity-surface rounded-3xl border border-clarity-border p-6 sm:p-8 shadow-soft mb-8">
          <h2 className="text-lg font-bold text-clarity-teal mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            {t.clinicalPatterns}
          </h2>

          <div className="space-y-4">
            {clinicalPatterns.map((pat, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-indigo-50/50 border border-indigo-200">
                <h3 className="font-bold text-sm text-indigo-950 mb-1">{pat.pattern_name}</h3>
                <p className="text-xs sm:text-sm text-clarity-charcoal mb-2">{pat.what_this_means}</p>
                <div className="text-xs text-indigo-800 space-y-1">
                  <div><strong>Alternative explanations: </strong>{pat.alternative_explanations}</div>
                  <div><strong>Missing evidence: </strong>{pat.missing_evidence}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION 6: WHAT THESE TESTS COMMONLY CHECK */}
      {testPurposes.length > 0 && (
        <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-6 shadow-soft mb-8">
          <h2 className="text-base font-bold text-clarity-teal mb-3">
            {t.whatTestsCheck}
          </h2>
          <div className="space-y-3">
            {testPurposes.slice(0, 4).map((tp, idx) => (
              <div key={idx} className="text-xs sm:text-sm border-b border-clarity-border/60 pb-2">
                <span className="font-bold text-clarity-teal">{tp.test_name}: </span>
                <span className="text-clarity-charcoal">{tp.why_checked}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION 7: WITHIN REFERENCE RANGE ("See all results" expandable) */}
      {withinRangeItems.length > 0 && (
        <div className="mb-8">
          <button
            onClick={() => setShowAllResults(!showAllResults)}
            className="w-full p-4 bg-clarity-surface hover:bg-clarity-ivory rounded-2xl border border-clarity-border shadow-soft flex items-center justify-between text-sm font-semibold text-clarity-teal transition-all"
          >
            <span>{t.healthyResults} ({withinRangeItems.length})</span>
            <span className="underline">{showAllResults ? t.hideResults : t.seeAllResults}</span>
          </button>

          {showAllResults && (
            <div className="mt-3 p-4 bg-clarity-surface rounded-2xl border border-clarity-border space-y-2 animate-in fade-in">
              {withinRangeItems.map((item, idx) => (
                <div key={idx} className="flex justify-between items-center py-2 border-b border-clarity-border/50 text-xs sm:text-sm">
                  <span className="font-medium text-clarity-charcoal">{item.name}</span>
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-clarity-teal">{item.value}</span>
                    <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded text-[11px] font-bold">
                      {item.status_label || t.normal}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Suggested Questions for Your Doctor */}
      {suggestedQuestions.length > 0 && (
        <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-6 shadow-soft mb-8">
          <h2 className="text-base font-bold text-clarity-teal mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-clarity-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            {t.suggestedDoctorQuestions}
          </h2>
          <div className="space-y-2">
            {suggestedQuestions.map((q, idx) => (
              <div key={idx} className="p-3 bg-clarity-ivory/60 rounded-xl border border-clarity-border/60 text-sm text-clarity-charcoal flex items-start gap-2">
                <span className="font-bold text-clarity-teal">{idx + 1}.</span>
                <span>"{q}"</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Safe Next Steps */}
      {safeNextSteps.length > 0 && (
        <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-6 shadow-soft mb-8">
          <h2 className="text-base font-bold text-clarity-teal mb-3">
            {t.safeNextSteps}
          </h2>
          <div className="space-y-2">
            {safeNextSteps.map((step, idx) => (
              <div key={idx} className="text-xs sm:text-sm text-clarity-charcoal flex items-start gap-2">
                <span className="text-clarity-teal font-bold">&bull;</span>
                <span>{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* OPTIONAL INLINE NUTRITION & DOCTOR PROMPTS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        <div className="p-5 rounded-2xl bg-clarity-surface border border-clarity-border shadow-soft flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-sm text-clarity-teal mb-1">
              {t.nutritionPrompt}
            </h3>
            <p className="text-xs text-clarity-muted mb-4">
              {language === 'hi' ? 'आपकी जाँच के अनुसार संतुलित दैनिक आहार विचार।' : language === 'mr' ? 'तुमच्या निकालांशी सुसंगत दैनंदिन आहाराचे मार्गदर्शन.' : 'Balanced, practical everyday food ideas matched to your results.'}
            </p>
          </div>
          <div>
            <Button size="sm" variant="mint" onClick={() => setIsNutritionOpen(true)}>
              {t.showNutrition} &rarr;
            </Button>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-clarity-surface border border-clarity-border shadow-soft flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-sm text-clarity-teal mb-1">
              {t.doctorPrompt}
            </h3>
            <p className="text-xs text-clarity-muted mb-4">
              {language === 'hi' ? 'विशेषज्ञ चिकित्सकों से परामर्श का समय देखें।' : language === 'mr' ? 'तज्ज्ञ डॉक्टरांशी चर्चेसाठी वेळ निश्चित करा.' : 'Explore specialized physicians and book a demo consultation.'}
            </p>
          </div>
          <div>
            <Button size="sm" variant="secondary" onClick={() => setIsDoctorOpen(true)}>
              {t.findDoctor} &rarr;
            </Button>
          </div>
        </div>
      </div>

      {/* PDF DOWNLOAD & RESTART */}
      <div className="p-6 bg-clarity-surface rounded-3xl border border-clarity-border shadow-soft flex flex-col sm:flex-row items-center justify-between gap-4 mb-8">
        <div>
          <h3 className="font-bold text-sm text-clarity-teal">
            {t.keepCopy}
          </h3>
          <p className="text-xs text-clarity-muted">
            {t.keepCopySub}
          </p>
        </div>
        <Button variant="primary" onClick={handleDownloadPdf}>
          {t.downloadPdf}
        </Button>
      </div>

      {/* Translation Review Notice & Medical Disclaimer */}
      <div className="p-4 bg-clarity-ivory rounded-2xl border border-clarity-border text-xs text-clarity-muted leading-relaxed mb-8 space-y-1">
        <p className="font-semibold text-clarity-charcoal">{t.disclaimerTitle}</p>
        <p>{report.disclaimer || t.disclaimer}</p>
        <p className="italic text-[11px] pt-1 border-t border-clarity-border/40">{t.translationReviewNotice}</p>
      </div>

      {/* Restart */}
      <div className="flex justify-center">
        <Button variant="secondary" onClick={onRestart}>
          {t.understandAnother}
        </Button>
      </div>

      {/* Inline Nutrition Modal */}
      <InlineNutritionModal
        isOpen={isNutritionOpen}
        onClose={() => setIsNutritionOpen(false)}
        abnormalItems={attentionItems}
      />

      {/* Inline Doctor Discovery Modal */}
      <InlineDoctorModal
        isOpen={isDoctorOpen}
        onClose={() => setIsDoctorOpen(false)}
      />
    </div>
  );
}
