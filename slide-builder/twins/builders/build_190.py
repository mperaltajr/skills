"""
Builder for pattern 190: Core Competency Tree.

Picture-asset chart-canvas placeholder + native text overlays for root, 3 branches,
8 leaves, and differentiator band (pattern-local tree-* + diff-chip-N IDs).

Source HTML: _pattern-library/190_core-competency-tree.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Building a <strong>Competitive Edge</strong> Through Core Competencies",
        subtitle="Structured view of capability domains, key disciplines, and differentiation drivers",
        title_h=42, subtitle_h=20, brand_rule_w=64,
    )

    # Chart canvas area
    fw_top = 170
    fw_bot = 600
    fw_left = 64
    fw_right = 1280 - 64
    fw_w = fw_right - fw_left
    canvas = add_rect(slide, "chart-canvas", fw_left, fw_top, fw_w, fw_bot - fw_top, CARD_BG)
    canvas.line.color.rgb = CARD_BORDER
    canvas.line.width = 9525

    # Root node (centered top)
    root_w = 240
    root_x = fw_left + (fw_w - root_w) // 2
    root_y = fw_top + 16
    add_rect(slide, "tree-root-bg", root_x, root_y, root_w, 36, BRAND_PRIMARY)
    add_text(slide, "tree-root", "Core Competency Platform",
             x_px=root_x, y_px=root_y, w_px=root_w, h_px=36,
             font_size_px=14, color=WHITE, bold=True, align="center", anchor="middle")

    # Branch row: 3 columns
    branch_y = root_y + 36 + 50  # after vertical connector
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
        # Branch node
        add_rect(slide, f"tree-branch-{i+1}-bg", bx, branch_y, branch_w, 32, BRAND_PRIMARY_MID)
        add_text(slide, f"tree-branch-{i+1}-name", bname,
                 x_px=bx, y_px=branch_y, w_px=branch_w, h_px=32,
                 font_size_px=12, color=WHITE, bold=True, align="center", anchor="middle")
        # Leaves
        leaf_top = branch_y + 32 + 28
        for j, (lname, lsub) in enumerate(leaves):
            ly = leaf_top + j * (leaf_h + 8)
            leaf_bg = add_rect(slide, f"tree-branch-{i+1}-leaf-{j+1}-bg", bx, ly, branch_w, leaf_h, CARD_BG)
            leaf_bg.line.color.rgb = CARD_BORDER
            leaf_bg.line.width = 9525
            add_text(slide, f"tree-branch-{i+1}-leaf-{j+1}", lname,
                     x_px=bx, y_px=ly + 4, w_px=branch_w, h_px=14,
                     font_size_px=11, color=TEXT_DARK, bold=True, align="center")
            add_text(slide, f"tree-branch-{i+1}-leaf-{j+1}-sub", lsub,
                     x_px=bx, y_px=ly + 20, w_px=branch_w, h_px=14,
                     font_size_px=10, color=TEXT_MID, align="center")

    # Diff band at bottom of canvas
    diff_y = fw_bot - 44
    add_text(slide, "diff-label", "COMPETITIVE DIFFERENTIATION",
             x_px=fw_left + 12, y_px=diff_y + 12, w_px=200, h_px=18,
             font_size_px=9, color=TEXT_MID, bold=True, uppercase=True)
    chips = ["End-to-End Integration", "Proprietary Toolchain", "Global Talent Network"]
    chip_start = fw_left + 240
    chip_w = (fw_w - 240 - 12) // 3 - 12
    for i, chip in enumerate(chips):
        cx = chip_start + i * (chip_w + 12)
        add_text(slide, f"diff-chip-{i+1}", chip,
                 x_px=cx, y_px=diff_y + 8, w_px=chip_w, h_px=24,
                 font_size_px=11, color=WHITE, bold=True, align="center", anchor="middle",
                 bg_fill=BRAND_PRIMARY)

    add_footer(slide, page_num=190)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "190_core-competency-tree.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
