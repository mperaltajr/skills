# v2 smoke-test finding — 2026-05-25

Smoke test: slidelab-intro brief × FedEx template × v2 pipeline. Stage 2 (parallel agent dispatch) complete; this doc captures the architectural findings before Stage 3.

---

## Headline result

**v2 works end-to-end through Stage 2.** 10 parallel agents, 30 option scripts produced, no SKELETON_REJECTED, no FALLBACK_MERMAID needed for this brief. All script headers honor the convention. All `_pattern_pick.md` files captured.

## Architecture-test slides — both PASS

The two diagnostic slides where the prep-time forecaster missed:

### Slide 6 — Expected `Horizontal bands`

- Forecaster predicted: `Full canvas` (missed — keyword "stacked horizontal rows" not in forecaster vocab)
- Agent picked: **`Horizontal bands`** ✅
- Agent reasoning: cited "editorial_emphasis explicitly demands 'two stacked horizontal rows'" + treated editorial_emphasis as load-bearing brief content (Hardline #4 brief fidelity). Adjacency: "overrides hint — prior slides 4 and 5 forecast Full canvas; Horizontal bands breaks that run."

### Slide 7 — Expected `Vertical N-row stack` or `N-column row`

- Forecaster predicted: `Org chart (hierarchical)` (wrong — brief explicitly says "no spatial hierarchy")
- Agent picked: **`Vertical N-row stack`** ✅ (via seed tiebreak between N-column row and Vertical N-row stack)
- Agent reasoning: caught "Full canvas can't carry enumerated content per its 'Do not use for' line"; used hex-character mod 2 tiebreak per the closed protocol.

**Conclusion.** The "agent overrides forecaster when brief signal is clear" architecture works. v2 doesn't need a smarter forecaster to ship — the forecaster is correctly serving as advisory context, and the agent's own scoring pass wins when the forecaster is wrong.

---

## New finding — adjacency-context staleness

**Problem.** Slides 1, 2, 3, 4 all picked `Full canvas`. That's 4 consecutive same-pattern slides, violating Hardline #3 (no 3+ consecutive same-split).

**Per-slide reasoning trace:**

| Slide | Pick | Adjacency log |
|---|---|---|
| 1 | Full canvas | no prior context — first slide |
| 2 | Full canvas | "matches hint (slide 1 forecast was Full canvas; this is 2-in-a-row, allowed)" |
| 3 | Full canvas | "would-be-3-in-a-row, kept anyway because top scorer" — agent recognized the violation, chose brief fidelity per § 4.3 |
| 4 | Full canvas | "matches hint (slide 2 forecast was Full canvas; **slide 3 is Top band + body**; slide 4 = Full canvas is 2-of-last-3, not 3-in-a-row — allowed)" |

**Root cause.** Slide 4's agent reasoned against slide 3's *forecast* (Top band + body), not against slide 3's *actual pick* (Full canvas). The `{{LIKELY_PRIOR_PATTERNS}}` injection in each prompt carries the prep-time forecaster's output, not the agents' actual picks. When the forecaster and an agent diverge — which happens any time the brief signal is stronger than keyword heuristics — downstream agents reason against stale data.

This is by design today: `build_deck.py` runs the forecaster once at prep time, *before* any agent dispatches. Agents run in parallel after that; no agent sees the others' actual picks. The post-hoc adjacency check in `finalize_deck.py` is supposed to catch the result and surface it in REVIEW.html. It will catch this case (4 consecutive Full canvas → flagged).

**Severity.** Soft. Hardline #3 is enforced at finalize time, not pick time, by explicit design choice (see SKILL.md § "Classifier" and DECISIONS.md § "Variant rotation discipline"). The user sees the adjacency warning in REVIEW.html and decides per-slide whether to pick different options or send specific slides back for regen.

**But the data point matters.** Three of the four Full-canvas slides genuinely *should* be Full canvas (cover + 2 section dividers); only slide 3 is debatable (the 70%-finding hero — could equally be Top band + body with 70% in the band). The adjacency violation is real, but it's a property of *this brief* (one cover + two dividers + one hero finding clustered in the first 4 slides), not a bug in the agents.

**Mitigations to consider for v0.1:**

1. **Tighter prep-time forecaster.** If the forecaster's hit rate were higher, agents would have better adjacency context. But on the same architecture-test, agents correctly override the forecaster when it's wrong — so a tighter forecaster mainly helps the *next* slide reason about *this* one's likely pick. Marginal benefit.

2. **Serial agent dispatch with state passing.** Each agent learns the prior agent's actual pick before dispatching. Defeats parallelism — the whole point of v2's 10× fanout. Hard "no."

3. **Two-pass dispatch with post-hoc rebalancing.** Round 1: agents pick freely in parallel. Round 2: re-dispatch any slide in a 3+ run to pick a different pattern. Doubles cost for the affected slides. Possibly worth it for production. Defer to v0.1 after more A/B data.

4. **Document the staleness in prompt.md explicitly.** Add a note: "The LIKELY_PRIOR_PATTERNS field is the prep-time forecast, NOT the actual picks. Other agents may have overridden their forecasts. Treat this as a weak signal; trust your own brief read." This is honest but doesn't fix the violation — just helps agents calibrate.

5. **Accept the post-pass behavior.** Finalize-time adjacency check + REVIEW.html surfacing IS the architecture's answer. It worked here — finalize will catch slides 1-2-3-4. User resolves by picking a different option for one of those slides at review time.

**Recommended action.** No change to architecture today. Note this finding; revisit after 2-3 more real briefs run through v2. If staleness consistently produces 3+ runs that require manual resolution, escalate to option 3 (two-pass).

---

## Classification rollup

| Status | Count |
|---|---|
| Native (built normally) | 30 / 30 |
| FALLBACK_MERMAID | 0 |
| SKELETON_REJECTED — ambiguous intent | 0 |
| SKELETON_REJECTED — brief/pattern disagreement | 0 |
| SKELETON_REJECTED — no Mermaid analogue (fishbone / concentric) | 0 |

No fallback triggered. The slidelab-intro brief is entirely native-pattern-buildable. This means **the Mermaid fallback path is not exercised in this smoke test** — that's a separate validation gap. The brief doesn't have a hub-spoke, Porter's, ecosystem, or free-form network slide. To exercise the Mermaid path, a separate test brief is needed.

## Directive-verb distribution

| Verb | Slides | Notes |
|---|---|---|
| `summarize` | 1, 3, 4, 5 | Used 4× — heavily weighted to cover/dividers and hero-claim slides |
| `compare neutrally` | 6, 7, 9 | Used 3× — bands, list of three, two-path comparison |
| `diagnose` | 2 | Used 1× — section divider for "problem with how decks get built" |
| `show progress` | 8 | Used 1× — process flow |
| `recommend` | 10 | Used 1× — CTA |
| `warn` | (none) | Not exercised by this brief |
| `show urgency` | (none) | Not exercised by this brief |

5 of 7 verbs exercised. The brief doesn't argue from danger or deadline, so `warn` and `show urgency` don't show up — that's brief-shape, not verb-vocabulary failure.

## Seed tiebreaker exercised

Slide 7 used the pattern-pick seed for tiebreak (between `N-column row` and `Vertical N-row stack`). First hex char `3` mod 2 = 1; sorted alphabetically, index 1 = `Vertical N-row stack`. Deterministic; reproducible.

## Next step

Gate 2 PASS recommended. Proceed to Stage 3 (finalize_deck.py) for visual verification via GATE3-PREVIEW.html.

The adjacency violation on slides 1-2-3-4 is a known finding and will surface in REVIEW.html via the post-pass adjacency check (already implemented in `build_review.py`). No mid-pipeline halt needed; the architecture's existing mechanism handles it at the right gate.

---

# Stage 3 outcome — HALTED at Gate 3 (failed visual fidelity gate)

Stage 3 fired against the existing option scripts from Stage 2. Result: **12 of 30 options built; 18 failed.** Three failure modes traced to a single root cause.

## Critical Finding A — prompt.md ↔ finalize_deck.py contract mismatch (sys.argv[1])

**Root cause.** `prompt.md` § 8 said: *"Saves the slide as a standalone PPTX at the path passed in as `sys.argv[1]` (`finalize_deck.py` provides this)."* But `finalize_deck.py` invokes scripts with **no command-line arguments** and looks for the literal filename `option_<X>.pptx` next to the `.py`. The contract was ambiguous; three valid agent interpretations emerged:

| Slides | Agent footer pattern | Result |
|---|---|---|
| 1, 7, 8, 9 | `out = sys.argv[1] if len(sys.argv) > 1 else "option_<X>.pptx"` | Built (12 options) |
| 2, 3, 5, 6, 10 | `out = sys.argv[1] if len(sys.argv) > 1 else "slide_NN_option_X.pptx"` | "Script ran but no .pptx produced" (15 options) — wrote to wrong filename |
| 4 | `build(sys.argv[1])` — no fallback | `IndexError: list index out of range` (3 options) |

All three are *valid* implementations of the ambiguous prompt. The bug is the contract itself.

**Fix landed.** `prompt.md` § 8 step 4 rewritten to specify the exact output filename (`option_A.pptx`, `option_B.pptx`, or `option_C.pptx`) with explicit "do NOT use sys.argv[1]" and a concrete `if __name__ == "__main__":` example. Step 2 also corrected (was "opens the client template" — actually scripts use `new_slide()` and finalize handles the graft).

**Contract audit performed** to surface any OTHER mismatches. Findings:

| Contract | Status |
|---|---|
| Script invocation (sys.argv) | **BUG — fixed** |
| Output filename convention | **BUG — fixed** |
| "Opens client template" wording in § 8 step 2 | **Doc drift — fixed** |
| Constraint phrasing "Touch only option_*.py" | **Mild drift — clarified to "files in OUTPUT_DIR"** to permit `.mmd` siblings + `.pptx` outputs |
| `SKELETON_REJECTED` token format | ✅ matches `finalize_deck.py::SKELETON_REJECTED_TOKEN` |
| `FALLBACK_MERMAID` token format | ✅ matches `finalize_deck.py::FALLBACK_MERMAID_TOKEN` |
| Sibling `.mmd` filename / location | ✅ matches `py.with_suffix(".mmd")` |
| Header line 1 (pattern) | ✅ matches `build_gate_preview.py::_PATTERN_LINE_RE` (em-dash + hyphen accepted) |
| Header line 2 (Variant) | ✅ matches `_VARIANT_LINE_RE` |
| Header line 3 (Brief fidelity check) | ✅ not parsed by any downstream; metadata-only |
| PATTERN PICK field names | ✅ matches `_PATTERN_PICK_FIELD_RE` (verified end-to-end in Stage 2 capture) |

Only one critical contract bug + one doc-drift line + one constraint-phrasing tightening in the audit. Re-run after fixes should be clean.

## Empirical Finding B — v1 client_theme loader works correctly for FedEx in practice

The user's Gate 3 watch-item asked: do rendered colors come out (1) purple primary + orange accent (correct), (2) orange primary + purple accent (loader inversion bug), or (3) some other broken mapping?

**Observed on the 12 successful builds:**

- **Slide 1 cover (option A):** PURPLE canvas + WHITE hero + ORANGE counter-line + soft-purple tagline. Canonical FedEx.
- **Slide 9 (option A):** PURPLE side-headers + dark gray title + gray body. Canonical FedEx.
- **Slide 7 (option A):** dark-gray title + RED/CORAL principle names (~#C74755) + gray body. The red is `BRAND_PRIMARY_MID` → through the theme color_map → resolves to FedEx `accent3` (coral), NOT a darker shade of purple.

**Verdict: outcome (1).** The v1 `client_theme.py::load_client_theme` correctly maps `dk2 → BRAND_PRIMARY = #4D148C` (purple) and `lt2 → BRAND_ACCENT = #FF6600` (orange) for the FedEx Moving Forward template. The console output confirms:

```
raw dk2=4D148C  lt2=FF6600
brand_primary=#4D148C (source: dk2)
brand_accent =#FF6600 (source: lt2)
```

**Cross-stream data point.** The v1 loader bug surfaced in v1's `register_template.py` smoke test is *theoretical for the FedEx case in production v2 builds*. The dk2/lt2 → primary/accent mapping happens to be correct for FedEx's actual template slot layout. **This does NOT mean the loader is bug-free** — other clients (Accenture, NFL, any non-convention template) may still inherit the bug. v1's `brand.yml` rewrite remains architecturally valuable.

For v2's FedEx smoke specifically: brand fidelity is intact for the purple/orange pair. The architectural concern that motivated `validate_theme()` (theoretical wrong-color shipping) is empirically absent for this client. v2's belt-and-braces guard correctly produced no warning.

## Architecture finding C — BRAND_PRIMARY_MID semantic drift through theme remap

Slide 7's principle names landed in red/coral, not the darker-purple shade an agent reasonably expects from a token named `BRAND_PRIMARY_MID`. Mechanism:

1. Agent writes `color=BRAND_PRIMARY_MID` (an enum constant imported from `twins/helpers.py`).
2. `twins/helpers.py` has a hardcoded hex for `BRAND_PRIMARY_MID` (whatever the helper module decided that should be).
3. `finalize_deck.py`'s `graft_and_theme()` step calls `apply_theme_to_shape_xml(color_map, ...)` — this rewrites every srgbClr hex in the slide XML through the theme's color_map.
4. The color_map for FedEx maps the hardcoded `BRAND_PRIMARY_MID` hex to FedEx `accent3` (likely `#C74755`, a coral/red), not to a darker purple.

The token NAME implies "primary mid" — a shade between BRAND_PRIMARY and a lighter tint. The token VALUE after theme remap can be any color in the client palette. The semantic drift is between agent expectation ("a darker version of brand primary") and actual resolution ("whatever the theme.color_map maps the hardcoded hex to, which can be any of accent3/4/5").

**v0.1 follow-up.** Either:
- Document `twins/helpers.py` palette token resolution paths explicitly (each token → what theme slot it maps through). Agents would then make informed choices.
- Rename tokens so they don't imply specific brand-color relationships. `MID_TONE_3` instead of `BRAND_PRIMARY_MID`.
- Add a deterministic palette mapping that honors the name: `BRAND_PRIMARY_MID` always resolves to a luminance-shifted version of `BRAND_PRIMARY`, never to `accent3`.

None blocking for v0; the empirical finding is just that **brand color rendering for FedEx is correct for primary + accent but unexpected for "mid" tones**. Worth documenting.

## Architecture finding D — QC self-check false-positives on cover/divider slides

Slide 1 (cover) blocked QC with `PNG too small (38KB; floor 50KB)`. Cover slides are sparse-by-design (dark canvas + one hero word + thin accent rule + small chrome) → PNG file size naturally small. The 50KB heuristic was calibrated for typical body slides, not sparse-type covers.

Additional warnings on slides 1 and 9 hit the `body_font_floor ≥ 10.5pt` rule against legitimate chrome elements (e.g., a 9pt italic `[Date]` placeholder on the cover, which is correctly tiny because it's a placeholder waiting for a real date).

**v0.1 follow-up.** Make `slide-qc`'s self-check cover-aware:
- Detect cover/divider slides (low shape count + dark canvas + 1-2 hero text shapes) and lower the PNG size floor for them.
- Treat 9-10pt italic placeholder text on covers as documented chrome, not body-font-floor violations.

The current QC heuristics are too strict for the sparse end of the layout spectrum. Not blocking v0; produces noisy false-positive blocks on cover slides.

## Summary of v0.1 backlog from this smoke

1. **Contract audit becomes part of build hygiene** — any time `prompt.md` or `finalize_deck.py` change, run the audit checklist above to catch new contract drift before re-dispatching agents.
2. **`twins/helpers.py` palette token semantics** — document or rename tokens so agents know what colors resolve through the theme.
3. **`slide-qc` cover-aware heuristics** — PNG size floor and body-font floor need to skip or relax for sparse-type slides.
4. **Forecaster vocab** (carried over from Gate 1 finding) — keywords like "stacked", "workstream", "lever" not in forecaster signal table; produces low-confidence forecasts on real-brief language. Adjacency context is weaker than design assumed but post-pass at finalize catches it.
5. **Slide 8 agent free-text typo** (carried over from Gate 2) — "N-column row (5)" vs "(4 columns)" inconsistency in agent's own annotation; doesn't affect build.

## Next action

Re-run Stage 1 → Stage 2 → Stage 3 with the corrected prompt.md. Watch-item at the re-run Gate 3: **30/30 builds.** Anything less means there's a contract issue the audit missed.

---

# Re-run outcome — Gate 3 PASS

After applying the prompt.md contract fix (§ 8 step 4 specifies exact `option_<X>.pptx` filename, no sys.argv) + doc-drift fixes on § 8 step 2 and § 9 constraint phrasing, the full pipeline re-ran.

## Headline result

**30 / 30 builds. 30 / 30 themed. 30 / 30 rendered.** The contract fix is empirically validated end-to-end. Stage 2 leading indicator was 8 of 10 agents pre-running their scripts during dispatch (proof the corrected pattern works at source level); Stage 3 confirmed all 30 execute cleanly via `finalize_deck.py`'s subprocess invocation.

## Architecture-test slides — both confirmed visually

- **Slide 6 (Horizontal bands):** renders as two parallel CARD_BG-tinted panels with PURPLE 01/02 numerals, dark-gray headings, italic gray subheaders, bulleted text on the right, and an ORANGE accent rule between the panels as the single accent moment. Faithful to the brief's "two stacked horizontal rows" framing. Forecast-override behavior confirmed at PNG-render level.
- **Slide 7 (N-column row, 3 columns):** renders as three parallel columns with PURPLE numerals, ORANGE accent track across the top, dark-gray principle names (NOT coral this run — see non-determinism note below), gray body. No spatial hierarchy. Faithful to "list of three principles, parallel structure" framing. Forecast-override behavior confirmed at PNG-render level.

Both architecture-test slides cross the PNG-render gate cleanly. The forecast-as-context-not-constraint design holds under real agent + LibreOffice render conditions.

## Color confirmation — outcome (1) sustained

**Purple primary + orange accent across the deck.** Console output confirms loader behavior:

```
raw dk2=4D148C  lt2=FF6600  font=FedEx Sans
brand_primary=#4D148C (source: dk2)
brand_accent =#FF6600 (source: lt2)
```

Visually validated on slides 1, 6, 7 (PNG inspection): all show canonical FedEx purple/orange. v1's `client_theme.py` mapping is empirically correct for the FedEx template — the theoretical loader bug does not bite in practice for this client. v1's `brand.yml` rewrite remains architecturally valuable for non-FedEx clients (Accenture, NFL, etc.) where the slot convention may differ.

## QC self-check rollup

| Status | Count | Notes |
|---|---|---|
| ok | 23 | |
| warn-only | 3 | slide 6/option_B, slide 9/option_A, slide 9/option_B |
| BLOCK | 4 | slide 1 (all 3 options) + slide 4/option_B |

All 4 BLOCKs are the **known v0.1 cover/divider false-positive pattern** — PNG too small (38KB / 38KB / 38KB / 48KB; all below the 50KB floor). Sparse-by-design slides naturally produce small PNG files. Not a real failure. Documented in this file as Architecture finding D.

## Architecture finding C (BRAND_PRIMARY_MID coral) — did NOT recur

Last run, slide 7's principle names rendered in coral/red because the agent used `BRAND_PRIMARY_MID`, which the theme color_map remapped to `accent3` (~#C74755). This run, the slide 7 agent used `TEXT_DARK` for the principle names instead — they render dark gray, as semantically expected.

**Implication:** the coral issue is not deterministic; it depends on which palette token the agent chooses. This is consistent with the broader non-determinism finding below. The semantic-drift problem is real but only surfaces when an agent happens to pick the affected token. v0.1 fix (rename/document tokens) still warranted to prevent future agents from hitting it.

## New v0.1 finding — agent pattern-pick non-determinism

Comparing the two runs of the same brief through v2:

| # | Title | Run 1 pick | Run 2 pick | Same? |
|---|---|---|---|---|
| 1 | Slide Lab | Full canvas | Full canvas | ✅ |
| 2 | Section 1 divider | Full canvas | Full canvas | ✅ |
| 3 | 70% hero finding | Full canvas | Full canvas | ✅ |
| 4 | Section 2 divider | Full canvas | Full canvas | ✅ |
| 5 | Narrative is the spec | Top band + body | Top band + body | ✅ |
| 6 | Two layers | Horizontal bands | Horizontal bands | ✅ pattern, ⚠ different directive verb (compare neutrally → summarize) |
| 7 | Three principles | Vertical N-row stack | N-column row (3) | ⚠ different pattern (both eligible) |
| 8 | Build → Theme → QC → Review | N-column row | N-column row | ✅ |
| 9 | Two paths | 50/50 vertical | 50/50 vertical | ✅ |
| 10 | Start with /storyline-helper | Full canvas | Asymmetric 75/25 | ⚠ different pattern (both valid) |

**Variance sources:**
- **Forecaster:** zero (deterministic keyword heuristic — same brief produces identical forecasts every run).
- **Seed-tiebreak:** zero (same seed math, same hex digest, same modulo result).
- **Agent pattern-pick reasoning:** stochastic (LLM token sampling produces different valid narrative reasoning paths; the closed 7-verb directive vocab + brief signal bound the variance but don't eliminate it).

**8 of 10 slides picked the same pattern across runs.** The two divergences (slides 7 and 10) both landed on alternative patterns that are valid per `layouts.md`'s "Use when" criteria for those briefs. No agent picked a pattern the brief excludes.

**Architecture interpretation.** The closed 7-verb vocabulary + brief-signal anchoring keep variance bounded but not absolute. Two runs of the same brief through v2 will not produce byte-identical PATTERN PICK metadata. This is consistent with the design intent — agents are reasoning about pattern fit, not computing a deterministic classifier — but worth recording.

**v0.1 candidate fixes (not blocking for current architecture):**

- **Option 1:** tighten agent picking discipline via explicit numeric scoring. Replace narrative "top signals" reasoning with a numeric rubric ("brief signal X = N points"); pick the highest sum. Deterministic given the brief, but ports v1's chassis-vocab failure mode (formalized scoring that doesn't match what works visually).
- **Option 2:** accept bounded variance as architectural feature. Multiple valid patterns CAN win on the same brief — that's a strength, not a bug, because the user picks per-slide at REVIEW.html. Document the non-determinism explicitly; train users to expect it.
- **Option 3:** lower-temperature dispatch. Re-dispatch the same brief at LLM `temperature=0` would converge picks across runs (fewer reasoning-path variations). Easy to implement; reduces aesthetic diversity in variant generation too — possibly a feature, possibly a bug.

**Recommendation:** Option 2 (accept the variance) for v0.1. Document it. Revisit if cross-run reproducibility becomes a real user-facing requirement (e.g., deck consistency across feedback iterations of the same brief).

## v0.1 follow-ups updated

The original v0.1 list (in the "Summary of v0.1 backlog from this smoke" section above) extended with:

6. **Agent pattern-pick non-determinism** — bounded by closed vocab + brief signal but not absolute. Accept as architectural feature (recommendation) or escalate to Option 1/3 if needed.
7. **`twins/helpers.py` BRAND_PRIMARY_MID semantic drift** — already noted; confirmed this run that the issue is agent-token-choice-dependent, not deterministic. Token rename or doc-the-actual-resolution-path is the fix.

## Final smoke verdict

**v2 is empirically shippable for A/B testing.** The full pipeline works end-to-end against a real brief + real client template: brief → 10 prompts → 30 option scripts → 30 themed PPTXs → 30 PNGs → REVIEW.html (Stage 4 pending visual approval).

Contract bugs caught and fixed in v0. Empirical color fidelity validated for FedEx. Architecture-test slides 6 + 7 visually confirmed. Adjacency advisory mechanism working (1 surfaced on the cover-heavy run-of-Full-canvas at slides 1-4). 4 QC false-positives all the same known v0.1 cover-aware-heuristic issue.

The architecture is ready for first real A/B against v1 once Mario green-lights Stage 4 (build_review.py → final REVIEW.html).

---

# Post-Stage-4 findings — additional defects caught at Gate 4

After firing Stage 4 (build_review.py), the resulting REVIEW.html reported `missing PNGs: 30, missing themed PPTX: 30` — every option tile a placeholder. Investigation surfaced a fourth Category 1 defect that the Gate 3 audit had missed (the Gate 3 audit was scoped to prompt.md ↔ finalize_deck.py; it didn't cover finalize_deck.py ↔ build_review.py or finalize_deck.py ↔ compile_picks.py).

## Category 1 — four defects, all addressed in one fix pass

### Defect 1: Slide 1 option A renders with zero brand color

Confirmed by source inspection. `slide_01/option_A.py` uses TEXT_DARK / TEXT_MID / TEXT_FAINT exclusively. Imports `BRAND_PRIMARY`, `BRAND_ACCENT` etc. but never uses them. The agent's variant description was "light canvas, left-aligned, no counter-line, standard typography (safe default)" — and "safe default" drifted into "no brand identity at all."

The previous Gate 3 report's QC BLOCK on slide 1 was attributed to the sparse-cover false-positive (PNG < 50KB). That diagnosis was partially correct — covers are sparse-by-design — but **the PNG was also small because there was literally no brand fill, no accent stripe, no purple anywhere.** Options B and C use brand colors (verified visually in Gate 3 PNGs).

**Fix applied:** `prompt.md` § 5 gained a new bullet (Reviewer C's revised 85-word version) explicitly requiring at least one brand token on a load-bearing element per variant, excluding placeholder/meta surfaces, and requiring brand application to vary across the three variants. This addresses the "safe default → no brand identity" agent interpretation drift.

### Defect 2: Adjacency unfixable at REVIEW.html (v0.1 architectural gap)

All 12 options across slides 1-4 in the re-run were Full canvas. The architecture says "user picks alternative pattern at REVIEW.html to resolve 3+ consecutive same-pattern adjacency violations" — but when every option for every adjacency-affected slide is on the SAME pattern, the user has no escape hatch.

This is a real architecture gap. **Not fixed in v0.** Documented as v0.1 candidate:

> **v0.1 candidate.** `build_deck.py` flags adjacency-risk slides at prep time (a slide whose forecasted pattern matches the prior two slides' forecasted patterns). The per-slide prompt gains a section instructing flagged slides to require ONE of the 3 options on a pattern from a different family. The agent picks two variants within the dominant pattern + one variant on the alternative pattern, giving the user a real escape hatch at REVIEW.html.

For the current smoke: the 4-in-a-row Full canvas finding surfaces in REVIEW.html's adjacency advisory banner; user resolves by picking different options where possible OR by sending one of slides 1-4 back for regen.

### Defect 3: Color-recurrence reporting was sloppy in this doc

The original Gate 3 report wrote: *"This run's agent used TEXT_DARK for the principle names — they render dark gray, as semantically expected."*

That conflated two design elements. Correct trace of `slide_07/option_A.py`:

```python
# Numeral anchor — large, brand-primary (line 57)
add_text(slide, f"numeral-{i}", numeral,
    font_size_pt=42, color=BRAND_PRIMARY, bold=True, ...)

# Claim — bold short sentence (line 65)
add_text(slide, f"claim-{i}", claim,
    font_size_pt=16, color=TEXT_DARK, bold=True, ...)
```

**Slide 7 this run** (pattern = N-column row 3 columns): numerals use `BRAND_PRIMARY` (purple); claim text (principle names like "Governing thought is mandatory.") uses `TEXT_DARK` (dark gray). Two separate elements, two separate colors.

**Slide 7 previous run** (pattern = Vertical N-row stack): a different agent on a different pattern chose `BRAND_PRIMARY_MID` for the principle name TEXT. That token resolved to coral (~#C74755) via the theme color_map.

The "BRAND_PRIMARY_MID coral didn't recur" finding holds at the architectural level: no agent in this run chose `BRAND_PRIMARY_MID` for any rendered element. But the per-element color attribution in the original report was muddled — the numerals on slide 7 this run ARE in BRAND_PRIMARY purple; only the principle name text uses TEXT_DARK. **Correcting the record.**

### Defect 4: build_review.py and compile_picks.py read from wrong path

After firing Stage 4, REVIEW.html reported every option tile as missing. Root cause: `build_review.py:297` reads `out_dir / "themed" / slide_id` and `compile_picks.py:210` reads `out_dir / "themed" / key / f"option_{letter}.pptx"`. But `finalize_deck.py:416-417` writes to `slide_dir / f"option_{letter}.pptx"` — no `themed/` subdir.

**Same kind of fork-time inheritance bug as the prompt.md sys.argv contract bug**, in a different pair of files. v1 used a `themed/` subdir convention; v2's `finalize_deck.py` migrated to writing themed PPTX/PNG directly into `slide_NN/` (raw goes to `_raw/` subdir), but the v2 `build_review.py` and `compile_picks.py` forks preserved the old read-side assumption.

**Fix applied:** one-line replacement at `build_review.py:297` (`themed_dir = src_dir`) + one-line deletion at `compile_picks.py:210` (drop `"themed" /`) + 2 docstring lines at `compile_picks.py:8,17` updated to drop the stale path-comment drift. Lines 26, 28, 160, 203 in `compile_picks.py` use "themed" as a semantic adjective (the PPTX has been theme-remapped) and are NOT path drift — unchanged.

### Underlying disease — no shared `paths.py`

Reviewer A's diagnosis: each of the three forked scripts independently encodes path assumptions about where artifacts live. Drift between them is structurally impossible to prevent. Extract a `paths.py` module locking artifact-layout constants:

```python
# paths.py (v0.1 candidate)
THEMED_PPTX_PATH = lambda out_dir, slide_n, letter: out_dir / f"slide_{slide_n:02d}" / f"option_{letter}.pptx"
THEMED_PNG_PATH  = lambda out_dir, slide_n, letter: out_dir / f"slide_{slide_n:02d}" / f"option_{letter}.png"
RAW_PPTX_PATH    = lambda out_dir, slide_n, letter: out_dir / f"slide_{slide_n:02d}" / "_raw" / f"option_{letter}.pptx"
MMD_PATH         = lambda out_dir, slide_n, letter: out_dir / f"slide_{slide_n:02d}" / f"option_{letter}.mmd"
# ... etc
```

All three scripts (`build_deck.py`, `finalize_deck.py`, `build_review.py`, `compile_picks.py`, `build_gate_preview.py`) import from `paths.py`. Drift becomes a compile-time error rather than a silent semantic bug discovered at Gate 4. **v0.1 candidate, paired with v1's `paths.py` extraction if v1 takes the same step.**

## Cross-stream finding — v1 has the identical bug

Reviewer B checked v1 for the same pattern and found it at parallel-shape line numbers:

- `slide-builder/scripts/build_review.py:243` — same `out_dir / "themed" / slide_id` mistake
- `slide-builder/scripts/compile_picks.py:202` — same path-segment drift

Per v1's commit log (`7dcbec9` — *"Swap themed PPTX to the obvious slide_NN path; raw goes to slide_NN/_raw/"*), v1's finalize_deck.py was migrated to the obvious-path convention but the reader side was never updated. **v1's REVIEW.html has been broken since that commit** — either v1 hasn't been run end-to-end since then, or someone has been tolerating missing thumbnails as cosmetic.

Fix shape is identical to the v2 fixes: one-line per file at `build_review.py:243` and `compile_picks.py:202`. **Outside v2's scope to apply** — flagged for the v1 chat to take on its own timeline. Worth pairing with the brand.yml + register_template.py theme rewrite work since both touch the same `twins/` neighborhood and a `paths.py` extraction would prevent the next instance of this disease in either fork.

## Gate 3 audit scope gap — note for future smoke runs

The Gate 3 audit was scoped to prompt.md ↔ finalize_deck.py only. That caught the sys.argv contract bug at Stage 3 but missed the read-side path drift in build_review.py and compile_picks.py. **The Gate 4 fire is itself a gate** — it catches contract drift that the prep-time audit didn't predicate-check.

**Future smoke runs should pre-fire Gate 4 against the empty-PNG state** to surface read-side path bugs before agent dispatch costs are sunk. Or run the predicate-grep audit across ALL forked scripts, not just the pair-touched ones. The 5-grep audit pattern from this session (path contract / filename contract / slide-N format / token field-names / hardcoded paths) is the right harness — apply it to every script pair in the pipeline, not just the prep ↔ build pair.

---

# Hardline #4 recalibration — empirical correction

Surfaced while costing Category 2 item 4 (brief-fidelity measurement). The reviewer-trio synthesis pushed back on running the measurement on slidelab-intro specifically (ritual on synthetic data) and instead landed on recalibrate-without-measuring with v2-native re-validation deferred to items 1 + 2 smoke outputs.

## Original claim was empirically false

v2's `SKILL.md`, `prompt.md` § 6, and `DECISIONS.md` all stated **"Brief fidelity ≥ 0.92"** as Hardline rule #4. This number was inherited from a v1 strawman document and **was never empirically validated** before being carried into v2's hardline rules.

Cost-check inspection of `slide-builder/tests/gate4/check_brief_fidelity.py` (the actual fidelity-checking script in v1) reveals:

```python
PER_SLIDE_MIN = 0.30  # Recalibrated 2026-05-25 (twice) post Gate 4 v2 first run.
DECK_AVG_MIN = 0.70   # The strawman's 0.95 was author-estimated; empirical data
                      # from the first real run shows healthy decks score 0.35-0.95
                      # per OPTION with deck-avg ~0.77. Per-slide-min is the worst-OPTION
                      # score across all options, which can dip when an agent legitimately
                      # expands the brief (slide 11 composite hit 0.354 with zero
                      # structural-fabrication flags).
```

The script's inline comment is explicit: **the strawman's 0.92/0.95 was author-estimated.** Real-run data showed legitimate agent-expanded content scores 0.35–0.95 per option; healthy decks land at deck-avg ≈ 0.77; the worst-option-per-slide can dip to 0.354 with zero structural-fabrication flags. v1 recalibrated twice post Gate 4 v2 first run and landed at 0.30 / 0.70.

v2 had been carrying the strawman number without recalibration. **Fixed in this pass.**

## "Fix the shape" — the load-bearing non-negotiable is structural, not token-ratio

The original rule statement (`≥ 0.92`) hid a two-tier check. The actual script enforces:

| Tier | Check | Severity |
|---|---|---|
| **(a)** | `structural_flag_count == 0` | **Hard non-negotiable.** Zero structural-count fabrications (e.g., 4 cards when the brief enumerates 2). This is the load-bearing rule. |
| **(b)** | `score >= PER_SLIDE_MIN` (worst option, per slide) AND `score_avg >= DECK_AVG_MIN` (deck average) | Calibration thresholds. Token-ratio measurement. Currently 0.30 / 0.70. |

The original `≥ 0.92` flattened both tiers into a single number, which (a) hides which check is doing what work and (b) sets the calibration tier at an empirically-wrong value.

**The corrected rule statement makes both tiers explicit** and cites the script as source-of-truth so future drift is auditable. The `structural_flag_count == 0` non-negotiable is the actual hardline; the token-ratio is calibration that re-baselines as v2 accumulates real-build data.

## Provenance

- **0.92 origin:** v1 strawman document, author-estimated. Never validated against real-build data before being adopted as a hardline.
- **First recalibration:** v1, post Gate 4 v2 first run. Empirical data from real decks showed the strawman number was too high — legitimate agent-expanded content was being flagged as fabrication. Adjusted to a lower threshold.
- **Second recalibration:** v1, same session, after more data — landed at 0.30 / 0.70 as documented in the script's inline comments.
- **v2's adoption (this pass):** inherit v1's calibration as the starting baseline. Cite the script constants directly so future v1 recalibrations propagate automatically (no number duplication in v2 docs).

## n=1 limitation explicitly accepted

v2's distribution may diverge from v1's by construction — different patterns (14 splits vs. 19 chassis), different prompt structure (closed directive verbs, single pattern across 3 options), different agent dispatch (general-purpose with v2 prompt vs. v1 deck-builder agents). The inherited 0.30 / 0.70 thresholds are the **best-known approximation**, not a v2-validated calibration.

**Re-validation commitment:** treat 0.30 / 0.70 as transitional. Measure brief-fidelity scores against items 1 (trigger-brief) and 2 (ACN) smoke outputs as part of those smokes' inspection step. Document the observed v2 distribution. After 3+ real (non-smoke) v2 builds, recalibrate v2-native thresholds if the distribution diverges from v1's.

## v0.1 follow-on — extract a shared QC CONTRACT (not script)

Reviewer B's deeper anti-drift fix: stand up a small `shared/qc_contract.py` defining where the brief lives, where options live, how rejection is signaled. Both v1 and v2 target the contract; each owns its check implementation independently. Same disease shape as the `themed/` and `sys.argv[1]` bugs: source-of-truth duplication creates inevitable drift. v0.1 candidate paired with the `paths.py` extraction.

Forking the script itself (Reviewer B's alternative) is also v0.1 candidate work — copy `check_brief_fidelity.py` to `slide-builder-simple/scripts/qc/`, adapt to v2's conventions (read from `dispatch_plan.md` rather than `_meta.json`, handle `FALLBACK_MERMAID` as a skip case parallel to `SKELETON_REJECTED`). Inherit v1's threshold constants but cite v1's source explicitly so future drift is auditable.

**For items 1 + 2 smoke measurement in v0:** patch v1's `check_brief_fidelity.py` in-place to skip `FALLBACK_MERMAID` files (parallel to its existing `SKELETON_REJECTED` skip logic). Shim a minimal `_meta.json = {"brief": "<absolute path>"}` into the v2 smoke output dirs before running. Capture per-option scores, per-slide-min, deck-avg, and structural_flag_count. Document the v2 distribution.

## Audit follow-on — verify the other 4 hardline rules

Reviewer A: "one fictional number corrodes trust in the other four." The other Hardline rules:

1. **Charts and tables only in their respective object layouts** — structural rule, no number. ✅ Empirically grounded (object-layout primitives are documented in `layouts.md`).
2. **No fabrication beyond brief enumeration** — structural rule, no number. ✅ Same `structural_flag_count == 0` enforcement as #4(a); they're the same load-bearing rule expressed in different vocabularies.
3. **No 3+ consecutive slides on the same split** — numerical, but explicitly counts adjacency, not a calibration ratio. The number `3` is the structural threshold (3+ is the violation), not an empirically-tunable parameter. ✅
4. **Brief fidelity** — **recalibrated this pass.** ✅
5. **SKELETON_REJECTED protocol** — structural rule (token-on-line-1 check), no number. ✅

**Result of follow-on audit: rule #4 was the only one carrying a strawman-author number.** The other four are structural rules or structural counts, not empirical calibration parameters. No further recalibration needed in v0; the hardline-rules set is empirically defensible after this pass.

---

# Item 1 trigger-brief smoke — surfaced two real blockers + corrected prior false-positive

The trigger-brief smoke (a 4-slide synthetic brief intentionally triggering SKELETON_REJECTED + FALLBACK_MERMAID) reached Gate 2 cleanly (all 4 agents returned with correct classifications) and then failed at Stage 3 finalize. Two distinct failures + one critical correction to the prior FedEx smoke's reporting.

## Architecture mechanisms validated at Gate 2 (this section is the architectural win)

| Mechanism | Status | Evidence |
|---|---|---|
| Pattern-pick override of forecaster | ✅ | Slide 2: forecast = 50/50 vertical (would dodge trap); agent overrode → N-column row (4-phase) → SKELETON_REJECTED. Slide 3: forecast = Swimlane; agent overrode → FALLBACK_MERMAID. |
| SKELETON_REJECTED protocol (Hardline #5) | ✅ | All 3 slide-2 options emit `# SKELETON_REJECTED: brief enumerates 2 phases, N-column row pattern needs 4 cells` on line 1 + `sys.exit(0)` body. No fabrication of Phase 3/4. |
| FALLBACK_MERMAID classification + sibling .mmd | ✅ | All 3 slide-3 options emit `# FALLBACK_MERMAID:` on line 1 + sibling `option_X.mmd` files written. 3 cosmetic variants (TD/LR/TB orientations), topology preserved across all 3, 5-spoke brief enumeration honored (didn't fabricate a 6th from the worked example). |
| finalize_deck.py classification routing | ✅ | Console output: `classification: native=6 mermaid=3 rejected=3`. All 12 options classified correctly. SKELETON_REJECTED branch worked — slide 2 all 3 options reported `[rejected] rejected (...)` with reason. FALLBACK_MERMAID branch correctly invoked `render_mermaid.py` (then failed on the mmdc install gap — see Failure 1). |
| Anti-convergence brand-token rule (§ 5 revised) | ✅ | Slide 1: variants use brand on DIFFERENT load-bearing elements (A on accent rule, B on hero fill, C on hero text fill). Reviewer C's anti-convergence clause held empirically. |

**Both v2 architectural mechanisms work correctly at the agent + classification level.** The failures below are environment + cross-stream, not v2 architectural defects.

## Failure 1: `mmdc` not installed (environment gap, now fixed)

`render_mermaid.py` returned exit 1 on all 3 slide-3 options. Diagnosis: `command -v mmdc` returned empty — Mermaid CLI not on PATH.

`fallback.md` documented the prerequisite (`npm install -g @mermaid-js/mermaid-cli@11.4.0`) but v0 never validated the install on this machine. The architecture caught this cleanly — finalize_deck.py marked the options as `FAIL (fallback render: render_mermaid.py exit 1)` and continued; didn't crash. That's the correct failure mode for an item-level environment gap.

**Resolved this pass.** `npm install -g @mermaid-js/mermaid-cli@11.4.0` ran successfully:

```
added 217 packages in 1m
$ mmdc --version
11.4.0
```

Exact match to the pinned version in `render_mermaid.py` docstring and `fallback.md`. Documented here as "v0 prerequisite installed; previously documented but not validated until this smoke."

Side note: `npm warn deprecated puppeteer@23.11.1: < 24.15.0 is no longer supported` appeared during install. mmdc 11.4.0 transitively pins puppeteer 23.11.1; not a v2 concern but worth noting if mmdc itself bumps later.

## Failure 2: v1 brand-sidecar migration shipped mid-stream (cross-stream blocker)

`finalize_deck.py` crashed at Stage 3 step 3 ("Load client theme") with:

```
twins.client_theme.BrandSidecarMissing: Brand sidecar(s) missing for template:
  MISSING: Moving Forward PPT Template.brand.yml
  MISSING: Moving Forward PPT Template.theme.json
```

v1's `client_theme.py::load_client_theme` was migrated to require per-template `.brand.yml` + `.theme.json` sidecars next to the PPTX. The migration shipped between this session's earlier FedEx smoke (which worked with the OLD loader) and Item 1's trigger-brief smoke (which now hits the NEW loader). FedEx and ACN templates have not been registered with v1's new `register_template.py`.

**This is the exact cross-stream timing risk the architecture review anticipated.** v2 inherited a v1 contract change without an explicit migration signal.

**Architectural follow-on (v0.1 process improvement, captured per Reviewer A):** cross-stream migration-log protocol. v1 publishes a "shared-infra migration ready" signal in `_migration/` before merging changes that affect `twins/`. v2's Stage-1 sanity check (proposed Step 4 below) reads this signal and halts at prep-time with a clear error before agent compute is sunk. **Documented in DECISIONS.md as v0.1 process improvement.**

## Critical correction to prior FedEx smoke reporting (false positive)

**The prior FedEx smoke's "PNG colors correct (purple/orange)" finding was a false positive.** Reviewer B's catch.

Mechanism of the false positive:
1. v2's `generate_mermaid_theme()` walks `("colors", "dk2")` tuples against the OLD `template.json` shape.
2. No `template.json` existed for the FedEx template (or it existed in a different shape) — every `_lookup()` call returned `None`.
3. The function fell back to **hardcoded defaults** in `THEME_MAPPING` (the FedEx-default hex values baked into `build_deck.py:75-100`).
4. The hardcoded defaults happen to be FedEx purple (`#4D148C`) + orange (`#FF6600`), so the generated `theme/mermaid-fedex.json` produced visually-correct FedEx colors **by coincidence, not by extraction**.
5. The console output flagged this transparently: `Theme slots using hardcoded fallback: 17 (see dispatch_plan.md)` — 17 of ~22 themeVariables fell back to hardcoded defaults. I documented this in the original Gate 3 report but mis-attributed the "outcome (1) sustained" finding to v1's loader correctness when the loader had never actually fed real template values into v2's Mermaid theme.

**v2's mermaid theme path has never actually been exercised against real client data.** Every FedEx-purple PNG rendered to date used the hardcoded fallback defaults that happened to match FedEx, not extracted-from-template values.

**Implications:**
- The "v1 loader bug is theoretical for FedEx, doesn't bite in practice" finding from the original Gate 3 report is **unsupported by the data**. The loader was never exercised against the FedEx template through v2's path — v2 was using hardcoded defaults.
- For ACN (where the hardcoded FedEx defaults would NOT match ACN colors), the same code path would have produced visibly-wrong PNG colors. The validation deferred until Item 2 was the right call — but the prior "FedEx loader works in practice" certainty needs retraction.
- v2's mermaid theme path now needs to read from v1's new `<stem>.theme.json` shape (top-level `brand.primary_hex` / `brand.accent_hex` etc.) — patch covered in proposed Step 3 below.

**Record correction:** the original FedEx smoke Gate 3 report and the post-Stage-4 finding both contain the false-positive claim. Future readers of those sections should cross-reference this correction.

## Unblock sequence (Reviewer-trio synthesized path)

Skip Path α (hot-patch), Path β (bundles independent issues), Path δ (freeze v1). Apply the integrated 3/3 path:

| Step | Action | Status |
|---|---|---|
| 1 | Install mmdc 11.4.0 (v2 hygiene, no cross-stream dependency) | **DONE this pass** |
| 2 | Delete stale `theme/mermaid-fedex.json` (misleading false-positive evidence) | pending Mario approval |
| 3 | Patch `generate_mermaid_theme()` in `build_deck.py:499-559` to read from v1's new `<stem>.theme.json` shape (`brand.primary_hex` / `brand.accent_hex` / `brand.cover_bg_hex` / `brand.font_heading` / `brand.font_body`). Do NOT salvage via slot-position guessing — that would reintroduce the bug v1 just retired. | pending Mario approval |
| 4 | Add Stage-1 shared-infra sanity check at start of `build_deck.py main()`: warm-up call to `load_client_theme` (halts at prep if registration missing); `mmdc --version` probe (halts at prep if Mermaid CLI missing). Proactive, not reactive. | pending Mario approval |
| 5 | Mario registers FedEx + ACN templates via v1's `register_template.py` (interactive — Reviewer B specifically flagged inversion risk on `--auto-accept-phase1`). Mario checks v1 Phase 3 status first. | pending Mario action |
| 6 | Re-fire Item 1 finalize ONLY (existing agent artifacts are theme-neutral) — reuse `_raw/option_X.pptx` for native; reuse `option_X.mmd` for fallback. | pending Steps 2-5 |
| 7 | Validate Item 1 ran cleanly: `_comment_fallbacks_used` in regenerated `mermaid-fedex.json` should be EMPTY; PNGs render with real FedEx colors from registered brand.yml. | pending Step 6 |
| 8 | Item 2 (ACN) same flow once Step 7 passes. | pending Step 7 |

---

## Handoff contract drift — knowingly accepted (v0.1 candidates)

Surfaced 2026-05-25 during the Stage-3 re-fire post-mortem. The `_meta.json`
manifest fix (writer added to `build_deck.py`, silent fallback removed from
`finalize_deck.py::_resolve_mermaid_theme`) eliminated the load-bearing
build→finalize contract drift that caused the Mermaid false-positive.

The audit also surfaced three handoff orphans that we are **knowingly accepting
as-is for v0**. Each is documented here so the gap is visible and v0.1 work has
a starting list.

### 1. `brief_qc.json` — read but never written

- **Reader**: `build_review.py:454` (`render_qc_banner`).
- **Writer**: none. v2 has no brief-time QC step.
- **Current behavior**: `build_review.py` checks `out_dir / "brief_qc.json"`; on
  missing-file it renders `_render_qc_info_stub()` (an INFO panel explaining
  the file is absent). Existing fallback is graceful and labels the gap honestly.
- **Knowingly accepted because**: brief-time QC integration is a separate
  workstream (storyline-helper hand-off). Stub UI is acceptable in v0; the
  banner labels itself as "INFO · brief_qc.json not found", not silent omission.
- **v0.1 candidate**: either wire build_deck.py to invoke a brief-QC pass and
  emit `brief_qc.json`, or remove the reader and stub from build_review.py.

### 2. `dispatch_plan.md` — written but never read

- **Writer**: `build_deck.py::write_dispatch_plan` (function call site near end
  of `main()`).
- **Reader**: none — no other script parses it.
- **Current behavior**: human-readable summary of slide forecasts + artifact
  locations + next-step instructions. Useful for the parent session at
  dispatch time; not part of any script-to-script contract.
- **Knowingly accepted because**: it's a human-readable artifact, not a
  programmatic handoff. The forecasted-pattern data it surfaces is also in
  `_meta.json['slides'][i]['forecasted_pattern']` for any future script that
  wants it.
- **v0.1 candidate**: keep `dispatch_plan.md` for the parent session, but
  formally mark it as "human-only, not a script contract" in a future
  `shared/paths.py` registry so contract tests don't false-positive on it.

### 3. `picks.json` — human-clipboard handoff, not script-to-script

- **Reader**: `compile_picks.py:72` (`parse_picks`).
- **Writer**: a human pastes JSON from the REVIEW.html "Picks" panel into
  `<out>/picks.json` (or passes it via `--picks <json-string>` on the CLI).
- **Current behavior**: explicit human-in-the-loop bridge between Stage 4
  (review) and Stage 5 (compile).
- **Knowingly accepted because**: this is the intended contract. Stage 4 must
  surface picks to a human for approval; the human's decision lands in
  `picks.json` (or `--picks`). No script should write this file directly.
- **v0.1 candidate**: keep as-is. Future "auto-approve" mode (if it ever
  exists) would write `picks.json` programmatically — that would be a new
  script-to-script contract, separately documented.

### Cross-reference

Reviewer C's audit at `_decisions/handoff-fix-review-C.md` flagged the broader
systemic risk: pipeline scripts share filenames as a soft contract, with no
central registry. v0.1 work tracked in `DECISIONS.md` § "v0.1 commitments
(handoff hardening)" addresses this with a `shared/paths.py` registry +
contract test + `_meta.json` schema validation.
