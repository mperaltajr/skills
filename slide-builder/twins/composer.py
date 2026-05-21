"""
Deck composer.

Given a list of slides — each specifying a pattern_id + text/color overrides —
this module produces a single PPTX deck by:
  1. Copying the matching twin PPTX (slides are merged into the output deck)
  2. Substituting text in shapes by data-shape-id (mapped to shape.name)
  3. Optionally recoloring shapes whose names match

Find-or-skip: if a slide specifies an override for a shape that doesn't exist
in the twin, the composer logs and continues. No errors.

Usage:
    from twins.composer import compose_deck

    compose_deck(
        out_path="out/my-deck.pptx",
        slides=[
            {"pattern": "01_anchor-with-cards-icons", "overrides": {
                "title": "Our hypothesis on the pilot.",
                "subtitle": "Three structural reasons the current process slows us down.",
                "card-1-heading": "Latency",
                "card-1-body": "Every approval gate adds median 3.2 days.",
                "card-2-heading": "Rework",
                "card-2-body": "32% of artifacts get redrawn in week 2.",
                "card-3-heading": "Handoffs",
                "card-3-body": "Five role transitions per deliverable.",
                "convergence": "Fixing latency alone gets us to week 8.",
            }},
        ],
    )
"""
from pathlib import Path
from copy import deepcopy
from typing import Dict, Any, List, Optional

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

from twins.client_theme import load_client_theme, apply_theme_to_shape_xml

# Default emphasis color for bold runs introduced by substitution when the
# original shape didn't have a multi-color emphasis hint of its own. Brand
# primary matches the design system's title convention across all 85 patterns.
_DEFAULT_EMPHASIS_RGB = RGBColor(0x2D, 0x0A, 0x4E)


TWINS_DIR = Path(__file__).resolve().parent.parent / "_renders" / "twins"


# Cache the catalog at module level — composer is hot path for thumbnail
# rendering, and load_catalog() reads a 25 MB YAML.
_CATALOG_CACHE: Optional[Dict[str, Any]] = None


def _get_catalog() -> Dict[str, Any]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE is None:
        from twins.selector import load_catalog
        _CATALOG_CACHE = load_catalog()
    return _CATALOG_CACHE


def _role_map_for(pattern_stem: str) -> Dict[str, str]:
    """Return the shape_role_map for a catalog pattern stem (or {} if not in
    the catalog). Used by _apply_overrides for role-aware blanking.
    """
    cat = _get_catalog()
    entry = cat.get(pattern_stem) or {}
    return entry.get("shape_role_map") or {}


def _resolve_twin_pptx(twins_dir: Path, pattern_stem: str) -> Optional[Path]:
    """Return the on-disk PPTX path for a catalog pattern key.

    Handles three known filename variances vs catalog keys:
      1. Zero-padding for single-digit IDs (catalog "1_foo" → file "01_foo.pptx")
      2. Trailing "-dark" suffix on dark patterns (catalog "177d_cover-logo-..."
         → file "177d_cover-logo-...-dark.pptx")
      3. Both above combined.

    Returns the resolved Path if found, else None.
    """
    import re
    candidates = [pattern_stem, f"{pattern_stem}-dark"]
    # Add zero-padded forms for single-digit IDs (catalog often uses unpadded)
    m = re.match(r"^(\d+)(d?)(_.+)$", pattern_stem)
    if m and len(m.group(1)) < 2:
        padded = f"0{m.group(1)}{m.group(2)}{m.group(3)}"
        candidates.append(padded)
        candidates.append(f"{padded}-dark")
    # Catalog keys like "02_foo-dark" should also resolve to the "Nd_foo.pptx" form
    # (some Phase-4 catalog entries embed -dark in the slug instead of using the
    # d-suffix on the number).
    dash_dark_match = re.match(r"^(\d+)_(.+)-dark$", pattern_stem)
    if dash_dark_match:
        num, slug = dash_dark_match.group(1), dash_dark_match.group(2)
        candidates.append(f"{num}d_{slug}")
        if len(num) < 2:
            candidates.append(f"0{num}d_{slug}")
    for cand in candidates:
        p = twins_dir / f"{cand}.pptx"
        if p.exists():
            return p
    return None


def _hex_to_rgb(hex_str: str) -> RGBColor:
    s = hex_str.lstrip("#")
    return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _find_shape_by_name(slide, name: str):
    """Return the first shape on the slide whose .name == name, or None."""
    for shape in slide.shapes:
        if shape.name == name:
            return shape
    return None


def _substitute_text(shape, new_text: str) -> None:
    """Replace all text in shape's text frame with `new_text`, preserving the
    first run's font properties.

    If `new_text` contains `<strong>X</strong>` or `<em>X</em>` tags, the text
    is split into multiple runs. Strong runs are bolded and (where the original
    shape was a title-like run with a strong-color hint) re-tinted toward
    brand-primary. Em runs are italicized. Other tags pass through as text.
    """
    if not shape.has_text_frame:
        return
    tf = shape.text_frame
    # Capture the first run's font properties so we don't lose styling
    src_p = tf.paragraphs[0]
    src_run = src_p.runs[0] if src_p.runs else None
    src_font = None
    if src_run:
        src_font = {
            "name": src_run.font.name,
            "size": src_run.font.size,
            "bold": src_run.font.bold,
            "italic": src_run.font.italic,
            "color_rgb": (src_run.font.color.rgb if src_run.font.color and src_run.font.color.type else None),
        }
    src_alignment = src_p.alignment
    # Detect if any other runs in the original had a different color — likely a
    # strong-emphasis run. Use it as the emphasis color hint for the substitution.
    emphasis_color_rgb = None
    if len(src_p.runs) > 1 and src_font and src_font.get("color_rgb"):
        for r in src_p.runs[1:]:
            try:
                if r.font.color and r.font.color.type:
                    rgb = r.font.color.rgb
                    if rgb is not None and rgb != src_font["color_rgb"]:
                        emphasis_color_rgb = rgb
                        break
            except Exception:
                pass

    # Clear and rewrite
    tf.clear()
    p = tf.paragraphs[0]
    if src_alignment is not None:
        p.alignment = src_alignment

    runs = _parse_inline_runs(new_text)
    if not runs:
        runs = [(new_text, False, False)]

    for seg, is_bold, is_italic in runs:
        run = p.add_run()
        run.text = seg
        f = run.font
        if src_font:
            if src_font["name"]:
                f.name = src_font["name"]
            if src_font["size"]:
                f.size = src_font["size"]
            f.bold = (src_font["bold"] or False) or is_bold
            f.italic = (src_font["italic"] or False) or is_italic
            if is_bold:
                f.color.rgb = emphasis_color_rgb or _DEFAULT_EMPHASIS_RGB
            elif src_font["color_rgb"] is not None:
                f.color.rgb = src_font["color_rgb"]


_INLINE_RE = __import__("re").compile(
    r"<(strong|em|b|i)>(.*?)</\1>", __import__("re").IGNORECASE | __import__("re").DOTALL
)


def _parse_inline_runs(text):
    """Split text into [(segment, bold, italic), ...] honoring <strong>/<em>
    (and <b>/<i>) inline tags."""
    if not text:
        return []
    runs = []
    pos = 0
    for m in _INLINE_RE.finditer(text):
        if m.start() > pos:
            runs.append((text[pos:m.start()], False, False))
        tag = m.group(1).lower()
        seg = m.group(2)
        runs.append((seg, tag in ("strong", "b"), tag in ("em", "i")))
        pos = m.end()
    if pos < len(text):
        runs.append((text[pos:], False, False))
    return runs


def _recolor_fill(shape, hex_str: str) -> None:
    """Set the shape's fill to a solid color (hex)."""
    shape.fill.solid()
    shape.fill.fore_color.rgb = _hex_to_rgb(hex_str)


def _apply_overrides(slide, overrides: Dict[str, Any], skip_log: List[str],
                      shape_role_map: Optional[Dict[str, str]] = None) -> None:
    """For each (shape_id, value) in overrides, find the shape and apply.
    Then blank any content-bearing shape on the slide that wasn't overridden,
    so the twin's hardcoded placeholder text doesn't leak into the final deck.

    When `shape_role_map` is provided (the picked pattern's catalog field),
    blanking is driven by the role map — every shape whose role is a content
    role and that wasn't overridden gets blanked. This is the authoritative
    path. When the role map is unavailable, falls back to the legacy regex
    heuristic (covers the common families but misses risk/quadrant/etc.).

    Value formats:
      - str: substitute text
      - {"text": "..."}: substitute text
      - {"fill": "#RRGGBB"}: recolor shape fill
      - {"text": "...", "fill": "#..."}: both
    """
    for shape_id, value in overrides.items():
        shape = _find_shape_by_name(slide, shape_id)
        if shape is None:
            skip_log.append(shape_id)
            continue
        if isinstance(value, str):
            _substitute_text(shape, value)
        elif isinstance(value, dict):
            if "text" in value:
                _substitute_text(shape, value["text"])
            if "fill" in value:
                _recolor_fill(shape, value["fill"])

    if shape_role_map:
        _blank_unmatched_via_role_map(slide, overrides, shape_role_map)
    else:
        _blank_unmatched_content_shapes(slide, overrides)


# Shape-id patterns whose default text is always meant to come from the
# brief (not the twin). If one of these shapes exists on the slide but the
# brief didn't supply an override, we BLANK it rather than leak the
# builder's placeholder text into the rendered deck.
#
# Chrome (source, footnote-N, page-num, brand-rule, *-bg, *-accent, *-icon,
# wordmark, logo, etc.) is intentionally NOT in this list — those keep
# their builder defaults.
import re as _re

_CONTENT_SHAPE_PATTERNS = [
    # Title-family text bound to governing_thought / so_what / cover content
    r"^title$",
    r"^subtitle$",
    r"^eyebrow$",
    r"^headline$",
    r"^hero-statement$",
    r"^hero-context$",
    r"^hero-attribution$",
    r"^key-question$",
    r"^anchor-statement$",
    r"^tagline$",
    # Cover-family text
    r"^cover-deck-title$",
    r"^cover-title$",
    r"^cover-wordmark$",
    r"^cover-tagline$",
    r"^cover-subtitle$",
    r"^cover-eyebrow$",
    r"^cover-pre-label$",
    r"^cover-presenter$",
    r"^cover-presented-name$",
    r"^cover-presented-label$",
    r"^cover-client-name$",
    r"^cover-brand-name$",
    r"^cover-date$",
    r"^cover-meta(-\d+(-label|-value)?)?$",
    # Grid items (cards / panels / columns / pillars / steps / options / buckets / cols)
    r"^(card|panel|column|pillar|step|option|bucket|col)-\d+-(heading|name|body|label|title|description|eyebrow)$",
    # Before/after comparison
    r"^(before|after)-panel-(heading|body|label)$",
    r"^(before|after)-(heading|body|label)$",
    # Metrics
    r"^metric-\d+-(label|value|delta)$",
    # Sub-asks / primary asks
    r"^sub-ask-\d+-(label|body)$",
    r"^primary-ask-text$",
    # Convergence + takeaway bands
    r"^convergence$",
    r"^takeaway$",
    # Memo/letter pattern content shapes (pattern 157 leak surface)
    r"^memo-(header-title|recipient|from|to|date|re|body|body-p\d+)$",
    r"^meta-(label|value)-\d+$",
    r"^body-p\d+$",
    r"^sig-(name|title|contact|line|divider)$",
    r"^priv-footer$",
    # Decision/comparison pattern content shapes (pattern 314 leak surface)
    r"^decision-(strip|label|text|divider|recommendation)$",
    r"^option-\d+-(card|header|name|title|subtitle|body|footer)$",
    r"^option-\d+-row-\d+-(label|value|status|dot|num)$",
    r"^recommendation-(label|text|body)$",
]
_CONTENT_SHAPE_RE = _re.compile("|".join(f"(?:{p})" for p in _CONTENT_SHAPE_PATTERNS))


def _blank_unmatched_via_role_map(slide, overrides: Dict[str, Any],
                                    shape_role_map: Dict[str, str]) -> None:
    """Role-map-driven blanking. For each shape on the slide:
      - Look up its role via overrides_resolver.role_for_shape (which
        understands templated keys like 'card-{n}-heading').
      - If the role is a content role AND the shape wasn't overridden,
        blank the text. Chrome / decoration / constant-label roles keep
        their builder defaults.

    This is more precise than the regex heuristic in
    `_blank_unmatched_content_shapes` because it consults the picked
    pattern's actual role map — covers risk-/quadrant-/glossary-/etc.
    shape families the regex missed.
    """
    from twins.overrides_resolver import role_for_shape, is_content_role
    matched_keys = set(overrides.keys())
    for shape in slide.shapes:
        try:
            name = shape.name or ""
        except Exception:
            continue
        if name in matched_keys:
            continue
        if not getattr(shape, "has_text_frame", False):
            continue
        try:
            if not shape.text_frame.text:
                continue
        except Exception:
            continue
        role = role_for_shape(shape_role_map, name)
        if not is_content_role(role):
            continue
        _substitute_text(shape, "")


def _blank_unmatched_content_shapes(slide, overrides: Dict[str, Any]) -> None:
    """Legacy regex-based blanking. Used when no shape_role_map is available
    (callers that don't know the picked pattern). Covers the common shape
    families (title / cards / panels / pillars / cover / metric / sub-ask /
    convergence) but misses risk/quadrant/glossary/etc.

    For every shape on the slide whose name matches a content-bearing
    pattern (see _CONTENT_SHAPE_PATTERNS) but that wasn't in `overrides`,
    replace its text with empty string. Prevents builder defaults from
    leaking through when the brief doesn't supply that piece of content.
    """
    matched_keys = set(overrides.keys())
    for shape in slide.shapes:
        try:
            name = shape.name or ""
        except Exception:
            continue
        if name in matched_keys:
            continue
        if not _CONTENT_SHAPE_RE.match(name):
            continue
        if not getattr(shape, "has_text_frame", False):
            continue
        try:
            if not shape.text_frame.text:
                continue
        except Exception:
            continue
        _substitute_text(shape, "")


def _find_blank_layout(prs):
    """Find a blank slide layout across all masters in `prs`.

    Looks for a layout whose name (case-insensitive, after stripping whitespace
    and leading numeric prefixes like '1_') is exactly 'blank'. Scans every
    slide master because client templates often put their blank layout on
    a non-zero master (FedEx puts it on master 11).
    """
    import re
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            n = layout.name.strip().lower()
            n = re.sub(r"^[\d_]+", "", n)  # strip "1_", "12__", etc.
            if n == "blank":
                return layout
    # Fallback to first master's first layout if no blank found
    return prs.slide_masters[0].slide_layouts[0]


def _strip_layout_placeholders(slide) -> int:
    """Remove every shape inherited from the slide's layout AND hide all master
    shapes BEFORE copying our twin shapes on top.

    Two-step strip:
      1. Remove layout-level placeholders that were copied onto the slide
         when add_slide(layout) was called (Click to add title, sample bullets).
      2. Set <p:sld showMasterSp="0"> so master-level shapes (Click to edit
         Master title style, FedEx Proprietary & Confidential footer,
         <Customize with Department> placeholders) DO NOT inherit onto the slide.

    Background, theme colors, and theme fonts inherit regardless of
    showMasterSp — those are not "shapes" in OOXML's sense. So the client's
    brand styling stays; only the leaky placeholder TEXT goes away.

    Returns the number of slide-level shapes removed.
    """
    # Step 1: drop slide-level shapes (placeholders copied from the layout)
    spTree = slide.shapes._spTree
    removed = 0
    for shp in list(slide.shapes):
        try:
            spTree.remove(shp.element)
            removed += 1
        except (ValueError, AttributeError):
            pass

    # Step 2: tell PowerPoint not to render master shapes on this slide.
    # The attribute is on the <p:sld> root element; default is "1" (show).
    try:
        slide.element.set("showMasterSp", "0")
    except Exception:
        pass

    return removed


def _clear_existing_slides(prs):
    """Remove any slides already present in the presentation (client templates
    often ship with sample slides we don't want) AND remove section groupings
    from the slide-panel sidebar.
    """
    sldIdLst = prs.slides._sldIdLst
    # Snapshot then drop each <p:sldId> element
    for sldId in list(sldIdLst):
        rId = sldId.get(qn("r:id"))
        try:
            prs.part.drop_rel(rId)
        except Exception:
            pass
        sldIdLst.remove(sldId)
    # Strip <p14:sectionLst> from the presentation extLst so the slide panel
    # doesn't show stale section groupings ('Brand Elements', 'Begin Building',
    # etc.) from the original template. Sections live under a <p:ext> whose
    # child is <p14:sectionLst>, where p14 is the 2010 powerpoint namespace.
    # (Earlier versions of this code used the 2012 namespace by mistake and
    # the strip never fired — orphaned section groups bled through grafted
    # decks. Check BOTH known namespaces to survive future schema variants.)
    pres_el = prs.part._element
    _SECTION_LST_TAGS = (
        "{http://schemas.microsoft.com/office/powerpoint/2010/main}sectionLst",
        "{http://schemas.microsoft.com/office/powerpoint/2012/main}sectionLst",
    )
    for ext_lst in pres_el.findall(qn("p:extLst")):
        for ext in list(ext_lst):
            for tag in _SECTION_LST_TAGS:
                if ext.find(".//" + tag) is not None:
                    ext_lst.remove(ext)
                    break


# ---------------------------------------------------------------------------
# Pattern-to-FedEx-layout routing
# ---------------------------------------------------------------------------

# Map pattern stems (the part before the first underscore-less segment) to
# a layout-name substring. The composer picks the first layout whose name
# CONTAINS the substring, scanning all masters. Generic enough to work on any
# client template that follows PowerPoint's standard layout-naming conventions
# (Title Slide, Section Divider, Statement / Quote, Closing, etc.).
#
# Patterns not listed default to the first "Text" / "Content" layout, then
# blank if neither exists.
_PATTERN_LAYOUT_HINTS = {
    "19_cover-split-panel":         "Title Slide",
    "06_section-divider-numeral":   "Section Divider",
    "30_verbatim-pull-quote":       "Statement",
    "38_statement-hero-text":       "Statement",
    "97_mission-statement-slide":   "Statement",
    "40_closing-cta-revival":       "Closing",
}


def _find_layout_containing(prs, substring: str):
    """Return the first layout in any master whose name contains `substring`
    (case-insensitive). None if no match.
    """
    needle = substring.lower()
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            if needle in layout.name.lower():
                return layout
    return None


def _resolve_layout_for_pattern(prs, pattern: str):
    """Pick the most appropriate client-template layout for a given pattern.

    Strategy: lookup by pattern name in _PATTERN_LAYOUT_HINTS; if no hint,
    use a generic body content layout (`Text Only` / `Text` / `Content`).
    Final fallback is the blank layout.
    """
    hint = _PATTERN_LAYOUT_HINTS.get(pattern)
    if hint:
        layout = _find_layout_containing(prs, hint)
        if layout:
            return layout
    # Default body content
    for needle in ("Text Only", "Text", "Content"):
        layout = _find_layout_containing(prs, needle)
        if layout:
            return layout
    return _find_blank_layout(prs)


# Twin shape IDs that should be REMOVED when composing onto a client template.
# Strict policy (per user direction 2026-05-19): only strip CHROME shapes
# (accenture-tag, draft-badge, footer chrome). The template's master provides
# those.
#
# Do NOT strip title / subtitle / brand-rule. The twin was designed with these
# at specific positions sized for the body content; pushing them into the
# layout's TITLE placeholder ruins the format because the placeholder is
# typically sized differently and the body shapes below collide.
#
# The user keeps the twin's own title/subtitle visible; switching layouts in
# PowerPoint won't auto-move them, and that's the explicit trade-off.
_CHROME_SHAPE_IDS_TO_STRIP = {
    "accenture-tag",
    "draft-badge",
    "footer-rule",
    "footer-left",
    "footer-right",
    "footer-center",
}


def _find_title_placeholder(slide):
    """Return the slide's title placeholder, or None.

    A 'title placeholder' here is strictly TITLE-type or a placeholder whose
    name contains 'title'. BODY placeholders are NOT used as a fallback —
    they're sized for body content (often very large, like in Closing
    layouts) and putting a title there causes visual conflict with the
    pattern's body shapes. When no proper title placeholder exists, the
    caller should keep the twin's own title shape.
    """
    from pptx.enum.shapes import PP_PLACEHOLDER
    for shp in slide.placeholders:
        try:
            if shp.placeholder_format.type == PP_PLACEHOLDER.TITLE:
                return shp
        except Exception:
            continue
    for shp in slide.placeholders:
        if "title" in (shp.name or "").lower():
            return shp
    return None


def compose_deck(out_path: str, slides: List[Dict[str, Any]], *,
                 twins_dir: Optional[Path] = None,
                 client_template: Optional[str] = None,
                 verbose: bool = True) -> Path:
    """Compose a deck from a list of {pattern, overrides} entries.

    If `client_template` is provided (path to a .pptx/.potx), the deck is
    built on top of that template — slides inherit its theme, masters, and
    fonts. Otherwise the deck is built starting from the first twin (which
    uses Slide Lab's default theme).

    Returns the output path. Skipped overrides are logged but not raised.
    """
    twins_dir = Path(twins_dir) if twins_dir else TWINS_DIR
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not slides:
        raise ValueError("compose_deck called with empty slides list")

    # ------------------------------------------------------------------
    # Branch 1: client-template-based composition (multi-slide always)
    # ------------------------------------------------------------------
    if client_template:
        tpl_path = Path(client_template)
        if not tpl_path.exists():
            raise FileNotFoundError(f"Client template not found: {tpl_path}")
        prs = Presentation(str(tpl_path))
        _clear_existing_slides(prs)

        # Load the client's theme — used to recolor every twin shape and swap
        # the Inter font for the client's body font.
        client_theme = load_client_theme(str(tpl_path))
        color_map = client_theme.color_map()
        client_body_font = client_theme.minor_font

        if verbose:
            print(f"  Client theme: primary #{client_theme.dk2}, accent #{client_theme.lt2}, font '{client_body_font}'")

        skip_log_total = []
        theme_subs_total = 0
        chrome_stripped_total = 0
        for spec in slides:
            twin_path = _resolve_twin_pptx(twins_dir, spec['pattern'])
            if twin_path is None:
                raise FileNotFoundError(
                    f"Twin not found for pattern {spec['pattern']!r} in {twins_dir}. "
                    f"Tried variants with zero-padding and -dark suffix."
                )
            src_prs = Presentation(str(twin_path))
            src_slide = src_prs.slides[0]

            # Pick a layout from the client template that matches this pattern
            chosen_layout = _resolve_layout_for_pattern(prs, spec["pattern"])
            new_slide = prs.slides.add_slide(chosen_layout)

            # Strip template-inherited placeholders BEFORE copying twin shapes.
            # Without this, client templates leak "Click to add title" /
            # sample bullets / footer text fields behind our twin design.
            _strip_layout_placeholders(new_slide)

            # Carry the twin's background only for true dark-mode patterns
            # (where the twin sets a colored background). For light-mode
            # patterns we let the client layout's background show through.
            try:
                src_bg_rgb = src_slide.background.fill.fore_color.rgb
                # Only override if the source background is NOT pure white
                if not (src_bg_rgb[0] == 0xFF and src_bg_rgb[1] == 0xFF and src_bg_rgb[2] == 0xFF):
                    src_bg_hex = "{:02X}{:02X}{:02X}".format(src_bg_rgb[0], src_bg_rgb[1], src_bg_rgb[2])
                    remapped = color_map.get(src_bg_hex, src_bg_hex)
                    new_slide.background.fill.solid()
                    new_slide.background.fill.fore_color.rgb = RGBColor(
                        int(remapped[0:2], 16), int(remapped[2:4], 16), int(remapped[4:6], 16)
                    )
            except Exception:
                pass

            # Per user direction 2026-05-19: do NOT push title into the
            # layout's TITLE placeholder. The placeholder is sized differently
            # from the twin's title shape and causes body-content collision.
            # Keep the twin's title/subtitle/brand-rule shapes as designed.
            overrides = dict(spec.get("overrides", {}))

            # Copy twin shapes, skipping chrome that the master provides.
            # Title / subtitle / brand-rule come from the twin (they ARE the
            # design of the slide).
            for shp in src_slide.shapes:
                if (shp.name or "") in _CHROME_SHAPE_IDS_TO_STRIP:
                    chrome_stripped_total += 1
                    continue
                new_el = deepcopy(shp.element)
                new_slide.shapes._spTree.append(new_el)
                appended = new_slide.shapes._spTree[-1]
                theme_subs_total += apply_theme_to_shape_xml(
                    appended, color_map,
                    major_font=client_theme.major_font,
                    minor_font=client_body_font,
                )
            # Apply remaining overrides to the new slide (covers card-N-* etc.)
            _apply_overrides(new_slide, overrides, skip_log_total,
                              shape_role_map=_role_map_for(spec["pattern"]))

        prs.save(str(out_path))
        if verbose:
            if skip_log_total:
                print(f"  Skipped {len(skip_log_total)} unknown shape ids: {skip_log_total}")
            print(f"  Stripped {chrome_stripped_total} twin chrome shapes (provided by template master)")
            print(f"  Applied {theme_subs_total} theme substitutions (colors + fonts) across {len(slides)} slides")
            print(f"Wrote {out_path} ({len(slides)} slides on client template: {tpl_path.name})")
        return out_path

    # ------------------------------------------------------------------
    # Branch 2: single-slide composition (twin as base, no template)
    # ------------------------------------------------------------------
    if len(slides) == 1:
        spec = slides[0]
        twin_path = _resolve_twin_pptx(twins_dir, spec['pattern'])
        if twin_path is None:
            raise FileNotFoundError(
                f"Twin not found for pattern {spec['pattern']!r} in {twins_dir}. "
                f"Tried variants with zero-padding and -dark suffix."
            )
        prs = Presentation(str(twin_path))
        slide = prs.slides[0]
        skip_log = []
        _apply_overrides(slide, spec.get("overrides", {}), skip_log,
                          shape_role_map=_role_map_for(spec["pattern"]))
        prs.save(str(out_path))
        if verbose and skip_log:
            print(f"  Skipped {len(skip_log)} unknown shape ids: {skip_log}")
        if verbose:
            print(f"Wrote {out_path}")
        return out_path

    # ------------------------------------------------------------------
    # Branch 3: multi-slide composition (first twin as base, no template)
    # ------------------------------------------------------------------
    from pptx.oxml.ns import qn
    from lxml import etree

    first_spec = slides[0]
    first_twin = twins_dir / f"{first_spec['pattern']}.pptx"
    if not first_twin.exists():
        raise FileNotFoundError(f"Twin not found: {first_twin}")
    prs = Presentation(str(first_twin))
    skip_log_total = []
    _apply_overrides(prs.slides[0], first_spec.get("overrides", {}), skip_log_total,
                      shape_role_map=_role_map_for(first_spec["pattern"]))

    for spec in slides[1:]:
        twin_path = _resolve_twin_pptx(twins_dir, spec['pattern'])
        if twin_path is None:
            raise FileNotFoundError(
                f"Twin not found for pattern {spec['pattern']!r} in {twins_dir}. "
                f"Tried variants with zero-padding and -dark suffix."
            )
        src_prs = Presentation(str(twin_path))
        src_slide = src_prs.slides[0]
        blank_layout = _find_blank_layout(prs)
        new_slide = prs.slides.add_slide(blank_layout)
        # Strip any layout-inherited placeholders before copying twin shapes.
        _strip_layout_placeholders(new_slide)
        try:
            new_slide.background.fill.solid()
            new_slide.background.fill.fore_color.rgb = src_slide.background.fill.fore_color.rgb
        except Exception:
            pass
        for shp in src_slide.shapes:
            new_el = deepcopy(shp.element)
            new_slide.shapes._spTree.append(new_el)
        _apply_overrides(new_slide, spec.get("overrides", {}), skip_log_total,
                          shape_role_map=_role_map_for(spec["pattern"]))

    prs.save(str(out_path))
    if verbose and skip_log_total:
        print(f"  Skipped {len(skip_log_total)} unknown shape ids: {skip_log_total}")
    if verbose:
        print(f"Wrote {out_path} ({len(slides)} slides)")
    return out_path


if __name__ == "__main__":
    # Smoke test: substitute text in pattern 01's twin
    out = Path(__file__).resolve().parent.parent / "_renders" / "twins" / "_compose-test-01.pptx"
    compose_deck(
        out_path=str(out),
        slides=[{
            "pattern": "01_anchor-with-cards-icons",
            "overrides": {
                "title": "Our hypothesis on the pilot.",
                "subtitle": "Three structural reasons the current process slows us down.",
                "card-1-heading": "Latency",
                "card-1-body": "Every approval gate adds median 3.2 days. Compounds week over week — the slow path eats the fast path.",
                "card-2-heading": "Rework",
                "card-2-body": "32% of artifacts get redrawn in week 2. The first draft anchors the wrong assumption.",
                "card-3-heading": "Handoffs",
                "card-3-body": "Five role transitions per deliverable. Each handoff loses context and adds wait time.",
                "convergence": "Fixing latency alone gets us to week 8 — but we have to commit by Friday.",
                "footer-right": "Slide Lab · 2026 · 14",
            },
        }],
    )
