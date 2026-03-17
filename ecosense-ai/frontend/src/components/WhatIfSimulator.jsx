import React from 'react';

export default function WhatIfSimulator({
  values,
  onChange,
  originalEvs,
  simulatedEvs,
  compoundActive,
}) {
  const sliders = [
    { key: 'sst', label: 'SST Δ (°C)', min: -2.0, max: 4.0, step: 0.1 },
    { key: 'ph', label: 'pH Δ', min: -0.4, max: 0.1, step: 0.01 },
    { key: 'do', label: 'DO Δ (mg/L)', min: -4.0, max: 2.0, step: 0.1 },
    { key: 'bio', label: 'Biodiversity Δ', min: -80, max: 20, step: 1 },
    { key: 'poll', label: 'Pollution Δ (%)', min: -50, max: 200, step: 5 },
  ];

  const presets = [
    { label: 'Marine heatwave', sst: 2.5, ph: -0.15, do: -1.5, bio: -40, poll: 40 },
    { label: 'Eutrophication', sst: 0.5, ph: -0.05, do: -3.0, bio: -30, poll: 120 },
    { label: 'Bleaching pulse', sst: 3.0, ph: -0.1, do: -1.0, bio: -60, poll: 20 },
    { label: 'Mitigation', sst: -0.5, ph: 0.05, do: 1.0, bio: 10, poll: -40 },
    { label: 'Storm mixing', sst: -1.0, ph: 0.02, do: 0.5, bio: 0, poll: 10 },
    { label: 'Chronic stress', sst: 1.0, ph: -0.08, do: -2.0, bio: -30, poll: 80 },
  ];

  const delta = simulatedEvs && originalEvs
    ? simulatedEvs.evs_score - originalEvs.evs_score
    : 0;
  const deltaColor = delta >= 0 ? 'bg-emerald-600/80' : 'bg-red-600/80';

  return (
    <div className="flex flex-col gap-4 text-xs text-cyan-100/80">
      <div className="grid grid-cols-5 gap-3">
        {sliders.map((s) => (
          <div key={s.key} className="flex flex-col gap-1">
            <div className="flex items-center justify-between">
              <span>{s.label}</span>
              <span className="text-cyan-200">
                {values[s.key].toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min={s.min}
              max={s.max}
              step={s.step}
              value={values[s.key]}
              onChange={(e) =>
                onChange({ ...values, [s.key]: parseFloat(e.target.value) })
              }
              className="w-full accent-cyan-400"
            />
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-3">
        {presets.map((p) => (
          <button
            key={p.label}
            onClick={() => onChange(p)}
            className="card px-3 py-2 text-[11px] text-left hover:border-cyan-400/60"
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-4 mt-2">
        <div className="card flex-1 px-3 py-2">
          <div className="text-[11px] text-cyan-100/60">Original EVS</div>
          <div className="text-lg text-cyan-100 font-semibold">
            {originalEvs ? Math.round(originalEvs.evs_score) : '—'}
          </div>
        </div>
        <div className="card flex-1 px-3 py-2">
          <div className="text-[11px] text-cyan-100/60">Simulated EVS</div>
          <div className="text-lg text-cyan-100 font-semibold">
            {simulatedEvs ? Math.round(simulatedEvs.evs_score) : '—'}
          </div>
        </div>
        <div className="card px-3 py-2">
          <div className="text-[11px] text-cyan-100/60">Delta</div>
          <div
            className={`inline-flex items-center px-2 py-1 rounded-full text-[11px] ${deltaColor}`}
          >
            {delta >= 0 ? '+' : ''}
            {delta.toFixed(1)}
          </div>
        </div>
      </div>

      {compoundActive ? (
        <div className="px-3 py-2 rounded-[12px] border border-red-500/40 bg-red-500/10 text-red-200 text-xs">
          3+ anomalies in stress zone — simulated compound stress banner would be active.
        </div>
      ) : null}
    </div>
  );
}

