"""Streamlit MVP — AffectTwin Call Coach."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from affecttwin.client.nfs import NextFrameSeqClient
from affecttwin.kpi.synthetic import synthetic_kpis
from affecttwin.pipeline import AffectTwinPipeline

st.set_page_config(page_title="AffectTwin Call Coach", layout="wide")
st.title("AffectTwin Call Coach")
st.caption("face/call KPIs → affect/intent proxies → next utterance + expression preview")

with st.sidebar:
    nfs_url = st.text_input("NextFrameSeq API", "http://127.0.0.1:8765")
    prefer_nfs = st.checkbox("Prefer NextFrameSeq text_causal when available", True)
    scenario = st.selectbox(
        "Synthetic scenario",
        ["neutral", "engaged", "stressed", "withdrawn", "confused"],
    )
    goal = st.text_input("Coaching goal", "")
    context = st.text_input("Context hint", "")
    st.markdown("---")
    client = NextFrameSeqClient(nfs_url)
    st_status = client.status()
    if st_status.available:
        st.success(f"NFS up · {nfs_url}")
    else:
        st.warning(f"NFS down — offline coaching only\n({st_status.detail})")
    st.info("Affect proxies are not mind-reading. See docs/SOTA.md.")

src = st.radio("Input", ["Synthetic KPIs", "Upload frame", "Paste KPI JSON"], horizontal=True)

kpis = None
if src == "Synthetic KPIs":
    kpis = synthetic_kpis(scenario=scenario)
elif src == "Upload frame":
    up = st.file_uploader("Image / frame", type=["jpg", "jpeg", "png", "webp", "bmp"])
    if up is not None:
        import cv2
        import numpy as np

        from affecttwin.kpi.frame import mine_frame_kpis

        data = np.frombuffer(up.read(), dtype=np.uint8)
        bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if bgr is not None:
            kpis = mine_frame_kpis(bgr)
            st.image(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), caption="Input frame", width=280)
else:
    raw = st.text_area("KPI JSON", '{"color_warmth": 0.15, "motion_score": 0.1, "face_detected": true}')
    try:
        from affecttwin.kpi.frame import kpis_from_mapping

        kpis = kpis_from_mapping(json.loads(raw))
    except Exception as exc:  # noqa: BLE001
        st.error(f"Invalid JSON: {exc}")

if kpis is not None and st.button("Coach", type="primary"):
    pipe = AffectTwinPipeline(nfs_url=nfs_url, prefer_nfs=prefer_nfs)
    result = pipe.run(kpis, context_hint=context, goal=goal, scenario=scenario)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Suggested next utterance")
        st.write(result.suggestion.utterance)
        st.caption(result.suggestion.rationale)
        if result.suggestion.alternatives:
            st.markdown("**Alternatives**")
            for alt in result.suggestion.alternatives:
                st.write(f"- {alt}")
        st.warning(result.suggestion.caution)
    with c2:
        st.subheader("Expression preview")
        st.write(result.suggestion.expression_cue)
        st.components.v1.html(result.expression_preview.get("svg", ""), height=180)
        if result.nfs_used:
            st.success("Linked NextFrameSeq text_causal")
        else:
            st.caption("NFS not used (offline or unavailable)")

    st.subheader("Insight")
    st.write(result.insight)
    st.subheader("Affect / intent proxies")
    st.json(result.affect.to_dict())
    st.subheader("KPIs")
    st.json(result.kpis.to_dict())
