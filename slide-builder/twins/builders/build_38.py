"""
Builder for pattern 38: Statement hero — single bold thesis dominates the canvas.

Dark-mode pattern. Brand-primary background. No standard title block — the
"stage" is centered and replaces title/subtitle/brand-rule.

Source HTML: _pattern-library/38_statement-hero-text.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    DRAFT_BG, DRAFT_TEXT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_FAINT = RGBColor(0xB8, 0xA5, 0xD9)


def build():
    prs, slide = new_slide()

    # Override slide background — hero pattern uses brand-primary
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Variant chrome — project-label at left:64 in brand-accent-soft

    # Stage — centered. Total stage content height ~430px, sits centered around y=360
    # Items, top to bottom: eyebrow (16h) + 48mb + statement (~160h) + 56mt + rule (3h) + 32mb + attribution (16h) + 28mt + context (~40h)
    # Total: 16+48+160+56+3+32+16+28+40 = 399. Centered → top = (720-399)/2 ≈ 160
    stage_top = 145
    stage_left = 120  # 1280 width - 1040 stage / 2 = 120

    # Eyebrow
    add_text(
        slide, "eyebrow", "What it comes down to",
        x_px=stage_left, y_px=stage_top, w_px=1040, h_px=18,
        font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True,
        align="center", uppercase=True,
    )

    # Hero statement (large italic centered)
    add_text(
        slide, "hero-statement",
        "“The deck doesn’t need to be longer. It needs to be sharper.”",
        x_px=stage_left, y_px=stage_top + 18 + 48,
        w_px=1040, h_px=170,
        font_size_px=56, color=WHITE, italic=True, align="center",
    )

    # Hero rule — 120px × 3px, centered, brand-accent
    rule_y = stage_top + 18 + 48 + 170 + 56
    add_rect(
        slide, "hero-rule",
        x_px=(1280 - 120) // 2, y_px=rule_y, w_px=120, h_px=3,
        fill_color=BRAND_ACCENT,
    )

    # Attribution
    attr_y = rule_y + 3 + 32
    add_text(
        slide, "hero-attribution",
        "Mario Peralta · After 12 pilot decks · May 2026",
        x_px=stage_left, y_px=attr_y, w_px=1040, h_px=18,
        font_size_px=14, color=TEXT_ON_DARK_FAINT, align="center",
    )

    # Context
    ctx_y = attr_y + 18 + 28
    add_text(
        slide, "hero-context",
        "If you remember nothing else from the next 30 minutes, remember this.",
        x_px=(1280 - 720) // 2, y_px=ctx_y, w_px=720, h_px=24,
        font_size_px=14, color=BRAND_ACCENT_SOFT, italic=True, align="center",
    )

    # Footer (variant — brand-accent-soft at low opacity. Use faint color.)
    add_text(slide, "page-number", "38",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "38_statement-hero-text.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
