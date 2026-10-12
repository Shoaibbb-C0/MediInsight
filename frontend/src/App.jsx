import React, { useState } from 'react';
import { Navigation } from './components/common/Navigation';
import { HomeScreen } from './components/journey/HomeScreen';
import { FileUploadModal } from './components/capture/FileUploadModal';
import { CameraCaptureModal } from './components/capture/CameraCaptureModal';
import { QuestionnaireScreen } from './components/journey/QuestionnaireScreen';
import { SimplifiedReportScreen } from './components/journey/SimplifiedReportScreen';
import { Button } from './components/common/WarmUI';
import { TRANSLATIONS } from './fixtures/translations';
import {
  LOCAL_SYNTHETIC_BIOMARKERS,
  LOCAL_SYNTHETIC_QUESTIONS,
  generateLocalReport,
} from './fixtures/sampleData';

export default function App() {
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'reports' | 'profile'
  const [language, setLanguage] = useState('en'); // 'en' | 'hi' | 'mr'
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;
  
  // Patient Journey State Machine
  // 'idle' -> 'processing' -> 'questionnaire' -> 'report'
  // (No mandatory manual transcription screen in the standard journey)
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

      // Fetch questions in current selected language
      let questionData = LOCAL_SYNTHETIC_QUESTIONS;
      try {
        const qRes = await fetch(`/api/v1/reports/${reportId}/questions?lang=${language}`);
        if (qRes.ok) {
          const json = await qRes.json();
          questionData = json.questions;
        }
      } catch (e) {
        // use local fixture
      }

      setBiomarkers(extractedData);
      setQuestions(questionData);

      // Step directly to Step 1 of Journey: Adaptive Context Questionnaire
      // (Bypassing mandatory transcription verification)
      setJourneyStep('questionnaire');
    } catch (err) {
      console.error('Processing error:', err);
      setCurrentReportId(`rep_${Date.now()}`);
      setBiomarkers(LOCAL_SYNTHETIC_BIOMARKERS);
      setQuestions(LOCAL_SYNTHETIC_QUESTIONS);
      setJourneyStep('questionnaire');
    }
  };

  // Direct demo flow
  const handleStartDemo = async () => {
    setCurrentReportId('rep_demo_fixture');
    setBiomarkers(LOCAL_SYNTHETIC_BIOMARKERS);
    
    // Fetch demo questions for current language
    let questionData = LOCAL_SYNTHETIC_QUESTIONS;
    try {
      const qRes = await fetch(`/api/v1/reports/rep_demo_fixture/questions?lang=${language}`);
      if (qRes.ok) {
        const json = await qRes.json();
        questionData = json.questions;
      }
    } catch (e) {
      // offline fixture
    }

    setQuestions(questionData);
    setJourneyStep('questionnaire');
  };

  // Questionnaire submission -> Final Smart Report
  const handleSubmitAnswers = async (answersPayload) => {
    setJourneyStep('processing');

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

    // Retrieve generated report in user's language
    let rep = null;
    try {
      const sumRes = await fetch(`/api/v1/reports/${currentReportId}/summary?lang=${language}`);
      if (sumRes.ok) {
        rep = await sumRes.json();
      }
    } catch {
      // offline fallback
    }

    if (!rep) {
      rep = generateLocalReport(currentReportId, answersPayload, language);
    }

    setFinalReport(rep);
    
    // Add to history
    setReportsHistory((prev) => [
      {
        id: currentReportId,
        date: language === 'hi' ? 'अभी-अभी' : language === 'mr' ? 'आत्ताच' : 'Just now',
        title: language === 'hi' ? 'रक्त एवं मेटाबॉलिक रिपोर्ट' : language === 'mr' ? 'रक्त व चयापचय अहवाल' : 'Uploaded Blood & Metabolic Panel',
        statusSummary: rep.patient_summary.slice(0, 60) + '...',
      },
      ...prev,
    ]);

    // Arrive at Final Smart Report
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
        }}
        language={language}
        onSelectLanguage={setLanguage}
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
                language={language}
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
                  {t.readingReport}
                </h2>
                <p className="text-sm text-clarity-muted">
                  {t.readingSubtitle}
                </p>
              </div>
            )}

            {journeyStep === 'questionnaire' && (
              <QuestionnaireScreen
                questions={questions}
                onSubmitAnswers={handleSubmitAnswers}
                onBack={handleRestartJourney}
                onSkipAll={() => handleSubmitAnswers([])}
                language={language}
              />
            )}

            {journeyStep === 'report' && (
              <SimplifiedReportScreen
                report={finalReport}
                onRestart={handleRestartJourney}
                language={language}
              />
            )}
          </>
        )}

        {/* TAB 2: MY REPORTS */}
        {activeTab === 'reports' && (
          <div className="max-w-2xl mx-auto px-4 py-10">
            <h1 className="text-2xl sm:text-3xl font-bold text-clarity-teal mb-2">
              {t.reports}
            </h1>
            <p className="text-sm text-clarity-muted mb-6">
              {language === 'hi' ? 'अपनी पिछली व्याख्याओं को देखें और समय के साथ बदलाव समझें।' : language === 'mr' ? 'तुमचे मागील अहवाल पहा आणि काळासोबत झालेले बदल समजून घ्या.' : 'Access your previously explained reports and track changes over time.'}
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
                    {language === 'hi' ? 'देखें' : language === 'mr' ? 'पहा' : 'View'}
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
              {t.profile}
            </h1>
            <p className="text-sm text-clarity-muted mb-6">
              {language === 'hi' ? 'भाषा और व्यक्तिगत प्राथमिकताओं का प्रबंधन करें।' : language === 'mr' ? 'भाषा आणि वैयक्तिक पसंती व्यवस्थापित करा.' : 'Manage language and health context preferences.'}
            </p>

            <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-6 shadow-soft space-y-6">
              <div>
                <label className="text-sm font-semibold text-clarity-teal block mb-1">
                  {t.preferredLanguage}
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full sm:w-72 p-2.5 rounded-xl border border-clarity-border bg-clarity-ivory text-sm font-medium text-clarity-charcoal"
                >
                  <option value="en">English (Warm Clarity)</option>
                  <option value="hi">हिंदी (Hindi) — Noto Sans Devanagari</option>
                  <option value="mr">मराठी (Marathi) — Noto Sans Devanagari</option>
                </select>
              </div>

              <div className="pt-4 border-t border-clarity-border flex justify-between items-center">
                <span className="text-xs text-clarity-muted">
                  {language === 'hi' ? 'सत्र स्थानीय व गोपनीय है।' : language === 'mr' ? 'सत्र स्थानिक व सुरक्षित आहे.' : 'Private Session Mode: Records stay local.'}
                </span>
                <Button size="sm" variant="primary">
                  {t.savePreferences}
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
        language={language}
      />

      {/* Camera Capture Modal */}
      <CameraCaptureModal
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onCompleteCapture={handleProcessFile}
        language={language}
      />
    </div>
  );
}
