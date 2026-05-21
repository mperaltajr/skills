"""
Builder for pattern 19: Cover slide — split-panel (dark left / light right).

Source HTML: _pattern-library/19_cover-split-panel.html

Cover-only chrome — no standard title block, no footer rule, no convergence.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, TEXT_DARK, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor


def build():
    prs, slide = new_slide()

    # Left panel — brand-primary fill, full height, half width
    add_rect(slide, "cover-left-panel", x_px=0, y_px=0, w_px=640, h_px=720, fill_color=BRAND_PRIMARY)

    # Right edge accent strip — 4px brand-accent at x=636 (inner edge)
    add_rect(slide, "cover-left-accent", x_px=636, y_px=64, w_px=4, h_px=600, fill_color=BRAND_ACCENT)

    # Pre-label
    add_text(
        slide, "cover-pre-label", "INTERNAL DECK · 2026",
        x_px=64, y_px=64, w_px=400, h_px=16,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )

    # Deck title (60px white bold)
    add_text(
        slide, "cover-deck-title", "Slide Lab",
        x_px=64, y_px=260, w_px=540, h_px=76,
        font_size_px=60, color=WHITE, bold=True,
    )

    # Tagline (19px italic, brand-accent-soft)
    add_text(
        slide, "cover-tagline", "Think. Argue. Build.",
        x_px=64, y_px=348, w_px=540, h_px=28,
        font_size_px=19, color=BRAND_ACCENT_SOFT, italic=True,
    )

    # Presented-by — bottom-left, top border, 360px wide
    pby_y = 580
    presented_border = RGBColor(0x4A, 0x2B, 0x6E)
    add_rect(slide, "cover-presented-rule", x_px=64, y_px=pby_y, w_px=360, h_px=1, fill_color=presented_border)
    add_text(
        slide, "cover-presented-label", "PRESENTED BY",
        x_px=64, y_px=pby_y + 14, w_px=360, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "cover-presented-name", "Mario Peralta · Strategy Manager",
        x_px=64, y_px=pby_y + 32, w_px=360, h_px=22,
        font_size_px=15, color=WHITE, bold=True,
    )

    # RIGHT panel — meta block + bottom-right DRAFT
    # (Brand-mark square in top-right removed per feedback — too distracting on a cover.)

    # Meta block (vertical centered, ~y=300)
    meta_left = 704
    meta_top = 270

    # Vertical accent rule (4px wide)
    add_rect(slide, "cover-meta-rule", x_px=meta_left, y_px=meta_top, w_px=4, h_px=180, fill_color=BRAND_ACCENT)

    meta_x = meta_left + 32
    meta_rows = [
        ("PREPARED FOR", "Internal · Accenture Strategy", True),
        ("DATE", "May 2026", False),
        ("DURATION", "30 minutes", False),
    ]
    row_y = meta_top
    for i, (label, value, is_lead) in enumerate(meta_rows):
        n = i + 1
        add_text(
            slide, f"cover-meta-{n}-label", label,
            x_px=meta_x, y_px=row_y, w_px=400, h_px=14,
            font_size_px=10, color=TEXT_FAINT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"cover-meta-{n}-value", value,
            x_px=meta_x, y_px=row_y + 16, w_px=440, h_px=28 if is_lead else 22,
            font_size_px=22 if is_lead else 17,
            color=BRAND_PRIMARY if is_lead else TEXT_DARK,
            bold=is_lead,
        )
        row_y += 64


    # No standard chrome (cover variant)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "19_cover-split-panel.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
