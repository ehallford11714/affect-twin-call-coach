"""Face / call KPIs — synthetic + optional OpenCV frame mining."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class FaceKPIs:
    """Quantitative face/frame KPIs used for affect proxies and coaching."""

    luminance_mean: float = 0.5
    luminance_std: float = 0.2
    edge_density: float = 0.05
    entropy: float = 4.0
    motion_score: float = 0.02
    motion_accel: float = 0.0
    face_ratio: float = 0.15
    texture_energy: float = 0.1
    color_warmth: float = 0.05
    stability: float = 0.85
    face_detected: bool = True
    # Call-context proxies (optional; synthetic or upstream)
    speaking_rate: float = 0.4
    pause_ratio: float = 0.2
    gaze_away: float = 0.15

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def synthetic_kpis(
    *,
    scenario: str = "neutral",
    seed: int | None = None,
) -> FaceKPIs:
    """Deterministic synthetic KPI bundles for CLI dry-runs and tests."""
    import random

    rng = random.Random(seed if seed is not None else hash(scenario) & 0xFFFFFFFF)
    base = FaceKPIs()
    s = (scenario or "neutral").lower()

    if s in ("engaged", "happy", "rapport"):
        base.color_warmth = 0.18 + rng.uniform(0, 0.05)
        base.motion_score = 0.08 + rng.uniform(0, 0.04)
        base.stability = 0.7
        base.speaking_rate = 0.55
        base.pause_ratio = 0.12
        base.gaze_away = 0.08
        base.face_detected = True
        base.face_ratio = 0.22
    elif s in ("stressed", "anxious", "tense"):
        base.color_warmth = -0.05
        base.motion_score = 0.14
        base.stability = 0.45
        base.edge_density = 0.12
        base.speaking_rate = 0.72
        base.pause_ratio = 0.08
        base.gaze_away = 0.35
        base.texture_energy = 0.25
    elif s in ("withdrawn", "sad", "disengaged"):
        base.color_warmth = -0.12
        base.motion_score = 0.02
        base.stability = 0.9
        base.speaking_rate = 0.25
        base.pause_ratio = 0.45
        base.gaze_away = 0.4
        base.luminance_mean = 0.35
    elif s in ("confused", "load", "thinking"):
        base.edge_density = 0.15
        base.motion_score = 0.03
        base.stability = 0.88
        base.speaking_rate = 0.3
        base.pause_ratio = 0.35
        base.gaze_away = 0.25
        base.texture_energy = 0.2
    else:
        base.motion_score = 0.02 + rng.uniform(0, 0.03)
        base.color_warmth = rng.uniform(-0.02, 0.08)
        base.speaking_rate = 0.35 + rng.uniform(0, 0.15)

    return base


def insight_from_kpis(kpis: FaceKPIs | dict[str, Any]) -> str:
    d = kpis.to_dict() if isinstance(kpis, FaceKPIs) else dict(kpis)
    parts: list[str] = []
    if not d.get("face_detected", True) and float(d.get("face_ratio", 0)) < 0.02:
        parts.append("No face detected — coaching confidence is low.")
    motion = float(d.get("motion_score", 0))
    stability = float(d.get("stability", 1))
    warmth = float(d.get("color_warmth", 0))
    pause = float(d.get("pause_ratio", 0))
    rate = float(d.get("speaking_rate", 0.4))
    gaze = float(d.get("gaze_away", 0))

    if warmth > 0.12 and motion > 0.05:
        parts.append("Warmth + motion suggest positive engagement.")
    elif warmth < -0.08:
        parts.append("Cool color / low warmth bias — check rapport.")
    if stability < 0.55 or motion > 0.12:
        parts.append("Elevated motion / low stability — possible tension.")
    if pause > 0.35:
        parts.append("High pause ratio — leave space or check understanding.")
    if rate > 0.65:
        parts.append("Fast speaking-rate proxy — slow down and clarify.")
    if gaze > 0.3:
        parts.append("Gaze-away proxy elevated — re-anchor attention gently.")
    if not parts:
        parts.append("Near-neutral call KPIs — maintain steady presence.")
    return " ".join(parts)
