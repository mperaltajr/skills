"""
Builder for pattern 150d: Retrospective sailboat — 2x2 zones (Sail/Island/Anchor/Rocks) — dark.

Source HTML: _pattern-library/150_retrospective-sailboat-dark.html
Authored from scratch (light counterpart was rejected and removed); structurally
inspired by build_89 (lessons-learned retro) layout patterns.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

# Zone palette (dark-friendly)
SAIL_HEAD = BRAND_ACCENT
SAIL_DOT = BRAND_ACCENT
ISLAND_HEAD = RGBColor(0x16, 0xA3, 0x4A)
ISLAND_DOT = RGBColor(0x86, 0xEF, 0xAC)
ANCHOR_HEAD = BRAND_PRIMARY_MID
ANCHOR_DOT = BRAND_ACCENT_SOFT
ROCKS_HEAD = RGBColor(0xDC, 0x26, 0x26)
ROCKS_DOT = RGBColor(0xF8, 0x71, 0x71)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Canonical chrome
    add_text(slide, "title",
             "<strong>Velocity is strong but three risks need mitigation</strong> — anchor items from sprint 4 must be resolved before Phase 2 launch",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=22, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Sprint retrospective · Sailboat framework · what propelled, what slows, what blocks",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Grid layout
    gx = 48
    gy = 220
    gw = 1280 - 96
    gh = 580 - gy  # leave room for convergence
    gap = 12
    cw = (gw - gap) // 2
    ch = (gh - gap) // 2

    zones = [
        ("tl", "Sail & Wind — what propelled us", SAIL_HEAD, SAIL_DOT, "💨", [
            "Strong stakeholder alignment kept priorities stable across all sprints",
            "Pre-built accelerators saved 3 weeks of custom development effort",
            "Team velocity improved 40% from sprint 1 to sprint 4",
        ]),
        ("tr", "Island — goals & vision", ISLAND_HEAD, ISLAND_DOT, "🏝", [
            "Deliver Phase 2 on time by end of Q3",
            "100% user adoption across all business units",
            "Reduce defect rate to <2% in production",
        ]),
        ("bl", "Anchor — what slowed us", ANCHOR_HEAD, ANCHOR_DOT, "⚓", [
            "Legacy system dependencies blocked three sprint deliverables",
            "Unclear requirements in sprint 4 caused two rework cycles",
            "3 team members on leave reduced capacity by 25% in weeks 6-8",
        ]),
        ("br", "Rocks — risks ahead", ROCKS_HEAD, ROCKS_DOT, "⚠", [
            "Integration testing window is tight — only 4 days before Phase 2 freeze",
            "Budget variance likely if scope creeps beyond current sprint plan",
            "Key stakeholder availability drops in July — decisions may stall",
        ]),
    ]
    positions = {"tl": (0, 0), "tr": (1, 0), "bl": (0, 1), "br": (1, 1)}

    head_h = 30
    for pos, name, head_color, dot_color, icon, bullets in zones:
        col, row = positions[pos]
        cx = gx + col * (cw + gap)
        cy = gy + row * (ch + gap)
        zone = add_rect(slide, f"quadrant-{pos}-bg", cx, cy, cw, ch, CARD_BG_DARK)
        zone.line.color.rgb = CARD_BORDER_DARK
        zone.line.width = 9525
        # Header band
        add_rect(slide, f"quadrant-{pos}-head", cx, cy, cw, head_h, head_color)
        add_text(slide, f"quadrant-{pos}-icon", icon,
                 x_px=cx + 10, y_px=cy + 4, w_px=24, h_px=22,
                 font_size_px=14, color=WHITE, anchor="middle")
        add_text(slide, f"quadrant-{pos}-name", name,
                 x_px=cx + 38, y_px=cy + 6, w_px=cw - 48, h_px=18,
                 font_size_px=11, color=WHITE, bold=True, uppercase=True)
        # Body bullets
        body_y = cy + head_h + 10
        bullet_h = (ch - head_h - 20) // len(bullets)
        for j, txt in enumerate(bullets):
            by = body_y + j * bullet_h
            add_rect(slide, f"quadrant-{pos}-dot-{j+1}", cx + 14, by + 8, 5, 5, dot_color)
            add_text(slide, f"quadrant-{pos}-body-{j+1}", txt,
                     x_px=cx + 28, y_px=by, w_px=cw - 42, h_px=bullet_h - 4,
                     font_size_px=11, color=WHITE)

    # Convergence bar
    conv_y = gy + gh + 8
    conv_h = 60
    add_rect(slide, "convergence-bg", 48, conv_y, 1280 - 96, conv_h, BRAND_PRIMARY_MID)
    add_text(slide, "convergence-mark", "SO WHAT",
             x_px=64, y_px=conv_y + 8, w_px=72, h_px=16,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True,
             bg_fill=BRAND_PRIMARY, padding_px=(2, 6, 2, 6))
    add_text(slide, "convergence",
             "Velocity is strong and the island is in sight — but three anchor items from sprint 4 and a tight integration window must be resolved before Phase 2 launch or the rocks will stop us.",
             x_px=152, y_px=conv_y, w_px=1280 - 200, h_px=conv_h,
             font_size_px=12, color=WHITE, anchor="middle")

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "150",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "150d_retrospective-sailboat.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
