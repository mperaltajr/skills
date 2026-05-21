"""
Builder for pattern 279: Value Stream Map (Order-to-Cash, 6 steps).

Source HTML: _pattern-library/279_value-stream-map.html

CRITICAL: Legend (VA / NVA) MUST sit BELOW subheadline (top-y ≥ 230,
right-aligned to x ≈ 1240). Body shifted down to clear legend.
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

VA_COLOR = RGBColor(0x15, 0x80, 0x3D)
NVA_COLOR = RGBColor(0xDC, 0x26, 0x26)
VA_BG = RGBColor(0xDC, 0xFC, 0xE7)
NVA_BG = RGBColor(0xFE, 0xE2, 0xE2)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Value Stream Map — <strong>Order-to-Cash</strong>",
        subtitle="Cycle time, wait time, and efficiency ratio across 6 process steps",
    )

    # === LEGEND — below subheadline (top-y = 232, right-edge = 1240) ===
    leg_w = 360
    leg_h = 30
    leg_y = 234
    leg_x = 1240 - leg_w
    leg = add_rect(slide, "legend-bg", leg_x, leg_y, leg_w, leg_h, CARD_BG)
    leg.line.color.rgb = CARD_BORDER
    leg.line.width = 9525

    add_text(
        slide, "legend-label", "LEGEND",
        x_px=leg_x + 10, y_px=leg_y, w_px=56, h_px=leg_h,
        font_size_px=9, color=TEXT_FAINT, bold=True, anchor="middle",
        uppercase=True, letter_spacing_px=1.2,
    )
    # VA swatch
    add_rect(slide, "legend-va-swatch", leg_x + 72, leg_y + 10, 12, 10, VA_BG)
    add_text(
        slide, "legend-va-text", "Value-Add (VA)",
        x_px=leg_x + 88, y_px=leg_y, w_px=130, h_px=leg_h,
        font_size_px=10, color=TEXT_MID, bold=True, anchor="middle",
    )
    # NVA swatch
    add_rect(slide, "legend-nva-swatch", leg_x + 220, leg_y + 10, 12, 10, NVA_BG)
    add_text(
        slide, "legend-nva-text", "Non-Value-Add (NVA)",
        x_px=leg_x + 236, y_px=leg_y, w_px=140, h_px=leg_h,
        font_size_px=10, color=TEXT_MID, bold=True, anchor="middle",
    )

    # === BODY (pushed down to clear legend) ===
    # Section header
    add_text(
        slide, "section-header", "CURRENT STATE — Order-to-Cash Process",
        x_px=56, y_px=276, w_px=600, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY, bold=True,
        uppercase=True, letter_spacing_px=2,
    )

    # Process row — 6 step boxes + arrows
    row_y = 298
    row_h = 130
    process_x = 56
    process_w = 1280 - 112
    arrow_w = 20
    total_arrow = arrow_w * 5
    step_w = (process_w - total_arrow) // 6

    steps = [
        ("01", "Order Receipt", "VA: 0.5h", "NVA: 4h"),
        ("02", "Credit Check", "VA: 1h", "NVA: 24h"),
        ("03", "Inventory Confirm", "VA: 0.5h", "NVA: 2h"),
        ("04", "Pick & Pack", "VA: 4h", "NVA: 1h"),
        ("05", "Dispatch", "VA: 2h", "NVA: 8h"),
        ("06", "Invoice", "VA: 1h", "NVA: 24h"),
    ]
    sx = process_x
    for i, (num, name, va, nva) in enumerate(steps):
        # Step box
        box = add_rect(slide, f"step-{i+1}", sx, row_y, step_w, row_h, CARD_BG)
        box.line.color.rgb = CARD_BORDER
        box.line.width = 9525
        # Top accent stripe
        add_rect(slide, f"step-{i+1}-stripe", sx, row_y, step_w, 3, BRAND_ACCENT)
        # Number
        add_text(
            slide, f"step-{i+1}-num", num,
            x_px=sx + 10, y_px=row_y + 10, w_px=40, h_px=14,
            font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True,
            uppercase=True, letter_spacing_px=1.4,
        )
        # Name
        add_text(
            slide, f"step-{i+1}-name", name,
            x_px=sx + 10, y_px=row_y + 28, w_px=step_w - 20, h_px=36,
            font_size_px=12, color=BRAND_PRIMARY, bold=True,
        )
        # Divider
        add_rect(slide, f"step-{i+1}-rule", sx + 10, row_y + 70, step_w - 20, 1, CARD_BORDER)
        # VA
        add_text(
            slide, f"step-{i+1}-va", va,
            x_px=sx + 10, y_px=row_y + 76, w_px=step_w - 20, h_px=14,
            font_size_px=11, color=VA_COLOR, bold=True,
        )
        # NVA
        add_text(
            slide, f"step-{i+1}-nva", nva,
            x_px=sx + 10, y_px=row_y + 92, w_px=step_w - 20, h_px=14,
            font_size_px=11, color=NVA_COLOR, bold=True,
        )
        # Cycle+Wait label
        add_text(
            slide, f"step-{i+1}-label", "CYCLE + WAIT",
            x_px=sx + 10, y_px=row_y + 110, w_px=step_w - 20, h_px=12,
            font_size_px=8, color=TEXT_FAINT,
            uppercase=True, letter_spacing_px=0.8,
        )

        # Arrow after step (except last)
        if i < 5:
            ax = sx + step_w
            add_text(
                slide, f"arrow-{i+1}", "→",
                x_px=ax, y_px=row_y + row_h // 2 - 12, w_px=arrow_w, h_px=24,
                font_size_px=16, color=BRAND_ACCENT_SOFT, bold=True, align="center",
            )
        sx += step_w + arrow_w

    # KPI tiles + Opportunity callout in summary row
    # (matches HTML reference: summary band starts ~16px below process row bottom)
    summary_y = 446
    summary_h = 154

    # KPI tiles (3 across)
    kpi_w = 140
    kpi_gap = 12
    kpi_x = 56
    kpis = [
        ("TOTAL LEAD TIME", "72", "hours", False),
        ("VALUE-ADD TIME", "9", "hours", False),
        ("EFFICIENCY", "12.5%", "of time adds value", True),
    ]
    for i, (label, value, unit, accent) in enumerate(kpis):
        tx = kpi_x + i * (kpi_w + kpi_gap)
        bg = BRAND_PRIMARY if accent else CARD_BG
        tile = add_rect(slide, f"kpi-{i+1}", tx, summary_y, kpi_w, summary_h, bg)
        tile.line.color.rgb = CARD_BORDER
        tile.line.width = 9525
        label_color = BRAND_ACCENT_SOFT if accent else TEXT_FAINT
        value_color = WHITE if accent else BRAND_PRIMARY
        unit_color = BRAND_ACCENT_SOFT if accent else TEXT_MID
        add_text(
            slide, f"kpi-{i+1}-label", label,
            x_px=tx + 14, y_px=summary_y + 16, w_px=kpi_w - 28, h_px=14,
            font_size_px=9, color=label_color, bold=True,
            uppercase=True, letter_spacing_px=1.8,
        )
        # Value
        if i == 1:
            value_color = VA_COLOR
        add_text(
            slide, f"kpi-{i+1}-value", value,
            x_px=tx + 14, y_px=summary_y + 40, w_px=kpi_w - 28, h_px=64,
            font_size_px=36, color=value_color, bold=True,
        )
        # Unit
        add_text(
            slide, f"kpi-{i+1}-unit", unit,
            x_px=tx + 14, y_px=summary_y + 104, w_px=kpi_w - 28, h_px=16,
            font_size_px=11, color=unit_color, bold=True,
        )

    # Opportunity callout
    opp_x = kpi_x + 3 * (kpi_w + kpi_gap)
    opp_w = 1280 - 56 - opp_x
    opp = add_rect(slide, "opp-box", opp_x, summary_y, opp_w, summary_h,
                   RGBColor(0xFF, 0xF7, 0xED))
    opp.line.color.rgb = RGBColor(0xFD, 0xE6, 0x8A)
    opp.line.width = 9525
    # left orange bar
    add_rect(slide, "opp-bar", opp_x, summary_y, 4, summary_h,
             RGBColor(0xF5, 0x9E, 0x0B))
    add_text(
        slide, "opp-tag", "OPPORTUNITY",
        x_px=opp_x + 18, y_px=summary_y + 16, w_px=opp_w - 32, h_px=14,
        font_size_px=10, color=RGBColor(0x92, 0x40, 0x0E), bold=True,
        uppercase=True, letter_spacing_px=2,
    )
    add_text(
        slide, "opp-text",
        "Eliminating wait time in Credit Check and Invoice steps alone reduces "
        "lead time by 48h (67% reduction), cutting the process from 72h to 24h "
        "without changing any value-add activity.",
        x_px=opp_x + 18, y_px=summary_y + 36, w_px=opp_w - 32, h_px=summary_h - 50,
        font_size_px=12, color=TEXT_DARK,
    )

    add_footer(slide, page_num=279)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "279_value-stream-map.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
