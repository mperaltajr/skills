"""
Builder for pattern 234: Insight text findings + callout panel with key numbers + quote.

Source HTML: _pattern-library/234_insight-text-callout-panel.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT,
    CARD_BG, CARD_BORDER,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Three findings that <strong>redefine</strong> the operating model",
        subtitle="Synthesised from 42 stakeholder interviews and benchmarking across 6 peer organisations",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # Body: top:148, left:48, right:48, bottom 56
    body_top = 148
    body_h = 516
    panel_gap = 48
    total_w = 1184
    # 65% / 35%
    left_w = int((total_w - panel_gap) * 0.65)
    right_w = total_w - panel_gap - left_w
    left_x = 48
    divider_x = left_x + left_w + panel_gap // 2
    right_x = divider_x + panel_gap // 2

    # Divider line
    add_rect(slide, "panel-divider", divider_x, body_top, 1, body_h, CARD_BORDER)

    # Left: 3 findings stacked
    findings = [
        ("01", "Decision rights are fragmented across four layers of governance",
         "Approval authority is split between regional, functional, and global leads with no clear escalation path. This creates an average 18-day delay for cross-functional decisions and erodes accountability at every tier."),
        ("02", "Data flows do not support the speed required for real-time pricing",
         "Core pricing signals reach the commercial team with a 72-hour lag due to batch processing in the legacy ERP. Competitors operating on event-driven architectures reprice 40× faster on average."),
        ("03", "Talent density in analytics is concentrated in one cost centre",
         "82% of qualified data practitioners sit in a single shared-services unit, creating a structural bottleneck. Business units waiting on analytics support report an average queue time of 3.4 weeks per request."),
    ]
    find_h = body_h // 3
    for i, (num, title, body_text) in enumerate(findings):
        n = i + 1
        fy = body_top + i * find_h
        if i > 0:
            add_rect(slide, f"section-{n}-divider", left_x, fy, left_w - 16, 1, CARD_BORDER)
        add_text(slide, f"section-{n}-num", num,
                 x_px=left_x, y_px=fy + 16, w_px=24, h_px=18,
                 font_size_px=11, color=BRAND_ACCENT, bold=True)
        add_text(slide, f"section-{n}-name", title,
                 x_px=left_x + 28, y_px=fy + 14, w_px=left_w - 44, h_px=22,
                 font_size_px=14, color=BRAND_PRIMARY, bold=True)
        add_text(slide, f"section-{n}-body", body_text,
                 x_px=left_x + 28, y_px=fy + 42, w_px=left_w - 44, h_px=find_h - 50,
                 font_size_px=11, color=TEXT_DARK)

    # Right: callout panel
    panel = add_rect(slide, "annot-panel", right_x, body_top, right_w, body_h, CARD_BG)
    panel.line.color.rgb = CARD_BORDER
    panel.line.width = 9525
    add_text(slide, "annot-header", "KEY NUMBERS",
             x_px=right_x + 20, y_px=body_top + 20, w_px=right_w - 40, h_px=18,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)

    stats = [
        ("18d", "Average delay on cross-functional decisions", "Source: Governance audit, Q1 2026"),
        ("40×", "Faster repricing by event-driven competitors", "Source: Benchmarking study"),
        ("82%", "Analytics talent concentrated in one unit", "Source: HR capability mapping, Feb 2026"),
    ]
    stat_top = body_top + 48
    stat_h = 84
    for i, (val, lab, src) in enumerate(stats):
        n = i + 1
        sy = stat_top + i * stat_h
        if i > 0:
            add_rect(slide, f"metric-{n}-divider", right_x + 20, sy, right_w - 40, 1, CARD_BORDER)
        add_text(slide, f"metric-{n}-value", val,
                 x_px=right_x + 20, y_px=sy + 8, w_px=right_w - 40, h_px=36,
                 font_size_px=32, color=BRAND_PRIMARY, bold=True)
        add_text(slide, f"metric-{n}-label", lab,
                 x_px=right_x + 20, y_px=sy + 48, w_px=right_w - 40, h_px=18,
                 font_size_px=11, color=TEXT_MID)
        add_text(slide, f"metric-{n}-source", src,
                 x_px=right_x + 20, y_px=sy + 66, w_px=right_w - 40, h_px=14,
                 font_size_px=9, color=TEXT_FAINT)

    # Quote
    quote_y = stat_top + 3 * stat_h + 16
    add_rect(slide, "quote-rule", right_x + 20, quote_y, 3, 64, BRAND_ACCENT)
    add_text(slide, "quote-text",
             "“Speed is not a technology problem — it is a structural one. The architecture of accountability must change before the data architecture can follow.”",
             x_px=right_x + 30, y_px=quote_y, w_px=right_w - 50, h_px=80,
             font_size_px=12, color=BRAND_PRIMARY_MID, italic=True)

    add_footer(slide, page_num=234)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "234_insight-text-callout-panel.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
