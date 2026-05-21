"""
Builder for pattern 222: Capability Maturity Assessment Grid (5 dimensions x 5 levels).

Source HTML: _pattern-library/222_maturity-model-assessment.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_DARK, TEXT_MID,
    CARD_BG, CARD_BORDER, WHITE,
)
from pptx.dml.color import RGBColor

# Progressively darker column header shades (lv1 → lv5)
LVL_BGS = [
    RGBColor(0xED, 0xE7, 0xF6),
    RGBColor(0xD8, 0xC8, 0xF0),
    RGBColor(0xC3, 0xA8, 0xE6),
    RGBColor(0xA9, 0x7F, 0xD4),
    BRAND_PRIMARY,
]
LVL_TEXTS = [
    RGBColor(0x6B, 0x46, 0xA3),
    RGBColor(0x5C, 0x2D, 0x87),
    RGBColor(0x4A, 0x1E, 0x75),
    BRAND_PRIMARY,
    WHITE,
]
TARGET_BG = RGBColor(0xFB, 0xF5, 0xFF)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Capability <strong>Maturity</strong> Assessment Grid",
        subtitle="Current-state rating across five dimensions · target state identified per dimension",
        title_x=48, title_y=44, title_w=820, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # Legend top-right
    leg_x = 880
    leg_y = 64
    add_rect(slide, "legend-1-swatch", leg_x, leg_y + 4, 20, 10, BRAND_ACCENT)
    add_text(slide, "legend-1-label", "Current State",
             x_px=leg_x + 26, y_px=leg_y, w_px=120, h_px=18,
             font_size_px=9, color=TEXT_MID)
    add_rect(slide, "legend-2-swatch", leg_x, leg_y + 22, 20, 10, TARGET_BG)
    add_text(slide, "legend-2-label", "Target State",
             x_px=leg_x + 26, y_px=leg_y + 18, w_px=120, h_px=18,
             font_size_px=9, color=TEXT_MID)
    add_text(slide, "legend-3-label", "→ Progress direction",
             x_px=leg_x, y_px=leg_y + 36, w_px=200, h_px=18,
             font_size_px=9, color=BRAND_ACCENT, bold=True)

    # Grid: top:140, left:48, w=1184, h=508
    grid_top = 140
    grid_left = 48
    grid_w = 1184
    grid_h = 508
    row_header_w = 160
    cell_gap = 4
    col_header_h = 38

    # Cell layout
    cell_area_left = grid_left + row_header_w + cell_gap
    cell_area_w = grid_w - row_header_w - cell_gap
    col_w = (cell_area_w - 4 * cell_gap) // 5

    # Column headers
    for j in range(5):
        cx = cell_area_left + j * (col_w + cell_gap)
        add_rect(slide, f"level-{j+1}-header", cx, grid_top, col_w, col_header_h, LVL_BGS[j])
        add_text(slide, f"level-{j+1}-num", f"L{j+1}",
                 x_px=cx, y_px=grid_top + 4, w_px=col_w, h_px=12,
                 font_size_px=9, color=LVL_TEXTS[j], bold=True, align="center")
        names = ["Initial", "Managed", "Defined", "Quantified", "Optimizing"]
        add_text(slide, f"level-{j+1}-name", names[j],
                 x_px=cx, y_px=grid_top + 18, w_px=col_w, h_px=16,
                 font_size_px=11, color=LVL_TEXTS[j], bold=True, align="center")

    # Data rows
    rows_top = grid_top + col_header_h + cell_gap
    rows_h_area = grid_h - col_header_h - cell_gap
    row_h = (rows_h_area - 4 * cell_gap) // 5

    dimensions = [
        ("01", "Strategy & Governance", 2, 3,
         ["Ad hoc decisions; no formal policy",
          "Governance structure in place; reactive oversight",
          "Proactive governance; cross-function alignment",
          "Metrics-driven decisions; benchmarked",
          "Continuous strategy refinement; self-optimising"]),
        ("02", "Data & Analytics", 1, 2,
         ["Siloed data; manual exports",
          "Central data platform; basic dashboards",
          "Standardised data models; self-serve",
          "Predictive models in production; ML ops",
          "AI-driven insights; real-time data fabric"]),
        ("03", "Technology & Infra", 3, 4,
         ["Legacy monoliths; manual deployments",
          "Basic CI/CD pipeline; cloud migration started",
          "Cloud-native stack; automated pipelines",
          "FinOps optimised; zero-trust security",
          "Self-healing infra; autonomous scaling"]),
        ("04", "People & Culture", 2, 3,
         ["Change-resistant culture; skills gaps unquantified",
          "Training programmes launched; champions forming",
          "Digital fluency baseline met; agile embedded",
          "Skills marketplace live; mobility driving retention",
          "Learning culture institutionalised; AI augments"]),
        ("05", "Customer Experience", 3, 4,
         ["Inconsistent journeys; NPS not tracked",
          "NPS in place; basic segmentation",
          "Omni-channel orchestration; real-time feedback",
          "Personalisation at scale; CX linked to P&L",
          "Anticipatory CX; emotion AI deployed"]),
    ]

    for i, (num, name, current_lv, target_lv, cells) in enumerate(dimensions):
        n = i + 1
        ry = rows_top + i * (row_h + cell_gap)
        # Row header
        rh = add_rect(slide, f"dim-{n}-header", grid_left, ry, row_header_w, row_h, CARD_BG)
        rh.line.color.rgb = CARD_BORDER
        rh.line.width = 9525
        add_text(slide, f"dim-{n}-num", num,
                 x_px=grid_left + 10, y_px=ry + 8, w_px=row_header_w - 20, h_px=12,
                 font_size_px=8, color=BRAND_ACCENT, bold=True, uppercase=True)
        add_text(slide, f"dim-{n}-name", name,
                 x_px=grid_left + 10, y_px=ry + 20, w_px=row_header_w - 20, h_px=row_h - 26,
                 font_size_px=12, color=BRAND_PRIMARY, bold=True)
        # 5 cells
        for j in range(5):
            cx = cell_area_left + j * (col_w + cell_gap)
            lv = j + 1
            if lv == current_lv:
                cell = add_rect(slide, f"cell-{n}-{j+1}", cx, ry, col_w, row_h, BRAND_ACCENT)
                cell.line.color.rgb = BRAND_ACCENT
                cell.line.width = 9525
                tc = WHITE
                tbold = True
            elif lv == target_lv:
                cell = add_rect(slide, f"cell-{n}-{j+1}", cx, ry, col_w, row_h, TARGET_BG)
                cell.line.color.rgb = BRAND_ACCENT
                cell.line.width = 19050  # 2px dashed-ish
                tc = TEXT_DARK
                tbold = False
            else:
                cell = add_rect(slide, f"cell-{n}-{j+1}", cx, ry, col_w, row_h, CARD_BG)
                cell.line.color.rgb = CARD_BORDER
                cell.line.width = 9525
                tc = TEXT_MID
                tbold = False
            add_text(slide, f"cell-{n}-{j+1}-text", cells[j],
                     x_px=cx + 6, y_px=ry + 6, w_px=col_w - 12, h_px=row_h - 12,
                     font_size_px=10, color=tc, bold=tbold)

    add_footer(slide, page_num=222)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "222_maturity-model-assessment.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
