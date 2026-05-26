# Cross-client pattern-pick comparison — slidelab-intro brief
## v2 FedEx (2026-05-25) vs v2 ACN (2026-05-26) — apples-to-apples bounded-non-determinism datapoint

**Brief**: `slidelab-intro-shippable.md` (10 slides) — same brief, same forecasts, two different client templates.

**Hypothesis under test**: agents are influenced by **brief content** only, NOT by **client identity**. Significant divergence (≥ 8/10 different) would suggest agents are reading client signal (template colors, font name, project folder) and shifting picks. Minor divergence (1–2/10) confirms the bounded non-determinism documented in `DECISIONS.md`.

**Result**: **9/10 patterns identical at the geometric level**, 1 divergence inside the eligibility set, 1 directive-verb shift. Bounded non-determinism confirmed. Hypothesis supported.

---

## Side-by-side picks

| Slide | Title (truncated)                                        | FedEx pick                  | ACN pick                    | FedEx verb         | ACN verb           | Pattern diverged? | Verb diverged? |
|------:|----------------------------------------------------------|-----------------------------|-----------------------------|--------------------|--------------------|:-----------------:|:--------------:|
|     1 | Slide Lab (cover)                                        | Full canvas                 | Full canvas                 | summarize          | summarize          | —                 | —              |
|     2 | Section 1: The problem...                                | Full canvas                 | Full canvas                 | summarize          | summarize          | —                 | —              |
|     3 | Consultants spend... fighting templates                  | Full canvas                 | Full canvas                 | summarize          | summarize          | —                 | —              |
|     4 | Section 2: How Slide Lab inverts...                      | Full canvas                 | Full canvas                 | summarize          | summarize          | —                 | —              |
|     5 | Narrative is the spec                                    | Top band + body             | Top band + body             | summarize          | summarize          | —                 | —              |
|   **6** | **Two layers, one workflow** [architecture-test]       | **Horizontal bands**        | **Horizontal bands**        | summarize          | summarize          | —                 | —              |
|   **7** | **Three principles** [architecture-test]               | N-column row (3 cols)       | Vertical N-row stack        | summarize          | compare neutrally  | **YES** (within eligibility set) | **YES** |
|     8 | Build → Theme → QC → Review                              | N-column row                | N-column row (4 cols)       | show progress      | show progress      | —                 | —              |
|     9 | Two paths from brief to slides                           | 50/50 vertical              | 50/50 vertical              | compare neutrally  | compare neutrally  | —                 | —              |
|    10 | Start with /storyline-helper                             | Asymmetric vertical (75/25) | Asymmetric vertical (75/25) | recommend          | recommend          | —                 | —              |

**Pattern-level agreement**: 9/10 = **90%**
**Verb-level agreement**: 9/10 = **90%**
**Architecture-test slide agreement (6 + 7)**: 2/2 architecture tests passed in BOTH runs (agents overrode the wrong forecast in BOTH client contexts).

---

## Slide 7 divergence analysis (the only one)

**Brief signal**: "Three principles Slide Lab enforces" — parallel structure, no spatial hierarchy. Brief content is three principles with bold-lead + one-sentence elaboration per item.

**FedEx pick**: N-column row (3 columns), directive `summarize`.
**ACN pick**: Vertical N-row stack, directive `compare neutrally`.

**Both picks are within the documented eligibility set for this brief**:
- `layouts.md` "Use when" for **N-column row**: 3–9 parallel items, items fit horizontal columns, no hierarchy.
- `layouts.md` "Use when" for **Vertical N-row stack**: 3–9 parallel items with body text per item too dense for horizontal columns at the 14pt body-font floor.

The ACN agent's `_pattern_pick.md` explicitly reasoned: *"per-item body text (bold lead + one-sentence elaboration) too dense for N-column row at 14px floor"* — a content-driven judgment about column width vs body-text density. The FedEx agent treated the same content as compact enough for columns. **Both reads are defensible.** The eligibility-set boundary case worked exactly as the architecture intends — agents disagree at the margin without going off-pattern.

**Tie-break trail (ACN)**: seed-broke a tie with N-column row (the ACN agent noted: *"tied with N-column row; first hex `3`, 3 mod 2 = 1, alphabetical index 1 = 'Vertical N-row stack'"*). The seed-based tiebreak is documented per-slide deterministic.

**Tie-break trail (FedEx)**: no seed used; N-column row was the top scorer.

**Verb divergence**: FedEx agent saw the three principles as a `summarize` brief ("each principle as a hero-claim-like statement, oversized numeral as figure"); ACN agent saw them as `compare neutrally` ("identical row treatment, equal weight, no accent winner"). Both treatments produce equal-weight visualizations. Verb shift at the architecture-test boundary is within bounded variance.

---

## What this confirms

1. **Brief content drives picks**, not client identity. Client-template colors, font names, and project paths did not measurably shift the picks across 10 slides on the same brief.
2. **Bounded non-determinism is real and small**: 1 divergence in 10 picks, inside the eligibility set, with explicit pattern-pick reasoning preserved on both sides. This is what `DECISIONS.md` § "Variant rotation discipline" predicted.
3. **The architecture-test slides** (6 and 7) **passed in BOTH runs**: agents overrode the forecaster's wrong predictions (Full canvas for slide 6 → Horizontal bands; Org chart for slide 7 → list pattern) based on brief signal in both contexts. The forecast-as-context-not-constraint discipline holds across clients.
4. **The seed-tiebreak mechanism is doing useful work**: when two patterns are genuinely tied on signals, the seed lands the agent on a deterministic answer rather than introducing random variance.

---

## What this does NOT prove

- **Not a v1-vs-v2 comparison.** This is v2-vs-v2 across two clients. The actual A/B against v1 (FedEx slidelab-intro v1 vs v2 build, side-by-side review) is the next test, scheduled after Item 3 and the convergence-hold declaration.
- **Not a multi-brief comparison.** Both runs used the same brief. A second brief on the same two clients would test whether the convergence is brief-dependent (likely yes — different brief shape, different pattern picks, but the same client-independence should hold).
- **Not a verbatim option-content comparison.** This is pattern-level + verb-level. The actual python-pptx output differs in font (FedEx Sans vs Graphik), colors (FedEx purple/orange vs ACN deep-purple/bright-purple), and per-variant tilt detail. That's expected — same pattern, different brand chrome.

---

## Empirical signal for convergence-hold lift

Per `DECISIONS.md`, convergence-hold lifts when:
1. v2 produces verifiably correct output for FedEx and ACN on the slidelab-intro brief (this comparison + the two REVIEW.html files document that).
2. v2 produces verifiably correct output for FedEx on the trigger-brief (Item 1 documented in `smoke-test-finding-2026-05-25.md`).
3. NFL scope boundary is documented and routable (`nfl-scope-boundary.md`, this directory).

Items 1 + 2 + 3 close on Item 2's Stage 4 sign-off. Convergence-hold can lift to FedEx + ACN scope at that point, with the NFL boundary preserved per the scope doc.

The v1-vs-v2 A/B test is the *next* phase, not part of the convergence-hold lift decision.
