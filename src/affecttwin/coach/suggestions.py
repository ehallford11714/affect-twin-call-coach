"""Coaching suggestions — next utterance + expression guidance from affect proxies."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from affecttwin.thought.proxies import AffectProxies


@dataclass
class CoachSuggestion:
    """One coaching turn recommendation."""

    utterance: str
    rationale: str
    expression_cue: str
    expression_aspects: dict[str, float] = field(default_factory=dict)
    alternatives: list[str] = field(default_factory=list)
    caution: str = (
        "Suggestion only — verify with conversation context; "
        "do not treat affect proxies as ground truth."
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_UTTERANCES: dict[str, list[str]] = {
    "repair": [
        "I want to make sure we're aligned — what feels most important to you right now?",
        "It sounds like something may be off — can we pause and reset together?",
    ],
    "simplify": [
        "Let me put that more simply — the key point is…",
        "I'll break this into two steps so it's easier to follow.",
    ],
    "invite": [
        "Take your time — what are you thinking so far?",
        "I'm happy to wait — does anything need clarifying before we continue?",
    ],
    "advance": [
        "Great — shall we move to the next step?",
        "That sounds promising. Here's what I'd suggest we do next…",
    ],
    "close": [
        "If this works for you, we can lock in a next step now.",
        "Would you like me to send a short summary and proposed timeline?",
    ],
    "clarify": [
        "Just to confirm I understood — you're saying… is that right?",
        "Can I check one detail so I don't miss anything?",
    ],
    "support": [
        "I hear you — that sounds frustrating. Let's work through it together.",
        "Thanks for sharing that. What would be most helpful from me right now?",
    ],
    "question": [
        "What outcome would make this call a success for you?",
        "Which option feels closest to what you need?",
    ],
    "observe": [
        "I'm with you — tell me more about that.",
        "Got it. What would you like to focus on next?",
    ],
}

_EXPRESSION: dict[str, tuple[str, dict[str, float]]] = {
    "happy": ("soft smile, open brows", {"mouth_curve": 0.35, "brow_raise": 0.1}),
    "frustrated": ("neutral-calm, slight brow ease", {"mouth_curve": -0.05, "brow_knit": -0.2}),
    "sad": ("gentle concern, soft eyes", {"mouth_curve": -0.1, "brow_inner": 0.15}),
    "anxious": ("steady gaze, slow nod", {"mouth_curve": 0.05, "brow_raise": 0.05}),
    "confused": ("curious tilt, open face", {"brow_raise": 0.2, "mouth_open": 0.05}),
    "neutral": ("relaxed neutral presence", {"mouth_curve": 0.05}),
}


def suggest_next_utterance(
    affect: AffectProxies,
    *,
    goal: str = "",
) -> CoachSuggestion:
    """Rule-based coaching suggestion from affect/intent proxies."""
    intent = affect.intent_label or "observe"
    if goal:
        g = goal.lower()
        if "close" in g or "schedule" in g:
            intent = "close"
        elif "empath" in g or "support" in g:
            intent = "support"

    pool = _UTTERANCES.get(intent, _UTTERANCES["observe"])
    utterance = pool[0]
    alternatives = pool[1:] if len(pool) > 1 else []

    cue, aspects = _EXPRESSION.get(affect.emotion_label, _EXPRESSION["neutral"])
    # Soften expression if confidence is low
    if affect.confidence < 0.4:
        aspects = {k: v * 0.5 for k, v in aspects.items()}
        cue = f"{cue} (low-confidence — keep subtle)"

    rationale = (
        f"intent={intent}, emotion≈{affect.emotion_label}, "
        f"rapport={affect.rapport:.2f}, load={affect.cognitive_load:.2f}, "
        f"v={affect.valence:.2f}/a={affect.arousal:.2f} (proxy conf={affect.confidence:.2f})"
    )
    return CoachSuggestion(
        utterance=utterance,
        rationale=rationale,
        expression_cue=cue,
        expression_aspects=aspects,
        alternatives=alternatives,
    )
