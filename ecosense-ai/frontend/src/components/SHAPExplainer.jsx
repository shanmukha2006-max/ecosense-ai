import React from 'react';

export default function SHAPExplainer({ shap }) {
  const items = shap?.features
    ? Object.entries(shap.features)
        .map(([name, value]) => ({
          name,
          value,
          contribution: shap.contributions?.[name] ?? 0,
        }))
        .sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution))
        .slice(0, 5)
    : [];

  return (
    <div className="flex flex-col gap-2">
      <div className="text-sm text-cyan-100 font-semibold mb-2">
        Why is this region stressed — AI explanation
      </div>
      {items.length === 0 ? (
        <div className="text-xs text-cyan-100/70">
          No SHAP-style breakdown available yet for this region.
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {items.map((it) => {
            const harmful = it.contribution < 0;
            const width = Math.min(100, Math.abs(it.contribution));
            const color = harmful ? '#ef4444' : '#22c55e';
            return (
              <div key={it.name} className="text-[11px]">
                <div className="flex justify-between mb-1">
                  <span className="text-cyan-100/80">{it.name}</span>
                  <span className="text-cyan-100/60">
                    {it.value.toFixed ? it.value.toFixed(2) : String(it.value)}
                  </span>
                </div>
                <div className="h-2 rounded-full bg-cyan-500/10 border border-cyan-500/20 overflow-hidden">
                  <div
                    className="h-full"
                    style={{
                      width: `${width}%`,
                      background: color,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

