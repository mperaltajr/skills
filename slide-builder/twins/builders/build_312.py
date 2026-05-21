"""
Builder for pattern 312: 2-bucket left/right split.

Bucket family base layout: numbered bucket cards with a strip header (brand-primary
for first, brand-primary-mid for second), heading, bullets, and a metric callout.
Used as the visual template for the 12-pattern bucket family (312-326).

Source HTML: _pattern-library/312_2bucket-left-right-split.html
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


def _bucket_panel(slide, n, x, y, w, h, *, strip_color, strip_label,
                  heading, bullets, metric_value, metric_label):
    panel = add_rect(slide, f"bucket-{n}-panel", x, y, w, h, CARD_BG)
    panel.line.color.rgb = CARD_BORDER
    panel.line.width = 9525
    # Strip header
    strip_h = 44
    add_rect(slide, f"bucket-{n}-strip", x, y, w, strip_h, strip_color)
    add_text(
        slide, f"bucket-{n}-strip-title", strip_label,
        x_px=x + 16, y_px=y, w_px=w - 32, h_px=strip_h,
        font_size_px=14, color=WHITE, bold=True, anchor="middle",
    )
    # Body
    body_x = x + 20
    body_y = y + strip_h + 18
    body_w = w - 40
    # Heading
    add_text(
        slide, f"bucket-{n}-heading", heading,
        x_px=body_x, y_px=body_y, w_px=body_w, h_px=40,
        font_size_px=13, color=BRAND_PRIMARY, bold=True,
    )
    # Bullets
    bullets_y = body_y + 48
    for bi, b in enumerate(bullets):
        bn = bi + 1
        by = bullets_y + bi * 36
        add_rect(slide, f"bucket-{n}-bullet-{bn}-dot",
                 body_x, by + 7, 5, 5, BRAND_ACCENT_SOFT)
        add_text(
            slide, f"bucket-{n}-bullet-{bn}-text", b,
            x_px=body_x + 12, y_px=by, w_px=body_w - 12, h_px=34,
            font_size_px=11, color=TEXT_MID,
        )
    # Metric callout at bottom
    metric_h = 64
    metric_y = y + h - metric_h - 18
    metric_w = body_w
    metric_box = add_rect(slide, f"bucket-{n}-metric-bg",
                          body_x, metric_y, metric_w, metric_h, WHITE)
    metric_box.line.color.rgb = CARD_BORDER
    metric_box.line.width = 9525
    add_text(
        slide, f"bucket-{n}-metric-value", metric_value,
        x_px=body_x, y_px=metric_y + 6, w_px=metric_w, h_px=36,
        font_size_px=32, color=BRAND_ACCENT, bold=True, align="center",
    )
    add_text(
        slide, f"bucket-{n}-metric-label", metric_label.upper(),
        x_px=body_x, y_px=metric_y + 42, w_px=metric_w, h_px=14,
        font_size_px=10, color=TEXT_MID, align="center",
        letter_spacing_px=1.2,
    )


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Two perspectives, <strong>one clear picture</strong>",
        subtitle="Side-by-side comparison of two strategic dimensions or workstreams",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # ── Two panels side-by-side ──
    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap = 12
    panel_w = (body_w - gap) // 2

    _bucket_panel(
        slide, 1, body_left, body_top, panel_w, body_h,
        strip_color=BRAND_PRIMARY,
        strip_label="Bucket A",
        heading="Primary heading or theme for this section",
        bullets=[
            "First supporting point that elaborates on the bucket theme",
            "Second key insight or finding relevant to this dimension",
            "Third data point or recommendation tied to the argument",
            "Fourth point closing the narrative for this bucket",
        ],
        metric_value="00%",
        metric_label="Metric or KPI label",
    )
    _bucket_panel(
        slide, 2, body_left + panel_w + gap, body_top, panel_w, body_h,
        strip_color=BRAND_PRIMARY_MID,
        strip_label="Bucket B",
        heading="Primary heading or theme for this section",
        bullets=[
            "First supporting point that elaborates on the bucket theme",
            "Second key insight or finding relevant to this dimension",
            "Third data point or recommendation tied to the argument",
            "Fourth point closing the narrative for this bucket",
        ],
        metric_value="00%",
        metric_label="Metric or KPI label",
    )

    add_footer(slide, page_num=312)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "312_2bucket-left-right-split.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
