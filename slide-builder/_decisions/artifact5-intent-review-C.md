# Artifact 5 + Editorial Intent — Review C

Reviewer C, independent. Blind to A and B.

---

## Q1 Verdict — SHIP IT WITH FIXES

The fallback artifact is structurally sound and the integration contract is the cleanest piece of v2 plumbing I have read so far. Two-file emission, line-1 sentinel parsing, exit-code discipline in `render_mermaid.py`, brand theming via `-c` config — all correct. But there are real defects, two of which will bite on first real use.

### What is right

- **Exit codes are clean.** `render_mermaid.py` uses 1/2/3/4/5 distinctly. `finalize_deck.py` can branch on them. Timeouts caught. Windows npm-global fallback paths handled. This is production-shaped.
- **Two-file contract is unambiguous.** Sentinel on line 1 of `option_X.py` + sibling `option_X.mmd` + sentinel substring match on "Mermaid fallback" or `option_X.mmd` — three independent signals. A stray `SKELETON_REJECTED` from a non-fallback rejection won't trip the fallback branch. Good.
- **Variants restricted to cosmetics is the right call.** § Agent contract pinning the three `.mmd` variants to orientation / node shape / connector / color and explicitly forbidding topology drift is exactly what saves the user from reconciling three different diagrams of the same idea.
- **The worked examples are correct Mermaid.** `hub-spoke.mmd`, `porters-five-forces.mmd`, `fishbone.mmd` — syntax is valid; `classDef` blocks are applied to the right node sets; `%%{init: ...}%%` config preamble is well-formed.
- **themeVariables JSON is shaped right.** Keys (`primaryColor`, `lineColor`, `mainBkg`, `nodeBorder`, `clusterBkg`, `defaultLinkColor`, `edgeLabelBackground`) are real Mermaid theme variables. `theme: "base"` at the top is required for overrides to take effect — gotcha that's easy to miss; you didn't miss it.

### Defects to fix before shipping

1. **`mindmap` for concentric rings is a lie.** `fallback.md` § "Mermaid diagram types per pattern" says concentric rings uses `flowchart LR with manual positioning, OR mindmap`. Neither works. Mermaid `mindmap` renders a single central node with radial branches — a tree, not concentric rings. Concentric rings require nested ellipses sharing a center, which Mermaid does not produce in any diagram type. The honest move: drop concentric rings from the supported list, route it explicitly to v0.1 Playwright in the table, OR document that the v0 output for concentric rings is a hub-spoke approximation and flag the brand-fidelity gap loudly in REVIEW.html. The current text gives the agent permission to ship something that visually misses the concept.

2. **Per-client theme override spec is asserted but not implemented.** `fallback.md` says `build_deck.py reads the client template's theme.json at prep time and writes a per-deck theme/mermaid-<client>.json override`. No artifact for that exists in the prep script (artifact 6 is described as building it). Until that lands, every fallback slide renders in FedEx purple/orange even when grafted onto a different client's template. This is not a defect of artifact 5 itself, but it is a contract that artifact 5 promises and artifact 6 must honor — call it out as a binding requirement on artifact 6, not a footnote.

3. **mmdc PNG sizing vs. body zone.** Renderer defaults to 1280x720 (full slide). The slide is 1280x720 BUT the body zone is y~110-650, i.e., ~540px tall after title and footer. A 1280x720 PNG embedded full-bleed inside a 1280x540 body zone will either overflow or compress. `finalize_deck.py`'s `build_fallback_slide_pptx` pseudocode says "embedded full-bleed in the body zone" but the renderer is producing slide-sized art. Fix one of: render at 1280x540 (pass the body-zone height to the renderer), or render at 1280x720 and accept the title overlap, or render at 1280x540 padding-aware and let `finalize_deck.py` crop. Pick one before artifact 6.

4. **Font won't match.** `fontFamily: "Helvetica, Arial, sans-serif"` in `mermaid-brand.json` ignores the client template's body font (FedEx Sans, Graphik, etc.). When grafted next to a native slide using the template font, the fallback PNG will be visibly off-typeface. The per-client theme override fix (#2 above) solves this — but the v0 default sitting at Helvetica means every v0 build looks off-brand. Either match v1's font extraction at prep time or pin the v0 default to a generic that won't stand out (Inter / system sans).

5. **`shutil.which("mmdc")` on Windows misses `mmdc.cmd` in some installs.** `shutil.which` does respect `PATHEXT` on Windows 3.8+, so this might be fine in practice — but the explicit fallback locations don't include `nvm-windows` installs (`%APPDATA%\nvm\v<version>\mmdc.cmd`) or `pnpm` global. Minor — document the gap in the install instructions.

6. **No `useMaxWidth: false` enforcement in the examples.** Theme config sets `useMaxWidth: false` for flowchart, but if an agent writes an `.mmd` with its own `%%{init: ...}%%` preamble that resets `useMaxWidth: true` (the Mermaid default), the rendered PNG comes out at viewBox width, not the requested 1280px. Add "do not override `useMaxWidth`" to the don't-list in `fallback.md` § "What the agent must NOT do."

**Net:** ship it with defects 1, 3, and 4 fixed. Defects 2, 5, 6 can land in v0.1.

---

## Q2 Verdict — Option E: leave it alone (with one minor addition)

**Do not add an intent-translation layer.** v2's premise is "simpler than v1." Adding a reference file or a prompt § for editorial intent reintroduces exactly the kind of taxonomy v1's chassis-vocabulary failed at — only this time on top of an already-working primitive layer.

### The cost / maintainability angle

An intent reference file (Option A) or a prompt step (Option B) would need to enumerate the rhetorical moves: recommend, compare-then-pick, evidence-then-conclude, contrast-and-resolve, escalate, reassure, anchor, frame, etc. That list is open-ended. Editorial intent isn't a finite taxonomy — it's the *brief itself* read by a competent reader. Every entry you add becomes:

- More tokens in every per-slide prompt (already heavy with `layouts.md` + `anti-patterns.md` + `SKILL.md` references).
- A new abstraction the agent must reconcile against pattern picking. Today the picker has one job: match brief signals to a geometric pattern. Adding "and now translate the intent" doubles the cognitive load and creates a new failure mode — picking the right pattern *and* the wrong intent gloss, or vice versa.
- A new file to keep in sync with prompt.md, layouts.md, and anti-patterns.md. v1's `designer-brief.md` is 290 lines of exactly this kind of cross-referenced taxonomy and it's a maintenance tax — the kind of cost v2 was supposed to avoid.

### Does v1 encode intent implicitly via exemplars? Mostly yes

v1's `designer-brief.md` § 4 ("Page types") and § 5 ("Visual treatments") *is* the intent layer — Recommendation/CTA gets dark-panel-dominant, Comparison gets convergence-band, Hero Number gets the giant numeral. v1 doesn't say "the editorial intent is to recommend"; it says "Recommendation pages look like this." Intent -> page type -> visual treatment.

v2 collapsed page-types into geometric splits because the page-type taxonomy was too fuzzy (the "23% acceptance" problem). The cost: a brief that says "recommend option B" no longer routes to a Recommendation/CTA visual treatment automatically. The geometric picker sees "2 items being compared, takeaway at end" -> 50/50 vertical with band. Structurally correct, rhetorically neutral.

### Where the gain actually sits

The gain is real but narrow: ~5-10% of slides where the brief's *governing thought* is a directive ("recommend B," "halt the pilot," "scale to all regions") and the rhetorical move requires a visual hero that the geometric picker won't pick on signals alone.

For that 5-10%, the cheapest fix is **a single signal added to `layouts.md` § "How to pick"**: if the governing thought is a directive verb ("recommend / halt / scale / approve / reject / move / cut"), the pattern picker treats that as a strong signal toward Full canvas with hero treatment, Top band + body, or the chart's quadrant-with-recommended-marker variant. Not a new file. Not a new prompt step. One row added to the existing signals table.

### The REVIEW.html detective-mode loop

Prompt.md § 10 already requires the agent to output `SLIDE N BUILD REPORT` with `Pattern picked` and `Variant A/B/C` descriptions. Pipe those into REVIEW.html so the user sees "Pattern: 50/50 vertical · Variant A: dark canvas hero (recommend variant)" next to each option. If the agent picked a neutral comparison when the brief was directive, the user catches it at review — same loop they would catch any other miss.

Is that "catch it post-review" feeling acceptable? Yes, for two reasons:

1. **The three-option fanout is the safety net by design.** v2 ships three structurally distinct variants per slide. If even one of the three is the directive read, the user picks that one and the other two are discarded. The variant rotation seeds already push one option toward "bolder" — formalize "bolder = directive-aware where applicable" in the variant-picking § 5 of prompt.md.
2. **The alternative is worse.** An intent layer that is *almost* right is more dangerous than no intent layer at all — it gives the agent false confidence that it understood the rhetorical move when it didn't, and the user stops scanning because the build report says "Intent: recommend." Detective mode forces the user to look.

**Recommended action:** Option E. Add one row to `layouts.md` signals table for directive verbs in the governing thought, and add one sentence to prompt.md § 5 that "one of the three variants should lean toward the rhetorical move implied by the governing thought (e.g., if the brief says 'recommend X', one variant uses a hero treatment of X)." That is the whole change. No new file. No new abstraction.

---

## Brief -> intent -> visual mappings

| Brief governing thought | Intent | Visual move v2 should produce |
|---|---|---|
| "Recommend Option B over A on cost and risk." | Recommend (directive) | 50/50 vertical, but Option B card uses BRAND_PRIMARY fill + WHITE text + accent stripe; Option A is muted CARD_BG. The visual answers the recommendation before the reader scans. |
| "The pilot's KPI gap is 38% — halt and reassess." | Escalate (urgency) | Full canvas with hero numeral 38% in BRAND_ACCENT (the one accent moment); supporting facts in vertical N-row stack below. The number IS the alarm. |
| "Three workstreams; only Workstream 2 is on track." | Contrast-and-resolve | 3-column row; columns 1 and 3 use neutral CARD_BG; column 2 uses BRAND_PRIMARY header band + accent stripe. The asymmetry tells the story without a sentence. |
| "Reassure on timeline: phase 1 milestones met, phase 2 on track." | Reassure (calm) | Horizontal bands; phase 1 band shows checkmarks + complete; phase 2 shows progress to date. No accent moment — calm by absence of alarm color. |
| "Frame the choice: 2x2 of cost vs. complexity, target quadrant is low-cost, low-complexity." | Frame (positioning) | Chart with `chart_type="quadrant"`; target quadrant filled with BRAND_PRIMARY_MID + named "Target"; candidates plotted as dots, BRAND_ACCENT for the recommended one. |

All five are buildable today within the 14-pattern + variant system. None require a new reference file. They require the agent to *choose* the variant that carries the intent — which is what the third-variant-bolder rule in § 5 of prompt.md already nudges at.

---

## Biggest concern

The biggest concern is not Q1 or Q2 individually — it is that **v2's architecture review process is producing a pattern of additive proposals** (intent layer, fallback Mermaid, per-client theme overrides, variant rotation seeds, adjacency check, brief fidelity score). Each one is individually defensible. Together they recreate v1's compensating-layer stack that the DECISIONS.md doc explicitly cites as the failure mode v2 was meant to escape ("v1's chassis-vocabulary path failed at 23% curator acceptance after four compensating layers").

The discipline that has to hold: every new addition gets the "would v2 still be simpler than v1 with this in it?" question asked out loud. The Mermaid fallback survives that question because it solves a real failure case (curved containers) that the 14-pattern primitive cannot. The editorial intent layer does not survive that question — it solves a 5-10% rhetorical-miss problem with a taxonomy that fights the architecture's premise.

Pick Option E. Defend the simpler architecture. The REVIEW.html loop + the third-variant-bolder rule + a directive-verb signal in `layouts.md` is enough.
