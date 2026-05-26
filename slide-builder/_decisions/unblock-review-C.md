# Unblock Review — Reviewer C (Scope / Is-This-Convergence-Now?)

**Date:** 2026-05-25
**Blind to:** Reviewers A and B.
**Angle:** Is this the convergence moment the plan always had, or did v1 ship prematurely mid-smoke? What does Mario''s production-grade bar say about the unblock choice?

---

## Verdict

**Pivot to integration. Re-smoke ONCE against the integrated end-state.**

Not α (install+register+retry on the v0 environment as-of-when-smoke-started). Not β (pause everything). Not γ (mmdc only). A scoped variant of "pivot-to-integration" — described in the final section as Path δ.

---

## Is this convergence?

**Honestly: yes, this is the convergence moment. But it arrived early and noisy.**

Re-read DECISIONS.md § "Open — cross-skill dependency on v1 theme rescope" carefully — it explicitly says:

> v2-side state today (transitional): `scripts/build_deck.py::validate_theme()` still runs as belt-and-braces. The path-substring → expected color family check (`KNOWN_CLIENT_HUE_RANGES`) becomes unnecessary once `brand.yml` is canonical.

> **v2-side follow-on when v1 ships `brand.yml`:** [4 items listed]
> None of these v2 follow-ons are urgent. v1''s `brand.yml` work lands first; v2 picks up the change transitively.

The plan was always "v1 ships first; v2 picks up transitively." What the plan *also* said was that v2''s current build is **shippable for A/B testing in the interim**, because `validate_theme()` halts on the failure mode the rescope addresses. The implicit assumption was that v1''s rewrite would land in *additive* mode — `brand.yml` would become canonical, slot-mapping would remain as legacy fallback for templates without a registered `brand.yml`.

What actually shipped is not additive. v1''s loader now *requires* per-template `.brand.yml` + `.theme.json` sidecars; neither exists for FedEx or ACN; v2 inherits the loader and crashes. That is **not** the convergence shape DECISIONS.md described. The plan said "v2 picks up the change transitively"; v1 shipped a change v2 cannot pick up transitively because the migration tail (legacy slot-mapping fallback) was not preserved.

So: **convergence was always coming, but v1 shipped a non-transitive rewrite mid-smoke.** That is a v1-side discipline failure — v1 shipped without honoring the cross-stream contract in DECISIONS.md § "Open — cross-skill dependency" — not a v2-side scope creep. Calling it "v1 shipped prematurely" is fair; calling it "premature ship that broke v2" is also fair. Both are true.

The architectural mechanisms (Stage 1+2) passed. That matters. v2''s core picking + dispatch + classification works; what broke is the downstream theme loader, which is v1 code v2 inherits. The break is at the integration seam, not in v2''s architecture.

---

## Production-grade bar verdict

**The bar rejects α (install+register+retry to keep the original smoke running) and favors pivot-to-integration.**

Re-read my prior Production-grade-bar review (`post-stage4-plan-review-C-revisited.md`). The four forbiddens under Mario''s bar:

1. Deferring known validation gaps to production.
2. Honor-system rules with no measurement.
3. Untested code paths shipping as ready.
4. Multi-client claims without multi-client evidence.

Option α (install + register both templates + retry the original smoke against the v0 loader environment that v1 has just abandoned) violates #3 and skirts #1. Here''s why:

- α produces a smoke run on **a code path that no longer exists in v1**. v1 has shipped the new loader. The next v2 deck will not run against the loader v2 just smoked against — it will run against the new `brand.yml`-requiring loader. So α produces validation of a code path that''s already historical the moment it finishes.
- α also requires Mario to register FedEx and ACN templates as a one-off via `register_template.py` (the new v1 flow). But "one-off to unblock the smoke" is exactly the path that becomes the production registration. So the registration work isn''t throwaway — it''s the actual integration work, just done in the wrong order. Doing it without committing to the integration is a half-step.
- The production-grade bar specifically rejected "real A/B will surface it" in my prior review. The shape of that rejection: synthetic smokes exist precisely so the first production deck isn''t the test case. **α has the same shape inverted** — it ships a smoke against the old environment so the first production deck is the test case for the new integrated environment. Same failure mode, different direction.

Option β (halt + document + resume later) is defensible only if v1''s `brand.yml` migration is genuinely blocking and Mario needs a day or two to author the sidecars. If `brand.yml` authoring for FedEx + ACN is achievable in the same window as α (~45-60 min), then β is just α without the work — strictly worse.

Option γ (mmdc only) is a non-answer. mmdc is one of two blockers. Fixing one and leaving the other is half-work.

**The production-grade move is to author the `brand.yml` sidecars for FedEx and ACN (the actual integration), install mmdc, then re-smoke ONCE against the integrated end-state.** That gets:

- One smoke run on the production code path (not on a historical path).
- Validation of the `brand.yml` integration as actually used in production.
- Cross-stream finding from v1''s smoke (loader bug for non-FedEx clients) gets retested under the integrated state — does the new loader correctly handle ACN''s two-purples case via the authored `brand.yml`?
- The 4 v2-side follow-ons listed in DECISIONS.md § "v2-side follow-on when v1 ships brand.yml" all land in the same pass: `generate_mermaid_theme()` reads `brand.yml`; `validate_theme()` drops `KNOWN_CLIENT_HUE_RANGES`; `reference/fallback.md` updates; `dispatch_plan.md` logs theme source.

This is Path δ: **integrate first, smoke against the integrated state, get one clean data point.**

---

## Biggest concern

**The biggest concern is treating this as "unblock the smoke" rather than "this IS the integration."**

If v2 picks α and "unblocks the smoke" by registering FedEx + ACN templates as a quick fix to keep the original validation running, the project ends up with:

- A smoke run on the old code path (now historical).
- An incomplete integration (no `generate_mermaid_theme` rewrite, no `KNOWN_CLIENT_HUE_RANGES` drop, no `fallback.md` rewrite).
- Two registered templates with `brand.yml` files authored *under pressure to unblock*, not authored as production artifacts.
- A second pass needed later to do the actual integration.

That''s "more time" disguised as "fast unblock." Mario''s production-grade bar specifically rejects work that creates more downstream work to look fast upstream.

The cross-cutting concern about Item 2 (ACN smoke) makes this sharper, not weaker. If v2 commits to registering BOTH templates to keep going, v2 has just committed to half the integration work without committing to the full integration. The clean move is: commit to the integration, do it once, smoke against the result. If the integration reveals a fatal gap in v2''s downstream (e.g., `generate_mermaid_theme` can''t be cleanly rewritten to read `brand.yml`), that''s a real finding, surfaced at the right time, not buried by an α-style fast-unblock.

NFL scope boundary (item 3 in the smoke list) is independent — author the boundary doc regardless of α/β/γ/δ. That''s free signal and shouldn''t gate any of the unblock options.

---

## Critical

**Direct answer to the question posed: yes, the production-grade bar rejects "register templates to keep going" for the same reason it rejected "real A/B will surface it."** Both are forms of "ship a partial validation against a code path that''s not the production code path, on the bet that the gap won''t bite." The bar named that bet as the lazy move.

**It is NOT OK to pay the cost to unblock if the cost is "register templates as a one-off."** It IS OK to pay the cost to unblock if the cost is "do the integration properly, then smoke." Same dollars, different meaning. The first is α; the second is δ.

The cleanest framing for Mario: **v1 shipped the convergence event mid-smoke. v2''s response is not to limp the old smoke to completion — it''s to recognize convergence has arrived noisily and pivot to integrating. The smoke that matters is the integrated-state smoke, not the v0-environment smoke. Do the integration. Smoke once. Move on.**

If the `brand.yml` authoring for FedEx + ACN turns out to take longer than 45-60 min (e.g., v1''s `register_template.py` flow is itself broken or under-documented), then β (halt + document + resume) becomes the right call — not as defeatism but as honest accounting of the v1-side discipline failure. Pay the cost of the failure visibly, not by burying it in α.

The smoke is not the deliverable. The integration is. Treat it that way.
