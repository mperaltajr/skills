# Skeleton promotion plan — 2026-05-18

Triage of all 89 reference templates in [references/index.md](../../references/index.md) against the current 8 skeletons in this folder. Each row is one source slide.

## Capability flags

- **TOOL-OK** — `promote_skeleton.py` handles cleanly as-is (text shapes, 1–3 columns)
- **NEEDS-TABLE** — uses native PPT table; need tool extension to recurse into cell text frames
- **NEEDS-GROUP** — uses grouped shapes (chevrons, connectors, org-chart boxes); need tool extension to recurse into group children
- **NEEDS-CHART-EXT** — chart with a treatment variant not currently in chart-with-takeaway family
- **HAND-BUILD** — complex visual model (fishbone, value chain, wheel, etc.); must be constructed by hand, no tool path
- **COVERED** — already supported by an existing skeleton or its variants
- **SKIP** — dupe of another row, doc/educational slide, or low-value variant

---

## 01_Executive Summary

| Slide | Description | Flag | Notes |
|---|---|---|---|
| 2 | Educational guide | SKIP | doc slide |
| 3 | Four-row labeled list | TOOL-OK | 1-col repeated label+paragraph |
| 4 | Section-headed bullet groups | TOOL-OK | 1-col, 4 section headers + bullets |
| 5 | Three-col problem/solution/recommendation | COVERED | use existing three-column, add "progressive emphasis" variant later |
| 6 | Options comparison table + bottom strip | NEEDS-TABLE | 4-col × 3-row native table |
| 7 | Two-col dashboard (bar + 2×2 grid) | HAND-BUILD | mixed chart + tile grid |
| 8 | Four numbered buckets | TOOL-OK | 4-col, may degrade naming — test |
| 9 | Comparison matrix with row labels | NEEDS-TABLE | native table |
| 10 | Harvey-ball comparison matrix | NEEDS-TABLE | native table + Harvey balls |

## 02_Bar Charts — fully COVERED by chart-with-takeaway 8-variant family

| Slides 2–11 | Various bar/column chart layouts | COVERED | chart-with-takeaway handles all via variant + bg=dark + chart_zone positioning |

## 03_Line Scatter Charts

| Slide | Description | Flag | Notes |
|---|---|---|---|
| 2 | Scatter with positioning bands | NEEDS-CHART-EXT | extend chart-with-takeaway to render scatter PNG; reuses "bottom-strip" layout |
| 3 | 2×2 quadrant matrix (data scatter) | NEEDS-CHART-EXT | scatter chart with quadrant labels; new variant |
| 4 | Buying-criteria line chart | NEEDS-CHART-EXT | line-chart variant of chart-with-takeaway-third |
| 5 | Scatter with quadrant labels + grouping | HAND-BUILD | competitors in dashed-border colored boxes — custom shapes |
| 6 | Bubble chart full-width | NEEDS-CHART-EXT | full-width bubble variant |
| 7 | Bubble chart + comments panel | NEEDS-CHART-EXT | bubble variant of chart-with-takeaway-third |

## 04_Competitive Analysis

| Slide | Description | Flag | Notes |
|---|---|---|---|
| 2 | Two-col rows with arrow connectors | NEEDS-GROUP | arrow connectors are grouped |
| 3 | Four image-headed buckets | TOOL-OK | 4-col text — may degrade naming |
| 4 | Channel adoption matrix | NEEDS-TABLE | native table |
| 5 | Survey demographics dashboard | HAND-BUILD | bars + age pyramid + 4 small charts |
| 6 | Competitor profile with logos + Harvey balls | NEEDS-TABLE | native table + image placeholders |
| 7 | Competitor revenue/margin | NEEDS-TABLE | native table + inline mini-bars |
| 8 | 5-competitor matrix with row labels | NEEDS-TABLE | native table |
| 9 | Product feature matrix grouped by area | NEEDS-TABLE | native table |
| 10 | Feature presence with check/X | NEEDS-TABLE | native table + status icons |
| 11 | Core vs additional feature matrix | NEEDS-TABLE | native table |

## 05_Frameworks — almost all HAND-BUILD

| Slide | Description | Flag | Notes |
|---|---|---|---|
| 2 | Fishbone diagram | HAND-BUILD | complex visual |
| 3 | Action list + impact-feasibility 2×2 | HAND-BUILD | list + quadrant with dots |
| 4 | Strategy house | HAND-BUILD | hierarchical metaphor |
| 5 | 4-step cycle | HAND-BUILD | cycle arrows + icons |
| 6 | 5-tier maturity pyramid | HAND-BUILD | pyramid shape + side labels |
| 7 | Fishbone variant | SKIP | dupe of slide 2 |
| 8 | Range bars by area grouping | NEEDS-GROUP | custom range bar shapes |
| 9 | Issue tree | HAND-BUILD | hierarchical tree |
| 10 | SMART framework rows | TOOL-OK | 5 colored letter boxes + columns — test |
| 11 | Porter's value chain | HAND-BUILD | chevron + support arrows |

## 06_Process Journey

| Slide | Description | Flag | Notes |
|---|---|---|---|
| 2 | Three-state progression | COVERED | three-column variant |
| 3 | 4-step cycle with arrows | HAND-BUILD | dark circles + curved arrows |
| 4 | 5-step ribbon process | NEEDS-GROUP | chevron ribbon + cards below |
| 5 | 6-step chevron with 2-row bands | NEEDS-GROUP | chevrons + bullet bands |
| 6 | Wave progression | HAND-BUILD | location pins on ascending tiers |
| 7 | Staircase with side callouts | HAND-BUILD | isometric steps |

## 07_Roadmaps

| Slide | Description | Flag | Notes |
|---|---|---|---|
| 2 | 3-phase ribbon with row bands | NEEDS-GROUP | chevrons + 3 row bands |
| 3 | 3-bucket phases + bottom takeaway | COVERED | three-column variant |
| 4 | Multi-phase timeline with rows | NEEDS-GROUP | chevron timeline + content bands |
| 5 | 3-phase × 3-row band matrix | NEEDS-GROUP | chevrons + bands |
| 6 | Gantt with phase grouping | HAND-BUILD | task bars + milestone diamonds |
| 7 | Phase ribbon + 3 buckets + takeaway third | NEEDS-GROUP | mixed |
| 8 | 3-phase chevron with 2-row deliverables | NEEDS-GROUP | chevrons + bands |
| 9 | Workstream Gantt with milestones | HAND-BUILD | task bars + stage gates |
| 10 | Country launch Gantt + criteria panel | HAND-BUILD | Gantt + side panel |
| 11 | 7-step process with milestones | NEEDS-GROUP | chevron + milestone diamonds |

## 08_Structured Text — almost all NEEDS-TABLE

| Slide | Description | Flag | Notes |
|---|---|---|---|
| 2 | 5-row labeled list with colored labels | TOOL-OK | 1-col repeated row |
| 3 | Title/score/description comparison | NEEDS-TABLE | 5×3 table |
| 4 | 5×5 Harvey ball matrix | NEEDS-TABLE | native table |
| 5 | 4-trend matrix with examples | NEEDS-TABLE | native table |
| 6 | Hypothesis evaluation matrix | NEEDS-TABLE | native table + check/X |
| 7 | Parameter list with category dots | TOOL-OK | 7-row labeled list with colored circles |
| 8 | Personnel/role data table | NEEDS-TABLE | 12×6 data table |
| 9 | Area-grouped feature comparison | NEEDS-TABLE | grouped row labels |
| 10 | Assessment status overview matrix (RAG) | NEEDS-TABLE | RAG status dashboard |

## 09_Cover Divider — all TOOL-OK ✅ (best starting batch)

| Slide | Description | Flag | Notes |
|---|---|---|---|
| 2 | Dark-mode appendix divider | TOOL-OK | text on dark bg |
| 3 | Gradient agenda divider | TOOL-OK | centered title on gradient |
| 4 | Hero numeral section divider | TOOL-OK | title + numeral |
| 5 | Numbered TOC | TOOL-OK | header + numbered list |

## 10_Org Charts — all NEEDS-GROUP

| Slide | Description | Flag | Notes |
|---|---|---|---|
| 2 | 5-branch org chart | NEEDS-GROUP | boxes + connector lines |
| 3 | 5-branch org variant | SKIP | dupe of slide 2 |
| 4 | Three parallel mini-trees | NEEDS-GROUP | 3 small trees |
| 5 | Org with bulleted children | NEEDS-GROUP | branches + bullet lists |
| 6 | Standard 3-level org chart | NEEDS-GROUP | 3 levels |
| 7 | Org chart with shared resource panel | NEEDS-GROUP | org + side panel |

## 11_Visual Models — all HAND-BUILD

| Slide | Description | Flag | Notes |
|---|---|---|---|
| 2 | 10-step curved sequence | HAND-BUILD | S-curve of numbered circles |
| 3 | Cycle with corner callouts | HAND-BUILD | 4 circles + curved arrows |
| 4 | Pentagon overlap + comparison table | HAND-BUILD | pentagon + table — mixed |
| 5 | Half-circle 5-segment | HAND-BUILD | wedges + leader lines |
| 6 | 5-tier maturity pyramid (variant) | SKIP | dupe of 05s6 |
| 7 | 3D cube pyramid | HAND-BUILD | isometric cubes + callouts |
| 8 | Wheel infographic | HAND-BUILD | central circle + 8 wedges |
| 9 | Hexagon infinity loop | HAND-BUILD | 6 overlapping hexagons |

## 12_KPIs and Dashboards

| Slide | Description | Flag | Notes |
|---|---|---|---|
| 2 | KPI tile dashboard | NEEDS-GROUP | tiles + chart |
| 3 | Strategy KPI dashboard table | NEEDS-TABLE | RAG + trend arrows |

---

## Capability tally

| Flag | Count | Tool work first? |
|---|---:|---|
| TOOL-OK | 11 | None — run now |
| NEEDS-TABLE | 18 | Extend `promote_skeleton.py` to recurse into table cells |
| NEEDS-GROUP | 15 | Extend `promote_skeleton.py` to recurse into group children |
| NEEDS-CHART-EXT | 5 | Add scatter/line/bubble variants to chart-with-takeaway |
| HAND-BUILD | 18 | Construct by hand, no tool path |
| COVERED | 12 | Skip — already in library |
| SKIP (dupes/doc) | 5 | Skip |
| **Total** | **84** | (89 source − 5 SKIP) |

## Phase order

1. **Phase A — TOOL-OK batch** (no tool work). Promote 11 skeletons. ~45 min.
2. **Phase B — Table extension**. Extend `promote_skeleton.py` to iterate into table cells, name tokens by row/col position. Then promote 18 NEEDS-TABLE skeletons. ~2 hours total.
3. **Phase C — Group extension**. Extend `promote_skeleton.py` to recurse into grouped shapes. Then promote 15 NEEDS-GROUP skeletons. ~2 hours total.
4. **Phase D — Hand-built family** (18 skeletons). Each is a custom shape composition. ~5–8 hours total.
5. **Phase E — Chart extension** (5 chart variants). Extend `chart-with-takeaway` skeleton.yaml + chart generator. ~1 hour.
6. **SKILL.md routing rewrite + smoke test**. ~1 hour.

## Realistic single-session yield

| End-of-session option | Skeletons added | Wall time | Covers |
|---|---:|---|---|
| Phases A + B + E | ~34 | ~4 hours | All text-only + all tables + chart variants. Covers most missed slides in typical strategy decks. |
| Phases A + B + C + E | ~49 | ~6 hours | Adds org charts and roadmap variants. Covers ~90% of consulting patterns. |
| All phases | ~67 | ~10–12 hours | Full library including hand-built visual models. Multi-session. |

**Recommendation:** Phases A + B + C + E in one session. Defer hand-built visual models (fishbone, wheel, etc.) to a follow-up session — they're lower frequency in real strategy decks and need careful per-slide design.
