"""
Builder for pattern 158: One-page strategy — vision/pillars/metrics/priorities (4 rows).

Source HTML: _pattern-library/158_one-page-strategy.html
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

    # Eyebrow + title
    add_text(slide, "eyebrow", "Strategy on one page — vision · pillars · metrics · priorities",
             x_px=48, y_px=58, w_px=700, h_px=14,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "title",
             "<strong>Strategy on one page</strong> — share with all 1,200 employees as the single source of strategic truth",
             x_px=48, y_px=76, w_px=1100, h_px=28,
             font_size_px=20, color=TEXT_DARK, bold=True,
             emphasis_color=BRAND_PRIMARY)
    add_text(slide, "subtitle",
             "Three strategic pillars, key performance targets and the top four priorities for the next 12 months.",
             x_px=48, y_px=108, w_px=960, h_px=18,
             font_size_px=12, color=TEXT_MID)
    add_rect(slide, "brand-rule", 48, 132, 56, 3, BRAND_ACCENT)

    # Layout: top:148 left:48 right:48 bottom:36
    la_x = 48
    la_y = 148
    la_w = 1280 - 96
    la_h = 720 - 36 - la_y

    # Row 1: Vision banner
    r1_h = 58
    r1_y = la_y
    add_rect(slide, "vision-banner", la_x + 30, r1_y, la_w - 30, r1_h, BRAND_PRIMARY)
    add_text(slide, "tag-vision", "VISION",
             x_px=la_x, y_px=r1_y + 22, w_px=24, h_px=14,
             font_size_px=8, color=BRAND_ACCENT, bold=True, uppercase=True, align="center")
    add_text(slide, "vision-label", "VISION",
             x_px=la_x + 50, y_px=r1_y + 22, w_px=70, h_px=16,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True, align="center",
             padding_px=(2, 4, 2, 4))
    add_text(slide, "vision-text",
             "To be the most trusted digital transformation partner in financial services by 2028",
             x_px=la_x + 130, y_px=r1_y, w_px=la_w - 150, h_px=r1_h,
             font_size_px=13, color=WHITE, bold=True, anchor="middle")

    # Row 2: Pillars
    r2_y = r1_y + r1_h + 8
    r2_h = 168
    add_text(slide, "tag-pillars", "PILLARS",
             x_px=la_x, y_px=r2_y + r2_h // 2 - 8, w_px=24, h_px=14,
             font_size_px=8, color=BRAND_ACCENT, bold=True, uppercase=True, align="center")
    pillar_w = (la_w - 30 - 16) // 3
    pillars = [
        ("Pillar 01", "Customer Centricity", [
            "Redesign end-to-end client onboarding journey",
            "Launch real-time NPS feedback loop across all channels",
            "Embed customer advisory board into product roadmap"]),
        ("Pillar 02", "Operational Excellence", [
            "Consolidate ERP and finance systems onto single platform",
            "Automate 60% of back-office reconciliation workflows",
            "Reduce cost-to-income ratio from 58% to 48% by 2027"]),
        ("Pillar 03", "Digital Innovation", [
            "Launch AI-powered advisory platform in H1 2025",
            "Build open banking API ecosystem with 50+ partners",
            "Scale cloud-native infrastructure to 100% of core systems"]),
    ]
    for i, (num, title, items) in enumerate(pillars):
        n = i + 1
        px = la_x + 30 + i * (pillar_w + 8)
        card = add_rect(slide, f"pillar-{n}-bg", px, r2_y, pillar_w, r2_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        add_rect(slide, f"pillar-{n}-accent", px, r2_y, pillar_w, 3, BRAND_ACCENT)
        add_text(slide, f"pillar-{n}-num", num,
                 x_px=px + 12, y_px=r2_y + 10, w_px=pillar_w - 24, h_px=14,
                 font_size_px=9, color=BRAND_ACCENT, bold=True, uppercase=True)
        add_text(slide, f"pillar-{n}-title", title,
                 x_px=px + 12, y_px=r2_y + 26, w_px=pillar_w - 24, h_px=20,
                 font_size_px=13, color=TEXT_DARK, bold=True)
        add_rect(slide, f"pillar-{n}-divider", px + 12, r2_y + 50, 24, 2, BRAND_ACCENT_SOFT)
        items_text = "\n".join("· " + it for it in items)
        add_text(slide, f"pillar-{n}-list", items_text,
                 x_px=px + 12, y_px=r2_y + 60, w_px=pillar_w - 24, h_px=r2_h - 70,
                 font_size_px=10, color=TEXT_MID)

    # Row 3: Metrics
    r3_y = r2_y + r2_h + 8
    r3_h = 72
    add_text(slide, "tag-metrics", "METRICS",
             x_px=la_x, y_px=r3_y + r3_h // 2 - 8, w_px=24, h_px=14,
             font_size_px=8, color=BRAND_ACCENT, bold=True, uppercase=True, align="center")
    metric_w = (la_w - 30 - 16) // 3
    metrics = [("$2B", "Revenue target by 2028"),
               ("95%", "CSAT score target"),
               ("Top 3", "NPS ranking in sector")]
    for i, (val, label) in enumerate(metrics):
        n = i + 1
        mx = la_x + 30 + i * (metric_w + 8)
        tile = add_rect(slide, f"metric-{n}-bg", mx, r3_y, metric_w, r3_h, WHITE)
        tile.line.color.rgb = CARD_BORDER
        tile.line.width = 9525
        add_text(slide, f"metric-{n}-value", val,
                 x_px=mx, y_px=r3_y + 12, w_px=metric_w, h_px=28,
                 font_size_px=22, color=BRAND_PRIMARY, bold=True, align="center")
        add_text(slide, f"metric-{n}-label", label,
                 x_px=mx, y_px=r3_y + 42, w_px=metric_w, h_px=20,
                 font_size_px=9, color=TEXT_MID, align="center", uppercase=True, bold=True)

    # Row 4: Priorities
    r4_y = r3_y + r3_h + 8
    r4_h = 60
    add_text(slide, "tag-priorities", "12 MO",
             x_px=la_x, y_px=r4_y + r4_h // 2 - 8, w_px=24, h_px=14,
             font_size_px=8, color=BRAND_ACCENT, bold=True, uppercase=True, align="center")
    prio_w = (la_w - 30 - 24) // 4
    priorities = [("Priority 01", "Complete ERP migration"),
                  ("Priority 02", "Launch AI platform"),
                  ("Priority 03", "Hire 200 digital specialists"),
                  ("Priority 04", "Enter APAC markets")]
    for i, (num, txt) in enumerate(priorities):
        n = i + 1
        px = la_x + 30 + i * (prio_w + 8)
        tile = add_rect(slide, f"priority-{n}-bg", px, r4_y, prio_w, r4_h, CARD_BG)
        tile.line.color.rgb = CARD_BORDER
        tile.line.width = 9525
        add_text(slide, f"priority-{n}-num", num,
                 x_px=px, y_px=r4_y + 8, w_px=prio_w, h_px=14,
                 font_size_px=8, color=BRAND_ACCENT, bold=True, align="center", uppercase=True)
        add_text(slide, f"priority-{n}-text", txt,
                 x_px=px + 8, y_px=r4_y + 26, w_px=prio_w - 16, h_px=28,
                 font_size_px=11, color=TEXT_DARK, bold=True, align="center", anchor="middle")

    add_footer(slide, page_num=158)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "158_one-page-strategy.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
