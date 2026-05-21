"""
Builder for pattern 105: Time series with confidence band (chart-canvas pattern).

Source HTML: _pattern-library/105_time-series-confidence-band.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_MID, TEXT_FAINT,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="<strong>ARR on track</strong> — forecast band narrows as pipeline converts",
        subtitle="Projected ARR, Q1 2024 - Q4 2025 - $M - Central trend, 80% confidence band, actuals vs. forecast",
        title_h=64,
        subtitle_h=24,
        brand_rule_w=56,
    )

    # Legend (top-right area near chart-canvas)
    leg_y = 152
    leg_items = [
        ("Actuals", BRAND_ACCENT),
        ("Forecast", BRAND_ACCENT_SOFT),
        ("80% confidence band", BRAND_ACCENT_SOFT),
    ]
    leg_x = 1280 - 56 - 360
    for i, (label, color) in enumerate(leg_items):
        n = i + 1
        x = leg_x + i * 120
        add_rect(slide, f"legend-{n}-swatch", x, leg_y + 6, 16, 8, color)
        add_text(slide, f"legend-{n}-label", label,
                 x_px=x + 22, y_px=leg_y, w_px=98, h_px=16,
                 font_size_px=10, color=TEXT_MID, bold=True)

    # Chart canvas placeholder (picture-asset SVG)
    add_rect(slide, "chart-canvas", 80, 180, 1280 - 80 - 48, 720 - 180 - 100,
             CARD_BG)

    # Convergence band
    add_convergence(
        slide,
        "Band narrows from +/-$16M today to +/-$12M by Q4 2025 as late-stage deals convert "
        "— Q3 forecast range is tight enough to commit to board guidance.",
        bottom_px=56, height_px=44,
    )

    add_footer(slide, page_num=105)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "105_time-series-confidence-band.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
