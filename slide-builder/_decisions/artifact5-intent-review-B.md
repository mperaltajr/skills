# Reviewer B — Artifact 5 + Editorial Intent

Independent review, blind to A and C. Direct attack-mode by request.

---

## Q1 — Artifact 5 (Mermaid fallback)

### Verdict: **SHIP IT WITH FIXES**

The architecture is sound. The contract between agent -> finalize -> mmdc is unambiguous. The shape mapping table is correct (one exception below), and `render_mermaid.py` has cleaner exit-code coverage than most code review targets. But there are five issues that will bite on first real use. None are deep — all are mechanical fixes before A/B.

### What works

- **Two-file emission contract is clear.** The first-line `# SKELETON_REJECTED:` sentinel + `Mermaid fallback` substring is a clean dispatch primitive. `finalize_deck.py` can dispatch in one regex. The fact that the `.py` companion still runs `sys.exit(0)` means existing v1 finalize scaffolding won't crash — it just no-ops cleanly. Good.
- **Failure-mode coverage in `render_mermaid.py` is genuinely thorough.** Five distinct exit codes, all with stderr diagnostics, plus a Windows-path-fallback for `mmdc.cmd` that is easy to miss. The 60s timeout catches mmdc-hung-on-bad-syntax (real failure mode). The "exists but zero bytes" check catches half-rendered SVGs (also real).
- **Worked examples are good Mermaid syntax.** `flowchart TD` / `flowchart LR`, `classDef` blocks, `(["..."])` for stadium nodes, `<br/>` for line breaks, `&amp;` entity for ampersands — these all parse cleanly through current mmdc 10.x.
- **Tradeoff is acknowledged up front** ("ships as embedded PNG, not editable"). That belongs in the doc, not surprise-revealed at REVIEW.html time.

### Fixes required before ship

**Fix 1: `mindmap` does NOT substitute for concentric rings — drop the claim or escalate.**

The doc says (line 76): *"Mermaid doesn't have a native concentric-rings type. `mindmap` is the closest analogue (one central node, radiating branches)."*

This is wrong in a way that will surface as a curator failure. A mindmap renders as a horizontal tree with curved branches off a central root — it looks nothing like concentric rings. Concentric rings convey *containment* (inner = core, outer = periphery, hierarchical reading). A mindmap conveys *branching* (root has children, children have grandchildren). The semantic mismatch will register as "this is the wrong diagram" to any consultant looking at the output.

Two options:
- **(a)** Remove "concentric rings" from the fallback trigger list. If a brief implies concentric rings, route to v0.1 Playwright (HTML+CSS can do concentric rings with nested `border-radius: 50%` divs trivially) and emit `# SKELETON_REJECTED: concentric rings — needs v0.1 Playwright` until that ships.
- **(b)** Keep the trigger but generate a labeled radial layout via `classDef ring1 / ring2 / ring3` and acknowledge in the doc that this is "rings-as-tree" not "rings-as-nested-circles."

I prefer (a). Do not ship a known-wrong substitution; let SKELETON_REJECTED surface the gap honestly.

**Fix 2: mmdc CLI flag for theme config — `-c` is correct, but pin the version.**

Current mmdc (`@mermaid-js/mermaid-cli` >= 10) accepts `-c <configFile>` for the puppeteer/mermaid config JSON. The shape of `mermaid-brand.json` (top-level `theme`, `themeVariables`, `flowchart`, `mindmap`) is correct for `-c`. **However:** Mermaid CLI also has a `--cssFile` and `--configFile` (long-form), and some 10.x versions are pickier than others. The doc currently says "Node.js required" but no version pin on mmdc — that will rot. Pin: `npm install -g @mermaid-js/mermaid-cli@10.9.0` (or whatever version was tested) so the flag set is stable.

**Fix 3: `mainBkg` and the white-on-white risk in flowchart nodes.**

In `mermaid-brand.json`: `mainBkg: #FFFFFF`, `primaryColor: #4D148C`. Mermaid uses `mainBkg` as the default node fill in flowchart. So the *default* node fill is white. The worked examples override this with `classDef hub fill:#4D148C` etc., which works *because* the example author thought to add the classDef block. **If the agent writes a Mermaid spec without the classDef block** (perfectly valid Mermaid) every node renders as white-on-white-background — invisible borders unless `nodeBorder` lands a stroke. The example template makes this work; an agent improvising will not.

Fix: change `mainBkg` to `#F7F7F7` (off-white) so unstyled nodes still have a visible boundary. Better — make the prompt instruction in step Section 4.4 say "every `.mmd` MUST include the `classDef` block — copy from the worked example."

The current `fallback.md` Section "What the agent must NOT do" item 4 says brand colors come from theme override but bulk styling is in the theme file — that contradicts the worked examples, which all use `classDef` for bulk styling. Pick one model. Recommend: classDef is required (only way Mermaid does selective emphasis); theme file is for defaults that do not matter once classDef covers every node.

**Fix 4: per-client override mechanism — underspecified.**

The doc says: *"For other clients, `build_deck.py` reads the client template's `theme.json` at prep time and writes a per-deck `theme/mermaid-<client>.json` override."*

But:
- It does not say WHERE `theme/mermaid-<client>.json` is written. Inside the skill (bad — skill dir should be read-only per project convention)? In `{{OUTPUT_DIR}}`? In a project-scoped theme cache?
- It does not say HOW `build_deck.py` maps the client `theme.json` shape to the Mermaid themeVariables shape. The mapping table is documented in `fallback.md` but is the mapping code in `build_deck.py` or `render_mermaid.py`?
- `finalize_deck.py` pseudocode hardcodes `THEME_FILE` — so per-deck override does not actually flow through unless that variable is computed from deck context.

Pin this before A/B against a non-FedEx brief, or you will ship FedEx purple on a Mars deck. Concrete recommendation: `build_deck.py` writes `{{OUTPUT_DIR}}/../_theme/mermaid-theme.json` once per deck and finalize_deck.py points there; falls back to the FedEx default if absent.

**Fix 5: Subprocess invocation portability.**

`finalize_deck.py` pseudocode invokes `["py", "-3", str(SCRIPTS_DIR / "render_mermaid.py"), ...]`. `py -3` is Windows-Python-launcher syntax; the user env has it (Windows-only per CLAUDE.md), but on a CI rerun under a fresh Python it will fail. Use `sys.executable` instead — the script already runs under Python, so call back with `[sys.executable, str(SCRIPTS_DIR / ...)]`. Minor, free to fix now.

### Smaller issues (not blocking)

- The fishbone example uses `flowchart LR` with the effect on the right and causes flowing left — but writes `People --> Effect` (arrow points right). With `LR`, mmdc places source on left, target on right. That gives causes-on-left, effect-on-right, which IS the correct fishbone orientation. Good. (Worth noting because LR + reverse-direction edges is the kind of thing that quietly inverts a diagram.)
- The brand theme JSON has both `nodeBorder` and `primaryBorderColor` set to `#4D148C`. Different versions of Mermaid use one or the other depending on diagram type. Belt-and-suspenders is fine; no fix.
- `--width 1280 --height 720` produces a 16:9 PNG. Standard widescreen PowerPoint is 13.33" x 7.5" at 96 DPI = 1280 x 720. Math checks out.

---

## Q2 — How architecture should capture editorial intent

### Verdict: **B + a brief-side fallback for ambiguous intent. Recommend against A (new reference file).**

### Reasoning

Right place for intent translation is **the agent pick-time procedure in `prompt.md` Section 4**, NOT a new standalone file. Three reasons:

1. **A new reference file gets skipped.** Agents already read `layouts.md` + `anti-patterns.md` + (conditionally) `fallback.md`. Adding a fourth file creates compliance drag — every agent reads it at slide 1, half skip at slide 8. The architecture has stayed lean (5 hardline rules, 14 patterns) precisely by refusing to add reference surface area. An intent file re-bloats what v2 just collapsed from v1.

2. **Intent is a pick-time decision, not a lookup.** Intent shapes which pattern + which variant emerges. It is exactly the kind of cross-cutting consideration that belongs *in the picking procedure*, alongside item count and comparison shape. Treat it as a new signal in the signals table, not a separate axis.

3. **Anti-patterns are detective by design — wrong shape for intent.** Option C (anti-pattern entries) describes failures *after* the fact ("do not ship a neutral compare when the brief recommends B"). The whole point of the user framing is intent failures should be preventive. An anti-pattern entry like "if brief said recommend X, do not build symmetric comparison" is a band-aid; the actual lever is at pick time.

### Where in build flow

**In `prompt.md` Section 4, between current step 2 (score patterns) and step 3 (adjacency context):**

> **2.5 — Intent translation.** Re-read `{{GOVERNING_THOUGHT}}` and `{{EDITORIAL_EMPHASIS}}`. Identify the rhetorical move this slide makes. If the move is `recommend`, your variant choices must visually weight the recommended option (asymmetric split, accent on one side, hero treatment for one card). If the move is `warn`, your variant choices must visually mark the threat (dark canvas, BRAND_ACCENT on the risk element). If the move is `report` (neutral status), symmetric/balanced variants are correct. State the intent in your PATTERN PICK block.

Add an `Intent:` line to the PATTERN PICK block output:

```
PATTERN PICK — Slide {{SLIDE_N}}
  Picked       : <pattern name>
  Intent       : <recommend|warn|report|reveal|persuade|compare|explain>
  ...
```

The intent vocabulary should be small (5-7 verbs max). Do not recreate v1 chassis-intent enum from `page-types.md` (`finding/recommendation/status/process/evidence/comparison/explanation/quote/open/transition`) — half are page-type categories smuggled in as intents. Pure rhetorical moves only.

### Ambiguous-intent fallback (the angle the prompt flagged)

**When the brief itself does not make intent explicit, the agent must NOT default to neutral.**

Neutral-default is exactly the failure mode the user described — "show X" silently routes to a 50/50 balanced compare when the consultant actually meant "X is better than Y." Defaulting to neutral makes the failure systemic.

Three options for the ambiguous case:

- **(A) Refuse to build -> SKELETON_REJECTED.** Surfaces ambiguity at REVIEW.html. Forces brief revision. Honest but slow.
- **(B) Infer from `EDITORIAL_EMPHASIS` field + so-what verb.** Most briefs do have a directional verb in the so-what ("We recommend...", "This proves...", "The risk is..."). Agent extracts the verb, maps it. If no directional verb, fall back to (A).
- **(C) Default to neutral.** This is the failure mode. Do not.

**Recommendation: (B) with (A) as fallback.** Add a verb-detection step:

> If `EDITORIAL_EMPHASIS` is empty and `SO_WHAT` contains no directional verb (recommend/should/must/avoid/threat/etc.), emit `# SKELETON_REJECTED: ambiguous intent — brief does not signal whether to recommend, warn, or report` as line 1 of all three options. Surface in REVIEW.html.

This means the architecture *refuses to build* a slide whose rhetorical purpose cannot be inferred. Stronger commitment than v1 ever made and it is the right one — the alternative is wasting the user review-time fatigue on slides that were always going to need redoing.

### 5 concrete brief-signal -> intent -> visual-treatment examples

| # | Brief signal (governing thought / so-what / editorial emphasis) | Intent | Visual treatment |
|---|---|---|---|
| 1 | "We recommend Option B because it captures $14M faster and lowers integration risk." | **recommend** | 75/25 asymmetric split favoring the recommended option. Option B card gets BRAND_PRIMARY fill, hero numeral, accent rule. Option A card recedes to CARD_BG outline only. **Do not** use 50/50 vertical. |
| 2 | "Three workstreams compare across cost, speed, and risk — pick the right one." | **compare -> recommend (latent)** | Looks like compare but so-what verb "pick the right one" implies recommendation incoming. If brief evidence enumerates a winner, treat as recommend (asymmetric). If genuinely balanced, agent must SKELETON_REJECTED `ambiguous intent — comparison without verdict` and ask which workstream wins. |
| 3 | "Order-to-cash cycle time has slipped to +12 days vs plan — cause is a hand-off gap between fulfillment and billing." | **warn / diagnose** | Hero number variant: "+12 days" at 96-144px in BRAND_ACCENT (threat color). Supporting line below in TEXT_DARK. Cause as subordinate line, not co-equal. **Do not** balance metric against cause as if equal weight. |
| 4 | "Status update across 6 workstreams as of week 4." | **report** | Symmetric N-column row or N-row stack, all cards equal weight. RAG pills carry the only emphasis, not the cards themselves. No accent moment on any single workstream unless one row status explicitly differs. Neutral is correct — but only because brief verb ("update") is genuinely neutral. |
| 5 | "Three options on the table; the board will decide." | **report (deferred)** | Symmetric 3-column with explicit "no recommendation" treatment — equal visual weight, no accent moment. **Critical:** if deck author added editorial emphasis "lean toward option 2," agent must override surface neutrality and treat as recommend. The so-what verb governs; editorial_emphasis is the override switch. |

### Biggest concern

**Intent without a verb taxonomy will silently re-introduce v1 chassis problem.**

If the v2 architecture adds an "Intent" field but does not constrain the vocabulary, every agent picks a different verb ("highlight," "showcase," "demonstrate," "argue") and the field becomes useless metadata. Fix: publish a **closed list of 5-7 intent verbs** in `prompt.md` (not in a separate file), with one-line definitions and one example each. Anything else is "Intent: it is complicated" which is exactly the noise v2 was built to eliminate.

Secondary concern: ambiguous-intent SKELETON_REJECTED will fire more often than the team expects. Real consultant briefs often genuinely do not know whether they are recommending or reporting — that ambiguity is upstream of slide building. v2 will surface it rather than paper over it. Feature, not bug, but the user needs to know it is coming or they will read the first wave of rejections as a v2 failure.

---

## File path

`C:\Users\m.a.peralta\.claude\skills\slide-builder-simple\_decisions\artifact5-intent-review-B.md`
