"""
Dark variant of pattern 37: Comparison tier cards.

Source HTML: _pattern-library/37_comparison-tier-cards-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

CHECK_GOOD = RGBColor(0x6E, 0xE7, 0xA7)
CHECK_NO = RGBColor(0xFC, 0xA5, 0xA5)
CHECK_MEH = RGBColor(0xFC, 0xD3, 0x4D)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Three rollout options — pick one to learn from, not three to maintain.",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Two of these defer the decision; one gives us the evidence to make it. The middle path is sized to learn fast and reverse cleanly.",
        x_px=64, y_px=108, w_px=900, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    cards_top = 180
    cards_left = 64
    cards_right = 1280 - 64
    cards_w_total = cards_right - cards_left
    card_w = (cards_w_total - 40) // 3
    card_h = 420
    gap = 20

    eyebrows = ["Option A · Internal pilot", "Option B · Full practice rollout", "Option C · Firm-wide license"]
    headings = [
        "Quiet single-workstream test",
        "Structured pilot, measured against baseline",
        "Buy a vendor tool firm-wide",
    ]
    taglines = [
        "Low-visibility trial on one team",
        "All practice areas, evidence-based decision",
        "Procurement-led, off-the-shelf rollout",
    ]
    features = [
        [("ok", "One workstream"), ("ok", "4-week duration"), ("no", "Public commitment"),
         ("ok", "Reversible decision"), ("meh", "Limited learning")],
        [("ok", "All practice areas"), ("ok", "8 weeks with checkpoint"),
         ("ok", "Measurable outcomes"), ("ok", "Reversible at week 4"),
         ("ok", "Builds case for scale")],
        [("ok", "Vendor support"), ("no", "Tunable to our taste"),
         ("no", "Reversible"), ("no", "Internal IP"),
         ("no", "Compounds across decks")],
    ]
    stat_labels = ["Investment", "Investment", "Investment"]
    stat_values = ["~40 hr / 4 weeks", "~160 hr / 8 weeks", "$X license + ramp"]

    icon_color_map = {"ok": CHECK_GOOD, "no": CHECK_NO, "meh": CHECK_MEH}
    icon_glyph_map = {"ok": "✓", "no": "✗", "meh": "–"}

    for i in range(3):
        n = i + 1
        cx = cards_left + i * (card_w + gap)
        is_rec = (i == 1)

        if is_rec:
            card = add_rect(slide, f"card-{n}", cx, cards_top, card_w, card_h, BRAND_ACCENT_SOFT)
            card.line.color.rgb = BRAND_ACCENT_SOFT
            card.line.width = 25400
        else:
            card = add_rect(slide, f"card-{n}", cx, cards_top, card_w, card_h, CARD_BG_DARK)
            card.line.color.rgb = CARD_BORDER_DARK
            card.line.width = 9525

        if is_rec:
            badge_w = 130
            badge_x = cx + (card_w - badge_w) // 2
            add_rect(slide, "card-2-badge", badge_x, cards_top - 11, badge_w, 22, BRAND_ACCENT)
            add_text(
                slide, "card-2-badge-text", "RECOMMENDED",
                x_px=badge_x, y_px=cards_top - 11, w_px=badge_w, h_px=22,
                font_size_px=10, color=WHITE, bold=True, align="center",
                anchor="middle", letter_spacing_px=1.6,
            )

        head_top = cards_top + 24
        eyebrow_color = BRAND_PRIMARY if is_rec else BRAND_ACCENT_SOFT
        name_color = BRAND_PRIMARY if is_rec else WHITE
        tagline_color = BRAND_PRIMARY if is_rec else TEXT_ON_DARK_MID

        add_text(
            slide, f"card-{n}-eyebrow", eyebrows[i],
            x_px=cx + 22, y_px=head_top, w_px=card_w - 44, h_px=14,
            font_size_px=10, color=eyebrow_color, bold=True,
            letter_spacing_px=1.6, uppercase=True,
        )
        add_text(
            slide, f"card-{n}-heading", headings[i],
            x_px=cx + 22, y_px=head_top + 18, w_px=card_w - 44, h_px=44,
            font_size_px=16, color=name_color, bold=True,
        )
        add_text(
            slide, f"card-{n}-tagline", taglines[i],
            x_px=cx + 22, y_px=head_top + 64, w_px=card_w - 44, h_px=18,
            font_size_px=11, color=tagline_color, italic=True,
        )

        feat_top = cards_top + 122
        feat_row_h = 36
        for fi, (state, ftext) in enumerate(features[i]):
            fn = fi + 1
            fy = feat_top + fi * feat_row_h
            if fi > 0:
                rule_color = RGBColor(0x55, 0x36, 0x77) if is_rec else CARD_BORDER_DARK
                add_rect(slide, f"card-{n}-feat-{fn}-rule", cx + 22, fy, card_w - 44, 1, rule_color)
            add_text(
                slide, f"card-{n}-feat-{fn}-icon", icon_glyph_map[state],
                x_px=cx + 22, y_px=fy + 8, w_px=22, h_px=22,
                font_size_px=12, color=icon_color_map[state], bold=True, align="center",
            )
            add_text(
                slide, f"card-{n}-feat-{fn}-text", ftext,
                x_px=cx + 50, y_px=fy + 8, w_px=card_w - 70, h_px=22,
                font_size_px=12, color=BRAND_PRIMARY if is_rec else WHITE,
            )

        stat_y = cards_top + card_h - 56
        stat_rule_color = BRAND_PRIMARY if is_rec else CARD_BORDER_DARK
        add_rect(slide, f"card-{n}-stat-rule", cx + 22, stat_y, card_w - 44, 2, stat_rule_color)
        stat_label_color = BRAND_PRIMARY if is_rec else TEXT_ON_DARK_FAINT
        add_text(
            slide, f"card-{n}-stat-label", stat_labels[i],
            x_px=cx + 22, y_px=stat_y + 6, w_px=card_w - 44, h_px=12,
            font_size_px=9, color=stat_label_color, bold=True,
            letter_spacing_px=1.4, uppercase=True,
        )
        add_text(
            slide, f"card-{n}-stat-value", stat_values[i],
            x_px=cx + 22, y_px=stat_y + 22, w_px=card_w - 44, h_px=22,
            font_size_px=13, color=BRAND_PRIMARY if is_rec else WHITE, bold=True,
        )

    add_convergence(
        slide,
        "Pilot only the middle option — it gets you the data you need to decide on the others.",
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(
        slide, "source", "Source: [add source here or delete]",
        x_px=58, y_px=688, w_px=1100, h_px=16,
        font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True,
    )
    add_text(
        slide, "page-number", "37",
        x_px=1170, y_px=688, w_px=52, h_px=16,
        font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right",
    )
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "37d_comparison-tier-cards.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
