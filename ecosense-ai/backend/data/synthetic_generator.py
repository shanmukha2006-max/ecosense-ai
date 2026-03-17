from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import csv
import random


BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

REGIONS: Dict[str, Dict] = {
    "great_barrier_reef": {
        "name": "Great Barrier Reef (North)",
        "lat": -16.5,
        "lon": 145.8,
        "area_km2": 344400,
        "ecosystem_type": "coral_reef",
        "baseline_evs": 81,
        "current_evs": 31,
        "tipping_days": 847,
    },
    "gulf_of_mexico": {
        "name": "Gulf of Mexico Dead Zone",
        "lat": 29.0,
        "lon": -90.0,
        "area_km2": 160000,
        "ecosystem_type": "open_ocean",
        "baseline_evs": 74,
        "current_evs": 24,
        "tipping_days": 0,
    },
    "coral_triangle": {
        "name": "Coral Triangle",
        "lat": 2.0,
        "lon": 124.0,
        "area_km2": 6000000,
        "ecosystem_type": "coral_reef",
        "baseline_evs": 79,
        "current_evs": 47,
        "tipping_days": 2341,
    },
    "bay_of_bengal": {
        "name": "Bay of Bengal",
        "lat": 14.0,
        "lon": 80.0,
        "area_km2": 2172000,
        "ecosystem_type": "open_ocean",
        "baseline_evs": 72,
        "current_evs": 58,
        "tipping_days": 4102,
    },
    "arctic_shelf": {
        "name": "Arctic Shelf (Barents Sea)",
        "lat": 73.0,
        "lon": 25.0,
        "area_km2": 1400000,
        "ecosystem_type": "polar",
        "baseline_evs": 69,
        "current_evs": 38,
        "tipping_days": 1203,
    },
}

HISTORICAL_EVS: Dict[str, List[int]] = {
    "great_barrier_reef": [81, 75, 64, 51, 58, 44, 41, 36, 35, 38, 31],
    "gulf_of_mexico": [74, 68, 62, 58, 55, 50, 42, 38, 30, 27, 24],
    "coral_triangle": [79, 75, 72, 68, 65, 62, 58, 55, 52, 49, 47],
    "bay_of_bengal": [72, 70, 68, 65, 63, 63, 62, 61, 60, 59, 58],
    "arctic_shelf": [69, 66, 62, 58, 55, 52, 50, 47, 44, 41, 38],
}


def _baseline_for_region(region_id: str) -> Dict[str, float]:
    region = REGIONS[region_id]
    ecosystem_type = region["ecosystem_type"]

    if ecosystem_type == "coral_reef":
        return {
            "sst": 28.0,
            "sst_anomaly": -0.2,
            "salinity": 35.0,
            "wave_height": 1.2,
            "ph": 8.08,
            "dissolved_oxygen": 5.8,
            "chlorophyll_a": 0.8,
            "nitrogen_load": 2.0,
            "species_richness": 260.0,
            "biodiversity_index": 3.8,
        }
    if ecosystem_type == "open_ocean":
        return {
            "sst": 26.0,
            "sst_anomaly": 0.0,
            "salinity": 34.5,
            "wave_height": 1.5,
            "ph": 8.07,
            "dissolved_oxygen": 5.4,
            "chlorophyll_a": 1.2,
            "nitrogen_load": 3.0,
            "species_richness": 180.0,
            "biodiversity_index": 3.1,
        }
    if ecosystem_type == "polar":
        return {
            "sst": 2.0,
            "sst_anomaly": 0.3,
            "salinity": 33.5,
            "wave_height": 2.1,
            "ph": 8.05,
            "dissolved_oxygen": 6.8,
            "chlorophyll_a": 2.0,
            "nitrogen_load": 2.5,
            "species_richness": 130.0,
            "biodiversity_index": 2.9,
        }
    return {
        "sst": 26.0,
        "sst_anomaly": 0.0,
        "salinity": 34.5,
        "wave_height": 1.5,
        "ph": 8.07,
        "dissolved_oxygen": 5.4,
        "chlorophyll_a": 1.2,
        "nitrogen_load": 3.0,
        "species_richness": 180.0,
        "biodiversity_index": 3.1,
    }


def _target_evs(region_id: str) -> float:
    return REGIONS[region_id]["current_evs"]


def generate_synthetic_data(region_id: str) -> List[Dict[str, object]]:
    """Generate 90 days of synthetic daily readings and persist to CSV.

    Implemented with only the Python standard library so that the demo
    does not depend on compiled numeric stacks.
    """
    if region_id not in REGIONS:
        raise ValueError(f"Unknown region_id: {region_id}")

    baseline = _baseline_for_region(region_id)
    target = _target_evs(region_id)

    days = 90
    end_date = datetime.utcnow()
    dates = [end_date - timedelta(days=i) for i in range(days)][::-1]

    rng = random.Random(abs(hash(region_id)) % (2**32))

    rows: List[Dict[str, object]] = []
    start_evs = {
        "great_barrier_reef": 60,
        "gulf_of_mexico": 55,
        "coral_triangle": 65,
        "bay_of_bengal": 70,
        "arctic_shelf": 55,
    }.get(region_id, 60)

    for i, ts in enumerate(dates):
        frac = i / max(1, days - 1)
        evs_trend = start_evs + (target - start_evs) * frac
        evs_noise = rng.uniform(-3, 3)
        evs_target = max(0.0, min(100.0, evs_trend + evs_noise))

        sst = baseline["sst"] + rng.uniform(-0.8, 0.8)
        sst_anomaly = baseline["sst_anomaly"] + rng.uniform(-0.4, 0.4)
        salinity = baseline["salinity"] + rng.uniform(-0.3, 0.3)
        wave_height = max(0.1, baseline["wave_height"] + rng.uniform(-0.5, 0.5))
        ph = baseline["ph"] + rng.uniform(-0.04, 0.04)
        dissolved_oxygen = baseline["dissolved_oxygen"] + rng.uniform(-0.5, 0.5)
        chlorophyll_a = max(0.01, baseline["chlorophyll_a"] + rng.uniform(-0.4, 0.4))
        nitrogen_load = max(0.1, baseline["nitrogen_load"] + rng.uniform(-0.6, 0.6))
        species_richness = max(10.0, baseline["species_richness"] + rng.uniform(-15, 15))
        biodiversity_index = max(0.5, baseline["biodiversity_index"] + rng.uniform(-0.2, 0.2))

        if region_id == "great_barrier_reef" and i in (10, 25, 60):
            sst_anomaly += 1.8
            nitrogen_load += 2.5
            dissolved_oxygen -= 1.5
        elif region_id == "gulf_of_mexico":
            nitrogen_load += 1.5 * frac + 2.0 * frac
            dissolved_oxygen -= 1.0 * frac + 1.5 * frac
        elif region_id == "coral_triangle":
            sst_anomaly += 0.8 * frac
            nitrogen_load += 1.0 * frac
        elif region_id == "bay_of_bengal":
            nitrogen_load += 0.5 * frac
        elif region_id == "arctic_shelf":
            sst += 1.2 * frac
            sst_anomaly += 0.7 * frac

        rows.append(
            {
                "timestamp": ts.isoformat(),
                "region_id": region_id,
                "latitude": REGIONS[region_id]["lat"],
                "longitude": REGIONS[region_id]["lon"],
                "ecosystem_type": REGIONS[region_id]["ecosystem_type"],
                "sst": sst,
                "sst_anomaly": sst_anomaly,
                "salinity": salinity,
                "wave_height": wave_height,
                "ph": ph,
                "dissolved_oxygen": dissolved_oxygen,
                "chlorophyll_a": chlorophyll_a,
                "nitrogen_load": nitrogen_load,
                "species_richness": species_richness,
                "biodiversity_index": biodiversity_index,
                "evs_target": evs_target,
            }
        )

    out_path = CACHE_DIR / f"{region_id}_synthetic.csv"
    fieldnames = list(rows[0].keys())
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return rows


def generate_all_regions() -> None:
    for region_id in REGIONS.keys():
        generate_synthetic_data(region_id)


if __name__ == "__main__":
    generate_all_regions()

