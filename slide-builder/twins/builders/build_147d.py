"""
Builder for pattern 147d: Logic model — 5-column flow — dark.

Source HTML: _pattern-library/147_logic-model-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

ASSUMP_BG = RGBColor(0x57, 0x40, 0x12)
ASSUMP_TXT = RGBColor(0xFC, 0xD3, 0x4D)
EXT_BG = RGBColor(0x1F, 0x2D, 0x5C)
EXT_TXT = RGBColor(0x93, 0xC5, 0xFD)

COL_HEAD_COLORS = {
    1: BRAND_PRIMARY_MID,
    2: RGBColor(0x7C, 0x3F, 0xA8),
    3: BRAND_ACCENT,
    4: BRAND_ACCENT_SOFT,
    5: BRAND_PRIMARY,
}
COL_BODY_COLORS = {
    1: CARD_BG_DARK,
    2: CARD_BG_DARK,
    3: CARD_BG_DARK,
    4: CARD_BG_DARK,
    5: BRAND_PRIMARY_MID,
}


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Canonical chrome
    add_text(slide, "title",
             "<strong>Logic model supports program investment case</strong> — assumptions validated by year-1 pilot data",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Digital Skills Training Initiative — inputs, activities, and outputs mapped to outcomes and long-term impact",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Content zone
    cz_x = 48
    cz_y = 220
    cz_w = 1280 - 96
    cz_h = 664 - cz_y

    # Assumptions row
    assump_h = 36
    add_rect(slide, "assumptions-bg", cz_x, cz_y, cz_w, assump_h, ASSUMP_BG)
    add_text(slide, "assumptions-label", "ASSUMPTIONS",
             x_px=cz_x + 14, y_px=cz_y + 10, w_px=100, h_px=16,
             font_size_px=9, color=ASSUMP_TXT, bold=True, uppercase=True)
    add_text(slide, "assumptions-text",
             "Participants have internet access; employers value digital skills; training completion leads to employment",
             x_px=cz_x + 124, y_px=cz_y + 10, w_px=cz_w - 138, h_px=18,
             font_size_px=10, color=ASSUMP_TXT, italic=True)

    # Outcomes group label
    grp_y = cz_y + assump_h + 4
    grp_w = int(cz_w * 0.4) - 12
    grp_x = cz_x + cz_w - grp_w
    add_text(slide, "outcomes-group-label", "OUTCOMES",
             x_px=grp_x, y_px=grp_y, w_px=grp_w, h_px=14,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True, align="center")

    # Main columns
    main_y = grp_y + 18
    main_h = cz_h - (assump_h + 18 + 60 + 36)
    col_gap = 12
    col_w = (cz_w - 4 * col_gap) // 5
    col_titles = [
        ("STAGE 1", "INPUTS",     "input",     ["Budget $2.4M", "12 trainers", "Curriculum", "Partner employers"]),
        ("STAGE 2", "ACTIVITIES", "activity",  ["8-week bootcamp", "Mentorship", "Job placement support", "Employer partnerships"]),
        ("STAGE 3", "OUTPUTS",    "output",    ["240 graduates/yr", "95% completion rate", "18 employer partners", "Certifications issued"]),
        ("SHORT-TERM", "OUTCOMES", "shortterm",["Digital employment skills", "Job-ready graduates", "Employer relationships built"]),
        ("LONG-TERM", "IMPACT",    "longterm", ["Economic mobility", "Workforce gap closed", "Industry competitiveness"]),
    ]
    head_h = 30
    for i, (eyebrow, name, key, items) in enumerate(col_titles):
        n = i + 1
        cx = cz_x + i * (col_w + col_gap)
        add_rect(slide, f"col-{key}-head", cx, main_y, col_w, head_h, COL_HEAD_COLORS[n])
        add_text(slide, f"col-{key}-eyebrow", eyebrow,
                 x_px=cx + 10, y_px=main_y + 4, w_px=col_w - 20, h_px=12,
                 font_size_px=8, color=WHITE, bold=True, uppercase=True)
        add_text(slide, f"col-{key}-name", name,
                 x_px=cx + 10, y_px=main_y + 14, w_px=col_w - 20, h_px=14,
                 font_size_px=12, color=WHITE, bold=True)
        body_y = main_y + head_h
        body_h = main_h - head_h
        text_color = WHITE
        add_rect(slide, f"col-{key}-body", cx, body_y, col_w, body_h, COL_BODY_COLORS[n])
        items_text = "\n".join("· " + it for it in items)
        add_text(slide, f"col-{key}-body-text", items_text,
                 x_px=cx + 10, y_px=body_y + 8, w_px=col_w - 20, h_px=body_h - 16,
                 font_size_px=10, color=text_color)
        if i < 4:
            ax = cx + col_w + col_gap // 2 - 4
            add_text(slide, f"col-arrow-{n}", "▶",
                     x_px=ax, y_px=main_y + main_h // 2 - 8,
                     w_px=14, h_px=16,
                     font_size_px=14, color=BRAND_ACCENT, align="center")

    # External factors
    ext_y = main_y + main_h + 6
    add_rect(slide, "external-bg", cz_x, ext_y, cz_w, 30, EXT_BG)
    add_text(slide, "external-label", "EXTERNAL FACTORS",
             x_px=cz_x + 14, y_px=ext_y + 7, w_px=130, h_px=14,
             font_size_px=9, color=EXT_TXT, bold=True, uppercase=True)
    add_text(slide, "external-text",
             "Economic conditions, employer hiring freezes, policy changes",
             x_px=cz_x + 150, y_px=ext_y + 7, w_px=cz_w - 164, h_px=16,
             font_size_px=10, color=EXT_TXT, italic=True)

    # Convergence strip
    conv_y = ext_y + 36
    add_rect(slide, "convergence-bg", cz_x, conv_y, cz_w, 38, BRAND_ACCENT)
    add_text(slide, "convergence-mark", "PROGRAM THEORY",
             x_px=cz_x + 14, y_px=conv_y + 12, w_px=110, h_px=14,
             font_size_px=9, color=WHITE, bold=True, uppercase=True)
    add_text(slide, "convergence",
             "When funded inputs enable structured bootcamp activities, certified graduates and employer partnerships "
             "drive workforce mobility — closing the digital skills gap.",
             x_px=cz_x + 138, y_px=conv_y, w_px=cz_w - 152, h_px=38,
             font_size_px=11, color=WHITE, italic=True, anchor="middle")

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "147",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "147d_logic-model.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
