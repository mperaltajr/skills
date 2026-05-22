"""
Anti-exemplar — vertical accent rule with NO horizontal gutter to adjacent text.

Family: any (chrome-level failure — applies regardless of page-type family)
Verdict: dont

What this slide does WRONG:
- A vertical BRAND_ACCENT rule runs the full height of the body zone.
- Three numbered items (1. 2. 3.) are placed immediately to the right of the
  rule with ZERO horizontal padding. The numerals butt directly against the
  rule, so the line visually cuts into the numbers.

The failure is structural, not content-related. The fix is to leave ≥16px
of horizontal gutter between any vertical accent rule and adjacent text — or
narrow the rule, or shift the content right. The rule and the content must
not touch.

Run standalone:
    python exemplar.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_DARK, TEXT_MID,
)


# ── Layout constants ──────────────────────────────────────────────────────
CANVAS_W = 1280
CANVAS_H = 720

BODY_X = 64
BODY_Y = 156
BODY_W = CANVAS_W - 128       # 1152
BODY_H = 460                  # body zone runs to ~y=616, above the footer

RULE_W = 5                    # 4–6px wide vertical accent rule
RULE_X = BODY_X
RULE_Y = BODY_Y
RULE_H = BODY_H

# THE FAILURE: content starts at RULE_X + RULE_W — zero horizontal gutter.
CONTENT_X = RULE_X + RULE_W   # numerals crash directly into the rule
CONTENT_W = BODY_W - RULE_W

ROW_GAP = 24
ROW_H = (BODY_H - 2 * ROW_GAP) // 3   # three rows stacked in the body zone


def build():
    prs, slide = new_slide()

    # === Title block (bottom-anchored at y=100) ===
    add_title_block(
        slide,
        title="[Placeholder title — governing thought for this slide]",
        subtitle="[Placeholder sub-headline — one supporting line of context]",
    )

    # === Vertical BRAND_ACCENT rule (the chrome element) ===
    add_rect(
        slide, "vertical-accent-rule",
        x_px=RULE_X, y_px=RULE_Y, w_px=RULE_W, h_px=RULE_H,
        fill_color=BRAND_ACCENT,
    )

    # === Three numbered items, butted against the rule (no gutter) ===
    items = [
        (
            "1.",
            "[Placeholder item heading one]",
            "[Placeholder supporting sentence describing the first item.]",
        ),
        (
            "2.",
            "[Placeholder item heading two]",
            "[Placeholder supporting sentence describing the second item.]",
        ),
        (
            "3.",
            "[Placeholder item heading three]",
            "[Placeholder supporting sentence describing the third item.]",
        ),
    ]

    for i, (num, heading, body) in enumerate(items):
        n = i + 1
        ry = BODY_Y + i * (ROW_H + ROW_GAP)

        # Numeral — placed at CONTENT_X (= rule's right edge). Zero gutter.
        # This is the visual crash: the "1." touches the vertical rule.
        add_text(
            slide, f"item-{n}-num", num,
            x_px=CONTENT_X, y_px=ry,
            w_px=56, h_px=44,
            font_size_px=28, color=BRAND_PRIMARY, bold=True,
        )
        # Heading — also starts at CONTENT_X-ish; we offset only past the numeral,
        # not past any gutter. The numeral itself is still kissing the rule.
        add_text(
            slide, f"item-{n}-heading", heading,
            x_px=CONTENT_X + 56, y_px=ry + 2,
            w_px=CONTENT_W - 56, h_px=32,
            font_size_px=20, color=TEXT_DARK, bold=True,
        )
        # Body
        add_text(
            slide, f"item-{n}-body", body,
            x_px=CONTENT_X + 56, y_px=ry + 40,
            w_px=CONTENT_W - 56, h_px=ROW_H - 44,
            font_size_px=14, color=TEXT_MID,
        )

    # === Footer (invariant chrome only) ===
    add_footer(slide, page_num=1)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
