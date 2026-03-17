from .synthetic_generator import REGIONS
from models.eco_reading import UnifiedEcoReading


def feature_engineer(reading: UnifiedEcoReading) -> UnifiedEcoReading:
    """Enrich a UnifiedEcoReading with derived features."""
    dhw = max(0.0, reading.sst_anomaly) * 4.2

    compound = 0
    if abs(reading.sst_anomaly) > 1.0:
        compound += 1
    if reading.ph < 8.05:
        compound += 1
    if reading.dissolved_oxygen < 3.0:
        compound += 1
    if reading.species_richness < 80:
        compound += 1
    if reading.nitrogen_load > 5.0:
        compound += 1

    acoustic_index = min(
        10.0,
        (reading.species_richness / 300.0)
        * (1.0 - max(0.0, reading.sst - 27.0) * 0.15)
        * (reading.dissolved_oxygen / 8.0)
        * 10.0,
    )

    edna_index = reading.species_richness / (
        1.0
        + max(0.0, reading.sst - 26.0) * 0.08
        + max(0.0, 8.1 - reading.ph) * 0.15
    )

    reading.dhw = dhw
    reading.compound_stress_count = compound
    reading.acoustic_index = max(0.0, acoustic_index)
    reading.edna_index = max(0.0, edna_index)

    return reading

