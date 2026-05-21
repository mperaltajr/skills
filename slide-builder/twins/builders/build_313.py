"""
Builder for pattern 313: 2-bucket top/bottom stacked.

Same visual treatment as 312 but rotated to vertical (two bands stacked). Each band
has a strip header on the left, heading, bullets, and a metric chip on the right.

Source HTML: _pattern-library/313_2bucket-top-bottom-stacked.html
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


def _band(slide, n, x, y, w, h, *, strip_color, section_label,
          headline, bullets, chip_value, chip_label):
    panel = add_rect(slide, f"band-{n}-bg", x, y, w, h, CARD_BG)
    panel.line.color.rgb = CARD_BORDER
    panel.line.width = 9525
    # Accent strip top
    add_rect(slide, f"band-{n}-accent", x, y, w, 4, strip_color)
    # Section pill
    add_rect(slide, f"band-{n}-pill", x + 20, y + 18, 76, 20, strip_color)
    add_text(
        slide, f"band-{n}-pill-text", section_label.upper(),
        x_px=x + 20, y_px=y + 18, w_px=76, h_px=20,
        font_size_px=9, color=WHITE, bold=True, align="center", anchor="middle",
        letter_spacing_px=1.4,
    )
    # Headline
    add_text(
        slide, f"band-{n}-headline", headline,
        x_px=x + 110, y_px=y + 18, w_px=w - 320, h_px=22,
        font_size_px=14, color=BRAND_PRIMARY, bold=True,
    )
    # Bullets
    bullets_y = y + 60
    for bi, b in enumerate(bullets):
        bn = bi + 1
        by = bullets_y + bi * 30
        add_rect(slide, f"band-{n}-bullet-{bn}-dot",
                 x + 20, by + 7, 5, 5, BRAND_ACCENT_SOFT)
        add_text(
            slide, f"band-{n}-bullet-{bn}-text", b,
            x_px=x + 32, y_px=by, w_px=w - 240, h_px=28,
            font_size_px=11, color=TEXT_MID,
        )
    # Right-side chip
    chip_w = 180
    chip_h = 76
    chip_x = x + w - chip_w - 20
    chip_y = y + (h - chip_h) // 2
    chip = add_rect(slide, f"band-{n}-chip", chip_x, chip_y, chip_w, chip_h, WHITE)
    chip.line.color.rgb = CARD_BORDER
    chip.line.width = 9525
    add_text(
        slide, f"band-{n}-chip-value", chip_value,
        x_px=chip_x, y_px=chip_y + 10, w_px=chip_w, h_px=34,
        font_size_px=22, color=BRAND_ACCENT, bold=True, align="center",
    )
    add_text(
        slide, f"band-{n}-chip-label", chip_label.upper(),
        x_px=chip_x + 10, y_px=chip_y + 46, w_px=chip_w - 20, h_px=20,
        font_size_px=9, color=BRAND_PRIMARY_MID, bold=True, align="center",
        letter_spacing_px=1.4,
    )


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Two distinct priorities demand <strong>parallel attention</strong>",
        subtitle="Each workstream carries equal weight — sequencing introduces avoidable risk.",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap = 12
    band_h = (body_h - gap) // 2

    _band(
        slide, 1, body_left, body_top, body_w, band_h,
        strip_color=BRAND_PRIMARY,
        section_label="Section 1",
        headline="Stabilise the core platform before extending capability",
        bullets=[
            "Legacy debt in authentication layer is causing 23% of production incidents — remediation is the critical path before any new feature work begins.",
            "Infrastructure observability gaps mean failures are detected reactively; a unified telemetry stack must be in place by end of Q2 to support SLAs.",
            "Technical steering committee has approved a six-week hardening sprint; resourcing is confirmed and delivery lead is assigned.",
        ],
        chip_value="23%",
        chip_label="Incident reduction target",
    )
    _band(
        slide, 2, body_left, body_top + band_h + gap, body_w, band_h,
        strip_color=BRAND_PRIMARY_MID,
        section_label="Section 2",
        headline="Accelerate go-to-market while the foundation is being hardened",
        bullets=[
            "Three enterprise pilots are scheduled for H2; delaying GTM activities to wait for platform stability would push revenue recognition into next year.",
            "Product team can operate on a feature-frozen branch, enabling parallel progress without dependency on the hardening sprint deliverables.",
            "Commercial commitments to pilot clients have been made — maintaining the timeline protects relationship trust and deal expansion potential.",
        ],
        chip_value="3",
        chip_label="Enterprise pilots confirmed",
    )

    add_footer(slide, page_num=313)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "313_2bucket-top-bottom-stacked.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
