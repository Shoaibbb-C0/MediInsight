import React, { useEffect, useState } from "react";
import { Button } from "./components/common/WarmUI";
import { apiFetch } from "./api";
const LABELS = {
  en: [
    "Sign in to Simplifier",
    "Email",
    "Password",
    "Sign in",
    "Authentication configuration is unavailable. Please retry.",
    "Sign-in failed. Check your account details and try again.",
    "Sign-out could not be verified. Please retry.",
    "Loading your session…",
    "Retry",
  ],
  hi: [
    "Simplifier में साइन इन करें",
    "ईमेल",
    "पासवर्ड",
    "साइन इन",
    "प्रमाणीकरण सेवा उपलब्ध नहीं है। फिर कोशिश करें।",
    "साइन इन नहीं हुआ। खाता विवरण जाँचकर फिर कोशिश करें।",
    "साइन आउट की पुष्टि नहीं हुई। फिर कोशिश करें।",
    "सत्र लोड हो रहा है…",
    "फिर कोशिश करें",
  ],
  mr: [
    "Simplifier मध्ये साइन इन करा",
    "ईमेल",
    "पासवर्ड",
    "साइन इन",
    "प्रमाणीकरण सेवा उपलब्ध नाही. पुन्हा प्रयत्न करा.",
    "साइन इन झाले नाही. खात्याची माहिती तपासून पुन्हा प्रयत्न करा.",
    "साइन आउट निश्चित झाले नाही. पुन्हा प्रयत्न करा.",
    "सत्र लोड होत आहे…",
    "पुन्हा प्रयत्न करा",
  ],
};
export function AuthGate({ children }) {
  const [language, setLanguage] = useState("en"),
    [configuration, setConfiguration] = useState(null),
    [signedIn, setSignedIn] = useState(false),
    [revision, setRevision] = useState(0),
    [attempt, setAttempt] = useState(0);
  const [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [error, setError] = useState(null),
    [busy, setBusy] = useState(false);
  const c = LABELS[language];
  useEffect(() => {
    let active = true;
    setError(null);
    apiFetch("/api/v1/auth/configuration")
      .then(async (response) => {
        if (!response.ok) throw new Error();
        const config = await response.json();
        if (typeof config.sign_in_required !== "boolean") throw new Error();
        if (config.sign_in_required) {
          let response = await apiFetch("/api/v1/auth/session");
          if (response.status === 401) {
            const refreshed = await apiFetch("/api/v1/auth/refresh", {
              method: "POST",
            });
            if (refreshed.ok) response = await apiFetch("/api/v1/auth/session");
          }
          if (active) setSignedIn(response.ok);
        }
        if (active) setConfiguration(config);
      })
      .catch(() => {
        if (active) setError(4);
      });
    const expire = () => {
      setSignedIn(false);
      setRevision((value) => value + 1);
    };
    window.addEventListener("simplifier-session-expired", expire);
    return () => {
      active = false;
      window.removeEventListener("simplifier-session-expired", expire);
    };
  }, [attempt]);
  async function login(event) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const response = await apiFetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) throw new Error();
      setPassword("");
      setSignedIn(true);
      setRevision((value) => value + 1);
    } catch {
      setError(5);
    } finally {
      setBusy(false);
    }
  }
  async function logout() {
    try {
      const response = await apiFetch("/api/v1/auth/logout", {
        method: "POST",
      });
      if (!response.ok) throw new Error();
      setSignedIn(false);
      setRevision((value) => value + 1);
    } catch {
      setError(6);
    }
  }
  if (!configuration)
    return (
      <main className="max-w-md mx-auto p-6 py-16">
        {error !== null ? (
          <>
            <p role="alert">{c[error]}</p>
            <Button onClick={() => setAttempt((value) => value + 1)}>
              {c[8]}
            </Button>
          </>
        ) : (
          <p role="status">{c[7]}</p>
        )}
      </main>
    );
  if (configuration.sign_in_required && !signedIn)
    return (
      <main lang={language} className="max-w-md mx-auto p-6 py-16">
        <div className="flex gap-2 mb-6">
          {[
            ["en", "English"],
            ["hi", "हिंदी"],
            ["mr", "मराठी"],
          ].map(([code, label]) => (
            <button
              key={code}
              onClick={() => setLanguage(code)}
              aria-pressed={language === code}
              className="p-3 border rounded-xl"
            >
              {label}
            </button>
          ))}
        </div>
        <h1 className="text-3xl font-bold mb-6">{c[0]}</h1>
        <form onSubmit={login} className="space-y-5">
          <label className="block">
            {c[1]}
            <input
              type="email"
              autoComplete="username"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              className="block border rounded-xl p-3 w-full mt-2"
            />
          </label>
          <label className="block">
            {c[2]}
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              className="block border rounded-xl p-3 w-full mt-2"
            />
          </label>
          <Button type="submit" className="w-full" disabled={busy}>
            {c[3]}
          </Button>
        </form>
        {error !== null && (
          <p role="alert" className="text-red-900 mt-5">
            {c[error]}
          </p>
        )}
      </main>
    );
  return (
    <React.Fragment key={revision}>
      {error !== null && (
        <p role="alert" className="p-4 text-red-900">
          {c[error]}
        </p>
      )}
      {children(configuration.sign_in_required ? logout : null, language)}
    </React.Fragment>
  );
}
