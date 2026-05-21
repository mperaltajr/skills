"""
Builder for pattern 198d: Partnership Model Comparison — DARK variant.

Light source: twins/builders/build_198.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

HIGHLIGHT_BG = RGBColor(0x5C, 0x2D, 0x87)
HIGHLIGHT_BG_ALT = RGBColor(0x6E, 0x3D, 0x9A)
GREEN = RGBColor(0x4A, 0xDE, 0x80)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Partnership Model <strong>Comparison</strong>",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Evaluating Reseller, Co-Sell, and OEM structures across eight critical dimensions",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    tbl_top = 220
    tbl_bot = 640
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

    add_rect(slide, "table-header-bg", tbl_left, tbl_top, tbl_w, hdr_h, BRAND_ACCENT)
    add_rect(slide, "table-col-3-bg", col_xs[2], tbl_top, col_widths[2], hdr_h, BRAND_ACCENT_SOFT)
    add_text(slide, "table-col-1-header", "Dimension",
             x_px=col_xs[0] + 12, y_px=tbl_top + 10, w_px=col_widths[0] - 20, h_px=16,
             font_size_px=10, color=WHITE, bold=True, uppercase=True)
    add_text(slide, "table-col-2-header", "Reseller",
             x_px=col_xs[1] + 12, y_px=tbl_top + 10, w_px=col_widths[1] - 20, h_px=16,
             font_size_px=12, color=WHITE, bold=True)
    add_text(slide, "table-col-3-header", "Co-Sell",
             x_px=col_xs[2] + 12, y_px=tbl_top + 10, w_px=80, h_px=16,
             font_size_px=12, color=BRAND_PRIMARY, bold=True)
    add_text(slide, "table-col-3-badge", "RECOMMENDED",
             x_px=col_xs[2] + 80, y_px=tbl_top + 10, w_px=110, h_px=16,
             font_size_px=8, color=BRAND_PRIMARY, bold=True, align="center", uppercase=True,
             bg_fill=GREEN, padding_px=(2, 6, 2, 6))
    add_text(slide, "table-col-4-header", "OEM",
             x_px=col_xs[3] + 12, y_px=tbl_top + 10, w_px=col_widths[3] - 20, h_px=16,
             font_size_px=12, color=WHITE, bold=True)

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
        bgc = CARD_BG_DARK if i % 2 == 0 else BRAND_PRIMARY
        add_rect(slide, f"table-row-{n}-bg", tbl_left, ry, tbl_w, row_h, bgc)
        hl_bg = HIGHLIGHT_BG if i % 2 == 0 else HIGHLIGHT_BG_ALT
        add_rect(slide, f"table-row-{n}-cell-3-bg", col_xs[2], ry, col_widths[2], row_h, hl_bg)
        add_text(slide, f"table-row-{n}-label", label,
                 x_px=col_xs[0] + 12, y_px=ry + 10, w_px=col_widths[0] - 16, h_px=row_h - 12,
                 font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"table-row-{n}-cell-2", c2,
                 x_px=col_xs[1] + 12, y_px=ry + 10, w_px=col_widths[1] - 16, h_px=row_h - 12,
                 font_size_px=11, color=TEXT_ON_DARK_MID)
        add_text(slide, f"table-row-{n}-cell-3", c3,
                 x_px=col_xs[2] + 12, y_px=ry + 10, w_px=col_widths[2] - 16, h_px=row_h - 12,
                 font_size_px=11, color=WHITE, bold=True)
        add_text(slide, f"table-row-{n}-cell-4", c4,
                 x_px=col_xs[3] + 12, y_px=ry + 10, w_px=col_widths[3] - 16, h_px=row_h - 12,
                 font_size_px=11, color=TEXT_ON_DARK_MID)
        for ci in col_xs[1:]:
            add_rect(slide, f"table-row-{n}-cell-divider-{ci}", ci, ry, 1, row_h, CARD_BORDER_DARK)

    note_y = tbl_bot + 4
    add_rect(slide, "convergence-rule", 64, note_y, 1280 - 128, 1, CARD_BORDER_DARK)
    add_text(slide, "convergence",
             "Recommendation basis: Co-Sell aligns best with joint GTM objectives and shared accountability — negotiate minimum commitment threshold and co-branding exclusivity in Q3 before contract signature.",
             x_px=64, y_px=note_y + 6, w_px=1280 - 128, h_px=32,
             font_size_px=10, color=TEXT_ON_DARK_MID, italic=True,
             emphasis_color=BRAND_ACCENT_SOFT)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "198",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "198d_partnership-model-comparison-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
