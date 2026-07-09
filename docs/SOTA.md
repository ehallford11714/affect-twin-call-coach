# AffectTwin Call Coach — SOTA notes

Research framing for **P10 AffectTwin Call Coach**: real-time call/video coaching from face/call KPIs → affect/intent *proxies* → suggested next utterance + expression preview.

**Related:** [FaceCause Studio](../../FaceCauseStudio/), [NextFrameSeq](../../NextFrameSeq/), EmotiveVision.

---

## 1. Affective computing (what is usable)

| Claim | Status |
|-------|--------|
| Dimensional affect (valence / arousal) from expression + context | **Partial** — improves with task instruments \(Z\) |
| Discrete emotion categories from face alone | **Weak** — Barrett reverse-inference limits; culture / display rules |
| Cognitive load / freeze proxies (motion drop, edge density, pauses) | **Medium** under controlled tasks |
| Rapport / engagement proxies for *coaching the user about themselves* | **Plausible** with consent + disclosure |
| Propositional thought / “what they mean” from face | **Not identifiable** |

**Working definition:** infer a low-dimensional latent \(T_t\) (affect + appraisal + coarse intent) that *correlates with* facial/call KPIs \(X_t\), under instruments \(Z\) and confounders \(U\) — then map \(\hat{T}_t\) to *suggestions*, never claims of ground-truth emotion.

---

## 2. Coaching agents

Lineage relevant to this product:

| Lineage | Idea | Relevance |
|---------|------|-----------|
| Motivational interviewing / sales enablement scripts | Rule libraries for next utterance | MVP suggestion tables |
| LLM coaching agents | Context-conditioned dialogue | Later: LLM rewrite of stubs |
| Multimodal call analytics (Gong-style) | Talk-listen ratios, topics | Call KPIs (`speaking_rate`, `pause_ratio`) |
| FaceCause / EmotiveVision | Face → proxy \(T\) | Shared measurement layer |
| NextFrameSeq `text_causal` | Text → face aspects | Optional expression preview path |

AffectTwin MVP is **measurement + proxy + suggestion**; generative rewrite and full AU fusion are later phases.

---

## 3. Ethics of emotion inference (non-negotiable)

1. **Language:** say *inferred appraisal / affect proxy / intent label* — never “what they are feeling/thinking.”
2. **Consent:** opt-in capture; no covert workplace / classroom surveillance framing.
3. **Audience:** prefer coaching the *user about their own* signals; third-party inference needs explicit consent UX.
4. **Limits disclosure:** UI, CLI, and API must surface epistemic limits (`notes`, `caution`, this file).
5. **Bias:** pixel KPIs entangle lighting, skin tone, disability, neurodiversity — keep confidence low without multimodal \(Z\).
6. **Dual use:** refuse covert emotion scoring for hiring / policing productization in this research line.

---

## 4. Reverse inference limits

Face → emotion is a classic **reverse inference** problem: many internal states can produce similar expressions; many expressions can arise without the labeled emotion.

Identification sketch (same spirit as FaceCause):

\[
X = f(T, U)+\varepsilon,\quad Z \perp U,\quad Z \not\perp T
\]

Without instruments \(Z\) (task context, self-report, conversation goal), \(\hat{T}\) is underdetermined. Coaching suggestions must therefore be **defeasible** and context-checkable.

---

## 5. Roadmap

| Phase | Deliverable |
|-------|-------------|
| **MVP** | Synthetic KPIs, affect proxies, utterance stubs, SVG preview, Streamlit/API, NFS client |
| P10.1 | EmotiveVision / AU fusion |
| P10.2 | LLM rewrite of suggestions with safety filters |
| P10.3 | Live webcam loop + talk-ratio audio KPIs |
| P10.4 | Consent UX + audit log |

---

## 6. Ports & integration

- NextFrameSeq API: **8765** (client only — do not bind)
- AffectTwin Streamlit: **8770**
- AffectTwin FastAPI: **8771**
