"""
Builder for pattern 314: 2-bucket comparison cards (Option A vs Option B with VS circle).

Two cards with comparison rows + Recommended footer. A decision strip at the bottom.

Source HTML: _pattern-library/314_2bucket-comparison-cards.html
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
from pptx.enum.shapes import MSO_SHAPE
from twins.helpers import px_to_emu
from pptx.dml.color import RGBColor

DOT_GOOD = RGBColor(0x22, 0xC5, 0x5E)
DOT_WARN = RGBColor(0xF5, 0x9E, 0x0B)
DOT_BAD = RGBColor(0xEF, 0x44, 0x44)


def _option_card(slide, n, x, y, w, h, *, header_color, label, name,
                 option_name, tagline, rows, recommended):
    card = add_rect(slide, f"option-{n}-card", x, y, w, h, WHITE)
    card.line.color.rgb = CARD_BORDER
    card.line.width = 9525
    # Header band
    hdr_h = 40
    add_rect(slide, f"option-{n}-header", x, y, w, hdr_h, header_color)
    add_text(
        slide, f"option-{n}-header-label", label.upper(),
        x_px=x + 16, y_px=y, w_px=80, h_px=hdr_h,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, anchor="middle",
        letter_spacing_px=1.4,
    )
    add_text(
        slide, f"option-{n}-header-name", name,
        x_px=x + 110, y_px=y, w_px=w - 130, h_px=hdr_h,
        font_size_px=14, color=WHITE, bold=True, anchor="middle",
    )
    # Icon zone
    iz_h = 90
    iz_y = y + hdr_h
    add_text(
        slide, f"option-{n}-letter", label[-1],
        x_px=x, y_px=iz_y + 8, w_px=w, h_px=40,
        font_size_px=36, color=BRAND_PRIMARY, bold=True, align="center",
    )
    add_text(
        slide, f"option-{n}-option-name", option_name,
        x_px=x + 16, y_px=iz_y + 52, w_px=w - 32, h_px=20,
        font_size_px=13, color=BRAND_PRIMARY, bold=True, align="center",
    )
    add_text(
        slide, f"option-{n}-tagline", tagline,
        x_px=x + 16, y_px=iz_y + 72, w_px=w - 32, h_px=16,
        font_size_px=10, color=TEXT_MID, italic=True, align="center",
    )
    # Comparison rows
    rows_top = iz_y + iz_h + 4
    rows_h = h - hdr_h - iz_h - 36 - 4  # leave room for footer
    row_h = rows_h // len(rows)
    dot_map = {"good": DOT_GOOD, "warn": DOT_WARN, "bad": DOT_BAD}
    for ri, (lbl, val, indicator) in enumerate(rows):
        rn = ri + 1
        ry = rows_top + ri * row_h
        bg_col = CARD_BG if ri % 2 == 0 else WHITE
        row_bg = add_rect(slide, f"option-{n}-row-{rn}-bg", x, ry, w, row_h, bg_col)
        row_bg.line.fill.background()
        add_text(
            slide, f"option-{n}-row-{rn}-label", lbl.upper(),
            x_px=x + 14, y_px=ry, w_px=80, h_px=row_h,
            font_size_px=9, color=TEXT_MID, bold=True, anchor="middle",
            letter_spacing_px=1.2,
        )
        add_text(
            slide, f"option-{n}-row-{rn}-value", val,
            x_px=x + 100, y_px=ry, w_px=w - 130, h_px=row_h,
            font_size_px=11, color=TEXT_DARK, anchor="middle",
        )
        add_rect(slide, f"option-{n}-row-{rn}-dot",
                 x + w - 22, ry + (row_h - 8) // 2, 8, 8, dot_map[indicator])
    # Footer
    ft_h = 32
    ft_y = y + h - ft_h
    if recommended:
        add_text(
            slide, f"option-{n}-footer-text",
            "★ RECOMMENDED — BEST VALUE & SPEED",
            x_px=x, y_px=ft_y, w_px=w, h_px=ft_h,
            font_size_px=10, color=WHITE, bold=True, align="center", anchor="middle",
            letter_spacing_px=1.4,
        )
    else:
        add_text(
            slide, f"option-{n}-footer-text", "Not recommended for current cycle",
            x_px=x, y_px=ft_y, w_px=w, h_px=ft_h,
            font_size_px=11, color=TEXT_FAINT, italic=True, align="center", anchor="middle",
        )


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Choose the right path: <strong>two options evaluated</strong>",
        subtitle="A structured side-by-side comparison across cost, speed, risk, and fit",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 50 - body_top  # leave space for decision strip + footer
    gap_center = 56
    card_w = (body_w - gap_center) // 2

    rows_a = [
        ("Cost", "$1.2M – $1.8M initial investment", "warn"),
        ("Timeline", "14 – 18 months to first release", "bad"),
        ("Risk", "High — talent dependency, scope creep", "bad"),
        ("Fit", "Fully tailored to our process & data", "good"),
    ]
    rows_b = [
        ("Cost", "$280K/yr subscription + $120K setup", "good"),
        ("Timeline", "3 – 4 months to production", "good"),
        ("Risk", "Low — proven stack, SLA-backed support", "good"),
        ("Fit", "80% fit; some workflow adaptation needed", "warn"),
    ]

    _option_card(
        slide, 1, body_left, body_top, card_w, body_h,
        header_color=BRAND_PRIMARY, label="Option A", name="Build In-House",
        option_name="Internal Development",
        tagline="Full ownership, custom-built by our team",
        rows=rows_a, recommended=False,
    )
    _option_card(
        slide, 2, body_left + card_w + gap_center, body_top, card_w, body_h,
        header_color=BRAND_PRIMARY_MID, label="Option B", name="SaaS Platform",
        option_name="Off-the-Shelf SaaS",
        tagline="Configure & launch with proven vendor platform",
        rows=rows_b, recommended=True,
    )

    # ── VS circle in the center ──
    vs_size = 40
    vs_x = body_left + card_w + (gap_center - vs_size) // 2
    vs_y = body_top + 60
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, px_to_emu(vs_x), px_to_emu(vs_y),
        px_to_emu(vs_size), px_to_emu(vs_size),
    )
    shape.name = "vs-circle"
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD_BORDER
    shape.line.color.rgb = WHITE
    shape.line.width = 19050
    add_text(
        slide, "vs-text", "VS",
        x_px=vs_x, y_px=vs_y, w_px=vs_size, h_px=vs_size,
        font_size_px=11, color=BRAND_PRIMARY_MID, bold=True,
        align="center", anchor="middle",
    )

    # ── Decision strip ──
    ds_y = body_top + body_h + 8
    ds_h = 32
    ds = add_rect(slide, "decision-strip", body_left, ds_y, body_w, ds_h, CARD_BG)
    ds.line.color.rgb = CARD_BORDER
    ds.line.width = 9525
    add_text(
        slide, "decision-label", "RECOMMENDATION",
        x_px=body_left + 16, y_px=ds_y, w_px=140, h_px=ds_h,
        font_size_px=10, color=BRAND_ACCENT, bold=True, anchor="middle",
        letter_spacing_px=1.4,
    )
    add_rect(slide, "decision-divider", body_left + 162, ds_y + 8, 1, ds_h - 16, CARD_BORDER)
    add_text(
        slide, "decision-text",
        "Proceed with Option B (SaaS): lower risk, 4× faster to market, and frees internal capacity for higher-value differentiation work.",
        x_px=body_left + 176, y_px=ds_y, w_px=body_w - 192, h_px=ds_h,
        font_size_px=11, color=TEXT_MID, italic=True, anchor="middle",
    )

    add_footer(slide, page_num=314)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "314_2bucket-comparison-cards.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
