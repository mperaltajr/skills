# Smoke-readiness review — Reviewer A (Gap Analysis)

**Date:** 2026-05-25
**Angle:** what has the smoke NOT validated that it needed to?
**Reviewer:** A (blind to B and C)

---

## Verdict

**SHIP STAGE 4 WITH CAVEATS.**

Stage 4 (`build_review.py`) is a small superset of what `build_gate_preview.py` already produced (adds per-option PPTX picking handles, QC banner, font banner, storyline panel, picking JSON). It is **cheap, near-verbatim from v1, and the marginal risk of running it is essentially zero** — it reads files Stage 3 already wrote and emits one more HTML. So the literal question "fire Stage 4" is yes.

What is **not yet earned** is the phrase that comes after: "then enter convergence hold." Convergence hold implies "v2's architecture is empirically validated and we're parked waiting on v1's `brand.yml`." The smoke as run validates the **happy path on one brief × one client × one pattern subset**. Three of the five architectural mechanisms v2 was built around (SKELETON_REJECTED, FALLBACK_MERMAID, Hardline #4 measurement) were not exercised end-to-end. That's an architectural blindfold worth naming before declaring hold.

---

## Gap analysis (per question)

### 1. Brief fidelity ≥ 0.92 (Hardline #4) — **NOT MEASURED. Severity: v0.1 (acceptable for ship; blocker for "validated").**

`grep brief.fidelity|fidelity_check|fidelity_score|0\.92` against `scripts/` returns zero hits. The only references to "Brief fidelity" anywhere in the codebase are:
- `prompt.md § 8` — instructs the agent to write a **one-line self-attested statement** in line 3 of each `option_X.py` header (`# Brief fidelity check: ...`)
- `prompt.md § 9` ("Brief fidelity: <one-line statement...>")
- `_decisions/smoke-test-finding-2026-05-25.md` line 138 — explicit note: "Header line 3 (Brief fidelity check) ✅ not parsed by any downstream; metadata-only"

The smoke did **not** measure fidelity. It assumed it via pattern-pick correctness. Hardline #4 is currently an honor-system rule the agent narrates and nothing checks. That's a gap by definition, but a defensible one for v0 — fidelity measurement is an unsolved problem and v2's design choice was to lean on slide-qc's vision pass + REVIEW.html human inspection as the de-facto fidelity gate. The gap should be **named explicitly** in the convergence-hold declaration, not papered over.

### 2. SKELETON_REJECTED protocol (Hardline #5) — **NOT EXERCISED. Severity: blocker for "architecturally validated"; acceptable for first ship.**

`RESULT.md` confirms `Rejected: 0`. The slidelab-intro brief is too clean to trigger this code path. The classifier branch (`finalize_deck.py::_classify_option`) returns one of `native | fallback_mermaid | skeleton_rejected | missing` and has live branches for each — the `skeleton_rejected` branch is wired into `build_pptx()` and the RESULT.md template, so it would surface if fired. But "wired" ≠ "validated under load." We have no observational evidence that an agent will actually emit the token when it should rather than fabricate content to the assigned pattern (the exact failure mode that motivated the rule).

This is a real gap. The way to close it is a deliberately mis-shaped brief: enumerate 2 items but instruct the agent to use a 4-cell layout, or use editorial language that maps to no directive verb. Without that, we are shipping with an untested guardrail.

### 3. FALLBACK_MERMAID path — **NOT EXERCISED. Severity: blocker for "architecturally validated"; v0.1 for ship.**

`RESULT.md` confirms `Mermaid: 0`. The entire Mermaid sub-architecture — `_render_mermaid_png()`, `_assemble_fallback_pptx()`, `_resolve_mermaid_theme()`, `render_mermaid.py`, the per-client theme JSON generation in `build_deck.py`, the chrome-from-helpers + embed-at-body-zone assembly — is **untested end-to-end at smoke level**. Dispatch_plan.md even reveals that 17 of 17 Mermaid theme variables are running on hardcoded defaults because there was no `template.json` for FedEx at smoke time.

This is the single biggest validation hole. An entire architectural component shipping without an end-to-end smoke is exactly the failure mode that bit v1 (chassis layers stacked without empirical validation, 23% acceptance discovered only at curator pass). The fix is a one-slide brief that explicitly triggers a hub-spoke or ecosystem-map.

### 4. Multi-client validation — **PARTIAL. Severity: blocker for "shippable for A/B against any client."**

`KNOWN_CLIENT_HUE_RANGES` in `build_deck.py` line 587 contains exactly one entry: `fedex`. The validator (line 737-747) emits a **warning, not an error**, when the client is not registered — so an Accenture or NFL deck would proceed past `validate_theme()` with only the structural checks (primary != accent, plausible saturation/luminance). The smoke proved nothing about whether the v1 loader inverts colors for Accenture (where the loader bug is theorized to bite). Mario''s standing claim has been that v1 ships A/B against FedEx, Accenture, and NFL. v2 has been validated against 1 of those 3.

### 5. Theme inheritance proof — **PARTIAL. Severity: v0.1 (acceptable for current ship; mandatory re-validation when v1 rewrite lands).**

The smoke proved v1''s current loader produces correct purple/orange for FedEx through v2''s pipeline. That is a useful empirical data point. But `_decisions/DECISIONS.md § "Open — cross-skill dependency on v1 theme rescope"` already enumerates four v2-side follow-ons when v1 ships `brand.yml`. None of those is exercised today. The convergence-hold framing is correct in spirit (v2 is parked waiting on v1) **but** the smoke does not constitute validation of the post-rewrite path. Re-validation against `brand.yml` is mandatory before declaring "v2 ships." Today''s smoke != tomorrow''s ship-validation.

### 6. Adjacency post-pass detection — **PARTIAL. Severity: acceptable.**

Good news: the logic exists in both `build_gate_preview.py::compute_adjacency_warnings` (line 208) and `build_review.py::compute_adjacency_warnings` (line 121), and the smoke output confirms it fired on slides 1-2-3-4. So the detector ran and surfaced an advisory.

But "the detector ran on a real case" != "the detector is correct in the general case." We did not observe:
- A 3-in-a-row case (only 4-in-a-row fired)
- A pattern run on option B or C — the code currently only scans option_A by hardcoded default
- A case where two non-adjacent runs exist (does it surface both?)
- A case where a Mermaid/Rejected option breaks an apparent run

These would take a 5-minute unit test against a synthetic slide list. Worth doing before convergence hold; not a blocker for Stage 4.

### 7. Bounded non-determinism vs. v1 determinism for A/B — **YES, this is a real concern. Severity: blocker for fair A/B; v0.1 for ship-as-experimental.**

The smoke-test-finding doc records that on run 1 vs run 2 of the same brief, slides 7 and 10 picked different valid patterns. v1''s rotation seed is deterministic. Setting these against each other in an A/B with N=1 per brief means v2 gets one roll of its own dice while v1 gets its single deterministic answer. If the user judges v2 "wins" on a lucky roll or "loses" on an unlucky one, the result mis-attributes architecture quality to sampling variance.

The right A/B protocol for v2 specifically is **k-of-N**: run v2 three times per brief, aggregate the three REVIEW.html outputs, and let the user pick the best variant across all 3k options before comparing to v1. This is not what the smoke or the convergence-hold plan currently call for. DECISIONS.md § "Testing protocol" still says "Both produce PPTX -> render to PNG" — singular, deterministic framing that does not match v2''s actual behavior.

---

## What additional smoke would actually validate

Minimum work to honestly close the gaps before convergence hold:

1. **Trigger brief (15-20 min build).** A 3-slide synthetic brief: one slide that mis-shapes enumeration (forces SKELETON_REJECTED), one that requires hub-spoke (forces FALLBACK_MERMAID with theme generation), one normal. Run through v2; observe one rejection in RESULT.md + one Mermaid PNG embedded in a themed PPTX. Closes gaps #2 and #3.

2. **Second-client smoke (30 min).** Run the same slidelab-intro brief against the Accenture template. Observe whether `validate_theme()` warns (it should, since `accenture` is not in `KNOWN_CLIENT_HUE_RANGES`), whether the loader produces correct colors or wrong colors, and whether v2 halts or proceeds. Closes gap #4 — or, equally usefully, **proves the gap is real** and we can decide whether to halt the A/B or proceed FedEx-only until v1''s `brand.yml` lands.

3. **Adjacency unit test (10 min).** Synthetic input to `compute_adjacency_warnings`: 3-in-a-row, 4-in-a-row split by a 1-different-pattern slide, two separate 3-runs, edge cases. Confirms the detector is correct beyond the one accidental case the smoke produced. Closes gap #6.

4. **k=3 A/B protocol amendment to DECISIONS.md (10 min).** Document explicitly that v2 runs 3x per brief in an A/B, and the user picks across the aggregated 3N options before scoring against v1''s single deck. Or pick option 3 from the smoke-test-finding doc (`temperature=0` dispatch) and acknowledge the cost. Closes gap #7.

Gap #1 (brief fidelity measurement) and gap #5 (post-`brand.yml` re-validation) are genuinely v0.1 work and do not block convergence hold provided they are named.

**Total additional smoke: ~1 hour of work.** Cheap insurance against the failure mode that bit v1.

---

## Biggest concern

**The FALLBACK_MERMAID path is dark code shipping to first A/B.** It has tests for `_classify_option` (the discriminator works in `RESULT.md`''s counts), but the actual rendering pipeline — `render_mermaid.py` -> embedded PNG -> themed PPTX — has never produced output observed by a human. Dispatch_plan.md showing 17 hardcoded theme defaults for a client that does not have a `template.json` means even if the Mermaid path fires on the first real brief, it will render with **default Mermaid colors, not FedEx brand colors**. That is a brand-fidelity break that would surface in the first real A/B that happens to need a hub-spoke, and the failure would look like "v2 ships off-brand decks" rather than "v2''s fallback theme generation has an unfilled dependency on `template.json`." Mis-attribution risk is high.

This is exactly the kind of leak v2''s whole architecture was supposed to prevent — a layer that was not validated empirically before being declared ready. A 15-minute trigger-brief smoke closes it definitively. Not doing that smoke before convergence hold is the single decision I would push back on hardest.

---

## Summary

Fire Stage 4 — it is near-zero risk. Do not call it "convergence hold" until you have spent ~1 hour on a trigger-brief smoke (SKELETON_REJECTED + FALLBACK_MERMAID), a second-client smoke (Accenture), an adjacency unit test, and a documented k=3 A/B protocol. Without those, the convergence-hold declaration over-claims what the FedEx-only happy-path smoke actually proved.
