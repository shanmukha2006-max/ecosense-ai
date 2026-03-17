const BASE = "http://localhost:8000/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status} ${path}: ${text}`);
  }
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return await res.json();
  return await res.text();
}

// Regions
export const getRegions = () => request("/regions");
export const getRegion = (id) => request(`/regions/${encodeURIComponent(id)}`);

// Reports / Copilot
export const postReport = ({ region_id, audience }) =>
  request("/reports/report", {
    method: "POST",
    body: JSON.stringify({ region_id, audience }),
  });
export const getMorningBriefing = () => request("/reports/morning-briefing");

// Simulation
export const postSimulate = (payload) =>
  request("/simulate", { method: "POST", body: JSON.stringify(payload) });

// Feature endpoints (16)
export const getHistory = (id) => request(`/history/${encodeURIComponent(id)}`);
export const getPassport = (id) => request(`/passport/${encodeURIComponent(id)}`);
export const getCompare = (a, b) =>
  request(`/compare/${encodeURIComponent(a)}/${encodeURIComponent(b)}`);
export const postAnnotation = (payload) =>
  request("/annotations", { method: "POST", body: JSON.stringify(payload) });
export const getAnnotations = (id) =>
  request(`/annotations/${encodeURIComponent(id)}`);
export const getShap = (id) => request(`/shap/${encodeURIComponent(id)}`);
export const getVessels = (id) => request(`/vessels/${encodeURIComponent(id)}`);
export const getDrift = (id) => request(`/drift/${encodeURIComponent(id)}`);
export const getSdg = (id) => request(`/sdg/${encodeURIComponent(id)}`);
export const getMigration = (id) =>
  request(`/migration/${encodeURIComponent(id)}`);
export const getCarbon = (id) => request(`/carbon/${encodeURIComponent(id)}`);
export const getInsurance = (id) =>
  request(`/insurance/${encodeURIComponent(id)}`);
export const getWeatherCorrelations = (id) =>
  request(`/weather-correlations/${encodeURIComponent(id)}`);
export const getAcoustic = (id) =>
  request(`/acoustic/${encodeURIComponent(id)}`);
export const getAlerts = () => request("/alerts");
export const getHealth = () => request("/health");

export { BASE };

