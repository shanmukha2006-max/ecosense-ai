import React, { useEffect, useMemo, useRef, useState } from 'react';
import { postReport } from '../api/client';

const MODES = ['Scientist', 'Policy', 'Community', 'Fisherman'];

export default function AICopilot({ regionId }) {
  const [mode, setMode] = useState(MODES[0]);
  const [loading, setLoading] = useState(false);
  const [fullText, setFullText] = useState('');
  const [shownText, setShownText] = useState('');
  const [lastGeneratedAt, setLastGeneratedAt] = useState(null);
  const timerRef = useRef(null);

  useEffect(() => {
    if (!fullText) return;
    setShownText('');
    if (timerRef.current) clearInterval(timerRef.current);
    let i = 0;
    timerRef.current = setInterval(() => {
      i += 1;
      setShownText(fullText.slice(0, i));
      if (i >= fullText.length) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }, 20);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      timerRef.current = null;
    };
  }, [fullText]);

  async function generate() {
    if (!regionId) return;
    setLoading(true);
    try {
      const res = await postReport({ region_id: regionId, audience: mode });
      setFullText(res.text || '');
      setLastGeneratedAt(new Date());
    } catch (e) {
      setFullText(`EcoSense AI analysis indicates report generation failed: ${String(e.message || e)}`);
      setLastGeneratedAt(new Date());
    } finally {
      setLoading(false);
    }
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(fullText || shownText || '');
    } catch {
      // ignore
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex gap-2 flex-wrap">
        {MODES.map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`px-3 py-1.5 rounded-full border text-[11px] tracking-wide ${
              mode === m
                ? 'border-cyan-400 bg-cyan-500/10 text-cyan-200'
                : 'border-cyan-500/20 text-cyan-100/70 hover:border-cyan-400/60 hover:text-cyan-100'
            }`}
          >
            {m}
          </button>
        ))}
      </div>

      <button
        onClick={generate}
        disabled={!regionId || loading}
        className="px-4 py-3 rounded-[12px] border border-cyan-400/40 bg-cyan-500/10 hover:bg-cyan-500/15 text-cyan-100 text-sm font-semibold disabled:opacity-50"
      >
        {loading ? 'Generating…' : 'Generate Report'}
      </button>

      <div className="card p-4 min-h-[220px]">
        {loading ? (
          <div className="text-cyan-100/80 text-sm">Generating…</div>
        ) : shownText ? (
          <div className="whitespace-pre-wrap text-sm leading-relaxed text-cyan-50">
            {shownText}
          </div>
        ) : (
          <div className="text-cyan-100/70 text-sm">
            Select a region and generate an audience-tuned report.
          </div>
        )}
      </div>

      <div className="flex items-center justify-between text-[11px] text-cyan-100/70">
        <div>
          Last generated:{' '}
          {lastGeneratedAt ? lastGeneratedAt.toLocaleString() : '—'}
        </div>
        <button
          onClick={copy}
          className="px-3 py-1 rounded-full border border-cyan-500/20 hover:border-cyan-400/60"
        >
          Copy
        </button>
      </div>
    </div>
  );
}

