"""
Builder for pattern 15: Org chart hierarchy.

Source HTML: _pattern-library/15_org-chart-hierarchy.html

Per SHAPE-ROLES.md classification: pattern 15 is treated as PICTURE-ASSET.
The SVG org chart is too irregular to decompose cleanly. We leave a
chart-canvas placeholder rectangle (the picture will be inserted later
when the SVG is rendered to PNG and added back).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    CARD_BG, CARD_BORDER, TEXT_FAINT,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Pilot governance — three leads, eight contributors.",
        subtitle="One sponsor sets direction. Three workstream leads own delivery. Contributors execute against a single rail.",
        title_h=68,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # Chart canvas placeholder — picture-asset treatment per SHAPE-ROLES
    canvas_top = 230
    canvas_left = 64
    canvas_w = 1280 - 128
    canvas_h = 360
    canvas = add_rect(slide, "chart-canvas", canvas_left, canvas_top, canvas_w, canvas_h, CARD_BG)
    canvas.line.color.rgb = CARD_BORDER
    canvas.line.width = 9525
    add_text(
        slide, "chart-canvas-placeholder",
        "[ Org chart — picture-asset; SVG renders here ]",
        x_px=canvas_left, y_px=canvas_top, w_px=canvas_w, h_px=canvas_h,
        font_size_px=13, color=TEXT_FAINT, italic=True,
        align="center", anchor="middle",
    )

    add_convergence(
        slide,
        "Decisions escalate up the rail; signoffs come back the same way — no side channels.",
    )

    add_footer(slide, page_num=15)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "15_org-chart-hierarchy.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
