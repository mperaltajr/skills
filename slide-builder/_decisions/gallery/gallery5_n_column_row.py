"""Gallery 5 — N-column row (N=4)."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT))
from twins.helpers import (
    new_slide, add_text, add_rect, add_circle, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE, CARD_BG,
)

prs, slide = new_slide()

add_title_block(
    slide,
    title="Four phases of the <strong>core systems migration</strong>",
    subtitle="A 14-month roadmap, with stage-gates between each phase",
)

TOP = 190
COL_H = 420
GUTTER = 16
N = 4
COL_W = (1280 - 128 - (N - 1) * GUTTER) // N

PHASES = [
    ("01", "Discover", "Months 1-2",
     "Map current ERP footprint, integrations, and data dependencies.",
     ["Stakeholder interviews (n=40)", "Process inventory & criticality scoring", "Data quality baseline"]),
    ("02", "Diagnose", "Months 3-5",
     "Identify root-cause sources of cost, latency, and risk.",
     ["Cost-to-serve teardown", "Order-to-cash time-and-motion", "Risk heatmap & control gaps"]),
    ("03", "Design", "Months 6-9",
     "Build target architecture and migration sequencing.",
     ["Future-state blueprint", "Wave plan & cutover strategy", "Org & capability model"]),
    ("04", "Deploy", "Months 10-14",
     "Execute waves with parallel run, hypercare, and value tracking.",
     ["Wave 1-3 cutover", "Hypercare (8 weeks)", "Value capture & sign-off"]),
]

add_rect(slide, "phase-track", x_px=64 + 28, y_px=TOP + 28, w_px=1280 - 128 - 56, h_px=2, fill_color=BRAND_ACCENT)

for i, (num, name, when, summary, items) in enumerate(PHASES):
    x = 64 + i * (COL_W + GUTTER)
    cd = 56
    add_circle(slide, f"phase-{i}-circle", x_px=x + COL_W//2 - cd//2, y_px=TOP, diameter_px=cd, fill_color=BRAND_PRIMARY)
    add_text(slide, f"phase-{i}-num", num,
        x_px=x + COL_W//2 - cd//2, y_px=TOP, w_px=cd, h_px=cd,
        font_size_pt=16, color=WHITE, bold=True, align="center", anchor="middle")
    add_text(slide, f"phase-{i}-name", name,
        x_px=x, y_px=TOP + 70, w_px=COL_W, h_px=36,
        font_size_pt=20, color=TEXT_DARK, bold=True, align="center")
    add_text(slide, f"phase-{i}-when", when,
        x_px=x, y_px=TOP + 106, w_px=COL_W, h_px=20,
        font_size_pt=11, color=BRAND_PRIMARY, bold=True, align="center", uppercase=True)
    add_text(slide, f"phase-{i}-summary", summary,
        x_px=x + 8, y_px=TOP + 138, w_px=COL_W - 16, h_px=64,
        font_size_pt=12, color=TEXT_MID, italic=True, align="center")
    y = TOP + 220
    for j, item in enumerate(items):
        add_text(slide, f"phase-{i}-item-{j}", f"-  {item}",
            x_px=x + 12, y_px=y, w_px=COL_W - 24, h_px=42,
            font_size_pt=12, color=TEXT_DARK)
        y += 50

add_footer(slide, page_num=5, source="Program plan v3.1, May 2026", footnote="Months indexed from program kickoff (Q3 FY26)")

out_pptx = HERE / "gallery5-n-column-row.pptx"
prs.save(out_pptx)
print(f"WROTE {out_pptx}")
