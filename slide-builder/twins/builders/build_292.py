"""
Builder for pattern 292: Pull Quote Interstitial.

Source HTML: _pattern-library/292_pull-quote-interstitial.html

Centered large quote, brand-accent quote-mark, rule, attribution.
No standard title block — it's an interstitial/divider slide.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Decorative quotation mark (large, brand-accent, Georgia serif)
    add_text(
        slide, "quote-mark", "“",
        x_px=560, y_px=120, w_px=160, h_px=160,
        font_size_px=140, color=BRAND_ACCENT, bold=True,
        font_name="Georgia", align="center", anchor="middle",
    )

    # Quote text — centered, italic, brand-primary
    quote = (
        "The organizations that will lead the next decade are not the ones "
        "with the most data — they are the ones that act on it faster "
        "than anyone else."
    )
    add_text(
        slide, "quote-text", quote,
        x_px=230, y_px=290, w_px=820, h_px=160,
        font_size_px=28, color=BRAND_PRIMARY, italic=True,
        align="center", anchor="top",
    )

    # Accent rule
    add_rect(slide, "quote-rule", x_px=600, y_px=480, w_px=80, h_px=4,
             fill_color=BRAND_ACCENT)

    # Attribution
    add_text(
        slide, "quote-attribution",
        "— Jane Smith, Chief Strategy Officer, Accenture",
        x_px=240, y_px=510, w_px=800, h_px=24,
        font_size_px=14, color=TEXT_MID, align="center",
    )

    add_footer(slide, page_num=292)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "292_pull-quote-interstitial.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
