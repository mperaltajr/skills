"""
Builder for pattern 277: SIPOC Diagram (Supplier/Input/Process/Output/Customer).

Source HTML: _pattern-library/277_sipoc-diagram.html

5 columns, color-coded headers, 4 item cards each (except Process: 5 numbered steps).
Arrows between columns. Scope statement bar at bottom.
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


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="<strong>SIPOC</strong> Diagram — Purchase-to-Pay Process",
        subtitle="End-to-end process mapping from suppliers to customers",
    )

    # Grid area
    grid_x = 56
    grid_y = 234
    grid_w = 1280 - 112
    grid_h = 410

    # 5 columns + 4 arrow gaps (22px each = 88 total)
    arrow_gap = 24
    total_arrow = arrow_gap * 4
    col_w = (grid_w - total_arrow) // 5

    columns = [
        ("S", "Suppliers",  BRAND_PRIMARY,
         ["Vendors", "Finance Dept", "IT Systems", "HR"]),
        ("I", "Inputs",     BRAND_PRIMARY_MID,
         ["Purchase Orders", "Budget Approvals", "System Data", "Staffing Plans"]),
        ("P", "Process",    BRAND_ACCENT, None),  # special — steps
        ("O", "Outputs",    BRAND_PRIMARY_MID,
         ["Approved Contracts", "Purchase Orders", "Performance Reports", "Payment Records"]),
        ("C", "Customers",  BRAND_PRIMARY,
         ["Business Units", "Finance", "Auditors", "Vendors"]),
    ]

    cx = grid_x
    for i, (letter, name, header_color, items) in enumerate(columns):
        col_id = ["s", "i", "p", "o", "c"][i]
        # Column container (outer border)
        outer = add_rect(slide, f"col-{col_id}", cx, grid_y, col_w, grid_h, CARD_BG)
        outer.line.color.rgb = CARD_BORDER
        outer.line.width = 9525

        # Header
        head_h = 60
        add_rect(slide, f"col-{col_id}-header", cx, grid_y, col_w, head_h, header_color)
        add_text(
            slide, f"col-{col_id}-letter", letter,
            x_px=cx, y_px=grid_y + 8, w_px=col_w, h_px=22,
            font_size_px=20, color=WHITE, bold=True, align="center",
        )
        add_text(
            slide, f"col-{col_id}-name", name,
            x_px=cx, y_px=grid_y + 34, w_px=col_w, h_px=18,
            font_size_px=10, color=WHITE, bold=True, align="center",
            uppercase=True, letter_spacing_px=1.2,
        )

        # Body items
        body_top = grid_y + head_h + 10
        body_h = grid_h - head_h - 20
        if col_id == "p":
            # Process column: 5 numbered steps with down arrows
            steps = ["Request Submission", "Approval Review", "Vendor Selection",
                     "Contract Execution", "Invoice Processing"]
            step_h = (body_h - 16) // 5
            for si, step in enumerate(steps):
                sy = body_top + si * step_h
                step_box = add_rect(slide, f"col-p-step-{si+1}-bg",
                                    cx + 8, sy, col_w - 16, step_h - 6, WHITE)
                step_box.line.color.rgb = CARD_BORDER
                step_box.line.width = 9525
                # number circle
                from pptx.enum.shapes import MSO_SHAPE
                circ = slide.shapes.add_shape(
                    MSO_SHAPE.OVAL,
                    (cx + 14) * 9525, (sy + 6) * 9525, 18 * 9525, 18 * 9525,
                )
                circ.name = f"col-p-step-{si+1}-num"
                circ.fill.solid()
                circ.fill.fore_color.rgb = BRAND_ACCENT
                circ.line.fill.background()
                add_text(
                    slide, f"col-p-step-{si+1}-num-text", str(si + 1),
                    x_px=cx + 14, y_px=sy + 6, w_px=18, h_px=18,
                    font_size_px=10, color=WHITE, bold=True,
                    align="center", anchor="middle",
                )
                add_text(
                    slide, f"col-p-step-{si+1}-text", step,
                    x_px=cx + 38, y_px=sy, w_px=col_w - 50, h_px=step_h - 6,
                    font_size_px=10, color=TEXT_DARK, bold=True, anchor="middle",
                )
        else:
            # Standard item cards
            item_h = (body_h - 4 * 6) // 4
            for ii, item in enumerate(items):
                iy = body_top + ii * (item_h + 6)
                item_box = add_rect(slide, f"col-{col_id}-item-{ii+1}-bg",
                                    cx + 8, iy, col_w - 16, item_h, WHITE)
                item_box.line.color.rgb = CARD_BORDER
                item_box.line.width = 9525
                add_text(
                    slide, f"col-{col_id}-item-{ii+1}", item,
                    x_px=cx + 12, y_px=iy, w_px=col_w - 24, h_px=item_h,
                    font_size_px=12, color=TEXT_DARK, bold=True, anchor="middle", align="center",
                )

        # Arrow after column (except last)
        if i < 4:
            ax = cx + col_w
            add_text(
                slide, f"arrow-{i+1}", "→",
                x_px=ax, y_px=grid_y + 22, w_px=arrow_gap, h_px=18,
                font_size_px=18, color=BRAND_ACCENT, bold=True, align="center",
            )

        cx = cx + col_w + arrow_gap

    # Scope bar at bottom
    scope_y = 654
    scope_h = 22
    scope_bg = add_rect(slide, "scope-bar", 56, scope_y, 1280 - 112, scope_h,
                        RGBColor(0xF6, 0xEC, 0xFB))
    scope_bg.line.color.rgb = CARD_BORDER
    scope_bg.line.width = 9525
    add_text(
        slide, "scope-label", "SCOPE",
        x_px=72, y_px=scope_y, w_px=60, h_px=scope_h,
        font_size_px=9, color=BRAND_ACCENT, bold=True, anchor="middle",
        uppercase=True, letter_spacing_px=1.2,
    )
    add_text(
        slide, "scope-text",
        "Purchase-to-Pay Process  ·  From: Initial requisition  ·  To: Vendor payment confirmed",
        x_px=132, y_px=scope_y, w_px=1280 - 200, h_px=scope_h,
        font_size_px=10, color=TEXT_MID, anchor="middle",
    )

    add_footer(slide, page_num=277)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "277_sipoc-diagram.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
