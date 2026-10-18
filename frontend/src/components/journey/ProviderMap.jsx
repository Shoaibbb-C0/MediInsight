import React, { useEffect, useRef, useState } from "react";
import "maplibre-gl/dist/maplibre-gl.css";

const MAP_LOCALE = {
  hi: { "NavigationControl.ZoomIn": "ज़ूम बढ़ाएँ", "NavigationControl.ZoomOut": "ज़ूम घटाएँ", "NavigationControl.ResetBearing": "उत्तर दिशा पर लौटें", "AttributionControl.ToggleAttribution": "मानचित्र स्रोत दिखाएँ" },
  mr: { "NavigationControl.ZoomIn": "झूम वाढवा", "NavigationControl.ZoomOut": "झूम कमी करा", "NavigationControl.ResetBearing": "उत्तर दिशेला परत या", "AttributionControl.ToggleAttribution": "नकाशाचा स्रोत दाखवा" },
};
const COPY = {
  en: ["Nearby healthcare facilities map", "Map unavailable. Use the facility list and OpenStreetMap links.", "Loading map…", "Select facility"],
  hi: ["आसपास के स्वास्थ्य केंद्रों का मानचित्र", "मानचित्र उपलब्ध नहीं। केंद्रों की सूची और OpenStreetMap लिंक उपयोग करें।", "मानचित्र लोड हो रहा है…", "केंद्र चुनें"],
  mr: ["जवळील आरोग्य केंद्रांचा नकाशा", "नकाशा उपलब्ध नाही. केंद्रांची यादी आणि OpenStreetMap लिंक वापरा.", "नकाशा लोड होत आहे…", "केंद्र निवडा"],
};
export function ProviderMap({ providers, location, onSelect, selectedId, language = "en" }) {
  const root = useRef(null), mapRef = useRef(null), markersRef = useRef([]);
  const selectRef = useRef(onSelect);
  selectRef.current = onSelect;
  const [state, setState] = useState("loading");
  const c = COPY[language] || COPY.en;
  const lat = location?.coordinates?.lat, lng = location?.coordinates?.lng;
  useEffect(() => {
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;
    let cancelled = false, map, timer;
    setState("loading");
    async function start() {
      try {
        const { Map, Marker, NavigationControl, LngLatBounds, setWorkerUrl } = await import("maplibre-gl");
        const { default: workerUrl } = await import("maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url");
        if (cancelled) return;
        setWorkerUrl(workerUrl);
        map = new Map({ container: root.current, style: import.meta.env.VITE_OSM_MAP_STYLE_URL || "https://tiles.openfreemap.org/styles/liberty", center: [lng, lat], zoom: 12, locale: { "Map.Title": c[0], ...MAP_LOCALE[language] }, attributionControl: { compact: false } });
        mapRef.current = map;
        map.addControl(new NavigationControl({ visualizePitch: false }), "top-right");
        timer = setTimeout(() => { if (!cancelled) setState("error"); }, 20000);
        map.on("load", () => { clearTimeout(timer); if (!cancelled) setState("ready"); });
        map.on("error", () => { clearTimeout(timer); if (!cancelled) setState("error"); });
        const bounds = new LngLatBounds([lng, lat], [lng, lat]);
        markersRef.current = providers.filter(p => Number.isFinite(p.coordinates?.lat) && Number.isFinite(p.coordinates?.lng)).map(p => {
          const button = document.createElement("button");
          button.type = "button";
          button.textContent = "+";
          button.className = "provider-marker";
          button.dataset.providerId = p.id;
          button.setAttribute("aria-label", `${c[3]}: ${p.name}`);
          button.setAttribute("aria-pressed", "false");
          button.addEventListener("click", () => selectRef.current(p));
          const point = [p.coordinates.lng, p.coordinates.lat];
          bounds.extend(point);
          const marker = new Marker({ element: button }).setLngLat(point).addTo(map);
          return { marker, button, point, id: p.id };
        });
        if (markersRef.current.length) map.fitBounds(bounds, { padding: 48, maxZoom: 14, duration: 0 });
      } catch { if (!cancelled) setState("error"); }
    }
    start();
    return () => { cancelled = true; clearTimeout(timer); markersRef.current.forEach(({ marker }) => marker.remove()); markersRef.current = []; map?.remove(); mapRef.current = null; };
  }, [lat, lng, providers, language]);
  useEffect(() => {
    markersRef.current.forEach(({ button, point, id }) => {
      button.setAttribute("aria-pressed", String(id === selectedId));
      if (id === selectedId) mapRef.current?.easeTo({ center: point, duration: 0 });
    });
  }, [selectedId, state]);
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return <p className="p-5">{c[1]}</p>;
  return <section className="mb-5" aria-label={c[0]}>
    {state !== "ready" && <p role="status" className="p-4 bg-clarity-ivory rounded-xl">{state === "error" ? c[1] : c[2]}</p>}
    <div ref={root} className="h-80 w-full rounded-2xl" style={state === "error" ? { display: "none" } : undefined} />
  </section>;
}
