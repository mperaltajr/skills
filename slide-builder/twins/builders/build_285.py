"""
Builder for pattern 285: Initiative roadmap with owners (Gantt by quarter).

Source HTML: _pattern-library/285_initiative-roadmap-owners.html

5 initiatives × 4 quarters × 3 months = 12 month columns.
CRITICAL: Status legend MUST sit BELOW subheadline (top-y ≥ 230,
right-aligned to x ≈ 1240). Table shifted down to clear it.
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
from pptx.enum.shapes import MSO_SHAPE

COMPLETE = RGBColor(0x10, 0xB9, 0x81)
ON_TRACK = BRAND_ACCENT
AT_RISK = RGBColor(0xF5, 0x9E, 0x0B)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="2026 Programme Roadmap — <strong>Initiatives & Owners</strong>",
        subtitle="Delivery schedule by quarter with accountable lead and milestone status",
    )

    # === LEGEND below subheadline (top-y = 234, right-edge = 1240) ===
    leg_w = 380
    leg_h = 30
    leg_y = 234
    leg_x = 1240 - leg_w
    leg = add_rect(slide, "legend-bg", leg_x, leg_y, leg_w, leg_h, CARD_BG)
    leg.line.color.rgb = CARD_BORDER
    leg.line.width = 9525
    add_text(
        slide, "legend-label", "STATUS",
        x_px=leg_x + 10, y_px=leg_y, w_px=56, h_px=leg_h,
        font_size_px=9, color=TEXT_FAINT, bold=True, anchor="middle",
        uppercase=True, letter_spacing_px=1.2,
    )
    statuses = [
        ("Complete", COMPLETE),
        ("On Track", ON_TRACK),
        ("At Risk", AT_RISK),
    ]
    item_x = leg_x + 72
    for i, (label, color) in enumerate(statuses):
        sx = item_x + i * 110
        add_rect(slide, f"legend-{i+1}-swatch", sx, leg_y + 11, 12, 8, color)
        add_text(
            slide, f"legend-{i+1}-label", label,
            x_px=sx + 16, y_px=leg_y, w_px=92, h_px=leg_h,
            font_size_px=10, color=TEXT_MID, anchor="middle",
        )

    # === TABLE (pushed down to clear legend, legend bottom = 264) ===
    # Bottom-anchored at y=664 to keep an 8px gap above the invariant footnote (y=672).
    t_x = 56
    t_y = 280
    t_w = 1280 - 112
    t_h = 664 - t_y  # 384

    init_col_w = 200
    owner_col_w = 90
    months_w = t_w - init_col_w - owner_col_w
    q_w = months_w // 4
    m_w = q_w // 3

    # Quarter header row
    qh_h = 26
    add_rect(slide, "qhead-init-bg", t_x, t_y, init_col_w, qh_h, BRAND_PRIMARY)
    add_text(
        slide, "qhead-init", "INITIATIVE",
        x_px=t_x + 10, y_px=t_y, w_px=init_col_w - 20, h_px=qh_h,
        font_size_px=10, color=WHITE, bold=True, anchor="middle",
        uppercase=True, letter_spacing_px=1,
    )
    add_rect(slide, "qhead-owner-bg", t_x + init_col_w, t_y, owner_col_w, qh_h, BRAND_PRIMARY)
    add_text(
        slide, "qhead-owner", "OWNER",
        x_px=t_x + init_col_w, y_px=t_y, w_px=owner_col_w, h_px=qh_h,
        font_size_px=10, color=WHITE, bold=True, align="center", anchor="middle",
        uppercase=True, letter_spacing_px=1,
    )
    quarters = ["Q1 · Jan – Mar", "Q2 · Apr – Jun", "Q3 · Jul – Sep", "Q4 · Oct – Dec"]
    for qi, qlabel in enumerate(quarters):
        qx = t_x + init_col_w + owner_col_w + qi * q_w
        add_rect(slide, f"qhead-q{qi+1}-bg", qx, t_y, q_w, qh_h, BRAND_PRIMARY)
        add_text(
            slide, f"qhead-q{qi+1}", qlabel,
            x_px=qx, y_px=t_y, w_px=q_w, h_px=qh_h,
            font_size_px=10, color=WHITE, bold=True, align="center", anchor="middle",
            uppercase=True, letter_spacing_px=0.8,
        )

    # Month sub-header
    mh_y = t_y + qh_h
    mh_h = 22
    add_rect(slide, "mhead-init-bg", t_x, mh_y, init_col_w, mh_h, CARD_BG)
    add_text(
        slide, "mhead-init", "Initiative",
        x_px=t_x + 10, y_px=mh_y, w_px=init_col_w - 20, h_px=mh_h,
        font_size_px=10, color=TEXT_DARK, bold=True, anchor="middle",
    )
    add_rect(slide, "mhead-owner-bg", t_x + init_col_w, mh_y, owner_col_w, mh_h, CARD_BG)
    add_text(
        slide, "mhead-owner", "Owner",
        x_px=t_x + init_col_w, y_px=mh_y, w_px=owner_col_w, h_px=mh_h,
        font_size_px=10, color=TEXT_DARK, bold=True, align="center", anchor="middle",
    )
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for mi, m in enumerate(months):
        mx = t_x + init_col_w + owner_col_w + mi * m_w
        add_rect(slide, f"mhead-{mi+1}-bg", mx, mh_y, m_w, mh_h, CARD_BG)
        add_text(
            slide, f"mhead-{mi+1}", m,
            x_px=mx, y_px=mh_y, w_px=m_w, h_px=mh_h,
            font_size_px=9, color=TEXT_MID, anchor="middle", align="center",
        )

    # Body rows
    rows_top = mh_y + mh_h
    rows_h = t_h - qh_h - mh_h
    initiatives = [
        # (name, sub, initials, owner_name, bars[(start_month_idx, span, color)])
        ("Data Platform Migration", "Cloud data lake & ETL re-platform", "SR", "S. Rivera",
         [(0, 3, COMPLETE), (3, 2, AT_RISK)]),
        ("CX Portal Rebuild", "Customer-facing self-service overhaul", "LP", "L. Park",
         [(3, 3, ON_TRACK), (6, 2, ON_TRACK)]),
        ("ERP Consolidation", "Finance & HR system unification", "MK", "M. Kim",
         [(0, 6, COMPLETE), (6, 1, ON_TRACK)]),
        ("AI Ops Tooling", "MLOps pipeline & monitoring layer", "JT", "J. Torres",
         [(7, 2, AT_RISK), (9, 2, AT_RISK)]),
        ("Security & Compliance", "ISO 27001 gap remediation & audit", "AN", "A. Nwosu",
         [(1, 2, ON_TRACK), (6, 3, ON_TRACK), (9, 2, ON_TRACK)]),
    ]
    row_h = rows_h // len(initiatives)
    for ri, (name, sub, initials, owner, bars) in enumerate(initiatives):
        ry = rows_top + ri * row_h
        bg = RGBColor(0xFD, 0xFB, 0xFF) if ri % 2 == 0 else WHITE
        add_rect(slide, f"row-{ri+1}-bg", t_x, ry, t_w, row_h, bg)

        # Initiative name
        add_text(
            slide, f"row-{ri+1}-name", name,
            x_px=t_x + 10, y_px=ry + 10, w_px=init_col_w - 20, h_px=20,
            font_size_px=12, color=TEXT_DARK, bold=True,
        )
        add_text(
            slide, f"row-{ri+1}-sub", sub,
            x_px=t_x + 10, y_px=ry + 30, w_px=init_col_w - 20, h_px=18,
            font_size_px=9, color=TEXT_MID,
        )
        # right border
        add_rect(slide, f"row-{ri+1}-init-rule", t_x + init_col_w - 1, ry, 1, row_h, CARD_BORDER)

        # Owner — avatar + name
        ox = t_x + init_col_w
        avatar_size = 28
        ax = ox + (owner_col_w - avatar_size) // 2
        ay = ry + 8
        avatar = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            ax * 9525, ay * 9525, avatar_size * 9525, avatar_size * 9525,
        )
        avatar.name = f"row-{ri+1}-avatar"
        avatar.fill.solid()
        avatar.fill.fore_color.rgb = BRAND_PRIMARY_MID
        avatar.line.fill.background()
        add_text(
            slide, f"row-{ri+1}-avatar-text", initials,
            x_px=ax, y_px=ay, w_px=avatar_size, h_px=avatar_size,
            font_size_px=10, color=WHITE, bold=True, align="center", anchor="middle",
        )
        add_text(
            slide, f"row-{ri+1}-owner-name", owner,
            x_px=ox, y_px=ay + avatar_size + 2, w_px=owner_col_w, h_px=14,
            font_size_px=9, color=TEXT_MID, align="center",
        )
        # right border
        add_rect(slide, f"row-{ri+1}-owner-rule",
                 t_x + init_col_w + owner_col_w - 1, ry, 1, row_h, CARD_BORDER)

        # Bars
        bar_h = 18
        by = ry + (row_h - bar_h) // 2
        for bi, (start, span, color) in enumerate(bars):
            bx = t_x + init_col_w + owner_col_w + start * m_w + 3
            bw = span * m_w - 6
            add_rect(slide, f"row-{ri+1}-bar-{bi+1}", bx, by, bw, bar_h, color)

        # Bottom border
        add_rect(slide, f"row-{ri+1}-bottom", t_x, ry + row_h - 1, t_w, 1, CARD_BORDER)

    add_footer(slide, page_num=285)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "285_initiative-roadmap-owners.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
