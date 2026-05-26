# Artifact 5 + Intent — Reviewer A

## Q1 Verdict: SHIP IT WITH FIXES (4 specific fixes)

The fallback design is structurally sound and the integration contract with artifact 6 is mostly clean. The two-file emission (`option_X.py` + `option_X.mmd`), the SKELETON_REJECTED-with-reason-substring discriminator, the mmdc subprocess wrapper, and the brand-theme JSON are all the right shape. The worked examples render legitimate Mermaid syntax I would expect to produce usable PNGs. But four issues will hit artifact 6 if not fixed first.

**Fix 1 — Concentric rings is not actually supported. Stop claiming it is.**

`fallback.md § When the fallback fires` lists concentric rings as a fallback case. The mapping table says use `mindmap` "as the closest analogue." That is not honest. Mermaid `mindmap` produces a center node with branches radiating outward — it is a hub-spoke, not a concentric-rings diagram. A real concentric-rings slide (e.g., a maturity model with inner/middle/outer tiers) cannot be produced by any flowchart-family Mermaid diagram. There is no nested-ellipse primitive. Shipping with this listed as supported will produce wrong-shape output that the agent has no recourse against. Three acceptable resolutions: (a) drop concentric rings from the supported list and route it to v0.1 Playwright-or-skip per the existing escalation note; (b) explicitly tell the agent "if brief implies concentric rings, emit SKELETON_REJECTED with reason `concentric rings unsupported in v0 fallback` and surface for user resolution"; (c) accept the substitution but make it explicit in the variant choice — "concentric rings will render as a mindmap; user must accept this in review." Option (b) is cleanest given the Hardline #5 protocol already exists.

**Fix 2 — Fishbone will not actually look like a fishbone with `flowchart LR`.**

The worked example produces a tree, not a spine-with-branches. Mermaid auto-layout will place the four category nodes as siblings feeding the effect node, with their sub-causes feeding them — that is a left-justified tree, not the iconic Ishikawa diagonal-spine shape. The visual gap between "Mermaid flowchart of cause-and-effect dependencies" and "what a consultant means by a fishbone" is significant enough that the user will reject all three options. Either (a) test-render the fishbone example before artifact 6 starts and confirm it is acceptable, or (b) downgrade the fishbone claim — call it a "cause-and-effect tree" and stop promising it looks like a real Ishikawa. If you want a real fishbone, that is also a Playwright-escalation case.

**Fix 3 — Discriminator substring match is brittle. Tighten the contract.**

`finalize_deck.py` decides fallback vs. brief/pattern-rejection by sniffing line 1 of `option_X.py` for the literal string `"Mermaid fallback"` or `"option_X.mmd"`. Any agent that paraphrases the comment ("see the mmd file", "Mermaid render path") will be mis-routed as a brief/pattern rejection and the slide will silently disappear from the deck. Two cheap fixes: (a) require an exact marker token, e.g., line 1 must start with `# SKELETON_REJECTED: FALLBACK_MERMAID:` and finalize_deck splits on that prefix — no substring search; or (b) make the existence of `option_X.mmd` the discriminator (if SKELETON_REJECTED and a sibling .mmd exists, it is a fallback). Either is fine; ship one. The current "fuzzy substring match on a comment authored by an LLM" is the kind of contract that works in dev and silently breaks in production.

**Fix 4 — Per-client theme override mechanism is under-specified for artifact 6.**

`fallback.md` says "For other clients, `build_deck.py` reads the client template`s `theme.json` at prep time and writes a per-deck `theme/mermaid-<client>.json` override." But: (a) there is no `theme.json` spec — what fields, what color keys, where in the template? (b) the path passed to render_mermaid.py is hard-coded to `theme/mermaid-brand.json` in the example invocation, not the per-client file; (c) it is not stated whether the per-deck override sits in the skill directory (shared, gets clobbered) or in the deck output directory (per-deck, what the user wants). Artifact 6 will get this wrong without explicit guidance. Specify: the theme file lives at `{{OUTPUT_DIR}}/_theme/mermaid.json`, build_deck.py writes it at prep time by reading the client template`s brand colors via the same helpers v1 uses for theme remap, and finalize_deck passes that path to render_mermaid via `--theme`. Without this, FedEx colors will leak into other-client decks.

**Minor observations (do not block ship):** the 60-second mmdc timeout is generous but reasonable; the `_find_mmdc()` Windows path coverage is good; exit codes 1–5 distinguish failure modes cleanly. The `useMaxWidth: false` in the flowchart config is correct (otherwise mmdc scales down).

---

## Q2 Verdict: D — combination of A + B, not C

The user said: "I do not want to catch this post-review and make a bunch of edits." That kills option C on its own — the don`t-library is a detective mechanism that fires after the agent has already built the wrong thing. The agent will still build neutral first, then maybe self-correct on cross-check, but only if the relevant entry is in the pattern-specific re-check matrix and the agent honestly reads its own draft. Anti-patterns can backstop, but they cannot be the primary mechanism.

Option A alone (intent translation reference) is also insufficient — the agent has to know to consult it. Right now `prompt.md § 4` has the agent score patterns on signals like item count, comparison shape, data shape. None of those signals are rhetorical. The picker can run to completion without ever consulting intent. A reference file no one reads does not change behavior.

Option B alone (add intent as step 4 prerequisite) is the load-bearing change, but it is not enough by itself — the agent needs a translation table to consult, or it will invent its own (and the per-agent variance is exactly why v2 introduced seeds for tiebreaking).

**The combination:** add intent as a mandatory step BEFORE pattern picking in `prompt.md § 4`, and back it with a new reference file (`reference/intent.md`) that maps brief signals → editorial intent → visual treatment. Specifically:

1. **Insert a new step 0 in the picking procedure** in `prompt.md § 4` (before pattern scoring): "Identify the slide`s editorial intent from the brief. Read `EDITORIAL_EMPHASIS` and `SO_WHAT` for tilt signals. Classify into one of: RECOMMEND, COMPARE-NEUTRAL, EMPHASIZE-FINDING, WARN, REASSURE, INFORM. State the intent before pattern scoring; it is a binding constraint on variant choice in § 5."
2. **Add an "Intent tilt" subsection to each pattern`s Variants list in `layouts.md`** — concrete mapping from intent to variant choice. For 50/50 vertical: RECOMMEND tilts → side-head color contrast (gray for losing side, brand-primary for recommended side) + framing language ("evidence" left, "recommendation" right). COMPARE-NEUTRAL tilts → both side-heads gray, no asymmetric color, both columns same bullet style.
3. **Make the build report include the intent statement** so the parent session can audit it pre-finalize. Add to the § 10 BUILD REPORT block: `Editorial intent: <RECOMMEND | COMPARE-NEUTRAL | EMPHASIZE-FINDING | WARN | REASSURE | INFORM>` and `Intent reflected in: <one-line — e.g., "Option B is recommended via gray/brand-primary side-head contrast">`.

This is preventive at prompt time. The agent picks intent first, then picks pattern with intent as a scoring boost (a 75/25 split scores higher than 50/50 for RECOMMEND, a Full canvas scores higher than Top band for EMPHASIZE-FINDING), then picks variants with intent as a binding constraint. The don`t-library still backstops as detective (add one entry: "Do not ship symmetric variants on a RECOMMEND intent slide") but is not the primary mechanism.

---

## Concrete examples — brief signal → intent → visual treatment

1. **Brief says "Recommend Option B over A"** → intent: RECOMMEND → pattern: Asymmetric 75/25 preferred over 50/50; variant: anchor panel on the right (B side) with dark brand-primary fill, A side rendered as evidence cards in light treatment. If pattern picker still picks 50/50, the variant tilt forces gray side-head on A, brand-primary side-head on B, side B`s bullets recast as "Why we recommend" not "Pros of B."

2. **Brief says "Show urgency on declining margins"** → intent: WARN → pattern: Full canvas with hero claim OR Chart with annotation; variant: brand-accent (orange) on the declining trend line + dashed brand-accent callout pointing at the inflection, oversized claim typography, no soft tertiary fills anywhere on the slide. Anti-pattern entry to backstop: "Do not equal-weight evidence cards when intent is WARN — the warning needs visual weight asymmetry."

3. **Brief says "This is THE finding from the diagnostic"** → intent: EMPHASIZE-FINDING → pattern: Full canvas OR Asymmetric 75/25 with hero metric, NOT Top band + body (which is for finding + supporting cards, plural). Variant: hero numeral at oversized scale, single accent moment under the claim, supporting evidence demoted to a 12px italic line below — never elevated to peer cards.

4. **Brief says "Compare three options on five criteria"** → intent: COMPARE-NEUTRAL → pattern: Table (recommended) or N-column row; variant: no recommended-row highlight, equal column widths, equal typographic weight across all three columns. The agent must NOT pre-bias toward an option the brief does not pre-bias toward — symmetric is the correct rhetorical move here.

5. **Brief says "Reassure the board that the risk is contained"** → intent: REASSURE → pattern: Left rail + body with "controls in place" rail OR Horizontal bands (risk band on top, mitigation band on bottom dominant); variant: brand-primary on the mitigation/control elements, brand-accent reserved for the single "residual risk" indicator (small), no dark canvas, no oversized numerals. The visual hierarchy puts the mitigation above the risk, not below it.

---

## Biggest concern across both

The v2 architecture has an implicit assumption that pattern + variant fully specifies a slide. They do not. Pattern picks the chassis, variants pick the trim — but the rhetorical move (whether the slide argues, compares, warns, or reassures) is orthogonal to both. The agent can produce a pattern-correct, variant-distinct, anti-pattern-clean slide that completely fails to make the argument the brief asked for. Q2 is the more important question of the two; Q1`s fixes are tactical, Q2`s gap is conceptual. If Q2 is not fixed before artifact 6, every build will require post-hoc editorial review — the exact loop v2 was supposed to eliminate.

Q1 fix priority: Fix 3 (discriminator) blocks artifact 6 most directly. Fix 4 (per-client theme) blocks any non-FedEx use. Fixes 1 and 2 (concentric rings, fishbone) are scope honesty — ship without fixing them and the user will discover the gaps in their first non-FedEx build.
