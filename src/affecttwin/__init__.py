"""AffectTwin Call Coach — face KPIs → affect/intent proxies → coaching suggestions."""

from affecttwin.coach.suggestions import CoachSuggestion, suggest_next_utterance
from affecttwin.kpi.synthetic import FaceKPIs, synthetic_kpis
from affecttwin.pipeline import AffectTwinPipeline, CoachResult
from affecttwin.thought.proxies import AffectProxies, affect_from_kpis

__version__ = "0.1.0"

__all__ = [
    "AffectProxies",
    "AffectTwinPipeline",
    "CoachResult",
    "CoachSuggestion",
    "FaceKPIs",
    "affect_from_kpis",
    "suggest_next_utterance",
    "synthetic_kpis",
    "__version__",
]
