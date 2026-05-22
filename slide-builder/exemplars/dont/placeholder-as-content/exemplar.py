"""
ANTI-EXEMPLAR — placeholder-as-content.

The slide looks designed. It has a title, a chart area, a takeaway panel, a
footer. The chrome is fine. But every single text slot still says its own
slot name. "Action Title" is the title. "Takeaway / Insight Panel" is the
panel header. "Bullet point – text description" is the bullet. The deck
shipped with the template's instructional placeholders left in as content.

This is the most teachable failure in the source deck because it is the one
that hides best: the slide passes a thumbnail glance, passes a "is the
hierarchy right?" check, passes a "is the palette on-brand?" check. It
fails the only check that matters — "does this slide say anything?"

Family: Chart + right takeaway panel (a `chart-right-takeaway` variant).
Rule violated: REFERENCE/rules.md — every text slot must carry a CLAIM, not
its own slot label. The action title must state the action. The takeaway
must state the takeaway. Bullets must list evidence, not announce that
bullets exist.

What to do instead: see `do/chart-right-takeaway/exemplar.py`. The same
layout with real placeholder copy — `[Action title: state the so-what]`,
`[$X.XM]`, `[bucket A] — [supporting evidence]` — makes the slot's role
visible while still being obviously placeholder, so the consultant cannot
ship it by accident.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_DARK, TEXT_MID,
    CARD_BG, CARD_BORDER,
)


# Anti-exemplar local colors — the source deck used a mint-green chart panel
# and a cool-grey takeaway panel. We re-create that combo (off-brand) so the
# failure stays visually obvious; brand-palette constants stay above for the
# title/footer chrome.
from pptx.dml.color import RGBColor
MINT_PANEL = RGBColor(0xDF, 0xF7, 0xEE)
GREY_PANEL = RGBColor(0xD7, 0xD8, 0xE0)
GREY_HEADER = RGBColor(0xC8, 0xCA, 0xD4)
BUBBLE_BLUE = RGBColor(0x1E, 0xA8, 0xE8)


def build():
    prs, slide = new_slide()

    # Title block — note that the title literally says "Action Title".
    # This is the failure: the slot label was never replaced with a claim.
    add_title_block(
        slide,
        title="Action Title",
        subtitle="Sub-headline",
    )

    # ── Chart panel (left, mint background) ──
    # Off-brand mint fill — chart area announces itself as "the chart area"
    # rather than disappearing into the page. Decorative panel, no insight.
    chart_x, chart_y, chart_w, chart_h = 64, 168, 800, 472
    add_rect(slide, "chart-panel-bg",
             x_px=chart_x, y_px=chart_y, w_px=chart_w, h_px=chart_h,
             fill_color=MINT_PANEL)

    # Chart title — placeholder literal kept in.
    add_text(slide, "chart-title", "Chart Title¹, [Unit]",
             x_px=chart_x + 16, y_px=chart_y + 14, w_px=400, h_px=24,
             font_size_px=14, color=TEXT_DARK, bold=True)

    # Legend — placeholder series names, no actual meaning.
    add_text(slide, "legend-aa", "● AA",
             x_px=chart_x + chart_w - 110, y_px=chart_y + 14, w_px=44, h_px=20,
             font_size_px=12, color=BRAND_PRIMARY)
    add_text(slide, "legend-bb", "● BB",
             x_px=chart_x + chart_w - 60, y_px=chart_y + 14, w_px=44, h_px=20,
             font_size_px=12, color=BUBBLE_BLUE)

    # Axis labels — SWAPPED in the source deck. "X Axis Title" is on the Y
    # position (vertical left); "Y-Axis Title" is on the X position (bottom).
    # We reproduce the swap because it is part of the same disease: text
    # treated as decoration, not as a label that means something.
    add_text(slide, "axis-label-y-but-says-x", "X Axis Title",
             x_px=chart_x + 16, y_px=chart_y + 44, w_px=120, h_px=20,
             font_size_px=12, color=TEXT_DARK)
    add_text(slide, "axis-label-x-but-says-y", "Y-Axis Title",
             x_px=chart_x + chart_w // 2 - 60, y_px=chart_y + chart_h - 28,
             w_px=120, h_px=20,
             font_size_px=12, color=TEXT_DARK)

    # Y-axis tick numbers (decorative — chart has no real data).
    for i, val in enumerate([60, 40, 20, 0]):
        add_text(slide, f"y-tick-{val}", str(val),
                 x_px=chart_x + 36, y_px=chart_y + 78 + i * 90,
                 w_px=24, h_px=18,
                 font_size_px=11, color=TEXT_MID, align="right")

    # X-axis tick numbers.
    for i, val in enumerate(["0.0", "0.2", "0.4", "0.6", "0.8", "1.0"]):
        add_text(slide, f"x-tick-{i}", val,
                 x_px=chart_x + 68 + i * 130, y_px=chart_y + chart_h - 52,
                 w_px=40, h_px=16,
                 font_size_px=11, color=TEXT_MID, align="center")

    # Decorative "bubbles" — single-color, no encoded meaning. Picked
    # arbitrarily to make the chart panel look populated.
    bubbles = [
        (chart_x + 80,  chart_y + 380, 18),
        (chart_x + 165, chart_y + 195, 36),
        (chart_x + 195, chart_y + 320, 28),
        (chart_x + 245, chart_y + 230, 24),
        (chart_x + 335, chart_y + 260, 48),
        (chart_x + 365, chart_y + 320, 22),
        (chart_x + 410, chart_y + 270, 30),
        (chart_x + 545, chart_y + 330, 28),
        (chart_x + 610, chart_y + 365, 18),
        (chart_x + 680, chart_y + 395, 22),
    ]
    for i, (bx, by, r) in enumerate(bubbles):
        # Use a rectangle with circle shape via add_shape would be nicer, but
        # add_rect is what's in helpers. Use square proxy — the failure isn't
        # about the bubbles; they're set dressing.
        add_rect(slide, f"bubble-{i}",
                 x_px=bx, y_px=by, w_px=r, h_px=r,
                 fill_color=BUBBLE_BLUE)

    # ── Takeaway panel (right, dead grey) ──
    # This is the heart of the failure. The panel header literally reads
    # "Takeaway / Insight Panel" — the slot label, not the takeaway.
    panel_x, panel_y, panel_w, panel_h = 896, 168, 320, 472
    add_rect(slide, "takeaway-panel-bg",
             x_px=panel_x, y_px=panel_y, w_px=panel_w, h_px=panel_h,
             fill_color=GREY_PANEL)
    # Header stripe — even uglier, also using grey-on-grey.
    add_rect(slide, "takeaway-panel-header",
             x_px=panel_x, y_px=panel_y, w_px=panel_w, h_px=64,
             fill_color=GREY_HEADER)
    add_text(slide, "takeaway-panel-header-text",
             "Takeaway / Insight Panel",
             x_px=panel_x + 16, y_px=panel_y + 16, w_px=panel_w - 32, h_px=32,
             font_size_px=15, color=TEXT_DARK, bold=True, align="center")

    # Panel body — the so-what restates that there is supposed to be a
    # so-what here.
    add_text(slide, "takeaway-body",
             "Concise text on “so what”. Explains takeaway",
             x_px=panel_x + 20, y_px=panel_y + 120, w_px=panel_w - 40, h_px=44,
             font_size_px=13, color=TEXT_DARK)

    # Bullets — every bullet announces that it is a bullet.
    bullet_y = panel_y + 190
    for i in range(3):
        add_text(slide, f"bullet-marker-{i}", "•",
                 x_px=panel_x + 20, y_px=bullet_y + i * 40,
                 w_px=12, h_px=18,
                 font_size_px=13, color=TEXT_DARK)
        add_text(slide, f"bullet-text-{i}",
                 "<strong>Bullet point –</strong> text description",
                 x_px=panel_x + 36, y_px=bullet_y + i * 40,
                 w_px=panel_w - 56, h_px=20,
                 font_size_px=13, color=TEXT_DARK)

    # DRAFT tag in the top invariant zone (violates invariant-zone-chrome
    # rule from MEMORY.md — top zone holds content, not status flags).
    add_text(slide, "draft-tag", "DRAFT",
             x_px=608, y_px=4, w_px=64, h_px=16,
             font_size_px=11, color=RGBColor(0xC4, 0x1E, 0x1E),
             italic=True, align="center")

    add_footer(slide, page_num=4)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
