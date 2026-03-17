from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict
import csv

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from data.synthetic_generator import REGIONS, CACHE_DIR
from data.feature_engineer import feature_engineer
from models.eco_reading import UnifiedEcoReading
from models.evs_score import calculate_evs_score
from models.cascade_engine import get_active_cascades
from models.new_features import (
    calculate_carbon,
    calculate_insurance,
    score_sdgs,
)


class SimulationRequest(BaseModel):
    region_id: str
    sst_delta: float = 0.0
    ph_delta: float = 0.0
    do_delta: float = 0.0
    bio_delta: float = 0.0
    poll_delta: float = 0.0


router = APIRouter(prefix="/simulate", tags=["simulate"])


def _baseline_reading(region_id: str) -> UnifiedEcoReading:
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


@router.post("")
def run_simulation(payload: SimulationRequest) -> Dict[str, Any]:
    if payload.region_id not in REGIONS:
        raise HTTPException(status_code=404, detail="Region not found")

    base = _baseline_reading(payload.region_id)
    base_evs = calculate_evs_score(base)

    sim = deepcopy(base)
    sim.sst += payload.sst_delta
    sim.sst_anomaly += payload.sst_delta
    sim.ph += payload.ph_delta
    sim.dissolved_oxygen += payload.do_delta
    sim.species_richness += payload.bio_delta
    sim.nitrogen_load += payload.poll_delta

    sim = feature_engineer(sim)
    sim_evs = calculate_evs_score(sim)

    meta = REGIONS[payload.region_id]
    new_cascades = get_active_cascades(sim)
    new_sdgs = score_sdgs(sim_evs)
    new_carbon = calculate_carbon(
        payload.region_id, meta["ecosystem_type"], sim_evs["evs_score"]
    )
    new_insurance = calculate_insurance(sim_evs["evs_score"])

    return {
        "region_id": payload.region_id,
        "original_evs": base_evs,
        "simulated_evs": sim_evs,
        "delta": sim_evs["evs_score"] - base_evs["evs_score"],
        "new_cascade": new_cascades,
        "new_sdgs": new_sdgs,
        "new_carbon": new_carbon,
        "new_insurance": new_insurance,
        "compound_active": sim_evs["compound_active"],
    }

