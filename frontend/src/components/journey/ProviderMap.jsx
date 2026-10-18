import React, { useEffect, useRef, useState } from "react";
let loader;
function loadMaps(key) {
  if (window.google?.maps?.importLibrary)
    return Promise.resolve(window.google.maps);
  loader ||= new Promise((resolve, reject) => {
    const script = document.createElement("script");
    window.simplifierMapsReady = () => {
      delete window.simplifierMapsReady;
      resolve(window.google.maps);
    };
    script.src =
      "https://maps.googleapis.com/maps/api/js?" +
      new URLSearchParams({
        key,
        v: "quarterly",
        loading: "async",
        callback: "simplifierMapsReady",
      });
    script.async = true;
    script.onerror = () => {
      delete window.simplifierMapsReady;
      loader = undefined;
      script.remove();
      reject(new Error("Map failed"));
    };
    document.head.append(script);
  });
  return loader;
}
export function ProviderMap({
  providers,
  location,
  onSelect,
  language = "en",
}) {
  const root = useRef(null),
    [error, setError] = useState(false);
  const key = import.meta.env.VITE_GOOGLE_MAPS_BROWSER_KEY,
    mapId = import.meta.env.VITE_GOOGLE_MAPS_MAP_ID;
  const unavailable =
    language === "hi"
      ? "मानचित्र सेवा उपलब्ध नहीं है। डॉक्टर का Google Maps लिंक खोलें।"
      : language === "mr"
        ? "नकाशा सेवा उपलब्ध नाही. डॉक्टरांची Google Maps लिंक उघडा."
        : "Map service is unavailable. Open the provider’s Google Maps link.";
  useEffect(() => {
    let cancelled = false,
      markers = [];
    if (!key || !mapId || !location?.coordinates) return;
    loadMaps(key)
      .then(async (googleMaps) => {
        const { Map } = await googleMaps.importLibrary("maps"),
          { AdvancedMarkerElement } = await googleMaps.importLibrary("marker");
        if (cancelled) return;
        const map = new Map(root.current, {
          mapId,
          center: location.coordinates,
          zoom: 12,
        });
        const bounds = new googleMaps.LatLngBounds();
        providers
          .filter((provider) => provider.coordinates)
          .forEach((provider) => {
            const marker = new AdvancedMarkerElement({
              map,
              position: provider.coordinates,
              title: provider.name,
            });
            marker.addListener("click", () => onSelect(provider));
            markers.push(marker);
            bounds.extend(provider.coordinates);
          });
        if (markers.length) map.fitBounds(bounds, 40);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
      markers.forEach((marker) => {
        marker.map = null;
      });
    };
  }, [providers, location, key, mapId, onSelect]);
  if (!key || !mapId || !location?.coordinates || error)
    return (
      <p className="bg-clarity-ivory rounded-2xl p-5 mb-5">{unavailable}</p>
    );
  return (
    <div
      ref={root}
      role="region"
      aria-label="Google Maps provider locations"
      className="h-80 w-full rounded-2xl mb-5"
    />
  );
}
