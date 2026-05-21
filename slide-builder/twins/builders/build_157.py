"""
Builder for pattern 157: Formal memo / decision document format.

Source HTML: _pattern-library/157_letter-memo-format.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title (18px, smaller variant)
    add_text(slide, "title",
             "<strong>Decision required by May 25</strong> — memo formally documents the steering committee's authority to approve Phase 3",
             x_px=48, y_px=58, w_px=1100, h_px=48,
             font_size_px=18, color=TEXT_DARK, bold=True,
             emphasis_color=BRAND_PRIMARY)
    add_text(slide, "subtitle",
             "Formal memorandum · Client Steering Committee · May 18, 2026",
             x_px=48, y_px=104, w_px=900, h_px=18,
             font_size_px=12, color=TEXT_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 128, 48, 2, BRAND_ACCENT)

    # Memo card: top:220 left:40 right:40 bottom:630 (safe content zone)
    mc_x = 40
    mc_y = 220
    mc_w = 1280 - 80   # 1200
    mc_h = 630 - mc_y  # 410
    memo = add_rect(slide, "memo-card", mc_x, mc_y, mc_w, mc_h, WHITE)
    memo.line.color.rgb = CARD_BORDER
    memo.line.width = 9525

    # MEMORANDUM header (centered, brand-accent underline)
    add_text(slide, "memo-header-title", "MEMORANDUM",
             x_px=mc_x + 40, y_px=mc_y + 10, w_px=mc_w - 80, h_px=26,
             font_size_px=18, color=BRAND_PRIMARY, bold=True, align="center", uppercase=True)
    add_rect(slide, "memo-header-rule", mc_x + 40, mc_y + 40, mc_w - 80, 2, BRAND_ACCENT)

    # Metadata table (4 rows × 18px = 72px + 10 top = 82px → ends at mc_y+52+72=mc_y+124)
    meta_y = mc_y + 50
    meta_labels = [("From", "Managing Director, Accenture"),
                   ("To", "Client Steering Committee"),
                   ("Date", "May 18, 2026"),
                   ("Re", "Phase 2 Decision Package")]
    for i, (lbl, val) in enumerate(meta_labels):
        my = meta_y + i * 18
        add_text(slide, f"meta-label-{i+1}", lbl + ":",
                 x_px=mc_x + 40, y_px=my, w_px=64, h_px=16,
                 font_size_px=9, color=BRAND_PRIMARY_MID, bold=True, uppercase=True)
        value_color = BRAND_PRIMARY if i == 3 else TEXT_DARK
        value_bold = i == 3
        add_text(slide, f"meta-value-{i+1}", val,
                 x_px=mc_x + 116, y_px=my, w_px=mc_w - 156, h_px=16,
                 font_size_px=10, color=value_color, bold=value_bold)

    # Divider rule below meta (ends at meta_y + 4*18 = meta_y+72)
    add_rect(slide, "meta-rule", mc_x + 40, meta_y + 76, mc_w - 80, 1, CARD_BORDER)

    # Body paragraphs — 3 paragraphs, each 64px tall, font 10px
    # body_y = meta_y + 86; total body = 3*64 = 192px; body ends at meta_y+86+192 = mc_y+50+86+192 = mc_y+328
    body_y = meta_y + 86
    para_h = 64
    paragraphs = [
        ("Phase 2 of the transformation program has been completed on schedule and within the approved "
         "budget envelope. All six workstreams have met their exit criteria, and the independent quality "
         "review confirmed zero critical findings. Delivery confidence for Phase 3 is assessed as high "
         "based on current resourcing and dependency status."),
        ("The Steering Committee is asked to make a formal decision on Phase 3 initiation. Three options "
         "are presented: (A) full scope go-ahead at the approved $4.2M envelope; (B) a reduced-scope entry "
         "covering Workstreams 1-3 only; or (C) a structured pause pending additional stakeholder alignment. "
         "Options A and B can proceed with a decision by May 25 without impacting the critical path."),
        ("Accenture recommends Option A — full scope initiation. Delay beyond May 25 introduces a six-week "
         "critical-path slip and estimated £380K in re-mobilisation costs. The team stands ready to brief "
         "individual committee members ahead of the formal session. A signed decision memo is required by "
         "close of business May 25, 2026."),
    ]
    for i, p in enumerate(paragraphs):
        add_text(slide, f"body-p{i+1}", p,
                 x_px=mc_x + 40, y_px=body_y + i * para_h, w_px=mc_w - 80, h_px=para_h - 4,
                 font_size_px=10, color=TEXT_DARK)

    # Signature block — starts at body_y + 3*para_h + 8 = meta_y+86+192+8 = mc_y+336
    # mc_y+336 = 556; sig block needs ~60px → ends at 616 < 630 ✓
    sig_y = body_y + 3 * para_h + 8
    add_rect(slide, "sig-divider", mc_x + 40, sig_y, mc_w - 80, 1, TEXT_MID)
    add_rect(slide, "sig-line", mc_x + 40, sig_y + 18, 160, 1, TEXT_DARK)
    add_text(slide, "sig-name", "Maria Santos",
             x_px=mc_x + 40, y_px=sig_y + 22, w_px=300, h_px=14,
             font_size_px=10, color=BRAND_PRIMARY, bold=True)
    add_text(slide, "sig-title", "Engagement Lead, Accenture",
             x_px=mc_x + 40, y_px=sig_y + 38, w_px=300, h_px=12,
             font_size_px=9, color=TEXT_MID)
    add_text(slide, "sig-contact", "maria.santos@accenture.com · +44 20 7844 1000",
             x_px=mc_x + 40, y_px=sig_y + 52, w_px=400, h_px=12,
             font_size_px=8, color=TEXT_FAINT)
    add_text(slide, "priv-footer", "PRIVILEGED & CONFIDENTIAL",
             x_px=mc_x + mc_w - 240, y_px=sig_y + 52, w_px=200, h_px=12,
             font_size_px=9, color=TEXT_FAINT, bold=True, align="right", uppercase=True)

    add_footer(slide, page_num=157)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "157_letter-memo-format.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
