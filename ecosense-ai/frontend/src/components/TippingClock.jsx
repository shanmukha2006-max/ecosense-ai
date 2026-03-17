import React from 'react';

export default function TippingClock({ days }) {
  let label = '';
  let color = '#22c55e';
  if (days === 0) {
    label = 'THRESHOLD PASSED';
    color = '#7f1d1d';
  } else if (days < 365) {
    label = 'CRITICAL';
    color = '#ef4444';
  } else if (days < 1000) {
    label = 'WATCH';
    color = '#f59e0b';
  } else {
    label = 'BUFFER';
    color = '#22c55e';
  }

  return (
    <div className="card px-4 py-3 flex items-center justify-between">
      <div>
        <div className="text-[11px] uppercase tracking-[0.25em] text-cyan-100/60">
          Days remaining
        </div>
        <div className="text-3xl font-semibold text-cyan-50">
          {days ?? '—'}
        </div>
      </div>
      <div className="text-right">
        <div
          className="px-3 py-1 rounded-full text-[11px] font-semibold"
          style={{ backgroundColor: `${color}33`, color }}
        >
          {label}
        </div>
      </div>
    </div>
  );
}

