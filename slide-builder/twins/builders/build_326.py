"""
Builder for pattern 326: 5-bucket numbered column (5 row cards on left + summary panel right).

Source HTML: _pattern-library/326_5bucket-numbered-column.html
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
from pptx.dml.color import RGBColor

PILL_GREEN_BG = RGBColor(0xD1, 0xFA, 0xE5)
PILL_GREEN_FG = RGBColor(0x06, 0x5F, 0x46)
PILL_AMBER_BG = RGBColor(0xFE, 0xF3, 0xC7)
PILL_AMBER_FG = RGBColor(0x92, 0x40, 0x0E)
PILL_BLUE_BG = RGBColor(0xDB, 0xEA, 0xFE)
PILL_BLUE_FG = RGBColor(0x1E, 0x40, 0xAF)
PILL_PURPLE_BG = RGBColor(0xED, 0xE9, 0xFE)
PILL_PURPLE_FG = RGBColor(0x5B, 0x21, 0xB6)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Five priorities that will define whether this program delivers <strong>lasting impact</strong>.",
        subtitle="Each bucket represents a distinct action area — tracked independently, resolved sequentially.",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top

    left_w = 760
    right_x = body_left + left_w + 16
    right_w = body_w - left_w - 16

    rows = [
        ("1", "Establish executive sponsorship",
         "Secure named C-suite champion with decision authority over budget and scope to unblock escalations."),
        ("2", "Define measurable success criteria",
         "Agree KPIs before mobilisation — financial, operational, and adoption targets locked at program launch."),
        ("3", "Integrate into core business cadence",
         "Embed deliverables into monthly operating reviews and governance forums — not a parallel workstream."),
        ("4", "Deploy standardised tooling at scale",
         "Mandated playbooks, templates, and platforms — adoption tracked and enforced across all teams."),
        ("5", "Close capability gap with upskilling plan",
         "Structured learning pathway with role-based certification milestones tied to performance objectives."),
    ]
    row_gap = 6
    row_h = (body_h - 4 * row_gap) // 5

    for i, (num, title, desc) in enumerate(rows):
        n = i + 1
        ry = body_top + i * (row_h + row_gap)
        card = add_rect(slide, f"row-{n}-card", body_left, ry, left_w, row_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Ghost number
        add_text(
            slide, f"row-{n}-ghost", num,
            x_px=body_left + 8, y_px=ry + 6, w_px=70, h_px=row_h - 12,
            font_size_px=58, color=BRAND_ACCENT_SOFT, bold=True,
        )
        # Badge
        bx = body_left + 78
        bsize = 26
        by = ry + (row_h - bsize) // 2
        add_rect(slide, f"row-{n}-badge-bg", bx, by, bsize, bsize, BRAND_PRIMARY)
        add_text(
            slide, f"row-{n}-badge", num,
            x_px=bx, y_px=by, w_px=bsize, h_px=bsize,
            font_size_px=12, color=WHITE, bold=True, align="center", anchor="middle",
        )
        # Title + desc
        add_text(
            slide, f"row-{n}-title", title,
            x_px=bx + bsize + 14, y_px=ry + 14, w_px=left_w - bsize - 90, h_px=22,
            font_size_px=14, color=BRAND_PRIMARY, bold=True,
        )
        add_text(
            slide, f"row-{n}-desc", desc,
            x_px=bx + bsize + 14, y_px=ry + 38, w_px=left_w - bsize - 90, h_px=row_h - 44,
            font_size_px=11, color=TEXT_MID,
        )

    # Right summary panel
    sp = add_rect(slide, "summary-panel", right_x, body_top, right_w, body_h, CARD_BG)
    sp.line.color.rgb = CARD_BORDER
    sp.line.width = 9525
    add_text(
        slide, "summary-header", "SUMMARY",
        x_px=right_x + 16, y_px=body_top + 14, w_px=right_w - 32, h_px=18,
        font_size_px=10, color=BRAND_PRIMARY, bold=True, letter_spacing_px=1.6,
    )
    add_rect(slide, "summary-rule",
             right_x + 16, body_top + 36, right_w - 32, 2, BRAND_PRIMARY)

    comp_top = body_top + 50
    comp_h = (body_h - 56) // 5
    comps = [
        ("3 sponsors", "Exec alignment", "On track", "green"),
        ("8 KPIs", "Agreed metrics", "In review", "amber"),
        ("2 of 4", "Forums embedded", "Partial", "amber"),
        ("74% adopted", "Tooling coverage", "Scaling", "blue"),
        ("42 certified", "Upskilling cohort", "Building", "purple"),
    ]
    pill_bg_map = {"green": PILL_GREEN_BG, "amber": PILL_AMBER_BG,
                   "blue": PILL_BLUE_BG, "purple": PILL_PURPLE_BG}
    pill_fg_map = {"green": PILL_GREEN_FG, "amber": PILL_AMBER_FG,
                   "blue": PILL_BLUE_FG, "purple": PILL_PURPLE_FG}
    for i, (stat, label, pill_lbl, pill_color) in enumerate(comps):
        n = i + 1
        cy = comp_top + i * comp_h
        # divider top (except first)
        if i > 0:
            add_rect(slide, f"comp-{n}-divider",
                     right_x + 16, cy, right_w - 32, 1, CARD_BORDER)
        add_text(
            slide, f"comp-{n}-num", str(n),
            x_px=right_x + 16, y_px=cy + 12, w_px=20, h_px=18,
            font_size_px=10, color=TEXT_FAINT, bold=True, align="center",
        )
        add_text(
            slide, f"comp-{n}-stat", stat,
            x_px=right_x + 42, y_px=cy + 8, w_px=right_w - 90, h_px=22,
            font_size_px=16, color=BRAND_PRIMARY, bold=True,
        )
        add_text(
            slide, f"comp-{n}-label", label,
            x_px=right_x + 42, y_px=cy + 30, w_px=right_w - 90, h_px=14,
            font_size_px=10, color=TEXT_MID,
        )
        pill_w = len(pill_lbl) * 6 + 16
        pill_h = 18
        pill_x = right_x + right_w - pill_w - 12
        pill_y = cy + (comp_h - pill_h) // 2
        pill = add_rect(slide, f"comp-{n}-pill", pill_x, pill_y, pill_w, pill_h,
                        pill_bg_map[pill_color])
        pill.line.fill.background()
        add_text(
            slide, f"comp-{n}-pill-text", pill_lbl,
            x_px=pill_x, y_px=pill_y, w_px=pill_w, h_px=pill_h,
            font_size_px=8, color=pill_fg_map[pill_color], bold=True,
            align="center", anchor="middle", letter_spacing_px=0.8,
        )

    add_footer(slide, page_num=326)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "326_5bucket-numbered-column.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
