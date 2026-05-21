"""
Builder for pattern 218: Scatter plot with quadrant zones.

SVG-heavy. The chart is placed as a chart-canvas placeholder rectangle.

Source HTML: _pattern-library/218_scatter-plot-quadrant-zones.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_MID, CARD_BG, CARD_BORDER,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Prioritize initiatives by <strong>impact vs. effort</strong>",
        subtitle="Quadrant analysis reveals quick wins and strategic investments across the portfolio",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # Chart-canvas placeholder (SVG decomposed into single picture-asset target)
    canvas_x, canvas_y = 48, 142
    canvas_w, canvas_h = 1184, 506
    canvas = add_rect(slide, "chart-canvas", canvas_x, canvas_y, canvas_w, canvas_h, CARD_BG)
    canvas.line.color.rgb = CARD_BORDER
    canvas.line.width = 9525

    # Placeholder label inside the canvas
    add_text(slide, "chart-canvas-label",
             "[ SVG scatter plot with quadrant zones — rendered at twin-gen time ]",
             x_px=canvas_x, y_px=canvas_y + canvas_h // 2 - 12, w_px=canvas_w, h_px=24,
             font_size_px=11, color=TEXT_MID, italic=True, align="center")

    add_footer(slide, page_num=218)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "218_scatter-plot-quadrant-zones.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
