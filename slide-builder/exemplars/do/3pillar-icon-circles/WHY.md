# 3pillar-icon-circles

**What this is.** Three vertical cards laid out as parallel pillars (Think / Argue / Build pattern), each led by a circular BRAND_PRIMARY icon container with a WHITE glyph.

**What makes it strong.**
- **Icon containers are CIRCLES, not squares.** Per `designer-brief § 5b` (CRITICAL rule that overrides earlier drafts that proposed BRAND_ACCENT_SOFT squares): "The background MUST be a circle, not a square or rectangle." This exemplar replaces an earlier failed pattern (peach squares) with the corrected pattern.
- **Same color across all three circles.** MECE rule: when three items are parallel, the containers MUST share one color. NEVER use a different bright color per pillar — that fragments the family read. All three use BRAND_PRIMARY ground + WHITE icon.
- **NEVER use BRAND_ACCENT / BRAND_ACCENT_SOFT for icon circles.** That burns the one accent moment on a container. Here the accent lives only on the title's brand-rule via `add_title_block`. Cards are CARD_BG with neutral CARD_BORDER 1px outlines.
- **88px circle diameter, 52px icon (~60% of circle).** Centered geometrically via `circle_cx - circle_d // 2`.
- **Bold discipline = 4.** Title + 3 card headings. Eyebrows (11px uppercase letter-spaced BRAND_PRIMARY) NOT bold; bodies (14px TEXT_MID) NOT bold; signature lines (12px italic TEXT_FAINT) NOT bold.
- **`add_icon_from_library`** with named glyphs (lightbulb / speech / package) — uses the library API, not raw unicode.

**Reach for this when.** Three parallel categories that should read as a single integrated family — three pillars of a method, three phases of a process, three branches of a product. Avoid for things that are NOT parallel (e.g., problem/solution/outcome → use a flow, not pillars).

**Patterns to copy.** Circle geometry math; `add_icon_from_library` with named icons; the eyebrow → heading → body → signature 4-line card vertical rhythm; `align="center"` consistently within each card.
