"""
Builder for pattern 29: Decision tree.

SVG-driven decision tree classified as picture-asset. Single chart-canvas
placeholder occupies the body zone; per-node text lives inside the SVG and
is NOT individually addressable. Convergence band stamped normally.

Source HTML: _pattern-library/29_decision-tree.html
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
        title="The routing decision — when to draft, when to coach first.",
        subtitle="One question at the top of every deck. Four outcomes at the bottom. No ambiguity in between.",
        title_h=68,
        subtitle_h=22,
    )

    # Chart canvas placeholder for picture-asset decision tree
    canvas_left, canvas_top, canvas_w, canvas_h = 64, 200, 1280 - 128, 400
    add_rect(slide, "chart-canvas", x_px=canvas_left, y_px=canvas_top,
             w_px=canvas_w, h_px=canvas_h, fill_color=CHART_PLACEHOLDER_FILL)
    label_w = 240
    add_text(
        slide, "chart-canvas-label", "[ Decision tree ]",
        x_px=canvas_left + (canvas_w - label_w) // 2,
        y_px=canvas_top + canvas_h // 2 - 10,
        w_px=label_w, h_px=20,
        font_size_px=14, color=TEXT_FAINT, italic=True, align="center",
    )

    add_convergence(
        slide,
        "Every deck starts with the same question. Most of them don't.",
    )

    add_footer(slide, page_num=29)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "29_decision-tree.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
