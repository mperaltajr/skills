"""
Builder for pattern 232: Proposal section break (split-panel divider).

Variant divider: left dark half with numeral + title, right light half with TOC.

Source HTML: _pattern-library/232_proposal-section-break.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT, CARD_BORDER, WHITE, DRAFT_BG, DRAFT_TEXT,
)
from pptx.dml.color import RGBColor


def build():
    prs, slide = new_slide()

    # Variant chrome

    # Left dark half — 560px wide
    add_rect(slide, "cover-left-panel", 0, 0, 560, 720, BRAND_PRIMARY)
    # Wordmark top-left of dark area
    add_text(slide, "wordmark", "ACCENTURE",
             x_px=28, y_px=38, w_px=200, h_px=18,
             font_size_px=12, color=WHITE, bold=True, uppercase=True)
    # Right-aligned section number (96px tall)
    add_text(slide, "divider-numeral", "03",
             x_px=28, y_px=200, w_px=560 - 56, h_px=130,
             font_size_px=96, color=BRAND_ACCENT_SOFT, bold=True, align="right")
    # Rule under numeral
    add_rect(slide, "divider-rule", 28, 350, 560 - 56, 1, RGBColor(0x66, 0x4C, 0x8F))
    # Section title — left-aligned (as in source)
    add_text(slide, "divider-title", "Our Proposed\nSolution",
             x_px=28, y_px=374, w_px=560 - 56, h_px=90,
             font_size_px=32, color=WHITE, bold=True)

    # Diagonal accent stripe at boundary — simplified as vertical 6px brand-accent line
    add_rect(slide, "diagonal-stripe", 558, 0, 6, 664, BRAND_ACCENT)

    # Right light half (560 → 1280)
    right_x = 560
    # "In this section:" label
    add_text(slide, "toc-label", "In this section:",
             x_px=right_x + 56, y_px=128, w_px=600, h_px=18,
             font_size_px=14, color=BRAND_PRIMARY, bold=True, uppercase=True)
    # TOC items
    toc = [
        ("01", "Solution Architecture Overview",
         "End-to-end platform design and integration model"),
        ("02", "Implementation Approach & Phases",
         "Phased delivery plan with milestones and decision gates"),
        ("03", "Team Structure & Governance",
         "Roles, responsibilities, and escalation pathways"),
        ("04", "Risk Management Framework",
         "Identified risks, mitigations, and contingency planning"),
    ]
    item_top = 178
    item_h = 60
    for i, (num, title, desc) in enumerate(toc):
        n = i + 1
        iy = item_top + i * item_h
        add_text(slide, f"toc-{n}-num", num,
                 x_px=right_x + 56, y_px=iy + 1, w_px=24, h_px=18,
                 font_size_px=11, color=BRAND_ACCENT, bold=True)
        add_text(slide, f"toc-{n}-title", title,
                 x_px=right_x + 90, y_px=iy, w_px=520, h_px=20,
                 font_size_px=12, color=TEXT_DARK, bold=True)
        add_text(slide, f"toc-{n}-desc", desc,
                 x_px=right_x + 90, y_px=iy + 22, w_px=520, h_px=20,
                 font_size_px=11, color=TEXT_MID)

    # Value tagline (italic, under TOC)
    add_rect(slide, "value-rule", right_x + 56, 458, 420, 1, CARD_BORDER)
    add_text(slide, "value-tagline",
             "Delivering measurable outcomes through proven methodology, deep industry expertise, and a commitment to your long-term success.",
             x_px=right_x + 56, y_px=474, w_px=620, h_px=80,
             font_size_px=11, color=RGBColor(0x5C, 0x2D, 0x87), italic=True)

    # Footer
    add_text(slide, "page-number", "232",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "232_proposal-section-break.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
