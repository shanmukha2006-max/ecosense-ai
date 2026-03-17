from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List
import csv

from fastapi import APIRouter, HTTPException

from data.synthetic_generator import REGIONS, HISTORICAL_EVS, CACHE_DIR
from models.db import Alert, Annotation, get_session
from models.new_features import (
    calculate_carbon,
    calculate_insurance,
    score_sdgs,
    simulate_drift,
    find_weather_correlations,
    reef_acoustic_index,
)
from models.evs_score import calculate_evs_score
from data.feature_engineer import feature_engineer
from models.eco_reading import UnifiedEcoReading


router = APIRouter(prefix="", tags=["features"])


def _ensure_region(region_id: str):
    if region_id not in REGIONS:
        raise HTTPException(status_code=404, detail="Region not found")


def _latest_row(region_id: str) -> Dict[str, str]:
    csv_path = CACHE_DIR / f"{region_id}_synthetic.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=500, detail=f"No data for region {region_id}")
    last_row: Dict[str, str] | None = None
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            last_row = row
    if last_row is None:
        raise HTTPException(status_code=500, detail=f"No rows for region {region_id}")
    return last_row


def _reading_from_row(region_id: str, row: Dict[str, str]) -> UnifiedEcoReading:
    reading = UnifiedEcoReading(
        region_id=region_id,
        timestamp=datetime.fromisoformat(row["timestamp"]),
        latitude=float(row["latitude"]),
        longitude=float(row["longitude"]),
        ecosystem_type=row["ecosystem_type"],
        sst=float(row["sst"]),
        sst_anomaly=float(row["sst_anomaly"]),
        salinity=float(row["salinity"]),
        wave_height=float(row["wave_height"]),
        ph=float(row["ph"]),
        dissolved_oxygen=float(row["dissolved_oxygen"]),
        chlorophyll_a=float(row["chlorophyll_a"]),
        nitrogen_load=float(row["nitrogen_load"]),
        species_richness=float(row["species_richness"]),
        biodiversity_index=float(row["biodiversity_index"]),
    )
    return feature_engineer(reading)


@router.get("/history/{region_id}")
def history(region_id: str) -> Dict[str, Any]:
    _ensure_region(region_id)
    values = HISTORICAL_EVS[region_id]
    years = list(range(2015, 2015 + len(values)))
    return {"region_id": region_id, "years": years, "evs": values}


@router.get("/passport/{region_id}")
def passport(region_id: str) -> Dict[str, Any]:
    _ensure_region(region_id)
    values = HISTORICAL_EVS[region_id]
    years = list(range(2015, 2015 + len(values)))
    history = [
        {
            "timestamp": f"{y}-06-30T00:00:00",
            "evs_score": v,
            "trend": (v - values[0]) / max(1, (y - 2015)),
        }
        for y, v in zip(years, values)
    ]
    events: List[Dict[str, Any]] = []
    from ..models.new_features import generate_passport

    passport = generate_passport(region_id, history, events, claude=None)
    return passport


@router.get("/compare/{a}/{b}")
def compare_regions(a: str, b: str) -> Dict[str, Any]:
    _ensure_region(a)
    _ensure_region(b)
    return {"a": REGIONS[a], "b": REGIONS[b]}


@router.post("/annotations")
def create_annotation(payload: Dict[str, Any]) -> Dict[str, Any]:
    session = get_session()
    ann = Annotation(
        region_id=payload.get("region_id", "unknown"),
        source=payload.get("source", "unknown"),
        text=payload.get("text", ""),
        agrees_with_ai=payload.get("agrees_with_ai", True),
    )
    session.add(ann)
    session.commit()
    session.refresh(ann)
    return {"id": ann.id}


@router.get("/annotations/{region_id}")
def list_annotations(region_id: str) -> List[Dict[str, Any]]:
    session = get_session()
    rows = session.query(Annotation).filter(Annotation.region_id == region_id).all()
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "region_id": r.region_id,
            "source": r.source,
            "text": r.text,
            "agrees_with_ai": r.agrees_with_ai,
        }
        for r in rows
    ]


@router.get("/shap/{region_id}")
def shap_explanation(region_id: str) -> Dict[str, Any]:
    _ensure_region(region_id)
    row = _latest_row(region_id)
    reading = _reading_from_row(region_id, row)
    evs = calculate_evs_score(reading)
    features = {
        "sst": reading.sst,
        "sst_anomaly": reading.sst_anomaly,
        "ph": reading.ph,
        "dissolved_oxygen": reading.dissolved_oxygen,
        "nitrogen_load": reading.nitrogen_load,
        "species_richness": reading.species_richness,
    }
    contributions = {k: (evs["evs_score"] / len(features)) for k in features.keys()}
    return {"region_id": region_id, "features": features, "contributions": contributions}


@router.get("/vessels/{region_id}")
def vessels(region_id: str) -> Dict[str, Any]:
    _ensure_region(region_id)
    vessels = [
        {"id": "IMO1234567", "type": "container", "lat": REGIONS[region_id]["lat"], "lon": REGIONS[region_id]["lon"] + 0.3},
        {"id": "IMO7654321", "type": "tanker", "lat": REGIONS[region_id]["lat"] - 0.2, "lon": REGIONS[region_id]["lon"] - 0.4},
    ]
    return {"region_id": region_id, "vessels": vessels}


@router.get("/drift/{region_id}")
def drift(region_id: str) -> Dict[str, Any]:
    _ensure_region(region_id)
    meta = REGIONS[region_id]
    return simulate_drift(meta["lat"], meta["lon"], current_u=0.8, current_v=0.4)


@router.get("/sdg/{region_id}")
def sdg(region_id: str) -> Dict[str, Any]:
    _ensure_region(region_id)
    row = _latest_row(region_id)
    reading = _reading_from_row(region_id, row)
    evs = calculate_evs_score(reading)
    return score_sdgs(evs)


@router.get("/migration/{region_id}")
def migration(region_id: str) -> Dict[str, Any]:
    _ensure_region(region_id)
    return {
        "region_id": region_id,
        "routes": [
            {"species": "tuna", "from": "equator", "to": "poleward", "confidence": 0.82},
            {"species": "whale", "from": "breeding", "to": "feeding", "confidence": 0.76},
        ],
    }


@router.get("/carbon/{region_id}")
def carbon(region_id: str) -> Dict[str, Any]:
    _ensure_region(region_id)
    row = _latest_row(region_id)
    reading = _reading_from_row(region_id, row)
    evs = calculate_evs_score(reading)
    meta = REGIONS[region_id]
    return calculate_carbon(region_id, meta["ecosystem_type"], evs["evs_score"])


@router.get("/insurance/{region_id}")
def insurance(region_id: str) -> Dict[str, Any]:
    _ensure_region(region_id)
    row = _latest_row(region_id)
    reading = _reading_from_row(region_id, row)
    evs = calculate_evs_score(reading)
    return calculate_insurance(evs["evs_score"])


@router.get("/weather-correlations/{region_id}")
def weather_correlations(region_id: str) -> List[Dict[str, Any]]:
    _ensure_region(region_id)
    base_time = datetime.utcnow() - timedelta(days=400)
    evs_history = [
        {
            "timestamp": (base_time + timedelta(days=i * 30)).isoformat(),
            "evs_score": 80 - i * 3,
        }
        for i in range(10)
    ]
    weather_events = [
        {
            "timestamp": (base_time + timedelta(days=i * 37)).isoformat(),
            "type": "marine_heatwave" if i % 2 == 0 else "storm",
        }
        for i in range(8)
    ]
    return find_weather_correlations(region_id, evs_history, weather_events)


@router.get("/acoustic/{region_id}")
def acoustic(region_id: str) -> Dict[str, Any]:
    _ensure_region(region_id)
    row = _latest_row(region_id)
    reading = _reading_from_row(region_id, row)
    return reef_acoustic_index(
        reading.sst,
        reading.species_richness,
        reading.dissolved_oxygen,
    )


@router.get("/alerts")
def alerts() -> List[Dict[str, Any]]:
    session = get_session()
    rows = session.query(Alert).order_by(Alert.created_at.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "region_id": r.region_id,
            "severity": r.severity,
            "message": r.message,
        }
        for r in rows
    ]


@router.get("/health")
def eco_health() -> Dict[str, Any]:
    return {"status": "ok"}

