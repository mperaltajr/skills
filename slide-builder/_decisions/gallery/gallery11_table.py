"""Gallery 11 — Banded-rows table comparing 3 strategy options."""
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
    title="<strong>Option B — Joint venture</strong> outperforms across three of four criteria",
    subtitle="Comparative assessment of three market-entry options for Southeast Asia",
)

TABLE_X = 64
TABLE_Y = 184
TABLE_W = 1280 - 128

HEADERS = ["Option", "Cost (3-yr)", "Time to market", "Risk", "Strategic fit"]
ROWS = [
    ("A — Greenfield build",       "$240M",      "30-36 months", "High",     "Strong long-term, slow short-term"),
    ("B — Joint venture",          "$110M",      "9-12 months",  "Moderate", "Best balance; preserves optionality"),
    ("C — Acquisition (Target X)", "$320M",      "12-15 months", "Moderate", "Strong, but integration is the variable"),
]
RECOMMENDED_IDX = 1

COL_WIDTHS = [320, 160, 200, 140, TABLE_W - 320 - 160 - 200 - 140]

ROW_H_HEADER = 50
ROW_H = 70

add_rect(slide, "th-bg", x_px=TABLE_X, y_px=TABLE_Y, w_px=TABLE_W, h_px=ROW_H_HEADER, fill_color=BRAND_PRIMARY)

x = TABLE_X
for c, header in enumerate(HEADERS):
    add_text(slide, f"th-{c}", header,
        x_px=x + 16, y_px=TABLE_Y, w_px=COL_WIDTHS[c] - 32, h_px=ROW_H_HEADER,
        font_size_pt=13, color=WHITE, bold=True, uppercase=True, anchor="middle",
        letter_spacing_px=1)
    x += COL_WIDTHS[c]

for r, row in enumerate(ROWS):
    y = TABLE_Y + ROW_H_HEADER + r * ROW_H
    is_recommended = (r == RECOMMENDED_IDX)
    if is_recommended:
        row_fill = BRAND_ACCENT_SOFT
    elif r % 2 == 0:
        row_fill = WHITE
    else:
        row_fill = CARD_BG
    add_rect(slide, f"row-{r}-bg", x_px=TABLE_X, y_px=y, w_px=TABLE_W, h_px=ROW_H, fill_color=row_fill)
    if is_recommended:
        add_rect(slide, f"row-{r}-edge", x_px=TABLE_X, y_px=y, w_px=4, h_px=ROW_H, fill_color=BRAND_ACCENT)

    x = TABLE_X
    for c, val in enumerate(row):
        bold = (c == 0) or is_recommended
        text_color = BRAND_PRIMARY if (is_recommended and c == 0) else TEXT_DARK
        add_text(slide, f"cell-{r}-{c}", val,
            x_px=x + 16, y_px=y, w_px=COL_WIDTHS[c] - 32, h_px=ROW_H,
            font_size_pt=12, color=text_color, bold=bold, anchor="middle")
        x += COL_WIDTHS[c]

# Recommended marker — small pill at the LEFT edge of the row, beside the accent edge
badge_y = TABLE_Y + ROW_H_HEADER + RECOMMENDED_IDX * ROW_H
# (the left accent edge is already drawn earlier as row-{r}-edge for the recommended row)

table_bottom = TABLE_Y + ROW_H_HEADER + len(ROWS) * ROW_H
add_rect(slide, "table-bottom", x_px=TABLE_X, y_px=table_bottom, w_px=TABLE_W, h_px=1, fill_color=CARD_BORDER)

SO_Y = table_bottom + 26
add_rect(slide, "sowhat-bar", x_px=TABLE_X, y_px=SO_Y, w_px=4, h_px=80, fill_color=BRAND_ACCENT)
add_text(slide, "sowhat-label", "SO WHAT",
    x_px=TABLE_X + 18, y_px=SO_Y, w_px=120, h_px=20,
    font_size_pt=10, color=BRAND_PRIMARY, bold=True, uppercase=True, letter_spacing_px=2)
add_text(slide, "sowhat-text",
    "Option B delivers the strategic position of greenfield at one-third the time and half the capital — and "
    "preserves the option to take full ownership in years 4-5 if performance warrants.",
    x_px=TABLE_X + 18, y_px=SO_Y + 22, w_px=TABLE_W - 36, h_px=60,
    font_size_pt=13, color=TEXT_DARK, italic=False)

add_footer(slide, page_num=11, source="Internal strategy model v1.4; benchmarks from prior SEA entries by peer firms (n=11)", footnote="Cost figures in USD nominal; time-to-market measured from board approval")

out_pptx = HERE / "gallery11-table.pptx"
prs.save(out_pptx)
print(f"WROTE {out_pptx}")


