"""
Builder for pattern 198: Partnership Model Comparison.

4-col table (Dimension / Reseller / Co-Sell / OEM) × 8 rows. Co-Sell column
highlighted with Recommended badge. Bottom note (convergence).

Source HTML: _pattern-library/198_partnership-model-comparison.html
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

HIGHLIGHT_BG = RGBColor(0xEF, 0xDD, 0xFB)  # ~rgba(199,128,255,0.18)
HIGHLIGHT_BG_ALT = RGBColor(0xF4, 0xE5, 0xFC)
GREEN = RGBColor(0x22, 0xC5, 0x5E)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Partnership Model <strong>Comparison</strong>",
        subtitle="Evaluating Reseller, Co-Sell, and OEM structures across eight critical dimensions",
        title_h=42, subtitle_h=20, brand_rule_w=64,
    )

    # Table
    tbl_top = 156
    tbl_bot = 612
    tbl_left = 64
    tbl_w = 1280 - 128
    col_pcts = [22, 26, 26, 26]
    col_xs = [tbl_left]
    for p in col_pcts[:-1]:
        col_xs.append(col_xs[-1] + int(tbl_w * p / 100))
    col_widths = [int(tbl_w * p / 100) for p in col_pcts]
    hdr_h = 34
    NUM_ROWS = 10
    row_h = (tbl_bot - tbl_top - hdr_h) // NUM_ROWS

    # Header
    add_rect(slide, "table-header-bg", tbl_left, tbl_top, tbl_w, hdr_h, BRAND_PRIMARY)
    # Highlight Co-Sell column header
    add_rect(slide, "table-col-3-bg", col_xs[2], tbl_top, col_widths[2], hdr_h, BRAND_ACCENT_SOFT)
    add_text(slide, "table-col-1-header", "Dimension",
             x_px=col_xs[0] + 12, y_px=tbl_top + 10, w_px=col_widths[0] - 20, h_px=16,
             font_size_px=10, color=RGBColor(0xCC, 0xCC, 0xDD), bold=True, uppercase=True)
    add_text(slide, "table-col-2-header", "Reseller",
             x_px=col_xs[1] + 12, y_px=tbl_top + 10, w_px=col_widths[1] - 20, h_px=16,
             font_size_px=12, color=WHITE, bold=True)
    add_text(slide, "table-col-3-header", "Co-Sell",
             x_px=col_xs[2] + 12, y_px=tbl_top + 10, w_px=80, h_px=16,
             font_size_px=12, color=BRAND_PRIMARY, bold=True)
    add_text(slide, "table-col-3-badge", "RECOMMENDED",
             x_px=col_xs[2] + 80, y_px=tbl_top + 10, w_px=110, h_px=16,
             font_size_px=8, color=WHITE, bold=True, align="center", uppercase=True,
             bg_fill=GREEN, padding_px=(2, 6, 2, 6))
    add_text(slide, "table-col-4-header", "OEM",
             x_px=col_xs[3] + 12, y_px=tbl_top + 10, w_px=col_widths[3] - 20, h_px=16,
             font_size_px=12, color=WHITE, bold=True)

    # Rows
    rows = [
        ("Revenue share", "30–40% margin to partner", "15–25% split, deal-based", "10–18% royalty on units"),
        ("Branding rights", "Partner brand leads", "Co-branded, negotiated", "White-label only"),
        ("Support responsibility", "Partner owns Tier 1–2", "Shared SLA framework", "Vendor owns all tiers"),
        ("Training provided", "Self-serve portal only", "Joint enablement sessions", "Full embedded training"),
        ("Contract term", "12 months, auto-renew", "24 months, milestone gates", "36+ months, fixed"),
        ("Minimum commitment", "$50K ARR", "$150K ARR, 3 deals/year", "$500K upfront license"),
        ("Integration depth", "API key, surface-level", "Native connector, joint roadmap", "Full SDK embed"),
        ("Exit clause", "60-day notice, no penalty", "90-day notice, wind-down plan", "12-month buyout required"),
        ("Marketing investment", "Partner-funded only", "Co-funded MDF program", "Vendor-led campaigns"),
        ("Lead routing", "Partner-sourced only", "Round-robin via PRM", "Vendor SDR routing"),
    ]
    for i, (label, c2, c3, c4) in enumerate(rows):
        n = i + 1
        ry = tbl_top + hdr_h + i * row_h
        bg = CARD_BG if i % 2 == 0 else WHITE
        add_rect(slide, f"table-row-{n}-bg", tbl_left, ry, tbl_w, row_h, bg)
        hl_bg = HIGHLIGHT_BG if i % 2 == 0 else HIGHLIGHT_BG_ALT
        add_rect(slide, f"table-row-{n}-cell-3-bg", col_xs[2], ry, col_widths[2], row_h, hl_bg)
        add_text(slide, f"table-row-{n}-label", label,
                 x_px=col_xs[0] + 12, y_px=ry + 10, w_px=col_widths[0] - 16, h_px=row_h - 12,
                 font_size_px=11, color=BRAND_PRIMARY_MID, bold=True)
        add_text(slide, f"table-row-{n}-cell-2", c2,
                 x_px=col_xs[1] + 12, y_px=ry + 10, w_px=col_widths[1] - 16, h_px=row_h - 12,
                 font_size_px=11, color=TEXT_DARK)
        add_text(slide, f"table-row-{n}-cell-3", c3,
                 x_px=col_xs[2] + 12, y_px=ry + 10, w_px=col_widths[2] - 16, h_px=row_h - 12,
                 font_size_px=11, color=TEXT_DARK, bold=True)
        add_text(slide, f"table-row-{n}-cell-4", c4,
                 x_px=col_xs[3] + 12, y_px=ry + 10, w_px=col_widths[3] - 16, h_px=row_h - 12,
                 font_size_px=11, color=TEXT_DARK)
        # Cell borders
        for cx in col_xs[1:]:
            add_rect(slide, f"table-row-{n}-cell-divider-{cx}", cx, ry, 1, row_h, CARD_BORDER)

    # Bottom note (convergence)
    note_y = tbl_bot + 4
    add_rect(slide, "convergence-rule", 64, note_y, 1280 - 128, 1, CARD_BORDER)
    add_text(slide, "convergence",
             "Recommendation basis: Co-Sell aligns best with joint GTM objectives and shared accountability — negotiate minimum commitment threshold and co-branding exclusivity in Q3 before contract signature.",
             x_px=64, y_px=note_y + 6, w_px=1280 - 128, h_px=32,
             font_size_px=10, color=TEXT_MID, italic=True,
             emphasis_color=BRAND_PRIMARY_MID)

    add_footer(slide, page_num=198)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "198_partnership-model-comparison.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
