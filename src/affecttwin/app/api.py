"""FastAPI companion for AffectTwin Call Coach (default port 8771 — not 8765)."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from affecttwin.pipeline import AffectTwinPipeline

app = FastAPI(title="AffectTwin Call Coach", version="0.1.0")


class CoachRequest(BaseModel):
    kpis: dict[str, Any] | None = None
    scenario: str = "neutral"
    context_hint: str = ""
    goal: str = ""
    offline: bool = False
    nfs_url: str = "http://127.0.0.1:8765"


class CoachResponse(BaseModel):
    result: dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "affecttwin"}


@app.post("/api/coach", response_model=CoachResponse)
def coach(req: CoachRequest) -> CoachResponse:
    pipe = AffectTwinPipeline(nfs_url=req.nfs_url, prefer_nfs=not req.offline)
    result = pipe.run(
        req.kpis,
        scenario=req.scenario,
        context_hint=req.context_hint,
        goal=req.goal,
        try_nfs=False if req.offline else None,
    )
    return CoachResponse(result=result.to_dict())
