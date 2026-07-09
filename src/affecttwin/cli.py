"""AffectTwin Call Coach CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def cmd_dry_run(args: argparse.Namespace) -> int:
    from affecttwin.pipeline import AffectTwinPipeline

    pipe = AffectTwinPipeline(nfs_url=args.nfs_url, prefer_nfs=not args.offline)
    result = pipe.run(
        scenario=args.scenario,
        context_hint=args.context,
        goal=args.goal,
        try_nfs=False if args.offline else None,
    )
    print(json.dumps(result.to_dict(), indent=2))
    if args.svg_out and result.expression_preview.get("svg"):
        out = Path(args.svg_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result.expression_preview["svg"], encoding="utf-8")
        print(f"Wrote expression SVG -> {out}", file=sys.stderr)
    return 0


def cmd_from_image(args: argparse.Namespace) -> int:
    import cv2
    import numpy as np

    from affecttwin.kpi.frame import mine_frame_kpis
    from affecttwin.pipeline import AffectTwinPipeline

    bgr = cv2.imread(args.image, cv2.IMREAD_COLOR)
    if bgr is None:
        print(f"Failed to read image: {args.image}", file=sys.stderr)
        return 1
    kpis = mine_frame_kpis(bgr)
    pipe = AffectTwinPipeline(nfs_url=args.nfs_url, prefer_nfs=not args.offline)
    result = pipe.run(
        kpis,
        context_hint=args.context,
        goal=args.goal,
        try_nfs=False if args.offline else None,
    )
    print(json.dumps(result.to_dict(), indent=2))
    return 0


def cmd_sota(_: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[2]
    path = root / "docs" / "SOTA.md"
    if path.is_file():
        print(path.read_text(encoding="utf-8"))
        return 0
    print("docs/SOTA.md not found", file=sys.stderr)
    return 1


def cmd_ui(args: argparse.Namespace) -> int:
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print('Install UI extras: pip install -e ".[ui]"', file=sys.stderr)
        return 1
    import subprocess

    app = Path(__file__).resolve().parent / "app" / "streamlit_app.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app),
        "--server.port",
        str(args.port),
    ]
    return subprocess.call(cmd)


def cmd_serve(args: argparse.Namespace) -> int:
    try:
        import uvicorn
    except ImportError:
        print('Install API extras: pip install -e ".[api]"', file=sys.stderr)
        return 1
    uvicorn.run("affecttwin.app.api:app", host=args.host, port=args.port, reload=False)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="affecttwin", description="AffectTwin Call Coach")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("dry-run", help="CLI dry-run with synthetic KPIs")
    d.add_argument("--scenario", default="neutral", help="engaged|stressed|withdrawn|confused|neutral")
    d.add_argument("--context", default="", help="Context hint for intent")
    d.add_argument("--goal", default="", help="Coaching goal (e.g. close, support)")
    d.add_argument("--nfs-url", default="http://127.0.0.1:8765")
    d.add_argument("--offline", action="store_true", help="Skip NextFrameSeq API")
    d.add_argument("--svg-out", default="", help="Write expression preview SVG")
    d.set_defaults(func=cmd_dry_run)

    img = sub.add_parser("from-image", help="Mine KPIs from an image frame then coach")
    img.add_argument("image", type=str)
    img.add_argument("--context", default="")
    img.add_argument("--goal", default="")
    img.add_argument("--nfs-url", default="http://127.0.0.1:8765")
    img.add_argument("--offline", action="store_true")
    img.set_defaults(func=cmd_from_image)

    s = sub.add_parser("sota", help="Print SOTA research notes")
    s.set_defaults(func=cmd_sota)

    u = sub.add_parser("ui", help="Launch Streamlit UI (port 8770)")
    u.add_argument("--port", type=int, default=8770)
    u.set_defaults(func=cmd_ui)

    a = sub.add_parser("serve", help="Launch FastAPI (port 8771)")
    a.add_argument("--host", default="127.0.0.1")
    a.add_argument("--port", type=int, default=8771)
    a.set_defaults(func=cmd_serve)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
