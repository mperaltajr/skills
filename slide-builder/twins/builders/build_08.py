"""
Builder for pattern 08: Closing CTA — single focal point with signature.

Small title block + dominant primary-ask band (brand-primary, accent left stripe)
+ three demoted sub-ask cards in a 3-column thin-divider grid.

Source HTML: _pattern-library/08_closing-cta-signature.html
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


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # --- Canonical title block (bottom-anchored title, brand rule at y≈132) ---
    add_title_block(
        slide,
        title="One commitment from program leadership.",
        subtitle="Everything below the ask is a condition of making it real.",
    )

    # --- THE FOCAL POINT: primary-ask band ---
    ask_x = 64
    ask_y = 200
    ask_w = 1280 - 128
    ask_h = 200

    add_rect(slide, "primary-ask-bg", ask_x, ask_y, ask_w, ask_h, BRAND_PRIMARY)
    # Left accent stripe
    add_rect(slide, "primary-ask-accent", ask_x, ask_y, 6, ask_h, BRAND_ACCENT)

    add_text(
        slide, "primary-ask-label", "Primary ask",
        x_px=ask_x + 64, y_px=ask_y + 36, w_px=400, h_px=18,
        font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True,
        letter_spacing_px=3, uppercase=True,
    )
    add_text(
        slide, "primary-ask-text",
        "Sponsor a <em>four-week pilot</em> on one priority workstream — and measure it against the baseline.",
        x_px=ask_x + 64, y_px=ask_y + 66, w_px=ask_w - 128, h_px=110,
        font_size_px=28, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
    )

    # --- Sub-asks: 3-column grid with thin divider borders ---
    sa_x = 64
    sa_y = ask_y + ask_h + 28
    sa_w = 1280 - 128
    sa_h = 100
    col_w = (sa_w - 2) // 3  # 1px gaps between cols

    # Outer border background
    add_rect(slide, "sub-asks-frame", sa_x, sa_y, sa_w, sa_h, CARD_BORDER)

    items = [
        ("Tooling", "Access for 4 people", "Two leads, two analysts. ~2 hours of onboarding, recorded."),
        ("Time", "90 minutes per deck", "One coached storyline session before drafting."),
        ("Visibility", "Weekly 15-min review", "Standing slot with the program MD to refine before scaling."),
    ]
    for i, (label, heading, body) in enumerate(items):
        n = i + 1
        cx = sa_x + i * (col_w + 1)
        # Card body (white over the frame)
        add_rect(slide, f"sub-ask-{n}-bg", cx + (0 if i == 0 else 0), sa_y, col_w, sa_h, WHITE)
        # Label (eyebrow)
        add_text(
            slide, f"sub-ask-{n}-label", label,
            x_px=cx + 18, y_px=sa_y + 14, w_px=col_w - 36, h_px=12,
            font_size_px=9, color=TEXT_FAINT, bold=True,
            letter_spacing_px=1.5, uppercase=True,
        )
        # Heading
        add_text(
            slide, f"sub-ask-{n}-heading", heading,
            x_px=cx + 18, y_px=sa_y + 30, w_px=col_w - 36, h_px=18,
            font_size_px=13, color=BRAND_PRIMARY, bold=True,
        )
        # Body
        add_text(
            slide, f"sub-ask-{n}-body", body,
            x_px=cx + 18, y_px=sa_y + 52, w_px=col_w - 36, h_px=46,
            font_size_px=11, color=TEXT_MID,
        )

    # --- Footer (canonical invariant zone — sources / footnotes / page only;
    # no Mario signature, no "Slide Lab" tag) ---
    add_footer(slide, page_num=8)

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "8_closing-cta-signature.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
