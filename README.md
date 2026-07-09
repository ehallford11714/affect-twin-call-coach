<p align="center">
  <img src="assets/logo.svg" alt="AffectTwin Call Coach" width="96" height="96" />
</p>

# AffectTwin Call Coach

**Real-time call/video coach: face/call KPIs to affect/intent proxies to suggested next utterance + expression preview.**

Package: `affecttwin` - Product **P10** in the causal research suite.

## Install

```bash
cd AffectTwinCallCoach
pip install -e ".[dev]"
pip install -e ".[ui]"
pip install -e ".[api]"
```

## Quick start

```bash
affecttwin dry-run --scenario stressed --goal support --offline
callcoach dry-run --scenario engaged --offline --svg-out out/expr.svg
affecttwin ui --port 8770
affecttwin serve --port 8771
```

## Docs

- [docs/SOTA.md](docs/SOTA.md) — state of the art notes for this product

## Suite

Part of the research product suite. Index: [PRODUCTS.md](../PRODUCTS.md) · GitHub: [affect-twin-call-coach](https://github.com/ehallford11714/affect-twin-call-coach)

## License

MIT