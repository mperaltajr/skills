# table-without-column-headers — WHY NOT

**Family:** Data Tables (also relevant to Comparison)
**Verdict:** dont

## The problem

Five rows of parallel numeric data sit in a 4-column grid with **no header row** explaining what any column represents. The reader sees:

```
[Workstream A]   [$X.XM]   [Y FTE]   [Z%]
[Workstream B]   [$X.XM]   [Y FTE]   [Z%]
[Workstream C]   [$X.XM]   [Y FTE]   [Z%]
[Workstream D]   [$X.XM]   [Y FTE]   [Z%]
[Workstream E]   [$X.XM]   [Y FTE]   [Z%]
                 [$XX.XM]  [YY FTE]  [ZZ%]
```

Every number is undecodable:
- Is `[$X.XM]` annual cost? Run-rate? Forecast? Variance to plan?
- Is `[Y FTE]` current headcount, target, or gap?
- Is `[Z%]` utilization, share of total, variance, or completion?

The totals row at the bottom amplifies the failure: three numbers float in the metric columns with **no "Total" label** in the first column. The reader sees a row of larger bold numbers and has to infer from position that these are totals — and even then, totals of what is still ambiguous.

## Rule violated

`designer-brief.md` § 4 Data Tables:

> "Parallel rows of numeric values that don't strictly use `add_table` (e.g., McKinsey-style structured columns) still need labeled column headers — the rule applies to any tabular content."

> "Header row in BRAND_PRIMARY band with WHITE text, banded rows for legibility, right-aligned numeric columns…"

This slide has zero header row, zero column labels, and an unlabelled totals row. Three structural failures stacked on one grid.

## Why this is a teaching anti-exemplar

The pattern is seductive because the data is genuinely tabular and the grid *looks* clean — straight columns, hairlines, right-aligned numbers. It passes a glance test. It fails the moment a reader tries to actually **use** the slide to answer a question, because every number is ambiguous without column context.

This failure recurs whenever a builder reaches for `add_rect` + `add_text` to hand-roll columns instead of using the table helper. The hand-rolled version omits the header because the builder is thinking in rows, not in (column, row) tuples.

## What to do instead

**Preferred:** use `add_table(slide, headers=[...], rows=[...])`. The helper makes `headers` a **mandatory keyword argument with no default** — calling `add_table` without headers raises a `TypeError`. The API enforces the rule by construction; this failure mode cannot recur with the helper.

```python
add_table(
    slide, "cost-table",
    x_px=64, y_px=180, w_px=1152, h_px=320,
    headers=["Workstream", "Annual cost", "Headcount", "Share of spend"],
    rows=[
        ["[Workstream A]", "[$X.XM]", "[Y FTE]",  "[Z%]"],
        ["[Workstream B]", "[$X.XM]", "[Y FTE]",  "[Z%]"],
        # ...
        ["Total",          "[$XX.XM]","[YY FTE]", "[ZZ%]"],
    ],
)
```

The totals row becomes a normal row with "Total" in the first column — labelled, aligned, anchored.

**If hand-building parallel columns** (justified case: cell-treatment patterns the helper doesn't support yet, or a layout that mixes table-like rows with non-table elements): the first row MUST be an explicit header row with column labels. Render it as a BRAND_PRIMARY band with WHITE text matching the helper's output. The totals row MUST carry a "Total" label cell in the first column.

## See also

- `reference/layouts.md` § "Table" — canonical v0.1 table pattern (proper column headers, type-prefix rows)
- `twins/helpers.py` `add_table()` — the helper signature that enforces this rule
