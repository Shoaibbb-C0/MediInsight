import { apiFetch } from "../../api";
import React, { useEffect, useState, useCallback } from "react";
import { Button } from "../common/WarmUI";
import { useDialogFocus } from "../common/useDialogFocus";
import { ProviderMap } from "./ProviderMap";
import { TRANSLATIONS } from "../../fixtures/translations";

const COPY = {
  en: [
    "Consult Doctor",
    "View profile",
    "Choose consultation type",
    "Contact Clinic",
    "No appointment has been booked. Confirm fees, type, and availability directly with the provider.",
    "Business information from Google Maps is not verified medical registration.",
    "Prepare for your consultation",
    "Report to discuss",
    "Abnormal findings",
    "Questions to ask",
    "I consent to include this report’s medical information in a PDF I can choose to share.",
    "Download consultation-ready PDF",
    "Nothing is sent to a provider automatically. External contact links contain no report or medical history.",
    "No supported consultation route was supplied.",
    "Map service is not configured. Use the provider’s Google Maps link.",
    "Google Maps",
    "Website",
    "Search radius",
    "Close",
    "Provider search unavailable. Please try again.",
    "Choose a location to search.",
    "Provider list",
    "Map",
    "No providers found. Try increasing the radius or a nearby town.",
    "Call Doctor/Clinic",
    "Online Consultation",
    "External Booking",
    "WhatsApp Consultation",
    "Request Clinic Visit",
    "Demo provider — no real consultation availability",
    "Consultation preparation unavailable.",
    "Live scheduling is not configured. Use a supported contact option; this does not confirm an appointment.",
    "Upcoming consultations",
    "No integrated appointments. External bookings must be managed with the provider.",
  ],
  hi: [
    "डॉक्टर से परामर्श",
    "प्रोफ़ाइल देखें",
    "परामर्श का प्रकार चुनें",
    "क्लीनिक से संपर्क करें",
    "अभी अपॉइंटमेंट बुक नहीं हुआ है। शुल्क, प्रकार और समय की पुष्टि डॉक्टर से करें।",
    "Google Maps की जानकारी सत्यापित चिकित्सा पंजीकरण नहीं है।",
    "परामर्श की तैयारी",
    "चर्चा के लिए रिपोर्ट",
    "असामान्य नतीजे",
    "पूछने के लिए प्रश्न",
    "मैं अपनी इच्छा से साझा करने योग्य PDF में इस रिपोर्ट की चिकित्सा जानकारी शामिल करने की सहमति देता/देती हूँ।",
    "परामर्श के लिए PDF डाउनलोड करें",
    "किसी डॉक्टर को जानकारी अपने आप नहीं भेजी जाती। संपर्क लिंक में रिपोर्ट या चिकित्सा इतिहास नहीं होता।",
    "समर्थित परामर्श संपर्क उपलब्ध नहीं है।",
    "मानचित्र सेवा कॉन्फ़िगर नहीं है। डॉक्टर का Google Maps लिंक खोलें।",
    "Google Maps",
    "वेबसाइट",
    "खोज की दूरी",
    "बंद करें",
    "डॉक्टर खोज उपलब्ध नहीं। फिर कोशिश करें।",
    "खोज के लिए स्थान चुनें।",
    "डॉक्टरों की सूची",
    "मानचित्र",
    "कोई डॉक्टर नहीं मिला। दूरी बढ़ाएँ या नज़दीकी शहर चुनें।",
    "डॉक्टर/क्लीनिक को कॉल करें",
    "ऑनलाइन परामर्श",
    "बाहरी बुकिंग",
    "WhatsApp परामर्श",
    "क्लीनिक परामर्श का अनुरोध",
    "डेमो डॉक्टर — वास्तविक समय उपलब्ध नहीं",
    "परामर्श की तैयारी उपलब्ध नहीं।",
    "प्रत्यक्ष समय बुकिंग कॉन्फ़िगर नहीं है। संपर्क विकल्प से पूछताछ करें। यह बुकिंग की पुष्टि नहीं है।",
    "आने वाले परामर्श",
    "एकीकृत अपॉइंटमेंट नहीं हैं। बाहरी बुकिंग डॉक्टर से प्रबंधित करें।",
  ],
  mr: [
    "डॉक्टरांचा सल्ला घ्या",
    "प्रोफाइल पाहा",
    "सल्ल्याचा प्रकार निवडा",
    "दवाखान्याशी संपर्क करा",
    "अद्याप भेट बुक झालेली नाही. शुल्क, प्रकार आणि वेळ डॉक्टरांकडून निश्चित करा.",
    "Google Maps वरील माहिती म्हणजे सत्यापित वैद्यकीय नोंदणी नाही.",
    "सल्ल्यासाठी तयारी",
    "चर्चेसाठी अहवाल",
    "असामान्य निकाल",
    "विचारायचे प्रश्न",
    "मी माझ्या इच्छेने शेअर करण्याजोग्या PDF मध्ये या अहवालाची वैद्यकीय माहिती समाविष्ट करण्यास संमती देतो/देते.",
    "सल्ल्यासाठी PDF डाउनलोड करा",
    "डॉक्टरांना आपोआप माहिती पाठवली जात नाही. संपर्क लिंकवर अहवाल किंवा वैद्यकीय इतिहास नसतो.",
    "समर्थित सल्ल्याचा संपर्क उपलब्ध नाही.",
    "नकाशा सेवा कॉन्फिगर नाही. डॉक्टरांची Google Maps लिंक उघडा.",
    "Google Maps",
    "वेबसाइट",
    "शोधाची त्रिज्या",
    "बंद करा",
    "डॉक्टर शोध उपलब्ध नाही. पुन्हा प्रयत्न करा.",
    "शोधासाठी ठिकाण निवडा.",
    "डॉक्टरांची यादी",
    "नकाशा",
    "डॉक्टर सापडले नाहीत. त्रिज्या वाढवा किंवा जवळचे गाव निवडा.",
    "डॉक्टर/दवाखान्याला कॉल करा",
    "ऑनलाइन सल्ला",
    "बाह्य बुकिंग",
    "WhatsApp सल्ला",
    "दवाखान्यात भेटीची विनंती",
    "डेमो डॉक्टर — प्रत्यक्ष वेळ उपलब्ध नाही",
    "सल्ल्याची तयारी उपलब्ध नाही.",
    "प्रत्यक्ष भेटीचे वेळापत्रक कॉन्फिगर केलेले नाही. संपर्क पर्याय वापरा. यामुळे भेट निश्चित होत नाही.",
    "आगामी सल्ले",
    "एकत्रित अपॉइंटमेंट नाहीत. बाह्य बुकिंग डॉक्टरांकडून व्यवस्थापित करा.",
  ],
};
async function jsonRequest(url, options) {
  const response = await apiFetch(url, {
    credentials: "same-origin",
    ...options,
  });
  const data = await response.json();
  if (!response.ok)
    throw new Error(
      typeof data.detail === "string" ? data.detail : "Request unavailable",
    );
  return data;
}
function safeLink(url) {
  return (
    typeof url === "string" &&
    (/^https:\/\//.test(url) || /^tel:\+?[\d]+$/.test(url))
  );
}

export function InlineDoctorSection({
  reportId = "rep_demo_fixture",
  language = "en",
  isExpanded = false,
  onToggleExpand = () => {},
}) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en,
    c = COPY[language] || COPY.en;
  const [data, setData] = useState(null),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(false);
  const [location, setLocation] = useState(""),
    [radius, setRadius] = useState(10000),
    [mode, setMode] = useState("list");
  const [provider, setProvider] = useState(null),
    [consulting, setConsulting] = useState(false);
  const [selectedReport, setSelectedReport] = useState(reportId),
    [reports, setReports] = useState([]),
    [preparation, setPreparation] = useState(null),
    [consent, setConsent] = useState(false),
    [exporting, setExporting] = useState(false);
  const dialogRef = useDialogFocus(Boolean(provider), () => setProvider(null));
  useEffect(() => {
    let active = true;
    setProvider(null);
    setData(null);
    setError("");
    setSelectedReport(reportId);
    if (isExpanded)
      jsonRequest(`/api/v1/reports/${reportId}/doctors?lang=${language}`)
        .then((result) => {
          if (active) setData(result);
        })
        .catch(() => {
          if (active) setError(c[19]);
        });
    return () => {
      active = false;
    };
  }, [reportId, language, isExpanded]);
  useEffect(() => {
    let active = true;
    setConsent(false);
    setPreparation(null);
    if (provider && consulting) {
      jsonRequest(
        `/api/v1/consultation/preparation/${selectedReport}?lang=${language}`,
      )
        .then((value) => {
          if (active) setPreparation(value);
        })
        .catch(() => {
          if (active) setError(c[30]);
        });
      jsonRequest(`/api/v1/reports/history/list?lang=${language}`)
        .then((value) => {
          if (active) setReports(value.reports || []);
        })
        .catch(() => {});
    }
    return () => {
      active = false;
    };
  }, [provider, consulting, selectedReport, language]);
  async function search(coords) {
    setLoading(true);
    setError("");
    setProvider(null);
    const params = new URLSearchParams({
      lang: language,
      radius_m: String(radius),
    });
    if (coords) {
      params.set("lat", coords.latitude);
      params.set("lng", coords.longitude);
    } else params.set("city", location.trim());
    try {
      setData(
        await jsonRequest(`/api/v1/reports/${reportId}/doctors?${params}`),
      );
    } catch {
      setData(null);
      setError(c[19]);
    } finally {
      setLoading(false);
    }
  }
  function locate() {
    if (!navigator.geolocation) {
      setError(t.locationPermissionDenied);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => search(position.coords),
      () => setError(t.locationPermissionDenied),
      { timeout: 10000 },
    );
  }
  async function download() {
    if (!consent || !preparation) return;
    setExporting(true);
    setError("");
    try {
      const response = await apiFetch("/api/v1/consultation/pdf", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          report_id: selectedReport,
          language,
          consent_to_include_report: true,
        }),
      });
      if (!response.ok) throw new Error();
      const blob = await response.blob(),
        url = URL.createObjectURL(blob),
        link = document.createElement("a");
      link.href = url;
      link.download = "Simplifier_Consultation_Preparation.pdf";
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch {
      setError(c[30]);
    } finally {
      setExporting(false);
    }
  }
  const openProfile = useCallback(
    (item) => {
      setProvider(item);
      setConsulting(false);
      setSelectedReport(reportId);
      setConsent(false);
      setError("");
    },
    [reportId],
  );
  const options = (provider?.consultation_options || []).filter(
    (option) => option.evidence && safeLink(option.url),
  );
  const optionLabels = {
    call: c[24],
    online: c[25],
    external_booking: c[26],
    whatsapp: c[27],
    clinic_visit: c[28],
    website: c[3],
  };
  return (
    <section
      id="doctor-discovery-section"
      className="bg-white rounded-3xl border border-clarity-border p-5 sm:p-8 mb-8"
    >
      <div className="flex flex-wrap justify-between gap-4 mb-5">
        <h2 className="font-bold text-2xl">{t.findDoctor}</h2>
        {!isExpanded && <Button onClick={onToggleExpand}>{c[0]}</Button>}
      </div>
      {isExpanded && (
        <>
          <p className="text-clarity-muted mb-5">{c[5]}</p>
          <form
            onSubmit={(event) => {
              event.preventDefault();
              if (location.trim()) search();
            }}
            className="flex flex-wrap gap-3 mb-5"
          >
            <label className="grow min-w-0">
              {t.locationPlaceholder}
              <input
                className="block w-full rounded-xl border p-3 mt-2"
                value={location}
                onChange={(event) => setLocation(event.target.value)}
                maxLength={120}
                placeholder={t.locationPlaceholder}
              />
            </label>
            <label>
              {c[17]}
              <select
                className="block rounded-xl border p-3 mt-2"
                value={radius}
                onChange={(event) => setRadius(Number(event.target.value))}
              >
                {[5000, 10000, 25000, 50000].map((value) => (
                  <option key={value} value={value}>
                    {value / 1000} km
                  </option>
                ))}
              </select>
            </label>
            <Button
              type="submit"
              disabled={loading || !location.trim()}
              className="self-end"
            >
              {t.searchLocationBtn}
            </Button>
            <Button variant="secondary" onClick={locate} className="self-end">
              {t.useMyLocation}
            </Button>
          </form>
          {error && (
            <p
              role="alert"
              className="bg-amber-50 text-amber-900 rounded-xl p-4 mb-4"
            >
              {error}
            </p>
          )}
          <div className="flex gap-3 mb-4">
            {["list", "map"].map((item, index) => (
              <Button
                key={item}
                variant={mode === item ? "primary" : "secondary"}
                aria-pressed={mode === item}
                onClick={() => setMode(item)}
              >
                {c[21 + index]}
              </Button>
            ))}
          </div>
          {loading && <p role="status">{t.readingReport}</p>}
          {data?.location_required && (
            <p className="py-8 text-clarity-muted">{c[20]}</p>
          )}
          {data?.is_demo_mode && (
            <p className="bg-amber-50 text-amber-900 rounded-xl p-4 mb-5">
              {c[29]}
            </p>
          )}
          {data?.live_provider_api_configured && (
            <p className="text-sm mb-4">
              <img
                src="/attribution/google-maps.svg"
                alt="Google Maps"
                translate="no"
                className="inline-block h-[18px] w-auto m-2.5"
              />{" "}
              · {data.resolved_location.display_name} ·{" "}
              {data.searched_radius_m / 1000} km
            </p>
          )}
          {mode === "map" && (
            <ProviderMap
              providers={data?.providers || []}
              location={data?.resolved_location}
              onSelect={openProfile}
              language={language}
            />
          )}
          <div className="grid md:grid-cols-2 gap-4">
            {(data?.providers || []).map((item) => (
              <article
                key={item.id}
                className="rounded-2xl border border-clarity-border p-5"
              >
                <h3 className="text-xl font-bold mb-2">{item.name}</h3>
                <p>{item.specialty}</p>
                <p className="text-clarity-muted my-3">{item.address}</p>
                {item.distance_km != null && <p>{item.distance_km} km</p>}
                <div className="flex flex-wrap gap-3 mt-5">
                  <Button variant="secondary" onClick={() => openProfile(item)}>
                    {c[1]}
                  </Button>
                  {item.source !== "demo_synthetic" && (
                    <Button
                      onClick={() => {
                        openProfile(item);
                        setConsulting(true);
                      }}
                    >
                      {c[0]}
                    </Button>
                  )}
                </div>
                {(item.attributions || []).map((attribution, index) => (
                  <p key={index} className="text-sm text-clarity-muted">
                    {safeLink(attribution.providerUri) ? (
                      <a
                        href={attribution.providerUri}
                        target="_blank"
                        rel="noopener noreferrer"
                        referrerPolicy="no-referrer"
                      >
                        {attribution.provider || attribution.displayName}
                      </a>
                    ) : (
                      attribution.provider || attribution.displayName
                    )}
                  </p>
                ))}
              </article>
            ))}
          </div>
          {data &&
            !data.location_required &&
            !loading &&
            !data.providers?.length && <p className="py-8">{c[23]}</p>}
          <div className="mt-8 border-t pt-5">
            <h3 className="font-bold text-lg">{c[32]}</h3>
            <p className="text-clarity-muted mt-2">{c[33]}</p>
          </div>
        </>
      )}
      {provider && (
        <div
          className="fixed inset-0 z-50 bg-clarity-charcoal/50 p-4 flex items-center justify-center"
          ref={dialogRef}
          role="dialog"
          aria-modal="true"
          aria-label={c[1]}
        >
          <div className="bg-white rounded-3xl max-w-2xl w-full p-5 sm:p-8 max-h-[90dvh] overflow-y-auto">
            <div className="flex justify-between items-start gap-3">
              <h2 className="font-bold text-2xl">{provider.name}</h2>
              <Button variant="ghost" onClick={() => setProvider(null)}>
                {c[18]}
              </Button>
            </div>
            <p className="mt-3">{provider.specialty}</p>
            <p className="text-clarity-muted mt-2">{provider.address}</p>
            <p className="text-sm text-clarity-muted my-4">{c[5]}</p>
            {provider.opening_hours?.map((day) => (
              <p key={day} className="text-sm">
                {day}
              </p>
            ))}
            <div className="flex flex-wrap gap-4 my-5">
              {[
                [provider.maps_url, c[15]],
                [provider.directions_url, t.getDirections],
                [provider.website, c[16]],
              ]
                .filter(([url]) => safeLink(url))
                .map(([url, label]) => (
                  <a
                    key={label}
                    className="underline text-clarity-teal py-3"
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    referrerPolicy="no-referrer"
                  >
                    {label}
                  </a>
                ))}
            </div>
            {!consulting && provider.source !== "demo_synthetic" && (
              <Button onClick={() => setConsulting(true)}>{c[0]}</Button>
            )}
            {provider.source === "demo_synthetic" && (
              <p className="text-amber-900">{c[29]}</p>
            )}
            {consulting && (
              <>
                <h3 className="font-bold text-xl mt-6 mb-3">{c[2]}</h3>
                <p className="mb-3">{c[31]}</p>
                {options.length ? (
                  <div className="flex flex-wrap gap-3">
                    {options.map((option) => (
                      <a
                        key={option.type}
                        href={option.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        referrerPolicy="no-referrer"
                        className="border border-clarity-border rounded-xl p-4 text-clarity-teal font-semibold"
                      >
                        {optionLabels[option.type] || c[3]}
                      </a>
                    ))}
                  </div>
                ) : (
                  <p>{c[13]}</p>
                )}
                <p className="bg-clarity-mint rounded-xl p-4 mt-4">{c[4]}</p>
                <h3 className="text-xl font-bold mt-8 mb-3">{c[6]}</h3>
                <label className="block mb-4">
                  {c[7]}
                  <select
                    value={selectedReport}
                    onChange={(event) => {
                      setConsent(false);
                      setPreparation(null);
                      setSelectedReport(event.target.value);
                    }}
                    className="block w-full border rounded-xl p-3 mt-2"
                  >
                    <option value={reportId}>{reportId}</option>
                    {reports
                      .filter((item) => item.id !== reportId)
                      .map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.filename}
                        </option>
                      ))}
                  </select>
                </label>
                {preparation && (
                  <>
                    <h4 className="font-bold mt-5 mb-2">{c[8]}</h4>
                    <ul className="list-disc pl-5 space-y-2">
                      {preparation.findings.map((item, index) => (
                        <li key={index}>
                          {item.name}: {item.value} ({item.status});{" "}
                          {item.reference_range}
                        </li>
                      ))}
                    </ul>
                    <h4 className="font-bold mt-5 mb-2">{c[9]}</h4>
                    <ul className="list-disc pl-5 space-y-2">
                      {preparation.questions.map((question) => (
                        <li key={question}>{question}</li>
                      ))}
                    </ul>
                  </>
                )}
                <label className="flex gap-3 items-start mt-6">
                  <input
                    type="checkbox"
                    checked={consent}
                    onChange={(event) => setConsent(event.target.checked)}
                    className="shrink-0"
                  />
                  {c[10]}
                </label>
                <Button
                  className="w-full mt-4"
                  onClick={download}
                  disabled={!consent || !preparation || exporting}
                >
                  {c[11]}
                </Button>
                <p className="text-sm text-clarity-muted mt-4">{c[12]}</p>
              </>
            )}
            {error && (
              <p role="alert" className="text-red-900 mt-4">
                {error}
              </p>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
