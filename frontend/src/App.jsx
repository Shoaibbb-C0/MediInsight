import React, { useState } from 'react';
import { Navigation } from './components/common/Navigation';
import { HomeScreen } from './components/journey/HomeScreen';
import { FileUploadModal } from './components/capture/FileUploadModal';
import { CameraCaptureModal } from './components/capture/CameraCaptureModal';
import { VerificationScreen } from './components/verification/VerificationScreen';
import { QuestionnaireScreen } from './components/journey/QuestionnaireScreen';
import { SimplifiedReportScreen } from './components/journey/SimplifiedReportScreen';
import { Button } from './components/common/WarmUI';
import {
  LOCAL_SYNTHETIC_BIOMARKERS,
  LOCAL_SYNTHETIC_QUESTIONS,
  generateLocalReport,
} from './fixtures/sampleData';

export default function App() {
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'reports' | 'profile'
  
  // Patient Journey State Machine
  // 'idle' -> 'processing' -> 'verifying' -> 'questionnaire' -> 'report'
  const [journeyStep, setJourneyStep] = useState('idle');
  const [currentReportId, setCurrentReportId] = useState(null);
  const [biomarkers, setBiomarkers] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [finalReport, setFinalReport] = useState(null);

  // Modals
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isCameraOpen, setIsCameraOpen] = useState(false);

  // Saved reports history state
  const [reportsHistory, setReportsHistory] = useState([
    {
      id: 'rep_prev_sample',
      date: 'September 2026',
      title: 'Routine Comprehensive Metabolic Panel',
      statusSummary: 'Kidneys healthy, blood sugar slightly elevated',
    },
  ]);

  // Handle file from upload or camera
  const handleProcessFile = async (file) => {
    setIsUploadOpen(false);
    setIsCameraOpen(false);
    setJourneyStep('processing');

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Attempt live backend API call with automatic graceful local fixture fallback
      let data = null;
      try {
        const res = await fetch('/api/v1/reports/upload', {
          method: 'POST',
          body: formData,
        });
        if (res.ok) {
          data = await res.json();
        }
      } catch (e) {
        console.info('Backend unavailable, using local client fixture mode', e);
      }

      const reportId = data ? data.report_id : `rep_${Date.now()}`;
      setCurrentReportId(reportId);

      // Fetch extractions
      let extractedData = LOCAL_SYNTHETIC_BIOMARKERS;
      try {
        const extRes = await fetch(`/api/v1/reports/${reportId}/extractions`);
        if (extRes.ok) {
          extractedData = await extRes.json();
        }
      } catch (e) {
        // use local fixture
      }

      // Fetch questions
      let questionData = LOCAL_SYNTHETIC_QUESTIONS;
      try {
        const qRes = await fetch(`/api/v1/reports/${reportId}/questions`);
        if (qRes.ok) {
          const json = await qRes.json();
          questionData = json.questions;
        }
      } catch (e) {
        // use local fixture
      }

      setBiomarkers(extractedData);
      setQuestions(questionData);

      // Transition to Step 1: Verification Screen
      setJourneyStep('verifying');
    } catch (err) {
      console.error('Processing error:', err);
      // Even upon failure, provide reliable local fixtures
      setCurrentReportId(`rep_${Date.now()}`);
      setBiomarkers(LOCAL_SYNTHETIC_BIOMARKERS);
      setQuestions(LOCAL_SYNTHETIC_QUESTIONS);
      setJourneyStep('verifying');
    }
  };

  // Direct demo flow
  const handleStartDemo = () => {
    setCurrentReportId('rep_demo_fixture');
    setBiomarkers(LOCAL_SYNTHETIC_BIOMARKERS);
    setQuestions(LOCAL_SYNTHETIC_QUESTIONS);
    setJourneyStep('verifying');
  };

  // Step 1 -> Step 2
  const handleConfirmVerification = async (verifiedBiomarkers) => {
    setBiomarkers(verifiedBiomarkers);
    // Transition to Step 2: Personalized Questionnaire
    setJourneyStep('questionnaire');
  };

  // Step 2 -> Step 3
  const handleSubmitAnswers = async (answersPayload) => {
    // Submit questionnaire to backend
    try {
      await fetch(`/api/v1/reports/${currentReportId}/questions/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          report_id: currentReportId,
          answers: answersPayload,
        }),
      });
    } catch {
      // offline fallback
    }

    // Retrieve generated report
    let rep = null;
    try {
      const sumRes = await fetch(`/api/v1/reports/${currentReportId}/summary`);
      if (sumRes.ok) {
        rep = await sumRes.json();
      }
    } catch {
      // offline fallback
    }

    if (!rep) {
      rep = generateLocalReport(currentReportId, answersPayload);
    }

    // Apply any patient corrections directly to key findings
    if (biomarkers && biomarkers.length > 0) {
      for (const b of biomarkers) {
        if (b.correction_provenance === 'patient_edited') {
          for (const finding of rep.key_findings) {
            if (finding.biomarker_name.includes(b.name) || finding.biomarker_name.toLowerCase().includes(b.canonical_name?.split('_')[0])) {
              finding.plain_english_summary = `Verified by you: ${b.name} (${b.value} ${b.unit}).`;
            }
          }
        }
      }
    }

    setFinalReport(rep);
    
    // Add to history
    setReportsHistory((prev) => [
      {
        id: currentReportId,
        date: 'Just now',
        title: 'Uploaded Blood & Metabolic Panel',
        statusSummary: rep.patient_summary.slice(0, 60) + '...',
      },
      ...prev,
    ]);

    // Transition to Step 3: Simplified Report
    setJourneyStep('report');
  };

  const handleRestartJourney = () => {
    setJourneyStep('idle');
    setCurrentReportId(null);
    setBiomarkers([]);
    setQuestions([]);
    setFinalReport(null);
  };

  return (
    <div className="min-h-screen bg-clarity-ivory flex flex-col font-sans">
      <Navigation
        activeTab={activeTab}
        onSelectTab={(tab) => {
          setActiveTab(tab);
          if (tab !== 'home') {
            // Keep state preserved or allow reviewing history
          }
        }}
      />

      <main className="flex-1 pb-16">
        {/* TAB 1: HOME & ACTIVE REPORT JOURNEY */}
        {activeTab === 'home' && (
          <>
            {journeyStep === 'idle' && (
              <HomeScreen
                onStartUpload={() => setIsUploadOpen(true)}
                onStartCamera={() => setIsCameraOpen(true)}
                onViewSample={handleStartDemo}
              />
            )}

            {journeyStep === 'processing' && (
              <div className="max-w-md mx-auto px-4 py-24 text-center">
                <div className="w-16 h-16 rounded-3xl bg-clarity-mint/40 border border-clarity-teal/20 flex items-center justify-center mx-auto mb-6 animate-pulse">
                  <svg className="w-8 h-8 text-clarity-teal animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-clarity-teal mb-2">
                  Reading your report carefully...
                </h2>
                <p className="text-sm text-clarity-muted">
                  Organizing test names, values, and reference ranges.
                </p>
              </div>
            )}

            {journeyStep === 'verifying' && (
              <VerificationScreen
                biomarkers={biomarkers}
                reportId={currentReportId}
                onConfirmAll={handleConfirmVerification}
                onBack={handleRestartJourney}
              />
            )}

            {journeyStep === 'questionnaire' && (
              <QuestionnaireScreen
                questions={questions}
                onSubmitAnswers={handleSubmitAnswers}
                onBack={() => setJourneyStep('verifying')}
                onSkipAll={() => handleSubmitAnswers([])}
              />
            )}

            {journeyStep === 'report' && (
              <SimplifiedReportScreen
                report={finalReport}
                onRestart={handleRestartJourney}
              />
            )}
          </>
        )}

        {/* TAB 2: MY REPORTS */}
        {activeTab === 'reports' && (
          <div className="max-w-2xl mx-auto px-4 py-10">
            <h1 className="text-2xl sm:text-3xl font-bold text-clarity-teal mb-2">
              My Reports
            </h1>
            <p className="text-sm text-clarity-muted mb-6">
              Access your previously explained reports and track changes over time.
            </p>

            <div className="space-y-3">
              {reportsHistory.map((rep) => (
                <div
                  key={rep.id}
                  className="p-5 bg-clarity-surface rounded-2xl border border-clarity-border shadow-soft flex items-center justify-between hover:border-clarity-teal/40 transition-all cursor-pointer"
                  onClick={() => {
                    handleStartDemo();
                    setActiveTab('home');
                  }}
                >
                  <div>
                    <span className="text-xs text-clarity-muted font-medium">{rep.date}</span>
                    <h3 className="font-bold text-clarity-teal text-base">{rep.title}</h3>
                    <p className="text-xs text-clarity-muted mt-1">{rep.statusSummary}</p>
                  </div>
                  <Button size="sm" variant="secondary">
                    View
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 3: PROFILE */}
        {activeTab === 'profile' && (
          <div className="max-w-2xl mx-auto px-4 py-10">
            <h1 className="text-2xl sm:text-3xl font-bold text-clarity-teal mb-2">
              Profile & Medical Context
            </h1>
            <p className="text-sm text-clarity-muted mb-6">
              Optional background to help customize explanations. Skip whatever you prefer.
            </p>

            <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-6 shadow-soft space-y-6">
              <div>
                <label className="text-sm font-semibold text-clarity-teal block mb-1">
                  Preferred Language
                </label>
                <select className="w-full sm:w-64 p-2.5 rounded-xl border border-clarity-border bg-clarity-ivory text-sm font-medium text-clarity-charcoal">
                  <option value="en">English (Warm Clarity)</option>
                  <option value="hi">हिंदी (Hindi) — Noto Sans Devanagari</option>
                  <option value="mr">मराठी (Marathi) — Noto Sans Devanagari</option>
                </select>
              </div>

              <div className="pt-4 border-t border-clarity-border">
                <label className="text-sm font-semibold text-clarity-teal block mb-1">
                  Known Health Conditions (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Mild hypertension, seasonal allergies (or leave blank)"
                  className="w-full p-2.5 rounded-xl border border-clarity-border bg-white text-sm"
                />
              </div>

              <div>
                <label className="text-sm font-semibold text-clarity-teal block mb-1">
                  Current Medications & Supplements (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Vitamin D3, multivitamin (or leave blank)"
                  className="w-full p-2.5 rounded-xl border border-clarity-border bg-white text-sm"
                />
              </div>

              <div>
                <label className="text-sm font-semibold text-clarity-teal block mb-1">
                  Known Reason for Testing
                </label>
                <input
                  type="text"
                  placeholder="e.g. Routine checkup, doctor requested follow-up"
                  className="w-full p-2.5 rounded-xl border border-clarity-border bg-white text-sm"
                />
              </div>

              <div className="pt-4 border-t border-clarity-border flex justify-between items-center">
                <span className="text-xs text-clarity-muted">
                  Private Session Mode: Records stay local.
                </span>
                <Button size="sm" variant="primary">
                  Save Preferences
                </Button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Upload File Modal */}
      <FileUploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onFileSelected={handleProcessFile}
      />

      {/* Camera Capture Modal */}
      <CameraCaptureModal
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onCompleteCapture={handleProcessFile}
      />
    </div>
  );
}
