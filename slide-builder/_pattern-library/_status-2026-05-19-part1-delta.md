# Pattern Review Part 1 Delta — 2026-05-19 (patterns 001–100)

User's reviewed status vs the prior 2026-05-18 baseline.

**New totals (part 1 only):** 67 approved · 24 tweak · 6 rejected · 3 pending

---

## Changed status

### Promoted (was rejected/tweak → now APPROVED)
| Pattern | Was | Now |
|---|---|---|
| 55 Delay sensitivity burn scale | REJECTED | APPROVED |
| 78 Weighted decision matrix | TWEAK | APPROVED |

### Demoted to TWEAK (was APPROVED)
| Pattern | Issue |
|---|---|
| 14 Gantt workplan timeline | Rogue diamond in legend under "upcoming" |
| 19 Cover split panel | Delete the purple square top-right |
| 20 Risk heat map | Matrix overlaps takeaway; make matrix 60/40 with tracked risks |
| 35 Funnel conversion | "Client ready 28" exceeds bottom padding |
| 40 Closing CTA revival | Too much whitespace bottom; recenter |
| 44 KPI scorecard table | Legend always below subheadline; no overlap |
| 45 Swim-lane chevron handoff | Bigger boxes below chevrons; #4 not aligned |
| 63 RACI matrix | Legend always below subheadline; no overlap |
| 69 Tornado sensitivity chart | Move "baseline:14 days" to open space |
| 80 Phased rollout | Text overlaps right side of timeline boxes (already partially fixed this session — verify) |
| 82 McKinsey 7S | Shape image to left half; expand right panel 60/40 or 50/50 |
| 86 Risk register table | Legend always below subheadline; no overlap |
| 87 Workstream × phase matrix | Legend always below subheadline; no overlap |
| 88 Status report exec summary | Spacing of key risks/wins leaves white space; decisions takes too much |
| 90 Capability gap analysis | Legend always below subheadline; no overlap |
| 92 Three-step approach chevrons | Expand chevrons; narrow tip should meet boxed content edge |
| 93 Communication plan matrix | Legend always below subheadline; table overlaps bottom strip |

### Demoted to REJECTED (was APPROVED or TWEAK)
| Pattern | Reason |
|---|---|
| 83 Porter's 5 forces | Ugly slide |
| 99 Quick-win priority matrix | Ugly; too many matrices already |

### Newly PENDING (was APPROVED — needs design decision)
| Pattern | Note |
|---|---|
| 33 Fishbone diagram | (pending re-decision) |
| 49 Convergence paths to outcome | (pending re-decision) |
| 54 Scenario comparison ledger | (pending re-decision) |

### Newly TWEAK (was REJECTED — wants to revive)
| Pattern | Issue |
|---|---|
| 8 Closing CTA original | Make bottom section bigger; primary ask one font size smaller |
| 79 ROI calculator visual | Arrows look disjointed; math on one line not two |

---

## Patterns that need builder fixes (have a builder today; need rework)

These have builders in `slide-builder/twins/builders/`. The change of status to TWEAK means the builder needs to be edited:

**Legend-below-subheadline cluster** (one root cause, fixes 6 patterns):
- 44, 63, 86, 87, 90, 93 — all need their legend moved to just below the subheadline, body content rebalanced so nothing overlaps. Same fix recipe.
- 73 (Workshop agenda) also in this cluster — was already TWEAK, still is.

**Individual fixes:**
- 14 Gantt: remove rogue diamond from legend
- 19 Cover: remove purple square top-right (builder line referencing `cover-brand-mark` likely)
- 20 Risk heatmap: 60/40 split matrix vs tracked-risks list
- 35 Funnel: bottom-tier text overflow
- 40 Closing CTA: recenter to fill whitespace
- 45 Swim-lane chevron: bigger boxes; align #4
- 69 Tornado: reposition baseline label
- 80 Phased rollout: ALREADY FIXED this session — verify against latest render
- 82 7S: split layout 60/40
- 88 Status report: rebalance whitespace
- 92 Three-step chevrons: align chevron tips to box edges

**Newly rejected — delete from catalog + delete builder:**
- 83 Porter's 5 forces
- 99 Quick-win priority matrix

**Newly pending — keep builder, mark catalog entry as `status: pending`:**
- 33 Fishbone, 49 Convergence paths, 54 Scenario ledger

**Newly tweak from rejected (no builder yet; need design fixes first):**
- 8 Closing CTA original
- 79 ROI calculator

---

## Recommended action sequence (waiting for parts 2-4 before executing)

1. Wait for user's REVIEW-2/3/4 status updates.
2. Once full status is in, run a single cleanup pass:
   - Delete builders for newly-rejected patterns
   - Update catalog: remove rejected, mark pending, update tags for approved
   - Apply legend-below-subheadline fix across the 7-pattern cluster (one targeted batch)
   - Apply per-pattern fixes for the individual TWEAK items
3. Then run the catalog enrichment (good_for / bad_for) — item #11 from open list.
4. Then align selector vocab to storyline-helper glossary — item #1.
