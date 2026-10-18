import React, { useState } from "react";
import { apiFetch } from "../../api";
import { Button } from "../common/WarmUI";

const COPY = {
  en: [
    "Check uncertain readings",
    "Compare each reading with the original report. Unverified readings stay excluded from interpretation.",
    "Original report",
    "Printed source text",
    "Reading",
    "Save reading",
    "Cannot verify — keep excluded",
    "Continue to questions",
    "Back",
    "The reading was not saved. Please try again.",
    "Saved",
    "Source file is available only during this upload. The printed source text is shown below.",
    "Page",
    "Reference interval",
    "Source",
  ],
  hi: [
    "अस्पष्ट माप जाँचें",
    "हर माप मूल रिपोर्ट से मिलाएँ। अपुष्ट माप व्याख्या में शामिल नहीं होते।",
    "मूल रिपोर्ट",
    "रिपोर्ट में छपा पाठ",
    "माप",
    "माप सहेजें",
    "पुष्टि नहीं कर सकते — अलग रखें",
    "प्रश्नों पर जाएँ",
    "वापस",
    "माप सहेजा नहीं गया। फिर कोशिश करें।",
    "सहेजा गया",
    "मूल फ़ाइल केवल इस अपलोड के दौरान उपलब्ध है। छपा पाठ नीचे है।",
    "पृष्ठ",
    "संदर्भ सीमा",
    "स्रोत",
  ],
  mr: [
    "अस्पष्ट मोजमाप तपासा",
    "प्रत्येक मोजमाप मूळ अहवालाशी जुळवा. अपुष्ट मोजमाप विश्लेषणात समाविष्ट होत नाहीत.",
    "मूळ अहवाल",
    "अहवालातील छापील मजकूर",
    "मोजमाप",
    "मोजमाप जतन करा",
    "पुष्टी करता येत नाही — वगळा",
    "प्रश्नांकडे जा",
    "मागे",
    "मोजमाप जतन झाले नाही. पुन्हा प्रयत्न करा.",
    "जतन झाले",
    "मूळ फाइल फक्त या अपलोडदरम्यान उपलब्ध आहे. छापील मजकूर खाली आहे.",
    "पान",
    "संदर्भ मर्यादा",
    "स्रोत",
  ],
};
export function VerificationScreen({
  biomarkers = [],
  reportId,
  language = "en",
  sourcePreviews = [],
  onConfirmAll,
  onBack,
}) {
  const c = COPY[language] || COPY.en;
  const [items, setItems] = useState(biomarkers),
    [index, setIndex] = useState(0),
    [value, setValue] = useState(biomarkers[0]?.value || ""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(false),
    [saved, setSaved] = useState(false);
  const item = items[index];
  const source =
    sourcePreviews.length > 1
      ? sourcePreviews[(item?.source_page || 1) - 1]
      : sourcePreviews[0];
  function choose(next) {
    setIndex(next);
    setValue(items[next]?.value || "");
    setSaved(false);
    setError(false);
  }
  async function save() {
    setBusy(true);
    setError(false);
    setSaved(false);
    try {
      const response = await apiFetch(
        `/api/v1/reports/${reportId}/verify?lang=${language}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            biomarker_id: item.id,
            corrected_value: value,
          }),
        },
      );
      if (!response.ok) throw new Error();
      const data = await response.json();
      setItems((current) =>
        current.map((entry) =>
          entry.id === item.id ? data.updated_biomarker : entry,
        ),
      );
      setSaved(true);
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="max-w-6xl mx-auto px-5 py-10">
      <h1 className="mb-4">{c[0]}</h1>
      <p className="mb-6 text-clarity-muted">{c[1]}</p>
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-3xl p-5 border border-clarity-border">
          <h2 className="text-xl font-bold mb-4">{c[2]}</h2>
          {source ? (
            source.type === "application/pdf" ? (
              <iframe
                title={c[2]}
                src={`${source.url}#page=${item?.source_page || 1}`}
                className="w-full h-[55vh] rounded-xl"
              />
            ) : (
              <img
                src={source.url}
                alt={c[2]}
                className="max-h-[55vh] w-full object-contain"
              />
            )
          ) : (
            <p>{c[11]}</p>
          )}
          <p className="font-semibold mt-4">
            {c[3]} · {c[12]} {item?.source_page || "—"}
          </p>
          <p className="break-words mt-2">{item?.source_line || "—"}</p>
        </div>
        <div className="bg-white rounded-3xl p-5 border border-clarity-border">
          <div className="flex flex-wrap gap-2 mb-6">
            {items.map((entry, i) => (
              <Button
                key={entry.id}
                size="sm"
                variant={i === index ? "primary" : "secondary"}
                onClick={() => choose(i)}
                aria-pressed={i === index}
              >
                {i + 1}
                {entry.requires_verification ? " ?" : ""}
              </Button>
            ))}
          </div>
          {item && (
            <>
              <h2 className="font-bold text-xl mb-4">{item.name}</h2>
              <p>
                {c[13]}: {item.reference_range || "—"}
              </p>
              <label className="block mt-5">
                {c[4]} ({item.unit})
                <input
                  value={value}
                  onChange={(event) => setValue(event.target.value)}
                  maxLength={100}
                  className="block border rounded-xl p-3 mt-2 w-full"
                />
              </label>
              <div className="flex flex-wrap gap-3 mt-5">
                <Button disabled={busy || !value.trim()} onClick={save}>
                  {c[5]}
                </Button>
                <Button
                  variant="secondary"
                  disabled={busy}
                  onClick={() =>
                    index < items.length - 1
                      ? choose(index + 1)
                      : onConfirmAll(items)
                  }
                >
                  {c[6]}
                </Button>
              </div>
            </>
          )}
          {error && (
            <p role="alert" className="text-red-900 mt-4">
              {c[9]}
            </p>
          )}
          {saved && (
            <p role="status" className="text-clarity-teal mt-4">
              {c[10]}
            </p>
          )}
        </div>
      </div>
      <div className="flex flex-wrap justify-between gap-3 mt-6">
        <Button variant="secondary" onClick={onBack}>
          {c[8]}
        </Button>
        <Button disabled={busy} onClick={() => onConfirmAll(items)}>
          {c[7]}
        </Button>
      </div>
    </section>
  );
}
