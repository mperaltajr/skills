"""Slide-graft chrome helpers.

Three small functions called by `scripts/finalize_deck.py::graft_and_theme`
and `scripts/compile_picks.py` to prepare a client-template `Presentation`
for slide grafting:

  - `_clear_existing_slides(prs)` — drop any sample slides shipped with the
    template + strip stale section groupings from the slide-panel sidebar.
  - `_find_blank_layout(prs)` — locate a 'Blank' slide layout across all
    masters (client templates often put the blank layout on a non-zero
    master; FedEx puts it on master 11).
  - `_strip_layout_placeholders(slide)` — remove inherited layout
    placeholders AND set `showMasterSp="0"` so master shapes don't bleed
    through onto the grafted content.

Historical note (Path D, 2026-05-26)
------------------------------------
This file used to host the legacy chassis-vocabulary skill's full
`compose_deck()` pipeline plus `_role_map_for`, `_blank_unmatched_via_role_map`,
`_PATTERN_LAYOUT_HINTS`, `_apply_overrides`, and ~25 supporting helpers — all
dependent on `twins.selector.load_catalog` and `twins.overrides_resolver`,
modules that no longer exist. v0.1 never reaches those code paths; v0.1 audit
(2026-05-26) flagged them as dead-broken imports (T1.4 in
`_decisions/v0.1-audit-handover-2026-05-26.md`). Deleted in this pass to
prevent future changes reaching them from exploding with ImportError.
The archived legacy skill at `slide-builder_archived_2026-05-26/` retains
the full composer if anyone needs to reference the chassis-vocabulary path.
"""
from __future__ import annotations

import re

from pptx.oxml.ns import qn


def _find_blank_layout(prs):
    """Find a blank slide layout across all masters in `prs`.

    Looks for a layout whose name (case-insensitive, after stripping
    whitespace and leading numeric prefixes like '1_') is exactly 'blank'.
    Scans every slide master because client templates often put their
    blank layout on a non-zero master (FedEx puts it on master 11).
    Falls back to the first master's first layout if no 'blank' is found.
    """
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            n = layout.name.strip().lower()
            n = re.sub(r"^[\d_]+", "", n)  # strip "1_", "12__", etc.
            if n == "blank":
                return layout
    return prs.slide_masters[0].slide_layouts[0]


def _strip_layout_placeholders(slide) -> int:
    """Remove every shape inherited from the slide's layout AND hide all
    master shapes BEFORE copying our twin shapes on top.

    Two-step strip:
      1. Remove layout-level placeholders that were copied onto the slide
         when `add_slide(layout)` was called (Click to add title, sample
         bullets).
      2. Set ``<p:sld showMasterSp="0">`` so master-level shapes (Click to
         edit Master title style, FedEx Proprietary & Confidential footer,
         <Customize with Department> placeholders) do NOT inherit onto the
         slide.

    Background, theme colors, and theme fonts inherit regardless of
    `showMasterSp` — those are not "shapes" in OOXML's sense. So the
    client's brand styling stays; only the leaky placeholder TEXT goes
    away.

    Returns the number of slide-level shapes removed.
    """
    spTree = slide.shapes._spTree
    removed = 0
    for shp in list(slide.shapes):
        try:
            spTree.remove(shp.element)
            removed += 1
        except (ValueError, AttributeError):
            pass

    try:
        slide.element.set("showMasterSp", "0")
    except Exception:
        pass

    return removed


def _clear_existing_slides(prs):
    """Remove any slides already present in the presentation (client
    templates often ship with sample slides we don't want) AND remove
    section groupings from the slide-panel sidebar.
    """
    sldIdLst = prs.slides._sldIdLst
    for sldId in list(sldIdLst):
        rId = sldId.get(qn("r:id"))
        try:
            prs.part.drop_rel(rId)
        except Exception:
            pass
        sldIdLst.remove(sldId)

    # Strip <p14:sectionLst> from the presentation extLst so the slide
    # panel doesn't show stale section groupings ('Brand Elements', 'Begin
    # Building', etc.) from the original template. Sections live under a
    # <p:ext> whose child is <p14:sectionLst>, where p14 is the 2010
    # PowerPoint namespace. Earlier versions of this code used the 2012
    # namespace by mistake and the strip never fired — orphaned section
    # groups bled through grafted decks. Check BOTH known namespaces to
    # survive future schema variants.
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
