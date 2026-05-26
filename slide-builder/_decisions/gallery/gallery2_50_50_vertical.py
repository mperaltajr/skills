"""Gallery 2 — 50/50 vertical split."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT))
from twins.helpers import (
    new_slide, add_text, add_rect, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)

prs, slide = new_slide()

add_title_block(
    slide,
    title="Today's process versus <strong>Slide Lab's process</strong>",
    subtitle="Where the 70% of wasted time goes — and what replaces it",
)

BODY_TOP = 170
BODY_H = 460
GUTTER = 24
COL_W = (1280 - 128 - GUTTER) // 2
LEFT_X = 64
RIGHT_X = LEFT_X + COL_W + GUTTER

add_rect(slide, "vrule", x_px=LEFT_X + COL_W + GUTTER//2 - 1, y_px=BODY_TOP, w_px=2, h_px=BODY_H, fill_color=TEXT_FAINT)

add_text(slide, "left-eyebrow", "TODAY",
    x_px=LEFT_X, y_px=BODY_TOP, w_px=COL_W, h_px=22,
    font_size_pt=11, color=TEXT_FAINT, bold=True, uppercase=True)
add_text(slide, "left-head", "Slow, manual, template-blind",
    x_px=LEFT_X, y_px=BODY_TOP + 28, w_px=COL_W, h_px=40,
    font_size_pt=22, color=TEXT_DARK, bold=True)

LEFT_BULLETS = [
    ("Hunt for a similar past deck", "20-40 minutes of searching shared drives before any work starts."),
    ("Hand-format every slide", "Color, type, alignment fought across 30+ slides per deck."),
    ("QC by eye, at midnight", "Inconsistencies found at the partner review, not earlier."),
    ("Rebuild on every reflow", "Adding a slide breaks the formatting of the next four."),
]
y = BODY_TOP + 90
for i, (head, body) in enumerate(LEFT_BULLETS):
    add_text(slide, f"left-bullet-{i}-head", f"-  {head}",
        x_px=LEFT_X, y_px=y, w_px=COL_W, h_px=22,
        font_size_pt=14, color=TEXT_DARK, bold=True)
    add_text(slide, f"left-bullet-{i}-body", body,
        x_px=LEFT_X + 14, y_px=y + 22, w_px=COL_W - 14, h_px=46,
        font_size_pt=12, color=TEXT_MID)
    y += 78

add_text(slide, "right-eyebrow", "WITH SLIDE LAB",
    x_px=RIGHT_X, y_px=BODY_TOP, w_px=COL_W, h_px=22,
    font_size_pt=11, color=BRAND_PRIMARY, bold=True, uppercase=True)
add_text(slide, "right-head", "Locked template, vision QC, parallel agents",
    x_px=RIGHT_X, y_px=BODY_TOP + 28, w_px=COL_W, h_px=40,
    font_size_pt=22, color=BRAND_PRIMARY, bold=True)

RIGHT_BULLETS = [
    ("Brief in, deck out", "Storyline helper writes the narrative brief in one pass."),
    ("Template is a constraint, not a chore", "Every shape inherits client brand automatically."),
    ("QC runs before partner sees it", "Vision model reads each slide; criticals block; majors flagged."),
    ("Reflow is free", "Page numbers, callouts, references all recompute on save."),
]
y = BODY_TOP + 90
for i, (head, body) in enumerate(RIGHT_BULLETS):
    add_text(slide, f"right-bullet-{i}-head", f"-  {head}",
        x_px=RIGHT_X, y_px=y, w_px=COL_W, h_px=22,
        font_size_pt=14, color=TEXT_DARK, bold=True)
    add_text(slide, f"right-bullet-{i}-body", body,
        x_px=RIGHT_X + 14, y_px=y + 22, w_px=COL_W - 14, h_px=46,
        font_size_pt=12, color=TEXT_MID)
    y += 78

add_footer(slide, page_num=2, source="Slide Lab v2.5 architecture review, May 2026", footnote="Process comparison covers a typical 30-slide consulting deliverable")

out_pptx = HERE / "gallery2-50-50-vertical.pptx"
prs.save(out_pptx)
print(f"WROTE {out_pptx}")
