import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function TimeMachine({ history = [], year, onYearChange }) {
  const years = history.map((h) => h.year);
  const minYear = years[0] ?? 2015;
  const maxYear = years[years.length - 1] ?? 2025;

  const marks = new Set([2015, 2016, 2019, 2020, 2022, 2023, 2025]);

  return (
    <div className="card p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between text-xs text-cyan-100/80">
        <span>EVS Time Machine (2015–2025)</span>
        <span className="text-cyan-100/60">Year: {year}</span>
      </div>
      <input
        type="range"
        min={minYear}
        max={maxYear}
        step={1}
        value={year}
        onChange={(e) => onYearChange(parseInt(e.target.value, 10))}
        className="w-full accent-cyan-400"
      />
      <div className="flex justify-between text-[10px] text-cyan-100/50">
        {Array.from({ length: maxYear - minYear + 1 }).map((_, i) => {
          const y = minYear + i;
          return (
            <span key={y} className={marks.has(y) ? 'text-cyan-200' : ''}>
              {y}
            </span>
          );
        })}
      </div>
      <div className="h-40">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={history}>
            <XAxis dataKey="year" stroke="#4b5563" fontSize={10} />
            <YAxis stroke="#4b5563" fontSize={10} domain={[0, 100]} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#020b18',
                borderRadius: 8,
                border: '1px solid rgba(148,163,184,0.4)',
                fontSize: 11,
              }}
            />
            <Line
              type="monotone"
              dataKey="evs"
              stroke="#06b6d4"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

