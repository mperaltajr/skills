"""
three-col-progressive — SCQA Problem / Solution / Recommendation as three
columns with PROGRESSIVE visual emphasis from left to right.

What makes this distinct from 3pillar-icon-circles:
- 3pillar-icon-circles is PARALLEL MECE pillars: all three columns get the
  same treatment because they read as a single integrated family.
- THIS pattern is SEQUENTIAL / SCQA: the three columns are NOT peers. The
  recommendation (column 3) is the load-bearing answer. The eye should be
  pulled rightward and land on the dark card.

Progressive emphasis ladder (left -> right):
- Column 1 (Problem): dashed neutral border, white fill, faint heading.
  Reads as "context / background" - necessary but light.
- Column 2 (Solution): solid CARD_BG fill, thin CARD_BORDER outline, full
  TEXT_DARK heading. Reads as "the analytical middle."
- Column 3 (Recommendation): BRAND_PRIMARY dark fill, WHITE text, with a
  BRAND_ACCENT top rule. THIS is the one accent moment. Reads as "the
  answer - start here if you only read one card."

Design rationale (rulebook citations):
- Designer Brief Sec 1 One accent moment: BRAND_ACCENT lives on the top
  rule of column 3 only. Columns 1 and 2 carry zero accent. The title
  block no longer auto-emits a brand-rule, so the accent budget is spent
  here on the load-bearing element (the recommendation).
- Designer Brief Sec 6 Bold discipline: title + 3 column headings = 4
  bold elements (under the <=5 ceiling). Body text and eyebrows stay
  non-bold.
- Designer Brief Sec 4 Page types - Three-column parallel (progressive
  variant for SCQA / Problem-Solution-Recommendation).
- Memory: title bottom-anchor rule via add_title_block.
- Memory: invariant zone chrome - only add_footer in the bottom zone.
- Memory: TEXT_MID / TEXT_FAINT are aliased to TEXT_DARK; hierarchy comes
  from size and weight, not from gray gradients.

Skeleton source: 01_Executive Summary.pptx, slide 5 ("Default" layout) -
the classic exec-summary three-column with Problem | Solution |
Recommendation columns.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree

from twins.helpers import (
    new_slide, add_text, add_rect, add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_DARK,
    CARD_BG, CARD_BORDER, WHITE,
    px_to_emu,
)


def _add_dashed_card(slide, shape_id, x_px, y_px, w_px, h_px,
                     fill_color, line_color):
    """Rectangle with a dashed neutral outline. Used for column 1 to
    visually de-emphasize it relative to columns 2 and 3."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        px_to_emu(x_px), px_to_emu(y_px),
        px_to_emu(w_px), px_to_emu(h_px),
    )
    shape.name = shape_id
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.color.rgb = line_color
    shape.line.width = 9525  # 1px
    # Dashed line via XML (python-pptx has no first-class dashed API)
    ln = shape.line._get_or_add_ln()
    for existing in ln.findall(qn("a:prstDash")):
        ln.remove(existing)
    prst = etree.SubElement(ln, qn("a:prstDash"))
    prst.set("val", "dash")
    return shape


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="[Action title - the recommendation in one sentence.]",
        subtitle="[Subtitle - the SCQA setup that earns the recommendation on the right.]",
    )

    # ------------------------------------------------------------------
    # Three-column geometry. Same widths as 3pillar-icon-circles so the
    # two patterns share a body grid - only the treatment differs.
    # ------------------------------------------------------------------
    body_left = 64
    body_w = 1280 - body_left * 2          # 1152
    gap = 24
    card_w = (body_w - gap * 2) // 3       # 368
    card_top = 178
    card_h = 440                           # bottom @ y=618

    pad_x = 24
    heading_h = 28
    eyebrow_h = 16

    columns = [
        # (eyebrow, heading, body)
        ("PROBLEM",
         "[Phase 1 - what we found]",
         "[Background and reasons the work was started.\n\n"
         "[Bullet on the business situation.\n\n"
         "[Bullet on the complication that triggered the question."),
        ("SOLUTION",
         "[Phase 2 - what we explored]",
         "[We identified three possible options:\n\n"
         "[Option 1 - short description.\n\n"
         "[Option 2 - short description.\n\n"
         "[Option 3 - short description."),
        ("RECOMMENDATION",
         "[Phase 3 - what we recommend]",
         "[We recommend Option [N].\n\n"
         "[Reason 1 - why it wins.\n\n"
         "[Reason 2 - why it wins.\n\n"
         "[Next step / owner / date."),
    ]

    for i, (eyebrow, heading, body) in enumerate(columns):
        n = i + 1
        cx = body_left + i * (card_w + gap)

        # --- TREATMENT LADDER --------------------------------------------
        if n == 1:
            # Column 1 - Problem: dashed neutral, white fill, faint read.
            _add_dashed_card(
                slide, f"col-{n}-bg",
                cx, card_top, card_w, card_h,
                fill_color=WHITE, line_color=CARD_BORDER,
            )
            eyebrow_color = TEXT_DARK
            heading_color = TEXT_DARK
            body_color = TEXT_DARK

        elif n == 2:
            # Column 2 - Solution: solid soft card, thin neutral border.
            card = add_rect(
                slide, f"col-{n}-bg",
                x_px=cx, y_px=card_top, w_px=card_w, h_px=card_h,
                fill_color=CARD_BG,
            )
            card.line.color.rgb = CARD_BORDER
            card.line.width = 9525  # 1px
            eyebrow_color = TEXT_DARK
            heading_color = TEXT_DARK
            body_color = TEXT_DARK

        else:
            # Column 3 - Recommendation: BRAND_PRIMARY ground, WHITE text,
            # BRAND_ACCENT 4px top rule. This is the one accent moment.
            add_rect(
                slide, f"col-{n}-bg",
                x_px=cx, y_px=card_top, w_px=card_w, h_px=card_h,
                fill_color=BRAND_PRIMARY,
            )
            # Top accent rule - the load-bearing accent of the slide.
            add_rect(
                slide, f"col-{n}-accent-rule",
                x_px=cx, y_px=card_top, w_px=card_w, h_px=4,
                fill_color=BRAND_ACCENT,
            )
            eyebrow_color = WHITE
            heading_color = WHITE
            body_color = WHITE

        # --- TEXT STACK (identical positions across all three columns) ---
        eyebrow_y = card_top + 28
        add_text(
            slide, f"col-{n}-eyebrow", eyebrow,
            x_px=cx + pad_x, y_px=eyebrow_y,
            w_px=card_w - pad_x * 2, h_px=eyebrow_h,
            font_size_px=11, color=eyebrow_color, bold=False,
            uppercase=True, letter_spacing_px=2,
        )

        heading_y = eyebrow_y + eyebrow_h + 8
        add_text(
            slide, f"col-{n}-heading", heading,
            x_px=cx + pad_x, y_px=heading_y,
            w_px=card_w - pad_x * 2, h_px=heading_h + 24,
            font_size_px=18, color=heading_color, bold=True,
        )

        body_y = heading_y + heading_h + 32
        add_text(
            slide, f"col-{n}-body", body,
            x_px=cx + pad_x, y_px=body_y,
            w_px=card_w - pad_x * 2, h_px=card_h - (body_y - card_top) - 24,
            font_size_px=13, color=body_color, bold=False,
        )

    add_footer(slide, page_num=5)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
