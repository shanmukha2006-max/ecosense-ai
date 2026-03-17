import React, { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

function statusToColor(statusColor) {
  switch (statusColor) {
    case 'green':
      return '#22c55e';
    case 'amber':
      return '#f59e0b';
    case 'red':
      return '#ef4444';
    case 'critical':
      return '#7f1d1d';
    default:
      return '#06b6d4';
  }
}

export default function OceanMap({
  regions = [],
  selectedRegionId,
  onRegionSelect,
  overlays = { vessels: false, drift: false, annotations: false, migration: false },
  onToggleOverlay,
}) {
  const center = useMemo(() => [10, 20], []);

  return (
    <div className="h-full w-full relative">
      <div className="absolute top-3 left-3 z-[1000] flex gap-2">
        {['vessels', 'drift', 'annotations', 'migration'].map((k) => (
          <button
            key={k}
            onClick={() => onToggleOverlay?.(k)}
            className={`px-2 py-1 text-[11px] rounded-full border ${
              overlays[k]
                ? 'border-cyan-400 bg-cyan-500/10 text-cyan-200'
                : 'border-cyan-500/20 text-cyan-100/70 hover:border-cyan-400/60 hover:text-cyan-100'
            }`}
          >
            {k}
          </button>
        ))}
      </div>

      <MapContainer
        center={center}
        zoom={2}
        worldCopyJump
        className="h-full w-full rounded-[12px]"
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution="&copy; OpenStreetMap &copy; CARTO"
        />

        {regions.map((r) => {
          const evs = r?.evs?.evs_score ?? 0;
          const statusColor = r?.evs?.status_color;
          const color = statusToColor(statusColor);
          const radius = 20 + (100 - evs) / 5;
          const pulse = evs < 35;
          const isSelected = selectedRegionId === r.id;

          return (
            <CircleMarker
              key={r.id}
              center={[r.lat, r.lon]}
              radius={radius}
              pathOptions={{
                color: isSelected ? '#06b6d4' : color,
                weight: isSelected ? 3 : 2,
                fillColor: color,
                fillOpacity: 0.35,
              }}
              eventHandlers={{
                click: () => onRegionSelect?.(r.id),
              }}
            >
              <Tooltip direction="top" opacity={1}>
                <div className="text-xs">
                  <div className="font-semibold">{r.name}</div>
                  <div>EVS: {Math.round(evs)}</div>
                </div>
              </Tooltip>
            </CircleMarker>
          );
        })}
      </MapContainer>

      <style>{`
        .leaflet-container { background: #020b18; }
      `}</style>
    </div>
  );
}

