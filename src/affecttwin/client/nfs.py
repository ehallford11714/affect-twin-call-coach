"""HTTP client for NextFrameSeq demo API (default http://127.0.0.1:8765)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

DEFAULT_NFS_URL = "http://127.0.0.1:8765"


@dataclass
class NFSStatus:
    available: bool
    url: str
    detail: str = ""


class NextFrameSeqClient:
    """Thin client — never required; AffectTwin falls back when NFS is down."""

    def __init__(self, base_url: str = DEFAULT_NFS_URL, timeout: float = 2.5) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def status(self) -> NFSStatus:
        try:
            r = requests.get(f"{self.base_url}/api/scenarios", timeout=self.timeout)
            if r.ok:
                return NFSStatus(True, self.base_url, "ok")
            return NFSStatus(False, self.base_url, f"HTTP {r.status_code}")
        except Exception as exc:  # noqa: BLE001
            return NFSStatus(False, self.base_url, str(exc))

    def text_causal(
        self,
        text: str,
        *,
        scenario: str = "calm",
        horizon: int = 3,
        infill: bool = False,
    ) -> dict[str, Any] | None:
        """POST /api/text_causal (or similar) — returns None on failure."""
        payload = {
            "text": text,
            "scenario": scenario,
            "horizon": horizon,
            "infill": infill,
        }
        for path in ("/api/text_causal", "/api/text-causal", "/api/step"):
            try:
                body = (
                    payload
                    if path != "/api/step"
                    else {
                        "scenario": scenario,
                        "horizon": horizon,
                        "text": text,
                        "infill": infill,
                    }
                )
                r = requests.post(
                    f"{self.base_url}{path}",
                    json=body,
                    timeout=max(self.timeout, 15.0),
                )
                if r.ok:
                    data = r.json()
                    data["_endpoint"] = path
                    return data
            except Exception:
                continue
        return None
