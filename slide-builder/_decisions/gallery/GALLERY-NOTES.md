# Gallery — simpler-architecture proof-of-concept

11 PNGs at 1280x720 rendered via LibreOffice headless from python-pptx scripts.
Each script imports `slide-builder/twins/helpers.py` for chrome (title block,
footer, brand colors) and uses raw python-pptx + helpers for body geometry.

## Per-PNG verdict

1. **gallery1-full-canvas.png** — Hero claim with single dominant statement, brand-primary counter line, and supporting tagline. Look at how the asymmetric left-aligned composition breathes against the white canvas. **SHIPPABLE.**

2. **gallery2-50-50-vertical.png** — Today vs. Slide Lab columns separated by thin vertical rule. Parallel structure (eyebrow + headline + 4 bullet+body items per side) reads cleanly. Look at how the right-column header is brand-primary while left is gray, to anchor the "after" side. **SHIPPABLE.**

3. **gallery3-asymmetric-75-25.png** — Dark left anchor panel (28%) with eyebrow, takeaway, and big metric "+340 bps"; right body with three evidence cards. The metric pairs with the supporting cards to telegraph the takeaway. **SHIPPABLE.**

4. **gallery4-top-band-body.png** — Dark brand-primary band at the top with the headline finding, three numbered evidence cards below. Cards have purple numerals, accent rule, evidence + italic implication. **SHIPPABLE.**

5. **gallery5-n-column-row.png** — 4-phase migration roadmap with circle anchors connected by a brand-accent track. Each phase: numeral circle, name, month range, summary, bullets. **SHIPPABLE.**

6. **gallery6-vertical-n-row-stack.png** — 4 numeral-anchored rows ("01", "02", "03", "04") with big purple numerals, vertical accent line, head + body. The card-bg tint keeps rows readable without heavy borders. **SHIPPABLE.**

7. **gallery7-dense-grid.png** — 2x4 KPI scorecard with 8 tiles: label / value / delta-with-arrow / vs-plan / status. Green for on-plan, red for watch. Clearly the densest layout. **SHIPPABLE.**

8. **gallery8-left-rail-body.png** — Narrow dark left rail with vertical "DIAGNOSE" letters and "02 / 05" pagination; main body with eyebrow, big title, narrative paragraph, three vertical metric tiles, and a dark "SO WHAT" band. Tiles use a vertical-stack layout (metric on top, sub below). **SHIPPABLE.**

9. **gallery9-horizontal-bands.png** — Today (light) above, 12-month future (dark brand-primary) below, separated by a downward arrow. Each band has eyebrow + headline + 3 bullets. The visual contrast carries the before/after story without needing extra graphics. **SHIPPABLE.**

10. **gallery10-chart-quadrant.png** — BCG 2x2 with brand-primary axes, quadrant labels in the four corners, 6 product bubbles plotted at correct fractional coordinates, and a right-side "Recommended moves" legend. **This is the test of matrix=chart collapse:** the quadrant labels and dots all live on a single chart canvas built from shapes + text overlays, no separate matrix layer needed. **SHIPPABLE.**

11. **gallery11-table.png** — 5-column comparison table with brand-primary header row, banded body, brand-accent-soft fill + left edge bar on the recommended row (Option B). Bold first column. "So what" callout beneath with brand-accent bar. **SHIPPABLE.**

## Rendering notes

- LibreOffice headless PNG conversion threw `Could not find platform independent libraries <prefix>` warnings on stderr (caused by `soffice.exe` inheriting host PYTHONHOME). The warnings are cosmetic — every PNG converted successfully.
- LibreOffice serialized the conversions when called in sequence; running them in parallel only produced 3 of 11 PNGs. Stopping any orphaned `soffice` process between sequential calls produced all 11 cleanly.
- Some Unicode glyphs (▲ ▼ ✓ ▼) were swapped for ASCII equivalents (UP, DN, v, *) because the rendered system fonts did not always include the symbol; safer for deterministic output. Future iteration could pull from the icon library instead.

## Defects caught and fixed during build (kept for the architecture record)

- **G10 quadrant label swap (fixed):** initial draft had STARS in the top-left corner; BCG convention is STARS = high-growth + high-share (top-right). Swapped pairs.
- **G11 RECOMMENDED badge overlap (fixed):** badge sat on top of the "Strategic fit" body text on the recommended row. Removed badge; the brand-accent left-edge stripe + tinted row fill already signal the recommendation.
- **G3 metric wrap (fixed):** "+340 bps" at 46pt overflowed the 300-px wide dark panel and wrapped "bps" to a new line. Reduced to 38pt.
- **G8 tile overlap (fixed):** original two-column tile layout caused "orders sampled" + "Mar-Apr 2026" labels to collide. Replaced with single-column vertical stack: big metric on top, italic caption below.

## Overall verdict

11 of 11 SHIPPABLE after one iteration. The architecture (helpers.py + raw python-pptx for body geometry) handles all 11 layout cases without needing layout-specific helpers. Quadrant chart and table render cleanly from the same primitives — the matrix=chart collapse holds. Recommend locking the architecture.
