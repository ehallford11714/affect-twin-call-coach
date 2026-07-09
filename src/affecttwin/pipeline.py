"""End-to-end AffectTwin pipeline: KPIs → affect → coaching (+ optional NFS)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from affecttwin.client.nfs import DEFAULT_NFS_URL, NextFrameSeqClient
from affecttwin.coach.suggestions import CoachSuggestion, suggest_next_utterance
from affecttwin.expression import expression_preview_dict
from affecttwin.kpi.synthetic import FaceKPIs, insight_from_kpis, synthetic_kpis
from affecttwin.thought.proxies import AffectProxies, affect_from_kpis


@dataclass
class CoachResult:
    kpis: FaceKPIs
    insight: str
    affect: AffectProxies
    suggestion: CoachSuggestion
    expression_preview: dict[str, Any] = field(default_factory=dict)
    nfs_used: bool = False
    nfs_payload: dict[str, Any] | None = None
    extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "kpis": self.kpis.to_dict(),
            "insight": self.insight,
            "affect": self.affect.to_dict(),
            "suggestion": self.suggestion.to_dict(),
            "expression_preview": {
                k: v for k, v in self.expression_preview.items() if k != "svg"
            },
            "nfs_used": self.nfs_used,
            "extras": self.extras,
        }
        if self.expression_preview.get("svg"):
            out["expression_preview"]["has_svg"] = True
        if self.nfs_payload is not None:
            slim = {
                k: v
                for k, v in self.nfs_payload.items()
                if not str(k).endswith("_b64") and k != "image"
            }
            out["nfs_summary"] = {
                k: v for k, v in slim.items() if not isinstance(v, (bytes, bytearray))
            }
        return out


class AffectTwinPipeline:
    """face/call KPIs → affect proxies → next utterance + expression preview."""

    def __init__(
        self,
        *,
        nfs_url: str = DEFAULT_NFS_URL,
        prefer_nfs: bool = True,
        nfs_timeout: float = 2.5,
        prefer_slm: bool = False,
    ) -> None:
        self.client = NextFrameSeqClient(nfs_url, timeout=nfs_timeout)
        self.prefer_nfs = prefer_nfs
        self.prefer_slm = prefer_slm

    def run(
        self,
        kpis: FaceKPIs | dict[str, Any] | None = None,
        *,
        scenario: str = "neutral",
        context_hint: str = "",
        goal: str = "",
        try_nfs: bool | None = None,
        use_slm: bool | None = None,
    ) -> CoachResult:
        if kpis is None:
            face_kpis = synthetic_kpis(scenario=scenario)
        elif isinstance(kpis, FaceKPIs):
            face_kpis = kpis
        else:
            from affecttwin.kpi.frame import kpis_from_mapping

            face_kpis = kpis_from_mapping(dict(kpis))

        insight = insight_from_kpis(face_kpis)
        affect = affect_from_kpis(face_kpis, context_hint=context_hint or goal)
        suggestion = suggest_next_utterance(affect, goal=goal)
        preview = expression_preview_dict(
            suggestion.expression_aspects, cue=suggestion.expression_cue
        )

        use_nfs = self.prefer_nfs if try_nfs is None else try_nfs
        nfs_payload = None
        nfs_used = False
        if use_nfs:
            st = self.client.status()
            if st.available:
                # Link coaching utterance to NFS text_causal for expression preview path
                nfs_payload = self.client.text_causal(suggestion.utterance)
                if nfs_payload:
                    nfs_used = True

        slm_on = self.prefer_slm if use_slm is None else use_slm
        extras: dict[str, Any] = {"nfs_url": self.client.base_url, "scenario": scenario}
        if slm_on:
            try:
                from affecttwin.slm_hooks import narrate_affect

                extras["slm_narrative"] = narrate_affect(
                    affect, suggestion=suggestion, use_slm=True
                )
            except Exception as e:  # noqa: BLE001
                extras["slm_narrative"] = {"error": f"{type(e).__name__}: {e}"}

        return CoachResult(
            kpis=face_kpis,
            insight=insight,
            affect=affect,
            suggestion=suggestion,
            expression_preview=preview,
            nfs_used=nfs_used,
            nfs_payload=nfs_payload,
            extras=extras,
        )
