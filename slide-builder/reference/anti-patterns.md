# Anti-patterns — the "don't" library

The aesthetics and discipline layer of `slide-builder`. Where `layouts.md` says **how** to render each pattern, this file catalogs **what looks bad even when allowed by the pattern**.

Seeded with 26 entries from the the architecture session. The library grows from every curator-flagged failure on real A/B builds.

**Wired in v0 at prompt time only** (preventive). The per-slide agent reads this file before finalizing the option script. Slide-qc vision-check wiring is open once we have real failure data from A/B builds — see SKILL.md § "Open questions open."

---

## How to use this file

1. The per-slide agent reads `layouts.md` to pick a pattern.
2. The per-slide agent reads this file before writing the option script.
3. Every entry below is a hard DON'T. If the option script would violate any entry, change the option script — not the rule.
4. If a real build hits an aesthetic failure not covered here, add it to the appropriate category. The library is permanent and append-only; old entries are deprecated with a strike-through but not deleted (so the history of decisions remains visible).

Entry format:

> **DON'T do X.** — *Why:* one line. *Do instead:* one line.

---

## Aesthetics / visual

1. **DON'T use accent bars on every slide.** — *Why:* accent is for the most important element only; ubiquity defeats the emphasis. *Do instead:* pick one element per slide that gets the accent; everything else uses brand-primary or neutral fills.

2. **DON'T use title font size below 25–28pt unless the slide is a hero.** — *Why:* sub-25pt titles fail to anchor the slide; the eye drifts. *Do instead:* default title at 28pt; hero claims at 36–45pt; never go below 25pt for a slide title.

3. **DON'T let the sub-headline shrink to caption size.** — *Why:* sub-headlines below 14pt collapse into the supporting content and lose their role as a second-tier anchor. *Do instead:* keep sub-headlines at 16pt minimum; 18–20pt when they carry meaningful editorial weight.

   **Font-floor convention (QC contract).** `finalize_deck.py::body_font_floor` enforces a two-tier floor: long-form running text (paragraphs, bullets, narrative blocks) ≥ **10.5pt**; all other text (eyebrows, kickers, category labels, chart legends, axis labels, decision-tree edges, column headers, sparkline deltas) ≥ **8.0pt hard floor**. Workers opt their long-form shapes into the 10.5pt soft floor by naming them with `body`, `bullet`, `paragraph`, or `narrative` tokens (substring match). Everything else free-floats in the 8–10.5pt band as legitimate small-by-design typography. Anything below 8.0pt fails QC regardless of role.

4. **DON'T put low-contrast text on dark fill backgrounds.** — *Why:* contrast below WCAG AA fails on projector screens, on print, and for color-blind readers. *Do instead:* use `lt1` (off-white) or a near-white tint for body text on `BRAND_PRIMARY` fills; reserve brand-accent only for emphasis tokens, never for body.

5. **DON'T use `BRAND_ACCENT_SOFT` (light purple) for text on `BRAND_PRIMARY` (dark purple) fill.** — *Why:* the specific combination fails WCAG AA contrast minimums and is borderline illegible at projection scale. *Do instead:* if text is on brand-primary fill, use white or near-white only.

   **Italic-on-dark variant (5a).** Italic body, sub-tagline, or supporting copy on a `BRAND_PRIMARY` dark-canvas fill must be **white** (`#FFFFFF`) or **near-white** (`lt1`), never `BRAND_ACCENT_SOFT` or any tinted brand color. Italics already reduce stroke contrast by ~15% against the background; combining the italic with a muted lavender / soft-accent color compounds the loss and renders the line near-invisible at projector distance. *Do instead:* italics on dark canvas use `lt1` at the same point size as the surrounding body, or skip italic styling entirely if a tint is needed.

6. **DON'T use 3+ font sizes on the same slide for body text.** — *Why:* type scale compounds; multiple body sizes destroy the visual hierarchy. *Do instead:* one body size (12pt), one supporting-detail size (10.5pt), plus the title/sub-headline. That's it.

7. **DON'T let a slide have more than one visual accent moment.** — *Why:* multiple accent moments (brand-accent stripes, hero metrics, color-coded callouts) compete and the reader can't tell what's important. *Do instead:* one accent moment per slide — pick whichever element carries the takeaway and accent only that.

8. **DON'T compress vertical spacing between text elements.** — *Why:* compressed spacing reads as cramped and amateur, even when content fits. *Do instead:* minimum 12–16pt between paragraphs in the same block, 24pt between sections, 32pt above a section heading.

---

## Structural / build

1. **DON'T put text inside curved containers.** — *Why:* python-pptx cannot shape-fit text to ovals; text wraps badly across the curve. *Do instead:* use rectangles with labels positioned outside, OR route the slide through the HTML→PNG fallback path (see `layouts.md § Fallback path`).

2. **DON'T use auto-routed connectors.** — *Why:* python-pptx auto-routing produces inconsistent diagonal lines; visual output is unpredictable. *Do instead:* set explicit `(x, y)` start and end points on every connector. For elbow connectors, use a polyline with the bend point computed explicitly.

3. **DON'T auto-shape-fit text to non-rectangular containers.** — *Why:* python-pptx silently breaks word boundaries to fit; the rendered output looks chopped. *Do instead:* size the container to the text, not the text to the container. Measure the rendered string and set container dimensions to match.

4. **DON'T let text boxes overlap each other or extend beyond their containing shape.** — *Why:* overlap is the most common visual defect in earlier builds; bounding-box collisions render as garbled stacked text. *Do instead:* compute each text box's bounding box from font metrics before placing; if two boxes would collide, fail the option script with a SKELETON_REJECTED rather than render it. Slide-qc vision-check covers this at QC time in v0.1.

5. **DON'T use Unicode glyphs that LibreOffice may not render reliably.** — *Why:* glyphs like ▲ ▼ ✓ ★ render as tofu boxes on some LibreOffice + font combinations; the failure is silent. *Do instead:* default to ASCII fallback (`UP`, `DN`, `[x]`, `*`) and only use Unicode glyphs from a verified safe set. The v2 gallery PNGs swapped ▲/▼/✓ for `UP/DN/v/*` — same convention applies here.

6. **DON'T overflow panel widths with large type.** — *Why:* hero metrics at 40pt+ in narrow panels wrap to a second line that hangs off the panel; the slide reads broken. *Do instead:* measure the text bounding box at the chosen point size against the container width before rendering. If overflow is possible, drop the point size by 4–6pt or widen the panel.

---

## Content / fabrication

1. **DON'T show invented content the brief didn't enumerate.** — *Why:* fabrication is the single most damaging failure mode in v1; agents invent a third path or fourth pillar to fill a pattern slot. *Do instead:* honor Hardline Rule #2 (no fabrication beyond brief enumeration). If the brief says 2 paths, the slide has 2 items. If the assigned split needs 4 and the brief has 2, emit SKELETON_REJECTED.

2. **DON'T invent `PART 1 OF 4` or similar enumerations the brief didn't specify.** — *Why:* invented enumerations imply structure that doesn't exist; the reader expects parts 2–4 elsewhere in the deck. *Do instead:* enumerations only when the brief explicitly declares the sequence (and only when the deck actually has all N parts).

3. **DON'T invent page-of-total markers ("02 / 05", "PAGE 3 OF 12").** — *Why:* same failure mode as enumerations — implies a structure not in the brief. *Do instead:* page-of-total only when the storyline-helper brief explicitly carries a section/total marker; otherwise the page number alone is enough.

4. **DON'T invent eyebrow text, section labels, or framework names.** — *Why:* "DIAGNOSE", "PRINCIPLE 02", "STRATEGIC LENS" all look like load-bearing structural elements; inventing them lies about the deck's organization. *Do instead:* eyebrow/section/framework labels appear only when the brief or storyline-helper produced them.

5. **DON'T repeat the same split for 3+ consecutive slides.** — *Why:* visual monotony reads as a deck-design failure even when each individual slide is correct. *Do instead:* honor Hardline Rule #3. Two consecutive slides on the same split is allowed; three is not. The rotation seed handles this automatically per-slide.

6. **DON'T build a neutral-weight layout when the brief's directive verb argues a position.** — *Why:* "recommend X" needs asymmetric weight toward X; "warn against Y" needs accent on the threat; "show urgency" needs bold typography on the deadline. Building three cosmetic variants of a neutral default strips the slide of its argument — the deck reads as a status update when it was supposed to be a recommendation. This is the failure mode the closed 7-verb directive vocabulary exists to prevent. *Do instead:* extract the directive verb from the brief (governing thought + editorial_emphasis) and map to one of `{recommend, warn, diagnose, show urgency, show progress, compare neutrally, summarize}`. See `layouts.md § "Directive verb vocabulary"` for the verb→variant-tilt translations. At least one of the three option variants must explicitly honor the directive (not just cosmetic variation). If no verb maps clearly from the brief, emit `SKELETON_REJECTED: ambiguous editorial intent` and stop — defaulting to neutral when the brief argues a position is itself the anti-pattern.

---

## Chrome / invariants

1. **DON'T put ACCENTURE / DRAFT / CONFIDENTIAL tags in the invariant top or bottom zones.** — *Why:* the invariant zones are reserved for sources, footnotes, and page numbers; brand/status tags belong elsewhere or nowhere. *Do instead:* if the client requires a DRAFT watermark, render it diagonally across the slide body — not in the chrome zones.

2. **DON'T displace the subtitle when titles grow to two lines.** — *Why:* titles that push the subtitle down cascade into the body and break the layout grid. *Do instead:* title bottom-y is fixed regardless of line count; 2-line titles grow UPWARD. The subtitle position never moves.

3. **DON'T put the legend below the chart when the right side is occupied.** — *Why:* legend-below-chart consumes vertical space that the chart needs; bottom placement is the fallback, not the default. *Do instead:* legend goes right-aligned below the sub-headline (primary); top-right of the chart only when the right side is occupied by a callout. **See `layouts.md § Chart (with quadrant mode)` for the canonical positive spec.**

4. **DON'T stack visual badges (RECOMMENDED, PRIORITY, MUST-DO, etc.) on top of body content.** — *Why:* stacked badges overlap evidence text; the badge wins visually but the reader misses the supporting content beneath it. *Do instead:* use a brand-accent left-edge stripe + tinted row fill to indicate the recommended row in a table, or an accent-fill on the recommended card in a card grid. The stripe is enough; no badge.

---

## Encoding / charts

1. **DON'T use size-encoded visual elements (bubbles, dots, tiles) without a scale legend.** — *Why:* size-encoded elements without a legend leave the reader guessing what "big" means; the chart fails to communicate. *Do instead:* if the chart uses size as an axis (bubble size = revenue, tile size = headcount), include a scale legend that shows what each size represents.

2. **DON'T swap convention positions in named frameworks.** — *Why:* BCG, Magic Quadrant, Eisenhower, and other named frameworks have established quadrant conventions; swapping positions confuses any reader who knows the framework. *Do instead:* follow the canonical positions documented in `layouts.md § Chart (with quadrant mode)`. **See that file for the full positive spec** (e.g., BCG: STARS top-right, CASH COWS bottom-right, QUESTION MARKS top-left, DOGS bottom-left).

---

## Ported anti-exemplars (visual reference library)

Nine Tier-1 failure modes ported from the legacy v1 exemplar corpus into `reference/anti-patterns/<slug>/`. Each entry includes `exemplar.png` (rendered failure case) and `WHY.md` (full diagnosis). Read these when authoring a new option script — they make the prose rules above concrete with a picture you can pattern-match against.

| Slug | Failure in one line | Category |
|---|---|---|
| [`evidence-stack`](anti-patterns/evidence-stack/) | A finding-hero block + accent rule creates a **second "section start" zone** below the title block — the slide reads as two pages mashed together. | Aesthetics / chrome |
| [`gray-text-on-brand-purple`](anti-patterns/gray-text-on-brand-purple/) | Body copy set in light gray (`#94A3B8`) on a saturated `BRAND_PRIMARY` purple panel — fails WCAG AA contrast on projector + print. | Aesthetics / contrast |
| [`midpoint-accent-splits-slide`](anti-patterns/midpoint-accent-splits-slide/) | A full-width `BRAND_ACCENT` bar at y≈336 (visual midpoint of the body) cuts the slide in half — reader treats top + bottom as unrelated content. | Chrome / accent abuse |
| [`placeholder-as-content`](anti-patterns/placeholder-as-content/) | Every text slot still says its slot label (`[Short title]`, `[Body 1]`). The slide shipped its template comments as content. | Content / fabrication |
| [`reading-order-bottom-up`](anti-patterns/reading-order-bottom-up/) | The slide's hero takeaway sits at the bottom of the body zone — reader scans top-down and never reaches the load-bearing claim. | Structural / reading order |
| [`six-panel-no-hierarchy`](anti-patterns/six-panel-no-hierarchy/) | Six equal-weight panels with no accent moment, no anchor, no hierarchy — every panel screams for attention; none win. | Aesthetics / hierarchy |
| [`table-without-column-headers`](anti-patterns/table-without-column-headers/) | Five rows of numeric data in a 4-column grid with **no header row**. Reader has to infer what each column means. | Encoding / charts |
| [`title-narrower-than-accent-bar`](anti-patterns/title-narrower-than-accent-bar/) | A short title ("[Short title]" at ~150px) sits above a full-bleed accent bar (~1152px). The bar dominates the title; the headline visually loses to its own underscore. | Chrome / proportion |
| [`vertical-rule-no-gutter`](anti-patterns/vertical-rule-no-gutter/) | A vertical `BRAND_ACCENT` rule with numbered items butting directly against it — no horizontal padding. The numerals touch the rule. | Chrome / spacing |

**How to use these in practice.** Before saving an option script, glance at the PNG of any anti-exemplar whose category matches what your slide is doing. If your slide rhymes with the failure picture, the rules above tell you what to change. The per-slide agent prompt instructs workers to consult this section at finalize time.

---

## Cross-references to layouts.md (positive rendering specs)

These rules have their canonical home in `layouts.md` (the "how to render" file). The anti-patterns above point to them; the full specifications live there.

| Topic | Canonical home |
|---|---|
| Legend placement on charts | `layouts.md § Chart (with quadrant mode)` |
| BCG / Magic Quadrant / Eisenhower convention positions | `layouts.md § Chart (with quadrant mode)` |
| Recommended-row stripe (Table) | `layouts.md § Table` cross-refs back here for the badge-stacking rule |
| Title bottom-anchor geometry | `layouts.md` (when documented) — for now see Chrome rule #2 above |

---

## Adding new entries

The library is self-improving. Every curator-flagged aesthetic failure on a real A/B build becomes a permanent entry.

**Process:**

1. During or after a build, capture the failure: which slide, which pattern, which option (A/B/C), what the curator (or user) flagged.
2. Choose the category (aesthetics / structural / content / chrome / encoding). If the failure doesn't fit, propose a new category — but check first whether an existing category covers it.
3. Write the entry in the same format: `DON'T do X. — Why: ... Do instead: ...`. Keep it tight; one rule per entry.
4. Append to the appropriate section. Do not renumber existing entries; new entries get the next available number.
5. If a new entry contradicts an old one, mark the old entry as deprecated using markdown strike-through (`~~entry~~`) with a note pointing to the new entry. Never delete; the history matters for understanding why decisions were made.

**Deprecation discipline:**

- Old entries that turn out to be wrong: deprecate, don't delete.
- Old entries that are subsumed by a clearer new entry: deprecate, don't delete.
- Old entries that the curator pushes back on: keep them, add the curator's note as a sub-bullet.

**Categorization rule (open question, open):**

Past ~100 entries, the library probably needs a more granular categorization scheme and a deprecation rule. Defer until the library actually reaches that size. See SKILL.md § "Open questions open."

---

## Source

The 26 seed entries are the locked output of the architecture session. The 9 visual exemplars under `reference/anti-patterns/` were ported from the legacy chassis-vocabulary skill's exemplar corpus during the consolidation pass (Tier-1 list per `_decisions/cleanup-plan-master-2026-05-26.md` Phase 0); the source corpus has since been archived and removed from disk. Documented at:

```
C:\Users\m.a.peralta\.claude\skills\slide-builder\_decisions\DECISIONS.md
```

§ "Starting entries for the don't library (from this session)."
