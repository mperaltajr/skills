"""
Builder for pattern 82: McKinsey 7S framework (picture-asset SVG + legend).

Source HTML: _pattern-library/82_mckinsey-7s-framework.html

The 7S diagram is treated as picture-asset (chart-canvas placeholder rectangle).
The accompanying legend column on the right is stamped with canonical legend-N-*
IDs plus pattern-local status fields.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT,
)
from pptx.dml.color import RGBColor

STATUS_STRONG_BG = RGBColor(0xE6, 0xF6, 0xEC)
STATUS_STRONG_TXT = RGBColor(0x0E, 0x7A, 0x37)
STATUS_BUILD_BG = RGBColor(0xFF, 0xF4, 0xD6)
STATUS_BUILD_TXT = RGBColor(0x8A, 0x5A, 0x00)
STATUS_GAP_BG = RGBColor(0xFC, 0xE4, 0xE4)
STATUS_GAP_TXT = RGBColor(0xB4, 0x21, 0x21)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Slide Lab through the 7S lens — Shared Values anchor the rest.",
        subtitle="Six elements orbit one center. When Shared Values drift, every other S has to compensate — and the network frays.",
        title_x=64, title_w=1152, title_h=60,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # Body block: diagram column on the LEFT (centered in its half) +
    # legend column on the right. Target a ~50/50 split with the diagram
    # visually centered in the left half so the 7S shape sits inside its
    # own zone instead of running edge-to-edge into the legend.
    body_top = 200
    body_bot = 720 - 120
    body_h = body_bot - body_top  # 400
    body_left = 64
    body_right = 1280 - 64
    body_w = body_right - body_left  # 1152
    gap = 36
    diag_w = 500  # shape canvas — narrower than before so it reads as "left half"
    diag_half_w = (body_w - gap) // 2  # 558 — the actual left-half region
    # Center the diagram canvas inside the left half
    diag_x = body_left + (diag_half_w - diag_w) // 2
    legend_x = body_left + diag_half_w + gap
    legend_w = body_right - legend_x

    # Diagram canvas placeholder (picture-asset target)
    diag_bg = add_rect(slide, "chart-canvas",
                       diag_x, body_top, diag_w, body_h, CARD_BG)
    diag_bg.line.color.rgb = CARD_BORDER
    diag_bg.line.width = 9525

    # Center "Shared Values" hub indicator (text overlay)
    add_text(
        slide, "chart-canvas-placeholder", "[ 7S DIAGRAM — Shared Values center, 6 outer Ss ]",
        x_px=diag_x, y_px=body_top, w_px=diag_w, h_px=body_h,
        font_size_px=12, color=TEXT_FAINT, italic=True,
        align="center", anchor="middle",
    )

    # Legend column
    add_text(slide, "legend-title", "The 7 S's — Slide Lab today",
             x_px=legend_x, y_px=body_top + 4, w_px=legend_w, h_px=18,
             font_size_px=10, color=BRAND_PRIMARY, bold=True, uppercase=True)
    add_rect(slide, "legend-title-rule",
             legend_x, body_top + 26, legend_w, 1, CARD_BORDER)

    rows = [
        ("Shared Values", "Render real artifacts; never fake the QC.", "Strong", BRAND_ACCENT),
        ("Strategy", "Coach the consultant, then build the deck.", "Strong", BRAND_PRIMARY),
        ("Structure", "Skills + skeleton library + QC reviewer.", "Building", BRAND_PRIMARY),
        ("Systems", "Token fill, COM render, vision QC loop.", "Building", BRAND_PRIMARY),
        ("Skills", "Pattern matching, narrative coaching, viz.", "Strong", BRAND_PRIMARY),
        ("Staff", "One consultant + Claude as co-pilot.", "Building", BRAND_PRIMARY),
        ("Style", "Blunt, direct, show before tell.", "Drifts", BRAND_PRIMARY),
    ]

    row_h = 48
    rows_top = body_top + 36
    for i, (name, desc, status, name_color) in enumerate(rows):
        n = i + 1
        ry = rows_top + i * row_h

        # Name column
        add_text(slide, f"legend-{n}-name", name,
                 x_px=legend_x, y_px=ry + 4, w_px=86, h_px=20,
                 font_size_px=11, color=name_color, bold=True)

        # Description
        add_text(slide, f"legend-{n}-desc", desc,
                 x_px=legend_x + 88, y_px=ry + 4, w_px=legend_w - 88 - 64, h_px=40,
                 font_size_px=10, color=TEXT_DARK)

        # Status pill
        if status == "Strong":
            bg = STATUS_STRONG_BG
            txt = STATUS_STRONG_TXT
        elif status == "Building":
            bg = STATUS_BUILD_BG
            txt = STATUS_BUILD_TXT
        else:
            bg = STATUS_GAP_BG
            txt = STATUS_GAP_TXT
        add_text(slide, f"legend-{n}-status", status,
                 x_px=legend_x + legend_w - 60, y_px=ry + 4, w_px=58, h_px=18,
                 font_size_px=9, color=txt, bold=True, align="center", uppercase=True,
                 bg_fill=bg, padding_px=(2, 4, 2, 4))

        # Dashed-ish row separator (last row no border in HTML)
        if i < len(rows) - 1:
            add_rect(slide, f"legend-{n}-rule",
                     legend_x, ry + row_h - 1, legend_w, 1, CARD_BORDER)

    add_convergence(
        slide,
        "Move any outer S and the spokes pull — but move Shared Values and the whole network reshapes.",
        bottom_px=70, height_px=42,
    )

    add_footer(slide, page_num=82)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "82_mckinsey-7s-framework.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
