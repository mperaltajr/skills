"""Gallery 7 — Dense 2x4 KPI grid (8 tiles)."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT))
from twins.helpers import (
    new_slide, add_text, add_rect, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE, CARD_BG, CARD_BORDER,
)
from pptx.dml.color import RGBColor

POSITIVE = RGBColor(0x0F, 0x9D, 0x58)
NEGATIVE = RGBColor(0xD4, 0x3F, 0x3A)

prs, slide = new_slide()

add_title_block(
    slide,
    title="Q2 FY26 scorecard — <strong>five of eight</strong> KPIs at or above plan",
    subtitle="Three watch-items: pipeline coverage, NPS, and inventory turns",
)

KPIS = [
    ("Revenue",         "$1.42B",  "+9.4%",  "vs plan +6.0%",  True),
    ("Operating margin","18.2%",   "+180 bps","vs plan +120 bps", True),
    ("Free cash flow",  "$312M",   "+22%",   "vs plan +15%",   True),
    ("Bookings",        "$1.61B",  "+11.0%", "vs plan +8.0%",  True),
    ("Pipeline coverage","2.6x",   "-0.4x",  "vs plan 3.0x",   False),
    ("NPS",             "+41",     "-3",     "vs plan +47",    False),
    ("Inventory turns", "6.8",     "-0.2",   "vs plan 7.2",    False),
    ("Employee engagement","78%",  "+2 pp",  "vs plan 76%",    True),
]

GRID_TOP = 178
COLS = 4
ROWS = 2
GUTTER = 14
TILE_W = (1280 - 128 - (COLS - 1) * GUTTER) // COLS
TILE_H = 200

for idx, (label, value, delta, vs_plan, is_pos) in enumerate(KPIS):
    r = idx // COLS
    c = idx % COLS
    x = 64 + c * (TILE_W + GUTTER)
    y = GRID_TOP + r * (TILE_H + GUTTER)
    add_rect(slide, f"tile-{idx}-bg", x_px=x, y_px=y, w_px=TILE_W, h_px=TILE_H, fill_color=WHITE)
    add_rect(slide, f"tile-{idx}-top", x_px=x, y_px=y, w_px=TILE_W, h_px=3, fill_color=BRAND_PRIMARY)
    add_rect(slide, f"tile-{idx}-tint", x_px=x, y_px=y+3, w_px=TILE_W, h_px=TILE_H - 3, fill_color=CARD_BG)
    add_text(slide, f"tile-{idx}-label", label,
        x_px=x + 16, y_px=y + 16, w_px=TILE_W - 32, h_px=22,
        font_size_pt=12, color=TEXT_MID, bold=True, uppercase=True)
    add_text(slide, f"tile-{idx}-value", value,
        x_px=x + 16, y_px=y + 44, w_px=TILE_W - 32, h_px=58,
        font_size_pt=30, color=TEXT_DARK, bold=True)
    arrow = "UP" if is_pos else "DN"
    color = POSITIVE if is_pos else NEGATIVE
    add_text(slide, f"tile-{idx}-delta", f"{arrow}  {delta}",
        x_px=x + 16, y_px=y + 110, w_px=TILE_W - 32, h_px=28,
        font_size_pt=14, color=color, bold=True)
    add_text(slide, f"tile-{idx}-plan", vs_plan,
        x_px=x + 16, y_px=y + 140, w_px=TILE_W - 32, h_px=20,
        font_size_pt=11, color=TEXT_MID, italic=True)
    add_rect(slide, f"tile-{idx}-base", x_px=x + 16, y_px=y + 170, w_px=TILE_W - 32, h_px=1, fill_color=CARD_BORDER)
    status = "On / above plan" if is_pos else "Watch"
    add_text(slide, f"tile-{idx}-status", status,
        x_px=x + 16, y_px=y + 174, w_px=TILE_W - 32, h_px=18,
        font_size_pt=10, color=(POSITIVE if is_pos else NEGATIVE), bold=True, uppercase=True)

add_footer(slide, page_num=7, source="Internal management reporting, Q2 FY26 close (pre-audit)", footnote="Plan = FY26 operating plan approved Nov 2025; pp = percentage points")

out_pptx = HERE / "gallery7-dense-grid.pptx"
prs.save(out_pptx)
print(f"WROTE {out_pptx}")
