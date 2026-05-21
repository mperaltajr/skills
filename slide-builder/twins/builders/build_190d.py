"""
Builder for pattern 190d: Core Competency Tree — DARK variant.

Light source: twins/builders/build_190.py
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
        "Building a <strong>Competitive Edge</strong> Through Core Competencies",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Structured view of capability domains, key disciplines, and differentiation drivers",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    fw_top = 220
    fw_bot = 620
    fw_left = 64
    fw_right = 1280 - 64
    fw_w = fw_right - fw_left
    canvas = add_rect(slide, "chart-canvas", fw_left, fw_top, fw_w, fw_bot - fw_top, CARD_BG_DARK)
    canvas.line.color.rgb = CARD_BORDER_DARK
    canvas.line.width = 9525

    root_w = 240
    root_x = fw_left + (fw_w - root_w) // 2
    root_y = fw_top + 16
    add_rect(slide, "tree-root-bg", root_x, root_y, root_w, 36, BRAND_ACCENT)
    add_text(slide, "tree-root", "Core Competency Platform",
             x_px=root_x, y_px=root_y, w_px=root_w, h_px=36,
             font_size_px=14, color=WHITE, bold=True, align="center", anchor="middle")

    branch_y = root_y + 36 + 40
    branch_w = 260
    branch_gap = 32
    branches_total = 3 * branch_w + 2 * branch_gap
    branch_start_x = fw_left + (fw_w - branches_total) // 2

    branches = [
        ("Technology & Engineering",
         [("Cloud Architecture", "Multi-cloud & hybrid platforms"),
          ("AI / ML Solutions", "Applied intelligence at scale"),
          ("Cybersecurity", "Zero-trust & threat response")]),
        ("Industry Expertise",
         [("Sector Knowledge", "Deep domain specialists"),
          ("Regulatory Acumen", "Compliance & policy alignment"),
          ("Market Intelligence", "Trend analysis & benchmarking")]),
        ("Delivery & Operations",
         [("Agile Execution", "Iterative delivery frameworks"),
          ("Talent & Culture", "High-performance teaming")]),
    ]
    leaf_h = 38
    for i, (bname, leaves) in enumerate(branches):
        bx = branch_start_x + i * (branch_w + branch_gap)
        add_rect(slide, f"tree-branch-{i+1}-bg", bx, branch_y, branch_w, 32, BRAND_ACCENT_SOFT)
        add_text(slide, f"tree-branch-{i+1}-name", bname,
                 x_px=bx, y_px=branch_y, w_px=branch_w, h_px=32,
                 font_size_px=12, color=BRAND_PRIMARY, bold=True, align="center", anchor="middle")
        leaf_top = branch_y + 32 + 24
        for j, (lname, lsub) in enumerate(leaves):
            ly = leaf_top + j * (leaf_h + 8)
            leaf_bg = add_rect(slide, f"tree-branch-{i+1}-leaf-{j+1}-bg", bx, ly, branch_w, leaf_h, BRAND_PRIMARY)
            leaf_bg.line.color.rgb = CARD_BORDER_DARK
            leaf_bg.line.width = 9525
            add_text(slide, f"tree-branch-{i+1}-leaf-{j+1}", lname,
                     x_px=bx, y_px=ly + 4, w_px=branch_w, h_px=14,
                     font_size_px=11, color=WHITE, bold=True, align="center")
            add_text(slide, f"tree-branch-{i+1}-leaf-{j+1}-sub", lsub,
                     x_px=bx, y_px=ly + 20, w_px=branch_w, h_px=14,
                     font_size_px=10, color=TEXT_ON_DARK_MID, align="center")

    diff_y = fw_bot - 44
    add_text(slide, "diff-label", "COMPETITIVE DIFFERENTIATION",
             x_px=fw_left + 12, y_px=diff_y + 12, w_px=200, h_px=18,
             font_size_px=9, color=TEXT_ON_DARK_MID, bold=True, uppercase=True)
    chips = ["End-to-End Integration", "Proprietary Toolchain", "Global Talent Network"]
    chip_start = fw_left + 240
    chip_w = (fw_w - 240 - 12) // 3 - 12
    for i, chip in enumerate(chips):
        cx = chip_start + i * (chip_w + 12)
        add_text(slide, f"diff-chip-{i+1}", chip,
                 x_px=cx, y_px=diff_y + 8, w_px=chip_w, h_px=24,
                 font_size_px=11, color=WHITE, bold=True, align="center", anchor="middle",
                 bg_fill=BRAND_ACCENT)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "190",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "190d_core-competency-tree-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
