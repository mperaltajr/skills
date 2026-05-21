"""
Builder for pattern 235: Three Horizons growth curves (chart-canvas + 3 annot cards).

Source HTML: _pattern-library/235_three-horizons-growth-curves.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, TEXT_DARK, TEXT_MID,
    CARD_BG, CARD_BORDER,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Managing the Portfolio Across <strong>Three Horizons</strong>",
        subtitle="Balancing today's core, emerging growth, and future options to sustain long-term value creation",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # Body: top:132, left:48, right:48, bottom 64
    body_top = 132
    body_h = 524
    gap = 24
    panel_w = 248
    chart_w = 1184 - panel_w - gap

    # Chart-canvas (SVG)
    canvas = add_rect(slide, "chart-canvas", 48, body_top, chart_w, body_h, CARD_BG)
    canvas.line.color.rgb = CARD_BORDER
    canvas.line.width = 9525
    add_text(slide, "chart-canvas-label",
             "[ SVG growth-curve chart: H1/H2/H3 horizons — rendered at twin-gen time ]",
             x_px=48, y_px=body_top + body_h // 2 - 12, w_px=chart_w, h_px=24,
             font_size_px=11, color=TEXT_MID, italic=True, align="center")

    # 3 annot cards
    panel_x = 48 + chart_w + gap
    card_h = (body_h - 2 * 10) // 3
    horizons = [
        ("H1 — Core Business", BRAND_PRIMARY,
         "Defend and extend the existing business. Maximize near-term profitability while managing decline.",
         ["Cost optimization & margin improvement",
          "Customer retention programs",
          "Core product enhancements",
          "Operational excellence initiatives"]),
        ("H2 — Emerging Growth", BRAND_PRIMARY_MID,
         "Scale up businesses with proven models. Bridge from core to future; requires active investment.",
         ["Adjacent market expansion",
          "New channel development",
          "Platform & ecosystem plays",
          "Strategic acquisitions / JVs"]),
        ("H3 — Future Options", BRAND_ACCENT,
         "Seed tomorrow's growth engines. High uncertainty; small bets that become tomorrow's H2s.",
         ["Emerging technology pilots",
          "New business model experiments",
          "Venture / incubator investments",
          "Disruptive innovation programs"]),
    ]
    for i, (name, color, desc, bullets) in enumerate(horizons):
        n = i + 1
        cy = body_top + i * (card_h + 10)
        card = add_rect(slide, f"horizon-{n}-card", panel_x, cy, panel_w, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Left accent bar (4px)
        add_rect(slide, f"horizon-{n}-bar", panel_x, cy, 4, card_h, color)
        # Title
        add_text(slide, f"horizon-{n}-name", name,
                 x_px=panel_x + 12, y_px=cy + 10, w_px=panel_w - 20, h_px=16,
                 font_size_px=11, color=color, bold=True, uppercase=True)
        # Desc
        add_text(slide, f"horizon-{n}-desc", desc,
                 x_px=panel_x + 12, y_px=cy + 28, w_px=panel_w - 20, h_px=38,
                 font_size_px=10, color=TEXT_MID)
        # Bullets
        body_text = "\n".join(f"· {b}" for b in bullets)
        add_text(slide, f"horizon-{n}-body", body_text,
                 x_px=panel_x + 12, y_px=cy + 68, w_px=panel_w - 20, h_px=card_h - 76,
                 font_size_px=10, color=TEXT_DARK)

    add_footer(slide, page_num=235)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "235_three-horizons-growth-curves.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
