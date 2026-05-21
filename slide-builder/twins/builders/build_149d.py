"""
Builder for pattern 149d: Brainstorm affinity map — 4 sticky clusters in 2x2 — dark.

Source HTML: _pattern-library/149_brainstorm-affinity-map-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

CLUSTER_COLORS = {
    1: RGBColor(0x60, 0xA5, 0xFA),
    2: RGBColor(0x86, 0xEF, 0xAC),
    3: RGBColor(0xFC, 0xD3, 0x4D),
    4: RGBColor(0xC7, 0x80, 0xFF),
}
STICKY_BG = {
    1: RGBColor(0x1E, 0x3A, 0x5C),
    2: RGBColor(0x14, 0x4E, 0x2A),
    3: RGBColor(0x57, 0x40, 0x12),
    4: RGBColor(0x4A, 0x29, 0x76),
}


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Canonical chrome
    add_text(slide, "title",
             "<strong>47 ideas generated, 4 themes emerged</strong> — technology and CX clusters have most cross-functional overlap",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Ideation output · Affinity Map · Cross-functional ideation session",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # 2x2 grid
    gx = 48
    gy = 220
    gw = 1280 - 96
    gh = 664 - gy
    gap = 12
    cw = (gw - gap) // 2
    ch = (gh - gap) // 2

    clusters = [
        (1, "Customer Experience", ["Faster checkout", "Loyalty rewards upgrade",
                                     "Personalized home page", "Return process simplified",
                                     "Chat-first support", "Self-serve account portal",
                                     "Proactive notifications", "Rating & review system",
                                     "Omnichannel returns"]),
        (2, "Operational Efficiency", ["Automate invoice reconciliation", "Reduce approval chains",
                                        "Real-time inventory sync", "Vendor portal",
                                        "Batch → streaming ETL", "RPA for back-office",
                                        "Eliminate manual handoffs", "Shared service center",
                                        "Lean process mapping"]),
        (3, "People & Culture", ["Remote work toolkit", "Peer recognition program",
                                  "Skills passport", "Manager coaching",
                                  "Mentorship circles", "Internal mobility hub",
                                  "Onboarding redesign", "Inclusion index",
                                  "Learning pathways"]),
        (4, "Technology & Data", ["Single data platform", "API governance",
                                   "AI/ML literacy training", "Cloud migration complete",
                                   "Zero-trust security", "Observability stack",
                                   "Data quality dashboards", "Self-serve analytics",
                                   "Event-driven architecture"]),
    ]

    for idx, (cn, heading, stickies) in enumerate(clusters):
        col = idx % 2
        row = idx // 2
        cx = gx + col * (cw + gap)
        cy = gy + row * (ch + gap)
        cl = add_rect(slide, f"cluster-{cn}-bg", cx, cy, cw, ch, CARD_BG_DARK)
        cl.line.color.rgb = CARD_BORDER_DARK
        cl.line.width = 9525
        add_rect(slide, f"cluster-{cn}-accent", cx, cy, cw, 4, CLUSTER_COLORS[cn])
        add_text(slide, f"cluster-{cn}-heading", heading,
                 x_px=cx + 14, y_px=cy + 14, w_px=cw - 28, h_px=18,
                 font_size_px=11, color=CLUSTER_COLORS[cn], bold=True, uppercase=True)
        s_x_base = cx + 14
        s_y_base = cy + 40
        s_cols = 3
        s_gap = 6
        s_w = (cw - 28 - s_gap * (s_cols - 1)) // s_cols
        s_rows = 3
        s_h = (ch - 48 - s_gap * (s_rows - 1)) // s_rows
        for si, sticky in enumerate(stickies):
            srow = si // s_cols
            scol = si % s_cols
            sx = s_x_base + scol * (s_w + s_gap)
            sy = s_y_base + srow * (s_h + s_gap)
            add_rect(slide, f"cluster-{cn}-sticky-{si+1}-bg",
                     sx, sy, s_w, s_h, STICKY_BG[cn])
            add_text(slide, f"cluster-{cn}-sticky-{si+1}", sticky,
                     x_px=sx + 4, y_px=sy + 4, w_px=s_w - 8, h_px=s_h - 8,
                     font_size_px=9, color=WHITE, anchor="middle")

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "149",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "149d_brainstorm-affinity-map.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
