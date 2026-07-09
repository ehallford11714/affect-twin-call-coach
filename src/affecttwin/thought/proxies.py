"""Affect / intent proxies — low-dimensional latent from face KPIs.

These are *proxies*, not mind-reading. See docs/SOTA.md for epistemic limits.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from affecttwin.kpi.synthetic import FaceKPIs


@dataclass
class AffectProxies:
    """Affect + appraisal + coarse intent for coaching (not propositional thought)."""

    valence: float = 0.0
    arousal: float = 0.25
    cognitive_load: float = 0.2
    approach_avoid: float = 0.0
    rapport: float = 0.5
    intent_label: str = "observe"
    emotion_label: str = "neutral"
    confidence: float = 0.35
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def affect_from_kpis(
    kpis: FaceKPIs | dict[str, float],
    *,
    context_hint: str = "",
) -> AffectProxies:
    """Map face/call KPIs → affect/intent proxies (rule-based offline stub)."""
    if isinstance(kpis, FaceKPIs):
        d = kpis.to_dict()
        face = bool(kpis.face_detected)
    else:
        d = dict(kpis)
        face = bool(d.get("face_detected", float(d.get("face_ratio", 0)) > 0.02))

    warmth = float(d.get("color_warmth", 0.0))
    motion = float(d.get("motion_score", 0.0))
    stability = float(d.get("stability", 1.0))
    edges = float(d.get("edge_density", 0.0))
    texture = float(d.get("texture_energy", 0.0))
    face_r = float(d.get("face_ratio", 0.0))
    rate = float(d.get("speaking_rate", 0.4))
    pause = float(d.get("pause_ratio", 0.2))
    gaze = float(d.get("gaze_away", 0.15))

    valence = _clip(warmth * 2.5 - gaze * 0.4 + (0.1 if face else -0.05), -1.0, 1.0)
    arousal = _clip(
        motion * 4.0 + (1.0 - stability) * 0.6 + rate * 0.25 + texture * 0.15, 0.0, 1.0
    )
    load = _clip(
        edges * 2.5 + pause * 0.5 + (0.3 if motion < 0.03 and edges > 0.1 else 0.0),
        0.0,
        1.0,
    )
    approach = _clip(valence * 0.55 - load * 0.25 + face_r - gaze * 0.3, -1.0, 1.0)
    rapport = _clip(
        0.5 + valence * 0.35 - gaze * 0.25 - abs(rate - 0.45) * 0.3, 0.0, 1.0
    )

    emotion = "neutral"
    if valence > 0.35 and arousal > 0.3:
        emotion = "happy"
    elif valence < -0.35 and arousal > 0.45:
        emotion = "frustrated"
    elif valence < -0.25 and arousal < 0.35:
        emotion = "sad"
    elif arousal > 0.65 and abs(valence) < 0.25:
        emotion = "anxious"
    elif load > 0.55 and motion < 0.05:
        emotion = "confused"

    intent = "observe"
    hint = (context_hint or "").lower()
    if any(w in hint for w in ("close", "next step", "cta", "schedule")):
        intent = "close"
    elif any(w in hint for w in ("clarify", "confirm", "understand")):
        intent = "clarify"
    elif any(w in hint for w in ("empath", "support", "sorry")):
        intent = "support"
    elif any(w in hint for w in ("ask", "question", "?")):
        intent = "question"
    elif rapport < 0.35 or approach < -0.25:
        intent = "repair"
    elif load > 0.5:
        intent = "simplify"
    elif approach > 0.35 and valence > 0.2:
        intent = "advance"
    elif pause > 0.35:
        intent = "invite"

    conf = _clip(0.25 + (0.2 if face else 0.0) + (0.1 if hint else 0.0), 0.0, 0.8)

    notes = (
        "Affect/intent *proxy* only — not mind-reading. "
        "Reverse inference from face is underdetermined; prefer opt-in coaching. "
        "See docs/SOTA.md."
    )
    return AffectProxies(
        valence=round(valence, 4),
        arousal=round(arousal, 4),
        cognitive_load=round(load, 4),
        approach_avoid=round(approach, 4),
        rapport=round(rapport, 4),
        intent_label=intent,
        emotion_label=emotion,
        confidence=round(conf, 4),
        notes=notes,
    )
