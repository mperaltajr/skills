"""
Builder for pattern 333: 7-bucket numbered list (7 row cards stacked vertically).

Inspired by 326's row-card pattern but stripped of the right summary panel.

Source HTML: _pattern-library/333_7bucket-numbered-list.html
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


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Seven priorities that <strong>shape the agenda</strong>",
        subtitle="A structured view of the key focus areas driving this initiative forward",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top

    rows = [
        ("1", "Strategic Alignment",
         "Ensure all workstreams map to the overarching enterprise objectives"),
        ("2", "Stakeholder Engagement",
         "Maintain structured communication cadence with key decision-makers"),
        ("3", "Data Governance",
         "Establish ownership, quality standards, and access controls across domains"),
        ("4", "Technology Enablement",
         "Deploy platforms that accelerate delivery and reduce manual overhead"),
        ("5", "Change Management",
         "Drive adoption through training, communication, and embedded champions"),
        ("6", "Risk & Compliance",
         "Proactively identify, track, and mitigate programme-level risk exposure"),
        ("7", "Value Realisation",
         "Track and communicate measurable outcomes tied to programme investment"),
    ]
    row_gap = 6
    row_h = (body_h - (len(rows) - 1) * row_gap) // len(rows)

    for i, (num, title, desc) in enumerate(rows):
        n = i + 1
        ry = body_top + i * (row_h + row_gap)
        card = add_rect(slide, f"row-{n}-card", body_left, ry, body_w, row_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Ghost number
        add_text(slide, f"row-{n}-ghost", num,
                 x_px=body_left + 8, y_px=ry + 2, w_px=64, h_px=row_h - 4,
                 font_size_px=40, color=BRAND_ACCENT_SOFT, bold=True,
                 anchor="middle")
        # Badge
        bsize = 26
        bx = body_left + 78
        by = ry + (row_h - bsize) // 2
        add_rect(slide, f"row-{n}-badge-bg", bx, by, bsize, bsize, BRAND_PRIMARY)
        add_text(slide, f"row-{n}-badge", num,
                 x_px=bx, y_px=by, w_px=bsize, h_px=bsize,
                 font_size_px=12, color=WHITE, bold=True,
                 align="center", anchor="middle")
        # Title
        add_text(slide, f"row-{n}-title", title,
                 x_px=bx + bsize + 16, y_px=ry + 8, w_px=380, h_px=row_h - 16,
                 font_size_px=14, color=BRAND_PRIMARY, bold=True, anchor="middle")
        # Description (right of title)
        add_text(slide, f"row-{n}-desc", desc,
                 x_px=bx + bsize + 16 + 380 + 16, y_px=ry + 8,
                 w_px=body_w - (bx + bsize + 16 + 380 + 16 - body_left) - 16, h_px=row_h - 16,
                 font_size_px=11, color=TEXT_MID, anchor="middle")

    add_footer(slide, page_num=333)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "333_7bucket-numbered-list.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
