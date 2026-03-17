from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from models.new_features import generate_morning_briefing


router = APIRouter(prefix="/reports", tags=["reports"])


class ReportRequest(BaseModel):
    region_id: str
    audience: str = "Scientist"


def get_claude_client() -> Any:
    try:
        import anthropic  # type: ignore
        import os

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key or api_key == "your_key_here":
            raise RuntimeError("Using fallback Claude stub")
        return anthropic.Anthropic(api_key=api_key)
    except Exception:
        return None


@router.post("/report")
def generate_report(
    payload: ReportRequest, claude_client: Any = Depends(get_claude_client)
) -> Dict[str, str]:
    system_prompt = (
        "You are EcoSense AI environmental intelligence engine. "
        "Be specific with numbers. Lead with the most urgent finding. "
        "End with exactly 2 concrete recommended actions. "
        "Write as EcoSense AI analysis indicates. Never say I. Max 200 words."
    )
    audience = payload.audience
    prompt = (
        f"{system_prompt}\n\n"
        f"Audience mode: {audience}.\n"
        f"Region: {payload.region_id}. Summarize current ecological state, key drivers, "
        "near-term tipping risks, and two highest-leverage actions."
    )

    from models.new_features import _safe_claude_call

    text = _safe_claude_call(claude_client, prompt)
    return {"text": text}


@router.get("/morning-briefing")
def morning_briefing(claude_client: Any = Depends(get_claude_client)) -> Dict[str, str]:
    text = generate_morning_briefing(claude_client)
    return {"text": text}

