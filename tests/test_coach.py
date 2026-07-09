"""Offline tests for AffectTwin Call Coach."""

from __future__ import annotations

from affecttwin.coach.suggestions import suggest_next_utterance
from affecttwin.expression import expression_preview_svg
from affecttwin.kpi.synthetic import FaceKPIs, insight_from_kpis, synthetic_kpis
from affecttwin.pipeline import AffectTwinPipeline
from affecttwin.thought.proxies import affect_from_kpis


def test_synthetic_scenarios():
    for s in ("neutral", "engaged", "stressed", "withdrawn", "confused"):
        k = synthetic_kpis(scenario=s, seed=1)
        assert isinstance(k, FaceKPIs)
        assert 0.0 <= k.stability <= 1.0


def test_affect_from_engaged():
    k = synthetic_kpis(scenario="engaged", seed=0)
    a = affect_from_kpis(k)
    assert -1.0 <= a.valence <= 1.0
    assert 0.0 <= a.arousal <= 1.0
    assert "Proxy" in a.notes or "proxy" in a.notes.lower()


def test_suggest_repair_on_low_rapport():
    a = affect_from_kpis(
        FaceKPIs(
            color_warmth=-0.15,
            motion_score=0.02,
            gaze_away=0.5,
            face_detected=True,
            face_ratio=0.1,
            pause_ratio=0.4,
        )
    )
    sug = suggest_next_utterance(a)
    assert sug.utterance
    assert sug.expression_aspects is not None
    assert "Suggestion" in sug.caution or "proxy" in sug.caution.lower()


def test_insight_stressed():
    text = insight_from_kpis(synthetic_kpis(scenario="stressed", seed=2))
    assert isinstance(text, str) and len(text) > 10


def test_expression_svg():
    svg = expression_preview_svg({"mouth_curve": 0.3, "brow_raise": 0.1}, cue="soft smile")
    assert "<svg" in svg and "soft smile" in svg


def test_pipeline_offline():
    pipe = AffectTwinPipeline(prefer_nfs=False)
    result = pipe.run(scenario="confused", goal="clarify", try_nfs=False)
    assert result.nfs_used is False
    assert result.suggestion.utterance
    d = result.to_dict()
    assert "kpis" in d and "affect" in d and "suggestion" in d
