"""
Builder for pattern 40: Closing CTA — revival / primary ask + conditions.

Eyebrow + small title + brand-rule; primary-ask brand-primary band; ask caption;
conditions header; 3 sub-ask cards.

Source HTML: _pattern-library/40_closing-cta-revival.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Header zone (top=64) — small action title (not the big one)
    add_text(
        slide, "eyebrow", "The Ask",
        x_px=64, y_px=64, w_px=1000, h_px=14,
        font_size_px=11, color=BRAND_ACCENT, bold=True,
        letter_spacing_px=3, uppercase=True,
    )
    add_text(
        slide, "title", "One commitment. Three conditions. Four weeks.",
        x_px=64, y_px=84, w_px=1000, h_px=40,
        font_size_px=20, color=TEXT_MID, bold=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=130, w_px=48, h_px=3, fill_color=BRAND_ACCENT)

    # Primary ask band (brand-primary)
    pa_top = 168
    pa_left = 64
    pa_w = 1280 - 128
    pa_h = 150
    add_rect(slide, "primary-ask", pa_left, pa_top, pa_w, pa_h, BRAND_PRIMARY)
    # 6px accent strip on left
    add_rect(slide, "primary-ask-accent", pa_left, pa_top, 6, pa_h, BRAND_ACCENT)

    add_text(
        slide, "primary-ask-label", "PRIMARY ASK",
        x_px=pa_left + 44, y_px=pa_top + 28, w_px=pa_w - 88, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
        letter_spacing_px=2.5, uppercase=True,
    )
    add_text(
        slide, "primary-ask-text",
        "Sponsor a four-week pilot on one priority workstream — and measure it against the baseline.",
        x_px=pa_left + 44, y_px=pa_top + 50, w_px=pa_w - 88, h_px=70,
        font_size_px=24, color=WHITE, bold=True,
    )

    add_text(
        slide, "ask-caption", "Two-level commitment from program leadership.",
        x_px=pa_left, y_px=pa_top + pa_h + 12, w_px=pa_w, h_px=18,
        font_size_px=12, color=TEXT_FAINT, italic=True,
    )

    # Conditions header
    ch_y = pa_top + pa_h + 50
    add_text(
        slide, "conditions-label", "CONDITIONS TO SUCCEED",
        x_px=pa_left, y_px=ch_y, w_px=300, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY, bold=True,
        letter_spacing_px=2.5, uppercase=True,
    )
    add_text(
        slide, "conditions-hint", "what we need from you to make the pilot real",
        x_px=pa_left + 220, y_px=ch_y, w_px=600, h_px=14,
        font_size_px=11, color=TEXT_FAINT, italic=True,
    )

    # Sub-ask cards (3, gap 16) — grown to fill bottom whitespace
    sa_top = ch_y + 30
    sa_h = 190
    sa_gap = 16
    sa_w = (pa_w - 2 * sa_gap) // 3

    sub_data = [
        ("1", "Tooling", "Access for 4 people on the pilot team.", "Licenses + sandbox by week 1"),
        ("2", "Time", "One 90-minute coached storyline per deck.", "~3 sessions over 4 weeks"),
        ("3", "Visibility", "Weekly 15-min review with the program MD.", "Friday standing slot"),
    ]

    for i, (num, label, body, meta) in enumerate(sub_data):
        n = i + 1
        sx = pa_left + i * (sa_w + sa_gap)
        card = add_rect(slide, f"sub-ask-{n}", sx, sa_top, sa_w, sa_h, WHITE)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Left accent border (3px)
        add_rect(slide, f"sub-ask-{n}-accent", sx, sa_top, 3, sa_h, BRAND_ACCENT)

        # Num circle (rectangle approximation)
        add_rect(slide, f"sub-ask-{n}-num-bg", sx + 18, sa_top + 18, 22, 22,
                 RGBColor(0xF8, 0xF4, 0xFC))
        add_text(
            slide, f"sub-ask-{n}-num", num,
            x_px=sx + 18, y_px=sa_top + 18, w_px=22, h_px=22,
            font_size_px=11, color=BRAND_PRIMARY, bold=True, align="center",
            anchor="middle",
        )
        # Label
        add_text(
            slide, f"sub-ask-{n}-label", label,
            x_px=sx + 50, y_px=sa_top + 22, w_px=sa_w - 66, h_px=18,
            font_size_px=16, color=BRAND_PRIMARY, bold=True,
        )
        # Body
        add_text(
            slide, f"sub-ask-{n}-body", body,
            x_px=sx + 18, y_px=sa_top + 50, w_px=sa_w - 36, h_px=32,
            font_size_px=13, color=TEXT_DARK,
        )
        # Meta
        add_text(
            slide, f"sub-ask-{n}-meta", meta,
            x_px=sx + 18, y_px=sa_top + sa_h - 22, w_px=sa_w - 36, h_px=14,
            font_size_px=11, color=TEXT_MID,
        )

    # Convergence band — close the gap before the footer
    conv_y = 720 - 56 - 40
    conv_h = 40
    add_rect(slide, "convergence-bg", 64, conv_y, pa_w, conv_h, BRAND_PRIMARY)
    add_rect(slide, "convergence-accent", 64, conv_y, 3, conv_h, BRAND_ACCENT)
    add_text(
        slide, "convergence",
        "Decide this week — pilot kicks off Monday or slips two weeks.",
        x_px=64 + 18, y_px=conv_y, w_px=pa_w - 36, h_px=conv_h,
        font_size_px=13, color=WHITE, italic=True, bold=True, anchor="middle",
    )

    # Footer (pattern 40 has a 3-part footer with center signature)
    add_text(
        slide, "footer-center", "Mario Peralta · Strategy Manager · May 2026",
        x_px=440, y_px=720 - 14 - 12, w_px=400, h_px=14,
        font_size_px=10, color=TEXT_MID, align="center",
    )
    add_text(slide, "page-number", "40",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "40_closing-cta-revival.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
