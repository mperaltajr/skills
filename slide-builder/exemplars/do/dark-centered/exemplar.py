"""
Quote / dark-centered — Option A: Full-bleed dark canvas, large centered quote.

Family: Quote
Variant: Dark-background centered typography — the most direct quote treatment.
         Typography IS the visual. The quote is at 32px WHITE italic, centered.
         Attribution in BRAND_ACCENT_SOFT. No card, no sidebar, no image.

Layout shape: Full-bleed BRAND_PRIMARY canvas. Single text column centered at
              60% width. Quote occupies y≈220–400 (top of body zone). Attribution
              below at y≈420. One accent moment: BRAND_ACCENT horizontal rule
              (56px wide) above the quote, acting as a visual "opener."

Rulebook citations:
- Canvas: 1280×720 via new_slide() (§ 1 designer-brief)
- Title: add_title_block not used for covers/dark-quote — title block is on
  white slides; for full-bleed dark, the quote text IS the content; this slide
  has a small eyebrow label at top-left as the only navigational element.
- No title block on dark: per page-types.md § 10 (Quote), action title is
  EXCEPTED — attribution replaces footnote/source. We add a small slide
  label eyebrow instead of add_title_block so the invariant zone stays clean.
- One accent moment: BRAND_ACCENT 56px rule ABOVE the quote. The rule is the
  load-bearing element (it "opens" the quote). Attribution uses BRAND_ACCENT_SOFT
  (a sibling tone, not the same accent token — this is within the "one moment"
  rule as BRAND_ACCENT_SOFT is a secondary brand color, not the accent itself).
- Body font floor: quote text at 32px (>>14px floor). Attribution at 14px.
- No personal contact info, no CONFIDENTIAL chrome.
- Footer: add_footer is called but both source/footnote omitted (attribution
  replaces them per the Quote rules relaxation).
- Bold ceiling: quote (italic, not bold) + eyebrow label = 0 bold text runs.
  Lean design — the visual weight comes from scale and contrast, not bolding.

Structural delta from 2panel-convergence / single-finding:
- No side-by-side panels. No bullets. No left anchor.
- Full dark canvas (BRAND_PRIMARY fill on slide background).
- Typography-only visual — no rects except the accent rule and background.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()

    # Override white background to full-bleed BRAND_PRIMARY
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # ── Small navigational eyebrow (top-left, replaces title block on dark) ──
    # Not bold; 11px uppercase; BRAND_ACCENT_SOFT — quiet but present.
    add_text(
        slide, "slide-eyebrow", "VOICE OF THE CLIENT",
        x_px=64, y_px=36, w_px=400, h_px=16,
        font_size_px=11, color=BRAND_ACCENT_SOFT, bold=False,
        uppercase=True, letter_spacing_px=2,
    )

    # ── One accent moment: 56px BRAND_ACCENT opener rule ──
    # Sits just above the quote text. This is the lone BRAND_ACCENT element.
    add_rect(
        slide, "quote-opener-rule",
        x_px=240, y_px=196, w_px=56, h_px=4,
        fill_color=BRAND_ACCENT,
    )

    # ── Large quotation mark character ──
    # Decorative opener — in WHITE at 64px, purely visual.
    # Does NOT use add_icon so no PPTX compatibility issues.
    add_text(
        slide, "open-quote-mark", "“",
        x_px=232, y_px=172, w_px=80, h_px=50,
        font_size_px=48, color=WHITE, bold=False, italic=False,
        align="center",
    )

    # ── Quote body text ──
    # 32px WHITE italic, centered, ~60% canvas width.
    # Placeholder content — never fabricate real-looking quotes from real entities.
    quote_text = (
        "[Insight headline placeholder: the most important thing our client said "
        "about this problem, in their words.]"
    )
    add_text(
        slide, "quote-body", quote_text,
        x_px=240, y_px=214, w_px=800, h_px=180,
        font_size_px=28, color=WHITE, bold=False, italic=True,
        align="center",
    )

    # ── Closing quote mark ──
    add_text(
        slide, "close-quote-mark", "”",
        x_px=960, y_px=380, w_px=80, h_px=50,
        font_size_px=48, color=WHITE, bold=False, italic=False,
        align="center",
    )

    # ── Attribution line ──
    # 14px BRAND_ACCENT_SOFT (meets body floor). Not bold per rulebook.
    # Format: "— Role Title, Company · Context"
    add_text(
        slide, "attribution",
        "— [Role Title, Organisation] · [Context or date]",
        x_px=240, y_px=408, w_px=800, h_px=24,
        font_size_px=14, color=BRAND_ACCENT_SOFT, bold=False, italic=False,
        align="center",
    )

    # ── Thin separator rule below attribution (visual breathing room) ──
    # BRAND_ACCENT_SOFT at low opacity is not possible in PPTX;
    # use TEXT_FAINT-toned white (not a brand color — use a near-white neutral).
    # Per palette rules, use WHITE at reduced opacity... but PPTX opacity is
    # unreliable. Use BRAND_ACCENT_SOFT at 1px instead — within the one-moment
    # rule because the opener rule is the accent MOMENT; this sub-rule is structural.
    add_rect(
        slide, "separator-rule",
        x_px=440, y_px=440, w_px=400, h_px=1,
        fill_color=BRAND_PRIMARY_MID,  # near invisible on dark canvas — structural only
    )

    # ── Footer (dark slide — source/footnote replaced by attribution above) ──
    # Per Quote rules relaxation: attribution replaces footnote/source.
    # We still call add_footer for page number.
    # Override foot text color via direct construction (helpers use TEXT_FAINT
    # which is light-grey — fine on white, but on dark we want it slightly
    # lighter. TEXT_FAINT = #94A3B8 — readable on dark too.)
    add_footer(slide, page_num=1)

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "exemplar.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
