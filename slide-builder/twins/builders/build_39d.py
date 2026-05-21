"""
Dark variant of pattern 39: Issue tree.

Source HTML: _pattern-library/39_issue-tree-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT_SOFT, WHITE,
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
        "Why are decks slow — three levels of MECE decomposition.",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Branching by mutually exclusive categories surfaces where time actually leaks — not where it feels slow.",
        x_px=64, y_px=108, w_px=900, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    tree_left = 56
    tree_top = 180

    # Root box
    root_x = tree_left
    root_y = tree_top + 168
    root_w = 240
    root_h = 80
    add_rect(slide, "tree-root", root_x, root_y, root_w, root_h, BRAND_ACCENT_SOFT)
    add_text(
        slide, "tree-root-tag", "Root question",
        x_px=root_x + 14, y_px=root_y + 14, w_px=root_w - 28, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY, bold=True,
        letter_spacing_px=1.2, uppercase=True,
    )
    add_text(
        slide, "tree-root-label", "Why are decks slow to produce?",
        x_px=root_x + 14, y_px=root_y + 32, w_px=root_w - 28, h_px=40,
        font_size_px=15, color=BRAND_PRIMARY, bold=True,
    )

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

    l2_x = tree_left + 760
    l2_w = 280
    l2_h = 54
    l2_offsets = [
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
        box = add_rect(slide, sid_base, l2_x, ly, l2_w, l2_h, CARD_BG_DARK)
        box.line.color.rgb = CARD_BORDER_DARK
        box.line.width = 9525
        add_text(
            slide, f"{sid_base}-tag", tag,
            x_px=l2_x + 14, y_px=ly + 6, w_px=l2_w - 28, h_px=12,
            font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
            letter_spacing_px=1.2,
        )
        add_text(
            slide, f"{sid_base}-label", label,
            x_px=l2_x + 14, y_px=ly + 20, w_px=l2_w - 28, h_px=30,
            font_size_px=12, color=WHITE,
        )

    # Connector arrows: root → L1, L1 → L2 (L-shaped routes; thin lines + arrowheads).
    connector_color = CARD_BORDER_DARK
    line_h = 1

    def _hline(sid, x, y, w):
        add_rect(slide, sid, x, y, w, line_h, connector_color)

    def _vline(sid, x, y, h):
        add_rect(slide, sid, x, y, line_h, h, connector_color)

    def _arrow_head(sid, x, y):
        # Small right-pointing triangle approximation: 3 stacked tiny rects.
        add_rect(slide, sid + "-1", x, y - 2, 2, 1, BRAND_ACCENT_SOFT)
        add_rect(slide, sid + "-2", x, y - 1, 4, 1, BRAND_ACCENT_SOFT)
        add_rect(slide, sid + "-3", x, y, 5, 1, BRAND_ACCENT_SOFT)
        add_rect(slide, sid + "-4", x, y + 1, 4, 1, BRAND_ACCENT_SOFT)
        add_rect(slide, sid + "-5", x, y + 2, 2, 1, BRAND_ACCENT_SOFT)

    # Root → 3 L1 connectors
    root_cx = root_x + root_w
    root_cy = root_y + root_h // 2
    mid_x = (root_cx + l1_x) // 2
    _hline("conn-root-stub", root_cx, root_cy, mid_x - root_cx)
    for i in range(3):
        l1_cy = l1_tops[i] + l1_h // 2
        # vertical segment from root level to l1 level
        top_y = min(root_cy, l1_cy)
        h = abs(l1_cy - root_cy)
        if h > 0:
            _vline(f"conn-root-v-{i+1}", mid_x, top_y, h)
        _hline(f"conn-root-h-{i+1}", mid_x, l1_cy, l1_x - mid_x - 5)
        _arrow_head(f"conn-root-arrow-{i+1}", l1_x - 5, l1_cy)

    # L1 → L2 connectors (each L1 fans to 2 L2 boxes)
    l1_right = l1_x + l1_w
    mid_x2 = (l1_right + l2_x) // 2
    pairs = [(0, [0, 1]), (1, [2, 3]), (2, [4, 5])]
    for l1_idx, l2_idxs in pairs:
        l1_cy = l1_tops[l1_idx] + l1_h // 2
        _hline(f"conn-l1-{l1_idx+1}-stub", l1_right, l1_cy, mid_x2 - l1_right)
        for j, l2_i in enumerate(l2_idxs):
            l2_cy = l2_offsets[l2_i][0] + l2_h // 2
            top_y = min(l1_cy, l2_cy)
            h = abs(l2_cy - l1_cy)
            if h > 0:
                _vline(f"conn-l1-{l1_idx+1}-v-{j+1}", mid_x2, top_y, h)
            _hline(f"conn-l1-{l1_idx+1}-h-{j+1}", mid_x2, l2_cy, l2_x - mid_x2 - 5)
            _arrow_head(f"conn-l1-{l1_idx+1}-arrow-{j+1}", l2_x - 5, l2_cy)

    conv_y = 632
    add_rect(slide, "convergence-rule", x_px=56, y_px=conv_y, w_px=1280 - 112, h_px=1,
             fill_color=CARD_BORDER_DARK)
    add_text(
        slide, "convergence",
        "Three levels deep is enough. Beyond that, the tree branches faster than the answer matters.",
        x_px=56, y_px=conv_y + 14, w_px=1280 - 112, h_px=24,
        font_size_px=13, color=WHITE, italic=True,
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(
        slide, "source", "Source: [add source here or delete]",
        x_px=58, y_px=688, w_px=1100, h_px=16,
        font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True,
    )
    add_text(
        slide, "page-number", "39",
        x_px=1170, y_px=688, w_px=52, h_px=16,
        font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right",
    )
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "39d_issue-tree.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
