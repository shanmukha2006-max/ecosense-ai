from __future__ import annotations

import time
from pathlib import Path

import httpx


BACKEND_URL = "http://localhost:8000/api"
BASE_DIR = Path(__file__).resolve().parents[1]


def check_1_csvs() -> bool:
    cache_dir = BASE_DIR / "data" / "cache"
    files = list(cache_dir.glob("*.csv"))
    ok = len(files) >= 5
    print(f"1. CSV cache files: {'CHECK PASSED' if ok else 'CHECK FAILED'} ({len(files)} found)")
    return ok


def check_2_pipeline() -> bool:
    model_path = BASE_DIR / "models" / "trained" / "pipeline_v1.joblib"
    ok = model_path.exists()
    print(f"2. ML pipeline artifact: {'CHECK PASSED' if ok else 'CHECK FAILED'}")
    return ok


def check_3_regions() -> bool:
    try:
        resp = httpx.get(f"{BACKEND_URL}/regions", timeout=5)
        data = resp.json()
        ok = isinstance(data, list) and len(data) == 5
    except Exception:
        ok = False
    print(f"3. /api/regions returns 5: {'CHECK PASSED' if ok else 'CHECK FAILED'}")
    return ok


def check_4_gbr_evs() -> bool:
    try:
        resp = httpx.get(f"{BACKEND_URL}/region/great_barrier_reef", timeout=5)
        data = resp.json()
        ok = data["meta"]["current_evs"] == 31 and data["meta"]["tipping_days"] == 847
    except Exception:
        ok = False
    print(f"4. GBR EVS and tipping_days: {'CHECK PASSED' if ok else 'CHECK FAILED'}")
    return ok


def check_5_report() -> bool:
    try:
        resp = httpx.post(
            f"{BACKEND_URL}/reports/report",
            json={"region_id": "great_barrier_reef", "audience": "Scientist"},
            timeout=20,
        )
        text = resp.json().get("text", "")
        ok = isinstance(text, str) and len(text.strip()) > 0
    except Exception:
        ok = False
    print(f"5. POST /api/report returns text: {'CHECK PASSED' if ok else 'CHECK FAILED'}")
    return ok


def check_6_bleaching_cascade() -> bool:
    try:
        resp_base = httpx.get(f"{BACKEND_URL}/region/great_barrier_reef", timeout=5)
        base = resp_base.json()
        base_sst = base["reading"]["sst"]
        sim = httpx.post(
            f"{BACKEND_URL}/simulate",
            json={
                "region_id": "great_barrier_reef",
                "sst_delta": 2.0,
                "ph_delta": 0.0,
                "do_delta": 0.0,
                "bio_delta": 0.0,
                "poll_delta": 0.0,
            },
            timeout=10,
        ).json()
        cascades = sim.get("new_cascade", [])
        ok = any(c["id"] == "coral_thermal_stress" for c in cascades)
    except Exception:
        ok = False
    print(f"6. SST +2.0 triggers bleaching cascade: {'CHECK PASSED' if ok else 'CHECK FAILED'}")
    return ok


def check_7_compound_banner() -> bool:
    try:
        sim = httpx.post(
            f"{BACKEND_URL}/simulate",
            json={
                "region_id": "great_barrier_reef",
                "sst_delta": 2.5,
                "ph_delta": -0.2,
                "do_delta": -2.0,
                "bio_delta": -60,
                "poll_delta": 50,
            },
            timeout=10,
        ).json()
        ok = bool(sim.get("compound_active"))
    except Exception:
        ok = False
    print(f"7. Compound stress banner condition: {'CHECK PASSED' if ok else 'CHECK FAILED'}")
    return ok


def check_8_acoustic_index() -> bool:
    try:
        gbr = httpx.get(f"{BACKEND_URL}/acoustic/great_barrier_reef", timeout=5).json()
        ct = httpx.get(f"{BACKEND_URL}/acoustic/coral_triangle", timeout=5).json()
        ok = gbr["index"] < ct["index"]
    except Exception:
        ok = False
    print(f"8. Reef audio index GBR < Coral Triangle: {'CHECK PASSED' if ok else 'CHECK FAILED'}")
    return ok


def check_9_time_machine() -> bool:
    try:
        import json

        for rid in [
            "great_barrier_reef",
            "gulf_of_mexico",
            "coral_triangle",
            "bay_of_bengal",
            "arctic_shelf",
        ]:
            resp = httpx.get(f"{BACKEND_URL}/history/{rid}", timeout=5)
            data = resp.json()
            if len(data.get("years", [])) != 11:
                raise RuntimeError("Bad history length")
        ok = True
    except Exception:
        ok = False
    print(f"9. Time Machine 11 points per region: {'CHECK PASSED' if ok else 'CHECK FAILED'}")
    return ok


def check_10_routers_import() -> bool:
    try:
        from routers import regions, simulate, reports, features  # noqa: F401

        ok = True
    except Exception:
        ok = False
    print(f"10. Routers import without circular errors: {'CHECK PASSED' if ok else 'CHECK FAILED'}")
    return ok


def main() -> None:
    checks = [
        check_1_csvs,
        check_2_pipeline,
        check_3_regions,
        check_4_gbr_evs,
        check_5_report,
        check_6_bleaching_cascade,
        check_7_compound_banner,
        check_8_acoustic_index,
        check_9_time_machine,
        check_10_routers_import,
    ]
    results = [fn() for fn in checks]
    if all(results):
        print("DEMO READY")
    else:
        print("DEMO NOT READY")


if __name__ == "__main__":
    main()

