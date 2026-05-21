"""
Builder for pattern 24: Four focus areas with stats — 4 full-height cards.

Variant chrome — title-band brand-primary, project-label on white over band.
Source HTML: _pattern-library/24_focus-areas-with-stats.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor


def build():
    prs, slide = new_slide()

    # === Title band (brand-primary, sits below chrome) ===
    add_rect(slide, "title-band", x_px=0, y_px=44, w_px=1280, h_px=72, fill_color=BRAND_PRIMARY)
    add_text(
        slide, "title",
        "Four focus areas deliver the integrated, intelligent enterprise",
        x_px=40, y_px=66, w_px=1200, h_px=36,
        font_size_px=26, color=WHITE, bold=False,
    )
    add_rect(slide, "brand-rule", x_px=0, y_px=116, w_px=1280, h_px=3, fill_color=BRAND_ACCENT)

    # === Chrome (standard positions, rendered on top of band) ===
    add_chrome(slide)

    # === 4 cards row: top=134, left=40, right=40, height=538, gap=16 ===
    # card_w = (1280 - 80 - 48) / 4 = 288
    grid_left = 40
    card_w = 288
    card_h = 538
    gap = 16
    card_top = 134

    headings = ["Strategy & Direction", "Technology & AI", "People & Talent", "Delivery & Value"]
    bodies = [
        "Align D&T roadmap to enterprise priorities and value bundles. Build integrated intelligent enterprise vision with clear FY26 milestones. Outside-in view of industry disruption. Cross-portfolio governance for sequencing.",
        "JARVIS agentic platform scaled across 40k enterprise employees. Tech Mod: Odyssey Joint Council governing modernization. Journey 2 Cloud Phase 2 architecture approved. GitHub Copilot active for 3,800+ developers.",
        "Prometheus talent rebrand — thought leadership and capability showcase. AIQ Learning: 10,000+ courses completed; exec coaching program active. Recognition programs running. Workforce upskilling aligned to roadmap.",
        "25+ DRIVE value bundles — $1.2M revenue, $500K savings delivered. Best peak performance in 10 years. Scorecard shifting to delivery-focused outcomes. Q4 outlook: 8 incremental bundles, $400K additional benefit.",
    ]
    metric_values = ["4", "40k", "10k+", "25+"]
    metric_labels = ["Strategic Pillars", "AI Users Enabled", "Courses Completed", "DRIVE Bundles Live"]

    for i in range(4):
        n = i + 1
        cx = grid_left + i * (card_w + gap)

        # Top brand-primary accent strip (3px)
        add_rect(slide, f"card-{n}-accent", cx, card_top, card_w, 3, BRAND_PRIMARY)

        # Card body (background + border)
        body = add_rect(slide, f"card-{n}-body", cx, card_top + 3, card_w, card_h - 3, CARD_BG)
        body.line.color.rgb = CARD_BORDER
        body.line.width = 9525

        # Header area (top section, light card bg)
        header_h = 110
        # Icon placeholder (48x48 box, centered)
        icon_x = cx + (card_w - 48) // 2
        add_rect(slide, f"card-{n}-icon", icon_x, card_top + 20, 48, 48, BRAND_ACCENT)

        # Card name (centered, uppercase)
        add_text(
            slide, f"card-{n}-heading", headings[i],
            x_px=cx + 12, y_px=card_top + 76, w_px=card_w - 24, h_px=30,
            font_size_px=13, color=BRAND_PRIMARY, bold=True, align="center",
            uppercase=True, letter_spacing_px=0.8,
        )

        # Card body (bullets — collapsed to single body block)
        body_top = card_top + header_h + 16
        body_h = card_h - header_h - 16 - 80  # leaves room for stat
        add_text(
            slide, f"card-{n}-body", bodies[i],
            x_px=cx + 16, y_px=body_top, w_px=card_w - 32, h_px=body_h,
            font_size_px=12, color=TEXT_DARK,
        )

        # Bottom stat callout — brand-primary fill
        stat_h = 80
        stat_y = card_top + card_h - stat_h
        add_rect(slide, f"card-{n}-stat-bg", cx, stat_y, card_w, stat_h, BRAND_PRIMARY)
        add_text(
            slide, f"metric-{n}-value", metric_values[i],
            x_px=cx, y_px=stat_y + 14, w_px=card_w, h_px=32,
            font_size_px=28, color=BRAND_ACCENT, bold=True, align="center",
        )
        add_text(
            slide, f"metric-{n}-label", metric_labels[i],
            x_px=cx, y_px=stat_y + 50, w_px=card_w, h_px=16,
            font_size_px=11, color=RGBColor(0xE8, 0xE8, 0xE8), align="center",
            uppercase=True,
        )

    add_footer(slide, page_num=24)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "24_focus-areas-with-stats.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
