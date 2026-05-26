"""Gallery 9 — Two full-width horizontal bands (before / after)."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT))
from twins.helpers import (
    new_slide, add_text, add_rect, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE, CARD_BG, CARD_BORDER,
)

prs, slide = new_slide()

add_title_block(
    slide,
    title="From a <strong>fragmented</strong> operating model to a <strong>unified</strong> one",
    subtitle="The 12-month transformation reshapes how the commercial organization runs",
)

BAND_TOP = 180
BAND_H = 220
GAP = 26
LEFT = 64
ROW_W = 1280 - 128

add_rect(slide, "today-bg", x_px=LEFT, y_px=BAND_TOP, w_px=ROW_W, h_px=BAND_H, fill_color=CARD_BG)
add_rect(slide, "today-edge", x_px=LEFT, y_px=BAND_TOP, w_px=4, h_px=BAND_H, fill_color=TEXT_FAINT)

add_text(slide, "today-label", "WHERE WE ARE TODAY",
    x_px=LEFT + 24, y_px=BAND_TOP + 18, w_px=400, h_px=22,
    font_size_pt=11, color=TEXT_FAINT, bold=True, uppercase=True)
add_text(slide, "today-head", "Fragmented, region-by-region",
    x_px=LEFT + 24, y_px=BAND_TOP + 44, w_px=600, h_px=36,
    font_size_pt=22, color=TEXT_DARK, bold=True)

TODAY_BULLETS = [
    "Six regional P&Ls, each with separate pricing committees and three-week cycles.",
    "Customer master fragmented across four CRM instances; no single global view.",
    "Quarterly forecast accuracy averages +/-18%; revisions land late in the quarter.",
]
y = BAND_TOP + 92
for i, b in enumerate(TODAY_BULLETS):
    add_rect(slide, f"today-bullet-{i}-dot", x_px=LEFT + 28, y_px=y + 8, w_px=6, h_px=6, fill_color=TEXT_FAINT)
    add_text(slide, f"today-bullet-{i}", b,
        x_px=LEFT + 44, y_px=y, w_px=ROW_W - 80, h_px=36,
        font_size_pt=13, color=TEXT_DARK)
    y += 38

B2_Y = BAND_TOP + BAND_H + GAP
add_rect(slide, "future-bg", x_px=LEFT, y_px=B2_Y, w_px=ROW_W, h_px=BAND_H, fill_color=BRAND_PRIMARY)
add_rect(slide, "future-edge", x_px=LEFT, y_px=B2_Y, w_px=4, h_px=BAND_H, fill_color=BRAND_ACCENT)

add_text(slide, "future-label", "WHERE WE'LL BE IN 12 MONTHS",
    x_px=LEFT + 24, y_px=B2_Y + 18, w_px=500, h_px=22,
    font_size_pt=11, color=BRAND_ACCENT, bold=True, uppercase=True)
add_text(slide, "future-head", "Unified, global, weekly cadence",
    x_px=LEFT + 24, y_px=B2_Y + 44, w_px=600, h_px=36,
    font_size_pt=22, color=WHITE, bold=True)

FUTURE_BULLETS = [
    "One global pricing engine; regions retain 80% mix authority within published guardrails.",
    "Single customer master on the new CRM platform; deduped against ERP and contracts.",
    "Weekly rolling forecast at +/-5%; replaces the quarterly cycle as the planning truth.",
]
y = B2_Y + 92
for i, b in enumerate(FUTURE_BULLETS):
    add_rect(slide, f"future-bullet-{i}-dot", x_px=LEFT + 28, y_px=y + 8, w_px=6, h_px=6, fill_color=BRAND_ACCENT)
    add_text(slide, f"future-bullet-{i}", b,
        x_px=LEFT + 44, y_px=y, w_px=ROW_W - 80, h_px=36,
        font_size_pt=13, color=WHITE)
    y += 38

arrow_y = BAND_TOP + BAND_H + 2
add_text(slide, "transition-arrow", "v",
    x_px=640 - 20, y_px=arrow_y, w_px=40, h_px=20,
    font_size_pt=14, color=BRAND_ACCENT, align="center", bold=True)

add_footer(slide, page_num=9, source="Commercial transformation plan v2.0, May 2026", footnote="Forecast accuracy measured as absolute % error vs. actuals, 6-quarter trailing")

out_pptx = HERE / "gallery9-horizontal-bands.pptx"
prs.save(out_pptx)
print(f"WROTE {out_pptx}")
