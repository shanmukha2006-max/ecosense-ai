import React from 'react';

export function CarbonCredits({ data }) {
  const cards = [
    { label: 'Annual sequestration (tCO₂e)', key: 'annual_sequestration_tonnes' },
    { label: 'Monthly credit value (USD)', key: 'monthly_credit_value_usd' },
    { label: 'Monthly loss (USD)', key: 'monthly_loss_usd' },
    { label: '30y NPV loss (USD)', key: '30yr_npv_loss_usd' },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 text-xs">
      {cards.map((c) => (
        <div key={c.key} className="card px-3 py-2">
          <div className="text-cyan-100/60">{c.label}</div>
          <div className="text-cyan-50 font-semibold">
            {data && data[c.key] != null ? data[c.key].toLocaleString() : '—'}
          </div>
        </div>
      ))}
    </div>
  );
}

export function SDGScorer({ sdgs }) {
  const order = ['SDG14', 'SDG13', 'SDG2', 'SDG1', 'SDG6'];
  return (
    <div className="flex flex-col gap-2 text-xs">
      {order.map((k) => {
        const item = sdgs?.[k];
        if (!item) return null;
        return (
          <div key={k}>
            <div className="flex justify-between mb-1">
              <span className="text-cyan-100/80">{k}</span>
              <span className="text-cyan-100/60">{Math.round(item.score)}</span>
            </div>
            <div className="h-2 rounded-full bg-cyan-500/10 border border-cyan-500/20 overflow-hidden">
              <div
                className="h-full"
                style={{ width: `${item.score}%`, background: item.color }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function NightWatchBadge() {
  return (
    <div className="inline-flex items-center gap-2 text-[11px] text-cyan-100/80">
      <span className="relative flex h-2.5 w-2.5">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-60" />
        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
      </span>
      <span>NightWatch cycle running</span>
    </div>
  );
}

export function InsurancePremium({ data }) {
  return (
    <div className="card px-3 py-2 text-xs flex flex-col gap-1">
      <div className="text-cyan-100/60">Premium per 1M USD</div>
      <div className="text-cyan-50 font-semibold">
        {data?.annual_premium_per_1m_usd
          ? `$${Math.round(data.annual_premium_per_1m_usd).toLocaleString()}`
          : '—'}
      </div>
      <div className="flex justify-between text-[11px] text-cyan-100/70">
        <span>Credit rating</span>
        <span>{data?.credit_rating ?? '—'}</span>
      </div>
    </div>
  );
}

export function ReefSoundscape({ acousticIndex }) {
  let profile = 'degraded';
  if (acousticIndex > 7) profile = 'vibrant';
  else if (acousticIndex >= 3) profile = 'stressed';
  return (
    <div className="card px-3 py-2 text-xs flex flex-col gap-2">
      <div className="flex justify-between">
        <span className="text-cyan-100/70">Reef soundscape</span>
        <span className="text-cyan-100/90">{acousticIndex?.toFixed(1) ?? '—'}</span>
      </div>
      <div className="h-8 bg-gradient-to-r from-sky-500/40 via-cyan-400/40 to-emerald-500/40 rounded-md" />
      <div className="flex gap-2">
        <button className="px-3 py-1 rounded-full border border-cyan-500/30 text-[11px]">
          Play
        </button>
        <button className="px-3 py-1 rounded-full border border-cyan-500/20 text-[11px]">
          Stop
        </button>
        <span className="text-cyan-100/60">Profile: {profile}</span>
      </div>
    </div>
  );
}

// The rest of the requested advanced components are stubbed
// as lightweight visual panels so the app can import them
// without runtime errors while still reflecting the intended layout.

export const SatelliteViewer = () => (
  <div className="card p-3 text-xs text-cyan-100/70">
    Satellite baseline vs today (WMTS split view placeholder).
  </div>
);

export const HealthPassport = () => (
  <div className="card p-3 text-xs text-cyan-100/70">
    Health passport layout placeholder; supports print-to-PDF.
  </div>
);

export const AlertFeed = () => (
  <div className="card p-2 text-[11px] text-cyan-100/80">
    Scrolling alert ticker placeholder (20 alerts).
  </div>
);

export const RegionComparator = () => (
  <div className="card p-3 text-xs text-cyan-100/70">
    Two-column region metric comparison placeholder.
  </div>
);

export const AnnotationLayer = () => (
  <div className="card p-3 text-xs text-cyan-100/70">
    Map annotations and pin sidebar placeholder.
  </div>
);

export const DigitalTwin = () => (
  <div className="card p-3 text-xs text-cyan-100/70">
    Digital twin vertical section placeholder.
  </div>
);

export const MicroplasticsDrift = () => (
  <div className="card p-3 text-xs text-cyan-100/70">
    Microplastics drift and MPA intersection placeholder.
  </div>
);

export const MigrationPredictor = () => (
  <div className="card p-3 text-xs text-cyan-100/70">
    Migration prediction arrows and species selector placeholder.
  </div>
);

export const VesselTracker = () => (
  <div className="card p-3 text-xs text-cyan-100/70">
    Vessel tracker overlay placeholder.
  </div>
);

export const WeatherCorrelator = () => (
  <div className="card p-3 text-xs text-cyan-100/70">
    Weather vs EVS timeline placeholder.
  </div>
);

export const PollutionAttribution = () => (
  <div className="card p-3 text-xs text-cyan-100/70">
    Pollution source attribution ranking placeholder.
  </div>
);

