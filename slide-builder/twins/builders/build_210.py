"""
Builder for pattern 210: Two-column compare with icon headers + critical row.

Source HTML: _pattern-library/210_two-column-compare-icons.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, CARD_BG, CARD_BORDER, WHITE,
)
from pptx.dml.color import RGBColor

RED_SOFT = RGBColor(0xFE, 0xE2, 0xE2)
GREEN_SOFT = RGBColor(0xDC, 0xFC, 0xE7)
RED_TXT = RGBColor(0xDC, 0x26, 0x26)
GREEN_TXT = RGBColor(0x16, 0xA3, 0x4A)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Bridging the gap between <strong>today's constraints</strong> and tomorrow's potential",
        subtitle="A structured view of current pain points versus the improved future state — with a clear path forward",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # Body: top:138, left:48, right:48 (w=1184), bottom 76
    body_top = 138
    body_left = 48
    body_w = 1184
    col_w = (body_w - 32) // 2  # 576 each, 32 px gap
    left_x = body_left
    right_x = body_left + col_w + 32
    # Vertical divider line between cols
    add_rect(slide, "panel-divider", body_left + col_w + 14, body_top, 2, 480, CARD_BORDER)

    # Column headers (icon circle + title + pill)
    header_y = body_top + 6
    # Left header
    add_icon(slide, "panel-1-icon", left_x, header_y, 28, "✗", color=RED_TXT)
    add_text(slide, "panel-1-heading", "Current State",
             x_px=left_x + 36, y_px=header_y + 2, w_px=200, h_px=18,
             font_size_px=13, color=TEXT_DARK, bold=True)
    add_text(slide, "panel-1-label", "AS IS",
             x_px=left_x + 36, y_px=header_y + 20, w_px=50, h_px=14,
             font_size_px=9, color=RED_TXT, bold=True, bg_fill=RED_SOFT,
             padding_px=(2, 4, 2, 4), align="center", uppercase=True)
    # Right header
    add_icon(slide, "panel-2-icon", right_x, header_y, 28, "✓", color=GREEN_TXT)
    add_text(slide, "panel-2-heading", "Future State",
             x_px=right_x + 36, y_px=header_y + 2, w_px=200, h_px=18,
             font_size_px=13, color=TEXT_DARK, bold=True)
    add_text(slide, "panel-2-label", "TO BE",
             x_px=right_x + 36, y_px=header_y + 20, w_px=50, h_px=14,
             font_size_px=9, color=GREEN_TXT, bold=True, bg_fill=GREEN_SOFT,
             padding_px=(2, 4, 2, 4), align="center", uppercase=True)
    # Header bottom border
    add_rect(slide, "header-rule-1", left_x, header_y + 44, col_w - 16, 2, CARD_BORDER)
    add_rect(slide, "header-rule-2", right_x, header_y + 44, col_w - 16, 2, CARD_BORDER)

    rows = [
        ("Manual reporting cycles take 3–5 days and require significant analyst effort",
         "Automated pipelines deliver real-time dashboards with zero manual intervention", False),
        ("Data siloed across 6+ systems with no single source of truth",
         "Unified data platform provides a governed, enterprise-wide source of truth", False),
        ("Decisions delayed by 2+ weeks due to lack of integrated customer insight",
         "AI-driven insight layer surfaces actionable recommendations within hours", True),  # critical
        ("High operational cost from duplicated processes and redundant tooling",
         "Consolidated toolchain reduces operational overhead by an estimated 35%", False),
        ("Teams operate reactively, unable to anticipate demand or capacity needs",
         "Predictive models enable proactive planning with 90-day forward visibility", False),
    ]
    rows_top = header_y + 56
    row_h = 70
    for i, (left, right, critical) in enumerate(rows):
        n = i + 1
        ry = rows_top + i * row_h
        if critical:
            add_rect(slide, f"row-{n}-bg", left_x, ry, body_w, row_h, CARD_BG)
            add_rect(slide, f"row-{n}-top", left_x, ry, body_w, 2, BRAND_ACCENT)
            add_rect(slide, f"row-{n}-bot", left_x, ry + row_h - 2, body_w, 2, BRAND_ACCENT)
            color = BRAND_PRIMARY
        else:
            color = TEXT_DARK
        # Left cell
        add_rect(slide, f"panel-1-row-{n}-dot", left_x + 4, ry + row_h // 2 - 3, 6, 6, RED_TXT)
        add_text(slide, f"panel-1-row-{n}", left,
                 x_px=left_x + 16, y_px=ry + 4, w_px=col_w - 30, h_px=row_h - 8,
                 font_size_px=12, color=color, bold=critical, anchor="middle")
        # Critical tag
        if critical:
            add_text(slide, f"panel-1-row-{n}-tag", "CRITICAL",
                     x_px=left_x + col_w - 70, y_px=ry + row_h // 2 - 8, w_px=60, h_px=14,
                     font_size_px=8, color=BRAND_ACCENT, bold=True, align="center",
                     bg_fill=RGBColor(0xF3, 0xE6, 0xFF), padding_px=(2, 4, 2, 4))
        # Right cell
        add_rect(slide, f"panel-2-row-{n}-dot", right_x + 4, ry + row_h // 2 - 3, 6, 6, GREEN_TXT)
        add_text(slide, f"panel-2-row-{n}", right,
                 x_px=right_x + 16, y_px=ry + 4, w_px=col_w - 30, h_px=row_h - 8,
                 font_size_px=12, color=color, bold=critical, anchor="middle")
        # Row divider (full width)
        if i < len(rows) - 1:
            add_rect(slide, f"row-{n}-divider", left_x, ry + row_h - 1, body_w, 1, CARD_BORDER)

    # Convergence bar
    conv_y = 720 - 76 - 38
    add_rect(slide, "convergence-bg", 48, conv_y, body_w, 38, BRAND_PRIMARY)
    add_text(slide, "convergence-mark", "→",
             x_px=64, y_px=conv_y, w_px=24, h_px=38,
             font_size_px=18, color=BRAND_ACCENT_SOFT, bold=True, anchor="middle")
    add_text(slide, "convergence",
             "Closing this gap requires a unified data and AI platform with phased adoption — achievable in 9 months.",
             x_px=92, y_px=conv_y, w_px=body_w - 60, h_px=38,
             font_size_px=12, color=WHITE, anchor="middle")

    add_footer(slide, page_num=210)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "210_two-column-compare-icons.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
