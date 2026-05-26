"""Gallery 8 — Narrow dark left rail + main body content."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT))
from twins.helpers import (
    new_slide, add_text, add_rect, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE, CARD_BG, CARD_BORDER,
)

prs, slide = new_slide()

RAIL_W = 72
add_rect(slide, "rail-bg", x_px=0, y_px=0, w_px=RAIL_W, h_px=720, fill_color=BRAND_PRIMARY)

add_text(slide, "rail-section-num", "02",
    x_px=8, y_px=60, w_px=RAIL_W - 16, h_px=44,
    font_size_pt=24, color=BRAND_ACCENT, bold=True, align="center")
add_rect(slide, "rail-rule", x_px=RAIL_W//2 - 12, y_px=112, w_px=24, h_px=2, fill_color=BRAND_ACCENT)

section = "DIAGNOSE"
y = 140
for ch in section:
    add_text(slide, f"rail-letter-{ch}-{y}", ch,
        x_px=8, y_px=y, w_px=RAIL_W - 16, h_px=24,
        font_size_pt=11, color=WHITE, bold=True, align="center", uppercase=True, letter_spacing_px=4)
    y += 22

add_text(slide, "rail-count", "02 / 05",
    x_px=8, y_px=660, w_px=RAIL_W - 16, h_px=18,
    font_size_pt=9, color=TEXT_FAINT, align="center", letter_spacing_px=1)

BODY_X = RAIL_W + 56
BODY_W = 1280 - BODY_X - 64

add_text(slide, "body-eyebrow", "SECTION 02  |  DIAGNOSE",
    x_px=BODY_X, y_px=60, w_px=BODY_W, h_px=22,
    font_size_pt=11, color=BRAND_PRIMARY, bold=True, uppercase=True)

add_text(slide, "body-title",
    "Three root causes explain <strong>80%</strong> of order-to-cash delay.",
    x_px=BODY_X, y_px=88, w_px=BODY_W, h_px=110,
    font_size_pt=30, color=TEXT_DARK, bold=True,
    emphasis_color=BRAND_ACCENT)

add_rect(slide, "body-rule", x_px=BODY_X, y_px=212, w_px=64, h_px=4, fill_color=BRAND_ACCENT)

add_text(slide, "body-para",
    "Time-and-motion across 412 orders identified three structural bottlenecks that compound: credit-hold rework, "
    "split-line picking, and manual freight booking. Together these account for 32 hours of the average 41-hour cycle. "
    "The remaining 9 hours sit in carrier handoff and proof-of-delivery reconciliation — both are tractable but "
    "deliver smaller absolute gains.",
    x_px=BODY_X, y_px=232, w_px=BODY_W - 280, h_px=200,
    font_size_pt=14, color=TEXT_DARK)

# Tiles arranged vertically with metric on top, label+sub stacked below — no two-column conflict
TILE_X = BODY_X + BODY_W - 240
TILE_W = 240
TILE_H = 96
TILES = [
    ("32 hrs", "of 41-hr cycle, explained by three root causes"),
    ("412",    "orders sampled in Mar-Apr 2026"),
    ("80%",    "delay concentration before any intervention"),
]
y = 232
for i, (big, sub) in enumerate(TILES):
    add_rect(slide, f"tile-{i}-bg", x_px=TILE_X, y_px=y, w_px=TILE_W, h_px=TILE_H, fill_color=CARD_BG)
    add_rect(slide, f"tile-{i}-edge", x_px=TILE_X, y_px=y, w_px=3, h_px=TILE_H, fill_color=BRAND_ACCENT)
    add_text(slide, f"tile-{i}-big", big,
        x_px=TILE_X + 16, y_px=y + 10, w_px=TILE_W - 32, h_px=42,
        font_size_pt=26, color=BRAND_PRIMARY, bold=True)
    add_text(slide, f"tile-{i}-sub", sub,
        x_px=TILE_X + 16, y_px=y + 54, w_px=TILE_W - 32, h_px=38,
        font_size_pt=11, color=TEXT_MID, italic=True)
    y += TILE_H + 12

add_rect(slide, "sowhat-bg", x_px=BODY_X, y_px=560, w_px=BODY_W, h_px=70, fill_color=BRAND_PRIMARY)
add_text(slide, "sowhat-label", "SO WHAT",
    x_px=BODY_X + 20, y_px=572, w_px=100, h_px=20,
    font_size_pt=10, color=BRAND_ACCENT, bold=True, uppercase=True)
add_text(slide, "sowhat-text",
    "Fixing credit-hold rework alone returns ~14 hours per order — and is the only one of the three solvable inside 90 days.",
    x_px=BODY_X + 20, y_px=594, w_px=BODY_W - 40, h_px=30,
    font_size_pt=14, color=WHITE, italic=True, anchor="top")

add_footer(slide, page_num=8, source="Order-to-cash time-and-motion study, Mar-Apr 2026; n=412 orders", footnote="Cycle measured as customer-PO-received to invoice-sent timestamps")

out_pptx = HERE / "gallery8-left-rail-body.pptx"
prs.save(out_pptx)
print(f"WROTE {out_pptx}")


