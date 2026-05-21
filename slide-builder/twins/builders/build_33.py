"""
Builder for pattern 33: Fishbone root cause.

SVG-driven fishbone classified as picture-asset (per SHAPE-ROLES table).
Single chart-canvas placeholder; per-category text is inside the SVG and
not individually addressable.

Source HTML: _pattern-library/33_fishbone-root-cause.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    TEXT_FAINT,
)
from pptx.dml.color import RGBColor

CHART_PLACEHOLDER_FILL = RGBColor(0xF4, 0xF4, 0xF6)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Why decks degrade — six categories of root cause.",
        subtitle="Six categories of root causes. The one we own is the structural process — that's where we can act.",
        title_h=68,
        subtitle_h=22,
    )

    # Chart canvas placeholder
    canvas_left, canvas_top, canvas_w, canvas_h = 64, 200, 1280 - 128, 380
    add_rect(slide, "chart-canvas", x_px=canvas_left, y_px=canvas_top,
             w_px=canvas_w, h_px=canvas_h, fill_color=CHART_PLACEHOLDER_FILL)
    label_w = 240
    add_text(
        slide, "chart-canvas-label", "[ Fishbone diagram ]",
        x_px=canvas_left + (canvas_w - label_w) // 2,
        y_px=canvas_top + canvas_h // 2 - 10,
        w_px=label_w, h_px=20,
        font_size_px=14, color=TEXT_FAINT, italic=True, align="center",
    )

    add_convergence(
        slide,
        "Six categories of root causes. The one we own is the structural process — that's where we can act.",
    )

    add_footer(slide, page_num=33)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "33_fishbone-root-cause.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
