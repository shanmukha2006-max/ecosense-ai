from __future__ import annotations

from datetime import datetime, timedelta

from models.db import Alert, Annotation, create_db_and_tables, get_engine, get_session
from data.synthetic_generator import REGIONS


def main() -> None:
    from dotenv import load_dotenv
    import os

    load_dotenv()
    database_url = os.getenv("DATABASE_URL", "sqlite:///./ecosense.db")
    create_db_and_tables(database_url)
    get_engine(database_url)

    session = get_session()

    existing_alerts = session.query(Alert).count()
    existing_annotations = session.query(Annotation).count()
    if existing_alerts > 0 and existing_annotations > 0:
        print("Demo data already present, skipping seed.")
        return

    now = datetime.utcnow()
    severities = ["CRITICAL", "WARNING", "ADVISORY", "WATCH"]
    alerts = []
    minutes_offsets = [2, 7, 15, 30, 60, 120, 360, 720]
    region_ids = list(REGIONS.keys())

    for i, offset in enumerate(minutes_offsets):
        alerts.append(
            Alert(
                created_at=now - timedelta(minutes=offset),
                region_id=region_ids[i % len(region_ids)],
                severity=severities[i % len(severities)],
                message=f"Demo alert {i+1} severity {severities[i % len(severities)]}",
            )
        )

    annotations = [
        Annotation(
            region_id="great_barrier_reef",
            source="NOAA",
            text="NOAA field team confirms widespread bleaching matches AI alerts.",
            agrees_with_ai=True,
        ),
        Annotation(
            region_id="great_barrier_reef",
            source="CSIRO",
            text="CSIRO moorings show thermal stress consistent with EcoSense AI projections.",
            agrees_with_ai=True,
        ),
        Annotation(
            region_id="great_barrier_reef",
            source="GBRMPA",
            text="GBRMPA surveys report coral mortality in predicted hotspots.",
            agrees_with_ai=True,
        ),
        Annotation(
            region_id="gulf_of_mexico",
            source="NOAA",
            text="Hypoxic area extent aligns with modeled dead-zone risk.",
            agrees_with_ai=True,
        ),
        Annotation(
            region_id="coral_triangle",
            source="Citizen Science",
            text="Diver reports confirm fish behavior anomalies flagged by AI.",
            agrees_with_ai=True,
        ),
    ]

    for alert in alerts:
        session.add(alert)
    for ann in annotations:
        session.add(ann)
    session.commit()

    print("Seeded demo alerts and annotations.")


if __name__ == "__main__":
    main()

