# Smoke readiness review — Reviewer B (false-positive interrogation)

## Verdict: WITH CAVEATS

The 4 BLOCKs and 3 WARNs are largely heuristic noise, not hidden bugs. BUT the smoke run has two real defects the coordinator is not surfacing — both visible the moment you open the PNGs — and one of them is a Hardline-#3 adjacency failure that v2 explicitly claims to prevent. Green-lighting Stage 4 is fine. Calling Gate 3 a PASS without acknowledging these defects is not.

---

## Per-finding interrogation

### 1. PNG-too-small BLOCKs on covers/dividers — mostly false positives, with one real omission

Read slide 1 option_A.png (38KB cover). The brief calls for product name, tagline, presenter, date, page number. All four content tokens render: "Slide Lab", "Narrative-first slide building for consultants", "[PRESENTER NAME]", "[DATE]", plus the page-1 footer chrome. Nothing is missing. The agent didnt strip content — it produced a genuinely sparse cover. The byte floor is doing what a byte floor does: misclassifying low-ink-density designs as broken renders. That part is a false positive.

However — slide 1 option_A renders with ZERO brand color. Title and tagline are TEXT_DARK + TEXT_MID. Presenter/date are TEXT_FAINT. No purple, no orange anywhere on the canvas. A "safe default" cover for a client deck on the FedEx template that ships without a single brand-color token is a real design defect, not a heuristic artifact. Option B (dark purple canvas) and Option C (purple wordmark + orange counter-line) both carry brand. Option A reads like a generic Word doc cover that happens to live inside a .pptx. If the reviewer picks A — and A is the "safe default" the agent ships as the conservative variant — the partner-facing cover has no brand identity at all.

This is not what the byte-floor blocker was flagging, but it is the actual issue on that PNG, and the BLOCK noise is masking it.

### 2. Body-font-floor WARN on [Date] / [Presenter] — wrong diagnosis, real underlying issue

The smoke summary describes the WARN as "9pt italic for [Date]." That is not what the QC JSON shows. Slide 1 option Cs WARN is on presenter-label = "PRESENTED BY" (9pt, faint, uppercase, NOT italic) — a tiny caption above the actual [Presenter name] placeholder which is 14pt. The smoke-summary characterization is sloppy: agents are not under-sizing presenter/date content; they are using a 9pt eyebrow caption above 14pt content, which is a deliberate label/value pattern.

Is the label/value pattern wrong? No. It is a legitimate cover convention used in serious decks. The body-font-floor rule should exempt cover meta-labels.

Real issue: the floor rule fires on a convention it should know about. The QC layer doesnt yet distinguish "9pt italic body run" (genuinely a Hardline violation) from "9pt uppercase eyebrow label above 14pt value" (correct typography). This is a v0.1 false positive on the symptom, but it is hiding the fact that the QC ontology doesnt yet name "eyebrow caption" as a legitimate zone.

### 3. Adjacency advisory — this is a real defect, not just a REVIEW.html user-picks issue

Look at the four option_A PNGs in sequence:

- Slide 1A: white background, "Slide Lab" + tagline + faint footer placeholders. ~70% empty space.
- Slide 2A: white background, oversized "01" + section title + one-line subtitle. ~70% empty space.
- Slide 3A: white background, oversized "70%" + headline + supporting line. ~50% empty space.
- Slide 4A: purple background, oversized "02" + section title + one-line subtitle. ~70% empty space.

That is four consecutive slides where the dominant visual is "one giant figure on a mostly empty canvas." The architectures promise was that the agent "overrides forecast when brief signal disagrees" — and the slide-7 pattern pick DOES demonstrate that override working (forecast was Org chart, agent picked N-column row on the "no spatial hierarchy" disqualifier). Good.

But on slides 1-4, the briefs genuinely point at Full canvas for each individual slide, so the per-slide override never fires. The advisory is correct that this is bad: a partner flipping through pages 1-4 sees a deck that looks like it has nothing to say until slide 5. The aggregate texture is wrong even when every individual pick is locally defensible. v2 should be flagging this as a Stage-3-blocking issue, not a "user picks at REVIEW.html" advisory — because the user has no way to fix this at REVIEW.html. A/B/C variants for slide 2 are all Full canvas-divider variants. You cannot pick your way out of the run; you would need a re-dispatch with cross-slide adjacency awareness.

Hardline #3s softened wording is doing real work hiding this. The architecture claim that adjacency is enforced is partially false in this run.

### 4. BRAND_PRIMARY_MID didnt recur — genuine non-determinism, low severity

Slide 7 option A this run uses BRAND_PRIMARY (deep purple) for the "01/02/03" numerals — see line 57 of option_A.py: color=BRAND_PRIMARY. The previous run reportedly used BRAND_PRIMARY_MID. Looking at the rendered slide, BRAND_PRIMARY on those numerals is correct: they are hero anchors, deliberately heavy. BRAND_PRIMARY_MID would actually be wrong here — mid-tone purples on small numeral anchors would read as desaturated and weak against the white card. So this run is BETTER than the previous run on slide 7, not inconsistent. Low concern.

The smoke summarys framing — "agent picked TEXT_DARK this run" — does not match what is actually in slide_07/option_A.py. Either the summary is mis-reporting which option it is describing, or it is looking at a different variant. The recurrence claim is muddled. Not a real defect, but the smoke writeup is imprecise.

### 5. Pattern-pick non-determinism for slides 7 and 10 — both runs valid, but not equally good

Slide 7: The brief says "parallel structure, no spatial hierarchy." N-column row honors "no spatial hierarchy" via equal-weight columns reading left-to-right with no implicit ordering claim. Vertical N-row stack DOES imply a soft top-to-bottom hierarchy (item 1 reads first, item 3 reads last). N-column row is the more brief-faithful pick. This run is correct; previous run was acceptable but slightly worse. The non-determinism is real and asymmetric — there is a "right answer" the seed tiebreaker is hiding behind "both valid."

Slide 10: Brief says "single bold ask with supporting context underneath." "Underneath" is a positional cue that points at vertical arrangement — but Asymmetric 75/25 (this run) is left-right, not vertical. Full canvas (previous run) puts everything stacked vertically with one hero ask up top. By a strict literal reading of "underneath," Full canvas matches the brief better than 75/25 does. The smoke writeup claims 75/25 is "arguably better" — defensible because 75/25 models "anchor + context" cleanly — but the briefs word "underneath" is unambiguous. The agent rationalized 75/25 via the "anchor + supporting context" reading and ignored the spatial cue. Variance hides a real "best pick" preference.

This is the strongest evidence that pattern-pick non-determinism is not architecturally clean. The seed tiebreaker is doing work that should be done by tighter brief-cue parsing.

### 6. The 23 OKs — what does "ok" mean?

The QC JSONs show 6-7 named heuristic checks per option (png_render_ok, palette_compliance, title_present, footer_present, body_font_floor, placeholder_leak, shape_count_sanity). An "OK" option is one that passed all checks under the BLOCK threshold. There is no vision-layer inspection in the .qc.json files; slide-qc is not running here. The visual eyeball IS the gate at GATE3-PREVIEW.html. The 23 OKs are 23 options that didnt trip a numeric floor — not 23 options a vision pass blessed. The coordinator is reading "30/30 rendered + 23 OK" as a higher signal than it is. Half the OKs are likely visually fine. The other half just didnt trip the limited heuristics.

---

## Findings that are NOT false positives

1. Slide 1 option_A is brand-color-free. Bug, not heuristic noise. The cover-patterns "safe default" variant ships without a single brand color. If A is the partner pick, the deck opens with a generic cover.
2. Slides 1-4 are four sparse Full-canvas-family slides in a row. Hardline #3 adjacency claim fails here. REVIEW.html cant fix it because the A/B/C variants for each slide are all within the same pattern family.
3. QC ontology doesnt name eyebrow-caption / meta-label as a legitimate zone, so the 10.5pt floor fires on conventional 9pt uppercase labels. Symptom is the WARN; bug is the missing zone definition.
4. Slide 10 pattern pick ignored the briefs "underneath" spatial cue. Asymmetric 75/25 is left-right. Not a v2 break, but the seed tiebreaker is masking a brief-cue parsing miss.
5. Smoke writeup is imprecise about which color/font/option it is describing on slide 7. Mis-reporting noise that erodes trust in the rest of the report.

---

## Biggest concern

The brand-color-free slide 1A cover is the single biggest concern. Everything else is heuristic noise or known-acceptable architectural variance. But shipping a default-safe variant for the deck cover that contains zero brand color is the kind of defect that, in a real client presentation, gets caught in 0.5 seconds by the partner and undermines the whole "templates are inherited, not invented" pitch the deck is literally making on slide 7.

Fix: the cover-patterns "safe default" variant should require at least one brand token (product name in BRAND_PRIMARY OR the orange counter-line OR a brand-tinted footer rule). Dont ship a chromeless cover as a safe default.

Stage 4 can fire. Convergence hold is the right place for these. But "Gate 3 PASS" should be qualified: the heuristic floors are tolerable; the brand-color-free safe-default cover and the 4-sparse-in-a-row adjacency are not.
