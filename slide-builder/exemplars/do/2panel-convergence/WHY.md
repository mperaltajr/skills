# 2panel-convergence

**What this is.** Symmetric two-column comparison where both panels carry equal visual weight and a BRAND_PRIMARY convergence band at the bottom delivers the punchline.

**What makes it strong.**
- **Equal weight panels.** Two panels with identical width, identical typography rhythm (11px uppercase TEXT_MID label → 22px bold TEXT_DARK heading → 14px TEXT_MID body). Neither side is favored — the contrast IS the argument.
- **Hairline vertical divider.** A 2px CARD_BORDER rectangle centered in the gutter, inset 24px top and bottom. Neutral chrome — does no semantic work, just visually separates the panels.
- **Convergence band = the climax.** A full-width BRAND_PRIMARY band (`add_convergence()` helper) sits below both panels carrying the "both panels collapse to this" sentence in WHITE italic. The convergence band IS the slide's takeaway.
- **One accent moment.** The BRAND_ACCENT brand-rule under the title (emitted by `add_title_block`). The convergence band stays BRAND_PRIMARY, NOT accent — accent is preserved for the title rule alone. Bold count = title + 2 panel headings = 3, well under the 5 ceiling.
- **Title bottom-anchored** via `add_title_block(title=..., subtitle=..., brand_rule_w=56)`.
- **Footer = page number only** via `add_footer(slide, page_num=3)`. No chrome leaks.

**Reach for this when.** Two failure modes / two options / two strategies that share a root cause or land at the same conclusion. The slide's argument is "these are different paths to the same problem" or "both roads lead here."

**Patterns to copy.** Panel-width arithmetic with explicit gutter (`(1280 - 128 - gutter) // 2`); the `add_convergence()` helper for the punchline band; uppercase eyebrow labels with `letter_spacing_px=1` and TEXT_MID (NOT BRAND_PRIMARY — eyebrows on neutral panels stay neutral).
