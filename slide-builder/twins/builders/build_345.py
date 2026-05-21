"""
Builder for pattern 345: Dark Investment Case.

Source HTML: _pattern-library/345_dark-investment-case.html
Standalone — closest light reference: 64_investment-thesis-cards.

Layout: 4 KPI tiles (top row), then 2-card body (Value Drivers · Risks &
Mitigations), then recommended action strip at bottom.
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
ACCENT_GREEN = RGBColor(0x22, 0xC5, 0x5E)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title
    add_text(slide, "title",
             "Digital Operations Transformation — <strong>Investment Case</strong>",
             x_px=64, y_px=20, w_px=1152, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Financial summary and value proposition for board review, FY 2026–2028",
             x_px=64, y_px=108, w_px=1100, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    # --- KPI tiles ---
    kpi_y = 162
    kpi_h = 96
    gap = 12
    tile_w = (1152 - 3 * gap) // 4
    kpis = [
        ("Investment Required", "$14.2M", "Over 24-month programme", WHITE),
        ("Expected ROI", "312% ▲", "vs. 180% industry benchmark", BRAND_ACCENT_SOFT),
        ("Payback Period", "18 mo", "Break-even Q2 FY 2028", WHITE),
        ("NPV (5-year)", "$38.7M", "Discount rate 8%", BRAND_ACCENT_SOFT),
    ]
    for i, (lbl, val, sub, vcol) in enumerate(kpis):
        x = 64 + i * (tile_w + gap)
        c = add_rect(slide, f"kpi-{i+1}-bg", x, kpi_y, tile_w, kpi_h, CARD_BG_DARK)
        c.line.color.rgb = CARD_BORDER_DARK
        c.line.width = 9525
        add_text(slide, f"kpi-{i+1}-label", lbl,
                 x_px=x + 16, y_px=kpi_y + 12, w_px=tile_w - 32, h_px=14,
                 font_size_px=10, color=TEXT_ON_DARK_FAINT, bold=True,
                 uppercase=True, letter_spacing_px=1.5)
        add_text(slide, f"kpi-{i+1}-value", val,
                 x_px=x + 16, y_px=kpi_y + 28, w_px=tile_w - 32, h_px=36,
                 font_size_px=28, color=vcol, bold=True)
        add_text(slide, f"kpi-{i+1}-sub", sub,
                 x_px=x + 16, y_px=kpi_y + 68, w_px=tile_w - 32, h_px=18,
                 font_size_px=10, color=TEXT_ON_DARK_MID)

    # --- Middle row: 2 cards ---
    mid_y = 272
    mid_h = 286
    card_gap = 16
    card_w = (1152 - card_gap) // 2

    # Value Drivers
    vx = 64
    c = add_rect(slide, "value-card-bg", vx, mid_y, card_w, mid_h, CARD_BG_DARK)
    c.line.color.rgb = CARD_BORDER_DARK
    c.line.width = 9525
    add_text(slide, "value-card-title", "VALUE DRIVERS",
             x_px=vx + 18, y_px=mid_y + 14, w_px=card_w - 36, h_px=14,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1.5)
    add_rect(slide, "value-card-rule", vx + 18, mid_y + 34, card_w - 36, 1,
             CARD_BORDER_DARK)
    drivers = [
        ("Operational Cost Reduction",
         "Automated order-to-cash and procure-to-pay cycles cut FTE hours by 40% across back-office functions",
         "$8.4M"),
        ("Revenue Uplift — Cross-Sell Enablement",
         "Real-time propensity models surface $220M in addressable cross-sell annually; 12% conversion improvement",
         "$26.4M"),
        ("Risk & Compliance Cost Avoidance",
         "Automated controls monitoring reduces audit findings and regulatory penalty exposure by 65%",
         "$3.9M"),
    ]
    drv_top = mid_y + 44
    drv_h = (mid_h - 56) // 3
    for i, (t, d, v) in enumerate(drivers):
        dy = drv_top + i * drv_h
        add_text(slide, f"drv-{i+1}-title", t,
                 x_px=vx + 18, y_px=dy + 4, w_px=card_w - 130, h_px=18,
                 font_size_px=12, color=WHITE, bold=True)
        add_text(slide, f"drv-{i+1}-desc", d,
                 x_px=vx + 18, y_px=dy + 22, w_px=card_w - 130, h_px=drv_h - 26,
                 font_size_px=10, color=TEXT_ON_DARK_MID)
        add_text(slide, f"drv-{i+1}-val", v,
                 x_px=vx + card_w - 110, y_px=dy + 4, w_px=92, h_px=28,
                 font_size_px=20, color=ACCENT_GREEN, bold=True, align="right")

    # Risks & Mitigations
    rx2 = 64 + card_w + card_gap
    c = add_rect(slide, "risk-card-bg", rx2, mid_y, card_w, mid_h, CARD_BG_DARK)
    c.line.color.rgb = CARD_BORDER_DARK
    c.line.width = 9525
    add_text(slide, "risk-card-title", "RISKS & MITIGATIONS",
             x_px=rx2 + 18, y_px=mid_y + 14, w_px=card_w - 36, h_px=14,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1.5)
    add_rect(slide, "risk-card-rule", rx2 + 18, mid_y + 34, card_w - 36, 1,
             CARD_BORDER_DARK)
    risks_list = [
        ("Change Resistance — Adoption Shortfall",
         "Dedicated OCM workstream with embedded change champions; adoption KPIs gated at each phase milestone"),
        ("Integration Complexity with Legacy ERP",
         "API-first middleware layer; phased cutover with parallel-run period; rollback playbook maintained per release"),
        ("Benefit Realisation Slippage",
         "Benefits locked in value-tracking register; quarterly steering review with go/no-go gates tied to disbursement"),
    ]
    rrow_top = mid_y + 44
    rrow_h = (mid_h - 56) // 3
    for i, (label, mit) in enumerate(risks_list):
        ry2 = rrow_top + i * rrow_h
        add_text(slide, f"risk-{i+1}-label", label,
                 x_px=rx2 + 18, y_px=ry2 + 4, w_px=card_w - 36, h_px=18,
                 font_size_px=12, color=WHITE, bold=True)
        add_text(slide, f"risk-{i+1}-mit", mit,
                 x_px=rx2 + 18, y_px=ry2 + 22, w_px=card_w - 36, h_px=rrow_h - 26,
                 font_size_px=10, color=TEXT_ON_DARK_MID)

    # --- Action strip ---
    act_y = 580
    act_h = 60
    add_rect(slide, "act-bg", 64, act_y, 1152, act_h, BRAND_PRIMARY_MID)
    add_rect(slide, "act-accent", 64, act_y, 4, act_h, BRAND_ACCENT)
    add_text(slide, "act-text",
             "Recommended: <strong>Approve Phase 1 ($5.8M) at July board</strong> — initiate vendor selection and OCM mobilisation immediately",
             x_px=84, y_px=act_y + 8, w_px=1100, h_px=24,
             font_size_px=13, color=WHITE, emphasis_color=BRAND_ACCENT_SOFT,
             anchor="middle")
    add_text(slide, "act-approval",
             "Requires board approval · Sponsor: Chief Operating Officer",
             x_px=84, y_px=act_y + 32, w_px=1100, h_px=20,
             font_size_px=10, color=TEXT_ON_DARK_MID, italic=True,
             anchor="middle")

    # Invariant zone
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "345",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = (Path(__file__).resolve().parents[2] / "_renders" / "twins" /
           "345_dark-investment-case.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
