"""
Builder for pattern 147: Logic model — 5-column flow (Inputs → Activities → Outputs → Outcomes → Impact).

Source HTML: _pattern-library/147_logic-model.html
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

ASSUMP_BG = RGBColor(0xFF, 0xFD, 0xE7)
ASSUMP_BORDER = RGBColor(0xB8, 0x86, 0x0B)
ASSUMP_TXT = RGBColor(0x5D, 0x4A, 0x00)
EXT_BG = RGBColor(0xEF, 0xF6, 0xFF)
EXT_BORDER = RGBColor(0x25, 0x63, 0xEB)
EXT_TXT = RGBColor(0x1E, 0x3A, 0x8A)

COL_HEAD_COLORS = {
    1: TEXT_MID,
    2: RGBColor(0x7C, 0x3F, 0xA8),
    3: BRAND_ACCENT,
    4: BRAND_PRIMARY_MID,
    5: BRAND_PRIMARY,
}
COL_BODY_COLORS = {
    1: CARD_BG,
    2: RGBColor(0xF2, 0xE8, 0xFA),
    3: RGBColor(0xEA, 0xD2, 0xFD),
    4: RGBColor(0xE3, 0xDA, 0xEE),
    5: BRAND_PRIMARY,
}


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="<strong>Logic model supports program investment case</strong> — assumptions validated by year-1 pilot data",
        subtitle="Digital Skills Training Initiative — inputs, activities, and outputs mapped to outcomes and long-term workforce impact",
        title_x=48, title_w=1100, title_h=48,
        subtitle_h=20, brand_rule_w=48,
    )

    # Content zone: top:140 left:48 right:48 bottom:36
    cz_x = 48
    cz_y = 140
    cz_w = 1280 - 96
    cz_h = 720 - 36 - cz_y

    # Assumptions row (top, dashed yellow)
    assump_h = 40
    add_rect(slide, "assumptions-bg", cz_x, cz_y, cz_w, assump_h, ASSUMP_BG)
    add_text(slide, "assumptions-label", "ASSUMPTIONS",
             x_px=cz_x + 14, y_px=cz_y + 12, w_px=100, h_px=16,
             font_size_px=9, color=ASSUMP_TXT, bold=True, uppercase=True)
    add_text(slide, "assumptions-text",
             "Participants have internet access; employers value digital skills; training completion leads to employment",
             x_px=cz_x + 124, y_px=cz_y + 12, w_px=cz_w - 138, h_px=18,
             font_size_px=10, color=ASSUMP_TXT, italic=True)

    # Outcomes group label (above col-4 and col-5)
    grp_y = cz_y + assump_h + 4
    grp_w = int(cz_w * 0.4) - 12
    grp_x = cz_x + cz_w - grp_w
    add_text(slide, "outcomes-group-label", "OUTCOMES",
             x_px=grp_x, y_px=grp_y, w_px=grp_w, h_px=14,
             font_size_px=9, color=BRAND_PRIMARY_MID, bold=True, uppercase=True, align="center")

    # Main columns
    main_y = grp_y + 18
    main_h = cz_h - (assump_h + 18 + 60 + 40)  # leave room for external + theory
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
        # Header
        add_rect(slide, f"col-{key}-head", cx, main_y, col_w, head_h, COL_HEAD_COLORS[n])
        add_text(slide, f"col-{key}-eyebrow", eyebrow,
                 x_px=cx + 10, y_px=main_y + 4, w_px=col_w - 20, h_px=12,
                 font_size_px=8, color=WHITE, bold=True, uppercase=True)
        add_text(slide, f"col-{key}-name", name,
                 x_px=cx + 10, y_px=main_y + 14, w_px=col_w - 20, h_px=14,
                 font_size_px=12, color=WHITE, bold=True)
        # Body
        body_y = main_y + head_h
        body_h = main_h - head_h
        text_color = WHITE if n == 5 else TEXT_DARK
        add_rect(slide, f"col-{key}-body", cx, body_y, col_w, body_h, COL_BODY_COLORS[n])
        items_text = "\n".join("· " + it for it in items)
        add_text(slide, f"col-{key}-body-text", items_text,
                 x_px=cx + 10, y_px=body_y + 8, w_px=col_w - 20, h_px=body_h - 16,
                 font_size_px=10, color=text_color)

        # Arrow between columns
        if i < 4:
            ax = cx + col_w + col_gap // 2 - 4
            add_text(slide, f"col-arrow-{n}", "▶",
                     x_px=ax, y_px=main_y + main_h // 2 - 8,
                     w_px=14, h_px=16,
                     font_size_px=14, color=BRAND_ACCENT, align="center")

    # External factors box (blue)
    ext_y = main_y + main_h + 6
    add_rect(slide, "external-bg", cz_x, ext_y, cz_w, 34, EXT_BG)
    add_text(slide, "external-label", "EXTERNAL FACTORS",
             x_px=cz_x + 14, y_px=ext_y + 9, w_px=130, h_px=14,
             font_size_px=9, color=EXT_BORDER, bold=True, uppercase=True)
    add_text(slide, "external-text",
             "Economic conditions, employer hiring freezes, policy changes",
             x_px=cz_x + 150, y_px=ext_y + 9, w_px=cz_w - 164, h_px=16,
             font_size_px=10, color=EXT_TXT, italic=True)

    # Convergence (program theory) strip
    conv_y = ext_y + 40
    add_rect(slide, "convergence-bg", cz_x, conv_y, cz_w, 42, BRAND_PRIMARY)
    add_text(slide, "convergence-mark", "PROGRAM THEORY",
             x_px=cz_x + 14, y_px=conv_y + 13, w_px=110, h_px=14,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "convergence",
             "When funded inputs enable structured bootcamp activities, certified graduates and employer partnerships "
             "drive workforce mobility — closing the digital skills gap and sustaining industry competitiveness over time.",
             x_px=cz_x + 138, y_px=conv_y, w_px=cz_w - 152, h_px=42,
             font_size_px=11, color=WHITE, italic=True, anchor="middle")

    add_footer(slide, page_num=147)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "147_logic-model.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
