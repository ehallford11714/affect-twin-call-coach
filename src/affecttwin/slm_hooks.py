"""Thin optional SLM hooks for coaching narrative (autocausal RuleBackend fallback)."""

from __future__ import annotations

from typing import Any, Optional


def narrate_affect(
    affect: Any,
    *,
    suggestion: Optional[Any] = None,
    use_slm: bool = False,
) -> dict[str, Any]:
    """Interpret affect proxies with causal caveats (never treat affect as Z)."""
    ad = affect.to_dict() if hasattr(affect, "to_dict") else dict(affect or {})
    utterance = ""
    if suggestion is not None:
        utterance = getattr(suggestion, "utterance", None) or (
            suggestion.get("utterance") if isinstance(suggestion, dict) else ""
        )
    try:
        from autocausal.slm import infer_from_results

        return infer_from_results(
            {
                "emotion": ad.get("dominant") or ad.get("label") or ad.get("mood"),
                "intent": ad.get("intent"),
                "text": utterance or "",
                "edges": [],
                "valence": ad.get("valence"),
                "arousal": ad.get("arousal"),
            },
            use_slm=use_slm,
        ).to_dict()
    except Exception:
        return {
            "backend": "affecttwin.rule",
            "narrative": (
                f"Affect proxies suggest mood={ad.get('dominant', ad.get('label', 'unknown'))}. "
                "Use coaching suggestions as hypotheses, not causal claims."
            ),
            "caveats": [
                "Affect proxies are not ground truth.",
                "Do not use facial/affect KPIs as instrumental variables.",
            ],
            "confidence": 0.35,
        }
