# Legacy path-a / path-b corpus — notes for future Claude

**TL;DR:** the slide-builder skill contains a large legacy corpus from two
deprecated build paths (catalog + skeletons). The code is not actively
routed for new deck builds — Path-C (custom python-pptx per slide via
parallel agents + designer-brief rulebook) is the only production path.
BUT the corpus is valuable for **QC work, exemplar lookup, and pattern
recognition**, so it stays on disk. This note explains what's there, why
it's there, and how to use it.

---

## What got deprecated and why

Path-c won a 3-path empirical test on 2026-05-18 (FedEx Intro to Slide Lab brief).
Path-a (catalog selector + composer) and path-b (skeletons + patches) both
produced structurally-correct-but-content-misaligned slides on the test brief.
Path-c produced consistently strong output once the design rulebook was inlined.
Specs 1-7 since then have raised path-c's quality further. We're committed to
path-c as the only build path going forward.

See `slide-builder/SKILL.md` Path-C section for the production architecture.

---

## What the legacy corpus contains

### Path-A — Catalog (the larger corpus)

Located in `~/.claude/skills/slide-builder/`:

| Asset | What it is | Why it's useful for QC |
|---|---|---|
| `_pattern-library/` (~416 `.html` files) | Curated editorial slide patterns — every approved layout family (comparison, hero-number, three-pillar, waterfall, etc.) authored as HTML/CSS | Reference catalog of known-good editorial layouts. When QC'ing a slide, you can ask "does this match any of these 416 patterns?" |
| `_pattern-library/INDEX.md` | Catalog index with status (APPROVED / REVIEW / REJECTED) per pattern | Tells you which patterns are vetted vs experimental |
| `_renders/twins/*.pptx` (377 files, ~12MB) | Hand-built PPTX "twins" — every approved HTML pattern has a matching PPTX with shapes named to mirror the HTML's `data-shape-id` attributes | Visual reference for what each pattern looks like rendered. Useful for QC by comparison. |
| `_renders/twins/_pngs/` | PNG renders of every twin | Visual diff target |
| `twins/selector.py` | The catalog-search engine (matches brief intent → pattern) | NOT used in path-c. Don't route through it. Code stays for archival reasons. |
| `twins/composer.py` | The PPTX twin cloner + theme remap pipeline | **Partial reuse:** `_clear_existing_slides`, `_find_blank_layout`, `_strip_layout_placeholders`, and `apply_theme_to_shape_xml` (from `client_theme.py`) ARE used by the path-c finalizer. Don't delete. The `compose_deck` orchestration function is dormant. |
| `twins/build_with_options.py` | Catalog-flow batch builder | Dormant in path-c. |
| `twins/themed_thumbnails.py` | Renders catalog patterns themed for a client | Dormant. |
| `twins/overrides_resolver.py` | Pattern-aware content routing for the catalog flow | Dormant in path-c (path-c agents author per-slide). |

### Path-B — Skeletons (the smaller corpus)

Located in `~/.claude/skills/slide-builder/skeletons/`:

| Asset | What it is | Why it's useful |
|---|---|---|
| `skeletons/<id>/skeleton.yaml` (12 skeletons) | Structural slide templates: cover, two-panel, three-column, anchor-with-cards, hero-numeral-divider, etc. Each defines token slots (`{title}`, `{card_1_heading}`, etc.) | Reference set of pure structural layouts. Useful for thinking about layout taxonomy. |
| `skeletons/<id>/skeleton.pptx` | The PPTX render of each skeleton | Visual reference |
| `patches/patches.py` | `fill_tokens()`, `skeleton_on_template()`, etc. — the path-b execution engine | NOT used in path-c. Dormant. |

---

## What QC work can do with this corpus

Three angles worth using:

1. **Pattern-match a built slide against the catalog.** If a brand-new path-c slide
   looks like it should be a "two-column comparison with convergence band," you can
   look up that pattern's HTML in `_pattern-library/`, compare proportions / slot
   counts / typography choices, and flag deviations. The catalog is a vetted
   editorial standard — handy for "is this slide drifting?"

2. **Exemplar lookup.** When you need to show an agent (or a user) "here's what a
   strong waterfall-chart slide looks like," `_renders/twins/_pngs/` has 377
   rendered examples. Use the index in `_pattern-library/INDEX.md` to find the right
   one by intent tag.

3. **Page-type recognition.** The 9 page-type families (single-finding, comparison,
   hero-number, three-column, etc.) are reflected in the pattern names. Useful for
   QC's "is this slide playing the right role in the deck story?" check.

---

## What NOT to do

- Don't reactivate `twins.selector.propose_options` or `twins.build_with_options.prepare_deck_specs` for a deck build. Those route through path-a which we deprecated.
- Don't add new HTML patterns to `_pattern-library/` expecting them to ship in deck builds. Path-c reads the designer-brief, not the pattern library.
- Don't delete the `twins.composer` or `twins.client_theme` modules — path-c reuses subsets of them. Specifically `_clear_existing_slides`, `_find_blank_layout`, `_strip_layout_placeholders`, `apply_theme_to_shape_xml`, `load_client_theme`. These are load-bearing for the path-c finalize step.
- Don't try to dispatch through the catalog flow from `deck-builder.md`'s engine-choice prompt — path-c is the only supported choice now. The "catalog" option in that prompt is dormant.

---

## How path-c relates to the corpus

Path-c is a clean break in routing, NOT in code reuse:

| Layer | Path-c uses? |
|---|---|
| `_pattern-library/*.html` | NO — agents author from scratch using designer-brief |
| `_renders/twins/*.pptx` | NO — agents author with python-pptx primitives |
| `_pngs/` | OPTIONAL — useful as reference imagery for agents IF a future spec wants to show them exemplars |
| `twins/selector.py` | NO — not invoked |
| `twins/composer.py` (partial) | YES — clear/blank/strip helpers reused by path-c finalizer |
| `twins/client_theme.py` | YES — graft + theme-remap pipeline |
| `twins/helpers.py` | YES — the primary primitives library agents import |
| `skeletons/` + `patches/` | NO |

So the corpus is dormant for new builds, but `twins/composer.py` and
`twins/client_theme.py` are still active code that the path-c finalizer depends on.
Treat those two files as production code, not legacy.

---

## When this note becomes outdated

If a future spec rewires the catalog or skeleton path into the path-c orchestrator
(e.g., "use pattern matching as a hint to the designer-brief"), update this note.
Until then, the corpus is reference-only.

Updated: 2026-05-21 by the architectural-decision pass that committed to path-c.
