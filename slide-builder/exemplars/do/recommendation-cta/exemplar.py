"""
Slide 3 — Option A: Hero CTA band + 3 sub-ask cards (horizontal row).

Page type: Recommendation / CTA (designer-brief §4 — "the ask is the visual
hero. Dark panel dominant. Sub-asks clearly subordinate.").

Layout family: hero-panel + supporting cards (visual-treatment-library
"Two-column with insight panel" + closing-CTA recipe).

Rules honored:
- Title bottom-anchored at y=100 via add_title_block. Title is 30 chars
  (well under the 90-char cap).
- One accent moment: the 6px BRAND_ACCENT strip on the hero's left edge.
  Sub-ask cards use the same accent at 3px width (subordinate weight —
  reads as the same "moment" extended).
- Bold discipline (§6): bold runs are (1) title, (2) primary ask hero text,
  (3-5) three card numerals/headings combined per card. Eyebrows + body
  are NEVER bold. Total bold elements ≤5 distinct visual emphases.
- Body font floor: all body text ≥14px (eyebrows 11px, italic meta 12px).
- Brand palette only — no raw hex literals.
- Footer = add_footer(slide, page_num=3). No CONFIDENTIAL / client name /
  signature / personal email anywhere.
- Hero band fills ~21% of canvas height; cards fill remainder — no empty
  bottom (content runs to ~y=612, just above footer).
- Insertion order = paint order: bg → accent → text.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()

    # === Title block (bottom-anchored at y=100) ===
    add_title_block(
        slide,
        title="Three Actions to Close the Gap",
        subtitle=("The gap is closeable — but only with active executive "
                  "sponsorship in the next few weeks."),
    )

    # === Hero PRIMARY ASK panel — the single focal point ===
    pa_x, pa_y, pa_w, pa_h = 64, 156, 1280 - 128, 152
    add_rect(slide, "primary-ask-bg", pa_x, pa_y, pa_w, pa_h, BRAND_PRIMARY)
    # 6px BRAND_ACCENT strip — the ONE accent moment on the slide
    add_rect(slide, "primary-ask-accent", pa_x, pa_y, 6, pa_h, BRAND_ACCENT)

    add_text(
        slide, "primary-ask-label", "THE ASK",
        x_px=pa_x + 32, y_px=pa_y + 22, w_px=pa_w - 64, h_px=16,
        font_size_px=11, color=BRAND_ACCENT_SOFT,
        uppercase=True, letter_spacing_px=3,
    )
    add_text(
        slide, "primary-ask-text",
        "[Primary ask — one declarative sentence stating the recommendation and the headline outcome.]",
        x_px=pa_x + 32, y_px=pa_y + 48, w_px=pa_w - 64, h_px=88,
        font_size_px=26, color=WHITE, bold=True,
    )

    # === Sub-ask cards row — 3 equal-width supporting cards ===
    sa_label_y = 320
    sa_y = 344
    sa_h = 256
    sa_gap = 18
    sa_w = (pa_w - 2 * sa_gap) // 3

    add_text(
        slide, "sub-ask-label", "WHAT EACH ACTION DELIVERS",
        x_px=pa_x, y_px=sa_label_y, w_px=400, h_px=14,
        font_size_px=11, color=TEXT_MID,
        uppercase=True, letter_spacing_px=2,
    )

    sub_data = [
        (
            "1",
            "[Sub-ask 1 heading]",
            "[One-sentence description of what this sub-ask is.]",
            "[Outcome or value this sub-ask delivers.]",
            "[Deep-dive reference]",
        ),
        (
            "2",
            "[Sub-ask 2 heading]",
            "[One-sentence description of what this sub-ask is.]",
            "[Outcome or value this sub-ask delivers.]",
            "[Deep-dive reference]",
        ),
        (
            "3",
            "[Sub-ask 3 heading]",
            "[One-sentence description of what this sub-ask is.]",
            "[Outcome or value this sub-ask delivers.]",
            "[Deep-dive reference]",
        ),
    ]

    for i, (num, heading, body, value, meta) in enumerate(sub_data):
        n = i + 1
        sx = pa_x + i * (sa_w + sa_gap)

        # Card background
        card = add_rect(slide, f"sub-ask-{n}-bg", sx, sa_y, sa_w, sa_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # 3px subordinate accent on left edge
        add_rect(slide, f"sub-ask-{n}-accent", sx, sa_y, 3, sa_h, BRAND_ACCENT)

        # Numeral
        add_text(
            slide, f"sub-ask-{n}-num", num,
            x_px=sx + 22, y_px=sa_y + 20, w_px=44, h_px=46,
            font_size_px=36, color=BRAND_PRIMARY, bold=True,
        )
        # Heading
        add_text(
            slide, f"sub-ask-{n}-heading", heading,
            x_px=sx + 22, y_px=sa_y + 74, w_px=sa_w - 44, h_px=28,
            font_size_px=20, color=BRAND_PRIMARY, bold=True,
        )
        # Body description
        add_text(
            slide, f"sub-ask-{n}-body", body,
            x_px=sx + 22, y_px=sa_y + 108, w_px=sa_w - 44, h_px=48,
            font_size_px=14, color=TEXT_DARK,
        )
        # Value line (savings) — emphasized via inline strong, not full-bold
        add_text(
            slide, f"sub-ask-{n}-value", value,
            x_px=sx + 22, y_px=sa_y + 162, w_px=sa_w - 44, h_px=44,
            font_size_px=14, color=TEXT_DARK,
            emphasis_color=BRAND_PRIMARY,
        )
        # Meta (italic, bottom-anchored)
        add_text(
            slide, f"sub-ask-{n}-meta", meta,
            x_px=sx + 22, y_px=sa_y + sa_h - 32, w_px=sa_w - 44, h_px=20,
            font_size_px=12, color=TEXT_MID, italic=True,
        )

    # === Footer (invariant chrome only) ===
    add_footer(slide, page_num=3)

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "option_A.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
