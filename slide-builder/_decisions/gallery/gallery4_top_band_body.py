"""Gallery 4 — Top band with headline + body with 3 cards."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT))
from twins.helpers import (
    new_slide, add_text, add_rect, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE, CARD_BG, CARD_BORDER,
)

prs, slide = new_slide()

BAND_H = 170
add_rect(slide, "band-bg", x_px=0, y_px=0, w_px=1280, h_px=BAND_H, fill_color=BRAND_PRIMARY)

add_text(slide, "band-eyebrow", "INDUSTRY OUTLOOK 2026",
    x_px=64, y_px=44, w_px=1152, h_px=22,
    font_size_pt=11, color=BRAND_ACCENT, bold=True, uppercase=True)

add_text(slide, "band-headline",
    "Three forces are compressing industry margins simultaneously.",
    x_px=64, y_px=72, w_px=1152, h_px=80,
    font_size_pt=28, color=WHITE, bold=True, anchor="top")

add_text(slide, "subtitle",
    "Each is independently survivable; together they require a structural response within 18 months.",
    x_px=64, y_px=BAND_H + 18, w_px=1152, h_px=24,
    font_size_pt=14, color=TEXT_MID, italic=True)

CARDS = [
    ("01", "Input cost re-rating",
     "Energy, freight, and skilled labor all stepped up 8-14% in 2025 and have not retraced.",
     "Pass-through to customers stalled at ~60% across the sector."),
    ("02", "Tariff regime instability",
     "Six tariff lines material to the sector revised in the last 12 months.",
     "Hedging windows have shortened; inventory carry costs up 22%."),
    ("03", "Channel concentration",
     "Top-3 customers now control 47% of volume, up from 31% in 2020.",
     "Renewal negotiations have visibly hardened in the last two cycles."),
]

CARD_TOP = 252
CARD_H = 380
GUTTER = 24
CARD_W = (1280 - 128 - 2 * GUTTER) // 3
for i, (num, head, body1, body2) in enumerate(CARDS):
    x = 64 + i * (CARD_W + GUTTER)
    add_rect(slide, f"card-{i}-bg", x_px=x, y_px=CARD_TOP, w_px=CARD_W, h_px=CARD_H, fill_color=CARD_BG)
    add_text(slide, f"card-{i}-num", num,
        x_px=x + 20, y_px=CARD_TOP + 18, w_px=80, h_px=44,
        font_size_pt=32, color=BRAND_PRIMARY, bold=True)
    add_text(slide, f"card-{i}-head", head,
        x_px=x + 20, y_px=CARD_TOP + 80, w_px=CARD_W - 40, h_px=60,
        font_size_pt=18, color=TEXT_DARK, bold=True)
    add_rect(slide, f"card-{i}-rule", x_px=x + 20, y_px=CARD_TOP + 156, w_px=40, h_px=2, fill_color=BRAND_ACCENT)
    add_text(slide, f"card-{i}-body1", body1,
        x_px=x + 20, y_px=CARD_TOP + 170, w_px=CARD_W - 40, h_px=110,
        font_size_pt=13, color=TEXT_DARK)
    add_text(slide, f"card-{i}-body2", body2,
        x_px=x + 20, y_px=CARD_TOP + 290, w_px=CARD_W - 40, h_px=80,
        font_size_pt=12, color=TEXT_MID, italic=True)

add_footer(slide, page_num=4, source="Sector benchmarks, McKinsey CPG outlook 2026; client interviews Mar-Apr 2026", footnote="Cost re-rating measured as TTM input index vs. 2019 base")

out_pptx = HERE / "gallery4-top-band-body.pptx"
prs.save(out_pptx)
print(f"WROTE {out_pptx}")
