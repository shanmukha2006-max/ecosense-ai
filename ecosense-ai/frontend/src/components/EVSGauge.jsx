import React, { useEffect, useMemo, useState } from 'react';

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function scoreColor(score) {
  if (score >= 75) return '#22c55e';
  if (score >= 55) return '#f59e0b';
  if (score >= 35) return '#ef4444';
  return '#7f1d1d';
}

function arcPath(cx, cy, r, startAngle, endAngle) {
  const rad = (deg) => (deg * Math.PI) / 180;
  const x1 = cx + r * Math.cos(rad(startAngle));
  const y1 = cy + r * Math.sin(rad(startAngle));
  const x2 = cx + r * Math.cos(rad(endAngle));
  const y2 = cy + r * Math.sin(rad(endAngle));
  const largeArc = endAngle - startAngle <= 180 ? 0 : 1;
  return `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`;
}

export default function EVSGauge({ evs }) {
  const score = evs?.evs_score ?? 0;
  const physical = evs?.physical_score ?? 0;
  const chemical = evs?.chemical_score ?? 0;
  const biological = evs?.biological_score ?? 0;
  const compoundActive = !!evs?.compound_active;
  const compoundCount = evs?.compound_count ?? 0;
  const trend = evs?.trend ?? 0;

  const [animScore, setAnimScore] = useState(0);
  useEffect(() => {
    let raf = 0;
    const start = performance.now();
    const from = animScore;
    const to = score;
    const duration = 700;
    const tick = (t) => {
      const p = Math.min(1, (t - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      setAnimScore(lerp(from, to, eased));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [score]);

  const color = scoreColor(score);
  const cx = 120;
  const cy = 120;
  const r = 90;
  const startAngle = 180;
  const endAngle = 0;
  const sweep = 180 - (animScore / 100) * 180;

  const trendSymbol = trend > 0.5 ? '↑' : trend < -0.5 ? '↓' : '→';

  return (
    <div className="flex flex-col gap-3">
      {compoundActive ? (
        <div className="px-3 py-2 rounded-[12px] border border-red-500/40 bg-red-500/10 text-red-200 text-xs">
          Compound stress active ({compoundCount}) — cascading risk elevated.
        </div>
      ) : null}

      <div className="flex gap-4 items-center">
        <svg width="240" height="140" viewBox="0 0 240 140">
          <path
            d={arcPath(cx, cy, r, startAngle, endAngle)}
            stroke="rgba(6,182,212,0.18)"
            strokeWidth="14"
            fill="none"
            strokeLinecap="round"
          />
          <path
            d={arcPath(cx, cy, r, startAngle, sweep)}
            stroke={color}
            strokeWidth="14"
            fill="none"
            strokeLinecap="round"
          />
          <text
            x={cx}
            y={cy}
            textAnchor="middle"
            dominantBaseline="middle"
            fill="#e6f7ff"
            fontSize="34"
            fontWeight="700"
          >
            {Math.round(score)}
          </text>
          <text
            x={cx}
            y={cy + 28}
            textAnchor="middle"
            dominantBaseline="middle"
            fill="rgba(230,247,255,0.75)"
            fontSize="12"
          >
            EVS {trendSymbol}
          </text>
        </svg>

        <div className="flex-1 flex flex-col gap-2">
          <ScoreBar label="Physical" value={physical} />
          <ScoreBar label="Chemical" value={chemical} />
          <ScoreBar label="Biological" value={biological} />
        </div>
      </div>
    </div>
  );
}

function ScoreBar({ label, value }) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div>
      <div className="flex justify-between text-[11px] text-cyan-100/70 mb-1">
        <span>{label}</span>
        <span>{Math.round(v)}</span>
      </div>
      <div className="h-2 rounded-full bg-cyan-500/10 border border-cyan-500/20 overflow-hidden">
        <div
          className="h-full"
          style={{
            width: `${v}%`,
            background: scoreColor(v),
          }}
        />
      </div>
    </div>
  );
}

