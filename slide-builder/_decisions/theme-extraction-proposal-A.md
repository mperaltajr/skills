# Theme Extraction — Reviewer A (XML-direct / pure-technical)

Status: proposal · Reviewer A · blind to B and C
Templates tested: Accenture/_templates/ACN Graphik Template.pptx, FedEx/_templates/Moving Forward PPT Template.pptx
Both extracted to /tmp/pptx_inspect/{acn,fedex}/ and inspected directly.

---

## TL;DR — XML-direct as PRIMARY is correct, but the brand-primary signal is NOT in the master slide

The conventional wisdom in the prompt ("brand-primary is the color used in title text fill / header stripe / logo placement on the master") **falls apart on real templates I just opened**. In both ACN and FedEx, the slide master's title placeholder resolves to `tx1` (text color = `dk1`), not to a brand slot. Title-fill-as-signal is wrong.

What IS reliably extractable from XML:

1. **Font scheme is trivially semantic** — `<a:majorFont>/<a:latin>` and `<a:minorFont>/<a:latin>` are by definition heading and body. No heuristic needed.
2. **Brand color slot inventory is trivially extractable** — `theme1.xml::clrScheme` gives all 12 named slots.
3. **Brand-primary identity is NOT trivially extractable from XML alone.** Slots are positional. Master/layout usage is dominated by `tx1`, direct sRGB chrome colors, and `accentN` references that mean whatever the designer wanted them to mean. There is no XML element labeled "this is the brand primary."

**My recommendation:** XML-direct extraction as the primary mechanism, but reframed. Stop trying to *infer* `brand_primary` from XML. Instead, **extract the full, faithful theme dictionary, and require an explicit per-template mapping file** (`brand.yml`) that names which slot is primary, which is accent, which contains the cover-slide chrome color, etc. The mapping is created once per template by the human onboarding the client, stored in version control next to the PPTX, and read deterministically on every build.

This is the correct factoring: **mechanical extraction handles what is mechanical; one-time human judgment handles what is semantic.** The current bug class exists precisely because we conflated those two layers into a guess function.

---

## Evidence from the two real templates

I unzipped both PPTX files and read theme1.xml, slideMaster1.xml, and a sample of slideLayoutNNN.xml directly.

ACN clrScheme:
```
dk1=000000 lt1=FFFFFF dk2=A100FF lt2=460073
accent1=7500C0 accent2=C2A3FF accent3=E6DCFF accent4=FF50A0 accent5=224BFF accent6=05F2DB
```
FedEx clrScheme:
```
dk1=333333 lt1=FFFFFF dk2=4D148C lt2=FF6600
accent1=7D22C3 accent2=A63685 accent3=C74755 accent4=8E8E8E accent5=E3E3E3 accent6=F2F2F2
```

Two important findings the current slot-mapping does NOT capture:

- **ACN lt2 is dark purple #460073** — not "light" at all. The current heuristic's lt2-as-accent fallback would pick a near-black-purple as the "accent." That is why `_pick_brand_colors` falls back to `accent1` here. Fragile.
- **FedEx lt2 is orange #FF6600** — a real secondary brand color, NOT an accent the builder should desaturate or treat as soft. Today's `_pick_accent_soft` (client_theme.py:291-320) tries to derive a "pale" version of accent; that math turns FedEx orange into beige, which is wrong for any FedEx slide that needs the orange treatment.

Slide-master schemeClr usage frequency:
- ACN master: tx1 x 22, bg1 x 1, tx2 x 1. Zero accentN or dk2/lt2 references.
- FedEx master: tx1 x 18, bg1 x 1, tx2 x 1. Zero brand-slot references.

Slide-master direct srgbClr usage:
- ACN: #5ACBF0, #9FCC3B, #C35EA4, #F26B43, #FDE53C — none of which is the brand-primary #A100FF.
- FedEx: same color palette #5ACBF0, #C35EA4, #F26B43, #FDE53C — same generic-looking colors.

So both templates' masters share a near-identical chrome palette unrelated to either brand. The "find brand-primary by what the master uses" approach yields cyan-ish blue, not the actual brand color.

Slide-layout layer is more useful. Counting brand-slot references across all layouts:
- FedEx layouts reference accent6 (about 50 layouts), accent4 (chart fills), accent5 (map fills) heavily. dk2 and lt2 are NOT referenced as schemeClr in any layout — but dk2's literal hex #4D148C appears as direct srgbClr in 42 files (hardcoded by the designer).
- ACN layouts reference accent2 heavily in dark-mode layouts.

The frequency signal is template-specific and high-noise. A counting approach picks accent2 for ACN (wrong) and accent6 for FedEx (also wrong). I tested this directly before discarding it.

---

## Proposal — XML-direct extraction + per-template brand.yml

### Mechanism

On build, for every dispatch:

1. **Resolve template path.** From CLI flag or brief front-matter (`client_template:`).
2. **Locate sidecar brand.yml.** Same directory as the PPTX, stem-matched: `<template-stem>.brand.yml`, falling back to `_templates/brand.yml`, falling back to the client-project-root `brand.yml`. If none exists, halt with exit code 7 and print the bootstrap command. Do not guess.
3. **Open the PPTX as a ZIP** (no python-pptx needed for the read; use zipfile + lxml).
4. **Extract canonical XML facts** into a Theme object:
   - `ppt/theme/theme1.xml::a:clrScheme` → 12 named color slots (sRGB or sysClr-resolved).
   - `ppt/theme/theme1.xml::a:fontScheme` → major/minor latin typefaces, with style-suffix stripping.
   - `ppt/theme/theme1.xml::a:fmtScheme` → fill, line, effect style lists (read but currently unused).
   - `ppt/presentation.xml::p:sldSz` → slide width/height in EMU (16:9 vs 16:10 vs 4:3).
   - `ppt/slideMasters/slideMaster1.xml::p:clrMap` → maps `bg1/tx1/bg2/tx2/accent1..6/hlink/folHlink` to scheme slots. NOT identity for every template; must preserve verbatim to correctly resolve schemeClr refs.
5. **Merge with brand.yml** which names the semantic roles: `primary_slot: dk2`, `accent_slot: lt2`, `cover_bg_slot: accent1`, `card_bg_slot: accent6`, etc.
6. **Write a canonical theme.json** to the project directory. Every downstream agent reads this single file. Builders never re-open the PPTX for theme purposes.

The build agent's very first action becomes: `theme = load_theme(project_dir / "theme.json")`. Single source of truth. No re-derivation.

### Why this beats slot-mapping

`_pick_brand_colors` (twins/client_theme.py lines 138-183) walks a hardcoded preference order `("dk2", "accent1", "accent2", "accent3", "accent4")` and picks the first slot whose `is_branded()` test passes (HSV-S >= 0.30, HSV-V >= 0.20). This produces the right answer for ACN (dk2 = #A100FF) and FedEx (dk2 = #4D148C) **by coincidence** — both put their primary in dk2 AND no upstream slot was more saturated. Change either fact and the heuristic fails silently. There is no XML structure that prevents a future client from putting their brand in accent3 while leaving a saturated decorative color in dk2.

A per-template manifest, written once by a human looking at the actual deck, eliminates the failure mode.

### What I am explicitly NOT proposing

- **Not** "infer brand-primary from how often a hex appears in slide layouts." Frequency signal is template-dependent (tested above).
- **Not** "infer brand-primary from the master's title placeholder." Both templates' titles use tx1 which resolves to text-black.
- **Not** "infer from logo image inspection." Templates may not contain logo bitmaps; some logos are SVG groups indistinguishable from decorative chrome.

---

## What the canonical theme file looks like

Filename: `theme.json` (lives at the project root, next to the brief). Generated by `extract_theme.py`. Read by every builder.

```json
{
  "_schema_version": 1,
  "_generated_by": "extract_theme.py",
  "_generated_at": "2026-05-25T14:00:00Z",
  "_source_pptx": "C:/.../FedEx/_templates/Moving Forward PPT Template.pptx",
  "_source_pptx_sha256": "abc123...",
  "_brand_yml": "C:/.../FedEx/_templates/Moving Forward PPT Template.brand.yml",
  "client_slug": "fedex",
  "slide": {
    "width_emu": 12192000,
    "height_emu": 6858000,
    "aspect": "16:9"
  },
  "colors": {
    "raw": {
      "dk1":"333333","lt1":"FFFFFF","dk2":"4D148C","lt2":"FF6600",
      "accent1":"7D22C3","accent2":"A63685","accent3":"C74755",
      "accent4":"8E8E8E","accent5":"E3E3E3","accent6":"F2F2F2",
      "hlink":"333333","folHlink":"4D148C"
    },
    "clr_map": {
      "bg1":"lt1","tx1":"dk1","bg2":"lt2","tx2":"dk2",
      "accent1":"accent1","accent2":"accent2","accent3":"accent3",
      "accent4":"accent4","accent5":"accent5","accent6":"accent6",
      "hlink":"hlink","folHlink":"folHlink"
    },
    "semantic": {
      "primary":         "4D148C", "primary_source":      "dk2",
      "accent":          "FF6600", "accent_source":       "lt2",
      "primary_mid":     "7D22C3", "primary_mid_source":  "accent1",
      "accent_soft":     "F2F2F2", "accent_soft_source":  "accent6",
      "text_dark":       "333333", "text_dark_source":    "dk1",
      "text_mid":        "888888", "text_mid_source":     "derived",
      "text_faint":      "BBBBBB", "text_faint_source":   "derived",
      "card_bg":         "F8F8F8", "card_bg_source":      "derived",
      "card_border":     "E3E3E3", "card_border_source":  "derived"
    }
  },
  "fonts": {
    "major": { "latin": "FedEx Sans", "raw": "FedEx Sans Bold" },
    "minor": { "latin": "FedEx Sans", "raw": "FedEx Sans Regular" }
  }
}
```

Every field has provenance:
- `colors.raw.*` is the literal hex from theme1.xml::clrScheme/<slot> (XML path).
- `colors.semantic.primary_source` is the slot name from brand.yml.
- `colors.semantic.text_mid_source: "derived"` flags computed values.

Auditable end-to-end. Schema is forward-compatible: `_schema_version: 1` lets future fields (e.g., `colors.semantic.danger`) be added without breaking old builders.

---

## Implementation sketch

**Library choice: lxml + zipfile (stdlib).** Not python-pptx. Reasons:
- python-pptx is heavy, opens the whole presentation, and exposes a writer-oriented model — overkill for reading 4 XML files.
- lxml is already transitively present.
- The current `load_client_theme` uses regex against decoded XML strings (client_theme.py lines 404-415). That is a real bug surface — `<a:dk2>` matches inside a comment or in another scheme. lxml with proper XPath is faster and correct.

```python
# scripts/extract_theme.py  (~150 lines, stdlib + lxml + PyYAML)
import hashlib, json, zipfile, datetime
from pathlib import Path
from lxml import etree
import yaml

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

SLOT_NAMES = ("dk1", "lt1", "dk2", "lt2",
              "accent1", "accent2", "accent3", "accent4", "accent5", "accent6",
              "hlink", "folHlink")

_FONT_SUFFIXES = (" Bold", " Regular", " Italic", " Light", " Medium",
                  " SemiBold", " ExtraBold", " Black", " Thin", " ExtraLight",
                  " Heavy", " Oblique", "-Semibold", "-Bold", "-Regular")

def _strip_font(name):
    n = name.strip()
    for suf in _FONT_SUFFIXES:
        if n.endswith(suf):
            return n[:-len(suf)].strip()
    return n

def _color_from_slot(slot_elem):
    srgb = slot_elem.find("a:srgbClr", NS)
    if srgb is not None:
        return srgb.get("val", "").upper()
    sysc = slot_elem.find("a:sysClr", NS)
    if sysc is not None:
        last = sysc.get("lastClr")
        if last:
            return last.upper()
    return None

def extract(pptx_path, brand_yml_path):
    pptx_path = Path(pptx_path).resolve()
    sha = hashlib.sha256(pptx_path.read_bytes()).hexdigest()
    brand = yaml.safe_load(brand_yml_path.read_text(encoding="utf-8"))

    with zipfile.ZipFile(pptx_path) as z:
        theme_xml  = z.read("ppt/theme/theme1.xml")
        master_xml = z.read("ppt/slideMasters/slideMaster1.xml")
        pres_xml   = z.read("ppt/presentation.xml")

    theme  = etree.fromstring(theme_xml)
    master = etree.fromstring(master_xml)
    pres   = etree.fromstring(pres_xml)

    clr_scheme = theme.find(".//a:clrScheme", NS)
    raw = {}
    for slot in SLOT_NAMES:
        node = clr_scheme.find(f"a:{slot}", NS)
        if node is not None:
            raw[slot] = _color_from_slot(node)

    clr_map_el = master.find(".//p:clrMap", NS)
    clr_map = {k: clr_map_el.get(k) for k in
               ("bg1", "tx1", "bg2", "tx2",
                "accent1", "accent2", "accent3", "accent4", "accent5", "accent6",
                "hlink", "folHlink")}

    def _font(kind):
        f = theme.find(f".//a:{kind}", NS)
        if f is None: return {"latin": "", "raw": ""}
        latin = f.find("a:latin", NS)
        if latin is None: return {"latin": "", "raw": ""}
        raw_name = latin.get("typeface", "")
        return {"latin": _strip_font(raw_name), "raw": raw_name}

    sz = pres.find(".//p:sldSz", NS)
    w, h = int(sz.get("cx")), int(sz.get("cy"))

    sem = {}
    for sem_name, slot_name in brand["semantic_slots"].items():
        if slot_name == "derive":
            continue
        sem[sem_name] = raw.get(slot_name)
        sem[sem_name + "_source"] = slot_name

    return {
        "_schema_version": 1,
        "_generated_by": "extract_theme.py",
        "_generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "_source_pptx": str(pptx_path),
        "_source_pptx_sha256": sha,
        "_brand_yml": str(brand_yml_path),
        "client_slug": brand["client_slug"],
        "slide": {"width_emu": w, "height_emu": h,
                  "aspect": "16:9" if abs(w/h - 16/9) < 0.01 else f"{w}:{h}"},
        "colors": {"raw": raw, "clr_map": clr_map, "semantic": sem},
        "fonts": {"major": _font("majorFont"), "minor": _font("minorFont")},
    }
```

brand.yml (one-time, human-written, ~15 lines):

```yaml
client_slug: fedex
semantic_slots:
  primary:      dk2
  accent:       lt2
  primary_mid:  accent1
  accent_soft:  accent6
  text_dark:    dk1
  cover_bg:     dk2
  card_bg:      derive   # signal to derive from dk1+lt1
notes: |
  FedEx puts secondary brand (orange #FF6600) in lt2.
  accent1 (#7D22C3) is the lighter purple used in process diagrams.
```

Total new code: ~200 lines including the brand.yml loader, the extractor, and a CLI front-end (`python -m scripts.extract_theme path/to/template.pptx --brand path/to/brand.yml --out theme.json`). The existing `client_theme.py::color_map()` reduces to a dict lookup against theme.json — drops ~120 lines.

I validated the extraction logic against both real templates on disk. Output matches the existing `Accenture/_templates/ACN Graphik Template.json` byte-for-byte on the color and font fields. The proposal does not invent any new dependencies; it removes assumptions.

---

## Failure modes

What this misses that slot-mapping caught:

1. **Zero-touch onboarding.** Slot-mapping let an operator drop a PPTX into a folder and run the build with no human review. The proposed mechanism halts on first encounter and demands a brand.yml. This is a feature, not a bug — silent wrong colors are worse than a halt — but it is more friction. Mitigation: ship a `bootstrap_brand_yml.py` that opens the PPTX, prints the slot inventory with ANSI color swatches, and writes a draft brand.yml for human review. Cuts onboarding to ~2 minutes.

2. **Templates with sysClr or schemeClr indirection in the scheme itself.** Some old templates (PowerPoint 2010 era) declare `<a:dk2><a:sysClr val="windowText"/></a:dk2>` without lastClr. Today's regex also fails here. The proposal degrades gracefully (slot becomes None, extract_theme.py warns, operator fills in brand.yml by eye). No regression.

3. **Multi-master templates** (FedEx has 12 themes and 12 masters). The proposal reads theme1.xml and slideMaster1.xml only. Risk: if the user builds against slideMaster3.xml, colors may differ. Mitigation: brand.yml can declare `master_index: 0` (default), and the extractor reads theme{N}.xml where N is resolved via the slideMaster's _rels. ~10 extra lines.

4. **Designer-overridden title text colors that DO carry brand intent.** Some templates do paint titles in brand-primary directly on the master. The proposal ignores this; brand.yml lets the human encode whatever truth applies. We do not pretend to infer it.

5. **Sub-theme rendering chrome.** Cover slide backgrounds, divider chevrons, footer rules — these are template-specific chrome encoded in slide layouts, not theme1.xml. The proposed theme.json does not capture them. Out of scope for "brand theme extraction"; if the builder needs to *match* template chrome (rather than recolor twin shapes), that is a different mechanism (layout cloning) which v1 already has via `apply_theme_to_shape_xml`.

---

## Trade-offs vs alternative approaches

| Approach | Verdict | Why |
|---|---|---|
| **XML-direct + brand.yml** (this proposal) | **Primary** | Mechanical and semantic concerns separated. Deterministic. Auditable provenance per field. Halts on ambiguity rather than guessing. |
| Image-analysis (render slide, extract dominant pixels) | Reject as primary | Brittle: requires LibreOffice headless + Pillow + cluster analysis. Slow (5-10 sec per template). Compresses away the slot distinction we need (primary vs accent vs primary_mid all blur into "purple"). Useful as a **validator**: render the cover slide, check the brand-primary appears in the top-3 cluster centers. |
| Interactive setup (operator confirms via CLI swatches) | Reject as runtime mechanism | Fine for one-time onboarding (= bootstrap_brand_yml.py). Not appropriate for build-time — agents fan out in parallel, they cannot prompt a human. |
| **Hybrid (XML + image validator)** | **Recommended for v2.x** | XML-direct is primary; the image validator runs once after extract_theme.py and warns if `colors.semantic.primary` does not appear in the cover slide's dominant clusters. Catches the case where brand.yml was filled in wrong. |

The XML-direct approach is right because the data we want IS in the XML, deterministically, with byte-exact provenance. The only question is "which slot means what to this client" — and that question has exactly one correct answer per template, written down once.

---

## Migration plan

**v1 (slide-builder/twins/client_theme.py):**

1. Land scripts/extract_theme.py and scripts/bootstrap_brand_yml.py.
2. Run bootstrap against every template currently in use (ACN, FedEx, and any session that has built). Commit the resulting brand.yml files alongside the PPTX in each client project folder. The existing setup_template.py already extracts to JSON; deprecate it in favor of extract_theme.py (smaller, schema-versioned, includes provenance hash).
3. Rewrite load_client_theme() as a 30-line wrapper that:
   - If a sibling theme.json exists and _source_pptx_sha256 matches the current PPTX, load it.
   - Else if brand.yml exists, run extract_theme.extract(), cache theme.json, return.
   - Else, halt with bootstrap instructions.
4. ClientTheme.color_map() becomes a dict-walk over theme.json::colors.semantic. Delete _pick_brand_colors, _pick_primary_mid, _pick_accent_soft, is_branded. Drops ~150 lines of heuristic code.
5. apply_theme_to_shape_xml is unchanged — it only consumes the resolved map.

**v2 (slide-builder-simple/scripts/build_deck.py):**

1. Replace today's generate_mermaid_theme() (lines 492-552) with a thin transform: read theme.json, walk the existing THEME_MAPPING table, emit mermaid-<slug>.json. The mapping table's left-hand side (e.g., colors.dk2) becomes colors.semantic.primary instead — making the Mermaid theme client-agnostic in lookup, since semantic resolution already happened in extract_theme.py. Centralizes the v1-bug-class fix identified in build-deck-review.md issue #3.
2. validate_theme() (lines 622-718) becomes the image validator described above. Repurpose its hue-range check as "render cover slide, confirm primary appears." Delete the FedEx-only KNOWN_CLIENT_HUE_RANGES dict.
3. The "first thing every build agent does" rule (user's quoted directive): every dispatched agent's prompt receives theme.json content inline. They never re-derive.

**Backward compatibility:**
- A build with no brand.yml halts with a clear bootstrap command. No silent regression.
- A build with brand.yml produces colors guaranteed to match the human-confirmed mapping. Eliminates the entire bug class that prompted this review.

**Timeline:** ~1 day for extract_theme.py + bootstrap_brand_yml.py + tests. ~half-day to migrate v1's client_theme.py. ~half-day to migrate v2's build_deck.py + retire validate_theme's hue check. Total: 2 days.

---

## Closing observation

The current code has accumulated three layers of correction (saturation-aware slot picker -> off-palette aliases -> v2 validate_theme guard) trying to make a fundamentally underspecified problem behave. Each layer added is another place a future client breaks. The proposal removes the underlying ambiguity instead of compensating for it downstream. That is the right shape of fix.
