"""Gallery 3 — Asymmetric 75/25 with dark anchor panel on the LEFT (25%)."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT))
from twins.helpers import (
    new_slide, add_text, add_rect, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE, CARD_BG,
)

prs, slide = new_slide()

LEFT_X, LEFT_Y, LEFT_W, LEFT_H = 0, 0, 360, 720
add_rect(slide, "anchor-bg", x_px=LEFT_X, y_px=LEFT_Y, w_px=LEFT_W, h_px=LEFT_H, fill_color=BRAND_PRIMARY)

add_text(slide, "anchor-eyebrow", "Q3 FY26 OUTLOOK",
    x_px=40, y_px=80, w_px=300, h_px=20,
    font_size_pt=11, color=BRAND_ACCENT, bold=True, uppercase=True)

add_text(slide, "anchor-claim",
    "Margin expansion will concentrate in <strong>three</strong> segments.",
    x_px=40, y_px=120, w_px=300, h_px=240,
    font_size_pt=26, color=WHITE, bold=False,
    emphasis_color=BRAND_ACCENT, anchor="top")

add_text(slide, "anchor-metric-label", "Projected lift",
    x_px=40, y_px=420, w_px=300, h_px=20,
    font_size_pt=11, color=TEXT_FAINT, uppercase=True, bold=True)
add_text(slide, "anchor-metric", "+340 bps",
    x_px=40, y_px=442, w_px=300, h_px=70,
    font_size_pt=38, color=WHITE, bold=True)
add_text(slide, "anchor-metric-sub", "vs. consensus +120 bps",
    x_px=40, y_px=512, w_px=300, h_px=20,
    font_size_pt=12, color=TEXT_FAINT, italic=True)

add_text(slide, "anchor-attr", "Finance & Strategy, internal model v4.2",
    x_px=40, y_px=660, w_px=300, h_px=18,
    font_size_pt=9, color=TEXT_FAINT, italic=True)

RIGHT_X = LEFT_W + 40
RIGHT_W = 1280 - RIGHT_X - 40

add_text(slide, "title", "Three segments drive the lift",
    x_px=RIGHT_X, y_px=70, w_px=RIGHT_W, h_px=42,
    font_size_pt=24, color=TEXT_DARK, bold=True)
add_text(slide, "subtitle",
    "Industrials, Specialty Chemicals, and Aftermarket Services together explain 82% of margin gain",
    x_px=RIGHT_X, y_px=114, w_px=RIGHT_W, h_px=26,
    font_size_pt=13, color=TEXT_MID, italic=True)

CARDS = [
    ("Industrials", "+520 bps", "Price discipline + supplier consolidation; backlog at 14-mo high."),
    ("Specialty Chemicals", "+410 bps", "Capacity exits by two competitors; pricing power returns to formulators."),
    ("Aftermarket Services", "+290 bps", "Attach-rate up 6pp on installed base; service mix shifts to recurring."),
]
y = 170
for i, (name, lift, body) in enumerate(CARDS):
    add_rect(slide, f"card-{i}-bg", x_px=RIGHT_X, y_px=y, w_px=RIGHT_W, h_px=130, fill_color=WHITE)
    add_rect(slide, f"card-{i}-edge", x_px=RIGHT_X, y_px=y, w_px=4, h_px=130, fill_color=BRAND_ACCENT)
    add_text(slide, f"card-{i}-name", name,
        x_px=RIGHT_X + 20, y_px=y + 14, w_px=RIGHT_W - 240, h_px=28,
        font_size_pt=18, color=TEXT_DARK, bold=True)
    add_text(slide, f"card-{i}-lift", lift,
        x_px=RIGHT_X + RIGHT_W - 200, y_px=y + 14, w_px=180, h_px=32,
        font_size_pt=22, color=BRAND_PRIMARY, bold=True, align="right")
    add_text(slide, f"card-{i}-body", body,
        x_px=RIGHT_X + 20, y_px=y + 56, w_px=RIGHT_W - 40, h_px=60,
        font_size_pt=13, color=TEXT_MID)
    add_rect(slide, f"card-{i}-rule", x_px=RIGHT_X + 20, y_px=y + 124, w_px=RIGHT_W - 40, h_px=1, fill_color=CARD_BG)
    y += 140

add_footer(slide, page_num=3, source="Internal Finance model v4.2, June 2026", footnote="Lift estimates use a 12-month forward window vs. trailing-twelve-month baseline")

out_pptx = HERE / "gallery3-asymmetric-75-25.pptx"
prs.save(out_pptx)
print(f"WROTE {out_pptx}")

