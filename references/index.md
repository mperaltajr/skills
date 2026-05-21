# Slide Lab reference index

The model's first move when designing a slide is to search this index for the closest-fit template. Use the page-type and "Reach for when" fields as filters; the "Avoid when" field prevents superficial matches that fail in practice.

Once the right template is identified, the build phase calls `copy_template_slide.py` with the source PPTX path + slide number + placeholder map. The copied slide inherits MBB-quality geometry from the source; the user's CLAUDE.md handles branding (colors, fonts) at render time via slide-master inheritance.

**Coverage:** 89 template slides across 12 reference PPTX files. Slide 1 of each file is the section divider for that file (12 total) and is excluded as a non-template.

---

## Quick navigation by layout family and variant

Auto-classified from the per-slide `Shows:` and `Page-type:` fields below. Use these lookups to jump straight to candidate templates once you've picked a layout family and (where applicable) a recipe variant from `slide-builder/reference/visual-treatment-library.md`. Always re-check the per-slide entry's `Reach for when` and `Avoid when` before copying — auto-classification matches on visual treatment vocabulary, not content fit.

Slides may appear under more than one family when their composition serves multiple purposes (e.g., a comparison matrix that's also chart-led).

### By layout family

**Cover / Divider** (8 templates)
- `02_Bar Charts` / slide 2 — Stacked column with growth callout + comments panel
- `03_Line Scatter Charts` / slide 2 — Scatter plot with positioning bands
- `04_Competitive Analysis` / slide 3 — Four image-headed buckets
- `06_Process Journey` / slide 5 — 6-step chevron with 2-row bands
- `09_Cover Divider` / slide 2 — Dark-mode appendix divider
- `09_Cover Divider` / slide 3 — Gradient agenda divider
- `09_Cover Divider` / slide 4 — Hero numeral section divider
- `09_Cover Divider` / slide 5 — Numbered table of contents

**Insight / Finding** — no exact matches in current library; compose fresh from chassis primitives following the recipe.

**Three-column parallel** (8 templates)
- `01_Executive Summary` / slide 5 — Three-column problem/solution/recommendation
- `01_Executive Summary` / slide 8 — Four numbered buckets
- `04_Competitive Analysis` / slide 3 — Four image-headed buckets
- `06_Process Journey` / slide 2 — Three-state progression
- `07_Roadmaps` / slide 3 — 3-bucket phases with bottom takeaway
- `07_Roadmaps` / slide 7 — Phase ribbon + 3 buckets + takeaway third
- `08_Structured Text` / slide 3 — Title/score/description comparison table
- `08_Structured Text` / slide 5 — 4-trend matrix with examples

**Two-column with insight panel** (8 templates)
- `01_Executive Summary` / slide 7 — Two-column dashboard
- `02_Bar Charts` / slide 8 — Channel landscape (table + chart)
- `04_Competitive Analysis` / slide 5 — Survey demographics dashboard
- `05_Frameworks` / slide 3 — Action list + impact-feasibility matrix
- `07_Roadmaps` / slide 10 — Country launch Gantt with criteria panel
- `10_Org Charts Team Governance` / slide 7 — Org chart with shared resource panel
- `11_Visual Models` / slide 4 — Pentagon overlap + comparison table
- `12_KPIs and Dashboards` / slide 2 — KPI tile dashboard

**Headline + chart** (20 templates)
- `01_Executive Summary` / slide 7 — Two-column dashboard
- `02_Bar Charts` / slide 2 — Stacked column with growth callout + comments panel
- `02_Bar Charts` / slide 3 — Full-width 100% stacked column
- `02_Bar Charts` / slide 4 — Stacked column with multiple growth callouts + YoY bubbles
- `02_Bar Charts` / slide 5 — Three side-by-side clustered columns
- `02_Bar Charts` / slide 6 — Horizontal bar with average benchmark
- `02_Bar Charts` / slide 7 — 100% stacked column with totals column
- `02_Bar Charts` / slide 8 — Channel landscape (table + chart)
- `02_Bar Charts` / slide 9 — Stacked column small multiples with cumulative top-N
- `02_Bar Charts` / slide 10 — Horizontal bar with top-N highlight
- `02_Bar Charts` / slide 11 — Combo chart (column + line)
- `03_Line Scatter Charts` / slide 2 — Scatter plot with positioning bands
- `03_Line Scatter Charts` / slide 3 — 2x2 quadrant matrix
- `03_Line Scatter Charts` / slide 4 — Buying-criteria comparison line chart
- `03_Line Scatter Charts` / slide 5 — Scatter with quadrant labels and grouping
- `03_Line Scatter Charts` / slide 6 — Bubble chart full-width
- `03_Line Scatter Charts` / slide 7 — Bubble chart with comments panel
- `04_Competitive Analysis` / slide 7 — Competitor revenue/margin comparison
- `05_Frameworks` / slide 8 — Range bars by area grouping
- `12_KPIs and Dashboards` / slide 2 — KPI tile dashboard

**Visual Model** (29 templates)
- `04_Competitive Analysis` / slide 4 — Channel adoption matrix
- `04_Competitive Analysis` / slide 5 — Survey demographics dashboard
- `05_Frameworks` / slide 2 — Fishbone diagram
- `05_Frameworks` / slide 4 — Strategy house framework
- `05_Frameworks` / slide 5 — 4-step cycle visual model
- `05_Frameworks` / slide 6 — 5-tier maturity pyramid
- `05_Frameworks` / slide 7 — Fishbone (variant of slide 2)
- `05_Frameworks` / slide 9 — Issue tree
- `05_Frameworks` / slide 11 — Porter's value chain
- `06_Process Journey` / slide 3 — 4-step cycle with arrows
- `06_Process Journey` / slide 4 — 5-step ribbon process
- `06_Process Journey` / slide 5 — 6-step chevron with 2-row bands
- `06_Process Journey` / slide 6 — Wave progression visual model
- `06_Process Journey` / slide 7 — Staircase with side callouts
- `07_Roadmaps` / slide 2 — 3-phase ribbon with row bands
- `07_Roadmaps` / slide 4 — Multi-phase timeline with rows
- `07_Roadmaps` / slide 7 — Phase ribbon + 3 buckets + takeaway third
- `07_Roadmaps` / slide 8 — 3-phase chevron with 2-row deliverables
- `07_Roadmaps` / slide 11 — 7-step process with milestones
- `10_Org Charts Team Governance` / slide 2 — 5-branch org chart
- `10_Org Charts Team Governance` / slide 3 — 5-branch org chart variant
- `11_Visual Models` / slide 2 — 10-step curved sequence
- `11_Visual Models` / slide 3 — Cycle diagram with corner callouts
- `11_Visual Models` / slide 4 — Pentagon overlap + comparison table
- `11_Visual Models` / slide 5 — Half-circle 5-segment with leader lines
- `11_Visual Models` / slide 6 — 5-tier maturity pyramid (variant)
- `11_Visual Models` / slide 7 — 3D cube pyramid
- `11_Visual Models` / slide 8 — Wheel infographic with side callouts
- `11_Visual Models` / slide 9 — Hexagon infinity loop

**Comparison matrix** (17 templates)
- `01_Executive Summary` / slide 6 — Options comparison table with bottom strip
- `01_Executive Summary` / slide 9 — Comparison matrix with row labels
- `01_Executive Summary` / slide 10 — Harvey-ball comparison matrix
- `04_Competitive Analysis` / slide 4 — Channel adoption matrix
- `04_Competitive Analysis` / slide 6 — Competitor profile table with logos and harvey balls
- `04_Competitive Analysis` / slide 7 — Competitor revenue/margin comparison
- `04_Competitive Analysis` / slide 8 — 5-competitor matrix with row labels
- `04_Competitive Analysis` / slide 9 — Product feature matrix grouped by area
- `04_Competitive Analysis` / slide 10 — Feature presence matrix with check/X icons
- `04_Competitive Analysis` / slide 11 — Core vs additional features feature matrix
- `08_Structured Text` / slide 3 — Title/score/description comparison table
- `08_Structured Text` / slide 4 — 5-category × 5-dimension Harvey ball matrix
- `08_Structured Text` / slide 5 — 4-trend matrix with examples
- `08_Structured Text` / slide 6 — Hypothesis evaluation matrix
- `08_Structured Text` / slide 9 — Area-grouped feature comparison table
- `08_Structured Text` / slide 10 — Assessment status overview matrix
- `12_KPIs and Dashboards` / slide 3 — Strategy KPI dashboard table

**Framework (2x2 / quadrant)** (5 templates)
- `01_Executive Summary` / slide 7 — Two-column dashboard
- `03_Line Scatter Charts` / slide 3 — 2x2 quadrant matrix
- `04_Competitive Analysis` / slide 5 — Survey demographics dashboard
- `05_Frameworks` / slide 3 — Action list + impact-feasibility matrix
- `06_Process Journey` / slide 3 — 4-step cycle with arrows

**Roadmap / Timeline** (12 templates)
- `06_Process Journey` / slide 4 — 5-step ribbon process
- `06_Process Journey` / slide 6 — Wave progression visual model
- `07_Roadmaps` / slide 2 — 3-phase ribbon with row bands
- `07_Roadmaps` / slide 3 — 3-bucket phases with bottom takeaway
- `07_Roadmaps` / slide 4 — Multi-phase timeline with rows
- `07_Roadmaps` / slide 5 — 3-phase × 3-row band matrix
- `07_Roadmaps` / slide 6 — Gantt chart with phase grouping
- `07_Roadmaps` / slide 7 — Phase ribbon + 3 buckets + takeaway third
- `07_Roadmaps` / slide 8 — 3-phase chevron with 2-row deliverables
- `07_Roadmaps` / slide 9 — Workstream Gantt with milestones
- `07_Roadmaps` / slide 10 — Country launch Gantt with criteria panel
- `07_Roadmaps` / slide 11 — 7-step process with milestones

**Structured text** (10 templates)
- `01_Executive Summary` / slide 3 — Four-row labeled list
- `01_Executive Summary` / slide 4 — Section-headed bullet groups
- `04_Competitive Analysis` / slide 2 — Two-column rows with arrow connectors
- `04_Competitive Analysis` / slide 9 — Product feature matrix grouped by area
- `05_Frameworks` / slide 10 — SMART framework rows
- `08_Structured Text` / slide 2 — 5-row labeled list with colored labels
- `08_Structured Text` / slide 6 — Hypothesis evaluation matrix
- `08_Structured Text` / slide 7 — Parameter list with category dots
- `11_Visual Models` / slide 4 — Pentagon overlap + comparison table
- `12_KPIs and Dashboards` / slide 3 — Strategy KPI dashboard table

**Org chart** (7 templates)
- `08_Structured Text` / slide 8 — Personnel/role data table
- `10_Org Charts Team Governance` / slide 2 — 5-branch org chart
- `10_Org Charts Team Governance` / slide 3 — 5-branch org chart variant
- `10_Org Charts Team Governance` / slide 4 — Three parallel mini-trees
- `10_Org Charts Team Governance` / slide 5 — Org with bulleted children per branch
- `10_Org Charts Team Governance` / slide 6 — Standard 3-level org chart
- `10_Org Charts Team Governance` / slide 7 — Org chart with shared resource panel

**Quote / Pull-quote** — no exact matches in current library; compose fresh from chassis primitives following the recipe.

### By recipe variant

For layout families with multiple recipe variants in `visual-treatment-library.md`. If your slide's content matches one of these variants per the recipe's `when to use` criteria, start with templates here.

**Cover / Divider**
- *full-bleed dark* — slide 2 of 09_Cover Divider, slide 3 of 09_Cover Divider
- *split panel* — no exact matches; compose fresh
- *typographic numeral* — slide 4 of 09_Cover Divider

**Three-column parallel**
- *dark headers + light body* — slide 2 of 06_Process Journey
- *tinted cards* — slide 5 of 01_Executive Summary, slide 8 of 01_Executive Summary
- *rule + label only* — no exact matches; compose fresh
- *two-tier cards* — no exact matches; compose fresh
- *progressive emphasis* — slide 5 of 01_Executive Summary, slide 2 of 06_Process Journey

**Visual Model**
- *dark mode centerpiece* — no exact matches; compose fresh
- *tinted element boxes* — slide 5 of 11_Visual Models
- *white with accent rules* — slide 7 of 05_Frameworks

**Comparison matrix**
- *dark header row* — slide 9 of 01_Executive Summary
- *circle-letter columns* — slide 9 of 01_Executive Summary
- *harvey balls / ratings* — slide 10 of 01_Executive Summary, slide 6 of 04_Competitive Analysis, slide 8 of 04_Competitive Analysis, slide 4 of 08_Structured Text, slide 6 of 08_Structured Text

**Framework (2x2 / quadrant)** — no variants tagged from current library descriptions. Compose fresh from chassis primitives.

**Roadmap / Timeline**
- *graduated phase bars* — no exact matches; compose fresh
- *phase + gate markers* — slide 11 of 07_Roadmaps
- *swimlane* — no exact matches; compose fresh

**Org chart** — no variants tagged from current library descriptions. Compose fresh from chassis primitives.

### Notes for the model using this navigation

- **Multi-classification is intentional.** A slide that is both a comparison matrix AND uses chart elements appears under both. Read the per-slide entry to disambiguate.
- **"No exact matches"** for a variant doesn't mean the variant is wrong for your slide — it means the current 89-template library doesn't include it. Compose fresh from chassis primitives following the recipe in `visual-treatment-library.md`.
- **Variant tagging is conservative.** Fewer slides are tagged with variants than fall under each family because variant detection requires the `Shows:` field to use specific vocabulary. A template that fits a variant but doesn't use the keyword will be missing here. When in doubt, scan the family list and check the per-slide entries.

_This navigation header is auto-generated from the per-slide entries below. 0 of 89 templates remain unclassified — see the per-slide entries below._

---
## 01_Executive Summary.pptx

### slide 2 — Slideworks educational guide
- **Shows:** dual-section composition with "Executive summary / Slideworks guide" header on left and three What/Why/How explanation panels on right with bulleted instructions
- **Page-type:** none — educational reference, not a template
- **Reach for when:** never — this is documentation explaining how to build executive summaries
- **Avoid when:** always exclude from copy candidates

### slide 3 — Four-row labeled list
- **Shows:** 4 vertical rows, each with dark-fill left label box (Vision / Strategic objective / Solution / Sponsor) + paragraph text right, dashed dividers between rows
- **Page-type:** Executive Summary, Insight/Finding
- **Reach for when:** structured executive summary with 3-5 named sections; one paragraph per section; no quantitative content needed
- **Avoid when:** content needs charts/tables; ≥6 sections (gets crowded); sections aren't parallel in nature

### slide 4 — Section-headed bullet groups
- **Shows:** single-column structured text with 4 colored section headers (Business need / Suggested solution / Path forward / Next steps), each followed by 3 indented bullets
- **Page-type:** Executive Summary, Recommendation
- **Reach for when:** classic SCQA-style summary with 3-4 sections; each section has 2-4 supporting bullets; clean text-only delivery
- **Avoid when:** sections have unequal weight (use labeled-row-list); content needs visualization; single-section content (overkill)

### slide 5 — Three-column problem/solution/recommendation
- **Shows:** 3 vertical columns with progressive emphasis (dashed border / gray fill / dark fill), Problem on left, Solution in middle with numbered options, Recommendation on right with detailed bullets
- **Page-type:** Executive Summary, Recommendation
- **Reach for when:** SCQA structure where the recommendation is the headline; want visual hierarchy directing eye to the answer; problem is short, recommendation is detailed
- **Avoid when:** all 3 columns have equal weight (use multi-bucket); content fits in one column; recommendation isn't the primary message

### slide 6 — Options comparison table with bottom strip
- **Shows:** 4-column table (Options / Details / Benefits / NPV-ROI) with 3 option rows, bottom recommendation strip in gray
- **Page-type:** Recommendation, Comparison
- **Reach for when:** comparing 3-4 options across 3-5 evaluation criteria; need to show recommendation at bottom; quantitative + qualitative cells
- **Avoid when:** ≥5 options (too narrow); criteria aren't parallel; no clear recommendation to bookend

### slide 7 — Two-column dashboard
- **Shows:** dual-section with left = project background card + 2x2 setup grid (costs/sponsor/FTEs/manager), right = bar chart card + 2 dark NPV/ROI cards
- **Page-type:** Executive Summary, Status Update
- **Reach for when:** project one-pager with both narrative context and numerical outcomes; need to show ROI/NPV prominently; mixed cards work better than tables
- **Avoid when:** content is single-narrative (use slide 4); no quantitative outcome to highlight; either side is empty

### slide 8 — Four numbered buckets
- **Shows:** 4 multi-bucket cards with numbered circle headers (1-4), bucket title (Problem/Solution/Outcomes/Strategic rationale), paragraph body, gray fill
- **Page-type:** Executive Summary, Insight/Finding
- **Reach for when:** four-step framework summary; each step is parallel in weight; equal paragraph length per bucket
- **Avoid when:** ≤3 or ≥5 sections; sections need different visual emphasis; quantitative content

### slide 9 — Comparison matrix with row labels
- **Shows:** matrix layout with dark left labels (Main approach + 4 dimensions), 3 option columns (A/B/C) with dashed-border cells, circle-letter column headers
- **Page-type:** Comparison, Recommendation
- **Reach for when:** comparing 3 options across 4-5 dimensions; cells contain short text descriptions; need parallel structure across columns
- **Avoid when:** ≤2 options (use dual-section); >5 options (use comparison-table without dashed borders); cells need icons/charts (use slide 10)

### slide 10 — Harvey-ball comparison matrix
- **Shows:** matrix with row labels (4 dimensions), 3 option columns each split into Short-term/Long-term sub-columns, harvey ball cells, "Worse ↔ Better" legend top-right, yellow box highlight on recommended option
- **Page-type:** Recommendation, Comparison
- **Reach for when:** option comparison where the answer is qualitative (better/worse) not quantitative; multi-time-horizon dimension matters; want to visually highlight the recommendation
- **Avoid when:** quantitative comparison (use chart cells); single time horizon; no clear recommendation to box

---

## 02_Bar Charts.pptx

### slide 2 — Stacked column with growth callout + comments panel
- **Shows:** stacked column chart, historical (dark) + forecasted (light) bars, gray "Forecasted data" overlay, +N% growth annotation, right comments panel with bullets, dashed vertical divider
- **Page-type:** Insight/Finding, Data Deep-Dive
- **Reach for when:** past-trend-to-forecast story; one growth callout; ≤4 observation bullets fit panel
- **Avoid when:** no forecast; multiple growth callouts (use slide 4); story is comparison not time

### slide 3 — Full-width 100% stacked column
- **Shows:** 100% stacked column, two series, value labels per segment, total `xx` above each bar, no panel
- **Page-type:** Comparison, Data Deep-Dive
- **Reach for when:** part-of-whole composition over time; two-series proportional split; story is the proportion trend
- **Avoid when:** absolute values matter (use slide 2); >2 series (use slide 7); ≤4 periods

### slide 4 — Stacked column with multiple growth callouts + YoY bubbles
- **Shows:** stacked column with historical + forecast, multiple growth-rate annotations (+14%, +73%, +17%), YoY bubbles below x-axis, right comments panel
- **Page-type:** Insight/Finding, Data Deep-Dive
- **Reach for when:** trend + forecast with multiple growth callouts; need both per-period values AND YoY change visible
- **Avoid when:** single growth callout fits (use slide 2); no forecast; >12 periods

### slide 5 — Three side-by-side clustered columns
- **Shows:** 3 clustered column charts side-by-side, each with own description strip, growth-rate tables under each chart
- **Page-type:** Comparison, Data Deep-Dive
- **Reach for when:** same metric across 3 segments/regions; each segment has own growth story; need YoY tables per segment
- **Avoid when:** ≤2 segments (use dual-section); >3 segments; takeaway needs side panel

### slide 6 — Horizontal bar with average benchmark
- **Shows:** horizontal bar chart, ~10 ranked categories, orange dashed average line (Ø), right comments panel
- **Page-type:** Comparison, Insight/Finding
- **Reach for when:** ranking entities by single metric; compare each to benchmark/average; ≤10 categories
- **Avoid when:** time-series story; >12 categories; no benchmark

### slide 7 — 100% stacked column with totals column
- **Shows:** 100% stacked column with 5 series, time periods on x-axis + "Total" column on right separated by dashed line, right comments panel
- **Page-type:** Data Deep-Dive, Comparison
- **Reach for when:** part-of-whole with ≥3 series; need segment trends + totals summary side-by-side
- **Avoid when:** 2 series (slide 3 cleaner); no total/summary needed; story is absolute values

### slide 8 — Channel landscape (table + chart)
- **Shows:** dual-section. Left: 4-row table with channel labels and descriptions, group brackets. Right: 100% stacked column with 4 channels across 3 periods
- **Page-type:** Comparison, Data Deep-Dive
- **Reach for when:** explaining channel/segment landscape with mixed qualitative + quantitative; need both side-by-side
- **Avoid when:** quantitative-only; ≤2 channels; table has only 1-2 rows

### slide 9 — Stacked column small multiples with cumulative top-N
- **Shows:** 4 vertically-stacked column charts as small multiples, cumulative percentage callouts (74%, 70%, 63%, 55%), right legend with 5-row category breakdown, right comments panel
- **Page-type:** Comparison, Data Deep-Dive
- **Reach for when:** familiarity/awareness/NPS-style stacks across 4 segments; highlight cumulative top-N
- **Avoid when:** ≤2 segments; categories differ across segments; story isn't cumulative top-N

### slide 10 — Horizontal bar with top-N highlight
- **Shows:** horizontal bar, 10 metrics ranked descending, top 3 highlighted in lighter accent, right comments panel
- **Page-type:** Insight/Finding, Comparison
- **Reach for when:** ranking drivers/factors/KPIs; visual top-N callout; ≤10 metrics
- **Avoid when:** comparing entities not metrics (slide 6 closer); time-series; no clear top group

### slide 11 — Combo chart (column + line)
- **Shows:** combo chart — clustered column + line overlay, two bar series + one line series, value labels everywhere, full-width no panel
- **Page-type:** Data Deep-Dive, Comparison
- **Reach for when:** two related metrics with different scales (volume + price); show correlation; ≤8 periods
- **Avoid when:** single metric (use slide 2); 3+ comparable series; line metric unrelated to bars

---

## 03_Line Scatter Charts.pptx

### slide 2 — Scatter plot with positioning bands
- **Shows:** scatter plot with company labeled in highlight color, competitors as dots, gray gradient bands behind data, right takeaways panel with bullets, dashed vertical divider
- **Page-type:** Comparison, Competitive & Market Analysis
- **Reach for when:** competitive positioning across two dimensions; one company is the focus; need brief takeaway bullets
- **Avoid when:** more than ~10 competitors (clutter); story is single-dimension ranking (use bar chart); no clear positioning narrative

### slide 3 — 2x2 quadrant matrix
- **Shows:** scatter with explicit quadrant lines and quadrant labels (Challengers/Market leaders/Laggards/Incumbents), highlighted company, right takeaways panel
- **Page-type:** Competitive & Market Analysis, Comparison
- **Reach for when:** classic 2x2 strategic positioning; quadrants are the headline; want company in a specific quadrant
- **Avoid when:** dimensions don't have clear high/low boundaries; no quadrant narrative needed (slide 2 simpler)

### slide 4 — Buying-criteria comparison line chart
- **Shows:** vertical strip chart comparing company vs peer group across ranked buying criteria, light/dark dot connectors, right gray panel with main findings
- **Page-type:** Competitive & Market Analysis, Comparison
- **Reach for when:** comparing one entity to peer group across N criteria; show divergence/convergence; criteria have implicit ranking
- **Avoid when:** comparing groups not entities; no peer comparison; criteria aren't ranked

### slide 5 — Scatter with quadrant labels and grouping
- **Shows:** scatter with axis labels (e.g., price/brand), competitors in dashed-bordered colored boxes, company highlighted in solid box, right comments panel
- **Page-type:** Competitive & Market Analysis, Comparison
- **Reach for when:** segment-level positioning; competitors group into clusters; need to call out segment groupings visually
- **Avoid when:** no natural clusters; all competitors are independent points (use slide 2); ≤3 competitors

### slide 6 — Bubble chart full-width
- **Shows:** bubble chart with 3 group colors, product labels next to bubbles, dashed diagonal trend line, full-width no panel
- **Page-type:** Data Deep-Dive, Competitive & Market Analysis
- **Reach for when:** three dimensions to show (x, y, size); need diagonal trend reference; ≤12 bubbles
- **Avoid when:** ≤2 dimensions (use scatter); takeaway needs side panel; bubble sizes don't carry meaning

### slide 7 — Bubble chart with comments panel
- **Shows:** bubble chart with 3 series colors, competitor labels, x/y axes labeled, right comments panel, description strip above chart
- **Page-type:** Competitive & Market Analysis, Data Deep-Dive
- **Reach for when:** competitive bubble positioning with takeaway bullets needed; ≤10 competitors; three dimensions
- **Avoid when:** 2 dimensions (use scatter); no takeaway bullets needed (slide 6 cleaner)

---

## 04_Competitive Analysis.pptx

### slide 2 — Two-column rows with arrow connectors
- **Shows:** 4 rows, each with left card (icon + trend label) → blue arrow connector → right cell with implication bullets, dark header bands "Market trends" / "Implications"
- **Page-type:** Competitive & Market Analysis, Insight/Finding
- **Reach for when:** trend → implication pairs; 3-5 trends; want explicit causal connector visual
- **Avoid when:** trends don't map 1-to-1 to implications; ≥6 trends; either side has multi-paragraph content

### slide 3 — Four image-headed buckets
- **Shows:** 4 multi-bucket columns with stock photo headers, trend label below each image, 2-3 line description below label
- **Page-type:** Competitive & Market Analysis, Conceptual — Divider/Transition
- **Reach for when:** trends/themes that benefit from imagery; 4 parallel items; ≤4 lines text per bucket
- **Avoid when:** no relevant imagery available; data-driven content (use chart); ≥5 buckets (too crowded)

### slide 4 — Channel adoption matrix
- **Shows:** 6-column comparison matrix with channel icon + label rows, "Step 1/2/3/4" chevron column headers grouping Current/Prospective sub-columns, percentage cells with blue bubbles for highlights
- **Page-type:** Comparison, Competitive & Market Analysis
- **Reach for when:** journey-stage data across multiple channels with current vs target/prospective; want to bubble-highlight specific values
- **Avoid when:** single time-state (use simpler matrix); no journey/sequence; ≥7 channels (rows get cramped)

### slide 5 — Survey demographics dashboard
- **Shows:** dual-section. Left: respondent type bar + 2 metric breakdown bars + age pyramid. Right: 4 small bar charts (2x2 grid) showing characteristic distributions
- **Page-type:** Data Deep-Dive, Competitive & Market Analysis
- **Reach for when:** survey methodology page with respondent demographics + characteristics; multi-metric overview without one dominant chart
- **Avoid when:** single metric is the story; need to highlight insight not method; would compress charts too small

### slide 6 — Competitor profile table with logos and harvey balls
- **Shows:** 5-column comparison table — competitor logo cell / description bullets / market share % / strategy harvey ball / overall assessment text — 7 competitor rows with dashed dividers
- **Page-type:** Competitive & Market Analysis, Comparison
- **Reach for when:** competitor landscape one-pager with mixed qualitative + quantitative + visual cells; ≤8 competitors
- **Avoid when:** purely quantitative (use bar ranking); no harvey-ball-able dimension; ≥10 competitors (split deck)

### slide 7 — Competitor revenue/margin comparison
- **Shows:** 4-column comparison table — competitor logo / description bullets / revenue+profit bar chart inline / CAGR % — 7 competitor rows
- **Page-type:** Competitive & Market Analysis, Data Deep-Dive
- **Reach for when:** competitor financial comparison with inline mini-bars; want both absolute values and growth rate per competitor
- **Avoid when:** no financials available; ≥9 competitors; bar chart cells would be too narrow to read

### slide 8 — 5-competitor matrix with row labels
- **Shows:** matrix transposed from slide 6 — row labels left (Revenue/Market share/Strategy/Strengths/Weaknesses/Perceived threat), 5 competitor columns across, harvey ball row at bottom
- **Page-type:** Competitive & Market Analysis, Comparison
- **Reach for when:** ≤6 competitors deep-dive comparison across 5-7 dimensions; dimensions are the row primary structure
- **Avoid when:** ≥7 competitors (use slide 6 vertical orientation); ≤3 dimensions (overkill)

### slide 9 — Product feature matrix grouped by area
- **Shows:** comparison table with row-grouped left labels (Area 1/2/3 each spanning 4 rows), 4 product columns with header cards, repeating "Lorem ipsum" description cells
- **Page-type:** Comparison, Competitive & Market Analysis
- **Reach for when:** feature comparison grouped by category area; ≥3 areas with 3-4 features each; products being compared on text descriptions
- **Avoid when:** features aren't naturally grouped (use flat matrix); ≤2 products (use side-by-side)

### slide 10 — Feature presence matrix with check/X icons
- **Shows:** 6-column comparison table, product features as columns (header band), competitor rows with dashed-border logo cells, blue check / red X / blue circle status icons in cells
- **Page-type:** Competitive & Market Analysis, Comparison
- **Reach for when:** binary feature comparison (has/doesn't have) across competitors; want visual scan-ability
- **Avoid when:** features are continuous not binary (use harvey balls); ≥10 features (rows get crowded); needs detail beyond presence

### slide 11 — Core vs additional features feature matrix
- **Shows:** wide comparison table with grouped column headers (Core vs Additional features), 13 feature columns total, 7 competitor rows with row banding, check/parenthesis-check status icons
- **Page-type:** Competitive & Market Analysis, Comparison
- **Reach for when:** feature breadth analysis with core vs differentiator distinction; ≥10 features; need column-group visual emphasis
- **Avoid when:** features don't split into groups (use slide 10); ≤6 features

---

## 05_Frameworks.pptx

### slide 2 — Fishbone diagram
- **Shows:** classic Ishikawa fishbone — left tail + right head arrow, 6 category bones (3 above, 3 below), text labels on each bone branch
- **Page-type:** Conceptual — Analytical Framework, Visual Model
- **Reach for when:** root-cause analysis; effect on right + 4-6 categories of causes; bullet-level detail per category
- **Avoid when:** not a cause-effect story; ≥8 categories; insufficient detail to fill the bones

### slide 3 — Action list + impact-feasibility matrix
- **Shows:** dual-section — left: numbered action list (7 items), right: 2x2 matrix (Easy/Hard × Long-term/Short-term) with colored dots positioned in matrix
- **Page-type:** Recommendation, Conceptual — Analytical Framework
- **Reach for when:** prioritization story with explicit list + 2x2 plot; numbered list connects to plot points; recommendation emerges from quadrant
- **Avoid when:** ≥10 actions; no natural 2x2 framing; list is qualitative descriptions not actions

### slide 4 — Strategy house framework
- **Shows:** house metaphor — purpose roof spanning top, 3 strategic objective beams, 9 initiative columns, 3 enabler foundation rows below
- **Page-type:** Conceptual — Analytical Framework, Visual Model
- **Reach for when:** strategic plan one-pager with vision → objectives → initiatives → enablers hierarchy
- **Avoid when:** ≤2 objectives (overkill); no clear foundation/enabler distinction; strategy is non-hierarchical

### slide 5 — 4-step cycle visual model
- **Shows:** 4-step purple cycle with central icons, "Text Here" on each arrow segment, 4 corner descriptions ("Your Text Here" + paragraph)
- **Page-type:** Visual Model, Process/How
- **Reach for when:** repeating 4-step cycle (PDCA-style); each step has equal weight; corners need brief explanation
- **Avoid when:** linear process (use process-flow); ≤3 or ≥5 steps; sequential not cyclical

### slide 6 — 5-tier maturity pyramid
- **Shows:** ascending 5-tier pyramid (Initial/Managed/Defined/Quantitatively Managed/Optimizing), level numbers right of each tier, paragraph text left of each tier
- **Page-type:** Visual Model, Conceptual — Analytical Framework
- **Reach for when:** maturity model assessment; 4-5 levels each with description; CMMI-style tiered progression
- **Avoid when:** ≤3 levels (use multi-bucket); no clear progression; levels aren't hierarchical

### slide 7 — Fishbone (variant of slide 2)
- **Shows:** same fishbone structure as slide 2 but unbranded styling, 6 categories
- **Page-type:** Conceptual — Analytical Framework, Visual Model
- **Reach for when:** same as slide 2 but want cleaner styling
- **Avoid when:** same as slide 2

### slide 8 — Range bars by area grouping
- **Shows:** 8 dimension rows with range bars (low to high arrows), grouped by 3 areas (Area 1 light gray / Area 2 light blue / Area 3 dark) on left, "Key dimensions" header
- **Page-type:** Comparison, Conceptual — Analytical Framework
- **Reach for when:** spectrum-of-positions analysis across grouped dimensions; want visual range not point values
- **Avoid when:** point values matter (use bar chart); no group structure; ≤4 dimensions

### slide 9 — Issue tree
- **Shows:** hierarchical tree — main issue (key question) on left, 2 issues, 5 sub-issues, 13 sub-sub-issues, dark-fill boxes at left, blue boxes middle, light blue right
- **Page-type:** Conceptual — Analytical Framework, Visual Model
- **Reach for when:** MECE issue decomposition; 2-3 levels of "why" branching; structured problem-solving frame
- **Avoid when:** ≤2 levels (overkill); not MECE; tree gets >4 deep (split into multiple slides)

### slide 10 — SMART framework rows
- **Shows:** 5 row-labeled list — colored letter boxes (S/M/A/R/T) with descriptors below, Questions column with bullets, Answers column placeholder, columns labeled across top
- **Page-type:** Conceptual — Analytical Framework, Recommendation
- **Reach for when:** acronym-based framework (SMART, STAR, etc.); each letter has questions; user fills answers
- **Avoid when:** not an acronym framework; ≥6 rows (acronym usually maxes at 5)

### slide 11 — Porter's value chain
- **Shows:** Porter value chain — top row 5 chevron primary activities (Inbound/Operations/Outbound/Marketing/Services) with bullets below, 4 horizontal arrow support activity rows below
- **Page-type:** Conceptual — Analytical Framework, Visual Model
- **Reach for when:** value chain analysis; 4-6 primary activities; 3-5 support functions
- **Avoid when:** not a value chain story; activities are non-sequential; no support distinction

---

## 06_Process Journey.pptx

### slide 2 — Three-state progression
- **Shows:** 3 multi-bucket columns with progressive emphasis (gray/dark/blue), header bands "Where we were/Where we are/Where we aspire to be", main description + 5 bullets each
- **Page-type:** Status Update, Process/How
- **Reach for when:** as-is/to-be transformation with explicit current state; 3 time points; equal detail each
- **Avoid when:** ≥4 states; no clear current vs future distinction; quantitative data needed

### slide 3 — 4-step cycle with arrows
- **Shows:** 2x2 grid of dark circles with icons + step labels, blue arrows connecting clockwise (1→2→3→4→1), text descriptions outside corners
- **Page-type:** Visual Model, Process/How
- **Reach for when:** 4-step continuous cycle; explicit arrow rotation matters; minimal per-step text
- **Avoid when:** linear process; ≥5 or ≤3 steps; need per-step bullet detail (use slide 2 of 05)

### slide 4 — 5-step ribbon process
- **Shows:** 5-step purple gradient ribbon (chevron-styled), step icons on each, Title + bullets card below each step
- **Page-type:** Process/How, Roadmap & Timeline
- **Reach for when:** 5-step linear process; equal weight per step; per-step bullets needed
- **Avoid when:** ≥7 steps (use Gantt or split); steps have unequal weight; cyclical not linear

### slide 5 — 6-step chevron with 2-row bands
- **Shows:** 6-step chevron header band (Equipment providers → Service providers), top row = bullets describing each, bottom row = "Examples of disruptions" bullets, separated by horizontal divider with arrow icon
- **Page-type:** Process/How, Competitive & Market Analysis
- **Reach for when:** value chain or industry steps with parallel content types per step (definition + example); ≥5 steps
- **Avoid when:** ≤4 steps (too sparse); only one content type per step (use slide 4)

### slide 6 — Wave progression visual model
- **Shows:** 4 ascending tiers with location-pin icons on top, wave numbers (Pilot/Wave 1/Wave 2/Wave n), clustering dimensions placeholder cards below
- **Page-type:** Roadmap & Timeline, Visual Model
- **Reach for when:** rollout/scaling story with discrete waves; ascending progression; cluster details per wave
- **Avoid when:** linear non-wave process; specific dates matter (use Gantt); ≤3 waves

### slide 7 — Staircase with side callouts
- **Shows:** isometric staircase with 5 numbered steps (01-05), keyword + paragraph callouts on alternating sides, ascending purple gradient
- **Page-type:** Visual Model, Process/How
- **Reach for when:** ascending milestone story; 5 milestones; want visual sense of building up
- **Avoid when:** ≥7 milestones; no escalation theme; need precise timing (use Gantt)

---

## 07_Roadmaps.pptx

### slide 2 — 3-phase ribbon with row bands
- **Shows:** 3 chevron phase headers (Phase 1/1/3), 3 row-bands (Activities/Results/Duration-Involvement), purple gradient styling
- **Page-type:** Roadmap & Timeline, Process/How
- **Reach for when:** 3-phase project plan with parallel content types per phase; activities + outcomes + duration matter
- **Avoid when:** ≥5 phases; only one content type per phase; specific dates needed (use Gantt)

### slide 3 — 3-bucket phases with bottom takeaway
- **Shows:** 3 multi-bucket columns with icon-headed boxes (PHASE 1/2/3) and Month placeholders, 5 bullets each, bottom takeaway strip
- **Page-type:** Roadmap & Timeline, Process/How
- **Reach for when:** 3-phase plan with bullet detail; want bottom-line summary; equal-weight phases
- **Avoid when:** ≥5 phases; row bands needed (use slide 2); per-phase distinct visual treatment

### slide 4 — Multi-phase timeline with rows
- **Shows:** 6-segment phase chevron timeline header, 2-row content bands (What/Outcome) below, week-level granularity
- **Page-type:** Roadmap & Timeline, Process/How
- **Reach for when:** project plan with weekly breakdown; multiple phases; What+Outcome per phase
- **Avoid when:** ≤3 phases (use slide 2); needs daily granularity (use Gantt); no week structure

### slide 5 — 3-phase × 3-row band matrix
- **Shows:** 3 phase columns with header bands + duration labels above, 3 row bands (Activities/Outcomes/Required Contribution), all bullet content
- **Page-type:** Roadmap & Timeline, Process/How
- **Reach for when:** detailed 3-phase plan with multiple content streams; each phase has 3 distinct content types
- **Avoid when:** ≥5 phases; only 1-2 content streams; non-sequential

### slide 6 — Gantt chart with phase grouping
- **Shows:** 12-week timeline header, 3 phase row groups with task bars, milestone diamonds, phase legend
- **Page-type:** Roadmap & Timeline
- **Reach for when:** project plan with task-level detail; ≤12 task rows; up to 12 weeks horizon
- **Avoid when:** strategic narrative (use chevron); ≥15 tasks; >6 month horizon

### slide 7 — Phase ribbon + 3 buckets + takeaway third
- **Shows:** 3-phase chevron ribbon header, 3 multi-bucket week-cards below, right takeaway-third panel with numbered outcomes
- **Page-type:** Roadmap & Timeline, Recommendation
- **Reach for when:** project plan with phase breakdown + outcome takeaway; 3 phases of weekly work
- **Avoid when:** ≥5 phases; no clear outcome list; needs row bands instead

### slide 8 — 3-phase chevron with 2-row deliverables
- **Shows:** 3 chevron phases (Explore/Detail design/Build MVP), purple gradient, 2 row-bands (Deliverables/People), icons per row
- **Page-type:** Roadmap & Timeline, Status Update
- **Reach for when:** 3-phase rollout with deliverables + team focus; equal-weight phases
- **Avoid when:** ≥5 phases; only deliverables (use slide 3)

### slide 9 — Workstream Gantt with milestones
- **Shows:** 15-week timeline header, 7 workstream rows with task bars, milestone callouts below grouped under stage-gate labels
- **Page-type:** Roadmap & Timeline
- **Reach for when:** detailed program plan with multiple workstreams; explicit stage-gates/milestones
- **Avoid when:** single workstream (use slide 6); no milestones; <8 weeks (use phase chevron)

### slide 10 — Country launch Gantt with criteria panel
- **Shows:** dual-section. Left: Gantt with countries as rows, A/B/C option groupings. Right: gray takeaway panel with numbered selection criteria
- **Page-type:** Roadmap & Timeline, Recommendation
- **Reach for when:** rollout plan across geographies + selection rationale; multi-option staging
- **Avoid when:** no rationale to show; single option (use plain Gantt); ≤3 markets

### slide 11 — 7-step process with milestones
- **Shows:** 7-step chevron header (months as labels), milestone diamond markers, content cards below each step with bullets
- **Page-type:** Roadmap & Timeline, Process/How
- **Reach for when:** governance/decision cadence over 6+ months; meetings as milestones; per-meeting agenda
- **Avoid when:** ≤4 milestones; no governance structure; daily/weekly cadence needed

---

## 08_Structured Text.pptx

### slide 2 — 5-row labeled list with colored labels
- **Shows:** 5 rows, each with colored gradient title block left + paragraph right, icons on labels, dashed dividers between rows
- **Page-type:** Insight/Finding, Conceptual — Analytical Framework
- **Reach for when:** 5 named items each with paragraph explanation; want color-coded categorization; equal-weight items
- **Avoid when:** ≥7 rows; quantitative content (use chart); items aren't parallel

### slide 3 — Title/score/description comparison table
- **Shows:** 5-row × 3-column comparison table (Title/Score/Description), colored category labels, gray score cells, bullet description cells, 1-5 scale legend bottom
- **Page-type:** Comparison, Recommendation
- **Reach for when:** scorecard-style assessment; 5 categories scored on common scale; brief rationale per category
- **Avoid when:** continuous scoring (use chart); ≥7 categories; no comparable scale

### slide 4 — 5-category × 5-dimension Harvey ball matrix
- **Shows:** 5-row × 5-column comparison table with category labels left, dimension headers top, Harvey ball cells, bottom takeaway strip
- **Page-type:** Comparison, Recommendation
- **Reach for when:** category × dimension qualitative scoring; want visual scan; bottom-line takeaway needed
- **Avoid when:** quantitative cells; ≥7 dimensions; no overall takeaway

### slide 5 — 4-trend matrix with examples
- **Shows:** 4-row × 3-column comparison table (Trend label / Description bullets / Examples bullets), dashed dividers
- **Page-type:** Competitive & Market Analysis, Insight/Finding
- **Reach for when:** trend deep-dive with description + concrete examples per trend; 3-5 trends
- **Avoid when:** trends are quantitative (use chart); no examples to show; ≥7 trends

### slide 6 — Hypothesis evaluation matrix
- **Shows:** 3-row-grouped × 4-column matrix (Area / Hypothesis / Confirmation / Certainty), area labels span sub-rows, check/X icons + Harvey balls in cells
- **Page-type:** Insight/Finding, Conceptual — Analytical Framework
- **Reach for when:** structured hypothesis testing log; ≤3 areas with 2-4 hypotheses each; binary + qualitative confidence
- **Avoid when:** quantitative hypothesis testing; ≥4 areas; no confirmation/certainty distinction

### slide 7 — Parameter list with category dots
- **Shows:** 7-row labeled-row-list, dark/blue colored circles with letter labels (A-G), parameter labels in colored bands, description cells, category legend top right
- **Page-type:** Conceptual — Analytical Framework, Recommendation
- **Reach for when:** action/initiative list grouped into 2-3 categories visually; ≤8 items; brief description per item
- **Avoid when:** ≥10 items; flat list (use slide 5); quantitative

### slide 8 — Personnel/role data table
- **Shows:** 12-row × 6-column data table (ID/Name/Role/Level/Location/Email), level cells highlighted in purple gradient
- **Page-type:** Org Chart Team & Governance, Status Update
- **Reach for when:** team/role roster; flat data table; ≤15 rows; specific cells need emphasis
- **Avoid when:** ≥20 rows (split slide); hierarchical structure (use org chart); no cells need emphasis

### slide 9 — Area-grouped feature comparison table
- **Shows:** 3-area row groups × 4-product columns, "Lorem ipsum" headers in purple, repeated text cells with check icons
- **Page-type:** Comparison
- **Reach for when:** product comparison with features grouped by area; ≥3 areas; ≤5 products
- **Avoid when:** flat feature list; ≥7 products

### slide 10 — Assessment status overview matrix
- **Shows:** 11-row × 6-column comparison table, 3 area row groups, parameter cells, unit/data point cells with RAG status squares (green/light green/gray/red), 4-grade legend
- **Page-type:** Status Update, Comparison
- **Reach for when:** project/portfolio status RAG dashboard with grouped parameters; ≥3 areas
- **Avoid when:** binary status (use slide 4); ≤5 parameters (overkill); no area grouping

---

## 09_Cover Divider.pptx

### slide 2 — Dark-mode appendix divider
- **Shows:** full-bleed dark navy background, "Appendix A" small label + 2-line title white text, no other content
- **Page-type:** Conceptual — Divider/Transition
- **Reach for when:** appendix or major section break; want dark visual reset; brief title only
- **Avoid when:** has content beyond title; need section to feel light/airy

### slide 3 — Gradient agenda divider
- **Shows:** full-bleed purple gradient, large white centered title "Agenda Slides", no other content
- **Page-type:** Conceptual — Divider/Transition
- **Reach for when:** agenda or chapter title page; brand-styled deck; centered title aesthetic
- **Avoid when:** unbranded deck; need numbered sections (use slide 4); subtitle needed

### slide 4 — Hero numeral section divider
- **Shows:** white background with horizontal rules top and bottom, section title left, large numeral (e.g., "02") right
- **Page-type:** Conceptual — Divider/Transition
- **Reach for when:** numbered section break; classic MBB section opener; clean white aesthetic
- **Avoid when:** sections aren't numbered; want full-bleed visual

### slide 5 — Numbered table of contents
- **Shows:** "Content" header left, 9 numbered list items right with dark circle numbers, vertically centered
- **Page-type:** Conceptual — Divider/Transition
- **Reach for when:** agenda/TOC at deck start; ≤10 sections; want simple numbered list
- **Avoid when:** ≥12 sections (split or use 2 columns); need section pages numbers

---

## 10_Org Charts Team Governance.pptx

### slide 2 — 5-branch org chart
- **Shows:** single root node top + 5 branch nodes below + 2-3 leaf nodes per branch, gradient purple coloring of branches, connector lines
- **Page-type:** Org Chart Team & Governance, Visual Model
- **Reach for when:** 2-level org with one root and 4-6 branches; ≤4 leaves per branch
- **Avoid when:** ≥3 levels (use slide 6); no clear root; flat team (use slide 8 of 08 for roster)

### slide 3 — 5-branch org chart variant
- **Shows:** same structure as slide 2 with slight styling variant
- **Page-type:** Org Chart Team & Governance, Visual Model
- **Reach for when:** same as slide 2
- **Avoid when:** same as slide 2

### slide 4 — Three parallel mini-trees
- **Shows:** 3 small trees side-by-side, each with circle-icon root + 3-4 children, paragraph header text above
- **Page-type:** Org Chart Team & Governance, Conceptual — Analytical Framework
- **Reach for when:** comparing 3 alternative org structures; small trees fit horizontally; lightweight comparison
- **Avoid when:** single org (use slide 2); ≥4 alternatives; trees too deep to fit

### slide 5 — Org with bulleted children per branch
- **Shows:** root node top, 5 colored branch nodes (gradient purple), bulleted lists of child items below each branch (not boxes — indented bullets)
- **Page-type:** Org Chart Team & Governance, Conceptual — Analytical Framework
- **Reach for when:** branch is a category, leaves are list items not roles; want compact representation; ≤9 items per branch
- **Avoid when:** leaves are real positions/roles (use slide 6); branches need balance

### slide 6 — Standard 3-level org chart
- **Shows:** 1 root + 3 second-level + ~4 third-level per branch, name + designation in each box, gradient purple boxes, connector lines
- **Page-type:** Org Chart Team & Governance
- **Reach for when:** team org chart with names + titles; 3 levels deep; ≤25 total positions
- **Avoid when:** ≥4 levels; ≥30 positions (split by branch); roles only (no names)

### slide 7 — Org chart with shared resource panel
- **Shows:** dual-section. Left: 2-level org (head + 3 child boxes + 2 sub-boxes). Right: takeaway-third panel listing required + optional shared resources with role icons
- **Page-type:** Org Chart Team & Governance, Recommendation
- **Reach for when:** project team org with explicit shared/external resources; want to distinguish core vs shared
- **Avoid when:** no shared resources; flat team; ≥3-level core team

---

## 11_Visual Models.pptx

### slide 2 — 10-step curved sequence
- **Shows:** 10 numbered circles arranged in ascending S-curve, each circle has a brief label, gradient purple fill darker at top
- **Page-type:** Visual Model, Process/How
- **Reach for when:** sequential journey of ≥7 steps; want visual sense of progression; brief step labels
- **Avoid when:** ≤6 steps (use chevron flow); steps need detail (use roadmap); cyclical

### slide 3 — Cycle diagram with corner callouts
- **Shows:** 4 central icon circles connected by curved arrows forming cycle, 4 "Your Text Here" + paragraph callouts at corners, gradient purple
- **Page-type:** Visual Model, Process/How
- **Reach for when:** 4-element repeating cycle; equal weight elements; brief description per element
- **Avoid when:** linear process (use slide 2); ≤3 or ≥5 elements

### slide 4 — Pentagon overlap + comparison table
- **Shows:** dual-section. Left: 5-segment overlapping pentagon with topic labels. Right: 8-row labeled-row-list with topic/text/bar/text columns
- **Page-type:** Visual Model, Conceptual — Analytical Framework
- **Reach for when:** showing 5 interconnected concepts + detailed sub-table; visual model + data side-by-side
- **Avoid when:** no need for both visual + table; ≤3 concepts

### slide 5 — Half-circle 5-segment with leader lines
- **Shows:** half-circle pie segmented into 5 wedges (gradient purple lighter→darker), 5 objective callouts on right with leader lines connecting to wedges
- **Page-type:** Visual Model, Conceptual — Analytical Framework
- **Reach for when:** 5 ordered objectives radiating from a center; want one-side callout layout; equal weight
- **Avoid when:** ≤3 or ≥7 objectives; symmetric layout needed (use full circle)

### slide 6 — 5-tier maturity pyramid (variant)
- **Shows:** same as 05.s6 — ascending 5-tier pyramid with side text descriptions
- **Page-type:** Visual Model, Conceptual — Analytical Framework
- **Reach for when:** maturity model; 4-5 levels with descriptions
- **Avoid when:** ≤3 levels; no progression theme

### slide 7 — 3D cube pyramid
- **Shows:** isometric 3D pyramid built from cubes (purple gradient), 9 surrounding callouts ("Your Text Here" + paragraph) with leader lines, icons on visible cube faces
- **Page-type:** Visual Model, Conceptual — Analytical Framework
- **Reach for when:** building-blocks story with multiple components; ≥7 callouts to attach; want dimensional visual
- **Avoid when:** ≤5 callouts (overkill); flat model would do (use pyramid)

### slide 8 — Wheel infographic with side callouts
- **Shows:** central circle with title + 8 surrounding wedges with numbers (02-09), 8 callouts (4 left + 4 right) with icons + paragraphs
- **Page-type:** Visual Model, Conceptual — Analytical Framework
- **Reach for when:** 8-element framework arranged radially; want hub-and-spoke visual; numbered for sequence
- **Avoid when:** ≤4 or ≥10 elements; linear story (use chevron)

### slide 9 — Hexagon infinity loop
- **Shows:** 6-segment overlapping hexagonal loop in center, 6 callouts (3 left + 3 right) with title + paragraph + icon
- **Page-type:** Visual Model, Conceptual — Analytical Framework
- **Reach for when:** 6 interconnected concepts forming a system; equal weight; want unified visual not flat list
- **Avoid when:** ≤4 or ≥8 elements; sequential not interconnected; flat list works

---

## 12_KPIs and Dashboards.pptx

### slide 2 — KPI tile dashboard
- **Shows:** dual-section. Left: title card + gauge visual + 4-tile KPI grid. Right: full-height line chart with shaded confidence band
- **Page-type:** Status Update, Data Deep-Dive
- **Reach for when:** executive dashboard with KPI overview + trend chart; ≤5 KPI tiles; one focal trend
- **Avoid when:** multiple trends (use small multiples); no KPI summary needed; quarterly review (use slide 3)

### slide 3 — Strategy KPI dashboard table
- **Shows:** 4-area row-grouped × 7-column comparison table (Strategy pillar/KPI/%/Actual/Target/Status/Trend/Comments), RAG status circles + trend arrows
- **Page-type:** Status Update, Comparison
- **Reach for when:** comprehensive KPI tracking with status + trend per metric; multiple strategy pillars; need RAG visibility
- **Avoid when:** ≤5 KPIs (use tiles); no pillar grouping; no trend data
