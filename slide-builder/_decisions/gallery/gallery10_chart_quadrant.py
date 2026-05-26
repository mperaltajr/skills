"""Gallery 10 — BCG-style 2x2 quadrant chart with labeled dots."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT))
from twins.helpers import (
    new_slide, add_text, add_rect, add_circle, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE, CARD_BG, CARD_BORDER,
)

prs, slide = new_slide()

add_title_block(
    slide,
    title="<strong>Three</strong> of the six product lines are starving cash from the rest of the portfolio",
    subtitle="Growth-share matrix, FY26 H1 — bubble size scales with revenue",
)

CHART_X, CHART_Y = 170, 184
CHART_W, CHART_H = 760, 440

add_rect(slide, "y-axis", x_px=CHART_X, y_px=CHART_Y, w_px=2, h_px=CHART_H, fill_color=BRAND_PRIMARY)
add_rect(slide, "x-axis", x_px=CHART_X, y_px=CHART_Y + CHART_H, w_px=CHART_W, h_px=2, fill_color=BRAND_PRIMARY)

mid_x = CHART_X + CHART_W // 2
mid_y = CHART_Y + CHART_H // 2
add_rect(slide, "v-mid", x_px=mid_x, y_px=CHART_Y, w_px=1, h_px=CHART_H, fill_color=BRAND_ACCENT_SOFT)
add_rect(slide, "h-mid", x_px=CHART_X, y_px=mid_y, w_px=CHART_W, h_px=1, fill_color=BRAND_ACCENT_SOFT)

QUADS = [
    ("CASH COWS",       CHART_X + 16,                CHART_Y + 14,            "left"),
    ("STARS",           CHART_X + CHART_W - 200,     CHART_Y + 14,            "right"),
    ("DOGS",            CHART_X + 16,                CHART_Y + CHART_H - 36,  "left"),
    ("QUESTION MARKS",  CHART_X + CHART_W - 200,     CHART_Y + CHART_H - 36,  "right"),
]
for name, x, y, align in QUADS:
    add_text(slide, f"quad-{name}", name,
        x_px=x, y_px=y, w_px=184, h_px=22,
        font_size_pt=12, color=BRAND_PRIMARY, bold=True, uppercase=True,
        align=align, letter_spacing_px=2)

add_text(slide, "y-label", "Relative market share",
    x_px=CHART_X - 180, y_px=CHART_Y + CHART_H // 2 - 14, w_px=170, h_px=22,
    font_size_pt=12, color=TEXT_DARK, bold=True, align="right")
add_text(slide, "y-low", "Low",
    x_px=CHART_X - 50, y_px=CHART_Y + CHART_H - 22, w_px=40, h_px=20,
    font_size_pt=10, color=TEXT_FAINT, align="right", italic=True)
add_text(slide, "y-high", "High",
    x_px=CHART_X - 50, y_px=CHART_Y, w_px=40, h_px=20,
    font_size_pt=10, color=TEXT_FAINT, align="right", italic=True)
add_text(slide, "x-label", "Market growth",
    x_px=CHART_X, y_px=CHART_Y + CHART_H + 36, w_px=CHART_W, h_px=22,
    font_size_pt=12, color=TEXT_DARK, bold=True, align="center")
add_text(slide, "x-low", "Low",
    x_px=CHART_X - 8, y_px=CHART_Y + CHART_H + 8, w_px=50, h_px=18,
    font_size_pt=10, color=TEXT_FAINT, italic=True)
add_text(slide, "x-high", "High",
    x_px=CHART_X + CHART_W - 42, y_px=CHART_Y + CHART_H + 8, w_px=50, h_px=18,
    font_size_pt=10, color=TEXT_FAINT, italic=True, align="right")

POINTS = [
    ("Aurora",      0.78, 0.82, 480, BRAND_ACCENT),
    ("Pinnacle",    0.62, 0.72, 360, BRAND_PRIMARY),
    ("Bedrock",     0.22, 0.78, 620, BRAND_PRIMARY),
    ("Harbor",      0.18, 0.62, 410, BRAND_PRIMARY_MID),
    ("Spark",       0.82, 0.28, 180, BRAND_ACCENT_SOFT),
    ("Drift",       0.30, 0.18,  90, TEXT_FAINT),
]

def to_canvas(xf, yf):
    cx = CHART_X + int(xf * CHART_W)
    cy = CHART_Y + int((1 - yf) * CHART_H)
    return cx, cy

for i, (name, xf, yf, rev, col) in enumerate(POINTS):
    cx, cy = to_canvas(xf, yf)
    d = max(28, min(72, int(rev / 12)))
    add_circle(slide, f"dot-{i}", x_px=cx - d//2, y_px=cy - d//2, diameter_px=d, fill_color=col)
    add_text(slide, f"dot-{i}-label", name,
        x_px=cx + d//2 + 6, y_px=cy - 12, w_px=130, h_px=22,
        font_size_pt=12, color=TEXT_DARK, bold=True)
    add_text(slide, f"dot-{i}-rev", f"${rev}M",
        x_px=cx + d//2 + 6, y_px=cy + 8, w_px=130, h_px=18,
        font_size_pt=10, color=TEXT_MID, italic=True)

LEG_X = CHART_X + CHART_W + 40
add_text(slide, "legend-head", "Recommended moves",
    x_px=LEG_X, y_px=CHART_Y, w_px=240, h_px=26,
    font_size_pt=14, color=TEXT_DARK, bold=True)
MOVES = [
    ("Bedrock + Harbor", "Harvest. Cap reinvestment at maintenance.", BRAND_PRIMARY),
    ("Aurora + Pinnacle", "Double down. Pull capital forward by 2 quarters.", BRAND_ACCENT),
    ("Spark", "Decide in 90 days: invest or divest.", BRAND_ACCENT_SOFT),
    ("Drift", "Divest. Run sale process by Q4.", TEXT_FAINT),
]
y = CHART_Y + 38
for i, (name, body, col) in enumerate(MOVES):
    add_rect(slide, f"leg-{i}-dot", x_px=LEG_X, y_px=y + 6, w_px=10, h_px=10, fill_color=col)
    add_text(slide, f"leg-{i}-name", name,
        x_px=LEG_X + 20, y_px=y, w_px=220, h_px=22,
        font_size_pt=12, color=TEXT_DARK, bold=True)
    add_text(slide, f"leg-{i}-body", body,
        x_px=LEG_X + 20, y_px=y + 22, w_px=220, h_px=44,
        font_size_pt=11, color=TEXT_MID)
    y += 78

add_footer(slide, page_num=10, source="Strategy team analysis using FY26 H1 segment financials; market growth from IDC Q2 2026", footnote="Bubble area scales with last-twelve-months revenue ($M)")

out_pptx = HERE / "gallery10-chart-quadrant.pptx"
prs.save(out_pptx)
print(f"WROTE {out_pptx}")


