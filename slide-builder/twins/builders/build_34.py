"""
Builder for pattern 34: Cycle diagram.

SVG-driven cycle classified as picture-asset (per SHAPE-ROLES table).
Single chart-canvas placeholder; per-node text and callouts live inside
the SVG.

Source HTML: _pattern-library/34_cycle-diagram.html
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
        title="The Slide Lab loop — four phases, repeating with every deck.",
        subtitle="Think, argue, build, review — then start the next loop. The deck improves loop by loop, not page by page.",
        title_h=68,
        subtitle_h=22,
    )

    # Chart canvas placeholder
    canvas_left, canvas_top, canvas_w, canvas_h = 64, 205, 1280 - 128, 380
    add_rect(slide, "chart-canvas", x_px=canvas_left, y_px=canvas_top,
             w_px=canvas_w, h_px=canvas_h, fill_color=CHART_PLACEHOLDER_FILL)
    label_w = 240
    add_text(
        slide, "chart-canvas-label", "[ Cycle diagram ]",
        x_px=canvas_left + (canvas_w - label_w) // 2,
        y_px=canvas_top + canvas_h // 2 - 10,
        w_px=label_w, h_px=20,
        font_size_px=14, color=TEXT_FAINT, italic=True, align="center",
    )

    add_convergence(
        slide,
        "Every deck is one loop. The fastest improvement comes from completing more loops, not making longer ones.",
    )

    add_footer(slide, page_num=34)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "34_cycle-diagram.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
