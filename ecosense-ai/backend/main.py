from __future__ import annotations

import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from dotenv import load_dotenv

from models.db import create_db_and_tables, get_engine
from models.ml_pipeline import EcoSenseMLPipeline
from models.new_features import monitor_cycle
from routers import regions, simulate, reports, features


app = FastAPI(title="EcoSense AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _init_env() -> None:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_key_here":
        env = os.getenv("ENVIRONMENT", "development")
        if env != "development":
            raise RuntimeError("ANTHROPIC_API_KEY must be configured in non-development environments")


def _init_db() -> None:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./ecosense.db")
    create_db_and_tables(database_url)
    get_engine(database_url)


def _init_pipeline() -> EcoSenseMLPipeline:
    pipeline = EcoSenseMLPipeline()
    pipeline.train_or_load()
    return pipeline


def _init_scheduler(pipeline: EcoSenseMLPipeline) -> BackgroundScheduler:
    scheduler = BackgroundScheduler()

    def _cycle():
        def get_latest():
            return {"evs_score": 55.0}

        def get_cached():
            return {"evs_score": 52.0}

        monitor_cycle(get_latest, get_cached, lambda d: d, pipeline)

    scheduler.add_job(_cycle, "interval", seconds=60, id="nightwatch")
    scheduler.start()
    return scheduler


def _prewarm_claude() -> None:
    try:
        import anthropic  # type: ignore

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key or api_key == "your_key_here":
            return
        client = anthropic.Anthropic(api_key=api_key)
        client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=5,
            messages=[{"role": "user", "content": "EcoSense AI startup health ping."}],
        )
    except Exception:
        return


@app.on_event("startup")
def on_startup() -> None:
    _init_env()
    _init_db()
    pipeline = _init_pipeline()
    app.state.pipeline = pipeline
    app.state.scheduler = _init_scheduler(pipeline)
    _prewarm_claude()


@app.on_event("shutdown")
def on_shutdown() -> None:
    scheduler = getattr(app.state, "scheduler", None)
    if scheduler:
        scheduler.shutdown(wait=False)


app.include_router(regions.router, prefix="/api")
app.include_router(simulate.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(features.router, prefix="/api")


@app.get("/api/region/{region_id}")
def legacy_region_endpoint(region_id: str):
    """Compatibility alias so that /api/region/{id} matches the spec and verify script."""
    from routers.regions import get_region

    return get_region(region_id)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

