"""Gallery 1 — Full canvas / hero claim."""
import sys, os
from pathlib import Path
HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT))
from twins.helpers import (
    new_slide, add_text, add_rect, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_DARK, TEXT_MID, WHITE,
)

prs, slide = new_slide()

add_text(
    slide, "eyebrow", "SLIDE LAB — POINT OF VIEW",
    x_px=64, y_px=120, w_px=1152, h_px=22,
    font_size_pt=11, color=BRAND_PRIMARY, bold=True, letter_spacing_px=2,
    uppercase=True, align="left",
)

add_text(
    slide, "hero-claim",
    "<strong>70%</strong> of deck-building time is template-fighting.",
    x_px=64, y_px=180, w_px=1152, h_px=140,
    font_size_pt=52, color=TEXT_DARK, bold=False,
    emphasis_color=BRAND_ACCENT,
    align="left", anchor="top",
)

add_text(
    slide, "counter",
    "Slide Lab eliminates it.",
    x_px=64, y_px=340, w_px=1152, h_px=70,
    font_size_pt=44, color=BRAND_PRIMARY, bold=True,
    align="left", anchor="top",
)

add_rect(slide, "accent-rule", x_px=64, y_px=440, w_px=80, h_px=4, fill_color=BRAND_ACCENT)

add_text(
    slide, "support",
    "Hand-built twins. Vision-driven QC. One template-locked pipeline from brief to PPTX.",
    x_px=64, y_px=466, w_px=1080, h_px=60,
    font_size_pt=18, color=TEXT_MID, italic=True,
    align="left", anchor="top",
)

add_footer(slide, page_num=1, source="Slide Lab internal benchmarks, 2026", footnote="Time-on-task survey, n=42 consultants")

out_pptx = HERE / "gallery1-full-canvas.pptx"
prs.save(out_pptx)
print(f"WROTE {out_pptx}")
