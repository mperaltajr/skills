# chart-right-takeaway

**What this is.** Sibling variant of `chart-bottom-takeaway` — same chart, same data — but the takeaway moves from a full-width bottom band to a right-hand card sitting alongside the chart in a 2-column grid.

**What makes it strong.**
- **Two-column sibling layout.** Chart column (760w) + gutter (28) + takeaway column (~364w). Both columns share `column_top_y=176` and `column_bottom_y=584` — they are sibling boxes with identical vertical extents, which is what makes the layout read as a 2-column grid rather than two stacked things.
- **Legend constrained to the CHART column width.** Right-aligned to `left_x + left_w` (the chart's right edge), NOT to the canvas right edge. This makes the legend visually belong to its chart rather than floating across the whole slide.
- **Chart subtitle eyebrow + legend on the SAME ROW.** Subtitle left-aligned at the chart column top; legend right-aligned at the chart column top. Both at y=176 — together they form a single header bar above the bars.
- **One accent moment INSIDE the right-hand card.** A BRAND_ACCENT pill at the bottom of the takeaway card carrying "+47% YoY" in 15px WHITE bold. The chart itself stays accent-free — accent has moved from the chart (in the bottom-takeaway variant) to the card.
- **Takeaway card vertical rhythm.** Eyebrow (11px uppercase TEXT_MID) → heading (20px BRAND_PRIMARY bold, the so-what) → italic body (14px TEXT_MID, context) → 3 supporting bullets (region + trajectory text, 13px) → callout pill at the bottom.
- **Bullets use small BRAND_PRIMARY-square markers (6x6 px),** never bullet characters.

**Reach for this when.** The takeaway needs more room than a one-line band — 3+ bullets, an evidence list, OR a callout chip embedded in supporting prose. Also when the chart benefits from a narrower aspect ratio. Or when the editorial emphasis is "argument right, evidence left."

**Patterns to copy.** Sibling-box geometry (shared `column_top_y` and `column_bottom_y`); legend constrained to the chart column; callout pill INSIDE a card (vs ON a chart); the eyebrow → heading → italic body → bullet list → pill 5-element card vertical rhythm.
