# Pattern library — future backlog

A running list of pattern ideas to add in future sessions. Library currently has 100 patterns; this is what's NOT yet built but worth adding when there's session time.

## How to use this file

When starting a new session, open this file and pick a batch:
1. Pick 8–15 patterns from below
2. Dispatch parallel agents (one per pattern) with the standard agent prompt template (see existing agent prompts in chat history or just describe pattern + apply shared CSS vars + standing QC checklist)
3. After agents return, append to REVIEW.html for user review
4. Mark items DONE here once shipped + approved

## Conventions (every new pattern must use)

```css
:root {
  --brand-primary: #2D0A4E;
  --brand-primary-mid: #5C2D87;
  --brand-accent: #A100FF;
  --brand-accent-soft: #C780FF;
  --text-dark: #1A1A2E;
  --text-mid: #64748B;
  --text-faint: #94A3B8;
  --slide-bg: #FFFFFF;
  --card-bg: #F8F4FC;
  --card-border: #E5D5F0;
  --draft-bg: #FFD600;
  --draft-text: #B71C1C;
}
```
- Canvas: 1280×720, Inter font
- Top chrome: ACCENTURE INTERNAL top-left (10px faint gray letter-spacing), DRAFT badge top-center
- Action title (28–32px bold) + sub-headline (14px italic gray) + brand-accent rule (56–80px × 3–4px)
- Footer: 1px rule + CONFIDENTIAL bottom-left + page meta bottom-right
- Convergence line where applicable
- Standing QC: hierarchy, single focal point, consistent margins, intentional whitespace, grid alignment, balanced page

## Backlog (organized by family)

### Charts & data viz
- [x] **Waterfall chart** — cumulative drivers up/down to a final number (e.g., revenue bridge) → 101
- [x] **Bubble chart with annotation** — 3-axis scatter (x, y, size) + commentary panel → 102
- [x] **Sankey diagram** — flows between categories with proportional widths → 103
- [x] **Geographic / map slide** — regions colored by metric, with annotation callouts → 104
- [x] **Time series with confidence band** — line + shaded uncertainty range → 105
- [x] **Cohort retention grid** — N cohorts × M periods, cells colored by retention % → 106
- [x] **Box plot / distribution** — show variance across categories → 107
- [x] **100% stacked horizontal bar** — composition by row → 108
- [x] **Multi-line chart** — 3-5 trend lines, key event annotations → 109
- [x] **Histogram** — frequency distribution + median/mode callouts → 110
- [x] **Cumulative line / S-curve** — adoption / saturation curve → 111

### Frameworks (analytical)
- [x] **Ansoff matrix** — 2x2 product (new/existing) × market (new/existing) → 112
- [x] **Strategy clock (Bowman's)** — 8 strategic positions → 155
- [x] **Wardley map** — value chain × evolution → 149
- [x] **Blue ocean strategy canvas** — competitive factors with curves → 113
- [x] **3 horizons** (different from 60 — McKinsey three-horizons WITH curves visualization) → 150
- [x] **Concept map / mind map** — central node with branching ideas → 114
- [x] **Five whys** — root cause iteratively probed (different from fishbone) → 115

### Process & flow
- [x] **Data flow diagram (DFD)** — inputs/processes/outputs with arrows → 116
- [x] **Sequence diagram** — actors × time interactions → 117
- [ ] **State machine** — states + transitions with labels
- [x] **Customer journey funnel** — combined funnel + emotion line → 118
- [ ] **Process compliance flowchart** — yes/no decisions through governance
- [x] **Approval workflow** — multi-stakeholder review chain → 119

### Org & people
- [x] **Multi-persona** (3 personas side-by-side) — different from single persona 41 → 120
- [x] **Team gallery** (multi-photo of team members with name/role) → 121
- [x] **Hiring plan** — roles × quarters with status → 122
- [x] **Succession plan** — current role → potential successor mapping → 151
- [x] **Skills matrix** — people × skill levels with heatmap cells → 123
- [x] **Capability ladder / career path** — progression levels → 152

### Financial
- [x] **Burn rate / runway chart** — cash over time with runway end marker → 124
- [x] **Cost-benefit waterfall** — investments vs. benefits stacked → 125
- [x] **P&L summary card** — revenue, expenses, profit in structured layout → 126
- [x] **Sensitivity range chart** — best/base/worst case bars → 148
- [x] **Break-even analysis** — revenue vs. costs intersecting lines → 127
- [x] **NPV / IRR summary card** — key metrics with sensitivity ranges → 128

### Status / governance
- [x] **Quarterly review scorecard** — N strategic pillars with progress bars → 129
- [x] **Investment / portfolio scorecard** — N investments × status & ROI → 130
- [x] **Steering committee dashboard** — RAG + decisions + risks combined → 131
- [x] **Vendor / partner scorecard** — compare N vendors across criteria → 132
- [x] **Compliance checklist** — N requirements × status → 133

### Strategy & narrative
- [x] **Win themes** (proposal-specific) — 3-4 thematic value props → 134
- [x] **Differentiators** (3 columns) — why we're different → 135
- [x] **Proof points compilation** — multiple case studies summarized → 136
- [ ] **Capability vs requirement gap** — different from 90 (this is text-table style)
- [x] **Theory of change v2** (5-column with feedback loop) — extends 62 → 156
- [x] **Logic model** — distinct from theory of change, shows assumptions → 154

### Workshop & meeting
- [x] **Workshop summary** — what we did, what we decided, what's next → 137
- [x] **Brainstorm output / affinity map** — clustered ideas → 138
- [x] **Retrospective sailboat** — risks (anchor), forces (wind), goals (island) → 139
- [x] **Decision log** — N decisions × date / owner / rationale → 140
- [x] **FAQ slide** — pre-answered common questions → 141

### Implementation & planning
- [x] **Sprint review summary** — completed / in-progress / blocked → 142
- [x] **Implementation tracker** — milestones × status → 143
- [x] **Annual planning view** — 12 months × workstreams → 144
- [x] **Cross-functional dependency map** — workstream A blocks workstream B visual → 145

### Concept & vision
- [x] **Letter / memo format** — from the partner, to the board, formal layout → 146/157
- [x] **One-page strategy** — vision + 3 pillars + key actions → 147/158
- [x] **North star alignment** — north star + 3 supporting metrics + initiatives that move them → 159
- [x] **Strategy on a page** — vision / pillars / OKRs / initiatives all on one slide → 160
- [x] **2-by-2 with axis text** (deeper labels than current 13 + 99) → 161

### Operations
- [x] **System landscape** — N systems with integration arrows → 162
- [x] **Architecture stack (cloud)** — IaaS / PaaS / SaaS layers → 163
- [x] **API integration map** — services + connections → 164
- [x] **Service catalogue** — list of services with descriptions + owners → 165
- [x] **Operating rhythm** — daily / weekly / monthly cadence visualization → 166

### Edge cases & specialty
- [x] **Press / coverage compilation** — quotes from media outlets → 167
- [x] **Awards / accolades** — list of achievements with logos → 168
- [x] **Recognition / hall of fame** — people + contributions → 169
- [x] **News timeline** — major events with dates → 170
- [x] **Glossary v2** (technical jargon, more dense than 43) → 171
- [x] **Acronym key** — alphabetized list of acronyms used in deck → 172
- [x] **Reference / further reading** — books, articles, links → 173
- [x] **Appendix divider with sub-list** — section break + what's in this appendix → 174

### Cover variants
- [x] **Cover full-bleed photo with title overlay** — narrative covers → 175
- [x] **Cover minimalist type-only** — just the title, big, centered → 176
- [x] **Cover with logo + tagline + sub-meta** — corporate one-sheet style → 177
- [x] **Cover sliced diagonal split** — two-tone diagonal background → 178

### Hybrid / experimental
- [x] **Anchored quote + chart pairing** — quote on left, supporting chart on right → 179
- [x] **Big number + small chart sparkline** — KPI tile but with mini trend → 180
- [x] **Multi-modal slide** (table + chart + insight) — dense exec layout → 181
- [x] **Comparison with explicit math** — A vs B with delta calculation shown → 182
- [x] **Annotated photo / screenshot** — with callout pin markers → 183

### Novel / web-inspired (added in v3.0 build)
- [x] **Executive one-pager** — 4-zone dense exec digest → 184
- [x] **Market sizing pyramid (TAM/SAM/SOM)** → 185
- [x] **Problem / opportunity statement** — side-by-side with directional arrow → 186
- [x] **Key assumptions & dependencies** — dual-column table → 187
- [x] **Go-to-market motion** — 4-stage funnel with channel strip → 188
- [x] **Value chain analysis (Porter's)** — support + primary activities + margin → 189
- [x] **Core competency tree** — org-chart-style tree → 190
- [x] **Ecosystem map** — concentric ring hub-and-spoke → 191
- [x] **Agile sprint board** — 4-column Kanban with sprint progress → 192
- [x] **Benefits realization tracker** — table with inline progress bars + RAG → 193
- [x] **Key messages per audience** — 4-column (Board/C-Suite/Ops/Front-line) → 194
- [x] **Risk vs. opportunity matrix** — dual-panel red/green comparison → 195
- [x] **Pilot results summary** — quant + qual + lessons learned → 196
- [x] **Solution overview** — challenge / solution / benefits 3-panel → 197
- [x] **Partnership model comparison** — 4-col matrix (Reseller/Co-Sell/OEM) → 198
- [x] **AI & digital enablers stack** — 5-layer stack + use cases → 199
- [x] **Now / next / later roadmap** — 3-column initiative cards → 200

---

## Status update process

When you complete a batch:
1. Cross off `[ ]` → `[x]` items here
2. Increment the library count in INDEX.md
3. Add new patterns to REVIEW.html MOCKUPS array
4. Commit (if working in git)

## Session handoff notes

If starting cold, also read:
- `_HANDOFF-2026-05-18.md` (in slide-builder root) — full architecture context
- `INDEX.md` — current library state
- `REVIEW.html` — sticky REVIEW UI with all patterns + standing QC banner

## Known limitations (won't fix in HTML; will need translator/PPTX work)

These items are HTML-shipped but may not translate cleanly to PPTX:
- Complex SVG (fishbone 33, decision tree 29, issue tree 39, BCG 84, 7S 82, Porter 83, radar 70, cycle 34)
- Native PPT tables for ones we built as flex/grid (44, 51, 56, 78, 86, 87, 93, 95)
- Embedded photo placeholders (22, 74, 77)
- Curved arrows / connectors

These will be revisited when building the HTML→PPTX translator.
