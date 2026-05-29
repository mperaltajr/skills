"""Slide 2 — DARK variant — funnel with orange + white bars on purple ground.

Clean dark slide:
- Bars use either ORANGE (FF6600) or WHITE (FFFFFF) — both safely far from purple.
- Text inside the white bars uses purple — this would naively look like a
  collision, but the detector excludes text inside filled shapes (the text
  sits on the white bar, not on the dark bg).
- Outside-bar text is white.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parents[4]
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SCRIPTS))

from twins.helpers import (
    new_slide, add_title_block, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT,
)
from pptx.dml.color import RGBColor

# OTC palette literals (will be remapped by color_map to FedEx hexes,
# but for collision detection these are the actual XML hexes that come
# out of helpers.py).
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FEDEX_PURPLE = RGBColor(0x4D, 0x14, 0x8C)  # what the bg will be
FEDEX_ORANGE = RGBColor(0xFF, 0x66, 0x00)

prs, slide = new_slide()
# Title shape — finalize's dark path strips placeholders + draws a fresh
# white title at x=40/y=40. Add a title anyway so finalize can read it
# from the source slide.
add_title_block(slide, "Where the cash gets stuck - the funnel")

stages = [
    ("Invoiced this quarter", "$248M", 1000),
    ("Collected on time",     "$181M", 730),
    ("Aged 30+ days",         "$44M",  450),
    ("Disputed / unresolved", "$23M",  250),
]
bar_top = 160
bar_h = 56
bar_gap = 18
for i, (label, value, w_px) in enumerate(stages):
    y = bar_top + i * (bar_h + bar_gap)
    if i < 2:
        bar_color = BRAND_ACCENT   # orange (a100ff per helpers — remapped to FF6600)
        label_color = WHITE
    else:
        bar_color = WHITE
        label_color = BRAND_PRIMARY  # purple (460073 per helpers — remapped to 4D148C)
    add_rect(slide, "bar-%d" % i, 80, y, w_px, bar_h, bar_color)
    add_text(slide, "label-%d" % i, label, 96, y + 14, w_px - 32, bar_h - 8,
             font_size_pt=15, bold=True, color=label_color)
    add_text(slide, "value-%d" % i, value, 80 + w_px + 14, y + 14, 200, bar_h - 8,
             font_size_pt=18, bold=True, color=WHITE)

add_text(slide, "summary",
         "Bottom of funnel = 27% of invoiced revenue not converted to cash within 30 days.",
         80, 480, 1120, 80, font_size_pt=13, color=WHITE)

out = HERE / "option_A.pptx"
prs.save(str(out))
