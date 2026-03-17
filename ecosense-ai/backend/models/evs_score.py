from __future__ import annotations

from typing import Dict

from .eco_reading import UnifiedEcoReading


def calculate_evs_score(reading: UnifiedEcoReading) -> Dict[str, object]:
    sst_anom = reading.sst_anomaly
    wave = reading.wave_height
    ph = reading.ph
    do = reading.dissolved_oxygen
    chl = reading.chlorophyll_a
    n = reading.nitrogen_load
    species = reading.species_richness
    biodiv = reading.biodiversity_index
    compound = reading.compound_stress_count
    acoustic = reading.acoustic_index
    edna = reading.edna_index

    physical = max(0.0, 100.0 - min(abs(sst_anom) * 18.0, 45.0) - max(0.0, wave - 4.0) * 5.0)

    chemical = max(
        0.0,
        100.0
        - max(0.0, (8.1 - ph) * 120.0)
        - max(0.0, (4.5 - do) * 12.0)
        - max(0.0, (chl - 10.0) * 5.0)
        - max(0.0, (n - 3.0) * 8.0),
    )

    bio = min(100.0, (species / 400.0) * 100.0) * 0.6 + min(100.0, (biodiv / 5.0) * 100.0) * 0.4

    evs = physical * 0.35 + chemical * 0.35 + bio * 0.30
    compound_active = compound >= 3
    compound_count = compound
    if compound_active:
        evs *= 0.75

    if evs >= 75:
        status = "healthy"
        status_color = "green"
    elif evs >= 55:
        status = "stable"
        status_color = "amber"
    elif evs >= 35:
        status = "stressed"
        status_color = "red"
    else:
        status = "critical"
        status_color = "critical"

    confidence = max(0.0, min(1.0, reading.data_confidence))
    acoustic_score = min(10.0, max(0.0, acoustic))
    edna_score = max(0.0, edna)

    trend = 0.0

    return {
        "evs_score": evs,
        "physical_score": physical,
        "chemical_score": chemical,
        "biological_score": bio,
        "status": status,
        "status_color": status_color,
        "compound_active": compound_active,
        "compound_count": compound_count,
        "confidence": confidence,
        "acoustic_score": acoustic_score,
        "edna_score": edna_score,
        "trend": trend,
    }

