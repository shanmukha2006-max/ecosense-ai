from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Callable, Dict, List, Tuple

from apscheduler.schedulers.background import BackgroundScheduler

from .evs_score import calculate_evs_score

CHANGES_LOG: List[Dict[str, Any]] = []
SCHEDULER: BackgroundScheduler | None = None


def calculate_carbon(region_id: str, ecosystem_type: str, evs_score: float) -> Dict[str, float]:
    rates = {
        "coral_reef": 0.8,
        "seagrass": 6.4,
        "mangrove": 6.9,
        "open_ocean": 0.2,
        "polar": 0.1,
    }
    rate = rates.get(ecosystem_type, 0.2)
    carbon_price = 68.0

    health_factor = max(0.0, min(1.0, evs_score / 100.0))
    annual_sequestration_tonnes = rate * 1000.0 * health_factor

    annual_credit_value_usd = annual_sequestration_tonnes * carbon_price
    monthly_credit_value_usd = annual_credit_value_usd / 12.0

    baseline_factor = 0.85
    degraded_factor = 1.0 - health_factor
    monthly_loss_usd = monthly_credit_value_usd * degraded_factor * baseline_factor

    discount_rate = 0.05
    years = 30
    npv_loss = 0.0
    annual_loss = monthly_loss_usd * 12.0
    for t in range(1, years + 1):
        npv_loss += annual_loss / ((1 + discount_rate) ** t)

    return {
        "annual_sequestration_tonnes": annual_sequestration_tonnes,
        "monthly_credit_value_usd": monthly_credit_value_usd,
        "monthly_loss_usd": monthly_loss_usd,
        "30yr_npv_loss_usd": npv_loss,
    }


def calculate_insurance(evs_score: float, volatility: float = 5.0) -> Dict[str, Any]:
    risk_component = ((100.0 - evs_score) / 100.0) ** 1.8
    base_premium = risk_component * 100000.0
    premium = base_premium * (1.0 + volatility * 0.05) * (1.0 - 0.4 * 0.4)

    if evs_score >= 75:
        rating = "AAA"
    elif evs_score >= 65:
        rating = "AA"
    elif evs_score >= 55:
        rating = "A"
    elif evs_score >= 45:
        rating = "BBB"
    elif evs_score >= 35:
        rating = "BB"
    elif evs_score >= 25:
        rating = "B"
    else:
        rating = "CCC"

    trigger_threshold_evs = max(0.0, min(100.0, evs_score - 5.0))

    return {
        "annual_premium_per_1m_usd": premium,
        "credit_rating": rating,
        "trigger_threshold_evs": trigger_threshold_evs,
    }


def score_sdgs(evs_data: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    sdg14 = evs_data.get("biological_score", 0.0)
    sdg13 = evs_data.get("physical_score", 0.0)
    sdg2 = evs_data.get("chemical_score", 0.0)
    sdg1 = evs_data.get("evs_score", 0.0)
    sdg6 = evs_data.get("chemical_score", 0.0)

    def classify(score: float) -> Tuple[str, str]:
        if score >= 75:
            return "on_track", "#22c55e"
        elif score >= 55:
            return "needs_acceleration", "#f59e0b"
        elif score >= 35:
            return "off_track", "#ef4444"
        else:
            return "critical", "#7f1d1d"

    sdgs = {}
    for name, score in [
        ("SDG14", sdg14),
        ("SDG13", sdg13),
        ("SDG2", sdg2),
        ("SDG1", sdg1),
        ("SDG6", sdg6),
    ]:
        status, color = classify(score)
        sdgs[name] = {"score": score, "status": status, "color": color}
    return sdgs


def _safe_claude_call(claude_client: Any, prompt: str) -> str:
    try:
        if claude_client is None:
            raise RuntimeError("No Claude client configured")
        response = claude_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=300,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        text = ""
        for block in response.content:
            if isinstance(block, dict) and block.get("type") == "text":
                text += block.get("text", "")
        return text or "EcoSense AI analysis indicates moderate risk with data-driven safeguards recommended."
    except Exception:
        return (
            "EcoSense AI analysis indicates escalating ecological stress with clear early-warning "
            "signals in physical, chemical, and biological indicators. Without rapid mitigation, "
            "critical thresholds may be crossed within the coming years. "
            "Recommended actions: Deploy targeted pollution and temperature management interventions; "
            "expand protected areas and strengthen monitoring coverage."
        )


def generate_passport(region_id: str, history: List[Dict[str, Any]], events: List[Dict[str, Any]], claude) -> Dict:
    recent = history[-1] if history else {}
    evs = recent.get("evs_score", 50.0)
    trend = recent.get("trend", 0.0)
    prompt = (
        f"You are EcoSense AI. Provide a 3-sentence clinical prognosis for region {region_id}. "
        f"Current EVS is {evs:.1f} with trend {trend:.1f} points. "
        "Use specific numbers from the context where possible, highlight tipping risks, "
        "and write in a precise, analytical tone."
    )
    prognosis = _safe_claude_call(claude, prompt)
    return {
        "region_id": region_id,
        "generated_at": datetime.utcnow().isoformat(),
        "history": history,
        "events": events,
        "prognosis": prognosis,
    }


def monitor_cycle(
    get_latest: Callable[[], Dict[str, Any]],
    get_cached: Callable[[], Dict[str, Any]],
    calc_evs: Callable[[Dict[str, Any]], Dict[str, Any]],
    ml: Any,
) -> None:
    latest = get_latest()
    cached = get_cached()

    current_evs = latest.get("evs_score")
    prev_evs = cached.get("evs_score")

    if current_evs is None:
        latest_evs = calc_evs(latest)
        current_evs = latest_evs.get("evs_score", 0.0)

    if prev_evs is None:
        prev_evs = current_evs

    delta = current_evs - prev_evs
    if abs(delta) >= 3.0:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "previous_evs": prev_evs,
            "current_evs": current_evs,
            "delta": delta,
        }
        CHANGES_LOG.append(entry)


def generate_morning_briefing(claude_client: Any) -> str:
    if not CHANGES_LOG:
        return "EcoSense AI analysis indicates no material EVS changes over the last NightWatch cycle."

    summary_lines = [
        f"{c['timestamp']}: EVS changed by {c['delta']:+.1f} points (from {c['previous_evs']:.1f} to {c['current_evs']:.1f})."
        for c in CHANGES_LOG[-10:]
    ]
    prompt = (
        "You are EcoSense AI environmental intelligence engine. "
        "Summarize the following EVS changes into a concise morning briefing for decision-makers. "
        "Lead with the most urgent change and end with exactly two concrete recommended actions.\n\n"
        + "\n".join(summary_lines)
    )
    return _safe_claude_call(claude_client, prompt)


def simulate_drift(
    source_lat: float,
    source_lon: float,
    current_u: float,
    current_v: float,
    days: int = 90,
) -> Dict[str, Any]:
    particles = []
    num_particles = 80
    for i in range(num_particles):
        lat = source_lat
        lon = source_lon
        snapshots = {}
        for day in [7, 30, 90]:
            t = min(day, days)
            lat_offset = current_v * t * 0.1 + math.sin(i * 0.3) * 0.05
            lon_offset = current_u * t * 0.1 + math.cos(i * 0.2) * 0.05
            snapshots[day] = {"lat": lat + lat_offset, "lon": lon + lon_offset}
        particles.append({"id": i, "snapshots": snapshots})
    return {"source": {"lat": source_lat, "lon": source_lon}, "particles": particles}


def find_weather_correlations(
    region_id: str,
    evs_history: List[Dict[str, Any]],
    weather_events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for evs_point in evs_history:
        t_evs = datetime.fromisoformat(evs_point["timestamp"])
        for event in weather_events:
            t_evt = datetime.fromisoformat(event["timestamp"])
            lag_days = (t_evs - t_evt).days
            if 14 <= abs(lag_days) <= 57:
                confidence = max(0.2, 1.0 - (abs(lag_days) - 14) / (57 - 14 + 1))
                matches.append(
                    {
                        "region_id": region_id,
                        "evs_time": evs_point["timestamp"],
                        "event_time": event["timestamp"],
                        "lag_days": lag_days,
                        "event_type": event.get("type", "weather_event"),
                        "confidence": confidence,
                    }
                )
    matches.sort(key=lambda m: abs(m["lag_days"]))
    return matches


def reef_acoustic_index(sst: float, species: float, do: float) -> Dict[str, Any]:
    temp_factor = max(0.0, 1.0 - max(0.0, sst - 27.0) * 0.08)
    species_factor = min(1.0, species / 300.0)
    oxygen_factor = min(1.0, do / 6.0)
    index = max(0.0, min(10.0, 10.0 * temp_factor * species_factor * oxygen_factor))

    if index > 7:
        sound_profile = "vibrant_reef"
    elif index >= 3:
        sound_profile = "stressed_reef"
    else:
        sound_profile = "degraded_reef"

    return {"index": index, "sound_profile": sound_profile}

