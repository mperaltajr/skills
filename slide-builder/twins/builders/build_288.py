"""
Builder for pattern 288: Annotated Insight Panel (pull-quote + bar chart).

Source HTML: _pattern-library/288_annotated-insight-panel.html

Left 40%: pull-quote with serif quote-mark + attribution.
Right 60%: 8-row horizontal bar chart with 3 annotation callouts.
Center 4px brand-accent divider.
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


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="AI adoption is accelerating — <strong>but value capture remains uneven</strong>",
        subtitle="Survey of 1,200 enterprise leaders across 14 industries · Q1 2026",
    )

    # Body area
    body_y = 240
    body_h = 720 - body_y - 48

    # Divider (center, vertical 4px brand-accent)
    div_x = 56 + 460  # 40% of usable area
    add_rect(slide, "divider", div_x, body_y + 10, 4, body_h - 20, BRAND_ACCENT)

    # LEFT PANEL — pull quote
    lx = 56
    lw = div_x - lx - 24
    # Big quote mark
    add_text(
        slide, "quote-decoration", "“",
        x_px=lx, y_px=body_y - 10, w_px=80, h_px=80,
        font_size_px=72, color=BRAND_ACCENT, bold=True,
        font_name="Georgia",
    )
    # Pull quote
    add_text(
        slide, "pull-quote",
        "Only one in five enterprises has moved beyond pilot programmes to capture "
        "measurable, enterprise-wide value from AI investments.",
        x_px=lx, y_px=body_y + 70, w_px=lw, h_px=220,
        font_size_px=22, color=BRAND_PRIMARY, italic=True,
    )
    add_text(
        slide, "quote-attribution",
        "— Global AI Readiness Index, Accenture Research 2026",
        x_px=lx, y_px=body_y + 300, w_px=lw, h_px=20,
        font_size_px=11, color=TEXT_FAINT,
    )

    # RIGHT PANEL — bar chart
    rx = div_x + 24
    rw = 1280 - 56 - rx

    # Chart area: 8 rows, max bar = rw - 200 (label + value space)
    chart_x = rx + 140  # x where bars start
    chart_top = body_y + 10
    bar_h = 22
    bar_step = 38
    max_w = rw - 200

    # data: (label, pct, highlighted)
    bars = [
        ("Intelligent Automation", 78, True),
        ("Generative AI Pilots", 61, False),
        ("Predictive Analytics", 54, False),
        ("Decision Intelligence", 41, True),
        ("NLP / Conversational", 38, False),
        ("Computer Vision", 29, True),
        ("AI-Powered R&D", 22, False),
        ("Autonomous Agents", 11, False),
    ]

    for i, (label, pct, hi) in enumerate(bars):
        by = chart_top + i * bar_step
        # Label (right-aligned, ending at chart_x - 6)
        add_text(
            slide, f"bar-{i+1}-label", label,
            x_px=rx, y_px=by, w_px=132, h_px=bar_h,
            font_size_px=10, color=TEXT_MID, align="right", anchor="middle",
        )
        # Bar
        bw = int(max_w * pct / 100)
        color = BRAND_ACCENT if hi else BRAND_PRIMARY_MID
        add_rect(slide, f"bar-{i+1}", chart_x, by, bw, bar_h, color)
        # Value
        add_text(
            slide, f"bar-{i+1}-value", f"{pct}%",
            x_px=chart_x + bw + 8, y_px=by, w_px=50, h_px=bar_h,
            font_size_px=10, color=BRAND_PRIMARY, bold=True, anchor="middle",
        )

    # Callout bubbles (3 annotations) — placed in available space
    # CO1: Intelligent Automation (row 1) — "Highest adoption · mature ROI"
    co_y = chart_top + 8
    co_x = rx + 8
    co1 = add_rect(slide, "callout-1-bg", co_x, co_y, 150, 36, CARD_BG)
    co1.line.color.rgb = BRAND_ACCENT
    co1.line.width = 12700
    add_text(
        slide, "callout-1-title", "Highest adoption",
        x_px=co_x, y_px=co_y + 4, w_px=150, h_px=14,
        font_size_px=9, color=BRAND_ACCENT, bold=True, align="center",
    )
    add_text(
        slide, "callout-1-sub", "mature ROI story",
        x_px=co_x, y_px=co_y + 18, w_px=150, h_px=14,
        font_size_px=8, color=TEXT_MID, align="center",
    )

    # CO2: Decision Intelligence (row 4) — placed below the bar
    co2_y = chart_top + 3 * bar_step + bar_h + 4
    co2_x = chart_x + 240
    co2 = add_rect(slide, "callout-2-bg", co2_x, co2_y, 150, 30, CARD_BG)
    co2.line.color.rgb = BRAND_ACCENT
    co2.line.width = 12700
    add_text(
        slide, "callout-2-title", "Emerging priority",
        x_px=co2_x, y_px=co2_y + 2, w_px=150, h_px=14,
        font_size_px=9, color=BRAND_ACCENT, bold=True, align="center",
    )
    add_text(
        slide, "callout-2-sub", "C-suite investment rising",
        x_px=co2_x, y_px=co2_y + 16, w_px=150, h_px=12,
        font_size_px=8, color=TEXT_MID, align="center",
    )

    # CO3: Computer Vision (row 6) — placed to the right
    co3_y = chart_top + 5 * bar_step - 2
    co3_x = chart_x + 160
    co3 = add_rect(slide, "callout-3-bg", co3_x, co3_y, 150, 30, CARD_BG)
    co3.line.color.rgb = BRAND_ACCENT
    co3.line.width = 12700
    add_text(
        slide, "callout-3-title", "Specialist niche",
        x_px=co3_x, y_px=co3_y + 2, w_px=150, h_px=14,
        font_size_px=9, color=BRAND_ACCENT, bold=True, align="center",
    )
    add_text(
        slide, "callout-3-sub", "manufacturing-led growth",
        x_px=co3_x, y_px=co3_y + 16, w_px=150, h_px=12,
        font_size_px=8, color=TEXT_MID, align="center",
    )

    add_footer(slide, page_num=288)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "288_annotated-insight-panel.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
