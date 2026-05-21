"""
Builder for pattern 157d: Formal memo / decision document — dark.

Source HTML: _pattern-library/157_letter-memo-format-dark.html
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

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Canonical chrome
    add_text(slide, "title",
             "<strong>Decision required by May 25</strong> — memo formally documents the steering committee's authority to approve Phase 3",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Formal memorandum · Client Steering Committee · May 18, 2026",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Memo card
    mc_x = 40
    mc_y = 220
    mc_w = 1280 - 80
    mc_h = 660 - mc_y
    memo = add_rect(slide, "memo-card", mc_x, mc_y, mc_w, mc_h, CARD_BG_DARK)
    memo.line.color.rgb = CARD_BORDER_DARK
    memo.line.width = 9525

    # MEMORANDUM header
    add_text(slide, "memo-header-title", "MEMORANDUM",
             x_px=mc_x + 40, y_px=mc_y + 10, w_px=mc_w - 80, h_px=26,
             font_size_px=18, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True)
    add_rect(slide, "memo-header-rule", mc_x + 40, mc_y + 40, mc_w - 80, 2, BRAND_ACCENT)

    # Metadata table
    meta_y = mc_y + 50
    meta_labels = [("From", "Managing Director, Accenture"),
                   ("To", "Client Steering Committee"),
                   ("Date", "May 18, 2026"),
                   ("Re", "Phase 2 Decision Package")]
    for i, (lbl, val) in enumerate(meta_labels):
        my = meta_y + i * 18
        add_text(slide, f"meta-label-{i+1}", lbl + ":",
                 x_px=mc_x + 40, y_px=my, w_px=64, h_px=16,
                 font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
        value_color = BRAND_ACCENT_SOFT if i == 3 else WHITE
        value_bold = i == 3
        add_text(slide, f"meta-value-{i+1}", val,
                 x_px=mc_x + 116, y_px=my, w_px=mc_w - 156, h_px=16,
                 font_size_px=10, color=value_color, bold=value_bold)

    add_rect(slide, "meta-rule", mc_x + 40, meta_y + 76, mc_w - 80, 1, CARD_BORDER_DARK)

    body_y = meta_y + 86
    para_h = 60
    paragraphs = [
        ("Phase 2 of the transformation program has been completed on schedule and within the approved "
         "budget envelope. All six workstreams have met their exit criteria, and the independent quality "
         "review confirmed zero critical findings."),
        ("The Steering Committee is asked to make a formal decision on Phase 3 initiation. Three options "
         "are presented: (A) full scope go-ahead at the approved $4.2M envelope; (B) a reduced-scope entry "
         "covering Workstreams 1-3 only; or (C) a structured pause pending stakeholder alignment."),
        ("Accenture recommends Option A — full scope initiation. Delay beyond May 25 introduces a six-week "
         "critical-path slip and estimated £380K in re-mobilisation costs. A signed decision memo is required by "
         "close of business May 25, 2026."),
    ]
    for i, p in enumerate(paragraphs):
        add_text(slide, f"body-p{i+1}", p,
                 x_px=mc_x + 40, y_px=body_y + i * para_h, w_px=mc_w - 80, h_px=para_h - 4,
                 font_size_px=10, color=WHITE)

    # Signature block
    sig_y = body_y + 3 * para_h + 4
    add_rect(slide, "sig-divider", mc_x + 40, sig_y, mc_w - 80, 1, TEXT_ON_DARK_MID)
    add_rect(slide, "sig-line", mc_x + 40, sig_y + 18, 160, 1, WHITE)
    add_text(slide, "sig-name", "Maria Santos",
             x_px=mc_x + 40, y_px=sig_y + 22, w_px=300, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True)
    add_text(slide, "sig-title", "Engagement Lead, Accenture",
             x_px=mc_x + 40, y_px=sig_y + 38, w_px=300, h_px=12,
             font_size_px=9, color=TEXT_ON_DARK_MID)
    add_text(slide, "sig-contact", "maria.santos@accenture.com · +44 20 7844 1000",
             x_px=mc_x + 40, y_px=sig_y + 52, w_px=400, h_px=12,
             font_size_px=8, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "priv-footer", "PRIVILEGED & CONFIDENTIAL",
             x_px=mc_x + mc_w - 240, y_px=sig_y + 52, w_px=200, h_px=12,
             font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=True, align="right", uppercase=True)

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "157",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "157d_letter-memo-format.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
