# Stage 1 Deletions — Final List (post Wave A + Wave B review)

Builders + HTML files + catalog entries to delete.

## Light builders (10)

| Pattern | Builder | HTML | Reason |
|---|---|---|---|
| 20  | build_20.py  | 20_risk-heat-map.html | TWEAK 2x didn't converge; AM review REJECTED |
| 80  | build_80.py  | 80_phased-rollout-multi-wave-plan.html | TWEAK 2x didn't converge |
| 83  | build_83.py  | 83_porters-5-forces.html | Original review: "ugly slide" |
| 90  | build_90.py  | 90_capability-gap-analysis.html | TWEAK 2x didn't converge |
| 99  | build_99.py  | 99_quick-win-priority-matrix.html | Original review: "ugly slide, too many matrices" |
| 150 | build_150.py | 150_retrospective-sailboat.html | TWEAK 2x didn't converge ("adjustment made it worse") |
| 182 | build_182.py | 182_comparison-with-explicit-math.html | PENDING → user confirmed table |
| 191 | build_191.py | 191_ecosystem-map.html | TWEAK 2x didn't converge |
| 194 | build_194.py | 194_key-messages-per-audience.html | TWEAK 2x didn't converge |
| 295 | build_295.py | 295_split-color-cover.html | Wave A REJECTED |

## Dark builders (7)

| Pattern | Builder | HTML | Reason |
|---|---|---|---|
| 28d  | build_28d.py  | 28_vertical-timeline-dark.html | Wave B REJECTED |
| 29d  | build_29d.py  | 29_decision-tree-dark.html | Wave B REJECTED |
| 31d  | build_31d.py  | 31_maturity-pyramid-dark.html | Wave B REJECTED |
| 34d  | build_34d.py  | 34_cycle-diagram-dark.html | Wave B REJECTED |
| 41d  | build_41d.py  | 41_persona-card-dark.html | Wave B REJECTED |
| 70d  | build_70d.py  | 70_radar-capability-dark.html | Wave B REJECTED |
| 191d | build_191d.py | 191_ecosystem-map-dark.html | Wave B REJECTED (light also rejected) |

## Stage 1 cleanup actions

1. Delete 17 builder files (10 light + 7 dark)
2. Move corresponding HTML files to `_pattern-library/_rejected/`
3. Remove catalog entries for all 17 patterns from `twins/pattern_catalog.yaml`

**Total catalog after Stage 1**: 325 builders - 17 deletions = **308 production builders**.
