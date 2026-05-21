"""
Slide 2 — Option B: Left anchor panel + right list of forces.

Layout family: split-panel (anchor occupies left ~38%, supporting forces stack
vertically on the right). Structurally distinct from Option A (top anchor band
+ horizontal cards) and Option C (top headline + 3-card row).

Page type: anchor-with-supporting-cards (page-types.md — Insight / Finding
with editorial emphasis on conclusion dominance, expressed as a hero panel).

Rules honored:
- Designer brief §5 Two-column with insight panel: left dark panel = hero;
  right side = subordinate evidence rows.
- Designer brief §1 Title bottom-anchor: add_title_block handles y=100.
- Designer brief §6 Bold discipline: title (1) + anchor takeaway (1) + 3 row
  labels (3) = 5 bold elements. Eyebrow on panel is NOT bold; body rows are
  NOT bold; row numerals are NOT bold (numerals carry weight via size and
  BRAND_PRIMARY color).
- Designer brief §1 One accent moment: 4px BRAND_ACCENT vertical rule running
  the full height of the left anchor panel — single, load-bearing accent.
- Designer brief §6 No additional accents on the right side: separators
  between rows are 1px CARD_BORDER neutrals, NOT BRAND_ACCENT.
- Designer brief §6 Slot sizes: eyebrow=11px non-bold; anchor takeaway=24px
  bold WHITE; row label=18px bold TEXT_DARK; row body=14px TEXT_MID.
- Title length: governing thought = 67 chars (≤90), passed verbatim with
  inline <strong> tint on the operative phrase.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)


def build():
    prs, slide = new_slide()

    # === Title block (bottom-anchored at y=100) ===
    add_title_block(
        slide,
        title=("Consultants rarely lack ideas — "
               "they struggle to <strong>cut through them</strong>."),
        subtitle=("Not a knowledge gap. Not a skill deficit. "
                  "A structural problem — and structural problems have structural solutions."),
    )

    # === Left anchor panel — BRAND_PRIMARY fill, ~38% width ===
    # Body zone: y ≈ 156 → 640 (~484px tall panel, runs deep per §6 side-panel rule).
    body_y = 156
    body_h = 484
    lp_x = 64
    lp_w = int((1280 - 128) * 0.38)  # ≈ 437
    add_rect(slide, "anchor-panel-bg", lp_x, body_y, lp_w, body_h, BRAND_PRIMARY)

    # 4px BRAND_ACCENT vertical rule on the right edge of the panel — single
    # accent moment, marks the transition between hero and evidence.
    add_rect(slide, "anchor-panel-accent", lp_x + lp_w - 4, body_y, 4, body_h, BRAND_ACCENT)

    # Eyebrow (NOT bold)
    add_text(
        slide, "anchor-eyebrow", "THE REFRAME",
        x_px=lp_x + 28, y_px=body_y + 32, w_px=lp_w - 56, h_px=16,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=False,
        uppercase=True, letter_spacing_px=3,
    )
    # Anchor takeaway (bold #2 of 5)
    add_text(
        slide, "anchor-takeaway",
        "Not a knowledge gap. A structural problem — and structural problems have structural solutions.",
        x_px=lp_x + 28, y_px=body_y + 64, w_px=lp_w - 56, h_px=240,
        font_size_px=24, color=WHITE, bold=True,
    )
    # Bottom-anchored supporting line on panel (non-bold, soft white)
    add_text(
        slide, "anchor-tagline",
        "Three compounding forces drive the bottleneck →",
        x_px=lp_x + 28, y_px=body_y + body_h - 56, w_px=lp_w - 56, h_px=24,
        font_size_px=14, color=BRAND_ACCENT_SOFT, italic=True, bold=False,
    )

    # === Right side — three numbered rows ===
    rs_x = lp_x + lp_w + 32
    rs_w = 1280 - 64 - rs_x  # right side width
    row_h = body_h // 3  # ≈ 161 each

    labels = [
        "Too much to say",
        "Too many cooks",
        "The audience needs what's next",
    ]
    bodies = [
        ("Knowing what to cut is harder than knowing what to include. "
         "Every workstream generates legitimate findings."),
        ("Every collaborator has a view on what belongs on the page. "
         "More opinions mean harder choices, not a richer argument."),
        ("They don't need to understand all the work. "
         "They need to understand the next step."),
    ]

    for i in range(3):
        n = i + 1
        ry = body_y + i * row_h

        # 1px CARD_BORDER separator between rows (skip top edge of first row)
        if i > 0:
            add_rect(slide, f"row-{n}-divider", rs_x, ry, rs_w, 1, CARD_BORDER)

        # Big numeral — BRAND_PRIMARY, NOT bold (weight comes from size)
        add_text(
            slide, f"row-{n}-num", f"0{n}",
            x_px=rs_x, y_px=ry + 18, w_px=64, h_px=48,
            font_size_px=36, color=BRAND_PRIMARY, bold=False,
        )
        # Label (bold #3, #4, #5)
        add_text(
            slide, f"row-{n}-label", labels[i],
            x_px=rs_x + 76, y_px=ry + 22, w_px=rs_w - 76, h_px=30,
            font_size_px=18, color=TEXT_DARK, bold=True,
        )
        # Body (NOT bold)
        add_text(
            slide, f"row-{n}-body", bodies[i],
            x_px=rs_x + 76, y_px=ry + 58, w_px=rs_w - 76, h_px=row_h - 70,
            font_size_px=14, color=TEXT_MID, bold=False,
        )

    # === Footer (invariant chrome only) ===
    add_footer(slide, page_num=2)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "option_B.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
