"""
EXEMPLAR — Chart slide with multi-series legend (the canonical "chart treatment standard")

Demonstrates the four typographic moves that every chart slide should make:
  1. Action title (top of slide) — states the so-what, not the chart's topic
  2. Sub-headline — italic context line + brand-rule
  3. Legend (right-aligned, just below the brand-rule) — color-to-series chips
  4. Chart subtitle (eyebrow style, above the chart) — "what am I looking at"

PLUS the one-accent-moment discipline:
  - All three data series use neutral / brand-family colors (grey, mid-purple, deep purple)
  - The accent (BRAND_ACCENT) appears EXACTLY ONCE, on the callout annotation
  - The callout points at the load-bearing data point (Q4 APAC) — this is what
    the action title is making a claim about

Rendered exactly the way a consultant would expect to read a chart slide:
  eyes go title → sub-headline → legend → chart subtitle → chart → callout
  → takeaway. The reader doesn't have to do the encoding work.
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
# Multi-series grouped bar chart
# ---------------------------------------------------------------------------
def _grouped_bars(slide, x, y, w, h):
    """4 quarter groups, each with 3 series (NA / EMEA / APAC) bars side by side.
    Values intentionally tell a story: APAC accelerates each quarter, EMEA flat,
    NA in slight decline. Q4 APAC = climax = where the orange callout points.
    """
    # Series order matters — left-to-right within each group: NA, EMEA, APAC.
    series = [
        ("NA",   TEXT_MID,           [102, 100, 96, 92]),
        ("EMEA", BRAND_PRIMARY_MID,  [78, 80, 81, 83]),
        ("APAC", BRAND_PRIMARY,      [62, 75, 96, 124]),
    ]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    n_groups = len(quarters)
    n_bars = len(series)
    group_gap = 36
    inner_gap = 6

    # Compute layout: each group occupies (3 bars + 2 inner gaps); groups separated by group_gap
    total_inner = (w - group_gap * (n_groups - 1))
    group_w = total_inner // n_groups
    bar_w = (group_w - inner_gap * (n_bars - 1)) // n_bars

    # Y axis: 0..max_val mapped to bar heights up to (h - 36)
    max_val = max(v for _, _, vals in series for v in vals)
    base_y = y + h - 28           # bottom of bars (above x-axis labels)
    max_bar_h = h - 60            # leave headroom for $-labels above tallest bar

    # Optional faint y-axis baseline (zero line)
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
            # $-value label above the bar (only above APAC bars to avoid clutter
            # — direct-label convention: label the series the story is about)
            if name == "APAC":
                add_text(
                    slide, f"barval-{gi}-{si}",
                    f"${v}M",
                    x_px=bx - 6, y_px=by - 18, w_px=bar_w + 12, h_px=16,
                    font_size_px=11, color=TEXT_DARK, bold=True, align="center",
                )

        # Quarter label centered under the group
        add_text(
            slide, f"qlbl-{gi}", q,
            x_px=group_x, y_px=base_y + 6, w_px=group_w, h_px=18,
            font_size_px=12, color=TEXT_MID, align="center",
        )


# ---------------------------------------------------------------------------
# Legend chips — right-aligned, below the sub-headline
# ---------------------------------------------------------------------------
def _legend(slide, y, right_edge):
    """Right-aligned 3-chip legend. Chips read in the same order as the bars
    within each group (NA → EMEA → APAC). Built right-to-left so the rightmost
    chip's right edge lands exactly on `right_edge`.
    """
    chips = [
        (TEXT_MID,          "NA"),
        (BRAND_PRIMARY_MID, "EMEA"),
        (BRAND_PRIMARY,     "APAC"),
    ]
    swatch_size = 12
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
                 x_px=x, y_px=y + 3, w_px=swatch_size, h_px=swatch_size,
                 fill_color=color)
        add_text(slide, f"legend-label-{slug}",
                 label,
                 x_px=x + swatch_size + inner_gap, y_px=y,
                 w_px=label_w, h_px=16,
                 font_size_px=11, color=TEXT_DARK)


# ---------------------------------------------------------------------------
# Callout annotation — the ONE accent moment, points at Q4 APAC bar
# ---------------------------------------------------------------------------
def _callout(slide, chart_x, chart_y, chart_w, chart_h):
    """Orange (BRAND_ACCENT) callout pill + leader line pointing at the Q4 APAC
    bar. This is the slide's single accent moment. The pill text says +47% YoY
    — the load-bearing claim the action title hinges on.
    """
    # Position the callout pill upper-right of the chart, with a leader line
    # angling down-left toward the Q4 APAC bar's value-label position.
    # Q4 group is the 4th of 4 → group_x = chart_x + 3*(group_w + group_gap)
    # APAC bar is the 3rd of 3 within the group.
    # Compute the approximate position of the Q4 APAC bar top:
    # (we duplicate a small bit of layout math here — keeps the callout
    # self-contained without coupling to the chart's internal coords)
    group_gap = 36
    inner_gap = 6
    total_inner = (chart_w - group_gap * 3)
    group_w = total_inner // 4
    bar_w = (group_w - inner_gap * 2) // 3
    q4_x = chart_x + 3 * (group_w + group_gap)
    apac_bar_x = q4_x + 2 * (bar_w + inner_gap)
    apac_bar_top_y = chart_y + 60 + 10  # approximate top — tallest bar in the chart

    # Pill: rounded rectangle simulated with a filled rect (chart slide stays simple)
    pill_w = 130
    pill_h = 32
    pill_x = chart_x + chart_w - pill_w
    pill_y = chart_y - 6
    add_rect(slide, "callout-pill", pill_x, pill_y, pill_w, pill_h, BRAND_ACCENT)
    add_text(
        slide, "callout-text", "+47% YoY",
        x_px=pill_x, y_px=pill_y, w_px=pill_w, h_px=pill_h,
        font_size_px=14, color=WHITE, bold=True, anchor="middle", align="center",
    )
    # Leader: a thin angled line from the pill's bottom-left toward the bar top.
    # Approximated as a 1px BRAND_ACCENT rect; for a real angled leader you'd
    # use a connector shape. Keeping it as a faint rect lets the python-pptx
    # primitive stay clean. Agents building real charts can swap in a connector.
    leader_x = apac_bar_x + bar_w // 2
    leader_top_y = pill_y + pill_h
    leader_bot_y = apac_bar_top_y
    leader_h = leader_bot_y - leader_top_y
    if leader_h > 0:
        add_rect(slide, "callout-leader",
                 x_px=leader_x, y_px=leader_top_y, w_px=2, h_px=leader_h,
                 fill_color=BRAND_ACCENT)


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------
def build():
    prs, slide = new_slide()

    # Action title states the so-what (not the chart topic).
    add_title_block(
        slide,
        title="APAC overtakes NA by Q4 — the engine of FY26 growth.",
        subtitle="Quarterly revenue by region ($M), FY26.",
    )

    # Legend: right-aligned below the brand-rule (the rule's right edge is also
    # the right margin of the canvas body).
    _legend(slide, y=142, right_edge=1280 - 64)

    # Chart subtitle (eyebrow style — what am I looking at?) — separate from
    # the action title above. Keeps body-of-slide self-explanatory if the deck
    # is read out of context.
    add_text(
        slide, "chart-subtitle",
        "QUARTERLY REVENUE BY REGION ($M)",
        x_px=64, y_px=176, w_px=600, h_px=14,
        font_size_px=11, color=TEXT_MID, uppercase=True,
        letter_spacing_px=1,
    )

    # Chart area
    chart_x = 64
    chart_y = 204
    chart_w = 1280 - 128
    chart_h = 320

    _grouped_bars(slide, chart_x, chart_y, chart_w, chart_h)
    _callout(slide, chart_x, chart_y, chart_w, chart_h)

    # Takeaway strip below the chart — bottom-of-body anchor that closes the slide.
    takeaway_y = chart_y + chart_h + 24
    add_rect(slide, "takeaway-bg", 64, takeaway_y, 1280 - 128, 48, BRAND_PRIMARY)
    add_text(
        slide, "takeaway-text",
        "APAC's $58M FY26 delta is 2× total NA growth — concentrate FY27 invest there.",
        x_px=64, y_px=takeaway_y, w_px=1280 - 128, h_px=48,
        font_size_px=14, color=WHITE, italic=True,
        anchor="middle", align="center", padding_px=(0, 22, 0, 22),
    )

    add_footer(slide, page_num=1)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
