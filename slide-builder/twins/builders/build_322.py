"""
Builder for pattern 322: 4-bucket with metrics — KPI strip + supporting columns.

KPI strip (4 tiles) on top, then 4 detail columns underneath with bullets + status pill.
Status pills act as the legend visualisation per HTML — no separate legend block.

Source HTML: _pattern-library/322_4bucket-with-metrics.html
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

PILL_GREEN_BG = RGBColor(0xDC, 0xFC, 0xE7)
PILL_GREEN_FG = RGBColor(0x15, 0x80, 0x3D)
PILL_AMBER_BG = RGBColor(0xFE, 0xF9, 0xC3)
PILL_AMBER_FG = RGBColor(0xA1, 0x62, 0x07)
PILL_RED_BG = RGBColor(0xFE, 0xE2, 0xE2)
PILL_RED_FG = RGBColor(0xB9, 0x1C, 0x1C)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Program health at a glance — <strong>four critical dimensions</strong>",
        subtitle="KPI snapshot with supporting evidence by workstream · as of May 2026",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap = 12
    col_w = (body_w - 3 * gap) // 4

    # KPI strip
    kpi_h = 96
    kpis = [
        ("Delivery Velocity", "94%", "▲ 6pp vs. prior period", "up"),
        ("Budget Utilisation", "$8.2M", "▼ $0.4M over forecast", "down"),
        ("Adoption Rate", "71%", "▲ 12pp month-on-month", "up"),
        ("Risk Exposure", "3", "▼ 2 open critical items", "down"),
    ]
    for i, (name, val, delta, direction) in enumerate(kpis):
        n = i + 1
        kx = body_left + i * (col_w + gap)
        tile = add_rect(slide, f"kpi-{n}-tile", kx, body_top, col_w, kpi_h, CARD_BG)
        tile.line.color.rgb = CARD_BORDER
        tile.line.width = 9525
        add_rect(slide, f"kpi-{n}-accent", kx, body_top, 3, kpi_h, BRAND_ACCENT)
        add_text(
            slide, f"kpi-{n}-name", name.upper(),
            x_px=kx + 16, y_px=body_top + 12, w_px=col_w - 32, h_px=14,
            font_size_px=9, color=TEXT_FAINT, bold=True, letter_spacing_px=1.4,
        )
        add_text(
            slide, f"kpi-{n}-value", val,
            x_px=kx + 16, y_px=body_top + 30, w_px=col_w - 32, h_px=36,
            font_size_px=26, color=BRAND_PRIMARY, bold=True,
        )
        delta_color = PILL_GREEN_FG if direction == "up" else PILL_RED_FG
        add_text(
            slide, f"kpi-{n}-delta", delta,
            x_px=kx + 16, y_px=body_top + kpi_h - 22, w_px=col_w - 32, h_px=16,
            font_size_px=10, color=delta_color, bold=True,
        )

    # Columns below KPI
    col_top = body_top + kpi_h + 14
    col_h = body_top + body_h - col_top
    columns = [
        ("Delivery",
         ["Sprint 18 closed with zero carryover stories; velocity stable at 42 pts",
          "CI/CD pipeline mean lead time reduced from 4.1 to 2.8 days this quarter",
          "UAT sign-off achieved for three of four modules ahead of schedule"],
         "On Track", "green"),
        ("Finance",
         ["Infrastructure overspend driven by unplanned DR environment provisioning",
          "Change request #CR-041 submitted to baseline; approval pending steering",
          "Remaining contingency buffer: $1.1M against $12M total programme budget"],
         "Needs Attention", "amber"),
        ("Adoption",
         ["Wave 2 rollout covers 1,800 end-users across EMEA and North America",
          "Hypercare desk resolving 87% of tickets within 4 business hours",
          "Targeted coaching sessions scheduled for three low-engagement cohorts"],
         "On Track", "green"),
        ("Risk & Issues",
         ["Integration dependency on legacy ERP API remains unresolved — owner: TechOps",
          "Data privacy review for EU region requested; DPO response due 30 May",
          "Vendor SLA breach escalated; penalty clause review underway with Legal"],
         "At Risk", "red"),
    ]
    pill_bg_map = {"green": PILL_GREEN_BG, "amber": PILL_AMBER_BG, "red": PILL_RED_BG}
    pill_fg_map = {"green": PILL_GREEN_FG, "amber": PILL_AMBER_FG, "red": PILL_RED_FG}
    for i, (label, bullets, status, status_color) in enumerate(columns):
        n = i + 1
        cx = body_left + i * (col_w + gap)
        card = add_rect(slide, f"col-{n}-card", cx, col_top, col_w, col_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        add_text(
            slide, f"col-{n}-label", label.upper(),
            x_px=cx + 14, y_px=col_top + 12, w_px=col_w - 28, h_px=14,
            font_size_px=9, color=BRAND_PRIMARY, bold=True, letter_spacing_px=1.4,
        )
        bullets_y = col_top + 36
        for bi, b in enumerate(bullets):
            bn = bi + 1
            by = bullets_y + bi * 50
            add_rect(slide, f"col-{n}-bullet-{bn}-dot",
                     cx + 14, by + 6, 4, 4, BRAND_ACCENT_SOFT)
            add_text(
                slide, f"col-{n}-bullet-{bn}-text", b,
                x_px=cx + 24, y_px=by, w_px=col_w - 38, h_px=48,
                font_size_px=11, color=TEXT_MID,
            )
        # Status pill bottom
        pill_w = len(status) * 7 + 24
        pill_h = 20
        pill_x = cx + 14
        pill_y = col_top + col_h - pill_h - 14
        pill = add_rect(slide, f"col-{n}-pill", pill_x, pill_y, pill_w, pill_h, pill_bg_map[status_color])
        pill.line.fill.background()
        add_text(
            slide, f"col-{n}-pill-text", status,
            x_px=pill_x, y_px=pill_y, w_px=pill_w, h_px=pill_h,
            font_size_px=10, color=pill_fg_map[status_color], bold=True,
            align="center", anchor="middle",
        )

    add_footer(slide, page_num=322)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "322_4bucket-with-metrics.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
