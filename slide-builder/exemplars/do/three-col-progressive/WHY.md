# three-col-progressive

**Page type.** Three-column parallel (progressive variant) — specifically the SCQA / Problem-Solution-Recommendation exec-summary layout where the rightmost column is the load-bearing answer.

**What this is.** Three vertical columns with deliberate left-to-right emphasis escalation:
- **Column 1 (Problem)** — dashed neutral outline, white fill. Reads as context.
- **Column 2 (Solution)** — soft CARD_BG fill, thin neutral border. Reads as the analytical middle.
- **Column 3 (Recommendation)** — BRAND_PRIMARY dark ground, WHITE text, a BRAND_ACCENT 4px top rule. Reads as the answer.

**What makes it strong.**
- **The visual hierarchy mirrors the argument.** The eye is pulled rightward and lands on the recommendation. Anyone who only reads one column reads the right one — by design. This is the whole reason to use this pattern instead of `3pillar-icon-circles`.
- **One accent moment, well spent.** BRAND_ACCENT lives on column 3's top rule and nowhere else. The title-block no longer auto-emits a brand-rule, so the accent budget is fully available for the load-bearing element (the answer). Columns 1 and 2 carry zero accent.
- **Bold discipline = 4 (at ceiling).** Title + 3 column headings. Eyebrows are uppercase letter-spaced but NOT bold. Body text is NOT bold. Stays inside the ≤5 ceiling.
- **Same grid as the parallel three-column pattern.** body_left=64, gap=24, card_w=368, card_top=178, card_h=440. If you swap from this pattern to `3pillar-icon-circles` (or vice versa), nothing reflows.
- **Hierarchy from size and weight, not gray gradients.** TEXT_MID / TEXT_FAINT are aliased to TEXT_DARK in the helper module; this exemplar relies on size + weight + ground-color contrast instead of gray ramps (which read as off-brand on corporate templates).

**Reach for this when.**
- The three columns are **sequential**, not parallel: Problem → Solution → Recommendation; Past → Present → Future; Symptom → Diagnosis → Treatment.
- One column is **the answer** and the other two are setup. The reader's eye must end on the right.
- The deck is an **executive summary or SCQA close** where the recommendation has to dominate.

**Do NOT reach for this when.**
- The three things are **MECE peers** (three pillars of a method, three product lines, three branches of an org). Equal treatment is the point — use `3pillar-icon-circles` instead. Using progressive emphasis on parallel content would falsely signal that one pillar matters more than the others.
- You want **icon-anchored** cards (use `3pillar-icon-circles`).
- The three columns are **build phases of a process flow with explicit transitions** — that would warrant arrows or a horizontal flow pattern, not stacked columns.

**Distinction from `3pillar-icon-circles`.**
| | 3pillar-icon-circles | three-col-progressive |
|---|---|---|
| Logical relation | MECE / parallel pillars | Sequential / SCQA |
| Treatment across columns | Identical | Escalating (light → mid → dark) |
| Icon anchors | Yes — circular BRAND_PRIMARY caps | No |
| Accent location | None on cards (title rule only) | Column 3 top rule |
| Eye path | Scan-equal across three | Pulled rightward, lands on col 3 |
| Use when | Three peers | Problem / Solution / Recommendation |

**Patterns to copy.** The three-step emphasis ladder (dashed → soft fill → dark with accent rule). The shared column grid (same numbers as 3pillar-icon-circles so the two patterns are interchangeable at the geometry level). The `_add_dashed_card` helper for the de-emphasized column 1 outline.
