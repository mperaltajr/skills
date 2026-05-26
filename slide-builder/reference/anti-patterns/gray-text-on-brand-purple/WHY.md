# gray-text-on-brand-purple — WHY NOT

**Family:** Comparison / Three-column parallel
**Verdict:** dont

## The problem

The body of the slide is a large saturated BRAND_PRIMARY (`#2D0A4E`, deep purple) rectangle carrying a 3-column comparison. The column body copy is set in light/medium gray — specifically `#94A3B8`, the old TEXT_FAINT value the helpers used to ship.

On a saturated brand-primary fill, that gray collapses into the background. The text is effectively invisible:

- On a laptop screen at 100% zoom, it reads as a faint smudge.
- Projected in a conference room, the body text disappears entirely — viewers see "a block of purple with white headers" and nothing else.
- Auto-contrast accessibility checks fail badly (well under WCAG AA for body text).

**Rule it breaks:** contrast on saturated brand fills. Text on `BRAND_PRIMARY`, `BRAND_ACCENT`, or `BRAND_PRIMARY_MID` MUST be `WHITE`. It must never be `TEXT_DARK`, `TEXT_MID`, or `TEXT_FAINT` (all of which are now aliased to near-black, and all of which produce the same kind of low-contrast failure on a saturated fill).

This anti-exemplar uses the literal hex `#94A3B8` rather than the helper constants because `TEXT_MID` and `TEXT_FAINT` are now aliased to `TEXT_DARK`. The literal hex preserves the original visual failure mode for teaching purposes.

## Why this is a teaching anti-exemplar

A user looking at this slide on screen says, "What is that block of purple doing in the middle of my slide?" — not, "Look at this comparison." The carrier (the purple panel) overwhelms the cargo (the comparison content), because the cargo is unreadable.

The failure is silent in code review: the .py file looks fine — it uses named-ish color constants, lays out three columns cleanly, has a title and footer. The bug only appears when the PNG renders. That's exactly the kind of failure pattern a `dont/` exemplar exists to catch.

## What to do instead

On any saturated brand fill (BRAND_PRIMARY / BRAND_ACCENT / BRAND_PRIMARY_MID):

- **Body copy and column text:** `WHITE`.
- **Editorial hierarchy inside the panel:** vary size and weight, or use `BRAND_ACCENT_SOFT` (a high-luminance tint) for subordinate text. Never reach for gray.
- **Footnote-style asides inside the panel:** `WHITE` + smaller size + italic, not gray.

Gray text (`TEXT_DARK` / `TEXT_MID` / `TEXT_FAINT`) belongs on the white `SLIDE_BG` area only — never on a saturated panel.

If the design genuinely needs a "quiet" tone inside a brand-primary block, use `BRAND_ACCENT_SOFT` rather than a gray. It reads as a soft tint of the brand instead of a contrast failure.
