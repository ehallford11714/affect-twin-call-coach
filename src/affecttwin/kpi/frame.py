"""Optional OpenCV frame → FaceKPIs (offline; no NFS required)."""

from __future__ import annotations

from typing import Any

import numpy as np

from affecttwin.kpi.synthetic import FaceKPIs


def mine_frame_kpis(bgr: np.ndarray, *, detect_face: bool = True) -> FaceKPIs:
    """Extract lightweight KPIs from a BGR frame."""
    import cv2

    if bgr is None or not isinstance(bgr, np.ndarray) or bgr.size == 0:
        return FaceKPIs(face_detected=False, face_ratio=0.0)

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY) if bgr.ndim == 3 else bgr
    lum_mean = float(gray.mean()) / 255.0
    lum_std = float(gray.std()) / 255.0
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(edges.mean()) / 255.0
    hist = cv2.calcHist([gray], [0], None, [32], [0, 256]).ravel()
    hist = hist / max(1.0, float(hist.sum()))
    entropy = float(-(hist[hist > 0] * np.log2(hist[hist > 0])).sum())
    texture = float(cv2.Laplacian(gray, cv2.CV_64F).var()) / 10000.0

    warmth = 0.0
    if bgr.ndim == 3 and bgr.shape[2] >= 3:
        b, _g, r = cv2.split(bgr[:, :, :3])
        warmth = float(r.mean() - b.mean()) / 255.0

    face_detected = False
    face_ratio = 0.0
    if detect_face:
        cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces):
            face_detected = True
            areas = [int(w) * int(h) for (_x, _y, w, h) in faces]
            face_ratio = float(max(areas)) / float(gray.shape[0] * gray.shape[1])

    return FaceKPIs(
        luminance_mean=round(lum_mean, 4),
        luminance_std=round(lum_std, 4),
        edge_density=round(edge_density, 4),
        entropy=round(entropy, 4),
        motion_score=0.0,
        motion_accel=0.0,
        face_ratio=round(face_ratio, 4),
        texture_energy=round(min(1.0, texture), 4),
        color_warmth=round(warmth, 4),
        stability=1.0,
        face_detected=face_detected,
        speaking_rate=0.4,
        pause_ratio=0.2,
        gaze_away=0.15 if face_detected else 0.5,
    )


def kpis_from_mapping(data: dict[str, Any]) -> FaceKPIs:
    """Build FaceKPIs from a partial dict (API / Streamlit)."""
    known = set(FaceKPIs.__dataclass_fields__)  # type: ignore[attr-defined]
    filtered = {k: v for k, v in data.items() if k in known}
    return FaceKPIs(**filtered)
