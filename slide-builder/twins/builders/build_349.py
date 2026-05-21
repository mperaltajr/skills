"""
Builder for pattern 349: Dark Project Charter (one-pager).

Source HTML: _pattern-library/349_dark-project-charter.html
Standalone — closest light reference: 158_one-page-strategy.

Layout: title + meta bar (6 fields), then 2×3 card grid:
  [Objectives] [Scope] [Success Criteria]
  [Key Stakeholders] [Key Milestones] [Budget]
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)
ACCENT_GREEN = RGBColor(0x22, 0xC5, 0x5E)
ACCENT_RED = RGBColor(0xEF, 0x44, 0x44)


def add_oval(slide, name, x, y, size, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                 px_to_emu(x), px_to_emu(y),
                                 px_to_emu(size), px_to_emu(size))
    sh.name = name
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title
    add_text(slide, "title",
             "Project Charter — <strong>Digital Supply Chain Transformation</strong>",
             x_px=64, y_px=20, w_px=1152, h_px=80,
             font_size_px=28, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "One-page charter for executive alignment and project initiation approval",
             x_px=64, y_px=108, w_px=1100, h_px=22,
             font_size_px=13, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Meta bar (6 fields in row)
    meta_y = 150
    meta_h = 44
    add_rect(slide, "meta-bg", 64, meta_y, 1152, meta_h, CARD_BG_DARK)
    fields = [
        ("Project Name", "Supply Chain Digital Twin"),
        ("Sponsor", "R.J. (CFO)"),
        ("Project Manager", "M.P. (Delivery Lead)"),
        ("Start Date", "01 Jun 2026"),
        ("End Date", "28 Feb 2027"),
        ("Status", "Initiation"),
    ]
    field_w = 1152 // 6
    for i, (lbl, val) in enumerate(fields):
        fx = 64 + i * field_w
        add_text(slide, f"meta-{i+1}-lbl", lbl,
                 x_px=fx + 12, y_px=meta_y + 6, w_px=field_w - 16, h_px=12,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=False,
                 uppercase=True, letter_spacing_px=1)
        add_text(slide, f"meta-{i+1}-val", val,
                 x_px=fx + 12, y_px=meta_y + 20, w_px=field_w - 16, h_px=18,
                 font_size_px=11, color=WHITE, bold=True)
        if i < 5:
            add_rect(slide, f"meta-{i+1}-div",
                     fx + field_w - 1, meta_y + 8, 1, meta_h - 16, CARD_BORDER_DARK)

    # 2x3 grid
    grid_y = 204
    grid_h = 456
    row_gap = 10
    col_gap = 10
    cell_w = (1152 - 2 * col_gap) // 3
    cell_h = (grid_h - row_gap) // 2

    def card(x, y, w, h, label, label_color=BRAND_ACCENT_SOFT):
        c = add_rect(slide, f"card-{label}-bg", x, y, w, h, CARD_BG_DARK)
        c.line.color.rgb = CARD_BORDER_DARK
        c.line.width = 9525
        add_text(slide, f"card-{label}-title", label.upper(),
                 x_px=x + 14, y_px=y + 10, w_px=w - 28, h_px=14,
                 font_size_px=10, color=label_color, bold=True,
                 uppercase=True, letter_spacing_px=1.5)
        add_rect(slide, f"card-{label}-rule", x + 14, y + 28, 28, 2, BRAND_ACCENT)

    positions = [
        (64, grid_y),
        (64 + cell_w + col_gap, grid_y),
        (64 + 2 * (cell_w + col_gap), grid_y),
        (64, grid_y + cell_h + row_gap),
        (64 + cell_w + col_gap, grid_y + cell_h + row_gap),
        (64 + 2 * (cell_w + col_gap), grid_y + cell_h + row_gap),
    ]

    # Zone 1: Objectives
    x, y = positions[0]
    card(x, y, cell_w, cell_h, "Objectives")
    objs = [
        "Establish a real-time digital twin of end-to-end supply chain operations across 12 distribution centres",
        "Reduce inventory holding costs by 18% through AI-driven demand sensing and replenishment automation",
        "Enable executive-level supply risk visibility with a configurable tier-2 supplier monitoring dashboard",
    ]
    obj_top = y + 40
    obj_h = (cell_h - 52) // 3
    for i, t in enumerate(objs):
        oy = obj_top + i * obj_h
        add_oval(slide, f"obj-{i+1}-num-bg", x + 14, oy + 2, 18, BRAND_ACCENT)
        add_text(slide, f"obj-{i+1}-num", str(i + 1),
                 x_px=x + 14, y_px=oy + 2, w_px=18, h_px=18,
                 font_size_px=10, color=WHITE, bold=True,
                 align="center", anchor="middle")
        add_text(slide, f"obj-{i+1}-text", t,
                 x_px=x + 38, y_px=oy, w_px=cell_w - 52, h_px=obj_h - 4,
                 font_size_px=10, color=TEXT_ON_DARK_MID)

    # Zone 2: Scope
    x, y = positions[1]
    card(x, y, cell_w, cell_h, "Scope")
    scope_in = [
        "SAP ERP integration and real-time data pipeline (12 DCs)",
        "AI demand-sensing model training, validation and deployment",
        "Executive risk dashboard (Power BI) with tier-1 and tier-2 supplier data",
    ]
    scope_out = [
        "Manufacturing execution system (MES) integration",
        "Retail point-of-sale feed and last-mile logistics optimisation",
    ]
    s_top = y + 40
    add_text(slide, "scope-in-lbl", "IN SCOPE",
             x_px=x + 14, y_px=s_top, w_px=cell_w - 28, h_px=12,
             font_size_px=9, color=ACCENT_GREEN, bold=True,
             uppercase=True, letter_spacing_px=1.2)
    for i, t in enumerate(scope_in):
        iy = s_top + 16 + i * 22
        add_rect(slide, f"sc-in-{i+1}-dot", x + 14, iy + 5, 8, 8, ACCENT_GREEN)
        add_text(slide, f"sc-in-{i+1}-text", t,
                 x_px=x + 28, y_px=iy, w_px=cell_w - 42, h_px=20,
                 font_size_px=10, color=TEXT_ON_DARK_MID)
    so_top = s_top + 16 + 3 * 22 + 6
    add_text(slide, "scope-out-lbl", "OUT OF SCOPE",
             x_px=x + 14, y_px=so_top, w_px=cell_w - 28, h_px=12,
             font_size_px=9, color=ACCENT_RED, bold=True,
             uppercase=True, letter_spacing_px=1.2)
    for i, t in enumerate(scope_out):
        iy = so_top + 16 + i * 22
        add_rect(slide, f"sc-out-{i+1}-dot", x + 14, iy + 5, 8, 8, ACCENT_RED)
        add_text(slide, f"sc-out-{i+1}-text", t,
                 x_px=x + 28, y_px=iy, w_px=cell_w - 42, h_px=20,
                 font_size_px=10, color=TEXT_ON_DARK_MID)

    # Zone 3: Success Criteria
    x, y = positions[2]
    card(x, y, cell_w, cell_h, "Success Criteria")
    crit = [
        ("Inventory holding cost reduction", "≥ 18%"),
        ("Order fulfilment accuracy rate", "≥ 99.2%"),
        ("Dashboard adoption (weekly active users)", "≥ 85%"),
        ("System uptime SLA (production environment)", "99.5%"),
    ]
    c_top = y + 40
    c_h = (cell_h - 50) // 4
    for i, (lbl, tgt) in enumerate(crit):
        cy = c_top + i * c_h
        cb = add_rect(slide, f"crit-{i+1}-cb", x + 14, cy + 4, 12, 12, CARD_BG_DARK)
        cb.line.color.rgb = TEXT_ON_DARK_FAINT
        cb.line.width = 12700
        add_text(slide, f"crit-{i+1}-text", lbl,
                 x_px=x + 32, y_px=cy, w_px=cell_w - 110, h_px=c_h - 4,
                 font_size_px=10, color=WHITE, anchor="middle")
        add_text(slide, f"crit-{i+1}-target", tgt,
                 x_px=x + cell_w - 78, y_px=cy, w_px=64, h_px=c_h - 4,
                 font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True,
                 align="right", anchor="middle")

    # Zone 4: Stakeholders
    x, y = positions[3]
    card(x, y, cell_w, cell_h, "Key Stakeholders")
    stakeholders = [
        ("RJ", "Rachel Jensen", "Executive Sponsor · CFO"),
        ("MP", "Mario Peralta", "Project Manager · Delivery Lead"),
        ("SO", "Sandra Okonkwo", "Business Owner · VP Supply Chain"),
        ("TK", "Thomas Krause", "Tech Lead · Enterprise Architecture"),
    ]
    sh_top = y + 40
    sh_h = (cell_h - 50) // 4
    for i, (init, nm, role) in enumerate(stakeholders):
        sy = sh_top + i * sh_h
        add_oval(slide, f"sh-{i+1}-ic", x + 14, sy + 4, 26, BRAND_PRIMARY_MID)
        add_text(slide, f"sh-{i+1}-init", init,
                 x_px=x + 14, y_px=sy + 4, w_px=26, h_px=26,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
                 align="center", anchor="middle")
        add_text(slide, f"sh-{i+1}-name", nm,
                 x_px=x + 48, y_px=sy + 2, w_px=cell_w - 60, h_px=16,
                 font_size_px=11, color=WHITE, bold=True)
        add_text(slide, f"sh-{i+1}-role", role,
                 x_px=x + 48, y_px=sy + 18, w_px=cell_w - 60, h_px=14,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT)

    # Zone 5: Milestones
    x, y = positions[4]
    card(x, y, cell_w, cell_h, "Key Milestones")
    miles = [
        ("01 Jun 26", "Project kick-off and team onboarding complete"),
        ("15 Aug 26", "SAP data pipeline live across all 12 distribution centres"),
        ("30 Oct 26", "AI demand model validated and deployed to staging"),
        ("28 Feb 27", "Full platform go-live and hypercare period ends"),
    ]
    m_top = y + 40
    m_h = (cell_h - 50) // 4
    for i, (date, name) in enumerate(miles):
        my = m_top + i * m_h
        # date pill
        pill = add_rect(slide, f"mile-{i+1}-pill", x + 14, my + 4, 76, 18,
                        BRAND_PRIMARY_MID)
        pill.line.color.rgb = BRAND_ACCENT
        pill.line.width = 6350
        add_text(slide, f"mile-{i+1}-date", date,
                 x_px=x + 14, y_px=my + 4, w_px=76, h_px=18,
                 font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True,
                 align="center", anchor="middle")
        add_text(slide, f"mile-{i+1}-name", name,
                 x_px=x + 100, y_px=my, w_px=cell_w - 114, h_px=m_h - 4,
                 font_size_px=10, color=WHITE, anchor="middle")

    # Zone 6: Budget
    x, y = positions[5]
    card(x, y, cell_w, cell_h, "Budget")
    budget = [
        ("Technology & Licensing", "$620,000"),
        ("Professional Services", "$1,140,000"),
        ("Change Management & Training", "$185,000"),
    ]
    b_top = y + 40
    for i, (lbl, amt) in enumerate(budget):
        by = b_top + i * 30
        add_text(slide, f"bud-{i+1}-lbl", lbl,
                 x_px=x + 14, y_px=by, w_px=cell_w - 130, h_px=22,
                 font_size_px=11, color=TEXT_ON_DARK_MID, anchor="middle")
        add_text(slide, f"bud-{i+1}-amt", amt,
                 x_px=x + cell_w - 130, y_px=by, w_px=116, h_px=22,
                 font_size_px=11, color=WHITE, bold=True,
                 align="right", anchor="middle")
    # Total
    tot_y = b_top + 3 * 30 + 8
    add_rect(slide, "bud-total-rule", x + 14, tot_y - 4, cell_w - 28, 1,
             BRAND_ACCENT_SOFT)
    add_text(slide, "bud-total-lbl", "Total Budget",
             x_px=x + 14, y_px=tot_y, w_px=cell_w - 130, h_px=24,
             font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1, anchor="middle")
    add_text(slide, "bud-total-amt", "$1,945,000",
             x_px=x + cell_w - 130, y_px=tot_y, w_px=116, h_px=24,
             font_size_px=16, color=BRAND_ACCENT_SOFT, bold=True,
             align="right", anchor="middle")

    # Invariant zone
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "349",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = (Path(__file__).resolve().parents[2] / "_renders" / "twins" /
           "349_dark-project-charter.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
