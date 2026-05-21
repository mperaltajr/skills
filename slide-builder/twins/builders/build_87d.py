"""
Builder for pattern 87d: Workstream × phase matrix — dark variant.

Source HTML: _pattern-library/87_workstream-phase-matrix-dark.html
Light template: twins/builders/build_87.py
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
CURRENT_PHASE_TINT_DARK = RGBColor(0x4D, 0x2C, 0x73)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(slide, "eyebrow", "Workstreams × phases",
             x_px=48, y_px=20, w_px=400, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "title",
             "Four workstreams × four phases — sixteen plays.",
             x_px=48, y_px=42, w_px=820, h_px=60,
             font_size_px=24, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Each cell names the play that workstream runs in that phase. Read down for a workstream's arc; across for a phase end-to-end.",
             x_px=48, y_px=108, w_px=820, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 134, 56, 3, BRAND_ACCENT_SOFT)

    # Phase legend
    leg_w = 280
    leg_h = 40
    leg_x = 1216 - leg_w
    leg_y = 160
    leg = add_rect(slide, "phase-legend", leg_x, leg_y, leg_w, leg_h, CARD_BG_DARK)
    leg.line.color.rgb = CARD_BORDER_DARK
    leg.line.width = 9525
    add_text(slide, "legend-title", "CURRENT PHASE",
             x_px=leg_x + 10, y_px=leg_y + 13, w_px=110, h_px=14,
             font_size_px=9, color=TEXT_ON_DARK_MID, bold=True, uppercase=True)
    add_rect(slide, "legend-1-swatch", leg_x + 130, leg_y + 14, 22, 14, CURRENT_PHASE_TINT_DARK)
    swatch_border = add_rect(slide, "legend-1-swatch-border", leg_x + 130, leg_y + 14, 22, 14, CURRENT_PHASE_TINT_DARK)
    swatch_border.line.color.rgb = BRAND_ACCENT_SOFT
    swatch_border.line.width = 9525
    add_text(slide, "legend-1-label", "Pilot phase",
             x_px=leg_x + 160, y_px=leg_y + 13, w_px=110, h_px=14,
             font_size_px=10, color=WHITE, bold=True)

    # Matrix
    mtx_left = 48
    mtx_top = 220
    mtx_w = 1280 - 96
    ws_col_w = int(mtx_w * 0.16)
    phase_col_w = (mtx_w - ws_col_w) // 4
    cols_x = [mtx_left]
    cols_x.append(mtx_left + ws_col_w)
    for k in range(3):
        cols_x.append(cols_x[-1] + phase_col_w)

    headers = ["Workstream", "Setup", "Pilot", "Scale", "Sustain"]
    phase_nums = [None, "Phase 1", "Phase 2", "Phase 3", "Phase 4"]
    current_col = 2
    header_h = 50
    add_rect(slide, "table-header-bg", mtx_left, mtx_top, mtx_w, header_h, BRAND_PRIMARY_MID)
    add_rect(slide, "current-phase-accent",
             cols_x[current_col], mtx_top, phase_col_w, 3, BRAND_ACCENT)

    for i, (h, p) in enumerate(zip(headers, phase_nums)):
        col_x = cols_x[i]
        col_width = ws_col_w if i == 0 else phase_col_w
        align = "left" if i == 0 else "center"
        add_text(slide, f"table-col-{i+1}-header", h,
                 x_px=col_x + 8, y_px=mtx_top + 10, w_px=col_width - 16, h_px=18,
                 font_size_px=9, color=WHITE, bold=True, uppercase=True, align=align)
        if p:
            add_text(slide, f"table-col-{i+1}-phase-num", p,
                     x_px=col_x + 8, y_px=mtx_top + 28, w_px=col_width - 16, h_px=14,
                     font_size_px=8, color=BRAND_ACCENT_SOFT, uppercase=True, align=align)

    workstreams = [
        ("WS 1", "Strategy", [
            ["Define success metrics", "Align on scope & guardrails"],
            ["Weekly check-ins", "Steer mid-pilot pivots"],
            ["Quarterly review", "Reset targets per practice"],
            ["BAU governance", "Annual strategy refresh"],
        ]),
        ("WS 2", "Build", [
            ["Tool provisioning", "Skeleton library v1"],
            ["Live pattern library use", "Rapid iteration on gaps"],
            ["HTML → PPTX engine", "Self-serve onboarding"],
            ["Pattern contributions", "Quarterly release cadence"],
        ]),
        ("WS 3", "Coach", [
            ["Onboarding plan", "Recruit pilot consultants"],
            ["Daily coaching", "Office hours & pairing"],
            ["Coach certification", "Train-the-trainer rollout"],
            ["Champion community", "Peer review rituals"],
        ]),
        ("WS 4", "Measure", [
            ["Baseline capture", "Instrument the workflow"],
            ["Weekly scorecard", "Qualitative feedback loop"],
            ["Cross-practice scorecard", "Benchmark vs. baseline"],
            ["Annual ROI", "Value story refresh"],
        ]),
    ]
    row_h = 72
    body_top = mtx_top + header_h
    for ri, (ws_num, ws_name, cells) in enumerate(workstreams):
        n = ri + 1
        ry = body_top + ri * row_h

        ws_bg = add_rect(slide, f"table-row-{n}-cell-1",
                         cols_x[0], ry, ws_col_w, row_h, CARD_BG_DARK)
        ws_bg.line.color.rgb = CARD_BORDER_DARK
        ws_bg.line.width = 9525
        add_text(slide, f"table-row-{n}-num", ws_num,
                 x_px=cols_x[0] + 12, y_px=ry + 12, w_px=ws_col_w - 24, h_px=14,
                 font_size_px=8, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
        add_text(slide, f"table-row-{n}-cell-1-name", ws_name,
                 x_px=cols_x[0] + 12, y_px=ry + 30, w_px=ws_col_w - 24, h_px=20,
                 font_size_px=12, color=WHITE, bold=True)

        for ci, items in enumerate(cells):
            phase_idx = ci + 1
            col_x = cols_x[phase_idx]
            is_current = phase_idx == current_col
            cell_bg = CURRENT_PHASE_TINT_DARK if is_current else BRAND_PRIMARY
            cell = add_rect(slide, f"table-row-{n}-cell-{phase_idx + 1}",
                            col_x, ry, phase_col_w, row_h, cell_bg)
            cell.line.color.rgb = CARD_BORDER_DARK
            cell.line.width = 9525

            for j, item in enumerate(items):
                iy = ry + 12 + j * 22
                add_rect(slide, f"table-row-{n}-cell-{phase_idx + 1}-bullet-{j+1}-dot",
                         col_x + 10, iy + 7, 4, 4, BRAND_ACCENT_SOFT)
                add_text(slide, f"table-row-{n}-cell-{phase_idx + 1}-item-{j+1}", item,
                         x_px=col_x + 20, y_px=iy, w_px=phase_col_w - 32, h_px=20,
                         font_size_px=10, color=WHITE)

    total_h = header_h + row_h * len(workstreams)
    add_rect(slide, "matrix-border-top", mtx_left, mtx_top, mtx_w, 1, CARD_BORDER_DARK)
    add_rect(slide, "matrix-border-bottom", mtx_left, mtx_top + total_h, mtx_w, 1, CARD_BORDER_DARK)
    add_rect(slide, "matrix-border-left", mtx_left, mtx_top, 1, total_h, CARD_BORDER_DARK)
    add_rect(slide, "matrix-border-right", mtx_left + mtx_w - 1, mtx_top, 1, total_h, CARD_BORDER_DARK)

    # Convergence
    conv_y = 720 - 56 - 56
    conv_h = 52
    conv_w = 1280 - 96
    add_rect(slide, "convergence-bg", 48, conv_y, conv_w, conv_h, BRAND_PRIMARY_MID)
    add_text(slide, "convergence-mark", "SO WHAT",
             x_px=48 + 14, y_px=conv_y + 16, w_px=80, h_px=20,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center",
             bg_fill=BRAND_PRIMARY, padding_px=(3, 6, 3, 6))
    add_text(slide, "convergence",
             "Sixteen plays, one program. Every workstream owes the Pilot column its full attention this quarter — Scale and Sustain only land if Phase 2 proves the model.",
             x_px=48 + 110, y_px=conv_y, w_px=conv_w - 130, h_px=conv_h,
             font_size_px=13, color=WHITE, anchor="middle")

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "87",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "87d_workstream-phase-matrix-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
