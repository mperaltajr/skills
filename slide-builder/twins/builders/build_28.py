"""
Builder for pattern 28: Vertical timeline.

SVG-driven timeline classified as picture-asset (per SHAPE-ROLES table).
We use a single chart-canvas placeholder rectangle for the SVG timeline
geometry; the per-event labels are stamped with pattern-local IDs since
the HTML has them adjacent (not inside) the SVG.

Source HTML: _pattern-library/28_vertical-timeline.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT,
    CARD_BORDER, TEXT_DARK, TEXT_MID,
)
from pptx.dml.color import RGBColor

CHART_PLACEHOLDER_FILL = RGBColor(0xF4, 0xF4, 0xF6)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="How Slide Lab got here — six course corrections.",
        subtitle="Each step was a course-correction. The next one is yours to choose.",
        title_h=68,
        subtitle_h=22,
    )

    # Timeline canvas placeholder — picture-asset treatment (single chart-canvas)
    chart_left = 64
    chart_top = 200
    chart_w = 1280 - 128
    chart_h = 460
    add_rect(slide, "chart-canvas", chart_left, chart_top, chart_w, chart_h, CHART_PLACEHOLDER_FILL)

    # Event labels — left column at center-102, right column at center+102
    center_x = chart_left + chart_w // 2  # 640
    label_w = 340
    # row top y values (matching HTML row positions, offset by chart_top).
    # Bottom node lifted (425 -> 390) so the full TODAY circle + halo (r=18) plus
    # the 3-line description block clear the bottom edge of the chart canvas.
    row_y_offsets = [30, 112, 194, 276, 358, 390]

    events = [
        ("Q2 2025", "Spark",
         "Notice the pattern: senior consultants escape the deck-bloat trap; juniors get crushed by it.",
         "left"),
        ("Q3 2025", "Hypothesis",
         "The fix isn't training. It's a structural tool that enforces the discipline.",
         "right"),
        ("Q4 2025", "Prototype V1",
         "First HTML/Playwright build of Slide Lab. Twelve decks tested internally.",
         "left"),
        ("Q1 2026", "V2 Architecture",
         "Skeleton-first pipeline. Speed gains, but visual quality regressed.",
         "right"),
        ("Q2 2026", "V2.5 Hybrid",
         "Pattern library curation. Skeletons + HTML treatments. Editorial chrome restored.",
         "left"),
        ("Today", "Pilot",
         "Four-week pilot with the client strategy practice. The data speaks.",
         "right"),
    ]

    for i, (date, title_text, desc, side) in enumerate(events):
        n = i + 1
        is_today = (n == 6)
        row_y = chart_top + row_y_offsets[i]
        # vertical center of label = row_y; we anchor block top at row_y - 30
        block_y = row_y - 30
        if side == "left":
            x = center_x - 102 - label_w
            align = "right"
        else:
            x = center_x + 102
            align = "left"

        date_size = 13 if is_today else 12
        title_size = 18 if is_today else 15
        date_color = BRAND_ACCENT if is_today else BRAND_PRIMARY

        add_text(
            slide, f"event-{n}-date", date,
            x_px=x, y_px=block_y, w_px=label_w, h_px=16,
            font_size_px=date_size, color=date_color, bold=True,
            uppercase=True, letter_spacing_px=1.5, align=align,
        )
        add_text(
            slide, f"event-{n}-title", title_text,
            x_px=x, y_px=block_y + 18, w_px=label_w, h_px=22,
            font_size_px=title_size, color=BRAND_PRIMARY if is_today else TEXT_DARK,
            bold=True, align=align,
        )
        add_text(
            slide, f"event-{n}-desc", desc,
            x_px=x, y_px=block_y + 40, w_px=label_w, h_px=40,
            font_size_px=12, color=TEXT_DARK if is_today else TEXT_MID,
            align=align,
        )

    add_footer(slide, page_num=28)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "28_vertical-timeline.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
