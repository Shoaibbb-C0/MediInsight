import { apiFetch } from "./api";
import React, { useEffect, useState } from "react";
import { Navigation } from "./components/common/Navigation";
import { Button } from "./components/common/WarmUI";
import { ReportTrends } from "./components/journey/ReportTrends";
import { HomeScreen } from "./components/journey/HomeScreen";
import { FileUploadModal } from "./components/capture/FileUploadModal";
import { CameraCaptureModal } from "./components/capture/CameraCaptureModal";
import { QuestionnaireScreen } from "./components/journey/QuestionnaireScreen";
import { SimplifiedReportScreen } from "./components/journey/SimplifiedReportScreen";
import { InlineNutritionSection } from "./components/journey/InlineNutritionSection";
import { InlineDoctorSection } from "./components/journey/InlineDoctorSection";
import { TRANSLATIONS } from "./fixtures/translations";
import {
  getLocalDemoQuestions,
  generateLocalReport,
} from "./fixtures/sampleData";

async function request(url, options) {
  const response = await apiFetch(url, options);
  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  return response.json();
}

import { AuthGate } from "./AuthGate";
export default function App() {
  return (
    <AuthGate>{(onSignOut, initialLanguage) => <PatientApp onSignOut={onSignOut} initialLanguage={initialLanguage} />}</AuthGate>
  );
}
function PatientApp({ onSignOut, initialLanguage }) {
  const [activeTab, setActiveTab] = useState("home");
  const [language, setLanguage] = useState(initialLanguage || "en");
  const [step, setStep] = useState("idle");
  const [reportId, setReportId] = useState(null);
  const [uploadInfo, setUploadInfo] = useState(null);
  const [measurements, setMeasurements] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [report, setReport] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [history, setHistory] = useState([]);
  const [modal, setModal] = useState(null);
  const [error, setError] = useState(false);
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;
  const copy = {
    en: [
      "We could not complete this request. Check the service and try again. No example measurements were substituted.",
      "Example report · demo data",
      "Start with your report",
      "Your report connects your results with relevant food and doctor guidance.",
      "Your history starts here",
      "Reports uploaded in this session appear here. Demo reports stay separate.",
      "View report",
      "Uploaded laboratory report",
      "Session history clears when this page reloads. Uploaded reports are processed by the configured server.",
      "Changes apply immediately",
      "Manage your language preference",
      "Back to upload",
    ],
    hi: [
      "अनुरोध पूरा नहीं हुआ। सेवा जाँचकर फिर कोशिश करें। उदाहरण माप उपयोग नहीं किए गए।",
      "उदाहरण रिपोर्ट · डेमो डेटा",
      "पहले रिपोर्ट जोड़ें",
      "रिपोर्ट से संबंधित आहार और डॉक्टर मार्गदर्शन यहाँ दिखेगा।",
      "आपका इतिहास यहाँ शुरू होगा",
      "इस सत्र की रिपोर्ट यहाँ दिखेंगी। डेमो रिपोर्ट अलग रहती हैं।",
      "रिपोर्ट देखें",
      "अपलोड की गई रिपोर्ट",
      "पेज दोबारा लोड करने पर सत्र का इतिहास मिट जाता है। रिपोर्ट कॉन्फ़िगर किए गए सर्वर पर संसाधित होती हैं।",
      "बदलाव तुरंत लागू होते हैं",
      "अपनी भाषा चुनें",
      "अपलोड पर वापस जाएँ",
    ],
    mr: [
      "विनंती पूर्ण झाली नाही. सेवा तपासून पुन्हा प्रयत्न करा. उदाहरणातील मोजमाप वापरलेले नाहीत.",
      "उदाहरण अहवाल · डेमो डेटा",
      "आधी अहवाल जोडा",
      "अहवालाशी संबंधित आहार आणि डॉक्टरांचे मार्गदर्शन येथे दिसेल.",
      "तुमचा इतिहास येथे सुरू होतो",
      "या सत्रातील अहवाल येथे दिसतील. डेमो अहवाल वेगळे राहतात.",
      "अहवाल पाहा",
      "अपलोड केलेला अहवाल",
      "पेज पुन्हा लोड केल्यावर सत्रातील इतिहास मिटतो. अहवाल कॉन्फिगर केलेल्या सर्व्हरवर प्रक्रिया केले जातात.",
      "बदल लगेच लागू होतात",
      "तुमची भाषा निवडा",
      "अपलोडवर परत जा",
    ],
  }[language];
  useEffect(() => {
    document.documentElement.lang = language;
    document.title = `${t[activeTab] || (activeTab === "nutrition" ? "Nutrition" : "Doctors")} · Simplifier`;
  }, [language, activeTab, t]);

  useEffect(() => {
    let active = true;
    request(`/api/v1/reports/history/list?lang=${language}`)
      .then((data) => {
        if (active && Array.isArray(data.reports)) setHistory(data.reports);
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, [language]);

  async function processFile(file) {
    setModal(null);
    setError(false);
    setStep("processing");
    try {
      const form = new FormData();
      form.append("file", file);
      const uploaded = await request("/api/v1/reports/upload", {
        method: "POST",
        body: form,
      });
      if (uploaded.is_synthetic_fixture)
        throw new Error("Unexpected demo data");
      const extracted = await request(
        `/api/v1/reports/${uploaded.report_id}/extractions`,
      );
      if (!extracted.length) throw new Error("No measurements");
      const context = await request(
        `/api/v1/reports/${uploaded.report_id}/questions?lang=${language}`,
      );
      setReportId(uploaded.report_id);
      setUploadInfo(uploaded);
      setMeasurements(extracted);
      setReport(null);
      setQuestions(context.questions || []);
      setStep("questionnaire");
    } catch {
      setError(true);
      setStep("idle");
    }
  }
  async function startDemo() {
    setError(false);
    setReportId("rep_demo_fixture");
    setReport(null);
    setStep("processing");
    try {
      setQuestions(
        (
          await request(
            `/api/v1/reports/rep_demo_fixture/questions?lang=${language}`,
          )
        ).questions,
      );
    } catch {
      setQuestions(getLocalDemoQuestions(language));
    }
    setStep("questionnaire");
  }
  async function submitAnswers(payload) {
    setError(false);
    setStep("processing");
    try {
      let summary;
      if (reportId === "rep_demo_fixture") {
        try {
          await request(`/api/v1/reports/${reportId}/questions/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ report_id: reportId, answers: payload }),
          });
          summary = await request(
            `/api/v1/reports/${reportId}/summary?lang=${language}`,
          );
        } catch {
          summary = {
            ...generateLocalReport(reportId, payload, language),
            is_offline_demo: true,
          };
        }
      } else {
        await request(`/api/v1/reports/${reportId}/questions/submit`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ report_id: reportId, answers: payload }),
        });
        summary = await request(
          `/api/v1/reports/${reportId}/summary?lang=${language}`,
        );
        if (summary.is_synthetic_fixture)
          throw new Error("Unexpected demo data");
      }
      setAnswers(payload);
      setReport(summary);
      setStep("report");
      if (reportId !== "rep_demo_fixture")
        setHistory((prev) => [
          {
            id: reportId,
            date: new Date().toISOString(),
            report: summary,
            answers: payload,
            measurements,
            filename: uploadInfo?.filename,
            fileType: uploadInfo?.file_type,
          },
          ...prev.filter((item) => item.id !== reportId),
        ]);
    } catch {
      setError(true);
      setStep("questionnaire");
    }
  }
  async function changeLanguage(next) {
    setLanguage(next);
    setError(false);
    if (!reportId) return;
    try {
      if (report)
        setReport(
          report.is_offline_demo
            ? {
                ...generateLocalReport(reportId, answers, next),
                is_offline_demo: true,
              }
            : await request(`/api/v1/reports/${reportId}/summary?lang=${next}`),
        );
      else if (step === "questionnaire")
        setQuestions(
          (await request(`/api/v1/reports/${reportId}/questions?lang=${next}`))
            .questions || [],
        );
    } catch {
      if (reportId === "rep_demo_fixture" && step === "questionnaire")
        setQuestions(getLocalDemoQuestions(next));
      else setError(true);
    }
  }
  async function openStoredReport(item) {
    setReportId(item.id);
    setAnswers(item.answers);
    setMeasurements(item.measurements);
    setActiveTab("home");
    setStep("processing");
    setError(false);
    try {
      setReport(
        await request(`/api/v1/reports/${item.id}/summary?lang=${language}`),
      );
      setStep("report");
    } catch {
      setError(true);
      setStep("idle");
    }
  }
  function restart() {
    setStep("idle");
    setReport(null);
    setReportId(null);
    setError(false);
  }
  return (
    <div className="min-h-screen bg-clarity-ivory flex flex-col font-sans">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:p-4 bg-white"
      >
        Skip to content
      </a>
      <Navigation
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        language={language}
        onSelectLanguage={changeLanguage}
      />
      <main id="main-content" className="flex-1 pb-16">
        {error && (
          <div
            role="alert"
            className="max-w-3xl mx-auto m-4 p-5 rounded-2xl border border-red-200 bg-red-50 text-red-900"
          >
            {copy[0]}
          </div>
        )}
        {activeTab === "home" && (
          <>
            {step === "idle" && (
              <HomeScreen
                language={language}
                onStartUpload={() => setModal("upload")}
                onStartCamera={() => setModal("camera")}
                onViewSample={startDemo}
              />
            )}
            {step === "processing" && (
              <div
                role="status"
                className="max-w-lg mx-auto px-5 py-24 text-center"
              >
                <div className="animate-pulse w-16 h-16 bg-clarity-mint rounded-3xl mx-auto mb-6" />
                <h1>{t.readingReport}</h1>
                <p className="text-clarity-muted mt-4">{t.readingSubtitle}</p>
              </div>
            )}
            {step === "questionnaire" && (
              <>
                {reportId === "rep_demo_fixture" && (
                  <p className="max-w-xl mx-auto px-4 pt-6 text-amber-900">
                    {copy[1]}
                  </p>
                )}
                <QuestionnaireScreen
                  questions={questions}
                  onSubmitAnswers={submitAnswers}
                  onBack={restart}
                  onSkipAll={() => submitAnswers([])}
                  language={language}
                />
              </>
            )}
            {step === "report" && (
              <SimplifiedReportScreen
                report={report}
                onRestart={restart}
                language={language}
              />
            )}
          </>
        )}
        {["nutrition", "doctors"].includes(activeTab) && (
          <div className="max-w-6xl mx-auto px-5 sm:px-8 py-10">
            {report ? (
              <>
                {report.is_synthetic_fixture && (
                  <p className="text-amber-900 bg-amber-50 rounded-xl p-4 mb-5">
                    {copy[1]}
                  </p>
                )}
                {activeTab === "nutrition" ? (
                  <InlineNutritionSection
                    key={reportId}
                    reportId={reportId}
                    language={language}
                    isExpanded
                  />
                ) : (
                  <InlineDoctorSection
                    key={reportId}
                    reportId={reportId}
                    language={language}
                    isExpanded
                  />
                )}
              </>
            ) : (
              <div className="bg-white rounded-3xl p-8 sm:p-12">
                <h1 className="mb-4">{copy[2]}</h1>
                <p className="text-clarity-muted mb-6">{copy[3]}</p>
                <Button onClick={() => setActiveTab("home")}>
                  {t.uploadButton}
                </Button>
              </div>
            )}
          </div>
        )}
        {activeTab === "reports" && (
          <div className="max-w-4xl mx-auto px-5 py-10">
            <p className="text-clarity-teal font-bold text-sm mb-3">
              SIMPLIFIER
            </p>
            <h1 className="mb-8">{t.reports}</h1>
            {!history.length && (
              <div className="bg-white rounded-3xl p-8">
                <h2 className="text-2xl font-bold mb-3">{copy[4]}</h2>
                <p className="text-clarity-muted mb-5">{copy[5]}</p>
                <Button onClick={() => setActiveTab("home")}>
                  {t.uploadButton}
                </Button>
              </div>
            )}
            <div className="space-y-4">
              {history.map((item) => (
                <article
                  key={item.id}
                  className="p-6 bg-white rounded-3xl border border-clarity-border"
                >
                  <p className="text-sm text-clarity-muted">
                    {new Date(item.date).toLocaleDateString(language)} ·{" "}
                    {item.id}
                  </p>
                  <h2 className="font-bold text-2xl my-3 break-words">
                    {item.filename || copy[7]}
                  </h2>
                  <p className="text-sm text-clarity-muted">
                    {item.fileType?.toUpperCase()}
                  </p>
                  <p className="text-clarity-muted mb-5">
                    {item.report.patient_summary}
                  </p>
                  <Button
                    variant="secondary"
                    onClick={() => openStoredReport(item)}
                  >
                    {copy[6]}
                  </Button>
                </article>
              ))}
            </div>
            <ReportTrends history={history} language={language} />
          </div>
        )}
        {activeTab === "profile" && (
          <div className="max-w-3xl mx-auto px-5 py-10">
            <h1 className="mb-4">{t.profile}</h1>
            <p className="text-clarity-muted mb-8">{copy[10]}</p>
            <section className="bg-white rounded-3xl border border-clarity-border p-6 sm:p-8">
              <label
                htmlFor="preferred-language"
                className="font-bold text-lg block mb-4"
              >
                {t.preferredLanguage}
              </label>
              <select
                id="preferred-language"
                value={language}
                onChange={(e) => changeLanguage(e.target.value)}
                className="w-full rounded-xl border border-clarity-border p-3 bg-clarity-ivory"
              >
                <option value="en">English</option>
                <option value="hi">हिंदी</option>
                <option value="mr">मराठी</option>
              </select>
              <p className="text-clarity-teal text-sm mt-3">{copy[9]}</p>
              <p className="text-clarity-muted mt-8 pt-6 border-t border-clarity-border">
                {language === "hi"
                  ? "रिपोर्ट आपके सत्र या प्रमाणित खाते तक सीमित हैं।"
                  : language === "mr"
                    ? "अहवाल तुमच्या सत्र किंवा प्रमाणित खात्यापुरते मर्यादित आहेत."
                    : "Reports are stored for your isolated development session or verified account."}
              </p>
              {onSignOut && (
                <Button onClick={onSignOut} className="mt-6">
                  {language === "hi"
                    ? "साइन आउट"
                    : language === "mr"
                      ? "साइन आउट"
                      : "Sign out"}
                </Button>
              )}
            </section>
          </div>
        )}
      </main>
      <FileUploadModal
        isOpen={modal === "upload"}
        onClose={() => setModal(null)}
        onFileSelected={processFile}
        language={language}
      />
      <CameraCaptureModal
        isOpen={modal === "camera"}
        onClose={() => setModal(null)}
        onCompleteCapture={processFile}
        language={language}
      />
    </div>
  );
}
