"""Slide 1 — LIGHT body — three finding blocks."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parents[4]
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SCRIPTS))

from twins.helpers import (
    new_slide, add_title_block, add_text, add_rect,
    TEXT_DARK, BRAND_PRIMARY, BRAND_ACCENT,
)
from pptx.dml.color import RGBColor

WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs, slide = new_slide()
add_title_block(slide, "Top 3 findings - AR & collections gaps")

findings = [
    ("01", "Cash application gap", "27% of incoming wires unmatched > 5 days."),
    ("02", "Disputed invoice volume", "Disputes run at 4.8% of invoiced revenue."),
    ("03", "Credit-memo leakage", "$3.2M in credit memos with no PO-level audit trail."),
]
top = 130
h = 130
gap = 10
for i, (num, headline, body) in enumerate(findings):
    y = top + i * (h + gap)
    add_rect(slide, "num-bar-%d" % i, 58, y, 60, h, BRAND_PRIMARY)
    add_text(slide, "num-%d" % i, num, 64, y + 30, 50, 40,
             font_size_pt=28, bold=True, color=WHITE)
    add_text(slide, "head-%d" % i, headline, 140, y + 8, 1080, 36,
             font_size_pt=18, bold=True, color=BRAND_PRIMARY)
    add_text(slide, "body-%d" % i, body, 140, y + 50, 1080, h - 50,
             font_size_pt=13, color=TEXT_DARK)

out = HERE / "option_A.pptx"
prs.save(str(out))
