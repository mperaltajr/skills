# hero-kpi-tile

**What this is.** A hero stat at editorial scale (96px BRAND_PRIMARY) anchors the top half; a compact 3-row horizontal bar strip sits below as supporting evidence. The number IS the slide — the chart proves it.

**What makes it strong.**
- **Hero numeral at 96px BRAND_PRIMARY bold.** Single number, single color, no decoration. Eyebrow above (11px BRAND_PRIMARY uppercase letter-spaced) tells the reader what the number measures.
- **Hero supporting claim to the RIGHT of the numeral.** Two-column hero zone — numeral left (560w), claim right (552w). 18px TEXT_DARK with inline `<strong>` for the load-bearing $ values, `emphasis_color=BRAND_PRIMARY`.
- **Compact 3-row bar strip below.** Each row: 200w label slot + bar plot region + 84w value label. Faint CARD_BORDER track behind each bar (1px tall, 2px stroke at the bar's vertical center). Bars use TEXT_MID / BRAND_PRIMARY_MID / BRAND_ACCENT — a 3-tier brand-family ramp.
- **One accent moment = the ONE accent bar.** Only the load-bearing row (the actual outcome) is BRAND_ACCENT; the comparison rows are neutral or BRAND_PRIMARY_MID. The value label for that row is also BRAND_ACCENT + bold; all other value labels TEXT_DARK non-bold.
- **No legend.** Each row is direct-labeled (label on the left, value on the right of the bar). Legends are reserved for multi-series charts where direct-labeling won't fit.
- **Bold ≤ 5.** Title + hero numeral + supporting claim heading + accent-bar value label = 4.

**Reach for this when.** A single number IS the so-what — the gap, the shortfall, the delta, the magnitude. Especially when the supporting evidence is 2-4 comparable values that benefit from a small bar strip.

**Patterns to copy.** 96px numeral as the hero element (NEVER underline or decorate — the size carries it); two-column hero zone (numeral left, claim right); the "3-tier brand-family bar ramp" (TEXT_MID → BRAND_PRIMARY_MID → BRAND_ACCENT) with accent reserved for the one load-bearing bar.
