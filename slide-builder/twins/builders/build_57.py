"""
Builder for pattern 57: Anchor stat + stacked evidence rail.

Source HTML: _pattern-library/57_anchor-stat-with-evidence-rail.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.dml.color import RGBColor

RISK_HIGH = RGBColor(0xB7, 0x1C, 0x1C)
RISK_MID = RGBColor(0xB8, 0x78, 0x00)
RISK_LOW = RGBColor(0x5C, 0x2D, 0x87)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title with eyebrow
    add_text(
        slide, "eyebrow", "FY29 NRB OUTLOOK · RISK READ",
        x_px=48, y_px=56, w_px=900, h_px=14,
        font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True,
    )
    add_text(
        slide, "title",
        "$67.6M FY29 NRB is on track — but three risks could erode that figure.",
        x_px=48, y_px=74, w_px=1180, h_px=64,
        font_size_px=26, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Headline on the left, evidence on the right. Each evidence card colour-coded by severity; "
        "ordering top-to-bottom = priority of attention.",
        x_px=48, y_px=144, w_px=940, h_px=22,
        font_size_px=13, color=TEXT_MID,
    )
    add_rect(slide, "brand-rule", 48, 172, 56, 3, BRAND_ACCENT)

    # Body grid: 360 + gap20 + rest
    g_top = 196
    g_bottom = 720 - 80
    g_h = g_bottom - g_top
    g_left = 48
    panel_w = 360
    gap = 20
    stack_left = g_left + panel_w + gap
    stack_w = 1280 - 48 - stack_left

    # Anchor panel (left)
    add_rect(slide, "anchor-panel-bg", g_left, g_top, panel_w, g_h, BRAND_PRIMARY)
    add_rect(slide, "anchor-panel-accent", g_left, g_top, 4, g_h, BRAND_ACCENT)

    add_text(
        slide, "anchor-pre-label", "FY29 NET SAVINGS (GAAP)",
        x_px=g_left + 28, y_px=g_top + 40, w_px=panel_w - 56, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    stat_text = "$67.6"
    stat_font_px = 64
    stat_x = g_left + 28
    add_text(
        slide, "anchor-stat", stat_text,
        x_px=stat_x, y_px=g_top + 58, w_px=200, h_px=80,
        font_size_px=stat_font_px, color=WHITE, bold=True,
    )
    # Offset unit by estimated width of stat text (chars * font * 0.62) + small pad
    unit_offset = int(len(stat_text) * stat_font_px * 0.62) + 4
    add_text(
        slide, "anchor-unit", "M",
        x_px=stat_x + unit_offset, y_px=g_top + 78, w_px=80, h_px=56,
        font_size_px=40, color=BRAND_ACCENT, bold=True,
    )

    # Anchor status
    st_y = g_top + 162
    add_rect(slide, "anchor-status-bg", g_left + 28, st_y, panel_w - 56, 60,
             RGBColor(0x4D, 0x2A, 0x6E))
    add_rect(slide, "anchor-status-accent", g_left + 28, st_y, 3, 60, BRAND_ACCENT)
    add_text(
        slide, "anchor-status-label", "vs. $66M target",
        x_px=g_left + 42, y_px=st_y + 10, w_px=panel_w - 84, h_px=16,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True,
    )
    add_text(
        slide, "anchor-status-value", "✓ On Track",
        x_px=g_left + 42, y_px=st_y + 28, w_px=panel_w - 84, h_px=24,
        font_size_px=18, color=WHITE, bold=True,
    )

    # Divider
    add_rect(slide, "anchor-divider", g_left + 28, st_y + 78, panel_w - 56, 1,
             RGBColor(0x6A, 0x4E, 0x88))

    # Meta
    add_text(
        slide, "anchor-meta",
        "FY30 outlook: $70.8M\n5-year total: $198M",
        x_px=g_left + 28, y_px=st_y + 94, w_px=panel_w - 56, h_px=44,
        font_size_px=11, color=BRAND_ACCENT_SOFT,
    )

    # Evidence stack (right)
    ev_data = [
        ("!", "Open Roles Assumption Revised", "High",
         "Original model: 60 heads → current estimate: ~30 heads. Impact: ~$3M/year gap vs. original at $100K per head.",
         RISK_HIGH),
        ("°", "Potential CY29 Business Case Reduction", "Watch",
         "Watch-item only — not confirmed. Flagged by internal stakeholder; no escalation to leadership until evidence solidifies.",
         RISK_MID),
        ("!", "Finance Initiative Ownership", "High",
         "Non-labor-arbitrage levers (background checks, cost-per-hire) uncommitted. If Finance does not execute, savings do not materialize.",
         RISK_HIGH),
    ]
    card_gap = 12
    card_h = (g_h - 2 * card_gap) // 3
    for i, (icon, title, tag, body, color) in enumerate(ev_data):
        n = i + 1
        ey = g_top + i * (card_h + card_gap)
        # Card body
        card = add_rect(slide, f"evidence-{n}-card-bg", stack_left, ey, stack_w, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Severity left border (5px)
        add_rect(slide, f"evidence-{n}-severity", stack_left, ey, 5, card_h, color)

        # Icon (circle approximation via filled rectangle text)
        add_text(
            slide, f"evidence-{n}-icon", icon,
            x_px=stack_left + 20, y_px=ey + 16, w_px=22, h_px=22,
            font_size_px=12, color=WHITE, bold=True, align="center", anchor="middle",
            bg_fill=color, padding_px=(0, 0, 0, 0),
        )
        # Title
        add_text(
            slide, f"evidence-{n}-title", title,
            x_px=stack_left + 52, y_px=ey + 16, w_px=stack_w - 200, h_px=22,
            font_size_px=13, color=color, bold=True,
        )
        # Tag (right)
        add_text(
            slide, f"evidence-{n}-tag", tag.upper(),
            x_px=stack_left + stack_w - 90, y_px=ey + 16, w_px=70, h_px=20,
            font_size_px=9, color=WHITE, bold=True, align="center", uppercase=True,
            bg_fill=color, padding_px=(3, 8, 3, 8),
        )
        # Body (indented to align under title)
        add_text(
            slide, f"evidence-{n}-body", body,
            x_px=stack_left + 52, y_px=ey + 44, w_px=stack_w - 80, h_px=card_h - 56,
            font_size_px=12, color=TEXT_DARK,
        )

    add_footer(slide, page_num=57)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "57_anchor-stat-with-evidence-rail.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
