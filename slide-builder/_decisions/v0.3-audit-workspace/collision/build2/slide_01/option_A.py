"""Deliberately colliding dark slide: includes a purple-filled rect AND
purple text on a no-fill text box. If the collision detector works
end-to-end, finalize should raise DarkVariantCollisionError."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parents[4]
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SCRIPTS))

from twins.helpers import new_slide, add_title_block, add_text, add_rect
from pptx.dml.color import RGBColor

FEDEX_PURPLE = RGBColor(0x4D, 0x14, 0x8C)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs, slide = new_slide()
add_title_block(slide, "Colliding dark slide")

# A purple-filled rect on what will become a purple background — collision.
add_rect(slide, "evil-purple-rect", 200, 200, 400, 80, FEDEX_PURPLE)

# Purple text on a no-fill text box — collision.
add_text(slide, "evil-purple-text", "I am invisible on the dark bg",
         200, 320, 800, 60, font_size_pt=18, color=FEDEX_PURPLE)

# Plus some safe content to make sure non-colliding shapes don't get flagged.
add_text(slide, "safe-white", "This white text is visible",
         200, 420, 800, 40, font_size_pt=14, color=WHITE)

out = HERE / "option_A.pptx"
prs.save(str(out))
