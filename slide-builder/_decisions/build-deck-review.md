# build_deck.py implementation review

Reviewed file: C:\Users\m.a.peralta\.claude\skills\slide-builder-simple\scripts\build_deck.py (1010 lines).
Reviewed against: prompt.md, reference/fallback.md, reference/layouts.md, SKILL.md, _decisions/DECISIONS.md, and a sample of real storyline-helper narrative briefs on disk.

Note: the script DOES contain validate_theme() at lines 622-718, so the docstring at line 41 is consistent. I assume the "already-known gap" referred to an earlier draft. Not re-flagged.

---

### Critical issues (must fix before other scripts ship)

**1. SLIDE_HEADER_RE does not match real storyline-helper briefs — every real brief exits code 2.**

- File/line: build_deck.py:116. Pattern: `r"^##\s+Slide\s+(\d+)\s*[—\-:]\s*(.+?)\s*$"`.
- Failure mode: every storyline-helper brief on disk uses `### Slide N — Title` (three hashes). Verified against:
  - Documents/slides/client-fedex/narrative-brief-fedex-strategic-partner.md
  - OneDrive.../sessions/2026-05-14 Slide Labs Demo/narrative-brief-slide-labs-demo.md
  - OneDrive.../sessions/2026-05-15 PMO Test/narrative-brief-pmo-status.md
  - Downloads/slide-lab/skills/storyline-helper/narrative-brief-template.md (the template itself emits three hashes).
  Two-hash `## Slide N` does not exist in the wild.
- What it should be: `^#{2,3}\s+Slide\s+(\d+)...` so both depths parse. The parent section header `## Sequence` (or `## Slide Sequence` in the older FedEx brief) is content, not a slide block, so widening the pattern is safe — the `Slide\s+(\d+)` clause still gates on the digit.
- Severity: HARD STOP. The script returns exit code 2 ("no parseable slides") on every real brief. Nothing downstream can run.

**2. DECK_NOTES_RE lookahead assumes the next sibling section is `##` — wrong when `### Appendix` follows.**

- File/line: build_deck.py:117-120. Lookahead is `(?=^##\s|\Z)`.
- Real briefs (Slide Labs Demo brief) use `## Deck-level design notes` at two hashes — that part is fine. But the lookahead won't terminate on `### Appendix A — ...` (three hashes). If a brief orders sections as `## Deck-level design notes` → `### Appendix A — ...` → `## Flags`, the capture eats the appendix. Whichever ordering ships changes behavior. Brittle.
- Fix: tighten to `(?=^#{1,3}\s|\Z)`. One character.
- Severity: Major-to-Critical depending on brief ordering. Today's Slide Labs Demo and PMO briefs happen to have "Deck-level design notes" last so the capture is correct by accident.

**3. validate_theme() Check 3 only guards FedEx — every other client passes blindly even with the v1 loader bug active.**

- File/line: build_deck.py:697-716, KNOWN_CLIENT_HUE_RANGES at lines 580-585.
- Today the dict contains only "fedex". The comment correctly explains "don't add Accenture here — Accenture is also purple and would alias with FedEx." But the practical effect: for any non-FedEx client, Check 3 is a no-op. If the v1 client_theme loader returns Accenture's purple for, say, Microsoft's template, Checks 1+2 pass (primary != accent, plausible saturation, valid hex) and the slide ships with wrong colors. That defeats the architectural point of the validator.
- What it should be: either (a) require a positive client entry to be present (halt with "no hue range registered for this client; add to KNOWN_CLIENT_HUE_RANGES or pass --allow-untested-client"), or (b) demote Check 3 to a warning and add a Check 4 that asserts template.json was actually found+used (the v1 bug manifests when the loader fabricates colors from nowhere — so a non-empty slots_using_fallback for primary/accent slots should halt). The current asymmetry — halt FedEx, ship-anything-else — is the wrong default.
- Severity: Critical for any A/B test that doesn't use a FedEx template, which is most of the point of A/B testing.

---

### Major issues (should fix, but other scripts can proceed in parallel)

**4. Slide header regex misses the en-dash variant.**

- File/line: build_deck.py:116. Character class `[—\-:]` includes em-dash (U+2014) and ASCII hyphen but not en-dash (U+2013). Copy-paste from Word/Notion silently converts. Low-frequency but real. Add U+2013.

**5. extract_field truncates value at any indented `**Word**` line — including legitimate nested fields.**

- File/line: build_deck.py:196-199. Lookahead `(?=\n\s*\*\*[A-Za-z]|\Z)` allows leading whitespace before `**`. A continuation line that is `  **Sub-evidence:** ...` (indent + bold field) satisfies the lookahead and truncates the parent capture. Briefs with nested structured evidence (typical in PMO/risk-register briefs) lose the back half of Evidence.
- Fix: anchor at line-start with no preceding whitespace: `(?=\n\*\*[A-Za-z])`. Bullets and indented prose remain captured; only top-level `**Field:**` lines terminate.
- Severity: Major. Bites structured briefs.

**6. Re-run safety: orphan slide_NN/ directories from previous runs are not cleaned.**

- File/line: build_deck.py:893, 964-965. On a re-run where the previous brief had 9 slides and the new one has 5, slide_06/ through slide_09/ remain with stale _prompt.md and (after worker dispatch) stale option_*.py files. finalize_deck.py will likely iterate the output dir and try to build phantom slides.
- Fix: at start of main(), if args.out / "dispatch_plan.md" already exists, either error with "use --force to overwrite" or scan and remove orphan slide_NN/ dirs that don't correspond to a current-brief slide_n. v1 has the same problem; v2 should fix it once.
- Severity: Major. Re-runs are common (revise brief, rebuild).

**7. Front-matter parsing is dead code — built then discarded; violates the SKILL.md input contract.**

- File/line: build_deck.py:134-147, 227. front_matter is parsed and stuffed into the return dict, but main() never reads brief["front_matter"]. SKILL.md "Input contract" says: "If client_template: is present and the file exists, USE THAT PATH — do not re-ask the user." The contract requires fallback from CLI arg to front-matter; the script requires --template and never reads the brief's client_template: declaration.
- Fix: in main(), if --template is missing OR points to a non-existent file, fall back to brief["front_matter"].get("client_template"). Or delete the parse step if --template is the only source of truth (and update SKILL.md).
- Severity: Contract drift. Major.

**8. parse_yaml_simple mangles Windows paths with drive letters in front-matter.**

- File/line: build_deck.py:145-146. line.partition(":") splits on the first colon. A line `client_template: C:\Users\...\template.pptx` partitions to key="client_template", value="C", dropped: "\Users\...\template.pptx". Latent today (front_matter is unread per #7), activates the moment #7 is fixed.
- Fix: line.split(": ", 1) or a real YAML loader.
- Severity: Latent-Major.

**9. find_template_json walks the filesystem with no scope cap on non-Windows shells.**

- File/line: build_deck.py:483-489. The break at parent.name.lower() == "users" only fires on Windows-shaped paths. On WSL or a Unix dev box, the walk goes to / and could pick up an unrelated template.json at any ancestor. Add a break at parent == parent.parent (filesystem root) or Path.home().

---

### Advisory issues (worth noting, low urgency)

**10. Forecaster has narrow noun vocabulary — most real briefs forecast to the default.**

- File/line: build_deck.py:294-317. item_nouns covers path/pillar/phase/finding/option/step/principle/row/column/tile/card/force. Real briefs say "workstreams" (PMO), "levers/buckets/risks/decisions/metrics" (FedEx), "moves/levers/bets" (transformation decks). None match. Item-count returns 0 and the slide forecasts as full_canvas (default fall-through). Adjacency context is largely noise.
- DECISIONS.md acknowledges this is "context, not constraint." Not a bug, but the LIKELY_PRIOR_PATTERNS signal will be weak in production. Adding workstream/lever/bucket/risk/decision/metric/move/bet would meaningfully improve hit rate.

**11. Forecaster doesn't distinguish quadrant from other chart types.**

- File/line: build_deck.py:337-338. Any non-"none" chart_type returns the same chart pattern. Trivial fix; low urgency.

**12. chart_type is .lower()-cased indiscriminately.**

- File/line: build_deck.py:246. `**Chart type:** Quadrant (BCG)` becomes "quadrant (bcg)". The prompt template doc says values are none or scatter/line/bar/waterfall/donut/quadrant — multi-word values weren't anticipated. Worth either normalizing to the first token or preserving casing.

**13. validate_theme() Check 2 false-positives on intentionally neutral brand palettes.**

- File/line: build_deck.py:689-694. Saturation < 0.10 = "near-grey, indicates a loader bug." Some financial-services / luxury / monochrome clients have legitimately near-grey brand primaries. Halting with "loader bug" is wrong. Add --allow-neutral-brand or demote to warning.

**14. format_prior_patterns assumes contiguous 1-indexed slide numbers.**

- File/line: build_deck.py:787-800. Indexes forecasts[slide_n - 3] and forecasts[slide_n - 2] — correct only if numbers are contiguous starting at 1. A brief renumbered after deletes (`### Slide 1, 3, 5`) breaks the math. Real briefs don't skip; assumption is undocumented.

**15. parse_brief calls sys.exit(1) directly, bypassing main()'s return-code discipline.**

- File/line: build_deck.py:220, 224, 234. Harmless functionally but makes unit-testing painful. v1 has the same pattern.

---

### Implementation observations worth flagging

- **The hardcoded FedEx slot convention (colors.dk2 -> primary, colors.lt2 -> accent) appears four times in this file** (THEME_MAPPING entries + validate_theme error messages). When the v1 loader fix lands and canonical slot semantics shift, all four sites must update in lockstep. Centralizing as BRAND_PRIMARY_SLOT = ("colors", "dk2") constants would prevent drift.

- **No --force flag for re-runs.** Combined with #6, every re-run silently accumulates state.

- **HELPERS_MODULE_PATH = SKILL_ROOT.parent / "slide-builder"** assumes v1 lives next to v2 on disk. True today; brittle if v2 is ever cloned standalone or v1 is renamed.

- **Halt-on-validation-failure messaging is dense** (lines 940-957). Operators hitting this cold will be confused. Consider a one-line "what to do" at the top; three-paragraph diagnostic follows.

- **render_prompt's body-marker strip is correct and elegant.** It finds the literal `# Slide {{SLIDE_N}} build prompt` (with {{SLIDE_N}} UN-substituted) and slices from there, excluding the Placeholders documentation table at the top of prompt.md. No double-substitution risk.

- **Seed math is verbatim correct against DECISIONS.md.** content_hash = md5(governing_thought + so_what + evidence_content), pattern_pick_seed = md5(content_hash + slide_n), variant_seed_{A,B,C} = md5(content_hash + slide_n + option_letter). Matches _decisions/DECISIONS.md:163-165.

- **THEME_MAPPING is verbatim correct against fallback.md "theme.json -> mermaid themeVariables mapping".** All 22 themeVariable rows match, including fixed-value entries (background, mainBkg, clusterBkg, edgeLabelBackground, fontSize) and hardcoded fallback hexes. fontFamily is correctly handled separately with the fonts.minor + fallback stack pattern (lines 530-535).

- **Placeholder set in build_placeholders exactly matches the documented set in prompt.md** (24 tokens). No missing tokens, no extras.

- **No tests beside the file.** A fixture covering (a) `### Slide N` parsing, (b) multi-line evidence with nested bold, (c) cover-slide-with-no-governing-thought, (d) deck-notes-followed-by-appendix, (e) validate_theme failure modes — would catch most of the bugs above. Strongly recommend scripts/test_build_deck.py before the worker agent ships, otherwise the worker will be debugged against the wrong assumption about what reaches it.

- **Performance is fine.** Forecast + seed + render is O(N slides) with no I/O in the hot loop. 50-slide deck preps in milliseconds.

---

### Verdict

**HALT — fix issues #1, #2, #3 (and ideally #6 and #7) before the other scripts ship.**

Issue #1 alone means the script returns exit 2 on every real storyline-helper brief on disk; no downstream artifact can be tested end-to-end until the regex accepts `### Slide N`. Issue #3 is the same v1 client_theme bug ported into v2 — for any non-FedEx A/B test, the validator passes blindly and slides ship with wrong colors, defeating the architectural reason the validator exists. Issue #2 is a one-character regex fix that prevents a foot-gun in deck-notes parsing.

The remaining issues are recoverable in parallel work, but #1/#2/#3 are load-bearing for the first real A/B test and should be patched as a single follow-up commit before finalize_deck.py, build_review.py, compile_picks.py, and the worker agent are written against this contract. Once those land, the seed math, placeholder set, THEME_MAPPING (verbatim from fallback.md), Mermaid theme generation, dispatch-plan emission, and forecaster scaffolding are all sound and the other scripts can be built confidently against them.