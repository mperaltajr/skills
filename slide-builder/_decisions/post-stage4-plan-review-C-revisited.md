# Post-Stage 4 Plan Review — Reviewer C, Revisited Under Mario's Bar

**Date:** 2026-05-25
**Prior position:** "Fix only defect #4, document the rest, ship as-is, let real A/B builds surface what synthetic smokes cannot." (`post-stage4-plan-review-C.md`)
**Trigger for revisit:** Mario's pushback — "This is a production grade deliverable. Strategy content is sometimes shoddy. The bar needs to be 100% increased. Being lazy is not an excuse."

---

## Re-statement of Mario's bar

"Production-grade" for this deliverable means: **the artifact gets handed to a partner who walks into a client room with it.** The deck is the deliverable, but v2 is the *factory* producing the deliverable. So the bar applies to v2 itself: it must produce shippable output reliably, not produce-shippable-output-sometimes-and-find-out-which-times-in-front-of-the-client.

What that bar forbids:

1. **Deferring known validation gaps to production.** Synthetic smokes exist precisely so the first production deck isn't the test case. "We'll find out when a real deck hits production" treats the partner's client meeting as a QA environment.
2. **Honor-system rules with no measurement.** A "Hardline" that nothing actually checks is not a rule, it's a wish.
3. **Untested code paths shipping as ready.** Code that has never run end-to-end is code that doesn't work — we just haven't found out yet.
4. **Multi-client claims without multi-client evidence.** v1 ships A/B/C against FedEx, ACN, NFL. If v2 claims to be a peer of v1, it owes the same coverage or it owes an explicit "FedEx-only for now" boundary.

The legitimate paths under this bar are the three Mario named: fix, knowingly accept with defensible rationale, or shut down. "Let A/B find it" fails all three.

---

## Per-item verdict

### Item 1 — Trigger-brief smoke (SKELETON_REJECTED + FALLBACK_MERMAID)

**Verdict: A — Fix now.**

Defensible rationale at production-grade bar: this is the single largest dark-code surface in v2. The Mermaid pipeline — `render_mermaid.py`, `_assemble_fallback_pptx()`, per-client theme JSON generation, body-zone embedding, chrome assembly from helpers — has **never produced an observed output end-to-end against a real brief**. Reviewer A names this as the biggest concern and is right. The classifier branch is wired but the rendering pipeline downstream of the classifier has zero empirical validation.

The failure mode if we skip this: the first real brief that needs a hub-spoke or ecosystem-map fires the Mermaid path for the first time in front of a partner. Even if classification works, the theme JSON is generated from `template.json` slot lookups (currently 17/17 hardcoded defaults for FedEx — there is no `template.json` for FedEx) which means the Mermaid PNG will render in **default Mermaid colors, not brand colors**. The partner sees an off-brand diagram in an otherwise on-brand deck and the cause is invisible to them.

SKELETON_REJECTED has the same shape but lower magnitude — the protocol is honored by 30 of 30 agents not firing it on a brief that doesn't trigger it; we have no evidence an agent will emit the token rather than fabricate content when the brief and pattern actually disagree. That is the exact failure mode (slide-9 fabrication bug) v2 was built to prevent.

Cost: ~30 minutes to write a synthetic 3-slide brief (one enumeration mis-shape, one hub-spoke, one normal) and run it through the pipeline. That is not "lazy to skip." It is the cheapest possible validation of two of v2's five hardline mechanisms.

### Item 2 — Accenture-template smoke

**Verdict: A — Fix now.**

Defensible rationale at production-grade bar: `KNOWN_CLIENT_HUE_RANGES` contains exactly `fedex`. The validator emits a *warning* for unregistered clients, not an error. The v1 loader heuristic that breaks on Accenture's "two purples" case is the entire reason `brand.yml` exists as a planned v1 rewrite. v2's smoke proves v1's loader is correct for FedEx; it proves nothing about Accenture.

If v2 claims to be A/B-ready against v1, and v1 ships against ACN today, then v2 must at minimum show what happens against ACN. Three outcomes are possible:

- v2 halts on `validate_theme()` (good — guard works).
- v2 ships purple/purple wrong-color (bad — guard misses Accenture's specific failure mode; defect).
- v2 ships correct colors despite the loader's theoretical bug (good — and tells us the bug doesn't bite for ACN either).

All three are useful outcomes. The one we cannot afford is "we don't know" while claiming production readiness. Cost ~30 minutes — same brief, different template.

### Item 3 — NFL-template smoke

**Verdict: B — Knowingly accept the gap, with explicit scope boundary.**

Defensible rationale a partner reviewing the deck would accept: "v2 v0 ships validated against FedEx (full smoke) and Accenture (theme-loader smoke). NFL adds two additional risk surfaces — `strip_master_backgrounds` flag interaction and stadium-photo bleed-through — that are NFL-specific and don't generalize from the FedEx run. We have explicitly scoped v2 v0 to two-client A/B (FedEx primary, ACN secondary). NFL routes to v1 until v0.1, which adds the NFL smoke as the gating item before three-client A/B."

This is defensible because it draws a *line* rather than papering over absence. The bar Mario set is not "validate everything before shipping anything"; it is "if there's an issue, it should be resolved or knowingly accepted and put aside." NFL is the cleanest case for knowingly-accept because:

- The risk surface is *additive*, not architectural — `strip_master_backgrounds` is a flag that either works or doesn't; it doesn't change v2's core picking/build/theme behavior.
- The mitigation (route NFL to v1) is concrete and immediate.
- The cost to close (~30 min NFL smoke) is not free given we're already past budget; deferring it to v0.1 with an explicit boundary is a real trade, not a hand-wave.

This is the only "B" of the four. The reason it qualifies and the others don't: NFL's gap doesn't poison the FedEx + ACN claim. The other gaps do.

### Item 4 — Brief-fidelity measurement (Hardline #4: ≥ 0.92 per slide)

**Verdict: A — Fix now, but in the limited form Reviewer A described.**

Defensible rationale at production-grade bar: Hardline #4 currently is **not a rule**. It is a one-line self-attestation the agent writes in line 3 of each `option_X.py` header that nothing downstream parses. The smoke-test-finding doc says so explicitly at line 138: "Header line 3 (Brief fidelity check) ✅ not parsed by any downstream; metadata-only." Calling this a "Hardline" while not measuring it is exactly the honor-system-with-no-check failure that Mario's bar forbids.

The fix is not "build a sophisticated brief-fidelity engine." The fix is: **run the brief-fidelity check spec from build-deck-review.md against the existing 30 PNGs once, record the per-slide fidelity scores, and either confirm the ≥ 0.92 floor holds or document where it doesn't.** If the spec doesn't exist as executable code, then we either write the minimum check (count brief tokens visible in rendered text vs total brief tokens, with a documented chrome-allowance list) or we re-classify Hardline #4 as a documentation-only design principle and remove the "≥ 0.92" number from the architecture claim.

Either path is acceptable. What is *not* acceptable is keeping the "0.92" claim in DECISIONS.md while nothing measures it.

Cost: ~45-60 minutes for a minimum executable check, or ~10 minutes to downgrade Hardline #4 in the docs honestly. Pick one.

---

## Has my position changed?

**Yes, partially.**

What I got wrong in the prior review: I framed the work as "synthetic smokes catching synthetic defects" and argued real A/B would do the catching. That framing presumes the failure modes synthetic smokes catch and the failure modes A/B catches are roughly equivalent classes — they aren't. Synthetic smokes catch *predictable* dark-code failures (Mermaid path never run, ACN theme behavior unknown, Hardline #4 unmeasured). A/B catches *aesthetic* and *editorial* failures (does this slide actually make the partner's argument). The two are not substitutes. My prior position swapped one for the other.

The 2.5x-budget argument I made is still true but it cuts the wrong way under Mario's bar. Going from 2.5x to 3x budget to close known validation gaps is *cheaper* than shipping a v2 that fails in front of a partner and burns the credibility of the whole v2 path. The asymmetry favors closing gaps.

What I got right in the prior review and still defend: defect #1 (slide 1 option A monochrome cover) does not need architectural retrofit. Three sibling variants exist precisely to provide range; the picker is the gate. I would still mark that one as v0.1, not v0. Mario's bar is "production-grade deliverable" — and the deliverable in this case is the deck the partner picks, not every individual variant the picker offers. Bounded variance across A/B/C is a feature; demanding all three options ship-clean is the v1 chassis-vocab failure mode (over-constrain to prevent variance, lose range).

So: position changed on Category 2 (the four items above). Position unchanged on defect #1's classification.

---

## Biggest concern at this bar

**Brief fidelity is unmeasured and the v2 architecture cites "0.92" as a hardline number.**

This is the cleanest example of the gap Mario named: a production-grade deliverable cannot claim a numeric quality floor that nothing measures. Every other gap is a code-path that hasn't run. This one is a claim that isn't true. If a partner reads DECISIONS.md and asks "what's the brief fidelity on slide 5 option B," there is no answer. The answer is "we trust the agent's self-attestation." That is not production-grade.

This is also the gap most likely to bite *invisibly*. The Mermaid path failing is loud (off-brand diagram). ACN theme failing is loud (wrong colors). Brief fidelity failing is quiet — the slide looks fine but the partner who wrote the brief reads it and notices the third bullet doesn't say what the brief said. That's the failure mode Hardline #4 was named to prevent, and nothing currently prevents it.

---

## Single recommendation

**Path: Fix items 1, 2, 4. Accept item 3 with explicit scope boundary. Then ship v2 v0 to first A/B against FedEx and ACN.**

Sequenced:

1. Fix defect #4 (path-contract blocker) — 30 min. Re-fire Stage 4.
2. Write trigger brief, run through pipeline, observe SKELETON_REJECTED + FALLBACK_MERMAID end-to-end with theme generation — 45 min.
3. Run slidelab-intro brief against ACN template, record what `validate_theme()` and the loader do — 30 min.
4. Run minimum brief-fidelity check against existing 30 PNGs OR downgrade Hardline #4's numeric claim in DECISIONS.md — 45 min.
5. Document NFL scope-out boundary in DECISIONS.md — 10 min.
6. Update DECISIONS.md "Testing protocol" section with k=3 A/B for v2 (Reviewer A's gap #7) — 10 min.

Total: ~3 hours. Not the "2 hours" the coordinator estimated. Not the "1 hour D-minus" I previously recommended. Three hours, because that's what the bar costs.

If any of those four items reveals a fatal gap (Mermaid theme generation is structurally broken, ACN ships catastrophically wrong colors, brief fidelity is well below 0.92 across the deck), then **path C — shut down v2** becomes live, not as defeatism but as honest accounting: if v2 doesn't survive its own validation, it doesn't survive production. That outcome is what the smokes exist to surface before a partner sees it.

The shutdown branch is real but I don't expect it to fire. I expect items 1, 2, 4 to surface 1-2 fixable defects each, all closeable in the same ~3 hour window. The reason I expect that and not catastrophic failure is that v2's *architecture* has been validated empirically — 12 agents, 17 PNGs, the full FedEx smoke ran end-to-end. The remaining gaps are validation of *peripheral* mechanisms (Mermaid fallback, multi-client theme, fidelity measurement), not the core.

---

## Three-sentence verdict

My prior position deferred to A/B what Mario's production-grade bar requires resolving up front — three of the four Category 2 items (trigger-brief smoke, ACN smoke, brief-fidelity measurement) close real dark-code gaps that synthetic smokes are the *right* tool to catch, not the wrong one, and skipping them so first-real-deck-finds-out is the laziness Mario named. NFL stays deferred to v0.1 with an explicit two-client scope boundary because its risk surface is additive and routable to v1, not architectural. Three hours of work, then ship to A/B; if any of items 1, 2, 4 reveals an unfixable gap, shut down v2 — but I don't expect that branch to fire because v2's core architecture is already empirically validated and the remaining gaps are peripheral mechanisms whose validation we cheaped out on.
