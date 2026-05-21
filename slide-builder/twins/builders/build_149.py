"""
Builder for pattern 149: Brainstorm affinity map — 4 sticky-note clusters in 2x2.

Chrome-normalized to Style A (was top-chrome variant).
Source HTML: _pattern-library/149_brainstorm-affinity-map.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

CLUSTER_COLORS = {
    1: RGBColor(0x29, 0x80, 0xB9),
    2: RGBColor(0x27, 0xAE, 0x60),
    3: RGBColor(0xE6, 0x7E, 0x22),
    4: RGBColor(0x8E, 0x44, 0xAD),
}
STICKY_BG = {
    1: RGBColor(0xD6, 0xEA, 0xF8),
    2: RGBColor(0xD5, 0xF5, 0xE3),
    3: RGBColor(0xFC, 0xF3, 0xCF),
    4: RGBColor(0xE8, 0xDA, 0xEF),
}


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Eyebrow + title
    add_text(slide, "eyebrow", "Ideation Output — Affinity Map",
             x_px=48, y_px=58, w_px=600, h_px=14,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "title",
             "<strong>47 ideas generated, 4 themes emerged</strong> — technology and CX clusters have most cross-functional overlap",
             x_px=48, y_px=78, w_px=1100, h_px=46,
             font_size_px=22, color=TEXT_DARK, bold=True,
             emphasis_color=BRAND_PRIMARY)
    add_rect(slide, "brand-rule", 48, 128, 56, 3, BRAND_ACCENT)

    # 2x2 grid: top:148 left:48 right:48 bottom:60
    gx = 48
    gy = 148
    gw = 1280 - 96
    gh = 720 - 60 - gy
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
        # Cluster bg (white with top accent)
        cl = add_rect(slide, f"cluster-{cn}-bg", cx, cy, cw, ch, WHITE)
        cl.line.color.rgb = CARD_BORDER
        cl.line.width = 9525
        add_rect(slide, f"cluster-{cn}-accent", cx, cy, cw, 4, CLUSTER_COLORS[cn])
        # Heading
        add_text(slide, f"cluster-{cn}-heading", heading,
                 x_px=cx + 14, y_px=cy + 14, w_px=cw - 28, h_px=18,
                 font_size_px=11, color=CLUSTER_COLORS[cn], bold=True, uppercase=True)
        # Stickies (laid out in 3 cols × 3 rows)
        s_x_base = cx + 14
        s_y_base = cy + 40
        s_cols = 3
        s_gap = 6
        # Fit width: available = cw - 28, split into 3 cols
        s_w = (cw - 28 - s_gap * (s_cols - 1)) // s_cols
        # Fit height: available = ch - 40 - 8, split into 3 rows
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
                     font_size_px=9, color=TEXT_DARK, anchor="middle")

    add_footer(slide, page_num=149)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "149_brainstorm-affinity-map.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
