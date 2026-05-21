"""
Builder for pattern 74: Hero stat + photo combo.

Source HTML: _pattern-library/74_stat-photo-combo.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title block — 28px title, 14px subhead, rule below
    add_title_block(
        slide,
        title="What four weeks looked like — measured, not estimated.",
        subtitle="Data and the room it happened in — on the same page.",
        title_h=70,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # Body grid: photo zone left, stat zone right. 50/50, gap 40.
    # Container left:64, right:64, top:198, height:460
    body_top = 198
    body_h = 460
    col_w = (1280 - 128 - 40) // 2  # 556
    photo_x = 64
    stat_x = 64 + col_w + 40  # 660

    # Photo zone (placeholder, brand-primary gradient feel — flat fill here)
    add_rect(slide, "photo-zone", photo_x, body_top, col_w, body_h, BRAND_PRIMARY)

    # Corner tag overlay
    add_text(
        slide, "photo-corner-tag", "PHOTO PLACEHOLDER",
        x_px=photo_x + 16, y_px=body_top + 16, w_px=180, h_px=22,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
        bg_fill=BRAND_PRIMARY_MID, padding_px=(4, 8, 4, 8),
    )

    # Photo meta (bottom-left of photo zone)
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

    # Stat zone — pre-label, big stat, caption, source
    pre_y = body_top + 20
    add_text(
        slide, "hero-stat-label",
        "Measured across 12 pilot decks · Weeks 1–4",
        x_px=stat_x, y_px=pre_y, w_px=col_w, h_px=18,
        font_size_px=11, color=BRAND_PRIMARY_MID, bold=True, uppercase=True,
    )

    # Big stat value
    stat_y = pre_y + 50
    stat_text = "5"
    stat_font_px = 200
    add_text(
        slide, "hero-stat-value", stat_text,
        x_px=stat_x, y_px=stat_y, w_px=200, h_px=200,
        font_size_px=stat_font_px, color=BRAND_PRIMARY, bold=True,
    )
    # Unit beside the stat — offset by estimated value width
    unit_offset = int(len(stat_text) * stat_font_px * 0.62) + 12
    add_text(
        slide, "hero-stat-unit", "days",
        x_px=stat_x + unit_offset, y_px=stat_y + 90, w_px=200, h_px=80,
        font_size_px=58, color=BRAND_PRIMARY_MID, bold=True,
    )

    # Caption
    add_text(
        slide, "hero-stat-caption",
        "Median time from kickoff to partner-ready, weeks 1–4 of pilot.",
        x_px=stat_x, y_px=stat_y + 200, w_px=col_w - 20, h_px=58,
        font_size_px=17, color=TEXT_DARK, bold=False,
    )

    # Source (above bottom rule of stat zone)
    add_rect(slide, "stat-source-rule",
             stat_x, body_top + body_h - 40, col_w - 20, 1, CARD_BORDER)
    add_text(
        slide, "chart-source",
        "Compared to 14-day baseline · Apr–May 2026",
        x_px=stat_x, y_px=body_top + body_h - 32, w_px=col_w - 20, h_px=16,
        font_size_px=11, color=TEXT_FAINT, italic=True,
    )

    # Convergence — subtle horizontal accent line (not a band) per HTML
    add_rect(slide, "convergence", 64 + 200, 720 - 56 - 1,
             1280 - 128 - 400, 2, BRAND_ACCENT)

    add_footer(slide, page_num=74)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "74_stat-photo-combo.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
