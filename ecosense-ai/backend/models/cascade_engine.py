from __future__ import annotations

from typing import Dict, List

from .eco_reading import UnifiedEcoReading


ECOLOGICAL_CASCADES: Dict[str, Dict] = {
    "coral_thermal_stress": {
        "trigger": lambda r: r.sst_anomaly >= 1.0,
        "label": "Coral Thermal Stress",
        "steps": [
            {
                "id": "bleaching",
                "probability": 87,
                "timescale": "2-4 weeks",
                "severity": "CRITICAL",
                "impact": "$6B tourism at risk",
            },
            {
                "id": "fish_habitat",
                "probability": 71,
                "timescale": "1-3 months",
                "severity": "HIGH",
                "impact": "340 species habitat loss",
            },
            {
                "id": "fisheries",
                "probability": 58,
                "timescale": "6-12 months",
                "severity": "HIGH",
                "impact": "85,000 people affected",
            },
            {
                "id": "structural",
                "probability": 44,
                "timescale": "2-5 years",
                "severity": "CRITICAL",
                "impact": "$375B structural asset risk",
            },
        ],
    },
    "hypoxic_event": {
        "trigger": lambda r: r.dissolved_oxygen < 2.5,
        "label": "Hypoxic Event",
        "steps": [
            {
                "id": "hab",
                "probability": 78,
                "timescale": "days",
                "severity": "CRITICAL",
                "impact": "Shellfish harvest ban",
            },
            {
                "id": "benthic",
                "probability": 91,
                "timescale": "days-weeks",
                "severity": "CRITICAL",
                "impact": "Benthic collapse, 5-year recovery",
            },
            {
                "id": "dead_zone",
                "probability": 52,
                "timescale": "2-6 months",
                "severity": "HIGH",
                "impact": "$2.3M/week losses",
            },
        ],
    },
    "biodiversity_collapse": {
        "trigger": lambda r: r.species_richness < 80,
        "label": "Biodiversity Collapse",
        "steps": [
            {
                "id": "trophic",
                "probability": 91,
                "timescale": "weeks",
                "severity": "CRITICAL",
                "impact": "Urchin explosion, trophic imbalance",
            },
            {
                "id": "kelp_loss",
                "probability": 84,
                "timescale": "1-6 months",
                "severity": "HIGH",
                "impact": "Up to 70% kelp loss, 800 species affected",
            },
            {
                "id": "regime_shift",
                "probability": 45,
                "timescale": "2-5 years",
                "severity": "CRITICAL",
                "impact": "-45M kg CO2 sequestration",
            },
        ],
    },
    "ocean_acidification": {
        "trigger": lambda r: r.ph < 8.0,
        "label": "Ocean Acidification",
        "steps": [
            {
                "id": "pteropod",
                "probability": 89,
                "timescale": "months",
                "severity": "HIGH",
                "impact": "Pteropod dissolution, food web stress",
            },
            {
                "id": "calcification",
                "probability": 76,
                "timescale": "months",
                "severity": "CRITICAL",
                "impact": "-50% calcification growth",
            },
            {
                "id": "shellfish",
                "probability": 68,
                "timescale": "1-3 months",
                "severity": "HIGH",
                "impact": "$2.3B shellfish industry at risk",
            },
        ],
    },
    "compound_stress": {
        "trigger": lambda r: r.compound_stress_count >= 3,
        "label": "Compound Stress",
        "steps": [
            {
                "id": "synergy",
                "probability": 97,
                "timescale": "immediate",
                "severity": "CRITICAL",
                "impact": "Synergistic 25% penalty on EVS",
            },
            {
                "id": "resilience",
                "probability": 88,
                "timescale": "days-weeks",
                "severity": "CRITICAL",
                "impact": "<15% ecosystem recovery capacity",
            },
        ],
    },
}


def get_active_cascades(reading: UnifiedEcoReading) -> List[Dict]:
    """Return all cascades whose trigger conditions are met for this reading."""
    active: List[Dict] = []
    for key, cascade in ECOLOGICAL_CASCADES.items():
        try:
            if cascade["trigger"](reading):
                active.append(
                    {
                        "id": key,
                        "label": cascade["label"],
                        "steps": cascade["steps"],
                    }
                )
        except Exception:
            continue
    return active

