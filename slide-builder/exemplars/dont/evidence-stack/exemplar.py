"""
Insight/Finding / evidence-stack — a finding anchored by horizontal evidence bars.

Family: Insight / Finding
Variant: Finding headline at top (hero zone), followed by 3-4 horizontal evidence
         bars that visualize relative evidence weight. Each bar has a label on the
         left, a proportional fill bar in the middle, and a short callout note on
         the right. A convergence-band-style footer restates the so-what.

Structural delta from single-finding (which uses small square bullet markers):
- The evidence is rendered as SIZED BARS, not as bullet points.
- Each evidence row has a visible QUANTITY dimension (bar width = relative weight).
- The takeaway restatement is at the BOTTOM in a BRAND_PRIMARY strip, not above.
- This layout pattern is: "finding headline UP TOP, evidence-as-bars in the middle,
  so-what strip at the bottom." Three distinct horizontal zones.

Layout shape:
- Top zone (y=152–240): Finding headline (28px bold) + subtitle + accent rule
- Mid zone (y=248–550): 4 evidence bars (each ~72px tall)
- Bottom strip (y=558–618): BRAND_PRIMARY takeaway band (italic WHITE 14px)

Rulebook citations:
- Title bottom-anchored via add_title_block (§ 1 hard constraints)
- One accent moment: BRAND_ACCENT pill/callout on the FIRST bar (the primary
  evidence row — the one the headline references). Other bars use BRAND_PRIMARY.
- Body font floor: bar labels 14px. Callout notes 14px. Strip text 14px.
- Bold ceiling: title (1) + finding headline bold (1) = 2. ≤5 ceiling honored.
- No fabricated numbers — bars use placeholder widths (relative percentages
  expressed as fractions of the bar zone, not specific dollar/% figures).
- Reading order: finding headline first (top), evidence stack second (mid),
  so-what strip last (bottom). ✓
- Takeaway in the top half of body zone: headline at y≈168 is in the top third. ✓
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

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
        title="[Finding headline: the insight this evidence proves]",
        subtitle="[Sub-headline: what was measured, over what period]",
    )

    # ── Finding hero zone ──
    # Bold summary claim, larger than the title block but narrower than full width.
    # This is the "restate the headline" zone for eyes that skip the title.
    add_text(
        slide, "finding-hero",
        "[<strong>Key qualifier</strong>: one-sentence restatement of the finding at scale]",
        x_px=64, y_px=156, w_px=900, h_px=60,
        font_size_pt=16, color=TEXT_DARK, bold=False,
        emphasis_color=BRAND_PRIMARY,
    )

    # One accent moment: BRAND_ACCENT 48px rule under the finding hero
    add_rect(
        slide, "finding-accent-rule",
        x_px=64, y_px=218, w_px=48, h_px=4,
        fill_color=BRAND_ACCENT,
    )

    # ── Evidence bars zone ──
    # Four rows. Each row: category label (left) | bar fill (proportional) | callout note (right).
    # Bar zone: x=240→880 (640px wide). Label zone: x=64→230. Note zone: x=890→1216.
    bar_x = 240
    bar_track_w = 640    # full track width (100% = full bar)
    bar_track_h = 8      # bar height
    bar_zone_top = 240
    row_h = 78

    # Placeholder proportions — four evidence items with relative weights.
    # Do NOT use real numbers. Use relative fractions.
    evidence_rows = [
        ("[Evidence category A]", 0.90, "[Finding note for A: what this tells us]"),
        ("[Evidence category B]", 0.65, "[Finding note for B: what this tells us]"),
        ("[Evidence category C]", 0.45, "[Finding note for C: what this tells us]"),
        ("[Evidence category D]", 0.30, "[Finding note for D: what this tells us]"),
    ]

    for i, (label, proportion, note) in enumerate(evidence_rows):
        n = i + 1
        ry = bar_zone_top + i * row_h

        # Category label
        add_text(
            slide, f"bar-{n}-label", label,
            x_px=64, y_px=ry + 4,
            w_px=168, h_px=bar_track_h + 16,
            font_size_px=14, color=TEXT_MID, bold=False, align="right",
        )

        # Bar track (background)
        add_rect(
            slide, f"bar-{n}-track",
            x_px=bar_x, y_px=ry + 10, w_px=bar_track_w, h_px=bar_track_h,
            fill_color=CARD_BORDER,
        )

        # Bar fill — first row uses BRAND_ACCENT (the accent moment); rest use BRAND_PRIMARY
        bar_fill_color = BRAND_ACCENT if n == 1 else BRAND_PRIMARY
        fill_w = int(bar_track_w * proportion)
        add_rect(
            slide, f"bar-{n}-fill",
            x_px=bar_x, y_px=ry + 10, w_px=fill_w, h_px=bar_track_h,
            fill_color=bar_fill_color,
        )

        # Callout note to the right of the bar track
        add_text(
            slide, f"bar-{n}-note", note,
            x_px=bar_x + bar_track_w + 16, y_px=ry,
            w_px=1216 - (bar_x + bar_track_w + 16), h_px=50,
            font_size_px=14, color=TEXT_DARK, bold=False,
        )

        # Small proportion label (placeholder: "[HIGH]", "[MED]", etc.)
        proportion_labels = ["[HIGH]", "[MED-HIGH]", "[MEDIUM]", "[LOWER]"]
        add_text(
            slide, f"bar-{n}-pct-label", proportion_labels[i],
            x_px=bar_x + fill_w + 6, y_px=ry + 4,
            w_px=80, h_px=20,
            font_size_px=11, color=TEXT_FAINT, bold=False,
        )

    # ── Bottom convergence band ──
    # Full-width BRAND_PRIMARY strip. White italic 14px so-what summary.
    band_y = 558
    band_h = 60
    add_rect(
        slide, "takeaway-band",
        x_px=64, y_px=band_y, w_px=1152, h_px=band_h,
        fill_color=BRAND_PRIMARY,
    )
    add_text(
        slide, "takeaway-text",
        "[So-what: what this evidence means for the audience, and what it implies they should do]",
        x_px=80, y_px=band_y, w_px=1120, h_px=band_h,
        font_size_px=14, color=WHITE, italic=True, bold=False,
        align="center", anchor="middle",
    )

    add_footer(slide, page_num=3)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
