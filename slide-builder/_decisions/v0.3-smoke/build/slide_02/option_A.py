"""Minimal smoke option for slide 2. Builds a one-slide PPTX
with title + body content. The graft step substitutes the OTC layout
chrome around it."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parents[3]  # _decisions/v0.3-smoke/build/slide_NN -> slide-builder
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SCRIPTS))

from twins.helpers import (
    new_slide, add_title_block, add_text, TEXT_DARK, BRAND_PRIMARY,
    SLIDE_W_PX, SLIDE_H_PX,
)

prs, slide = new_slide()

add_title_block(slide, "OTC body dark via overlay")

add_text(
    slide, "body-1", "Slide 2: same body-canonical path, plus a dark overlay rectangle on top of the layout chrome.",
    x_px=60, y_px=200, w_px=1160, h_px=80,
    font_size_pt=18, color=TEXT_DARK,
)
add_text(
    slide, "body-2",
    "Body content lives in the zone between the layout title placeholder "
    "and its footer placeholder.",
    x_px=60, y_px=300, w_px=1160, h_px=60,
    font_size_pt=14, color=TEXT_DARK,
)

out = HERE / "option_A.pptx"
prs.save(str(out))
