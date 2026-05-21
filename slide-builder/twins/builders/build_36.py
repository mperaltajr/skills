"""
Builder for pattern 36: Customer journey map.

6-phase × 3-row grid (Actions / Pain points / Opportunities). Phase 3
(Storyline) is the focal break-point. Pattern-local IDs:
journey-phase-N-name/num, journey-row-N-name/num,
journey-phase-N-actions/pain/opps.

Source HTML: _pattern-library/36_customer-journey-map.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.dml.color import RGBColor

PAIN_TINT = RGBColor(0xFE, 0xF3, 0xC7)
PAIN_BORDER = RGBColor(0xF5, 0xD7, 0x8A)
GOOD_TINT = RGBColor(0xDC, 0xFC, 0xE7)
GOOD_BORDER = RGBColor(0xA7, 0xE5, 0xBF)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title block with eyebrow above title
    add_text(
        slide, "eyebrow", "Service Design · Journey",
        x_px=56, y_px=50, w_px=1000, h_px=14,
        font_size_px=10, color=BRAND_ACCENT, bold=True,
        letter_spacing_px=2.5, uppercase=True,
    )
    add_text(
        slide, "title",
        "Consultant journey building a deck — six phases, six pain points.",
        x_px=56, y_px=66, w_px=1000, h_px=44,
        font_size_px=26, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Where the work breaks down, and where Slide Lab steps in.",
        x_px=56, y_px=112, w_px=900, h_px=20,
        font_size_px=13, color=TEXT_MID,
    )
    add_rect(slide, "brand-rule", x_px=56, y_px=140, w_px=56, h_px=3, fill_color=BRAND_ACCENT)

    # Journey grid: left col=132 (row labels) + right col=phase grid, gap 14
    grid_left = 56
    grid_top = 165
    grid_right = 1280 - 56
    grid_w = grid_right - grid_left
    row_label_w = 132
    phase_grid_w = grid_w - row_label_w - 14
    phase_col_w = (phase_grid_w - 5 * 6) // 6  # 6 cols, 6 gaps

    # Row layout: 44px header strip + 3 equal content rows × 130px + gaps
    header_h = 44
    row_h = 130
    row_gap = 10

    # ---- Row labels (left col) ----
    row_label_x = grid_left
    row_names = ["Actions", "Pain Points", "Opportunities"]
    for ri in range(3):
        rn = ri + 1
        ry = grid_top + header_h + row_gap + ri * (row_h + row_gap)
        add_text(
            slide, f"journey-row-{rn}-num", f"0{rn}",
            x_px=row_label_x, y_px=ry + (row_h - 28) // 2, w_px=36, h_px=28,
            font_size_px=20, color=BRAND_ACCENT_SOFT, bold=True,
        )
        add_text(
            slide, f"journey-row-{rn}-name", row_names[ri],
            x_px=row_label_x + 40, y_px=ry + (row_h - 28) // 2, w_px=row_label_w - 50, h_px=28,
            font_size_px=11, color=BRAND_PRIMARY_MID, bold=True,
            letter_spacing_px=1.8, uppercase=True,
        )
        # Right border on row labels
        add_rect(slide, f"journey-row-{rn}-divider", row_label_x + row_label_w - 2,
                 ry, 2, row_h, CARD_BORDER)

    # ---- Phase grid (right col) ----
    grid_inner_left = grid_left + row_label_w + 14

    phase_names = ["Kickoff", "Research", "Storyline", "Draft", "Review", "Deliver"]
    actions = [
        "Get the brief from partner",
        "Synthesize workstream findings",
        "Build the deck outline",
        "Write slides and visuals",
        "Cycle through reviewer comments",
        "Present to client",
    ]
    pains = [
        "Brief unclear, scope ambiguous",
        "Workstreams produce raw, not synthesized",
        "Storyline gets skipped under time pressure",
        "Bullets accumulate without structure",
        "Reviewers add, no one subtracts",
        "Late edits break the through-line",
    ]
    opps = [
        "Slide Lab clarifies brief in 30 min",
        "Sharpen workstreams before compiling",
        "Coached storyline session is the unlock",
        "Pattern library applies treatment fast",
        "QC catches structural drift early",
        "Final review focuses on argument, not formatting",
    ]

    # Phase headers
    for pi in range(6):
        pn = pi + 1
        px_left = grid_inner_left + pi * (phase_col_w + 6)
        is_focal = (pn == 3)
        header_fill = BRAND_ACCENT if is_focal else BRAND_PRIMARY
        add_rect(slide, f"journey-phase-{pn}", px_left, grid_top, phase_col_w, header_h, header_fill)
        add_text(
            slide, f"journey-phase-{pn}-num", f"0{pn}",
            x_px=px_left + 10, y_px=grid_top + 6, w_px=phase_col_w - 20, h_px=12,
            font_size_px=8, color=BRAND_ACCENT_SOFT if not is_focal else WHITE,
            bold=True, letter_spacing_px=1.2, align="center",
        )
        add_text(
            slide, f"journey-phase-{pn}-name", phase_names[pi],
            x_px=px_left + 10, y_px=grid_top + 20, w_px=phase_col_w - 20, h_px=20,
            font_size_px=12, color=WHITE, bold=True, align="center",
            letter_spacing_px=1.4, uppercase=True,
        )

        # Action row cell
        ay = grid_top + header_h + row_gap
        add_rect(slide, f"journey-phase-{pn}-actions-bg", px_left, ay, phase_col_w, row_h, CARD_BG)
        add_text(
            slide, f"journey-phase-{pn}-actions", actions[pi],
            x_px=px_left + 10, y_px=ay + 8, w_px=phase_col_w - 20, h_px=row_h - 16,
            font_size_px=10, color=TEXT_DARK,
        )

        # Pain row cell
        py = ay + row_h + row_gap
        if is_focal:
            cell_bg = WHITE
            cell = add_rect(slide, f"journey-phase-{pn}-pain-bg", px_left, py, phase_col_w, row_h, cell_bg)
            cell.line.color.rgb = BRAND_ACCENT
            cell.line.width = 25400
            add_rect(slide, "journey-phase-3-pain-tag", px_left + (phase_col_w - 72) // 2,
                     py - 7, 72, 14, BRAND_ACCENT)
            add_text(
                slide, "journey-phase-3-pain-tag-text", "BIGGEST BREAK",
                x_px=px_left + (phase_col_w - 72) // 2, y_px=py - 7, w_px=72, h_px=14,
                font_size_px=7, color=WHITE, bold=True, align="center", anchor="middle",
                letter_spacing_px=1.2, uppercase=True,
            )
        else:
            cell = add_rect(slide, f"journey-phase-{pn}-pain-bg", px_left, py, phase_col_w, row_h, PAIN_TINT)
            cell.line.color.rgb = PAIN_BORDER
            cell.line.width = 9525
        add_text(
            slide, f"journey-phase-{pn}-pain", pains[pi],
            x_px=px_left + 10, y_px=py + 10, w_px=phase_col_w - 20, h_px=row_h - 20,
            font_size_px=10, color=BRAND_PRIMARY if is_focal else TEXT_DARK,
            bold=is_focal,
        )

        # Opps row cell
        oy = py + row_h + row_gap
        opp_cell = add_rect(slide, f"journey-phase-{pn}-opps-bg", px_left, oy, phase_col_w, row_h, GOOD_TINT)
        opp_cell.line.color.rgb = GOOD_BORDER
        opp_cell.line.width = 9525
        add_text(
            slide, f"journey-phase-{pn}-opps", opps[pi],
            x_px=px_left + 10, y_px=oy + 8, w_px=phase_col_w - 20, h_px=row_h - 16,
            font_size_px=10, color=TEXT_DARK,
        )

    # Convergence (thin line + italic text, per pattern 36 spec)
    conv_y = 660
    add_text(
        slide, "convergence",
        "Where the journey breaks is where the patterns are.",
        x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=20,
        font_size_px=11, color=BRAND_PRIMARY_MID, italic=True, align="center",
    )

    add_footer(slide, page_num=36)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "36_customer-journey-map.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
