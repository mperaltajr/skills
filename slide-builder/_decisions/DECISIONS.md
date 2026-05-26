# Slide Lab v2 (slide-builder) — Decisions & Architecture

> **2026-05-26 update (Path D):** v2 is now the **default and sole** Slide Lab build layer. v1 (`slide-builder/`) is being retired in Phase 8 of `cleanup-plan-master-2026-05-26.md`. All `twins/` modules and `scripts/icon_helper.py` have been re-homed under `slide-builder/`; the "parallel skill / A/B testing / nothing in v1 gets deleted" framing below is historical context only. NFL is fully out of scope (no v1 fallback).

**Status:** Architecture locked. v0 shipping. Path D consolidation in progress.
**Date:** 2026-05-25 (original) / 2026-05-26 (Path D supersession)
**Origin:** Multi-day session that diagnosed the chassis-vocabulary path failing at 23% curator acceptance, ran 4 empirical test rounds with 12 agents and 17 PNGs of evidence, and locked a simpler architecture.

---

## TL;DR

**Current (Path D, 2026-05-26):** `slide-builder/` is the default Slide Lab build layer. v1 `slide-builder/` is being archived. v2 owns its own copy of `twins/` and `icon_helper`; there is no shared infrastructure path.

v2 architecture: **9 geometric splits + 3 diagram primitives + 2 special objects + 1 HTML→PNG fallback path = 14 patterns + 1 fallback**, governed by 5 hardline rules and a "don't library" of anti-patterns.

**Historical framing (pre-Path D):** Built `slide-builder/` as a parallel skill to existing `slide-builder/`. Did NOT replace v1 initially. A/B-tested both on real briefs. Path D consolidated after v2 proved out. Estimated build was ~2 days of net-new work.

---

## Why v2 exists (the original failure modes)

1. **60% convergence bug.** 20 parallel agents picked the same layout from the chassis-vocabulary menu. Skeleton pre-assignment dropped this to 20%, but the underlying ontology was already wrong.
2. **23% curator acceptance.** After building the 19-chassis vocabulary + adjacency graph + content tags + list[1..2] schema + Layer 5 collision detector + 489-slug backfill, the first curator pass rejected 77% of agent chassis proposals. The abstraction was too granular for human users.
3. **Cross-slide twin bug.** Two adjacent same-family slides looked like twins despite nominally different chassis assignments.
4. **Slide-9 fabrication bug.** Brief said "2 paths," classifier routed to F-family (2×2 matrix), agents invented "Skeleton with overrides" and "Borderline" as fake quadrants to fill the chassis.

v1's response was to keep adding layers (skeleton pre-assignment, SKELETON_REJECTED rule, rotation, Layer 5, cross-slide collision detection, deadlock audit). Each layer compensated for a leak in the layer above. Three reviewers in round 1 flagged this as a symptom; we deferred them; the 23% data validated their pushback.

v2 collapses the lever stack into one architecture by changing the primitive — from named semantic chassis ("dark-canvas-hero") to geometric splits ("full canvas") that humans can hold in their head and validate by eyeballing the PNG.

---

## The architecture — 14 patterns + 1 fallback

### Splits (9) — pure geometric layouts

| # | Name | When to use |
|---|---|---|
| 1 | **Full canvas** | Hero claims, single statements, dividers, quotes, sparse-type slides |
| 2 | **50/50 vertical** | Symmetric compare (today vs. tomorrow, option A vs. option B) |
| 3 | **Asymmetric vertical (75/25)** | Anchor + supporting evidence; dark brand-fill panel + light content panel |
| 4 | **Top band + body** | Brand-fill headline band + cards/evidence beneath |
| 5 | **N-column row (3-9)** | Parallel principles, options, phases, journey stages |
| 6 | **Vertical N-row stack** | Anchored lists (numerals, icons, labels) |
| 7 | **Dense grid (2..5 × 2..5)** | KPI scorecards, dashboard tiles |
| 8 | **Left rail + body** | Section markers, navigation chrome + main content |
| 9 | **Horizontal bands** | Before/after, evidence/so-what, current-state/future-state |

### Diagram primitives (3) — native python-pptx

| # | Name | Implementation note |
|---|---|---|
| 10 | **Org chart (hierarchical)** | Rectangles + orthogonal connectors. Empirically clean. |
| 11 | **Swimlane (cross-functional process)** | Horizontal lanes × steps with hand-off arrows between lanes. |
| 12 | **Decision tree (branching)** | Rectangles + diagonal connectors + edge labels (Yes/No). |

### Special objects (2) — first-class helpers with their own plumbing

| # | Name | Note |
|---|---|---|
| 13 | **Chart (with quadrant mode)** | Axes + items in 2D + takeaway. `chart_type` param: `scatter`, `line`, `bar`, `waterfall`, `donut`, `quadrant`. Quadrant mode absorbs Matrix per Mario's call — BCG / Magic Quadrant / Eisenhower all render via `quadrants: [name×4]` field. |
| 14 | **Table** | Banded rows with header. Comparison tables, decision matrices. Brand-accent on recommended row. |

### Fallback path (1) — Mermaid render, v0 scope locked

**v0 supported (Mermaid):** hub-spoke, Porter's Five Forces, ecosystem map, free-form network. Agent emits `# FALLBACK_MERMAID: <reason>` on line 1 of `option_X.py` plus a sibling `option_X.mmd`; finalize_deck.py renders the .mmd to PNG via `scripts/render_mermaid.py` (mmdc 11.4.0 pinned) at body-zone dimensions (1240×540) and embeds the PNG in the slide body zone with chrome from `twins/helpers.py`. Brand colors come from a per-deck `theme/mermaid-<client_slug>.json` generated by build_deck.py from the client `template.json` — see `reference/fallback.md § "theme.json → mermaid themeVariables mapping"` for the canonical mapping.

**v0 NOT supported (deferred to v0.1):** fishbone / Ishikawa (Mermaid has no native spine syntax — auto-layout produces a left-justified tree), concentric rings (Mermaid has no analogue; `mindmap` was considered and rejected because it's hierarchical, not concentric). Both cases emit `# SKELETON_REJECTED: no Mermaid analogue — <fishbone|concentric-rings>` and surface in REVIEW.html for manual resolution.

The hard discriminator is the `# FALLBACK_MERMAID:` token, not substring matching on "Mermaid fallback". finalize_deck.py uses (token prefix) OR (sibling .mmd non-empty) as the branch condition. See `reference/fallback.md § "The .py companion — hard discriminator token"`.

---

## Hardline rules (5)

1. **Charts and tables only in their respective object layouts.** No fake chart-looking visuals in card grids. Inline sparklines/micro-charts in other layouts are allowed.
2. **No fabrication beyond brief enumeration.** If the brief says "2 paths," the slide has 2 items. No invented third or fourth.
3. **No 3+ consecutive slides use the same split.** (Softened from "no adjacent" per challenge-agent unanimous feedback — legitimate cadences like 6-finding executive sections need to be allowed.)
4. **Brief fidelity — thresholds defined in `slide-builder/tests/gate4/check_brief_fidelity.py`.** Every visible word traces to brief content or documented chrome (footer, page number, section label). Two-tier check: (a) `structural_flag_count == 0` (load-bearing non-negotiable — zero structural-count fabrications; the actual hardline). (b) Token-ratio: `PER_SLIDE_MIN = 0.30` (worst option per slide), `DECK_AVG_MIN = 0.70` (deck average). Constants inherited from v1's empirical recalibration post Gate 4 v2 first run (twice; original strawman value was 0.92 author-estimated, never validated). v2's calibration baseline pending — re-validate after 3+ real v2 builds. See `_decisions/smoke-test-finding-2026-05-25.md § "Hardline #4 recalibration"` for full provenance.
5. **SKELETON_REJECTED protocol.** If brief and pattern fundamentally disagree (e.g., brief enumerates 2 items, classifier assigned a 4-cell layout), emit `# SKELETON_REJECTED: <reason>` as first line of the option script and stop. Do not fabricate to fit. Also fires on: ambiguous editorial intent (brief doesn't map to one of the 7 directive verbs — see § "Editorial intent" below), no Mermaid analogue (fishbone / concentric rings).

---

## Editorial intent — closed directive verb vocabulary

Added during the artifact-5 review pass (2-1 reviewer split favoring inclusion; synthesis is reviewer B's middle ground). A pattern + variant doesn't fully specify a slide — the same pattern can ship as a recommendation or as a status update depending on which side of an asymmetric split gets the accent. The agent must identify the slide's **editorial intent** and tilt at least one variant to honor it.

**Closed vocabulary of exactly 7 directive verbs:**

```
recommend | warn | diagnose | show urgency | show progress | compare neutrally | summarize
```

The closed-set discipline is what prevents v1's chassis-vocab regrowth. If a brief signal does not map to one of the 7, the agent emits `# SKELETON_REJECTED: ambiguous editorial intent` and stops. **No invention of an 8th verb. No defaulting to "compare neutrally" when the brief argues a position** — defaulting to neutral IS the failure mode this vocabulary exists to prevent.

**Where it lives:**
- Canonical translations (verb → variant tilt direction): `reference/layouts.md § "Directive verb vocabulary"`.
- Agent picking procedure: `prompt.md § 4 step 1.5` (between pattern scoring and tiebreak).
- Variant rule: `prompt.md § 5` — at least one of three variants must explicitly honor the directive verb.
- Anti-pattern entry: `reference/anti-patterns.md § "Content / fabrication"` rule #6 — don't build neutral when brief argues a position.

**No separate `intent.md` file.** Multi-file maintenance was the v1 chassis-vocab failure mode the reviewers correctly flagged. The verb list lives in 3 places (layouts.md, prompt.md, anti-patterns.md) but the canonical translations sit only in layouts.md.

---

## The 3-layer quality stack

Single layer of "rules" wouldn't have caught the v1 quality problems (slides that followed rules but still looked amateur — accent bar overuse, three fonts on one slide, low contrast on dark, etc.). Quality needs three layers:

| Layer | Covers | Mechanism |
|---|---|---|
| **1. Helpers** | Geometry — where things go (positions, padding, zones) | Existing `twins/helpers.py` for chrome (title block, footer, brand colors). Raw python-pptx for body geometry. |
| **2. Hardline rules** | Process — what you must/mustn't do (the 5 rules above) | Validator + SKELETON_REJECTED protocol + brief-fidelity check |
| **3. Don't library** | Aesthetics — what looks bad even when allowed | `reference/anti-patterns.md` catalog, enforced at prompt time (preventive) + `slide-qc` vision check (detective) |

**Self-improving:** Every curator-flagged failure during real builds becomes a permanent entry in the don't library. After ~5-10 real decks, the library probably has 50-80 entries and curator-review time drops significantly.

### Starting entries for the don't library (from this session)

**Aesthetics / visual:**
- Don't use accent bars on every slide — accent is for the most important element only
- Don't have title font size below 25-28pt unless it's a hero
- Don't have sub-headline too small
- Don't put low-contrast text on dark fill backgrounds
- Don't use BRAND_ACCENT_SOFT (light purple) for text on BRAND_PRIMARY (dark purple) fill — fails WCAG AA contrast minimums
- Don't use 3+ font sizes on the same slide for body text
- Don't have more than 1 visual accent moment per slide
- Don't compress vertical spacing between text elements — minimum 12-16pt between paragraphs, 24pt between sections

**Structural / build:**
- Don't put text inside curved containers (use rectangles + labels outside, OR route to HTML→PNG fallback path)
- Don't use auto-routed connectors — use explicit (x, y) endpoints
- Don't auto-shape-fit text to non-rectangular containers
- Don't let text boxes overlap each other or extend beyond their containing shape (slide-qc vision check for bounding-box overlap)
- Don't use Unicode glyphs (▲ ▼ ✓ ★ etc.) that LibreOffice may not render reliably — use ASCII fallback (UP/DN, [x], etc.) by default
- Don't overflow panel widths with large type — measure text bounding box against container width before rendering at large point sizes

**Content / fabrication:**
- Don't show invented content the brief didn't enumerate
- Don't invent PART 1 OF 4 or similar enumerations the brief didn't specify
- Don't invent page-of-total ("02/05") or section-of-total markers the brief didn't specify
- Don't invent eyebrow text, section labels, or framework names the brief didn't provide
- Don't repeat the same layout 3+ slides in a row

**Chrome / invariants:**
- Don't use ACCENTURE/DRAFT/CONFIDENTIAL tags in invariant zones (top/bottom hold only sources/footnotes/page numbers)
- Don't displace subtitle when titles grow (titles grow upward, not down)
- Don't put legend below chart when right side is occupied
- Don't stack visual badges (RECOMMENDED, PRIORITY, etc.) on top of body content — use accent stripes or fills instead

**Encoding / charts:**
- Don't use size-encoded visual elements (bubbles, dots, tiles) without a scale legend showing what each size represents
- Don't swap convention positions in named frameworks (e.g., Stars goes top-right in BCG, never top-left)

---

## Variant rotation discipline (simplified for v2)

Within a chosen split, agents have autonomy on variant choices (typography weight, accent placement, icon vs no-icon, numeral vs no-numeral, eyebrow vs no-eyebrow). But variants must rotate deterministically to prevent variant-level convergence.

**Mechanism (locked in `build_deck.py` at prep time):**

```
content_hash      = md5(governing_thought + so_what + evidence_content)
pattern_pick_seed = md5(content_hash + slide_n)                       # tiebreaker for pattern pick
variant_seed      = md5(content_hash + slide_n + option_letter)       # variant tiebreaker per option
```

**Simplification from v1.** v1's seed was `md5(family + intent + content_hash + slide_n)`. v2 drops `family` and `intent` (both require pre-classification, which v2 explicitly avoids) and adds `option_letter` so the three sibling options A/B/C pick different variants within the chosen pattern. Without `option_letter` in the seed, all three siblings would land on the same variant — caught by the architecture review (3/3 reviewers concurred).

`content_hash` absorbs edits to the meaning-carrying fields (governing thought, so-what, evidence) so the deck doesn't re-shuffle when only formatting changes.

---

## Empirical validation summary

| Test round | Agents | Result |
|---|---|---|
| Simpler-arch build test (slidelab-intro brief) | 5 | 5/5 SHIPPABLE on diagnostic slides 5/6/9 (twin bug + fabrication bug both solved by the architecture, not by special-case rules) |
| Ontology challenge | 5 | 5/5 SHIP IT WITH FIXES (no SHIP-CLEAN; no DON'T-SHIP). Fixes incorporated above. |
| Diagram feasibility | 1 | 3/4 SHIPPABLE natively (org chart, swimlane, decision tree). Hub-spoke fails → HTML fallback. |
| Visual gallery | 1 | 11/11 SHIPPABLE on first iteration. |

**Total: 12 agents across 4 test rounds, 17 PNGs of evidence.**

Gallery viewable at `_renders/simpler-arch-test/GALLERY.html`.

---

## Shared infrastructure (works for both v1 and v2)

Don't touch. Both versions depend on:

- `twins/helpers.py` — chrome helpers (title block, footer, brand colors, add_text/add_rect/add_circle primitives)
- Gate 4 brief-fidelity + SKELETON_REJECTED protocol (§1 / §2 / §4 of the existing strawman)
- Rotation seed (simplified for v2): `md5(content_hash + slide_n)` for pattern tiebreak, `md5(content_hash + slide_n + option_letter)` for variant tiebreak — see § "Variant rotation discipline"
- `slide-qc` skill (extended for v2 with don't-library detection)
- Brief snapshot pipeline
- LibreOffice render path

---

## What was exclusive to v1 (retired in Path D)

> Historical. Path D (2026-05-26) retired v1; these artifacts are archived with the v1 skill, not maintained.

- 19-chassis vocabulary, adjacency graph, content tags
- list[1..2] composite schema
- Layer 5 cross-slide collision detector
- Deadlock audit, chassis-#24 acceptance rule
- 489-slug chassis TAGS backfill
- Family×variant×intent×relation TAGS schema

---

## What's new for v2 (the build work, ~3 days)

| # | Artifact | Estimate |
|---|---|---|
| 1 | `slide-builder/SKILL.md` — entry point, input contract identical to v1 (consume brief → emit PPTX) | 0.25 day |
| 2 | `slide-builder/reference/layouts.md` — 14 patterns documented with one paragraph + one PNG each | 0.5 day |
| 3 | `slide-builder/reference/anti-patterns.md` — don't library, starting with the 26 entries above | 0.25 day |
| 4 | `slide-builder/prompt.md` — agent prompt template around 14 patterns + 5 hardline rules + don't library + per-option variant seeds + adjacency-as-context + editorial-intent step | 0.5 day |
| 5 | HTML→PNG fallback path implementation (Mermaid 11.4.0 pinned, 4 v0-supported types, per-client theme override mechanism; Playwright escalation reserved for v0.1 if Mermaid brand fidelity fails) | 0.5 day |
| 6 | Scripts (`scripts/build_deck.py`, `scripts/finalize_deck.py`, `scripts/build_review.py`, `scripts/compile_picks.py`) + worker agent definition (`~/.claude/agents/slide-builder-worker.md`) | 1.0 day |

Total: ~3 days.

**Artifact #6 scope catch (from artifact-3 + artifact-5 architecture reviews).** Artifact #6 is **not** a near-verbatim fork of v1. Only `finalize_deck.py`, `build_review.py`, and `compile_picks.py` are near-verbatim — they operate on per-slide option scripts and need no v2-specific logic (other than `finalize_deck.py` gaining a fallback branch — see fallback.md pseudocode). `build_deck.py` is a real new build that does **five** things v1's `build_deck.py` does not:

1. **Prep-time pattern-hint pass.** Run the `layouts.md` signals table once per slide to forecast each slide's pattern. Inject the forecasted N-1 and N-2 patterns into each prompt as `{{LIKELY_PRIOR_PATTERNS}}` (adjacency context, not constraint).
2. **`content_hash` locked.** Compute `content_hash = md5(governing_thought + so_what + evidence_content)` once per slide; reuse for all four seeds.
3. **Four seeds per slide.** `pattern_pick_seed = md5(content_hash + slide_n)` plus `variant_seed_{A,B,C} = md5(content_hash + slide_n + option_letter)`. Inject all four into the prompt.
4. **Per-client Mermaid theme generation.** Read the client `template.json` at prep time, apply the mapping in `reference/fallback.md § "theme.json → mermaid themeVariables mapping"`, and write `theme/mermaid-<client_slug>.json` to the skill directory. Fall back to documented defaults for missing slots; log which slots used fallbacks.
5. **`prompt.md` rendering.** Substitute every `{{PLACEHOLDER}}` token in the template with concrete values for each slide. No editorial-intent extraction at prep time — that's the agent's job at dispatch time (Step 1.5 in the picking procedure). build_deck.py only provides the closed verb vocabulary by injecting `layouts.md` + `prompt.md` paths.

The worker agent definition (`slide-builder-worker.md`) is also a new file. It maps to v1's `deck-builder` agent in role (one-slide-per-dispatch, parallel fanout) but reads v2 references (layouts.md, anti-patterns.md, fallback.md, prompt.md).

---

## Testing protocol (historical — superseded by Path D)

> Historical. The A/B comparison protocol below was the convergence-decision mechanism. Path D (2026-05-26) declared v2 the winner before this protocol fully ran; the formal A/B harness was never built out. Section retained for the rationale only.

1. Same brief runs through both `slide-builder/` (v1) and `slide-builder/` (v2)
2. Both produce PPTX → render to PNG
3. Side-by-side comparison HTML page
4. Mario picks winner per slide; aggregate scoring across deck
5. Decision after 3 real briefs run through both:
   - Both perform similarly → keep both, route by user preference
   - v2 clearly wins → migrate v1 work to v2, deprecate chassis vocab
   - v1 clearly wins → deprecate v2, continue chassis path
   - Mixed → identify which slide types each handles better; route by classifier

---

## Open questions / deferred

**Resolved during the architecture review (no longer open):**

- ~~**Classifier for routing.**~~ Resolved: agent picks the pattern from the brief, no pre-classifier. Two light layers help — a prep-time pattern-hint pass (runs the `layouts.md` signals table once per slide and injects forecasted prior patterns as adjacency context) and a `pattern_pick_seed` for tiebreaking. Adjacency (Hardline #3) is soft-enforced at pick time and hard-enforced at finalize via a post-pass that surfaces 3+ same-split runs in REVIEW.html.
- ~~**HTML→PNG fallback implementation details.**~~ Resolved: Mermaid first with brand theme overrides. Mermaid covers the curved-container failure set (hub-spoke, Porter's, fishbone, ecosystem, free-form network). Raw HTML+CSS+Playwright reserved for v0.1 if Mermaid brand fidelity fails on a real failing brief.

**Open — cross-skill dependency on v1 theme rescope:**

- **v1 theme extraction is moving to a `brand.yml` sidecar.** 3 reviewers at the v1 layer concluded that automatic slot-mapping does not work for any client — not just the originally-reported Accenture/FedEx collision. The fix is **not** a corrected loader; it's a structural rescope to per-template `brand.yml` sidecars, human-authored once via a new `register_template.py` flow plus a setup-time smoke-build confirmation. Slot-position guessing (`colors.dk2` → primary, etc.) is being deprecated entirely. v2's two transitive inheritance paths (native chrome through `twins/helpers.py` and Mermaid theme generation through `template.json` slot lookup) both shift to `brand.yml`-as-canonical once v1's work lands.

  **v2-side state today (transitional):**
  - `scripts/build_deck.py::validate_theme()` still runs as belt-and-braces. The structural checks (primary != accent, plausible saturation/luminance) stay valid regardless of which loader produced the colors. The path-substring → expected color family check (`KNOWN_CLIENT_HUE_RANGES`) becomes unnecessary once `brand.yml` is canonical — slot-mapping guesses are what that check defends against.
  - `scripts/build_deck.py::generate_mermaid_theme()` still reads `template.json` via the 21-row slot-mapping table in `reference/fallback.md`. This is transitional; v2 doesn't need any change today.
  - `reference/fallback.md § "theme.json → mermaid themeVariables mapping"` admonition updated to reflect that the slot-position approach is being deprecated, not corrected.

  **v2-side follow-on when v1 ships `brand.yml`:**
  1. `generate_mermaid_theme()`: read `brand.yml` as the primary source; fall back to `template.json` + slot-mapping only if `brand.yml` is absent (covers the migration tail).
  2. `validate_theme()`: drop `KNOWN_CLIENT_HUE_RANGES` entirely. Keep the structural checks (primary != accent, saturation/luminance plausibility) as belt-and-braces — they're cheap and catch authoring mistakes in the `brand.yml` itself.
  3. `reference/fallback.md`: rewrite the mapping section so the canonical mapping is `brand.yml` keys → `themeVariables`. The slot-position table moves to a "Legacy fallback" subsection for templates without a registered `brand.yml`.
  4. Build report (dispatch_plan.md): log the theme source (`brand.yml` vs. slot-mapping) so failures are traceable to the right layer.

  None of these v2 follow-ons are urgent. v1's `brand.yml` work lands first; v2 picks up the change transitively. The current v0 build is shippable for A/B testing in the interim — `validate_theme()` correctly halts on the Accenture-default-bleed failure mode the rescope addresses, so v2 won't ship wrong-color decks even before v1's structural fix lands.

**Open — v0.1 HARD REQUIREMENT (blocking before production consultant-facing use):**

- **Chat-driven or GUI-driven template registration.** `register_template.py` requires a real TTY (v1's hardening pass added the "piped Y won't write" safeguard that correctly caught the auto-pick inversion observed in 3 of 3 historical templates). The TTY gate is the right safety mechanism; what's wrong is requiring it via PowerShell as the production UX path. Non-technical consultants (the actual target audience) cannot register a client template themselves.

  **Acceptable resolutions (pick one or hybrid):**
  - **Chat-driven wrapper.** `storyline-helper` or `slide-builder` detects "unregistered template," walks the user through registration in Claude Code chat, shows the smoke PNG via preview panel, takes Y/N/picks in chat. Requires lifting the TTY gate to accept verifiable non-TTY confirmations (e.g., Claude-Code-signed attribution that preserves the safety property).
  - **Web UI.** Browser-based swatch picker with inline smoke PNG.
  - **Concierge model.** Power users register templates on behalf of teams (one-time setup per client). Scales okay for dozens of clients, not hundreds.

  **Rejected:** status quo. "Open PowerShell, run this command" is not production-acceptable.

  **Cross-stream (pre-Path D framing — historical):** Originally applied to both v1 and v2 via a shared `register_template.py`. Path D (2026-05-26) retired v1; resolution is now scoped to v2 only. **Non-negotiable for declaring v2 production-ready** — Phase 3 of `cleanup-plan-master-2026-05-26.md`.

**Open for v0.1 (after first A/B builds):**

- **Don't library at scale:** how does it stay maintained as it grows past ~100 entries? Probably needs a categorization scheme (aesthetics / structural / content / chrome / encoding) and a deprecation rule. Defer until the library actually reaches that size.
- **Anti-patterns at QC time:** wire `anti-patterns.md` into slide-qc's vision check, or rely on prompt-time prevention only? v0 picks prompt-time only. Revisit after 3 real A/B builds.
- **Silent mis-pick risk (review-side fatigue).** SKELETON_REJECTED only catches enumeration mismatches and curved-container triggers. For a 20-slide deck with 3–4 silent mis-picks (agent picked a pattern the user wouldn't have), REVIEW.html fatigue ships wrong layouts. Mitigations to evaluate: surface the agent's top-2 pattern picks + the score gap in REVIEW.html; add a `# CONFIDENCE_LOW` marker when the score gap is narrow; build a regression harness that re-runs the picker against a held-out brief set after every layouts.md signals-table change. Decide before pattern #15 ships.
- **Migration of existing 489-slug exemplar corpus:** if v2 wins, do we re-tag chassis labels to split labels (cheap, auto via mapping table) or abandon the corpus?

---

## Files referenced in this doc

All artifacts now live under `C:\Users\m.a.peralta\.claude\skills\slide-builder\_decisions\`:

- This decision doc: `_decisions/DECISIONS.md`
- Gallery HTML: `_decisions/GALLERY.html`
- 11 layout PNGs: `_decisions/gallery/gallery{1..11}-*.png`
- 3 working diagram PNGs + 1 failed (hub-spoke as fallback example): `_decisions/diagram-test/diagram{1..4}-*.png`
- Diagram assessment: `_decisions/diagram-test/ASSESSMENT.md`
- Gallery notes: `_decisions/gallery/GALLERY-NOTES.md`
- 5-agent build test outputs (slidelab-intro brief): `_decisions/agent3-*` (agent 3 produced real PPTX/PNG artifacts via PowerShell workaround; agents 1, 2, 4, 5 hit write-tool denials and produced inline plans only — content captured in session transcripts)
- 5-agent ontology challenge reports: `_decisions/ontology-challenge-agent{1,2,3,5}.md` (agent 4 hit write-denial; verdict captured in session transcript)
- v1 work plan (unchanged, still at original location): `C:\Users\m.a.peralta\.claude\plans\reviewer-driven-post-build-hardening.md`
- v1 skill (untouched, parallel work continues): `C:\Users\m.a.peralta\.claude\skills\slide-builder\`

---

## v0.1 commitments — handoff hardening (Reviewer C's systemic triple)

Logged 2026-05-25 after the Stage-3 re-fire surfaced the `_meta.json`
silent-fallback bug. The point fix (build_deck writes `_meta.json`, finalize
fails loudly on its absence) closed the immediate Mermaid false-positive, but
the audit revealed a broader pattern: pipeline scripts share filenames as a
soft contract with no central registry, no schema validation, no contract
test. The triple below systematizes the fix.

**Acceptance gate**: contract test (item 2) must run in CI and pass before any
v0.1 release tag is cut.

### 1. `shared/paths.py` artifact-path registry

Create `slide-builder/scripts/_paths.py` (or a shared `shared/paths.py`
if v1 wants to converge). Every artifact path becomes a function of the
inputs:

```python
def meta_json(out_dir: Path) -> Path:        return out_dir / "_meta.json"
def slide_dir(out_dir: Path, n: int) -> Path: return out_dir / f"slide_{n:02d}"
def option_pptx(out_dir, n, letter) -> Path:  return slide_dir(out_dir, n) / f"option_{letter}.pptx"
def mermaid_png(out_dir, n, letter) -> Path:  return slide_dir(out_dir, n) / f"option_{letter}-mermaid.png"
# ... etc
```

Hardcoded path strings in scripts become a lint error (ruff + a custom rule,
or grep-based CI check). Writers and readers reference the same function;
renaming a filename is a one-line change.

### 2. Contract test at module-load time

Create `slide-builder/scripts/_contract.py`. On import, asserts every
documented handoff filename has at least one writer AND at least one reader
across the pipeline. Reads a manifest of `(filename, writer_script,
reader_scripts[])` tuples and greps the scripts directory.

Drift (e.g., adding a reader without a writer, or removing the only writer
of a file that still has readers) becomes a pytest failure, not a Gate-3 fire.

The three orphans documented in `_decisions/smoke-test-finding-2026-05-25.md`
§ "Handoff contract drift — knowingly accepted (v0.1 candidates)"
(`brief_qc.json`, `dispatch_plan.md`, `picks.json`) get explicit `accepted: true`
flags in the manifest so the test ignores them with reason recorded.

### 3. `_meta.json` schema validation

Use `pydantic` (or a hand-rolled validator if dependency cost is too high).
Define a `MetaJsonV1` model matching the current schema:

```python
class SlideMeta(BaseModel):
    n: int
    title: str
    forecasted_pattern: str
    page_type: str = ""

class DeckMeta(BaseModel):
    deck_type: str = ""
    governing_thought: str = ""
    audience: str = ""

class MetaJsonV1(BaseModel):
    schema_version: Literal[1]
    template: str
    brief: str
    out: str
    mermaid_theme: str
    client_slug: str
    slide_count: int
    generated_at: str  # top-level; build_review.py:1117 reads it here
    slides: list[SlideMeta]
    deck_meta: DeckMeta
```

`build_deck.py::write_meta_json` validates before writing; every reader
validates after loading. Adding a new key without bumping
`META_SCHEMA_VERSION` is a runtime error. Renaming a key is caught at the
writer.

### 4. CI gate before v0.1 deploy

`pytest` invocation runs items 2 + 3 (contract test + schema validation
round-trip) as part of CI. Green required before any v0.1 release tag.

---

## A/B test (formal head-to-head) — CANCELLED. Replaced by two-stage gate.

**Decided**: 2026-05-26 after 3-reviewer committee on A/B methodology.
**Committee files**: `_decisions/ab-methodology-review-{A,B,C}.md`
**Earlier framing**: this DOC § "Build philosophy" line 11 originally said *"A/B-test both on real briefs; consolidate later based on empirical comparison."* That framing is now superseded.

### Why the formal A/B was cancelled

All three reviewers independently flagged the head-to-head A/B (FedEx slidelab-intro v1 vs v2, ACN slidelab-intro v1 vs v2) as **structurally flawed for the decision it was meant to inform**:

1. **slidelab-intro is biased toward v2** (Reviewers B + C). The brief was authored after v2's design vocabulary stabilized; v2's pattern set aligns 1:1 with the brief's slide shapes. Running the same brief through v1's named-chassis vocabulary produces an artificial mismatch that scores against v1 unfairly.

2. **No v1-NOW baseline exists** (Reviewer B, load-bearing). v1's historical "23% curator acceptance" data predates *all* of: the theme rewrite, the path-resolution fixes documented at `build_review.py:243` / `compile_picks.py:202`, and Phase 3 color correction at registration time. A 2026-05-26 v2 cannot be compared against a 2024-era v1 — that's not an A/B, that's a v1-stale vs v2-current confound.

3. **Category 2 smokes already produced the architecture-validation evidence the A/B was meant to generate** (Reviewer C). Item 1 (FedEx trigger-brief) validated SKELETON_REJECTED + FALLBACK_MERMAID + sanity check + loud-failure paths. Item 2 (ACN slidelab-intro) validated per-client theme handoff + brand.yml-correct color rendering + adjacency advisory. Cross-client comparison validated bounded non-determinism (9/10 pattern agreement). The A/B would have produced *less* signal than the smokes already on file.

### Replacement: two-stage gate

#### Stage A — prerequisite: v1-NOW binary ship-test on slidelab-intro

**Locked 2026-05-26 after 3-reviewer protocol committee** (`_decisions/stage-a-protocol-review-{A,B,C}.md`). The earlier framing in this document that compared Stage A's number to the historical 23% acceptance figure is **superseded**: the committee was unanimous that the direct comparison is invalid (different corpus, methodology, and rubric — the 23% had statistical mass on a multi-deck real-client mix, slidelab-intro is a single 10-slide regression fixture engineered against v1's failure modes). Stage A is reframed as a **binary ship-test on v1-NOW**, not a re-measurement.

**Protocol — locked**:

1. **One v1 run** of `slidelab-intro-shippable.md` through current v1 (theme rewrite applied, path fixes applied, Phase 3 color correction applied, brand.yml sidecar contract applied). v1 is md5-deterministic; multiple runs add wall-clock cost without adding signal (Reviewer A).

2. **Mario writes per-slide predictions BEFORE opening any PNG.** Pre-commitment artifact at `_decisions/stage-a-precommit.md`. For each of the 10 slides, one line: "I expect v1-NOW will ship / fail on this slide because ____." This mitigates the first-slide gestalt anchoring failure mode where the directional read of slide 1 sets the acceptance rate for slides 2–10 (Reviewer A).

3. **Two binary scoring axes per slide:**

   | Axis | Question | Type |
   |---|---|---|
   | **SHIP-AS-IS** | Would Mario hand this slide to a FedEx exec without edits? | yes / no |
   | **FABRICATION FLAG** | Did v1 produce content that v2's SKELETON_REJECTED or FALLBACK_MERMAID would have refused? (Content invented beyond the brief; honest pattern-mismatch built anyway with workaround.) | yes / no |

   Each slide gets two binary calls. No Likert. No bucketing into cosmetic / structural / fabrication (Reviewer B's nuance is preserved in the binary FABRICATION FLAG — it captures the load-bearing v2-justifies bucket and leaves cosmetic/structural as the implicit residual when SHIP-AS-IS is "no" but FABRICATION FLAG is "no").

4. **Single scoring event.** One sitting, one pass, no re-scoring. Rubric drift via re-scoring produces confidently wrong numbers — the most dangerous Stage A failure mode (Reviewer B). If Mario feels he cannot decide on a slide after the first read, the decision is forced: SHIP-AS-IS defaults to "no" (conservative — would-not-ship is the safe default when uncertain).

**Decision rule — locked BEFORE scoring, do not modify mid-flight**:

Three-band outcome tree. Stage A produces a final decision in all three bands. Stage B as a separate measurement event does **not** fire from any band — the "Stage B" specification documented below is reframed as Path D-soft's natural rolling production validation, running WITHIN Path D-soft when Path D-soft is the outcome (bands 1 and 3), not as a fork that decides between Path D-soft and consolidate.

| Band | Criterion | Outcome |
|---|---|---|
| **(1) STRONG PASS** | ≥ 8/10 SHIP-AS-IS **AND** ≤ 1 FABRICATION FLAG | Gap closed. **Path D-soft confirmed.** Formal A/B permanently cancelled. The natural rolling production pilot (see "Stage B" below) begins as **validation, not a decision fork**. |
| **(2) STRONG FAIL** | ≤ 3/10 SHIP-AS-IS **OR** ≥ 3 FABRICATION FLAGS | v2 **categorically justified**. **Consolidate to v2.** No Path D-soft, no v1 fallback. No further measurement event — evidence already conclusive. |
| **(3) MIDDLE** | 4–7/10 SHIP-AS-IS **AND** ≤ 2 FABRICATION FLAGS | **Path D-soft default** (committee 2-of-3 majority: slidelab-intro is structurally biased; running an A/B on it would be ceremony, not measurement). **Re-evaluate after the first 2 real FedEx/ACN production decks.** No separate A/B measurement event on slidelab-intro. |

**Independent override — ≥ 2 fabrication flags forces Path D-soft minimum, regardless of ship-count.**

Architectural advantage is demonstrated by ≥ 2 fabrication events even if visual quality looks OK across the deck. This override prevents a high-ship-count, high-fabrication outcome from routing to "v1 ships fine" — the fabrication signal is the load-bearing v2-justifies bucket and cannot be outvoted by visual ship-as-is calls. Operationally: a 9/10 ship-as-is + 2 fabrication outcome lands in Path D-soft (band 3), not band 1.

Stage A runs in v1 chat. **No work on this side**; v2 stands down on A/B prep.

#### Stage B — Path D-soft rolling validation on real production work

**Trigger reframed**: Stage B is no longer a fork that decides between Path D-soft and consolidate. It runs **within Path D-soft** as the natural rolling production-validation pilot, triggered by:

> **Path D-soft is in effect AND the first 2 real FedEx/ACN production decks have completed.**

The validation pilot is what tells us whether Path D-soft holds (v2 default for scoped clients with v1 as documented fallback) or whether real-deck evidence forces a re-evaluation. Stage A's three-band tree never routes here directly — it routes to Path D-soft (bands 1 + 3) or to consolidate-to-v2 (band 2). Path D-soft *plus* 2 real decks → this validation fires.

**Pre-scoring step (load-bearing — unchanged)**: capability-bucket every slide BEFORE scoring. Buckets:
- **Symmetric-shippable**: both v1 and v2 produced a buildable slide on this number.
- **v1-only**: only v1 produced output (v2 hit SKELETON_REJECTED or FALLBACK_MERMAID and the operator wants the slide built).
- **v2-only**: only v2 produced output (v1's chassis library didn't have a match).

Score ONLY within the **symmetric-shippable subset**. Asymmetric buckets are reported as capability-coverage data, not as wins/losses.

**Decision rule at the validation pilot**:
- v2 stays default if BOTH ≥ 60% slide-level wins in the symmetric subset AND a clear deck-level coherence win (storyline reads as one argument, not 8 disconnected slides).
- **3-week hard stop** from kick-off. If results are ambiguous at the 3-week mark, **Path D-soft continues as-is** (v2 default, v1 fallback) — ambiguity is the signal that the difference doesn't justify a forced consolidation. No extensions.

### Scope of v2 work during Stage A

**v2 stands down on A/B prep**. No further dev on the v2 side specifically for A/B execution. Item 4 (formal A/B prep) is removed from the v0 backlog. v2's v0 architecture is locked per the convergence-hold declaration (`_decisions/convergence-hold-declaration-2026-05-26.md`).

Stage A outcome → v2 next action:
- **Band 1 (STRONG PASS) → Path D-soft confirmed.** v2 stays at v0 in production for FedEx + ACN. v0.1 work resumes on the documented handoff-hardening triple (`shared/paths.py`, contract test, pydantic schema validation, CI gate) and the documented v0.1 candidates (`nfl-scope-boundary.md` acceptance criteria, tighten QC `PNG too small` heuristic, post-pass adjacency check, etc.). Rolling validation pilot fires after first 2 real production decks complete.
- **Band 2 (STRONG FAIL) → consolidate to v2.** v1 fallback is removed. v0.1 work resumes immediately on the same documented backlog, plus a "v1 deprecation" work item.
- **Band 3 (MIDDLE) → Path D-soft default.** Same as band 1, but with explicit re-evaluation after 2 real production decks; if real-deck evidence shifts the picture, the v0.1 backlog can be re-prioritized at that point.

In all three bands: **no architecture changes** during the convergence hold (which lifts only on Stage A result, per `convergence-hold-declaration-2026-05-26.md`).

---

## Mario's standing preferences (from memory — applies to v2 build)

- **Be direct, not polite.** Push back on premature/vague ideas; don't soften the critique.
- **Validate user architecture before building.** Restate framing in user's words and confirm BEFORE dispatching agents.
- **Always provide file paths as plain text** — not only markdown links.
- **Preview panel active** — tell user when HTML files appear in preview, also give file paths.
- **Send paste-ready prompts** when synthesizing for hand-off to another chat — end with the paste-ready text itself, not "want me to tighten this?"
- **Deck artifacts live with the project** — never inside the slide-builder skill.
- **HALT before running automated checks the first time** — explicit user approval required before Gate 4 v2 runs.
