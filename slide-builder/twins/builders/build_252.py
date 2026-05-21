"""
Builder for pattern 252: SCQA Executive One-Pager.

Source HTML: _pattern-library/252_scqa-one-pager.html

Layout: title block + 4 horizontal SCQA bands (S/C/Q/A) each with a coloured
left label cell and a text cell, followed by a recommendation strip.
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
from pptx.dml.color import RGBColor

GREEN_ANS = RGBColor(0x1A, 0x6B, 0x3C)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Margin Recovery: <strong>Strategic Options Assessment</strong>",
        subtitle="Executive overview — structured problem framing and recommended path forward",
    )

    # Body zone: 4 SCQA bands stacked. Available area roughly y=225..600
    bands_top = 230
    bands_bottom = 590
    bands_h = bands_bottom - bands_top
    gap = 6
    band_h = (bands_h - 3 * gap) // 4
    left_x = 48
    right_x = 1280 - 48
    label_w = 88
    band_w = right_x - left_x

    bands = [
        ("S", "Situation", BRAND_PRIMARY,
         "The business has grown 40% YoY but operating costs have scaled disproportionately, compressing margins from 28% to 19%."),
        ("C", "Complication", BRAND_PRIMARY_MID,
         "Three structural inefficiencies in procurement, logistics, and workforce allocation are driving $14M in avoidable spend annually."),
        ("Q", "Question", BRAND_ACCENT,
         "How can the organization recover margin to 25%+ within 18 months without sacrificing growth momentum?"),
        ("A", "Answer", GREEN_ANS,
         "A targeted efficiency program across three workstreams can recover $11M and restore margins to 26% by Q4 2026."),
    ]

    for i, (letter, word, color, text) in enumerate(bands):
        n = i + 1
        by = bands_top + i * (band_h + gap)
        # Body card
        card = add_rect(slide, f"scqa-band-{n}", left_x, by, band_w, band_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Label cell
        add_rect(slide, f"scqa-band-{n}-label", left_x, by, label_w, band_h, color)
        add_text(
            slide, f"scqa-band-{n}-letter", letter,
            x_px=left_x, y_px=by + 8, w_px=label_w, h_px=24,
            font_size_px=22, color=WHITE, bold=True, align="center",
        )
        add_text(
            slide, f"scqa-band-{n}-word", word.upper(),
            x_px=left_x, y_px=by + band_h - 22, w_px=label_w, h_px=14,
            font_size_px=8, color=WHITE, bold=True, align="center",
            letter_spacing_px=1.2,
        )
        # Body text
        body_bold = (letter == "A")
        add_text(
            slide, f"scqa-band-{n}-text", text,
            x_px=left_x + label_w + 14, y_px=by, w_px=band_w - label_w - 28,
            h_px=band_h, font_size_px=13, color=TEXT_DARK, bold=body_bold,
            anchor="middle",
        )

    # Recommendation strip
    rec_y = 600
    rec_h = 34
    add_rect(slide, "rec-strip", left_x, rec_y, band_w, rec_h, BRAND_PRIMARY)
    add_text(
        slide, "rec-strip-text",
        "<strong>RECOMMENDED ACTION:</strong> Approve Phase 1 mobilisation — 6-week diagnostic, $320K investment, ROI payback in 4 months.",
        x_px=left_x + 16, y_px=rec_y, w_px=band_w - 32, h_px=rec_h,
        font_size_px=12, color=WHITE, anchor="middle", emphasis_color=WHITE,
        bold=False,
    )

    add_footer(slide, page_num=252)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "252_scqa-one-pager.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
