"""
Builder for pattern 315: 2-bucket dark split.

Two side-by-side buckets with label, heading, bullets, and bottom stat.

Source HTML: _pattern-library/315_2bucket-dark-split.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
BUCKET_LEFT_BG = RGBColor(0x3C, 0x1F, 0x5C)
BUCKET_RIGHT_BG = RGBColor(0x42, 0x24, 0x68)
CARD_BORDER = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY


    # Canonical chrome
    add_text(slide, "title",
             "Two paths to <strong>accelerated value</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=24, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subhead",
             "Side-by-side comparison of strategic options across the transformation horizon",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 80, 3, BRAND_ACCENT_SOFT)

    # 2 buckets — body shifted to clear brand rule
    body_top = 220
    body_bot = 668
    body_left = 48
    body_right = 1232
    body_w = body_right - body_left
    bucket_w = body_w // 2
    divider_x = body_left + bucket_w

    buckets = [
        ("BUCKET 1", "Operational\nExcellence",
         ["Streamline core delivery processes end-to-end",
          "Automate high-volume, low-judgment workflows",
          "Reduce cycle time across handoff points",
          "Establish real-time performance visibility"],
         "↓38%", "COST REDUCTION POTENTIAL",
         BUCKET_LEFT_BG),
        ("BUCKET 2", "Growth\nAcceleration",
         ["Expand addressable markets through digital channels",
          "Unlock new revenue streams via platform plays",
          "Shorten time-to-market for priority offerings",
          "Deepen client relationships with data-led insights"],
         "+2.4×", "REVENUE GROWTH MULTIPLIER",
         BUCKET_RIGHT_BG),
    ]
    for i, (lbl, head, bullets, stat_v, stat_l, bgcol) in enumerate(buckets):
        bx = body_left + i * bucket_w
        bh = body_bot - body_top
        add_rect(slide, f"bucket-{i+1}-bg", bx, body_top, bucket_w, bh, bgcol)
        # Top accent
        add_rect(slide, f"bucket-{i+1}-top", bx, body_top, bucket_w, 4, BRAND_ACCENT)
        # Label
        add_text(slide, f"bucket-{i+1}-label", lbl,
                 x_px=bx + 28, y_px=body_top + 20, w_px=bucket_w - 56, h_px=16,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=2)
        # Heading
        add_text(slide, f"bucket-{i+1}-heading", head,
                 x_px=bx + 28, y_px=body_top + 44, w_px=bucket_w - 56, h_px=70,
                 font_size_px=22, color=WHITE, bold=True)
        # Bullets
        by = body_top + 130
        for j, b in enumerate(bullets):
            add_rect(slide, f"bucket-{i+1}-dash-{j+1}", bx + 28, by + 8, 6, 1, BRAND_ACCENT_SOFT)
            add_text(slide, f"bucket-{i+1}-bullet-{j+1}", b,
                     x_px=bx + 42, y_px=by, w_px=bucket_w - 70, h_px=44,
                     font_size_px=12, color=TEXT_ON_DARK_MID)
            by += 42
        # Stat at bottom
        st_y = body_bot - 88
        add_rect(slide, f"bucket-{i+1}-rule", bx + 28, st_y, bucket_w - 56, 1, CARD_BORDER)
        add_text(slide, f"bucket-{i+1}-stat-value", stat_v,
                 x_px=bx + 28, y_px=st_y + 14, w_px=bucket_w - 56, h_px=42,
                 font_size_px=30, color=BRAND_ACCENT_SOFT, bold=True)
        add_text(slide, f"bucket-{i+1}-stat-label", stat_l,
                 x_px=bx + 28, y_px=st_y + 58, w_px=bucket_w - 56, h_px=20,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT, letter_spacing_px=1)

    # Vertical divider between buckets
    add_rect(slide, "bucket-divider", divider_x, body_top + 10, 1, body_bot - body_top - 20, CARD_BORDER)

    # Footer
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "315",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "315_2bucket-dark-split.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
