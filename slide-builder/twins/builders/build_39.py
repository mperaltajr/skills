"""
Builder for pattern 39: Issue tree (MECE decomposition).

Three-level horizontal tree: 1 root → 3 L1 nodes → 6 L2 nodes (2 per L1).
Tree connectors (L-shaped routes) are decorative; we render as static
rectangles for simplicity since they're geometric.

Pattern-local IDs: tree-root, tree-root-tag, tree-root-label,
tree-l1-N, tree-l1-N-tag, tree-l1-N-label,
tree-l2-N-M, tree-l2-N-M-tag, tree-l2-N-M-label.

Source HTML: _pattern-library/39_issue-tree.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Why are decks slow — three levels of MECE decomposition.",
        subtitle="Branching by mutually exclusive categories surfaces where time actually leaks — not where it feels slow.",
        title_h=64,
        subtitle_h=22,
    )

    # Tree area: top=180, left=56, right=56, h=416
    tree_left = 56
    tree_top = 180

    # Root box (240x80) at left=tree_left, top=tree_top+168
    root_x = tree_left
    root_y = tree_top + 168
    root_w = 240
    root_h = 80
    root = add_rect(slide, "tree-root", root_x, root_y, root_w, root_h, BRAND_PRIMARY)
    add_text(
        slide, "tree-root-tag", "Root question",
        x_px=root_x + 14, y_px=root_y + 14, w_px=root_w - 28, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
        letter_spacing_px=1.2, uppercase=True,
    )
    add_text(
        slide, "tree-root-label", "Why are decks slow to produce?",
        x_px=root_x + 14, y_px=root_y + 32, w_px=root_w - 28, h_px=40,
        font_size_px=15, color=WHITE, bold=True,
    )

    # L1 boxes (200x62) at left=tree_left+400
    l1_x = tree_left + 400
    l1_w = 200
    l1_h = 62
    l1_tops = [tree_top + 24, tree_top + 177, tree_top + 330]
    l1_tags = ["A", "B", "C"]
    l1_labels = ["Authoring is slow", "Reviews multiply", "Rework after partner"]

    for i in range(3):
        n = i + 1
        ly = l1_tops[i]
        add_rect(slide, f"tree-l1-{n}", l1_x, ly, l1_w, l1_h, BRAND_PRIMARY_MID)
        add_text(
            slide, f"tree-l1-{n}-tag", l1_tags[i],
            x_px=l1_x + 14, y_px=ly + 10, w_px=l1_w - 28, h_px=12,
            font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
            letter_spacing_px=1.2,
        )
        add_text(
            slide, f"tree-l1-{n}-label", l1_labels[i],
            x_px=l1_x + 14, y_px=ly + 24, w_px=l1_w - 28, h_px=30,
            font_size_px=13, color=WHITE, bold=True,
        )

    # L2 boxes (280x54) at left=tree_left+760, 2 per L1
    l2_x = tree_left + 760
    l2_w = 280
    l2_h = 54
    l2_offsets = [
        # (top relative to tree_top, parent L1 row, l2 index 1..2)
        (tree_top + 0, 1, 1),
        (tree_top + 64, 1, 2),
        (tree_top + 153, 2, 1),
        (tree_top + 217, 2, 2),
        (tree_top + 306, 3, 1),
        (tree_top + 370, 3, 2),
    ]
    l2_data = [
        ("A1", "No starting structure"),
        ("A2", "Workstreams unsynthesized"),
        ("B1", "Reviewers add ideas (no subtraction)"),
        ("B2", "Multiple parallel reviewers"),
        ("C1", "Late argument changes"),
        ("C2", "Visual treatment redone"),
    ]
    for (ly, parent_n, l2_idx), (tag, label) in zip(l2_offsets, l2_data):
        sid_base = f"tree-l2-{parent_n}-{l2_idx}"
        box = add_rect(slide, sid_base, l2_x, ly, l2_w, l2_h, CARD_BG)
        box.line.color.rgb = CARD_BORDER
        box.line.width = 9525
        add_text(
            slide, f"{sid_base}-tag", tag,
            x_px=l2_x + 14, y_px=ly + 6, w_px=l2_w - 28, h_px=12,
            font_size_px=10, color=BRAND_PRIMARY_MID, bold=True,
            letter_spacing_px=1.2,
        )
        add_text(
            slide, f"{sid_base}-label", label,
            x_px=l2_x + 14, y_px=ly + 20, w_px=l2_w - 28, h_px=30,
            font_size_px=12, color=TEXT_DARK,
        )

    # Convergence — pattern 39 uses a thin-top-border convergence
    conv_y = 632
    add_rect(slide, "convergence-rule", x_px=56, y_px=conv_y, w_px=1280 - 112, h_px=1,
             fill_color=CARD_BORDER)
    add_text(
        slide, "convergence",
        "Three levels deep is enough. Beyond that, the tree branches faster than the answer matters.",
        x_px=56, y_px=conv_y + 14, w_px=1280 - 112, h_px=24,
        font_size_px=13, color=TEXT_DARK, italic=True,
    )

    add_footer(slide, page_num=39)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "39_issue-tree.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
