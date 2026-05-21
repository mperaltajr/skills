"""
Builder for pattern 230: Org chart flat / wide (picture-asset).

Org chart is treated as a chart-canvas (picture rendered from HTML/SVG at twin-gen time).

Source HTML: _pattern-library/230_org-flat-wide.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    TEXT_MID, CARD_BG, CARD_BORDER,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Organizational Structure — <strong>Flat / Wide</strong>",
        subtitle="Single layer of direct reports beneath the executive lead — clarity at a glance",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    canvas_x, canvas_y = 48, 138
    canvas_w, canvas_h = 1184, 520
    canvas = add_rect(slide, "chart-canvas", canvas_x, canvas_y, canvas_w, canvas_h, CARD_BG)
    canvas.line.color.rgb = CARD_BORDER
    canvas.line.width = 9525
    add_text(slide, "chart-canvas-label",
             "[ Org chart: 1 root + 6 direct reports + 4 L2 nodes — rendered at twin-gen time ]",
             x_px=canvas_x, y_px=canvas_y + canvas_h // 2 - 12, w_px=canvas_w, h_px=24,
             font_size_px=11, color=TEXT_MID, italic=True, align="center")

    add_footer(slide, page_num=230)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "230_org-flat-wide.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
