"""
Builder for pattern 67: 100% stacked bar with takeaway panel.

Left (70%): chart zone with axis label, top-right legend (4 categories),
stacked bars (Baseline + W1..W4) with focal accent ring on W4.
Right (30%): annotation panel with key-takeaway bullets.
Convergence: centered italic line below.

Source HTML: _pattern-library/67_stacked-bar-takeaway.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # --- Canonical title block (bottom-anchored, brand rule at y≈132) ---
    add_title_block(
        slide,
        title="Where deck time goes — <strong>composition shift from rework to storyline.</strong>",
        subtitle="100% stacked view, pilot baseline through week 4 — mix tilts toward the work that matters.",
    )

    # === LEGEND — below subheadline, right-aligned to x≈1216 (HARD RULE: y ≥ 230) ===
    leg_y = 232
    leg_items = [
        ("Storyline", BRAND_ACCENT),
        ("Building", BRAND_PRIMARY_MID),
        ("Reviewing", BRAND_ACCENT_SOFT),
        ("Reworking", CARD_BG),
    ]
    # Compute width and right-align so right edge ≈ 1216
    item_w = 90
    legend_total_w = len(leg_items) * item_w
    leg_x_start = 1216 - legend_total_w
    for i, (lbl, color) in enumerate(leg_items):
        n = i + 1
        lx = leg_x_start + i * item_w
        sw = add_rect(slide, f"legend-sw-{n}", lx, leg_y + 3, 12, 12, color)
        if color == CARD_BG:
            sw.line.color.rgb = CARD_BORDER
            sw.line.width = 6350
        add_text(
            slide, f"legend-lbl-{n}", lbl,
            x_px=lx + 16, y_px=leg_y, w_px=item_w - 18, h_px=16,
            font_size_px=10, color=TEXT_DARK,
        )

    # --- Body grid: chart 70 / annotation 30 (shifted down to clear legend) ---
    body_top = 268
    body_bottom = 580
    body_h = body_bottom - body_top
    gap = 24
    chart_w = int((1280 - 128 - gap) * 0.70)
    annot_x = 64 + chart_w + gap
    annot_w = 1280 - 64 - annot_x

    # === Chart zone ===
    # Axis label
    add_text(
        slide, "chart-axis-label",
        "Share of deck-hours · % of total",
        x_px=64, y_px=body_top, w_px=400, h_px=16,
        font_size_px=10, color=TEXT_FAINT, bold=True,
        letter_spacing_px=1.8, uppercase=True,
    )

    # Chart plot area
    # Increased bottom margin so x-axis category labels have breathing room (no longer
    # visually touching the bar bottoms).
    plot_top = body_top + 30
    plot_bottom = body_bottom - 56
    plot_h = plot_bottom - plot_top
    y_axis_w = 36
    plot_left = 64 + y_axis_w
    plot_right = 64 + chart_w
    plot_w = plot_right - plot_left

    # Y-axis labels + gridlines
    y_labels = [("100%", 0), ("75%", 0.25), ("50%", 0.5), ("25%", 0.75), ("0%", 1.0)]
    for i, (lbl, frac) in enumerate(y_labels):
        n = i + 1
        gy = plot_top + int(plot_h * frac)
        add_text(
            slide, f"y-label-{n}", lbl,
            x_px=64, y_px=gy - 8, w_px=y_axis_w - 4, h_px=14,
            font_size_px=9, color=TEXT_FAINT, align="right",
        )
        add_rect(slide, f"y-grid-{n}", plot_left, gy, plot_w, 1, CARD_BORDER)

    # Bars
    bars = [
        ("Baseline", "pre-pilot", 10, 12, 8, 70, False),
        ("Week 1",   None,        18, 18, 12, 52, False),
        ("Week 2",   None,        28, 22, 14, 36, False),
        ("Week 3",   None,        40, 24, 16, 20, False),
        ("Week 4",   "current",   50, 26, 14, 10, True),
    ]
    bar_count = len(bars)
    bar_w = 64
    bar_gap = (plot_w - bar_count * bar_w) // (bar_count + 1)
    seg_colors = {
        "story": BRAND_ACCENT,
        "build": BRAND_PRIMARY_MID,
        "review": BRAND_ACCENT_SOFT,
        "rework": CARD_BG,
    }
    for bi, (name, sub, s, b, r, w, focal) in enumerate(bars):
        n = bi + 1
        bx = plot_left + bar_gap + bi * (bar_w + bar_gap)
        # Stack bottom-up: rework, review, build, story
        # Total 100, plot_h maps to 100
        def yh(v):
            return int(plot_h * v / 100)
        # Rework at bottom
        h_w = yh(w)
        y_w = plot_bottom - h_w
        re = add_rect(slide, f"bar-{n}-rework", bx, y_w, bar_w, h_w, CARD_BG)
        re.line.color.rgb = CARD_BORDER
        re.line.width = 6350
        # Review
        h_r = yh(r)
        y_r = y_w - h_r
        add_rect(slide, f"bar-{n}-review", bx, y_r, bar_w, h_r, BRAND_ACCENT_SOFT)
        # Build
        h_b = yh(b)
        y_b = y_r - h_b
        add_rect(slide, f"bar-{n}-build", bx, y_b, bar_w, h_b, BRAND_PRIMARY_MID)
        # Story
        h_s = yh(s)
        y_s = y_b - h_s
        add_rect(slide, f"bar-{n}-story", bx, y_s, bar_w, h_s, BRAND_ACCENT)

        # Focal accent ring (W4)
        if focal:
            ring = add_rect(slide, f"bar-{n}-ring", bx - 3, y_s - 3, bar_w + 6, plot_bottom - y_s + 6, WHITE)
            ring.fill.background()
            ring.line.color.rgb = BRAND_ACCENT
            ring.line.width = 19050

        # In-bar labels (only segments >= 15%)
        def label(name, y, h, val, col, big=False):
            if val >= 15:
                add_text(
                    slide, name, f"{val}%",
                    x_px=bx, y_px=y, w_px=bar_w, h_px=h,
                    font_size_px=13 if big else 11, color=col,
                    bold=True, align="center", anchor="middle",
                )
        label(f"bar-{n}-rework-lbl", y_w, h_w, w, BRAND_PRIMARY_MID, big=False)
        label(f"bar-{n}-review-lbl", y_r, h_r, r, WHITE, big=False)
        label(f"bar-{n}-build-lbl", y_b, h_b, b, WHITE, big=False)
        label(f"bar-{n}-story-lbl", y_s, h_s, s, WHITE, big=focal)

        # Category label — extra padding below bars so labels don't kiss the bar bottoms
        cat_color = BRAND_ACCENT if focal else TEXT_DARK
        add_text(
            slide, f"bar-{n}-cat", name,
            x_px=bx - 10, y_px=plot_bottom + 16, w_px=bar_w + 20, h_px=16,
            font_size_px=11, color=cat_color, bold=True, align="center",
        )
        if sub:
            add_text(
                slide, f"bar-{n}-sub", sub,
                x_px=bx - 10, y_px=plot_bottom + 32, w_px=bar_w + 20, h_px=12,
                font_size_px=9, color=cat_color if focal else TEXT_FAINT, bold=focal,
                align="center",
            )

    # === Annotation panel ===
    ap = add_rect(slide, "annotation-bg", annot_x, body_top, annot_w, body_h, CARD_BG)
    add_rect(slide, "annotation-accent", annot_x, body_top, 3, body_h, BRAND_ACCENT)

    add_text(
        slide, "annot-tag", "Key takeaway",
        x_px=annot_x + 22, y_px=body_top + 20, w_px=annot_w - 44, h_px=14,
        font_size_px=10, color=BRAND_ACCENT, bold=True,
        letter_spacing_px=1.8, uppercase=True,
    )
    add_text(
        slide, "annot-headline",
        "Time shifts from rework to storyline — <strong>that's the unlock.</strong>",
        x_px=annot_x + 22, y_px=body_top + 40, w_px=annot_w - 44, h_px=48,
        font_size_px=14, color=BRAND_PRIMARY, bold=True,
        emphasis_color=BRAND_ACCENT,
    )

    bullets = [
        "<strong>Rework collapses</strong> from 70% of deck-hours to 10% in four weeks.",
        "<strong>Storyline rises 5×</strong> — from 10% to 50% — as the dominant activity.",
        "Building and reviewing stay <strong>roughly flat</strong> — the mix change is real, not a volume artifact.",
    ]
    by = body_top + 100
    for i, b in enumerate(bullets):
        n = i + 1
        add_text(
            slide, f"annot-bullet-{n}-marker", "▸",
            x_px=annot_x + 22, y_px=by, w_px=14, h_px=18,
            font_size_px=12, color=BRAND_ACCENT, bold=True,
        )
        add_text(
            slide, f"annot-bullet-{n}", b,
            x_px=annot_x + 40, y_px=by, w_px=annot_w - 60, h_px=50,
            font_size_px=11, color=TEXT_DARK,
            emphasis_color=BRAND_PRIMARY,
        )
        by += 50

    # Source
    add_rect(slide, "annot-source-rule", annot_x + 22, body_top + body_h - 28, annot_w - 44, 1, CARD_BORDER)
    add_text(
        slide, "annot-source",
        "Source: pilot timesheets, n=12 consultants, 5 weeks.",
        x_px=annot_x + 22, y_px=body_top + body_h - 22, w_px=annot_w - 44, h_px=18,
        font_size_px=9, color=TEXT_FAINT, italic=True,
    )

    # --- Convergence (centered, not band) ---
    add_text(
        slide, "convergence",
        "When storyline lands first, <strong>rework stops being the job</strong> — the mix tells the story before the metrics do.",
        x_px=64, y_px=600, w_px=1280 - 128, h_px=30,
        font_size_px=12, color=BRAND_PRIMARY, italic=True, bold=False,
        align="center", anchor="middle",
        emphasis_color=BRAND_ACCENT,
    )

    add_footer(slide, page_num=67)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "67_stacked-bar-takeaway.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
