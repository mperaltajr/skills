"""
Builder for pattern 272: PESTLE grid (3x2 cards).

Source HTML: _pattern-library/272_pestle-grid.html

Layout: title + 3x2 grid of cells (Political, Economic, Social, Tech, Legal,
Environmental). Each cell has a coloured top band with letter + name +
impact pill, plus 3 bullets.

No legend at slide level — impact pills (High/Medium/Low) are inline per card.
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

# PESTLE band colors (distinct hues)
POL_C = RGBColor(0x5C, 0x2D, 0x87)
ECO_C = RGBColor(0xA1, 0x00, 0xFF)
SOC_C = RGBColor(0x6B, 0x46, 0xC1)
TEC_C = RGBColor(0x2D, 0x0A, 0x4E)
LEG_C = RGBColor(0x7E, 0x22, 0xCE)
ENV_C = RGBColor(0x86, 0x4E, 0xB8)

IMPACT_HIGH_BG = RGBColor(0xFE, 0xE2, 0xE2)
IMPACT_HIGH_FG = RGBColor(0xDC, 0x26, 0x26)
IMPACT_MED_BG = RGBColor(0xFE, 0xF3, 0xC7)
IMPACT_MED_FG = RGBColor(0x92, 0x40, 0x0E)
IMPACT_LOW_BG = RGBColor(0xDC, 0xFC, 0xE7)
IMPACT_LOW_FG = RGBColor(0x16, 0x65, 0x34)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="PESTLE analysis — <strong>macro forces shaping the strategic landscape.</strong>",
        subtitle="Six environmental dimensions assessed for impact on current and future operating context.",
    )

    # Body
    body_top = 230
    body_bottom = 632
    body_h = body_bottom - body_top
    left_x = 48
    right_x = 1280 - 48
    body_w = right_x - left_x

    # 3x2 grid
    cols = 3
    rows_n = 2
    col_gap = 12
    row_gap = 12
    card_w = (body_w - (cols - 1) * col_gap) // cols
    card_h = (body_h - (rows_n - 1) * row_gap) // rows_n

    cells = [
        ("P", "Political", POL_C, "high",
         ["Regulatory reform under new administration",
          "Trade policy uncertainty",
          "Government digitization agenda"]),
        ("E", "Economic", ECO_C, "high",
         ["Inflationary pressure on costs",
          "Interest rate normalisation",
          "FX volatility in key markets"]),
        ("S", "Social", SOC_C, "medium",
         ["Workforce skill gap in digital roles",
          "ESG expectations from stakeholders",
          "Remote work normalisation"]),
        ("T", "Technological", TEC_C, "high",
         ["GenAI adoption accelerating",
          "Cybersecurity threat landscape",
          "Cloud-first procurement mandates"]),
        ("L", "Legal", LEG_C, "medium",
         ["Data privacy regulation (GDPR v2)",
          "AI liability frameworks",
          "Employment law changes"]),
        ("E²", "Environmental", ENV_C, "low",
         ["Net zero commitments",
          "Supply chain sustainability",
          "Carbon reporting requirements"]),
    ]

    impact_styles = {
        "high": ("HIGH", IMPACT_HIGH_BG, IMPACT_HIGH_FG),
        "medium": ("MEDIUM", IMPACT_MED_BG, IMPACT_MED_FG),
        "low": ("LOW", IMPACT_LOW_BG, IMPACT_LOW_FG),
    }

    for idx, (letter, name, band_c, impact, bullets) in enumerate(cells):
        n = idx + 1
        r = idx // cols
        c = idx % cols
        cx = left_x + c * (card_w + col_gap)
        cy = body_top + r * (card_h + row_gap)
        # card bg
        card = add_rect(slide, f"cell-{n}", cx, cy, card_w, card_h, WHITE)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # top band
        band_h = 36
        add_rect(slide, f"cell-{n}-band", cx, cy, card_w, band_h, band_c)
        # letter
        add_text(slide, f"cell-{n}-letter", letter,
                 x_px=cx + 10, y_px=cy + 4, w_px=44, h_px=band_h - 8,
                 font_size_px=20, color=WHITE, bold=True, align="center", anchor="middle")
        # name
        add_text(slide, f"cell-{n}-name", name,
                 x_px=cx + 54, y_px=cy, w_px=card_w - 160, h_px=band_h,
                 font_size_px=13, color=WHITE, bold=True, anchor="middle")
        # impact pill
        label_text, pill_bg, pill_fg = impact_styles[impact]
        pill_w = 72
        pill_h = 20
        pill_x = cx + card_w - pill_w - 10
        pill_y = cy + (band_h - pill_h) // 2
        add_rect(slide, f"cell-{n}-impact-bg", pill_x, pill_y, pill_w, pill_h, pill_bg)
        add_text(slide, f"cell-{n}-impact", label_text,
                 x_px=pill_x, y_px=pill_y, w_px=pill_w, h_px=pill_h,
                 font_size_px=9, color=pill_fg, bold=True, align="center", anchor="middle",
                 letter_spacing_px=1)
        # bullets
        body_pad = 12
        bullet_top = cy + band_h + body_pad
        bullet_h = (card_h - band_h - body_pad * 2) // 3
        for bi, b in enumerate(bullets):
            iy = bullet_top + bi * bullet_h
            # marker
            add_rect(slide, f"cell-{n}-b{bi+1}-marker", cx + body_pad,
                     iy + 7, 4, 4, BRAND_ACCENT)
            add_text(slide, f"cell-{n}-b{bi+1}", b,
                     x_px=cx + body_pad + 12, y_px=iy, w_px=card_w - body_pad - 24, h_px=bullet_h - 4,
                     font_size_px=11, color=TEXT_DARK)

    add_footer(slide, page_num=272)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "272_pestle-grid.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
