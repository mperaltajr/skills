"""
Builder for pattern 11d: Long-form structured text — DARK variant.

Light source: twins/builders/build_11.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Light variant uses title_y=44 — keep that offset, with bottom anchor at y=44+68=112
    add_text(
        slide, "title",
        "Three structural failures, one root cause.",
        x_px=64, y_px=44, w_px=1000, h_px=68,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "How consulting decks get worse over the engagement, not better.",
        x_px=64, y_px=120, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=144, w_px=56, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    body_top = 220
    grid_left = 64
    num_w = 56
    stage_w = 200
    gap_w = 28
    body_w = 1280 - 128 - num_w - stage_w - 2 * gap_w

    header_y = body_top
    add_text(
        slide, "table-head-1", "#",
        x_px=grid_left, y_px=header_y, w_px=num_w, h_px=18,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "table-head-2", "STAGE",
        x_px=grid_left + num_w + gap_w, y_px=header_y, w_px=stage_w, h_px=18,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "table-head-3", "WHAT'S HAPPENING",
        x_px=grid_left + num_w + gap_w + stage_w + gap_w, y_px=header_y, w_px=body_w, h_px=18,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_rect(slide, "table-header-rule",
             x_px=grid_left, y_px=header_y + 24, w_px=1280 - 128, h_px=2, fill_color=BRAND_ACCENT_SOFT)

    rows = [
        ("01", "Situation",
         "Most consulting work starts strong — clear brief, fresh thinking, a partner who's bought in. The first week's deck reflects that clarity: a tight thesis, a single governing thought, and just enough evidence to carry it. Everyone leaves the kickoff aligned."),
        ("02", "Complication",
         "By week three, every stakeholder has touched a slide. The deck has tripled in length, lost its through-line, and added a new section called \"Appendix C: Detailed analysis.\" What started as an argument has become an archive."),
        ("03", "Question",
         "Why do decks degrade as the team learns more, instead of getting sharper? Every additional insight should make the thesis cleaner — yet the opposite happens, on every engagement, regardless of seniority or sector."),
        ("04", "Answer",
         "Because adding is faster than choosing. Every workstream contributes findings; nobody is paid to delete them. Reviewers ask \"what about X?\" and X gets added; nobody asks \"what should we cut?\" The deck becomes sediment, not synthesis."),
    ]
    rows_top = header_y + 36
    row_h = 88
    for i, (num, name, body2) in enumerate(rows):
        n = i + 1
        ry = rows_top + i * row_h
        add_text(
            slide, f"section-{n}-num", num,
            x_px=grid_left, y_px=ry + 4, w_px=num_w, h_px=28,
            font_size_px=22, color=BRAND_ACCENT_SOFT, bold=True,
        )
        add_text(
            slide, f"section-{n}-name", name.upper(),
            x_px=grid_left + num_w + gap_w, y_px=ry + 8, w_px=stage_w, h_px=24,
            font_size_px=14, color=WHITE, bold=True, uppercase=True,
        )
        add_text(
            slide, f"section-{n}-body", body2,
            x_px=grid_left + num_w + gap_w + stage_w + gap_w, y_px=ry + 4,
            w_px=body_w, h_px=row_h - 12,
            font_size_px=12, color=WHITE,
        )
        if i < len(rows) - 1:
            add_rect(slide, f"section-{n}-sep",
                     x_px=grid_left, y_px=ry + row_h - 1, w_px=1280 - 128, h_px=1,
                     fill_color=CARD_BORDER_DARK)

    conv_y = 720 - 78 - 42
    add_rect(slide, "convergence-bg",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=42, fill_color=BRAND_ACCENT)
    add_text(
        slide, "convergence",
        "Slide Lab's job isn't to add ideas. It's to make subtraction faster than addition.",
        x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=42,
        font_size_px=14, color=WHITE, italic=True,
        anchor="middle", padding_px=(0, 22, 0, 22),
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "11",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "11d_long-form-structured-text.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
