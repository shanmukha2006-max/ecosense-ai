import asyncio
from pathlib import Path
from typing import Dict, List

from .synthetic_generator import REGIONS, generate_synthetic_data

BASE_DIR = Path(__file__).resolve().parent


async def fetch_all_regions() -> Dict[str, List[Dict[str, object]]]:
    """Main entry to ensure synthetic data exists for all regions.

    In this offline demo we prioritise deterministic synthetic data
    generation over live API calls to avoid external dependencies.
    """
    results: Dict[str, List[Dict[str, object]]] = {}
    for region_id in REGIONS.keys():
        rows = generate_synthetic_data(region_id)
        results[region_id] = rows
    return results


if __name__ == "__main__":
    asyncio.run(fetch_all_regions())

