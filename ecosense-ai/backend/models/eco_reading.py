from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class UnifiedEcoReading:
    region_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    ecosystem_type: str
    sst: float
    sst_anomaly: float
    salinity: float
    wave_height: float
    ph: float
    dissolved_oxygen: float
    chlorophyll_a: float
    nitrogen_load: float
    species_richness: float
    biodiversity_index: float
    dhw: float = 0.0
    sst_7d_trend: float = 0.0
    ph_30d_trend: float = 0.0
    compound_stress_count: int = 0
    seasonal_deviation: float = 0.0
    acoustic_index: float = 0.0
    edna_index: float = 0.0
    data_confidence: float = 1.0
    sources: List[str] = field(default_factory=list)

