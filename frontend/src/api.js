let refreshPromise;
export async function apiFetch(url, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Accept-Language", document.documentElement.lang || "en");
  const request = { credentials: "same-origin", ...options, headers };
  let response = await fetch(url, request);
  if (response.status === 401 && !String(url).startsWith("/api/v1/auth/")) {
    refreshPromise ||= fetch("/api/v1/auth/refresh", {
      method: "POST",
      credentials: "same-origin",
    }).finally(() => {
      refreshPromise = undefined;
    });
    const refreshed = await refreshPromise;
    if (refreshed.ok) {
      response = await fetch(url, request);
      if(response.status === 401) window.dispatchEvent(new Event("simplifier-session-expired"));
    }
    else window.dispatchEvent(new Event("simplifier-session-expired"));
  }
  return response;
}
