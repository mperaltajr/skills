"""
Builder for pattern 160: Strategy on a Page — Vision/Mission + Pillars + OKRs + Initiatives.

Source HTML: _pattern-library/160_strategy-on-a-page.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title (28px brand-primary, "Strategy" in brand-accent)
    add_text(slide, "title", "Our <strong>Strategy</strong> on a Page",
             x_px=48, y_px=58, w_px=900, h_px=36,
             font_size_px=26, color=BRAND_PRIMARY, bold=True,
             emphasis_color=BRAND_ACCENT)
    add_text(slide, "subtitle",
             "Enterprise direction, pillars, and measurable outcomes — FY2026",
             x_px=48, y_px=96, w_px=900, h_px=18,
             font_size_px=12, color=TEXT_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 122, 64, 3, BRAND_ACCENT)

    # Body: top:140 left:48 right:48 bottom:60
    by = 140
    bx = 48
    bw = 1280 - 96
    bh = 720 - 60 - by

    # Row 1: 3-col main grid (220 / 1fr / 230)
    r1_h = bh - 90  # leave room for initiatives row
    col1_w = 220
    col3_w = 230
    col2_w = bw - col1_w - col3_w - 14
    col1_x = bx
    col2_x = bx + col1_w + 7
    col3_x = bx + col1_w + 14 + col2_w

    # Col 1: Vision + Mission stacked
    c1_card_h = (r1_h - 7) // 2
    # Vision card
    v_card = add_rect(slide, "vision-card", col1_x, by, col1_w, c1_card_h, CARD_BG)
    v_card.line.color.rgb = CARD_BORDER
    v_card.line.width = 9525
    add_text(slide, "vision-label", "VISION",
             x_px=col1_x + 12, y_px=by + 10, w_px=200, h_px=12,
             font_size_px=8, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "vision-text",
             "\"To be the most trusted partner in human-centered digital transformation by 2028.\"",
             x_px=col1_x + 12, y_px=by + 26, w_px=col1_w - 24, h_px=c1_card_h - 36,
             font_size_px=11, color=BRAND_PRIMARY, italic=True, bold=True)
    # Mission card
    m_y = by + c1_card_h + 7
    m_card = add_rect(slide, "mission-card", col1_x, m_y, col1_w, c1_card_h, CARD_BG)
    m_card.line.color.rgb = CARD_BORDER
    m_card.line.width = 9525
    add_text(slide, "mission-label", "MISSION",
             x_px=col1_x + 12, y_px=m_y + 10, w_px=200, h_px=12,
             font_size_px=8, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "mission-text",
             "We accelerate client impact through technology, talent, and data — delivering "
             "measurable outcomes at enterprise scale.",
             x_px=col1_x + 12, y_px=m_y + 26, w_px=col1_w - 24, h_px=c1_card_h - 36,
             font_size_px=11, color=TEXT_DARK)

    # Col 2: Pillars
    p_card = add_rect(slide, "pillars-card", col2_x, by, col2_w, r1_h, CARD_BG)
    p_card.line.color.rgb = CARD_BORDER
    p_card.line.width = 9525
    add_text(slide, "pillars-label", "STRATEGIC PILLARS",
             x_px=col2_x + 12, y_px=by + 10, w_px=180, h_px=12,
             font_size_px=8, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_rect(slide, "pillars-accent", col2_x + 200, by + 14, col2_w - 220, 2, BRAND_ACCENT)

    pillars = [
        ("1", "AI-Led Delivery at Scale",
         "Embed AI-native tooling into every engagement; reduce delivery cycle time by 30% through intelligent automation and co-pilot platforms."),
        ("2", "Talent & Capability Edge",
         "Upskill 80% of delivery staff on next-gen tools; build differentiated centers of excellence in cloud, data, and security."),
        ("3", "Client-Centric Growth",
         "Deepen relationships in top-20 accounts; grow share-of-wallet by 25% through outcome-based commercial models and proactive advisory."),
    ]
    pillar_row_h = (r1_h - 36) // 3
    for i, (num, name, desc) in enumerate(pillars):
        py = by + 32 + i * pillar_row_h
        # Numeral circle
        add_rect(slide, f"pillar-{i+1}-num-bg", col2_x + 14, py + 4, 20, 20, BRAND_PRIMARY)
        add_text(slide, f"pillar-{i+1}-num", num,
                 x_px=col2_x + 14, y_px=py + 4, w_px=20, h_px=20,
                 font_size_px=10, color=WHITE, bold=True, align="center", anchor="middle")
        # Name + desc
        add_text(slide, f"pillar-{i+1}-name", name,
                 x_px=col2_x + 44, y_px=py + 2, w_px=col2_w - 60, h_px=18,
                 font_size_px=11, color=BRAND_PRIMARY, bold=True)
        add_text(slide, f"pillar-{i+1}-desc", desc,
                 x_px=col2_x + 44, y_px=py + 20, w_px=col2_w - 60, h_px=pillar_row_h - 22,
                 font_size_px=10, color=TEXT_MID)
        if i < 2:
            add_rect(slide, f"pillar-{i+1}-divider",
                     col2_x + 14, py + pillar_row_h - 2, col2_w - 28, 1, CARD_BORDER)

    # Col 3: OKRs
    o_card = add_rect(slide, "okrs-card", col3_x, by, col3_w, r1_h, CARD_BG)
    o_card.line.color.rgb = CARD_BORDER
    o_card.line.width = 9525
    add_text(slide, "okrs-label", "OKRs / KPIs",
             x_px=col3_x + 12, y_px=by + 10, w_px=200, h_px=12,
             font_size_px=8, color=BRAND_ACCENT, bold=True, uppercase=True)
    okrs = [
        ("Accelerate AI-driven revenue", "AI-attributed revenue ≥ $500M by Q4"),
        ("Strengthen talent pipeline",   "80% workforce AI-certified by H2"),
        ("Grow strategic accounts",      "NPS ≥ 72; wallet share +25% YoY"),
    ]
    okr_row_h = (r1_h - 36) // 3
    for i, (obj, kr) in enumerate(okrs):
        oy = by + 32 + i * okr_row_h
        add_text(slide, f"okr-{i+1}-obj-pill", "O",
                 x_px=col3_x + 12, y_px=oy + 2, w_px=14, h_px=12,
                 font_size_px=7, color=WHITE, bold=True, align="center",
                 bg_fill=BRAND_ACCENT, padding_px=(0, 0, 0, 0))
        add_text(slide, f"okr-{i+1}-objective", obj,
                 x_px=col3_x + 30, y_px=oy, w_px=col3_w - 42, h_px=16,
                 font_size_px=10, color=BRAND_PRIMARY_MID, bold=True)
        add_text(slide, f"okr-{i+1}-kr", "KR  " + kr,
                 x_px=col3_x + 30, y_px=oy + 18, w_px=col3_w - 42, h_px=okr_row_h - 22,
                 font_size_px=9, color=TEXT_MID)
        if i < 2:
            add_rect(slide, f"okr-{i+1}-divider",
                     col3_x + 12, oy + okr_row_h - 2, col3_w - 24, 1, CARD_BORDER)

    # Row 2: Initiatives strip (4 cards, all brand-primary)
    init_y = by + r1_h + 7
    init_h = 82
    iw = (bw - 21) // 4
    initiatives = [
        ("Initiative 01", "GenAI Rapid Deployment Program",
         "Deploy GenAI co-pilots across top 10 client engagements by Q2"),
        ("Initiative 02", "Cloud Migration Accelerator",
         "Move 60% of legacy workloads to hybrid cloud within 18 months"),
        ("Initiative 03", "Data Fabric & Governance",
         "Unified data platform live in 5 priority accounts by Q3"),
        ("Initiative 04", "Cyber Resilience Baseline",
         "Zero-trust architecture rolled out across all internal systems by EOY"),
    ]
    for i, (num, title, desc) in enumerate(initiatives):
        ix = bx + i * (iw + 7)
        add_rect(slide, f"initiative-{i+1}-bg", ix, init_y, iw, init_h, BRAND_PRIMARY)
        add_rect(slide, f"initiative-{i+1}-accent", ix, init_y, iw, 2, BRAND_ACCENT)
        add_text(slide, f"initiative-{i+1}-num", num,
                 x_px=ix + 12, y_px=init_y + 10, w_px=iw - 24, h_px=12,
                 font_size_px=8, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
        add_text(slide, f"initiative-{i+1}-title", title,
                 x_px=ix + 12, y_px=init_y + 26, w_px=iw - 24, h_px=20,
                 font_size_px=11, color=WHITE, bold=True)
        add_text(slide, f"initiative-{i+1}-desc", desc,
                 x_px=ix + 12, y_px=init_y + 48, w_px=iw - 24, h_px=init_h - 54,
                 font_size_px=9, color=BRAND_ACCENT_SOFT)

    add_footer(slide, page_num=160)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "160_strategy-on-a-page.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
