"""
Builder for pattern 64d: Investment thesis cards (dark variant).

Source HTML: _pattern-library/64_investment-thesis-cards-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Why now, why this — three theses for the Q3 rollout.",
        x_px=64, y_px=20, w_px=1180, h_px=80,
        font_size_px=26, color=WHITE, bold=True, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Each thesis stands on its own and is anchored by a measured proof point.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=13, color=TEXT_ON_DARK_MID,
    )
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    g_top = 220
    g_left = 48
    g_right = 1280 - 48
    g_bottom = 720 - 48 - 32
    g_w = g_right - g_left
    g_h = g_bottom - g_top - 32
    gap = 14
    card_h = (g_h - 2 * gap) // 3

    thesis_data = [
        ("01", "Consulting decks are getting slower and worse — Slide Lab reverses both.",
         "Senior consultants spend more than 60% of their build time on deck structure, not insight. "
         "Slide Lab automates the structure layer, freeing partner hours for the thinking that actually moves the engagement.",
         "−64", "%", "Cycle time\nvs. baseline", None),
        ("02", "The IP compounds — every deck built adds to the pattern library.",
         "Each new pattern is reusable across practices and clients. The library is the moat: the marginal cost of the next deck "
         "falls as the catalog grows, and every batch widens the lead.",
         "44", None, "Patterns shipped\nacross 5 batches", None),
        ("03", "Internal IP, no vendor lock-in — we own the upside.",
         "Built on the Claude SDK as a thin substrate; the patterns, pipeline, and prompts are entirely ours. "
         "No recurring vendor license, no rev-share, no exit risk if the model layer shifts.",
         "0", None, "Vendor recurring\nat any scale", "$"),
    ]

    for i, (num, stmt, rat, stat, unit, stat_label, prefix) in enumerate(thesis_data):
        n = i + 1
        cy = g_top + i * (card_h + gap)
        card = add_rect(slide, f"thesis-{n}-card-bg", g_left, cy, g_w, card_h, CARD_BG_DARK)
        card.line.color.rgb = CARD_BORDER_DARK
        card.line.width = 9525
        add_rect(slide, f"thesis-{n}-accent", g_left, cy, 4, card_h, BRAND_ACCENT_SOFT)

        add_text(
            slide, f"thesis-{n}-num", num,
            x_px=g_left + 14, y_px=cy + 22, w_px=70, h_px=56,
            font_size_px=44, color=BRAND_ACCENT_SOFT, bold=True, align="center",
        )
        body_x = g_left + 100
        stat_w = 220
        body_w = g_w - 100 - stat_w - 24
        add_text(
            slide, f"thesis-{n}-statement", stmt,
            x_px=body_x, y_px=cy + 22, w_px=body_w, h_px=28,
            font_size_px=18, color=WHITE, bold=True,
        )
        add_text(
            slide, f"thesis-{n}-rationale", rat,
            x_px=body_x, y_px=cy + 56, w_px=body_w, h_px=card_h - 70,
            font_size_px=12, color=TEXT_ON_DARK_MID,
        )

        stat_x = g_left + g_w - stat_w
        add_rect(slide, f"thesis-{n}-divider", stat_x, cy + 18, 1, card_h - 36, CARD_BORDER_DARK)
        cur_x = stat_x + 24
        if prefix:
            add_text(
                slide, f"thesis-{n}-prefix", prefix,
                x_px=cur_x, y_px=cy + 30, w_px=24, h_px=28,
                font_size_px=22, color=BRAND_ACCENT_SOFT, bold=True,
            )
            cur_x += 24
        add_text(
            slide, f"thesis-{n}-stat", stat,
            x_px=cur_x, y_px=cy + 22, w_px=120, h_px=44,
            font_size_px=34, color=WHITE, bold=True,
        )
        if unit:
            add_text(
                slide, f"thesis-{n}-unit", unit,
                x_px=cur_x + 24 * len(stat), y_px=cy + 32, w_px=40, h_px=32,
                font_size_px=22, color=BRAND_ACCENT_SOFT, bold=True,
            )
        add_text(
            slide, f"thesis-{n}-stat-label", stat_label,
            x_px=stat_x + 24, y_px=cy + 70, w_px=stat_w - 36, h_px=36,
            font_size_px=10, color=TEXT_ON_DARK_MID, bold=True, uppercase=True,
        )

    add_text(
        slide, "convergence", "Three theses, three proof points.",
        x_px=48, y_px=720 - 48 - 22, w_px=1280 - 96, h_px=22,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True,
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "64",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "64d_investment-thesis-cards.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
