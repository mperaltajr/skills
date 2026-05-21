"""
Builder for pattern 225: Competitive Positioning Map (SVG chart + side annot panel).

SVG bubble chart treated as chart-canvas placeholder.
Right-side panel uses annot-* canonical vocabulary.

Source HTML: _pattern-library/225_competitive-positioning-map.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT,
    CARD_BG, CARD_BORDER, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="We hold the <strong>strongest position</strong> on breadth and leadership",
        subtitle="Competitive landscape mapped by capability breadth vs. market authority — 2025 snapshot",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # Content: top:130, left:48, right:48, bottom 64
    content_top = 130
    panel_w = 240
    chart_w = 1184 - panel_w - 20
    chart_x = 48

    # Chart-canvas placeholder
    canvas = add_rect(slide, "chart-canvas", chart_x, content_top, chart_w, 484, CARD_BG)
    canvas.line.color.rgb = CARD_BORDER
    canvas.line.width = 9525
    add_text(slide, "chart-canvas-label",
             "[ SVG bubble chart: competitive positioning — rendered at twin-gen time ]",
             x_px=chart_x, y_px=content_top + 240, w_px=chart_w, h_px=24,
             font_size_px=11, color=TEXT_MID, italic=True, align="center")
    add_text(slide, "chart-source",
             "Source: Gartner Magic Quadrant 2025 + internal analysis · Bubble size = estimated revenue",
             x_px=chart_x, y_px=content_top + 484 + 4, w_px=chart_w, h_px=16,
             font_size_px=9, color=TEXT_FAINT)

    # Right side panel
    panel_x = 48 + chart_w + 20
    panel = add_rect(slide, "annot-panel", panel_x, content_top, panel_w, 484, CARD_BG)
    panel.line.color.rgb = CARD_BORDER
    panel.line.width = 9525

    add_text(slide, "annot-header", "Our Advantage",
             x_px=panel_x + 16, y_px=content_top + 16, w_px=panel_w - 32, h_px=18,
             font_size_px=11, color=BRAND_PRIMARY, bold=True, uppercase=True)
    add_rect(slide, "annot-header-rule",
             panel_x + 16, content_top + 38, panel_w - 32, 2, BRAND_ACCENT)

    items = [
        ("Unmatched End-to-End Scope",
         "We cover strategy through execution across all verticals — no competitor matches our full-stack breadth."),
        ("Established Market Authority",
         "17 consecutive years as a Gartner Leader; recognized brand in 50+ markets with anchor clients."),
        ("Proprietary AI Platform",
         "SyntheticEdge AI platform accelerates delivery 2× vs. next-best competitor with embedded IP."),
    ]
    item_y = content_top + 56
    item_h = 120
    for i, (label, body) in enumerate(items):
        n = i + 1
        iy = item_y + i * item_h
        # Numbered marker
        add_rect(slide, f"annot-{n}-marker", panel_x + 16, iy + 4, 20, 20, BRAND_ACCENT)
        add_text(slide, f"annot-{n}-marker-text", str(n),
                 x_px=panel_x + 16, y_px=iy + 4, w_px=20, h_px=20,
                 font_size_px=9, color=WHITE, bold=True, align="center", anchor="middle")
        add_text(slide, f"annot-{n}-label", label,
                 x_px=panel_x + 44, y_px=iy + 2, w_px=panel_w - 60, h_px=28,
                 font_size_px=11, color=BRAND_PRIMARY, bold=True)
        add_text(slide, f"annot-{n}-body", body,
                 x_px=panel_x + 44, y_px=iy + 30, w_px=panel_w - 60, h_px=item_h - 36,
                 font_size_px=10, color=TEXT_MID)

    add_text(slide, "annot-footer",
             "Competitors benchmarked on publicly available capability inventories and analyst ratings.",
             x_px=panel_x + 16, y_px=content_top + 484 - 40, w_px=panel_w - 32, h_px=36,
             font_size_px=9, color=TEXT_FAINT, italic=True)

    add_footer(slide, page_num=225)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "225_competitive-positioning-map.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
