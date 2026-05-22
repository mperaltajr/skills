"""
Comparison / Three-column parallel — gray body text on a saturated BRAND_PRIMARY
fill. ANTI-EXEMPLAR: the body text is effectively invisible.

Family: Comparison / Three-column parallel
Verdict: dont

What this reproduces
--------------------
A confirmed real-build failure: a slide rendered with a large BRAND_PRIMARY
block in the body zone, and body copy on top of it set in light/medium gray
(the old TEXT_FAINT value, `#94A3B8`). On a dark purple fill, that gray reads
as a single muddy tone — the words effectively disappear, especially when the
slide is projected.

The current `twins/helpers.py` has already aliased `TEXT_FAINT` (and `TEXT_MID`)
to `TEXT_DARK` precisely because of this failure mode. To preserve the failure
visually for teaching purposes, this file uses ONE literal hex value
(`RGBColor(0x94, 0xA3, 0xB8)` — the old TEXT_FAINT) for the body text on the
purple block. Every other color is a named brand constant.

Rules broken
------------
- Contrast: text on a saturated brand fill must be WHITE. Never TEXT_DARK /
  TEXT_MID / TEXT_FAINT (all near-black or gray) on BRAND_PRIMARY /
  BRAND_ACCENT / BRAND_PRIMARY_MID.

What to do instead
------------------
- Body copy on BRAND_PRIMARY / BRAND_ACCENT / BRAND_PRIMARY_MID must be WHITE.
- If editorial hierarchy is needed inside a saturated panel, use WHITE +
  BRAND_ACCENT_SOFT (a high-luminance tint), or size/weight, NOT a gray.
- Gray text belongs on the SLIDE_BG (white) area only.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from pptx.dml.color import RGBColor

from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_ACCENT,
    TEXT_DARK, TEXT_MID,
    WHITE,
)

# The failure-mode color we're reproducing. This is the OLD value of
# TEXT_FAINT, before it was aliased to TEXT_DARK in helpers.py. Used here
# verbatim so the visible failure (gray-on-purple) survives the alias.
OLD_TEXT_FAINT_GRAY = RGBColor(0x94, 0xA3, 0xB8)


def build():
    prs, slide = new_slide()

    # === Title block (placeholder content only) ===
    add_title_block(
        slide,
        title="[Headline placeholder]",
        subtitle="[Sub-headline: comparison setup placeholder]",
    )

    # === Body: one big saturated BRAND_PRIMARY block filling most of the
    # body zone, carrying a 3-column comparison.
    body_x = 64
    body_y = 156
    body_w = 1280 - 128
    body_h = 480

    add_rect(
        slide, "body-block-bg",
        x_px=body_x, y_px=body_y, w_px=body_w, h_px=body_h,
        fill_color=BRAND_PRIMARY,
    )

    # Column headers — set in WHITE (this part is fine in isolation).
    col_w = body_w // 3
    headers = [
        "[Column A header]",
        "[Column B header]",
        "[Column C header]",
    ]
    for i, h in enumerate(headers):
        cx = body_x + i * col_w
        add_text(
            slide, f"col-{i+1}-header", h,
            x_px=cx + 24, y_px=body_y + 32, w_px=col_w - 48, h_px=28,
            font_size_pt=16, color=WHITE, bold=True,
        )

    # Column body copy — THE FAILURE.
    # Each column gets ~4 lines of placeholder body text set in the old
    # TEXT_FAINT gray. On the saturated purple fill, this reads as mud.
    body_lines = [
        ("[Column A body line 1 — placeholder copy]\n"
         "[Column A body line 2 — placeholder copy]\n"
         "[Column A body line 3 — placeholder copy]\n"
         "[Column A body line 4 — placeholder copy]"),
        ("[Column B body line 1 — placeholder copy]\n"
         "[Column B body line 2 — placeholder copy]\n"
         "[Column B body line 3 — placeholder copy]\n"
         "[Column B body line 4 — placeholder copy]"),
        ("[Column C body line 1 — placeholder copy]\n"
         "[Column C body line 2 — placeholder copy]\n"
         "[Column C body line 3 — placeholder copy]\n"
         "[Column C body line 4 — placeholder copy]"),
    ]
    for i, txt in enumerate(body_lines):
        cx = body_x + i * col_w
        add_text(
            slide, f"col-{i+1}-body", txt,
            x_px=cx + 24, y_px=body_y + 80,
            w_px=col_w - 48, h_px=body_h - 120,
            font_size_px=14, color=OLD_TEXT_FAINT_GRAY,
        )

    # Faint footnote-style line at the bottom of the block — also in gray
    # on purple, reinforcing the failure pattern.
    add_text(
        slide, "block-footnote",
        "[Footnote-style supporting line — placeholder copy that is also unreadable on the purple fill]",
        x_px=body_x + 24, y_px=body_y + body_h - 36,
        w_px=body_w - 48, h_px=24,
        font_size_px=12, color=OLD_TEXT_FAINT_GRAY, italic=True,
    )

    # Note: TEXT_DARK and TEXT_MID are now aliased to near-black in helpers,
    # so they too would fail on BRAND_PRIMARY. The OLD_TEXT_FAINT_GRAY value
    # preserves the original visual symptom (low-contrast gray-on-purple).
    _ = TEXT_DARK, TEXT_MID, BRAND_ACCENT  # keep imports honest

    add_footer(slide, page_num=1)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
