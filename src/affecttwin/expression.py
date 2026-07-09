"""Expression preview — lightweight SVG / aspect summary for coaching cues."""

from __future__ import annotations

from typing import Any


def expression_preview_svg(
    aspects: dict[str, float],
    *,
    cue: str = "",
    size: int = 160,
) -> str:
    """Return a simple face SVG reflecting mouth/brow aspect deltas."""
    mouth = float(aspects.get("mouth_curve", 0.0))
    brow = float(aspects.get("brow_raise", 0.0)) - float(aspects.get("brow_knit", 0.0))
    # mouth path: smile vs frown via control point
    cy = 110 - mouth * 18
    brow_y = 55 - brow * 10
    label = (cue or "expression")[:48].replace("<", "").replace(">", "")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 160 160">
  <rect width="160" height="160" fill="#1a1f2e"/>
  <ellipse cx="80" cy="78" rx="48" ry="58" fill="#c4a882" stroke="#8a6d4f" stroke-width="2"/>
  <circle cx="62" cy="70" r="5" fill="#2a2a2a"/>
  <circle cx="98" cy="70" r="5" fill="#2a2a2a"/>
  <path d="M50 {brow_y:.1f} Q62 {brow_y - 4:.1f} 74 {brow_y:.1f}" stroke="#3a2a1a" stroke-width="3" fill="none"/>
  <path d="M86 {brow_y:.1f} Q98 {brow_y - 4:.1f} 110 {brow_y:.1f}" stroke="#3a2a1a" stroke-width="3" fill="none"/>
  <path d="M55 105 Q80 {cy:.1f} 105 105" stroke="#6b3a4a" stroke-width="3" fill="none"/>
  <text x="80" y="152" text-anchor="middle" fill="#9aa3b5" font-size="9" font-family="sans-serif">{label}</text>
</svg>"""


def expression_preview_dict(aspects: dict[str, float], cue: str = "") -> dict[str, Any]:
    return {
        "cue": cue,
        "aspects": {k: round(float(v), 4) for k, v in aspects.items()},
        "svg": expression_preview_svg(aspects, cue=cue),
    }
