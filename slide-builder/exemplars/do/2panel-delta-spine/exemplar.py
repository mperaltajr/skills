"""
Comparison / 2panel-delta-spine — two columns with a center delta callout spine.

Family: Comparison
Variant: Two equal columns (Option A / Option B) with a narrow spine strip in the
         center carrying the DELTA ANNOTATION between the two. The spine is
         BRAND_PRIMARY-filled, white text, with a single BRAND_ACCENT chip showing
         the key delta number/label. Headers at the top of each column state which
         option is which. No convergence band at the bottom (contrast with
         2panel-convergence which unifies at the bottom — this variant keeps
         the two panels OPPOSED with the spine as the dividing/comparing element).

Layout shape:
- Left column (x=64, w=518): Option A content
- Center spine (x=590, w=100): BRAND_PRIMARY strip with delta annotation
- Right column (x=698, w=518): Option B content
- Column height: y=152→620 (full body)

Structural delta from 2panel-convergence:
- No convergence band at bottom (the footer stays neutral)
- CENTER SPINE is the visual differentiator — the delta lives there, not below
- The two columns end at the same y-level (no one wins visually — it's a true
  comparison, not a recommendation)
- Delta chip on spine = the ONE accent moment

Rulebook citations:
- Title block: add_title_block (§ 1)
- One accent moment: BRAND_ACCENT chip on the spine showing the key delta
- Bold ceiling: title (1) + 2 column headings (2) = 3. ≤5 ceiling honored.
- Body font floor: bullet text 14px, criteria labels 11px eyebrow
- No fabricated numbers — delta chip shows "[DELTA PLACEHOLDER]"
- Footer: add_footer(slide, page_num=4)
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT,
    CARD_BG, CARD_BORDER, WHITE,
)


def build():
    prs, slide = new_slide()

    add_title_block(
        slide,
        title="[Conclusion: which option is stronger, and why]",
        subtitle="[Sub-headline: what dimensions this comparison covers]",
    )

    # ── Geometry ──
    col_top = 152
    col_h = 468       # bottom @ y=620
    col_w = 518
    spine_w = 100
    spine_x = 64 + col_w + 8   # = 590

    left_x = 64
    right_x = spine_x + spine_w + 8   # = 698

    pad_x = 20
    pad_y = 16

    # ── Left column (Option A) ──
    add_rect(
        slide, "col-a-bg",
        x_px=left_x, y_px=col_top, w_px=col_w, h_px=col_h,
        fill_color=CARD_BG, no_line=True,
    )
    # Thin left border on col A
    add_rect(
        slide, "col-a-border",
        x_px=left_x, y_px=col_top, w_px=1, h_px=col_h,
        fill_color=CARD_BORDER,
    )

    # Column A header area
    add_rect(
        slide, "col-a-header-bg",
        x_px=left_x, y_px=col_top, w_px=col_w, h_px=56,
        fill_color=BRAND_PRIMARY,
    )
    add_text(
        slide, "col-a-header-eyebrow", "OPTION A",
        x_px=left_x + pad_x, y_px=col_top + 6,
        w_px=col_w - pad_x * 2, h_px=16,
        font_size_px=11, color=WHITE, bold=False, uppercase=True, letter_spacing_px=2,
    )
    add_text(
        slide, "col-a-header-label", "[Option A name or framing]",
        x_px=left_x + pad_x, y_px=col_top + 24,
        w_px=col_w - pad_x * 2, h_px=24,
        font_size_px=16, color=WHITE, bold=True,
    )

    # Column A bullets
    col_a_items = [
        ("[Criterion 1]: [Value / description for option A]",),
        ("[Criterion 2]: [Value / description for option A]",),
        ("[Criterion 3]: [Value / description for option A]",),
        ("[Criterion 4]: [Value / description for option A]",),
    ]
    for j, (item_text,) in enumerate(col_a_items):
        iy = col_top + 70 + j * 90
        add_rect(
            slide, f"col-a-item-{j+1}-marker",
            x_px=left_x + pad_x, y_px=iy + 5, w_px=8, h_px=8,
            fill_color=BRAND_PRIMARY,
        )
        add_text(
            slide, f"col-a-item-{j+1}", item_text,
            x_px=left_x + pad_x + 18, y_px=iy,
            w_px=col_w - pad_x * 2 - 18, h_px=78,
            font_size_px=14, color=TEXT_DARK, bold=False,
        )

    # ── Right column (Option B) ──
    add_rect(
        slide, "col-b-bg",
        x_px=right_x, y_px=col_top, w_px=col_w, h_px=col_h,
        fill_color=CARD_BG, no_line=True,
    )
    add_rect(
        slide, "col-b-border",
        x_px=right_x + col_w - 1, y_px=col_top, w_px=1, h_px=col_h,
        fill_color=CARD_BORDER,
    )

    # Column B header
    add_rect(
        slide, "col-b-header-bg",
        x_px=right_x, y_px=col_top, w_px=col_w, h_px=56,
        fill_color=BRAND_PRIMARY,
    )
    add_text(
        slide, "col-b-header-eyebrow", "OPTION B",
        x_px=right_x + pad_x, y_px=col_top + 6,
        w_px=col_w - pad_x * 2, h_px=16,
        font_size_px=11, color=WHITE, bold=False, uppercase=True, letter_spacing_px=2,
    )
    add_text(
        slide, "col-b-header-label", "[Option B name or framing]",
        x_px=right_x + pad_x, y_px=col_top + 24,
        w_px=col_w - pad_x * 2, h_px=24,
        font_size_px=16, color=WHITE, bold=True,
    )

    col_b_items = [
        ("[Criterion 1]: [Value / description for option B]",),
        ("[Criterion 2]: [Value / description for option B]",),
        ("[Criterion 3]: [Value / description for option B]",),
        ("[Criterion 4]: [Value / description for option B]",),
    ]
    for j, (item_text,) in enumerate(col_b_items):
        iy = col_top + 70 + j * 90
        add_rect(
            slide, f"col-b-item-{j+1}-marker",
            x_px=right_x + pad_x, y_px=iy + 5, w_px=8, h_px=8,
            fill_color=BRAND_PRIMARY,
        )
        add_text(
            slide, f"col-b-item-{j+1}", item_text,
            x_px=right_x + pad_x + 18, y_px=iy,
            w_px=col_w - pad_x * 2 - 18, h_px=78,
            font_size_px=14, color=TEXT_DARK, bold=False,
        )

    # ── Center spine ──
    # BRAND_PRIMARY filled strip. One BRAND_ACCENT chip in the middle = accent moment.
    add_rect(
        slide, "spine-bg",
        x_px=spine_x, y_px=col_top, w_px=spine_w, h_px=col_h,
        fill_color=BRAND_PRIMARY,
    )

    # "VS" label at top of spine
    add_text(
        slide, "spine-vs", "VS",
        x_px=spine_x, y_px=col_top + 16,
        w_px=spine_w, h_px=28,
        font_size_px=14, color=WHITE, bold=False,
        uppercase=True, align="center", letter_spacing_px=2,
    )

    # Divider rule below VS
    add_rect(
        slide, "spine-rule-top",
        x_px=spine_x + 16, y_px=col_top + 52, w_px=spine_w - 32, h_px=1,
        fill_color=WHITE,
    )

    # BRAND_ACCENT chip — the one accent moment — in the center of the spine.
    # Shows the key delta descriptor.
    chip_y = col_top + col_h // 2 - 24
    add_rect(
        slide, "delta-chip-bg",
        x_px=spine_x + 6, y_px=chip_y, w_px=spine_w - 12, h_px=36,
        fill_color=BRAND_ACCENT,
    )
    add_text(
        slide, "delta-chip-label", "[KEY DELTA]",
        x_px=spine_x + 6, y_px=chip_y,
        w_px=spine_w - 12, h_px=36,
        font_size_px=11, color=WHITE, bold=False, align="center", anchor="middle",
    )

    # Divider rule above bottom of spine
    add_rect(
        slide, "spine-rule-bottom",
        x_px=spine_x + 16, y_px=col_top + col_h - 54, w_px=spine_w - 32, h_px=1,
        fill_color=WHITE,
    )

    # Recommendation indicator at bottom of spine
    add_text(
        slide, "spine-recommend", "[RECOMMEND]",
        x_px=spine_x, y_px=col_top + col_h - 48,
        w_px=spine_w, h_px=40,
        font_size_px=11, color=WHITE, bold=False, align="center",
        anchor="middle",
    )

    add_footer(slide, page_num=4)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
