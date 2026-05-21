"""
Builder for pattern 299: Committee / governance structure (3-tier org chart + sidebar).

Org chart connectors are SVG in the HTML; treated as a chart-canvas placeholder.
Boxes for L1/L2/L3 are drawn natively; sidebar with key principles on the right.

Source HTML: _pattern-library/299_committee-governance-structure.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Committee & <strong>Governance Structure</strong>",
        subtitle="Oversight framework and committee mandates as of FY2026",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # Chart area on left (~960 wide), sidebar on right (~200)
    chart_x = 48
    chart_y = 184
    chart_w = 940
    chart_h = 460

    # ── Level 1: Board (full width of chart area) ──
    l1_h = 58
    add_rect(slide, "l1-box", chart_x, chart_y, chart_w, l1_h, BRAND_PRIMARY)
    add_text(
        slide, "l1-title", "Board of Directors",
        x_px=chart_x, y_px=chart_y, w_px=chart_w, h_px=l1_h,
        font_size_px=15, color=WHITE, bold=True, align="center", anchor="middle",
    )

    # ── Level 2: 2 boxes, half-width each with a gap ──
    l2_y = chart_y + l1_h + 72
    l2_h = 76
    l2_gap = 24
    l2_w = (chart_w - l2_gap) // 2
    l2_boxes = [
        ("Executive Committee", "12 members · meets monthly"),
        ("Audit & Risk Committee", "8 members · meets quarterly"),
    ]
    for i, (title, meta) in enumerate(l2_boxes):
        n = i + 1
        bx = chart_x + i * (l2_w + l2_gap)
        add_rect(slide, f"l2-{n}-box", bx, l2_y, l2_w, l2_h, BRAND_PRIMARY_MID)
        add_text(
            slide, f"l2-{n}-title", title,
            x_px=bx + 12, y_px=l2_y + 14, w_px=l2_w - 24, h_px=20,
            font_size_px=14, color=WHITE, bold=True, align="center",
        )
        add_text(
            slide, f"l2-{n}-meta", meta,
            x_px=bx + 12, y_px=l2_y + 38, w_px=l2_w - 24, h_px=18,
            font_size_px=11, color=WHITE, align="center",
        )

    # ── Level 3: 4 boxes ──
    l3_y = l2_y + l2_h + 72
    l3_h = 80
    l3_gap = 16
    l3_w = (chart_w - 3 * l3_gap) // 4
    l3_boxes = [
        ("Finance & Investment Sub-Committee", "6 members · meets quarterly"),
        ("People & Culture Sub-Committee", "5 members · meets quarterly"),
        ("Internal Audit Sub-Committee", "4 members · meets quarterly"),
        ("Compliance & Ethics Sub-Committee", "5 members · meets quarterly"),
    ]
    for i, (title, meta) in enumerate(l3_boxes):
        n = i + 1
        bx = chart_x + i * (l3_w + l3_gap)
        box = add_rect(slide, f"l3-{n}-box", bx, l3_y, l3_w, l3_h, CARD_BG)
        box.line.color.rgb = CARD_BORDER
        box.line.width = 9525
        add_text(
            slide, f"l3-{n}-title", title,
            x_px=bx + 10, y_px=l3_y + 14, w_px=l3_w - 20, h_px=42,
            font_size_px=11, color=BRAND_PRIMARY, bold=True,
        )
        add_text(
            slide, f"l3-{n}-meta", meta,
            x_px=bx + 10, y_px=l3_y + 56, w_px=l3_w - 20, h_px=16,
            font_size_px=9, color=TEXT_FAINT,
        )

    # ── Connectors (light rules: L1→L2, L2→L3) ──
    # L1 → midline rule
    mid_x1 = chart_x + chart_w // 4
    mid_x2 = chart_x + 3 * chart_w // 4
    # vertical drops from L1 bottom to between L1 and L2
    drop_top = chart_y + l1_h
    drop_mid = drop_top + 36
    # vertical from L1 center
    add_rect(slide, "conn-l1-down", chart_x + chart_w // 2, drop_top, 1, 36, CARD_BORDER)
    # horizontal across to two halves
    add_rect(slide, "conn-l1-across", mid_x1, drop_mid, mid_x2 - mid_x1, 1, CARD_BORDER)
    # drops into each L2
    add_rect(slide, "conn-l1-l2a", mid_x1, drop_mid, 1, l2_y - drop_mid, CARD_BORDER)
    add_rect(slide, "conn-l1-l2b", mid_x2, drop_mid, 1, l2_y - drop_mid, CARD_BORDER)

    # L2 → L3
    drop2_top = l2_y + l2_h
    drop2_mid = drop2_top + 36
    # Under L2 left (covers L3 #1 & #2)
    l2l_cx = chart_x + l2_w // 2
    l3a_cx = chart_x + l3_w // 2
    l3b_cx = chart_x + l3_w + l3_gap + l3_w // 2
    add_rect(slide, "conn-l2l-down", l2l_cx, drop2_top, 1, 36, CARD_BORDER)
    add_rect(slide, "conn-l2l-across", l3a_cx, drop2_mid,
             l3b_cx - l3a_cx, 1, CARD_BORDER)
    add_rect(slide, "conn-l2l-l3a", l3a_cx, drop2_mid, 1, l3_y - drop2_mid, CARD_BORDER)
    add_rect(slide, "conn-l2l-l3b", l3b_cx, drop2_mid, 1, l3_y - drop2_mid, CARD_BORDER)
    # Under L2 right (covers L3 #3 & #4)
    l2r_cx = chart_x + l2_w + l2_gap + l2_w // 2
    l3c_cx = chart_x + 2 * (l3_w + l3_gap) + l3_w // 2
    l3d_cx = chart_x + 3 * (l3_w + l3_gap) + l3_w // 2
    add_rect(slide, "conn-l2r-down", l2r_cx, drop2_top, 1, 36, CARD_BORDER)
    add_rect(slide, "conn-l2r-across", l3c_cx, drop2_mid,
             l3d_cx - l3c_cx, 1, CARD_BORDER)
    add_rect(slide, "conn-l2r-l3c", l3c_cx, drop2_mid, 1, l3_y - drop2_mid, CARD_BORDER)
    add_rect(slide, "conn-l2r-l3d", l3d_cx, drop2_mid, 1, l3_y - drop2_mid, CARD_BORDER)

    # ── Sidebar: Key Governance Principles ──
    sb_x = 1004
    sb_y = chart_y
    sb_w = 228
    sb_h = chart_h
    # Left divider
    add_rect(slide, "sidebar-divider", sb_x - 16, sb_y, 1, sb_h, CARD_BORDER)
    add_text(
        slide, "sidebar-heading", "KEY GOVERNANCE PRINCIPLES",
        x_px=sb_x, y_px=sb_y + 12, w_px=sb_w, h_px=16,
        font_size_px=10, color=BRAND_PRIMARY, bold=True,
        letter_spacing_px=1.6,
    )
    principles = [
        "Clear accountability at every level of the committee hierarchy",
        "Independent oversight through non-executive representation",
        "Transparent reporting with published meeting minutes and decisions",
        "Annual mandate reviews to ensure fitness for purpose",
    ]
    p_y = sb_y + 44
    for i, p in enumerate(principles):
        n = i + 1
        add_rect(slide, f"principle-{n}-dot", sb_x, p_y + 6, 6, 6, BRAND_ACCENT)
        add_text(
            slide, f"principle-{n}-text", p,
            x_px=sb_x + 14, y_px=p_y, w_px=sb_w - 14, h_px=66,
            font_size_px=11, color=TEXT_MID,
        )
        p_y += 80

    add_footer(slide, page_num=299)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "299_committee-governance-structure.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
