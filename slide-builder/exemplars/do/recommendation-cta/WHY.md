# recommendation-cta

**What this is.** A closing-action slide where the primary ask is the visual hero (top BRAND_PRIMARY band) and three sub-asks sit clearly subordinate as a row of supporting cards.

**What makes it strong.**
- **Hero ASK band dominates.** Top-of-body BRAND_PRIMARY rectangle (1152w × 152h) carrying the primary ask in 26px bold WHITE. An "THE ASK" eyebrow in 11px BRAND_ACCENT_SOFT uppercase sits above the ask line. The ask is unambiguous — it's the loudest thing on the slide.
- **One extended accent moment.** A 6px BRAND_ACCENT strip on the LEFT EDGE of the hero band, and a 3px BRAND_ACCENT strip on the left edge of each sub-ask card. Same accent, different weights — reads as the same "moment" extended across the supporting layer, not three new accents.
- **Three sub-ask cards, parallel structure.** Each card: numeral (36px BRAND_PRIMARY bold) → heading (20px BRAND_PRIMARY bold) → body (14px TEXT_DARK) → value line (14px TEXT_DARK with `emphasis_color=BRAND_PRIMARY`) → meta (12px TEXT_MID italic, bottom-anchored). CARD_BG fill + 1px CARD_BORDER outline.
- **Bold discipline = 5 max.** Title + primary ask + 3 card headings = 5. Numerals are bold but read as part of the heading line. Eyebrows, bodies, values, metas all NOT bold.
- **No personal contact info, no CONFIDENTIAL.** Footer = `add_footer(slide, page_num=3)` only. Cross-references to deeper-dive slides ("Deep dive: Slide D") live in the italic meta line at the bottom of each card.
- **Content runs to ~y=612, just above the footer.** No empty bottom zone — the slide commits to the cards being the body.

**Reach for this when.** Recommendation / closing-CTA / "the ask" slide where one primary ask has 2-4 supporting sub-asks. Editorial emphasis is "the ask dominates" or "one clear CTA."

**Patterns to copy.** Hero band + accent left-strip + sub-ask card row geometry; the "shared accent extended" technique (6px on hero, 3px on supporting cards = ONE moment, not four); meta italic line bottom-anchored inside each card; numeric values emphasized via inline `<strong>` + `emphasis_color`, never full-bold values.
