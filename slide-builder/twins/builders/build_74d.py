"""
Builder for pattern 74d: Hero stat + photo combo — dark variant.

Source HTML: _pattern-library/74_stat-photo-combo-dark.html
Light template: twins/builders/build_74.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor

# Dark-mode tokens
TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def _dark_chrome(slide, title, subtitle, *, brand_rule_w=64):
    """Inline canonical dark-mode chrome: title (white, bottom-anchored),
    subtitle (dark-mid italic), brand-rule (accent-soft).
    """
    add_text(
        slide, "title", title,
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle", subtitle,
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 64, 132, brand_rule_w, 3, BRAND_ACCENT_SOFT)


def _dark_footer(slide, page_num):
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(
        slide, "source", "Source: [add source here or delete]",
        x_px=58, y_px=688, w_px=1100, h_px=16,
        font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True,
    )
    add_text(
        slide, "page-number", f"{page_num}",
        x_px=1170, y_px=688, w_px=52, h_px=16,
        font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right",
    )


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    _dark_chrome(
        slide,
        title="What four weeks looked like — measured, not estimated.",
        subtitle="Data and the room it happened in — on the same page.",
        brand_rule_w=56,
    )

    # Body grid: photo zone left, stat zone right. Shifted to y=220.
    body_top = 220
    body_h = 432
    col_w = (1280 - 128 - 40) // 2  # 556
    photo_x = 64
    stat_x = 64 + col_w + 40

    # Photo zone — mid brand fill on dark bg
    add_rect(slide, "photo-zone", photo_x, body_top, col_w, body_h, BRAND_PRIMARY_MID)

    # Corner tag overlay
    add_text(
        slide, "photo-corner-tag", "PHOTO PLACEHOLDER",
        x_px=photo_x + 16, y_px=body_top + 16, w_px=180, h_px=22,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
        bg_fill=BRAND_PRIMARY, padding_px=(4, 8, 4, 8),
    )
    add_text(
        slide, "photo-meta", "Pilot week 4 · review session",
        x_px=photo_x + 24, y_px=body_top + body_h - 64, w_px=col_w - 48, h_px=18,
        font_size_px=11, color=WHITE, bold=True,
    )
    add_text(
        slide, "photo-meta-filename", "replace · pilot-w4_review-room.jpg",
        x_px=photo_x + 24, y_px=body_top + body_h - 40, w_px=col_w - 48, h_px=16,
        font_size_px=10, color=BRAND_ACCENT_SOFT,
        font_name="Consolas",
    )

    # Stat zone
    pre_y = body_top + 20
    add_text(
        slide, "hero-stat-label",
        "Measured across 12 pilot decks · Weeks 1–4",
        x_px=stat_x, y_px=pre_y, w_px=col_w, h_px=18,
        font_size_px=11, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True,
    )

    stat_y = pre_y + 50
    stat_text = "5"
    stat_font_px = 200
    add_text(
        slide, "hero-stat-value", stat_text,
        x_px=stat_x, y_px=stat_y, w_px=200, h_px=200,
        font_size_px=stat_font_px, color=BRAND_ACCENT_SOFT, bold=True,
    )
    unit_offset = int(len(stat_text) * stat_font_px * 0.62) + 12
    add_text(
        slide, "hero-stat-unit", "days",
        x_px=stat_x + unit_offset, y_px=stat_y + 90, w_px=200, h_px=80,
        font_size_px=58, color=TEXT_ON_DARK_MID, bold=True,
    )

    add_text(
        slide, "hero-stat-caption",
        "Median time from kickoff to partner-ready, weeks 1–4 of pilot.",
        x_px=stat_x, y_px=stat_y + 200, w_px=col_w - 20, h_px=58,
        font_size_px=17, color=WHITE, bold=False,
    )

    add_rect(slide, "stat-source-rule",
             stat_x, body_top + body_h - 40, col_w - 20, 1, CARD_BORDER_DARK)
    add_text(
        slide, "chart-source",
        "Compared to 14-day baseline · Apr–May 2026",
        x_px=stat_x, y_px=body_top + body_h - 32, w_px=col_w - 20, h_px=16,
        font_size_px=11, color=TEXT_ON_DARK_FAINT, italic=True,
    )

    _dark_footer(slide, page_num=74)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "74d_stat-photo-combo-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
