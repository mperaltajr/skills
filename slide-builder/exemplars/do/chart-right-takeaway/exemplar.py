"""
EXEMPLAR — Chart slide with RIGHT-HAND takeaway card (the sibling variant)

Same teaching content as the bottom-takeaway exemplar, but the takeaway moves
from a full-width bottom band to a right-hand card. Use this layout when:
  - The takeaway needs more room (3+ bullets, evidence list, or a callout chip)
  - The chart benefits from a slightly narrower aspect ratio
  - The slide needs to read "argument right, evidence left"

KEY LAYOUT MOVES (the differences from the bottom-takeaway variant):
  1. Chart shrinks from ~95% canvas width to ~62%
  2. Takeaway becomes a right-hand card (~32% width) anchored to chart-y
  3. Legend is constrained to the CHART column width (not full canvas)
     — its right edge sits at the right edge of the chart area, not the slide
  4. Chart subtitle still in eyebrow style above the chart
  5. ONE accent moment: the orange callout INSIDE the right-hand card
     (different from the bottom variant where the accent was on the chart itself)
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT, CARD_BG, CARD_BORDER, WHITE,
)


# ---------------------------------------------------------------------------
# Grouped bar chart (same data as the bottom-takeaway variant — keeps the pair
# directly comparable as a teaching set)
# ---------------------------------------------------------------------------
def _grouped_bars(slide, x, y, w, h):
    series = [
        ("NA",   TEXT_MID,           [102, 100, 96, 92]),
        ("EMEA", BRAND_PRIMARY_MID,  [78, 80, 81, 83]),
        ("APAC", BRAND_PRIMARY,      [62, 75, 96, 124]),
    ]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    n_groups = len(quarters)
    n_bars = len(series)
    group_gap = 24
    inner_gap = 5
    total_inner = (w - group_gap * (n_groups - 1))
    group_w = total_inner // n_groups
    bar_w = (group_w - inner_gap * (n_bars - 1)) // n_bars

    max_val = max(v for _, _, vals in series for v in vals)
    base_y = y + h - 28
    max_bar_h = h - 60

    add_rect(slide, "chart-baseline",
             x_px=x, y_px=base_y, w_px=w, h_px=1,
             fill_color=CARD_BORDER)

    for gi, q in enumerate(quarters):
        group_x = x + gi * (group_w + group_gap)
        for si, (name, color, vals) in enumerate(series):
            v = vals[gi]
            bh = int(max_bar_h * (v / max_val))
            bx = group_x + si * (bar_w + inner_gap)
            by = base_y - bh
            add_rect(slide, f"bar-{gi}-{si}", bx, by, bar_w, bh, color)
            if name == "APAC":
                add_text(
                    slide, f"barval-{gi}-{si}",
                    f"${v}M",
                    x_px=bx - 6, y_px=by - 18, w_px=bar_w + 12, h_px=16,
                    font_size_px=11, color=TEXT_DARK, bold=True, align="center",
                )
        add_text(
            slide, f"qlbl-{gi}", q,
            x_px=group_x, y_px=base_y + 6, w_px=group_w, h_px=18,
            font_size_px=12, color=TEXT_MID, align="center",
        )


# ---------------------------------------------------------------------------
# Legend chips — right-aligned to the CHART column (not the full canvas)
# ---------------------------------------------------------------------------
def _legend(slide, y, right_edge):
    """Right-aligned legend chips. `y` is the row's top Y; the swatches and
    labels are vertically centered inside a `row_h` band so swatch-center and
    text-center sit on the same line. `right_edge` is the rightmost X the
    legend should extend to (usually the chart column's right edge so the
    legend visually belongs to its chart)."""
    chips = [
        (TEXT_MID,          "NA"),
        (BRAND_PRIMARY_MID, "EMEA"),
        (BRAND_PRIMARY,     "APAC"),
    ]
    row_h = 16
    swatch_size = 10
    # Vertical center the swatch inside the row band:
    swatch_y = y + (row_h - swatch_size) // 2  # 3 for row_h=16, swatch=10
    inner_gap = 6
    chip_gap = 22

    cursor_x = right_edge
    placed = []
    for color, label in reversed(chips):
        label_w = int(len(label) * 7.0) + 4
        chip_w = swatch_size + inner_gap + label_w
        left_edge = cursor_x - chip_w
        placed.append((color, label, left_edge, label_w))
        cursor_x = left_edge - chip_gap
    placed.reverse()

    for color, label, x, label_w in placed:
        slug = label.lower().replace(" ", "-")
        add_rect(slide, f"legend-swatch-{slug}",
                 x_px=x, y_px=swatch_y, w_px=swatch_size, h_px=swatch_size,
                 fill_color=color)
        add_text(slide, f"legend-label-{slug}",
                 label,
                 x_px=x + swatch_size + inner_gap, y_px=y,
                 w_px=label_w, h_px=row_h,
                 font_size_px=11, color=TEXT_DARK, anchor="middle")


# ---------------------------------------------------------------------------
# Takeaway card — RIGHT-HAND. The slide's argument lives here.
# ---------------------------------------------------------------------------
def _takeaway_card(slide, x, y, w, h):
    """Right-hand card. Carries the so-what plus 3 supporting bullets and a
    callout pill at the bottom = the slide's single BRAND_ACCENT moment.

    Visual order from top:
      - Eyebrow ("THE TAKEAWAY") — 11px non-bold uppercase
      - Heading (the so-what) — 20px bold BRAND_PRIMARY, ≤2 lines
      - Body (italic context) — 14px TEXT_MID
      - Three numeric/bullet supports (12-14px TEXT_DARK)
      - Callout pill at bottom: "+47% YoY" — BRAND_ACCENT fill, white bold text
    """
    add_rect(slide, "takeaway-card-bg", x, y, w, h, CARD_BG)
    pad = 22

    # Eyebrow
    add_text(slide, "takeaway-eyebrow", "THE TAKEAWAY",
             x_px=x + pad, y_px=y + pad,
             w_px=w - 2*pad, h_px=14,
             font_size_px=11, color=TEXT_MID, uppercase=True,
             letter_spacing_px=1)

    # Heading
    add_text(slide, "takeaway-heading",
             "APAC is the engine of FY26 growth.",
             x_px=x + pad, y_px=y + pad + 22,
             w_px=w - 2*pad, h_px=66,
             font_size_px=20, color=BRAND_PRIMARY, bold=True)

    # Body — context line
    add_text(slide, "takeaway-body",
             "Three regions, three trajectories — only one is accelerating.",
             x_px=x + pad, y_px=y + pad + 90,
             w_px=w - 2*pad, h_px=44,
             font_size_px=14, color=TEXT_MID, italic=True)

    # Three supporting bullets (with subtle bullet rects in BRAND_PRIMARY)
    bullets = [
        ("APAC", "$62M → $124M, 2× over FY26"),
        ("NA",   "$102M → $92M, slight decline"),
        ("EMEA", "$78M → $83M, essentially flat"),
    ]
    bullet_y = y + pad + 140
    line_h = 36
    for i, (label, text) in enumerate(bullets):
        by = bullet_y + i * line_h
        # Small square bullet in BRAND_PRIMARY
        add_rect(slide, f"bullet-{i}-mark",
                 x_px=x + pad, y_px=by + 6, w_px=6, h_px=6,
                 fill_color=BRAND_PRIMARY)
        # Region label (compact, bold)
        add_text(slide, f"bullet-{i}-region", label,
                 x_px=x + pad + 14, y_px=by,
                 w_px=60, h_px=18,
                 font_size_px=13, color=TEXT_DARK, bold=True)
        # Trajectory text
        add_text(slide, f"bullet-{i}-text", text,
                 x_px=x + pad + 74, y_px=by,
                 w_px=w - 2*pad - 74, h_px=18,
                 font_size_px=13, color=TEXT_MID)

    # Callout pill at the BOTTOM of the card = the ONE BRAND_ACCENT moment.
    # Different placement than the bottom-takeaway variant where the accent
    # lives on the chart itself (callout pointing at Q4 APAC bar).
    pill_w = w - 2*pad
    pill_h = 42
    pill_y = y + h - pad - pill_h
    add_rect(slide, "callout-pill",
             x_px=x + pad, y_px=pill_y,
             w_px=pill_w, h_px=pill_h,
             fill_color=BRAND_ACCENT)
    add_text(slide, "callout-text",
             "Q4 APAC: +47% YoY",
             x_px=x + pad, y_px=pill_y,
             w_px=pill_w, h_px=pill_h,
             font_size_px=15, color=WHITE, bold=True,
             anchor="middle", align="center", padding_px=(0, 12, 0, 12))


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------
def build():
    prs, slide = new_slide()

    add_title_block(
        slide,
        title="APAC overtakes NA by Q4 — the engine of FY26 growth.",
        subtitle="Quarterly revenue by region ($M), FY26.",
    )

    # === Two-column layout: chart left, takeaway right ===
    # Both columns are SIBLING BOXES — same top edge (y=column_top_y) and same
    # bottom edge (y=column_bottom_y). The chart column has no visible card
    # background (the chart subtitle eyebrow sits at the top, bars fill below);
    # the takeaway column has a CARD_BG fill so it reads as an explicit box.
    # The takeaway card top edge ALIGNS with the chart subtitle's baseline so
    # the two columns appear as siblings in a 2-column grid.
    gutter = 28
    left_w = 760
    right_w = 1280 - 128 - left_w - gutter  # ~364
    left_x = 64
    right_x = left_x + left_w + gutter

    column_top_y = 176     # both columns start here
    column_bottom_y = 584  # both columns end here
    column_h = column_bottom_y - column_top_y  # 408

    # Chart column — subtitle eyebrow at the top of the column, LEFT-aligned;
    # the legend lives on the SAME ROW, RIGHT-aligned to the column's edge.
    # Together they form a clean "chart subtitle | legend" header bar.
    add_text(
        slide, "chart-subtitle",
        "QUARTERLY REVENUE BY REGION ($M)",
        x_px=left_x, y_px=column_top_y, w_px=left_w // 2, h_px=16,
        font_size_px=11, color=TEXT_MID, uppercase=True,
        letter_spacing_px=1, anchor="middle",
    )
    # Legend: same Y as the chart subtitle, right-aligned to the chart column
    _legend(slide, y=column_top_y, right_edge=left_x + left_w)
    # Chart bars start 28px below the eyebrow (gives the eyebrow breathing room)
    chart_bars_y = column_top_y + 28
    chart_bars_h = column_bottom_y - chart_bars_y  # 380
    _grouped_bars(slide, left_x, chart_bars_y, left_w, chart_bars_h)

    # Takeaway column — card box spans the FULL column (top edge aligns with
    # the chart subtitle baseline, bottom edge aligns with the chart baseline).
    _takeaway_card(slide, right_x, column_top_y, right_w, column_h)

    add_footer(slide, page_num=1)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
