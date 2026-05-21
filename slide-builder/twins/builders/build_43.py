"""
Builder for pattern 43: Definitions / glossary — 6 terms.

Two-column grid: term label (left, narrow) + definition (right, wide).
Top has table headers; bottom has convergence band.

Source HTML: _pattern-library/43_definitions-glossary.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID,
    CARD_BORDER, TEXT_DARK, TEXT_FAINT,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Vocabulary — six terms before we go further.",
        subtitle="Same words, same meaning — the shared dictionary for everything that follows.",
        title_h=68,
        subtitle_h=22,
    )

    # Glossary table region: top=200, left=64, right=64
    g_left = 64
    g_right = 1280 - 64
    g_w = g_right - g_left
    g_top = 200

    term_col_w = 240
    def_col_x = g_left + term_col_w + 32

    # Table header
    add_text(
        slide, "table-head-1", "TERM",
        x_px=g_left, y_px=g_top, w_px=term_col_w, h_px=14,
        font_size_px=11, color=BRAND_PRIMARY_MID, bold=True,
        letter_spacing_px=2, uppercase=True,
    )
    add_text(
        slide, "table-head-2", "DEFINITION",
        x_px=def_col_x, y_px=g_top, w_px=g_w - term_col_w - 32, h_px=14,
        font_size_px=11, color=BRAND_PRIMARY_MID, bold=True,
        letter_spacing_px=2, uppercase=True,
    )
    add_rect(slide, "table-head-rule", g_left, g_top + 18, g_w, 2, BRAND_PRIMARY)

    # 6 term rows
    terms = [
        ("Governing thought",
         "The single sentence the whole deck has to prove. If the deck were one sentence, it's this one.",
         None),
        ("Action title",
         "The headline of each slide, written as a declarative sentence with a verb and a so-what. Not \"Background\" — \"Background shows we lost 60% of cycle time in this phase.\"",
         None),
        ("So-what",
         "The decision or action a slide demands of the reader. Every slide has one; most slides don't say it.",
         None),
        ("Invariant zone",
         "The fixed parts of every slide that shouldn't change deck-to-deck: page number, source line, footer, brand chrome.",
         "PROVENANCE  Borrowed from architecture — \"the parts that hold even when everything else moves.\""),
        ("MECE",
         "Mutually Exclusive, Collectively Exhaustive. The discipline of cutting a problem into non-overlapping pieces that cover the whole space.",
         None),
        ("Convergence line",
         "The italic statement at the bottom of an argument slide that closes it — the final claim the evidence supports.",
         None),
    ]
    row_top_start = g_top + 32
    row_h = 60

    for i, (label, definition, prov) in enumerate(terms):
        n = i + 1
        ry = row_top_start + i * row_h

        add_text(
            slide, f"term-{n}-label", label,
            x_px=g_left, y_px=ry + 8, w_px=term_col_w, h_px=24,
            font_size_px=14, color=BRAND_PRIMARY, bold=True,
            letter_spacing_px=2, uppercase=True,
        )
        add_text(
            slide, f"term-{n}-def", definition,
            x_px=def_col_x, y_px=ry + 8, w_px=g_w - term_col_w - 32, h_px=42,
            font_size_px=13, color=TEXT_DARK,
        )
        if prov:
            add_text(
                slide, f"term-{n}-prov", prov,
                x_px=def_col_x, y_px=ry + 36, w_px=g_w - term_col_w - 32, h_px=14,
                font_size_px=10, color=TEXT_FAINT, italic=True,
            )
        # Bottom rule (except last)
        if i < 5:
            add_rect(slide, f"term-{n}-rule", g_left, ry + row_h - 2, g_w, 1, CARD_BORDER)

    add_convergence(
        slide,
        "Same words, same meaning — that's where the conversation starts.",
    )

    add_footer(slide, page_num=43)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "43_definitions-glossary.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
