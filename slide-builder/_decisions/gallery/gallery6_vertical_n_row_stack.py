"""Gallery 6 — Vertical N-row stack with numeral anchors."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT))
from twins.helpers import (
    new_slide, add_text, add_rect, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE, CARD_BG, CARD_BORDER,
)

prs, slide = new_slide()

add_title_block(
    slide,
    title="Four operating principles for <strong>FY26</strong>",
    subtitle="Adopted by the executive committee, May 14 — supersedes the FY25 operating model",
)

ROWS = [
    ("01", "Capital allocated to growth, not status quo",
     "Two-thirds of new capital flows to the three growth platforms; legacy receives maintenance-only funding."),
    ("02", "Decisions made closest to the customer",
     "Region presidents own pricing, mix, and SKU rationalization within published guardrails."),
    ("03", "One operating cadence — quarterly, not monthly",
     "Replace 14 monthly reviews with a single QBR; weekly ops calls stay for execution only."),
    ("04", "Talent moves toward the work, not the title",
     "Internal mobility default-on; managers cannot block transfers to strategic priorities."),
]

ROW_TOP = 178
ROW_H = 108
ROW_GAP = 14
LEFT = 64
ROW_W = 1280 - 128

for i, (num, head, body) in enumerate(ROWS):
    y = ROW_TOP + i * (ROW_H + ROW_GAP)
    add_rect(slide, f"row-{i}-bg", x_px=LEFT, y_px=y, w_px=ROW_W, h_px=ROW_H, fill_color=CARD_BG)
    add_text(slide, f"row-{i}-num", num,
        x_px=LEFT + 18, y_px=y + 18, w_px=80, h_px=72,
        font_size_pt=44, color=BRAND_PRIMARY, bold=True, align="left", anchor="middle")
    add_rect(slide, f"row-{i}-vline", x_px=LEFT + 112, y_px=y + 18, w_px=2, h_px=ROW_H - 36, fill_color=BRAND_ACCENT)
    add_text(slide, f"row-{i}-head", head,
        x_px=LEFT + 134, y_px=y + 20, w_px=ROW_W - 154, h_px=34,
        font_size_pt=18, color=TEXT_DARK, bold=True)
    add_text(slide, f"row-{i}-body", body,
        x_px=LEFT + 134, y_px=y + 56, w_px=ROW_W - 154, h_px=44,
        font_size_pt=13, color=TEXT_MID)

add_footer(slide, page_num=6, source="Executive committee resolution 2026-08", footnote="Principles take effect from FY26 Q1; transition guidance issued separately")

out_pptx = HERE / "gallery6-vertical-n-row-stack.pptx"
prs.save(out_pptx)
print(f"WROTE {out_pptx}")
