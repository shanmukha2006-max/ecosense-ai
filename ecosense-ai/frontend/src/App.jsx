import { useState, useEffect } from "react";
import OceanMap from "./components/OceanMap";
import EVSGauge from "./components/EVSGauge";
import CascadeTimeline from "./components/CascadeTimeline";
import AICopilot from "./components/AICopilot";
import WhatIfSimulator from "./components/WhatIfSimulator";
import AlertFeed from "./components/AlertFeed";
import TippingClock from "./components/TippingClock";
import { api } from "./api/client";

export default function App() {
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [regionData, setRegionData] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(false);
  const [regions, setRegions] = useState([]);
  const [cycleCount, setCycleCount] = useState(0);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  useEffect(() => {
    api.getRegions()
      .then(data => setRegions(data))
      .catch(() => setRegions(getFallbackRegions()));
    const interval = setInterval(() => {
      setCycleCount(c => c + 1);
      setLastUpdated(new Date());
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleRegionSelect = async (region) => {
    setSelectedRegion(region);
    setLoading(true);
    try {
      const data = await api.getRegion(region.id);
      setRegionData(data);
    } catch {
      setRegionData(getFallbackRegionData(region));
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: "overview",      label: "Overview" },
    { id: "cascade",       label: "Cascade" },
    { id: "copilot",       label: "AI Copilot" },
    { id: "simulation",    label: "Simulation" },
    { id: "intelligence",  label: "Intelligence" },
    { id: "satellite",     label: "Satellite" },
    { id: "history",       label: "History" },
    { id: "advanced",      label: "Advanced" },
  ];

  return (
    <div style={{
      minHeight: "100vh",
      background: "#020b18",
      color: "#e2e8f0",
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      display: "flex",
      flexDirection: "column",
    }}>
      {/* HEADER */}
      <header style={{
        position: "sticky", top: 0, zIndex: 100,
        background: "rgba(2,11,24,0.95)",
        borderBottom: "1px solid rgba(6,182,212,0.15)",
        padding: "10px 20px",
        display: "flex", alignItems: "center", gap: 16,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 22 }}>🌊</span>
          <div>
            <div style={{ fontSize: 14, fontWeight: 800,
              color: "#fff", letterSpacing: "0.15em" }}>
              ECOSENSE AI
            </div>
            <div style={{ fontSize: 9, color: "#06b6d4",
              letterSpacing: "0.2em" }}>
              PSDO04 · OCEANOGRAPHIC INTELLIGENCE
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center",
          gap: 6, marginLeft: 20 }}>
          <div style={{
            width: 8, height: 8, borderRadius: "50%",
            background: "#22c55e",
            boxShadow: "0 0 6px #22c55e",
            animation: "pulse 2s infinite",
          }} />
          <span style={{ fontSize: 10, color: "#22c55e" }}>LIVE</span>
        </div>

        <div style={{ fontSize: 10, color: "#475569", marginLeft: 10 }}>
          NightWatch cycles: <span style={{ color: "#06b6d4" }}>{cycleCount}</span>
        </div>

        <div style={{ fontSize: 10, color: "#475569", marginLeft: 10 }}>
          Updated: <span style={{ color: "#94a3b8" }}>
            {lastUpdated.toLocaleTimeString()}
          </span>
        </div>

        <div style={{ marginLeft: "auto" }}>
          <span style={{
            fontSize: 10, padding: "3px 10px", borderRadius: 99,
            background: "rgba(6,182,212,0.1)",
            border: "1px solid rgba(6,182,212,0.3)",
            color: "#06b6d4",
          }}>
            DevsHouse 26 · D3
          </span>
        </div>
      </header>

      {/* MAIN LAYOUT */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* MAP — 40% */}
        <div style={{ width: "40%", position: "relative",
          borderRight: "1px solid rgba(6,182,212,0.1)" }}>
          <OceanMap
            regions={regions}
            selectedRegion={selectedRegion}
            onRegionSelect={handleRegionSelect}
          />
        </div>

        {/* DASHBOARD — 60% */}
        <div style={{ width: "60%", display: "flex",
          flexDirection: "column", overflow: "hidden" }}>
          {/* Tab bar */}
          <div style={{
            display: "flex", gap: 2, padding: "8px 12px",
            borderBottom: "1px solid rgba(6,182,212,0.1)",
            overflowX: "auto",
          }}>
            {tabs.map(t => (
              <button key={t.id} onClick={() => setActiveTab(t.id)}
                style={{
                  padding: "5px 12px", borderRadius: 6,
                  fontSize: 10, cursor: "pointer",
                  fontFamily: "inherit", whiteSpace: "nowrap",
                  background: activeTab === t.id
                    ? "rgba(6,182,212,0.15)" : "transparent",
                  border: activeTab === t.id
                    ? "1px solid rgba(6,182,212,0.4)"
                    : "1px solid transparent",
                  color: activeTab === t.id ? "#06b6d4" : "#475569",
                  transition: "all 0.15s",
                }}>
                {t.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div style={{ flex: 1, overflowY: "auto", padding: 16 }}>
            {loading && (
              <div style={{ textAlign: "center", color: "#06b6d4",
                padding: 40, fontSize: 12 }}>
                Loading region data...
              </div>
            )}

            {!loading && !selectedRegion && (
              <div style={{ textAlign: "center", color: "#475569",
                padding: 60, fontSize: 12 }}>
                <div style={{ fontSize: 32, marginBottom: 12 }}>🌊</div>
                Click any region on the map to begin analysis
              </div>
            )}

            {!loading && selectedRegion && regionData && (
              <>
                {activeTab === "overview" && (
                  <div style={{ display: "flex",
                    flexDirection: "column", gap: 14 }}>
                    <EVSGauge evs={regionData.evs} />
                    <TippingClock
                      days={selectedRegion.tipping_days
                        || regionData.evs?.tipping_days || 847} />
                  </div>
                )}
                {activeTab === "cascade" && (
                  <CascadeTimeline cascade={regionData.cascade || []} />
                )}
                {activeTab === "copilot" && (
                  <AICopilot regionId={selectedRegion.id}
                    regionData={regionData} />
                )}
                {activeTab === "simulation" && (
                  <WhatIfSimulator regionId={selectedRegion.id}
                    baselineEvs={regionData.evs?.evs_score} />
                )}
                {activeTab === "intelligence" && (
                  <div style={{ color: "#94a3b8", fontSize: 12 }}>
                    Carbon Credits, SDG Scorer and Insurance
                    panels load here.
                  </div>
                )}
                {activeTab === "satellite" && (
                  <div style={{ color: "#94a3b8", fontSize: 12 }}>
                    Satellite viewer loads here.
                  </div>
                )}
                {activeTab === "history" && (
                  <div style={{ color: "#94a3b8", fontSize: 12 }}>
                    Time Machine loads here.
                  </div>
                )}
                {activeTab === "advanced" && (
                  <div style={{ color: "#94a3b8", fontSize: 12 }}>
                    Digital Twin, Migration, Vessels load here.
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* FOOTER — Alert Feed */}
      <div style={{
        borderTop: "1px solid rgba(6,182,212,0.1)",
        padding: "6px 16px",
        display: "flex", alignItems: "center",
        gap: 16, background: "rgba(2,11,24,0.9)",
      }}>
        <span style={{ fontSize: 10, color: "#475569",
          whiteSpace: "nowrap" }}>ALERTS</span>
        <AlertFeed />
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
          background: rgba(6,182,212,0.3);
          border-radius: 2px;
        }
      `}</style>
    </div>
  );
}

function getFallbackRegions() {
  return [
    { id: "great_barrier_reef", name: "Great Barrier Reef (North)",
      lat: -16.5, lon: 145.8, current_evs: 31,
      status: "Critical", tipping_days: 847 },
    { id: "gulf_of_mexico", name: "Gulf of Mexico Dead Zone",
      lat: 29.0, lon: -90.0, current_evs: 24,
      status: "Collapse Risk", tipping_days: 0 },
    { id: "coral_triangle", name: "Coral Triangle",
      lat: 2.0, lon: 124.0, current_evs: 47,
      status: "Stressed", tipping_days: 2341 },
    { id: "bay_of_bengal", name: "Bay of Bengal",
      lat: 14.0, lon: 80.0, current_evs: 58,
      status: "Stressed", tipping_days: 4102 },
    { id: "arctic_shelf", name: "Arctic Shelf (Barents Sea)",
      lat: 73.0, lon: 25.0, current_evs: 38,
      status: "Critical", tipping_days: 1203 },
  ];
}

function getFallbackRegionData(region) {
  return {
    evs: {
      evs_score: region.current_evs,
      physical_score: region.current_evs + 5,
      chemical_score: region.current_evs - 3,
      biological_score: region.current_evs + 2,
      status: region.status,
      status_color: region.current_evs < 25 ? "#7f1d1d"
                  : region.current_evs < 50 ? "#ef4444"
                  : "#f59e0b",
      compound_active: false,
      tipping_days: region.tipping_days,
    },
    cascade: [],
    anomalies: { is_anomaly: false, shap_values: [] },
  };
}