"""
Builder for pattern 290: Evidence row table.

Source HTML: _pattern-library/290_evidence-row-table.html

4 columns: Claim / Evidence (bullet list) / Source pill / Strength bar.
5 rows, left-edge color-strip by strength.
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

PILL_PRIMARY_BG = RGBColor(0xED, 0xE0, 0xFA)
PILL_PRIMARY_FG = RGBColor(0x5C, 0x2D, 0x87)
PILL_SEC_BG = RGBColor(0xE0, 0xF0, 0xFA)
PILL_SEC_FG = RGBColor(0x15, 0x65, 0xA8)
PILL_INT_BG = RGBColor(0xE6, 0xF4, 0xEA)
PILL_INT_FG = RGBColor(0x2E, 0x7D, 0x32)
SEG_WEAK = RGBColor(0xC8, 0xD0, 0xDC)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Evidence supports a <strong>phased activation</strong> approach",
        subtitle="Five claims stress-tested against primary, secondary, and internal sources — rated by evidential strength",
    )

    # Table area
    t_x = 48
    t_y = 234
    t_w = 1280 - 96
    t_h = 720 - t_y - 44

    # Column widths
    c1_w = int(t_w * 0.25)   # claim
    c2_w = int(t_w * 0.40)   # evidence
    c3_w = int(t_w * 0.15)   # source
    c4_w = t_w - c1_w - c2_w - c3_w

    # Header
    head_h = 40
    add_rect(slide, "thead-bg", t_x, t_y, t_w, head_h, BRAND_PRIMARY)
    headers = ["Claim / Assertion", "Evidence", "Source", "Strength"]
    widths = [c1_w, c2_w, c3_w, c4_w]
    hx = t_x
    for i, (h, w) in enumerate(zip(headers, widths)):
        add_text(
            slide, f"thead-{i+1}", h,
            x_px=hx + 14, y_px=t_y, w_px=w - 14, h_px=head_h,
            font_size_px=10, color=WHITE, bold=True, anchor="middle",
            uppercase=True, letter_spacing_px=1.4,
        )
        hx += w

    # Rows
    rows = [
        ("Market share is recoverable within 18 months",
         ["Category grew 22% YoY — headroom confirmed",
          "3 of 5 competitors have longer lead times than client",
          "NPS gap vs. category leader narrowed from −18 to −7"],
         "Primary Research", "primary", "strong"),
        ("Digital channels outperform field sales for SMB segment",
         ["Digital CAC 34% lower per internal benchmark",
          "Conversion rates comparable across comparable verticals"],
         "Internal Data", "internal", "medium"),
        ("Regulatory window closes Q3 2026, requiring early action",
         ["Draft legislation published Feb 2026, comment period ends Jun",
          "Three analogous markets enacted rule within 6 months of draft",
          "Legal counsel confirms no grandfather provisions expected"],
         "Secondary", "secondary", "strong"),
        ("Talent availability constrains speed of transformation",
         ["Role requisitions open 90+ days in 4 of 6 target geographies",
          "Industry attrition 18% vs. 12% historical average"],
         "Secondary", "secondary", "medium"),
        ("Partnership model reduces capex exposure by ~30%",
         ["Single comparable deal (different vertical) cited in analyst note",
          "Client finance has not stress-tested assumption"],
         "Secondary", "secondary", "weak"),
    ]
    pill_styles = {
        "primary":   (PILL_PRIMARY_BG, PILL_PRIMARY_FG),
        "secondary": (PILL_SEC_BG, PILL_SEC_FG),
        "internal":  (PILL_INT_BG, PILL_INT_FG),
    }
    strength_styles = {
        "strong": (BRAND_ACCENT, 3, "Strong"),
        "medium": (BRAND_ACCENT_SOFT, 2, "Medium"),
        "weak":   (SEG_WEAK, 1, "Weak"),
    }
    strength_left_color = {
        "strong": BRAND_ACCENT,
        "medium": BRAND_ACCENT_SOFT,
        "weak":   CARD_BORDER,
    }

    rows_top = t_y + head_h
    row_h = (t_h - head_h) // len(rows)
    for ri, (claim, evidence, source, source_kind, strength) in enumerate(rows):
        ry = rows_top + ri * row_h
        bg = WHITE if ri % 2 == 0 else CARD_BG
        add_rect(slide, f"row-{ri+1}-bg", t_x, ry, t_w, row_h, bg)
        # Left strength border
        add_rect(slide, f"row-{ri+1}-strength-stripe", t_x, ry, 3,
                 row_h, strength_left_color[strength])
        # Bottom border
        add_rect(slide, f"row-{ri+1}-bottom", t_x, ry + row_h - 1, t_w, 1, CARD_BORDER)

        # Claim cell
        add_text(
            slide, f"row-{ri+1}-claim", claim,
            x_px=t_x + 14, y_px=ry + 14, w_px=c1_w - 28, h_px=row_h - 28,
            font_size_px=13, color=TEXT_DARK, bold=True,
        )

        # Evidence — bullet list
        ev_x = t_x + c1_w
        ev_y = ry + 14
        for ei, ev in enumerate(evidence):
            ey = ev_y + ei * 22
            add_text(
                slide, f"row-{ri+1}-evidence-{ei+1}-dot", "•",
                x_px=ev_x + 14, y_px=ey, w_px=10, h_px=18,
                font_size_px=12, color=TEXT_MID,
            )
            add_text(
                slide, f"row-{ri+1}-evidence-{ei+1}", ev,
                x_px=ev_x + 26, y_px=ey, w_px=c2_w - 40, h_px=20,
                font_size_px=11, color=TEXT_MID,
            )

        # Source pill
        sp_x = t_x + c1_w + c2_w
        pill_bg, pill_fg = pill_styles[source_kind]
        # Center pill in cell
        from pptx.enum.shapes import MSO_SHAPE
        pill_w = 130
        pill_h = 22
        px = sp_x + (c3_w - pill_w) // 2
        py = ry + (row_h - pill_h) // 2
        pill = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            px * 9525, py * 9525, pill_w * 9525, pill_h * 9525,
        )
        pill.name = f"row-{ri+1}-source-pill-bg"
        pill.adjustments[0] = 0.5  # full round
        pill.fill.solid()
        pill.fill.fore_color.rgb = pill_bg
        pill.line.fill.background()
        add_text(
            slide, f"row-{ri+1}-source-pill", source,
            x_px=px, y_px=py, w_px=pill_w, h_px=pill_h,
            font_size_px=10, color=pill_fg, bold=True,
            align="center", anchor="middle",
        )

        # Strength bar
        st_x = t_x + c1_w + c2_w + c3_w
        seg_color, filled, label = strength_styles[strength]
        seg_w = 30
        seg_gap = 4
        seg_y = ry + (row_h - 10) // 2
        sx = st_x + 14
        for si in range(3):
            color = seg_color if si < filled else CARD_BORDER
            add_rect(slide, f"row-{ri+1}-seg-{si+1}",
                     sx + si * (seg_w + seg_gap), seg_y, seg_w, 10, color)
        # Label
        add_text(
            slide, f"row-{ri+1}-strength-label", label,
            x_px=sx + 3 * (seg_w + seg_gap) + 4, y_px=ry, w_px=80, h_px=row_h,
            font_size_px=10, color=TEXT_FAINT, anchor="middle",
        )

    add_footer(slide, page_num=290)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "290_evidence-row-table.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
