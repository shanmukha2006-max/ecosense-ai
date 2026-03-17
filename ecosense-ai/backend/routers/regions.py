from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List
import csv

from fastapi import APIRouter, HTTPException

from data.synthetic_generator import HISTORICAL_EVS, REGIONS, CACHE_DIR
from models.eco_reading import UnifiedEcoReading
from data.feature_engineer import feature_engineer
from models.evs_score import calculate_evs_score
from models.cascade_engine import get_active_cascades
from models.new_features import calculate_carbon, calculate_insurance, score_sdgs, reef_acoustic_index


router = APIRouter(prefix="/regions", tags=["regions"])


def _latest_reading(region_id: str) -> UnifiedEcoReading:
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

    reading = UnifiedEcoReading(
        region_id=region_id,
        timestamp=datetime.fromisoformat(last_row["timestamp"]),
        latitude=float(last_row["latitude"]),
        longitude=float(last_row["longitude"]),
        ecosystem_type=last_row["ecosystem_type"],
        sst=float(last_row["sst"]),
        sst_anomaly=float(last_row["sst_anomaly"]),
        salinity=float(last_row["salinity"]),
        wave_height=float(last_row["wave_height"]),
        ph=float(last_row["ph"]),
        dissolved_oxygen=float(last_row["dissolved_oxygen"]),
        chlorophyll_a=float(last_row["chlorophyll_a"]),
        nitrogen_load=float(last_row["nitrogen_load"]),
        species_richness=float(last_row["species_richness"]),
        biodiversity_index=float(last_row["biodiversity_index"]),
    )
    return feature_engineer(reading)


@router.get("")
def list_regions() -> List[Dict[str, Any]]:
    regions = []
    for rid, meta in REGIONS.items():
        reading = _latest_reading(rid)
        evs = calculate_evs_score(reading)
        acoustic = reef_acoustic_index(
            reading.sst,
            reading.species_richness,
            reading.dissolved_oxygen,
        )
        regions.append(
            {
                "id": rid,
                "name": meta["name"],
                "lat": meta["lat"],
                "lon": meta["lon"],
                "ecosystem_type": meta["ecosystem_type"],
                "baseline_evs": meta["baseline_evs"],
                "current_evs": meta["current_evs"],
                "tipping_days": meta["tipping_days"],
                "evs": evs,
                "acoustic": acoustic,
            }
        )
    return regions


@router.get("/{region_id}")
def get_region(region_id: str) -> Dict[str, Any]:
    if region_id not in REGIONS:
        raise HTTPException(status_code=404, detail="Region not found")

    meta = REGIONS[region_id]
    reading = _latest_reading(region_id)
    evs = calculate_evs_score(reading)
    cascades = get_active_cascades(reading)
    carbon = calculate_carbon(region_id, meta["ecosystem_type"], evs["evs_score"])
    insurance = calculate_insurance(evs["evs_score"])
    sdg_scores = score_sdgs(evs)
    acoustic = reef_acoustic_index(
        reading.sst,
        reading.species_richness,
        reading.dissolved_oxygen,
    )

    history = []
    hist_vals = HISTORICAL_EVS[region_id]
    year = 2015
    for value in hist_vals:
        history.append({"year": year, "evs": value})
        year += 1

    return {
        "id": region_id,
        "meta": meta,
        "reading": reading.__dict__,
        "evs": evs,
        "anomalies": {
            "sst_anomaly": reading.sst_anomaly,
            "compound_stress_count": reading.compound_stress_count,
        },
        "cascades": cascades,
        "carbon": carbon,
        "insurance": insurance,
        "sdg_scores": sdg_scores,
        "tipping_days": meta["tipping_days"],
        "acoustic": acoustic,
        "history": history,
    }

