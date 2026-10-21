"""_chrome_schema.py — pydantic schema for <template-stem>.chrome.yml.

Single source of truth for client-template layout chrome geometry. Written by
register_template.py at registration time; consumed by finalize_deck.py +
build_deck.py at build time.

Two layout classes:

  body-canonical
    Blank-ish body + chrome frame. Master decorates; layout is mostly empty.
    Slide Lab uses CANONICAL positions (see CANONICAL_* constants below) for
    title/subtitle/footnote/source/page-number. Position fields on
    LayoutChrome stay None. ~90% of consulting body layouts.

  bespoke
    Art-directed (cover, section divider, dark hero). Chrome IS the slide;
    placeholder positions are extracted from the template and stored in
    LayoutChrome's position fields. Helpers use those positions directly.

The chrome.yml file is THE canonical home for client-template-specific
geometry. Layout helpers, QC rules, and twin builders read it via
finalize_deck.py's _ACTIVE_CHROME injection; they never re-encode positions
locally. Numeric coordinate literals outside this module + chrome.yml are
a contract violation enforced by `_contract.py::check_chrome_field_single_source`.

Loud-failure contract
---------------------
Any sidecar/config file whose absence is recoverable must be recovered loudly.
If chrome.yml is missing or any required position field is None for a bespoke
layout, helpers raise ChromeSidecarMissingError. Silent fallback to hardcoded
defaults is the slot-mapping bug class — see feedback_sidecar_fallback_must_be_loud.

Adding a new field
------------------
Bump CHROME_SCHEMA_VERSION_CURRENT. Update SUPPORTED_SCHEMA_VERSIONS to gate
which versions readers accept. Re-register every template to repopulate.
"""
from __future__ import annotations

import re

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ValidationError

# Bumped when the schema shape changes. Stay in lockstep with register_template
# (writer) and finalize_deck (reader).
#
# Schema version 2 adds the body-canonical layout-inheritance fields:
#   title_placeholder_idx, body_top_y_px, body_bottom_y_px, body_overlay_hex.
# Version-1 chrome.yml is still readable — validate_chrome_dict defaults the
# new fields to None so version-1 sidecars load without re-registration.
# Templates already registered at version 1 keep working in "strip-and-redraw"
# mode until they are re-registered.
CHROME_SCHEMA_VERSION_CURRENT: int = 2
SUPPORTED_SCHEMA_VERSIONS: tuple[int, ...] = (1, 2)


# ---------------------------------------------------------------------------
# Canvas <-> EMU helpers
# ---------------------------------------------------------------------------
#
# python-pptx convention at 96 DPI is 1 px = 9525 EMU. Slide Lab locked the
# sketch-path HTML render canvas at 1280×720, which makes the
# px↔EMU mapping exact: 12,192,000 EMU (the standard 16:9 slide width) ÷
# 1280 px = 9525. There is no scaling factor — one HTML pixel is one OOXML
# EMU step.
#
# These helpers are the canonical location for that conversion. Used by
# register_template.py (which extracts placeholder geometry from PPTX
# layout XML) and by the sketch-path translator agent when it converts
# HTML pixel coordinates from `getComputedStyle()` into `Emu(...)` kwargs
# for `slide.shapes.add_shape(...)`. No magic 9525s elsewhere — see
# `_contract.py::check_chrome_field_single_source` for the contract test.
EMU_PER_PX_AT_1280: int = 9525


def emu_to_px(emu: int) -> int:
    """Convert OOXML EMU to HTML pixel at the locked 1280×720 canvas scale."""
    return int(round(int(emu) / EMU_PER_PX_AT_1280))


def px_to_emu(px: int) -> int:
    """Convert HTML pixel to OOXML EMU at the locked 1280×720 canvas scale."""
    return int(round(int(px) * EMU_PER_PX_AT_1280))


def _emu_to_px_dict(emu_box: dict) -> dict:
    """Convert a {x,y,width,height,...} EMU dict to its pixel equivalent.

    Used by register_template.py to derive `BoxPx` fields from the EMU
    values it reads off PPTX layout placeholders.
    """
    return {k: emu_to_px(v) for k, v in emu_box.items()}


# ---------------------------------------------------------------------------
# Canonical body-canonical chrome positions
# ---------------------------------------------------------------------------
#
# These are the positions Slide Lab uses for body-canonical layouts where the
# master decorates and the layout is intentionally mostly-empty. Living here
# (and not in twins/helpers.py) keeps chrome geometry in a single source of
# truth — the same file the contract test allowlists.
#
# 1280x720 reference canvas; px units, 96 DPI assumed.

# Title block — bottom-anchored (feedback_title_bottom_anchor: 2-line titles
# grow UPWARD, never displace subtitle).
CANONICAL_TITLE_X: int = 64
CANONICAL_TITLE_Y: int = 20
CANONICAL_TITLE_W: int = 1000
CANONICAL_TITLE_H: int = 80
CANONICAL_TITLE_FONT_PT: int = 28

# Subtitle — single-line italic, just below title bottom.
CANONICAL_SUBTITLE_H: int = 26
CANONICAL_SUBTITLE_FONT_PT: int = 16

# Footer invariant zone (feedback_invariant_zone_chrome): footnote + source +
# page-number only. No ACCENTURE/DRAFT/CONFIDENTIAL tags.
CANONICAL_FOOTNOTE_X: int = 58
CANONICAL_FOOTNOTE_Y: int = 672
CANONICAL_FOOTNOTE_W: int = 1164
CANONICAL_FOOTNOTE_H: int = 16
CANONICAL_FOOTNOTE_FONT_PX: int = 10

CANONICAL_SOURCE_X: int = 58
CANONICAL_SOURCE_Y: int = 688
CANONICAL_SOURCE_W: int = 1100
CANONICAL_SOURCE_H: int = 16
CANONICAL_SOURCE_FONT_PX: int = 10

CANONICAL_PAGE_NUMBER_X: int = 1170
CANONICAL_PAGE_NUMBER_Y: int = 688
CANONICAL_PAGE_NUMBER_W: int = 52
CANONICAL_PAGE_NUMBER_H: int = 16
CANONICAL_PAGE_NUMBER_FONT_PX: int = 11

# Body-zone fallbacks for body-canonical layouts that lack title / footer
# placeholders during registration. Used only when register_template cannot
# locate the inherited placeholder bounds; real templates populate these
# fields per layout in chrome.yml.
# Chrome normalization (owner's rule, 2026-10-08): on every finished slide
# Slide Lab sets the takeaway, footnote(s) and source line itself, whatever
# the designer drew (twins/composer.py normalize_chrome).
#   takeaway: under the title (this gap below the title box, when the layout
#             has no takeaway slot), at the title's text left edge, the
#             template's Subtitle-slot size, else CHROME_TAKEAWAY_FONT_PT.
#   source:   at the template's source position, title's text left edge.
#   footnotes: stacked upward directly above the source line.
CHROME_TAKEAWAY_FONT_PT: int = 16
CHROME_TAKEAWAY_GAP_PX: int = 8
CHROME_NOTE_FONT_PT: int = 9
CHROME_NOTE_GAP_PX: int = 2
CHROME_PAGE_NUMBER_GAP_PX: int = 8

# Section tag (owner's decision, 2026-10-09): the brief's small label above
# the title ("THE MARKET"), drawn by Slide Lab, never by the designer. Left at
# the title's text edge, its box bottom this gap above the title box top, in
# the template's accent color (white on a dark slide; the main text color when
# the accent reads under SECTION_TAG_MIN_CONTRAST on the page), bold small
# caps, the template's body font. A layout with its own section-tag slot gets
# the tag in that slot instead (see SECTION_TAG_SLOT_NAMES). A template with no room above its title box stops the
# build with a plain message instead of guessing a place.
SECTION_TAG_NAME: str = "section-tag"
SECTION_TAG_FONT_PT: float = 10.5
SECTION_TAG_H_PX: int = 20
SECTION_TAG_GAP_PX: int = 6
# Page types that never carry the tag (also: bespoke layouts without a page
# number, which are covers and dividers).
SECTION_TAG_SKIP_PAGE_TYPES: tuple[str, ...] = (
    "cover", "divider", "section-divider", "section", "closing", "end", "back-cover")
# A template's own section-tag slot (2026-10-14): a BODY placeholder named
# like one of these in the top band of the page. When a layout has one,
# registration records it (LayoutChrome.section_tag_placeholder_idx) and
# finalize writes the tag into it in the template's own style instead of
# drawing a loose box. One client template's "Breadcrumb" slot is the case
# that started it: its loose tag was drawn in a pale yellow on white.
SECTION_TAG_SLOT_NAMES: tuple[str, ...] = (
    "breadcrumb", "bread crumb", "section tag", "section-tag", "section name",
    "section", "tracker")
# The slot counts only when it starts in this top share of the page.
SECTION_TAG_SLOT_MAX_TOP_SHARE: float = 0.2
# Readable text (WCAG AA for normal text). A loose tag in a highlight color
# below this against the page background uses the main text color instead.
SECTION_TAG_MIN_CONTRAST: float = 4.5


def is_section_tag_slot_name(name: str | None) -> bool:
    """True for a placeholder NAME that says it holds the section tag
    ("Breadcrumb", "Section tag 3", "Tracker"). PowerPoint's own numbering
    suffix is ignored."""
    import re as _re
    n = _re.sub(r"\s+\d+$", "", (name or "").strip().lower())
    n = _re.sub(r"\s+placeholder$", "", n)
    return n in SECTION_TAG_SLOT_NAMES


def contrast_ratio(hex_a: str, hex_b: str) -> float | None:
    """WCAG contrast ratio of two 'RRGGBB' colors (1.0 to 21.0); None when
    either is not a 6-digit hex color."""
    def _lum(h):
        h = (h or "").lstrip("#")
        if len(h) != 6:
            return None
        try:
            c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        except ValueError:
            return None
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    la, lb = _lum(hex_a), _lum(hex_b)
    if la is None or lb is None:
        return None
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

CANONICAL_BODY_TOP_Y: int = 110
CANONICAL_BODY_BOTTOM_Y: int = 660


# ---------------------------------------------------------------------------
# Named text slots (a BODY placeholder that does a chrome job)
# ---------------------------------------------------------------------------
#
# Many templates make the takeaway line and the source line ordinary text
# (BODY) placeholders and say what they are only in the name: "Subtitle",
# "Takeaway", "Source". Registration used to count only PowerPoint's own
# SUBTITLE / FOOTER placeholder types, so on those templates the takeaway was
# drawn as a loose shape and the source line had no home (2026-10-06).

_SUBTITLE_NAMES = ("subtitle", "sub-title", "sub title", "subheading", "sub-heading",
                   "sub heading", "subhead", "takeaway", "take-away", "take away")
_SOURCE_NAMES = ("source", "sources", "footnote", "footnotes", "foot note")


def slot_role_from_name(name: str | None) -> tuple[str, int] | None:
    """('subtitle' | 'source', rank) for a placeholder whose NAME says it holds
    the takeaway line or the source line; None otherwise. Lower rank = a
    stronger name ('Subtitle' beats 'Takeaway', 'Source' beats 'Footnote').
    PowerPoint's own numbering suffix ('Subtitle 2') is ignored."""
    import re as _re
    n = _re.sub(r"\s+\d+$", "", (name or "").strip().lower())
    n = _re.sub(r"\s+placeholder$", "", n)
    if not n:
        return None
    for rank, key in enumerate(_SUBTITLE_NAMES):
        if n == key or n.startswith(key + " ") or n.endswith(" " + key):
            return "subtitle", (0 if rank < 7 else 2)     # Subtitle/Subheading beat Takeaway
    for rank, key in enumerate(_SOURCE_NAMES):
        if n == key or n.startswith(key + " ") or n.endswith(" " + key):
            return "source", (0 if rank < 2 else 1)
    return None


# ---------------------------------------------------------------------------
# Which loose shape on a finished slide is the page takeaway, the source line
# or a footnote (one rule, used by chrome_rules.normalize_chrome and finalize)
# ---------------------------------------------------------------------------
#
# The chrome placement moves and restyles these shapes. It used to take ANY
# loose text box whose name started "subtitle" or "takeaway" as the takeaway,
# and "source" / "footnote" as a source line or footnote, so a designer's
# bottom band named "takeaway-bar" was pulled up under the title, restyled, or
# deleted as a "second copy" (2026-10-09). Now:
#
#   page takeaway  the layout's registered takeaway slot, a SUBTITLE
#                  placeholder, a loose box named exactly "subtitle" (anywhere),
#                  or a "subtitle-..." / "subtitle_..." / "Subtitle 2" name only
#                  when it sits in the top 35% of the page. A name starting
#                  "takeaway" never counts (that is a bottom band or card).
#   source/footnote  a loose box named "source..." / "footnote..." only when it
#                  sits in the bottom 25% of the page or its text starts like
#                  one ("Source", "Note", "1.", "*").
# Names "subtitle", "source-..." and "footnote-..." are reserved for those
# jobs; designers name a bottom band "band-..." or "so-what-...".

TAKEAWAY_TOP_SHARE: float = 0.35
NOTE_BOTTOM_SHARE: float = 0.75
_SUBTITLE_VARIANT_RE = None
_NOTE_TEXT_RE = None


def _shape_ph(shape) -> tuple[int | None, int | None]:
    """(placeholder type, idx), or (None, None) for a loose shape."""
    try:
        if not shape.is_placeholder:
            return None, None
        pf = shape.placeholder_format
        return int(pf.type or 0), int(pf.idx)
    except Exception:
        return None, None


def _shape_name(shape) -> str:
    try:
        return (shape.name or "").strip().lower()
    except Exception:
        return ""


def _shape_text(shape) -> str:
    try:
        return (shape.text_frame.text or "").strip() if shape.has_text_frame else ""
    except Exception:
        return ""


def slide_height_emu(slide, default: int = 720 * EMU_PER_PX_AT_1280) -> int:
    """The height of the presentation `slide` belongs to (EMU)."""
    try:
        return int(slide.part.package.presentation_part.presentation.slide_height) or default
    except Exception:
        return default


def is_page_takeaway(shape, slide_h_emu: int, takeaway_idx: int | None = None) -> bool:
    """True when `shape` is the slide's page takeaway (the line under the
    title), by the one rule above."""
    import re as _re
    global _SUBTITLE_VARIANT_RE
    t, idx = _shape_ph(shape)
    if t is not None:
        return (takeaway_idx is not None and idx == takeaway_idx) or t == 4   # 4 = SUBTITLE
    name = _shape_name(shape)
    if name == "subtitle":
        return True
    if _SUBTITLE_VARIANT_RE is None:
        _SUBTITLE_VARIANT_RE = _re.compile(r"^subtitle[\s\-_\d]")
    if not _SUBTITLE_VARIANT_RE.match(name):
        return False
    try:
        return shape.top is not None and int(shape.top) < TAKEAWAY_TOP_SHARE * slide_h_emu
    except Exception:
        return False


def note_role(shape, slide_h_emu: int) -> str | None:
    """'source' / 'footnote' for a loose shape that is the slide's source line
    or a footnote by the rule above; None otherwise (placeholders: None, the
    caller reads their slot type)."""
    import re as _re
    global _NOTE_TEXT_RE
    t, _idx = _shape_ph(shape)
    if t is not None:
        return None
    name = _shape_name(shape)
    role = "source" if name.startswith("source") else (
        "footnote" if name.startswith("footnote") else None)
    if role is None:
        return None
    try:
        low = shape.top is not None and int(shape.top) >= NOTE_BOTTOM_SHARE * slide_h_emu
    except Exception:
        low = False
    if low:
        return role
    if _NOTE_TEXT_RE is None:
        _NOTE_TEXT_RE = _re.compile(r"^\s*(sources?\b|notes?\b|\d{1,2}\.|\*)", _re.I)
    return role if _NOTE_TEXT_RE.match(_shape_text(shape)) else None


def canonical_title_box() -> "BoxPx":
    return BoxPx(
        x_px=CANONICAL_TITLE_X, y_px=CANONICAL_TITLE_Y,
        w_px=CANONICAL_TITLE_W, h_px=CANONICAL_TITLE_H,
        font_pt=CANONICAL_TITLE_FONT_PT, anchor="bottom",
    )


def canonical_subtitle_box() -> "BoxPx":
    return BoxPx(
        x_px=CANONICAL_TITLE_X,
        y_px=CANONICAL_TITLE_Y + CANONICAL_TITLE_H + 8,
        w_px=CANONICAL_TITLE_W - 120,
        h_px=CANONICAL_SUBTITLE_H,
        font_pt=CANONICAL_SUBTITLE_FONT_PT, anchor="top",
    )


def canonical_footnote_box() -> "BoxPx":
    return BoxPx(
        x_px=CANONICAL_FOOTNOTE_X, y_px=CANONICAL_FOOTNOTE_Y,
        w_px=CANONICAL_FOOTNOTE_W, h_px=CANONICAL_FOOTNOTE_H,
        font_pt=None, anchor="top",
    )


def canonical_source_box() -> "BoxPx":
    return BoxPx(
        x_px=CANONICAL_SOURCE_X, y_px=CANONICAL_SOURCE_Y,
        w_px=CANONICAL_SOURCE_W, h_px=CANONICAL_SOURCE_H,
        font_pt=None, anchor="top",
    )


def canonical_page_number_box() -> "BoxPx":
    return BoxPx(
        x_px=CANONICAL_PAGE_NUMBER_X, y_px=CANONICAL_PAGE_NUMBER_Y,
        w_px=CANONICAL_PAGE_NUMBER_W, h_px=CANONICAL_PAGE_NUMBER_H,
        font_pt=None, anchor="top",
    )


# ---------------------------------------------------------------------------
# Title-wrap line count
# ---------------------------------------------------------------------------

class TitleMetricsUnavailableError(RuntimeError):
    """Raised when title line-count cannot be measured because the configured
    TTF font cannot be loaded or Pillow is missing. Per
    feedback_sidecar_fallback_must_be_loud — silent char-count fallback was
    the bug class we're not repeating. Recovery: re-run register_template
    so it records the brand TTF path in brand.yml.
    """


import functools as _functools


@_functools.lru_cache(maxsize=1)
def _font_index() -> dict[str, str]:
    """Build a `lowercased-filename -> absolute-path` index of every font on
    disk, scanned ONCE per process (lru_cache). The OS font dirs are visited in
    preference order (Windows user → system → macOS → Linux) and the FIRST
    occurrence of a filename wins, so the resolution order matches the old
    per-call scan. Flat dirs use a cheap listdir; the nested Linux trees are
    walked once here instead of on every _find_brand_ttf call (registration
    calls it ~10x per template — that was ~10 full /usr walks).
    """
    import os
    flat_dirs = [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts"),
        r"C:\Windows\Fonts",
        os.path.expanduser("~/Library/Fonts"),
        "/Library/Fonts",
        "/System/Library/Fonts",
    ]
    walk_dirs = [
        os.path.expanduser("~/.fonts"),
        os.path.expanduser("~/.local/share/fonts"),
        "/usr/share/fonts",
        "/usr/local/share/fonts",
    ]
    idx: dict[str, str] = {}
    for d in flat_dirs:
        if not d or not os.path.isdir(d):
            continue
        try:
            for fn in os.listdir(d):
                full = os.path.join(d, fn)
                if os.path.isfile(full):
                    idx.setdefault(fn.lower(), full)
        except OSError:
            pass
    for d in walk_dirs:
        if not d or not os.path.isdir(d):
            continue
        for root, _dirs, files in os.walk(d):
            for fn in files:
                idx.setdefault(fn.lower(), os.path.join(root, fn))
    # Office cloud fonts (Aptos, Aptos Display, ...) are downloaded on demand
    # into FontCache\<n>\CloudFonts\<Family>\<number>.ttf and never appear in
    # the Windows font folders, so Aptos templates skipped the title-fit check
    # (2026-10-14). File names are numbers: keyed by family folder + file so
    # they never shadow one another; font_faces() matches them by name table.
    for cloud in _cloud_font_dirs():
        for root, _dirs, files in os.walk(cloud):
            fam = os.path.basename(root).lower()
            for fn in files:
                idx.setdefault(f"cloudfonts/{fam}/{fn.lower()}", os.path.join(root, fn))
    return idx


def _cloud_font_dirs() -> list[str]:
    """Every %LOCALAPPDATA%\\Microsoft\\FontCache\\<n>\\CloudFonts folder."""
    import glob
    import os
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        return []
    return sorted(d for d in glob.glob(os.path.join(base, "Microsoft", "FontCache",
                                                    "*", "CloudFonts"))
                  if os.path.isdir(d))


def _find_brand_ttf(font_name: str | None = None) -> str | None:
    """Discover a brand TTF on disk by name. Returns absolute path or None.

    Looks `font_name` up in a cached index of the OS font directories
    (Windows / macOS / Linux — all scanned regardless of current OS, so this
    stays additive). Case-insensitive. Used as a transitional fallback when
    brand.yml doesn't yet record the TTF path; once register_template writes the
    resolved path into brand.yml, callers prefer that and skip this. With no
    `font_name` there is nothing to search for, so it returns None.
    """
    if not font_name:
        return None
    return _font_index().get(font_name.lower())


# ---------------------------------------------------------------------------
# Font faces read from the fonts' own name tables
# ---------------------------------------------------------------------------
#
# A font file's NAME says little: one brand family shipped its narrow
# ("condensed") face as the bare <Family>.ttf, and registration, which guessed
# the file by name, copied that face. Every sketch was then drawn about a
# quarter narrower than the finished slide (2026-10-08). Faces are picked from
# what each file says about itself: family (name ids 16, else 1), style (17,
# else 2), weight and width (OS/2).

_WIDTH_WORDS = {1: "ultra-condensed", 2: "extra-condensed", 3: "condensed",
                4: "semi-condensed", 5: "normal width", 6: "semi-expanded",
                7: "expanded", 8: "extra-expanded", 9: "ultra-expanded"}
_FONT_EXTS = (".ttf", ".otf", ".ttc")


def _read_face(path: str) -> dict | None:
    """One face's facts from its name and OS/2 tables, or None if unreadable."""
    try:
        from fontTools.ttLib import TTFont
        f = TTFont(path, lazy=True, fontNumber=0)
        n = f["name"]
        fam1 = n.getDebugName(1) or ""
        sub2 = n.getDebugName(2) or ""
        os2 = f["OS/2"]
        face = {
            "path": str(path),
            "family": fam1,
            "style": sub2,
            "typo_family": n.getDebugName(16) or fam1,
            "typo_style": n.getDebugName(17) or sub2,
            "full_name": n.getDebugName(4) or f"{fam1} {sub2}".strip(),
            "weight": int(os2.usWeightClass),
            "width": int(os2.usWidthClass),
            "italic": bool(os2.fsSelection & 1) or "italic" in sub2.lower()
                      or "oblique" in sub2.lower(),
            "bold": bool(os2.fsSelection & 32) or "bold" in sub2.lower(),
        }
        f.close()
        return face
    except Exception:
        return None


_FACES_MEM: dict = {}


def font_faces(dirs: list | tuple | None = None) -> list[dict]:
    """Every readable font face, with its own name-table facts.

    dirs=None: the fonts installed on this computer (the same folders as
    _font_index), cached on disk and rebuilt when the set of font files
    changes. dirs given: just the font files in those folders (not cached on
    disk; used for a template's bundled fonts and by the tests)."""
    import json
    import os
    import tempfile
    if dirs is not None:
        paths = []
        for d in dirs:
            if d and os.path.isdir(str(d)):
                paths += [os.path.join(str(d), fn) for fn in sorted(os.listdir(str(d)))
                          if fn.lower().endswith(_FONT_EXTS)]
        key = tuple(sorted((p, os.path.getmtime(p)) for p in paths))
        if key not in _FACES_MEM:
            _FACES_MEM[key] = [f for f in (_read_face(p) for p in paths) if f]
        return _FACES_MEM[key]
    paths = sorted({p for p in _font_index().values() if p.lower().endswith(_FONT_EXTS)})
    import hashlib
    sig = hashlib.sha1("|".join(paths).encode("utf-8", "replace")).hexdigest()[:16]
    if ("installed", sig) in _FACES_MEM:
        return _FACES_MEM[("installed", sig)]
    try:
        import _scratch
        cache = _scratch.cache_dir() / "slidelab_font_name_tables.json"
    except Exception:
        cache = Path(tempfile.gettempdir()) / "slidelab_font_name_tables.json"
    faces = None
    try:
        data = json.loads(cache.read_text(encoding="utf-8"))
        if data.get("sig") == sig:
            faces = data["faces"]
    except Exception:
        faces = None
    if faces is None:
        faces = [f for f in (_read_face(p) for p in paths) if f]
        try:
            cache.write_text(json.dumps({"sig": sig, "faces": faces}), encoding="utf-8")
        except OSError:
            pass
    _FACES_MEM[("installed", sig)] = faces
    return faces


def installed_families() -> set[str]:
    """Lower-case family names (legacy and typographic) of every installed font."""
    out: set[str] = set()
    for f in font_faces():
        for k in ("family", "typo_family"):
            if f.get(k):
                out.add(f[k].strip().lower())
    return out


def describe_face(face: dict | None) -> str:
    """'Fict Sans Regular (normal width, weight 400)'."""
    if not face:
        return "(none)"
    return (f"{face['typo_family']} {face['typo_style']} "
            f"({_WIDTH_WORDS.get(face['width'], 'width ' + str(face['width']))}, "
            f"weight {face['weight']})")


def pick_family_faces(family: str, dirs: list | tuple | None = None) -> dict:
    """The regular and bold faces of `family`, chosen from the fonts' own data.

    Matches the family name against each face's family names (typographic and
    legacy) and, failing that, a full face name ("Fict Sans Bold" finds its
    family). Regular = upright, normal width when the family has one, weight
    nearest 400. Bold = upright, same width, weight nearest 700 (600 and up).
    Returns {"regular", "bold": path or None, "regular_face", "bold_face":
    face dicts or None, "warnings": [plain-English lines]}.
    """
    out = {"regular": None, "bold": None, "regular_face": None, "bold_face": None,
           "warnings": []}
    want = (family or "").strip().lower()
    if not want:
        return out
    faces = font_faces(dirs)
    fam = [f for f in faces if want in (f["typo_family"].strip().lower(),
                                        f["family"].strip().lower())]
    if not fam:
        hit = next((f for f in faces if f["full_name"].strip().lower() == want), None)
        if hit is not None:
            tf = hit["typo_family"].strip().lower()
            fam = [f for f in faces if f["typo_family"].strip().lower() == tf]
    upright = [f for f in fam if not f["italic"]] or fam
    if not upright:
        return out
    normal = [f for f in upright if f["width"] == 5]
    pool = normal or upright
    if not normal:
        widths = sorted({f["width"] for f in upright}, key=lambda w: abs(w - 5))
        pool = [f for f in upright if f["width"] == widths[0]]
        out["warnings"].append(
            f"only a {_WIDTH_WORDS.get(widths[0], 'non-standard width')} version of "
            f"{family!r} is installed, not its normal-width face: sketches and fit "
            f"checks will be drawn narrower or wider than PowerPoint shows the text. "
            f"Install the normal-width face and register the template again.")

    def _style_rank(f):
        s = f["style"].strip().lower()
        return 0 if s in ("regular", "normal", "book", "roman") else 1

    # On a tie, a face whose own (legacy) family is exactly the name asked for
    # wins: Aptos Display's faces also call their typographic family "Aptos",
    # and the file path alone picked Aptos Display for "Aptos" (2026-10-14).
    def _other_family(f):
        return 0 if f["family"].strip().lower() == want else 1

    regular = min(pool, key=lambda f: (abs(f["weight"] - 400), _style_rank(f),
                                       _other_family(f), f["path"]))
    heavy = [f for f in pool if f["weight"] >= 600 or f["bold"]]
    bold = min(heavy, key=lambda f: (abs(f["weight"] - 700), 0 if f["bold"] else 1,
                                     _other_family(f), f["path"])) if heavy else None
    out.update(regular=regular["path"], regular_face=regular,
               bold=bold["path"] if bold else None, bold_face=bold)
    return out


def bold_ttf_for(ttf: str | None) -> str | None:
    """The bold face of the same family as `ttf` (a filename or a path), or
    None. Titles are usually bold, and measuring them with the regular face
    under-counted wraps: on the 10/02 showcase 5 titles wrapped that the
    regular-face count said fit.

    Read from the fonts' own data: the family `ttf` belongs to, then its bold
    face in the same folder (a template's bundled fonts) or among the
    installed fonts. File-name guesses are the last resort."""
    if not ttf:
        return None
    import os
    path = str(ttf)
    me = _read_face(path) if os.path.isfile(path) else None
    if me is not None:
        here = os.path.normcase(os.path.dirname(os.path.abspath(path)))
        installed_dirs = {os.path.normcase(os.path.dirname(p)) for p in _font_index().values()}
        # The face's own family first ("Aptos Display" finds Aptos Display
        # Bold), then its typographic family ("Aptos" for that same face).
        families = list(dict.fromkeys(n for n in (me["family"], me["typo_family"]) if n))
        for dirs in (([os.path.dirname(path)],) if here not in installed_dirs else ()) + (None,):
            for fam_name in families:
                hit = pick_family_faces(fam_name, dirs)
                bf = hit.get("bold_face")
                if bf and os.path.normcase(bf["path"]) != os.path.normcase(path) \
                        and bf["width"] == me["width"]:
                    return bf["path"]
    idx = _font_index()
    name = os.path.basename(path).lower()
    stem, ext = os.path.splitext(name)
    cands = [stem + "bd", stem + "b", stem + "-bold", stem.replace("-regular", "-bold"),
             stem.replace("regular", "bold"), stem + "bold"]
    for c in cands:
        hit = idx.get(c + (ext or ".ttf"))
        if hit and c != stem:
            return hit
    return None


_HEAVY_FACE_WORDS = ("semibold", "semi bold", "demibold", "demi bold", "extrabold",
                     "extra bold", "ultrabold", "bold", "black", "heavy")


def face_name_is_bold(face_name: str | None) -> bool:
    """True for a theme face name that names a heavy face ('Fict Sans Bold')."""
    low = (face_name or "").strip().lower()
    return any(low.endswith(" " + w) for w in _HEAVY_FACE_WORDS)


def title_measure_ttf(regular: str | None, bold_path: str | None = None, *,
                      title_bold: bool = False, heading_face: str = "") -> str | None:
    """The font file to measure titles with: the bold face when the template's
    title style is bold or the theme's heading face is itself a bold face
    (titles then draw in it), else the regular face."""
    if title_bold or face_name_is_bold(heading_face):
        return bold_path or bold_ttf_for(regular) or regular
    return regular


def template_title_is_bold(template_path) -> bool:
    """True when the template's master title style (or its first layout's
    title placeholder) is bold."""
    try:
        from pptx import Presentation
        prs = Presentation(str(template_path))
    except Exception:
        return False
    return presentation_title_is_bold(prs)


def presentation_title_is_bold(prs) -> bool:
    """template_title_is_bold for an already-open Presentation."""
    try:
        from pptx.oxml.ns import qn
        master = prs.slide_masters[0]._element
        ts = master.find(qn("p:txStyles"))
        lvl = ts.find(qn("p:titleStyle")).find(qn("a:lvl1pPr")) if ts is not None else None
        rpr = lvl.find(qn("a:defRPr")) if lvl is not None else None
        return bool(rpr is not None and rpr.get("b") in ("1", "true"))
    except Exception:
        return False


def count_wrapped_lines(text: str, ttf_path: str | None,
                         size_pt: int, box_width_px: int) -> int:
    """Return the number of visual lines `text` wraps to in a box of width
    `box_width_px` at `size_pt` using the TTF at `ttf_path`.

    Greedy word-wrap (matches PowerPoint's behavior closely enough for the
    threshold check). Raises TitleMetricsUnavailableError when Pillow is
    missing or the TTF can't be loaded — this is a loud-fail surface per
    feedback_sidecar_fallback_must_be_loud. The caller is responsible for
    either re-registering the template to record a valid TTF path OR
    falling back to a char-count proxy and warning the operator.
    """
    if not text:
        return 0
    try:
        from PIL import ImageFont
    except ImportError as e:
        raise TitleMetricsUnavailableError(
            f"Pillow not available for title-wrap measurement: {e}. "
            f"Pillow is a pinned dependency — check requirements.txt."
        ) from e
    if not ttf_path:
        raise TitleMetricsUnavailableError(
            "No TTF path supplied for title-wrap measurement. Recovery: "
            "re-run register_template so brand.yml records the resolved "
            "title font path."
        )
    try:
        # 96 DPI: px = pt * 96/72
        font = ImageFont.truetype(ttf_path, int(round(size_pt * 96 / 72)))
    except (OSError, IOError) as e:
        raise TitleMetricsUnavailableError(
            f"Cannot load TTF {ttf_path!r}: {e}. Recovery: re-run "
            f"register_template to discover and record a valid TTF path."
        ) from e
    words = text.split()
    if not words:
        return 0
    lines = 0
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if font.getlength(trial) <= box_width_px:
            current = trial
        else:
            lines += 1
            current = word
    if current:
        lines += 1
    return lines


# ---------------------------------------------------------------------------
# Text fit: does every text box, table cell and placeholder fit as PowerPoint
# sets it? (owner's decision, 2026-10-09)
# ---------------------------------------------------------------------------
#
# Measured with the template's own font files (brand.yml), from each font's
# advance widths, without a renderer, so a check takes milliseconds per slide.
# It replaced finalize's character-count guess (characters x 0.6 x size, only
# boxes under 200 px, never table cells), which missed "FY2 H1" at 14 pt bold
# in a 68 px column: 66 px of text, and PowerPoint wrapped it (slide 38,
# 2026-10-09). Findings:
#   broken_word     a word wider than its box: PowerPoint breaks it mid-word (stop)
#   table_overflow  a table that grows past its frame or the body area (stop)
#   short_label_wraps  a label of two words or fewer that wraps (flag)
#   near_limit      one-line text that uses more than FIT_NEAR_LIMIT (92%) of the
#                   usable width, or the last line of wrapped text past
#                   FIT_NEAR_LIMIT_WRAPPED (98%): PowerPoint may wrap it (flag)
#   row_grows       a table row whose text is taller than the row's set height, or a
#                   table that grows into empty space below it (flag)
# A table that grows into another shape, past the body area or off the page is
# table_overflow (stop).
#
# Checked 2026-10-09 against PowerPoint itself: "FY2 H1" (Arial Bold 12 pt) set
# in 64 to 78 px cells and text boxes wrapped where these widths say (fits at
# 97% of the room, wraps at 100.4%), and row heights matched PowerPoint's
# within a pixel (lines x 1.2 x size, less a fifth of the size, plus margins).
# But the slide 38 page that shipped wrapped had "FY2 H1" at 14 pt bold in a
# 68 px room: 63.3 px by these widths (93%), and PowerPoint still wrapped it.
# So one-line text is flagged from 92% (the owner's number; 95% would miss
# that page). On a 71-slide client deck that flags about 90 one-line
# texts (spot-checked in PowerPoint pictures: they fit), so a near-limit line
# is an Advisory flag, never a Major and never fixed automatically. The last
# line of text that already wraps counts only from 98% (at 92% it added
# about 40 more flags on long sentences in wide boxes).

FIT_NEAR_LIMIT: float = 0.92
FIT_NEAR_LIMIT_WRAPPED: float = 0.98
FIT_STOP_KINDS: tuple[str, ...] = ("broken_word", "table_overflow")
_FIT_DEFAULT_INSET_EMU = 91440        # PowerPoint's default left/right text margin
_FIT_DEFAULT_TB_INSET_EMU = 45720     # and top/bottom
_FIT_CELL_LR_EMU = 91440              # table cell margins when the cell sets none
_FIT_CELL_TB_EMU = 45720
_FIT_TOLERANCE_PX = 2.0


class TextMeasurer:
    """Text width (px at 96 DPI) from a font file's own advance widths: exact
    at any size (Pillow rounds each letter to whole pixels at small sizes)."""
    _metrics: dict = {}

    def __init__(self, ttf_path: str, size_pt: float, spacing_pt: float = 0.0):
        if ttf_path not in TextMeasurer._metrics:
            from fontTools.ttLib import TTFont
            f = TTFont(ttf_path, lazy=True, fontNumber=0)
            adv = {g: m[0] for g, m in f["hmtx"].metrics.items()}
            upm = f["head"].unitsPerEm
            TextMeasurer._metrics[ttf_path] = (f.getBestCmap() or {}, adv, upm,
                                               adv.get(".notdef", upm // 2))
        self.cmap, self.adv, upm, self.default = TextMeasurer._metrics[ttf_path]
        self.k = float(size_pt) * 96.0 / 72.0 / upm
        self.spc = float(spacing_pt) * 96.0 / 72.0      # letter spacing per character

    def getlength(self, s: str) -> float:
        return (sum(self.adv.get(self.cmap.get(ord(ch)), self.default) for ch in s) * self.k
                + self.spc * len(s))


def fit_fonts(heading: str = "", body: str = "", heading_ttf: str = "",
              heading_bold_ttf: str = "", body_ttf: str = "", body_bold_ttf: str = "") -> dict:
    """The template's fonts for the fit check: names and font files (brand.yml
    paths first, the installed faces of the family second)."""
    out = {"heading": heading or "", "body": body or ""}
    for role, reg, bold in (("heading", heading_ttf, heading_bold_ttf),
                            ("body", body_ttf, body_bold_ttf)):
        fam = out[role]
        faces = pick_family_faces(fam) if fam else {}
        r = reg if reg and Path(reg).is_file() else (faces.get("regular") or _find_brand_ttf(fam))
        b = bold if bold and Path(bold).is_file() else (faces.get("bold") or bold_ttf_for(r) or r)
        out[role + "_regular"], out[role + "_bold"] = r, b
    if not out.get("body_regular"):
        out["body_regular"], out["body_bold"] = out.get("heading_regular"), out.get("heading_bold")
    if not out.get("heading_regular"):
        out["heading_regular"], out["heading_bold"] = out.get("body_regular"), out.get("body_bold")
    return out


def _fit_attr_chain(shape, para, run, attr: str):
    """A run attribute (sz / b) as PowerPoint inherits it: the run, the
    paragraph's defaults, the shape's list style, then the layout and master
    placeholder it inherits from, then the master's text styles."""
    from pptx.oxml.ns import qn
    if run is not None:
        rpr = run._r.find(qn("a:rPr"))
        if rpr is not None and rpr.get(attr) is not None:
            return rpr.get(attr)
    ppr = para._p.find(qn("a:pPr"))
    lvl = int(ppr.get("lvl", "0")) + 1 if ppr is not None else 1
    if ppr is not None:
        d = ppr.find(qn("a:defRPr"))
        if d is not None and d.get(attr) is not None:
            return d.get(attr)
    chain = [shape._element]
    try:
        base = shape._base_placeholder if shape.is_placeholder else None
        while base is not None:
            chain.append(base._element)
            base = getattr(base, "_base_placeholder", None)
    except Exception:
        pass
    for el in chain:
        lst = el.find(".//" + qn("a:lstStyle"))
        if lst is not None:
            d = lst.find(qn(f"a:lvl{lvl}pPr") + "/" + qn("a:defRPr"))
            if d is not None and d.get(attr) is not None:
                return d.get(attr)
    try:
        if shape.is_placeholder:
            t = int(shape.placeholder_format.type or 0)
            master = shape.part.slide_layout.slide_master._element
            ts = master.find(qn("p:txStyles"))
            style = ts.find(qn("p:titleStyle") if t in (1, 3) else qn("p:bodyStyle"))
            d = style.find(qn(f"a:lvl{lvl}pPr") + "/" + qn("a:defRPr"))
            if d is not None and d.get(attr) is not None:
                return d.get(attr)
    except Exception:
        pass
    return None


def _fit_shape_inset(shape, attr: str) -> int:
    """A text margin (EMU): the shape's own, else the layout's and master's
    placeholder it inherits from, else PowerPoint's default."""
    from pptx.oxml.ns import qn
    chain = [shape._element]
    try:
        base = shape._base_placeholder if shape.is_placeholder else None
        while base is not None:
            chain.append(base._element)
            base = getattr(base, "_base_placeholder", None)
    except Exception:
        pass
    for el in chain:
        bp = el.find(".//" + qn("a:bodyPr"))
        if bp is not None and bp.get(attr) is not None:
            try:
                return int(bp.get(attr))
            except ValueError:
                pass
    return _FIT_DEFAULT_INSET_EMU


def _fit_line_px(para, size_pt: float) -> float:
    """One line's height in px: the paragraph's exact spacing, else its
    percentage of PowerPoint's single line (1.2 x the size)."""
    from pptx.oxml.ns import qn
    ppr = para._p.find(qn("a:pPr"))
    ln = ppr.find(qn("a:lnSpc")) if ppr is not None else None
    if ln is not None:
        pts = ln.find(qn("a:spcPts"))
        if pts is not None and pts.get("val"):
            return int(pts.get("val")) / 100 * 96 / 72
        pct = ln.find(qn("a:spcPct"))
        if pct is not None and pct.get("val"):
            return size_pt * 1.2 * int(pct.get("val")) / 100000 * 96 / 72
    return size_pt * 1.2 * 96 / 72


def _fit_paragraphs(shape, frame, fonts: dict, heading: bool):
    """[(text, measurer, size_pt, line_px)] per non-empty paragraph, measured
    in the template font of its biggest run; None measurer when no font file."""
    out = []
    for para in frame.paragraphs:
        # a line break inside the paragraph (a:br) reads as "\v": a new line
        text = (para.text or "").replace("\v", "\n")
        if not text.strip():
            continue
        best = None
        for r in para.runs:
            if not r.text.strip():
                continue
            sz = _fit_attr_chain(shape, para, r, "sz")
            pt = int(sz) / 100 if sz else 18.0
            try:
                from twins.helpers import snap_font_pt
                pt = snap_font_pt(pt) or pt
            except Exception:
                pass
            b = _fit_attr_chain(shape, para, r, "b") in ("1", "true")
            face = (r.font.name or "").strip()
            is_head = heading or face.startswith("+mj") or (
                face and face.lower() == (fonts.get("heading") or "").lower()
                and face.lower() != (fonts.get("body") or "").lower())
            try:
                spc = int(_fit_attr_chain(shape, para, r, "spc") or 0) / 100
            except ValueError:
                spc = 0.0
            if best is None or pt > best[0]:
                best = (pt, b, is_head, spc)
        if best is None:
            continue
        pt, b, is_head, spc = best
        role = "heading" if is_head else "body"
        path = fonts.get(role + ("_bold" if b else "_regular")) or fonts.get(role + "_regular")
        try:
            m = TextMeasurer(path, pt, spc) if path else None
        except Exception:
            m = None
        out.append((text, m, pt, _fit_line_px(para, pt)))
    return out


_HYPHEN_BREAK = re.compile(r"(?<=[^\W\d_]-)(?=[^\W\d_])|(?<=[\u2013\u2014])(?=\S)")


def hyphen_pieces(word: str) -> list[str]:
    """A word cut where PowerPoint may end a line inside it: after an ordinary
    hyphen with a letter on both sides ("multi-|year"), and after an en or em
    dash. Never after a non-breaking hyphen (U+2011), between digits
    ("2025-2030"), at a word's start ("-5%"), or after "/" ("and/or"; not
    confirmed in PowerPoint). Chrome breaks after the hyphen too, so a
    predictor that didn't saw "Whole fleets, under multi-year" as one more
    line than the design and shrank the text a size (2026-10-13)."""
    parts = _HYPHEN_BREAK.split(word)
    return [q for q in parts if q]


def _fit_wrap(text: str, m: "TextMeasurer", width_px: float) -> tuple[list[float], float]:
    """Greedy word wrap as PowerPoint does it: (width of each line, widest
    piece that can't be broken), in px. A line may end at a space or after a
    hyphen or dash inside a word (hyphen_pieces)."""
    widths, cur, widest = [], 0.0, 0.0
    space = m.getlength(" ")
    for hard in text.split("\n"):
        cur = 0.0
        for word in hard.split():
            for k, piece in enumerate(hyphen_pieces(word)):
                wl = m.getlength(piece)
                widest = max(widest, wl)
                gap = space if (k == 0 and cur) else 0.0
                if cur and cur + gap + wl > width_px:
                    widths.append(cur)
                    cur = wl
                else:
                    cur = cur + gap + wl
        widths.append(cur)
    return widths, widest


def _fit_shapes(shapes, depth=0):
    for sh in shapes:
        try:
            if sh.shape_type == 6:                       # a group: look inside
                yield from _fit_shapes(sh.shapes, depth + 1)
                continue
        except Exception:
            pass
        yield sh, depth


def _fit_label(shape) -> str:
    try:
        return shape.name or "<unnamed>"
    except Exception:
        return "<unnamed>"


def fit_findings(slide, fonts: dict, body_bottom_px: float | None = None,
                 near_limit: float = FIT_NEAR_LIMIT,
                 near_limit_wrapped: float = FIT_NEAR_LIMIT_WRAPPED) -> dict:
    """Measure every text box, table cell and placeholder on `slide`.

    fonts: fit_fonts(...). body_bottom_px: the bottom of the layout's body
    area (a table may not grow past it). Returns {"findings": [{"kind",
    "shape", "text", "detail", "stop"}], "measured": n, "unmeasured": n}."""
    findings: list[dict] = []
    seen = {"measured": 0, "unmeasured": 0}

    def add(kind, shape_name, text, detail):
        findings.append({"kind": kind, "shape": shape_name, "text": text[:60],
                         "detail": detail, "stop": kind in FIT_STOP_KINDS})

    def check_frame(sh, frame, width_px, heading, where, cell=False):
        if width_px <= 4:
            return
        from pptx.oxml.ns import qn
        bp = frame._txBody.find(qn("a:bodyPr")) if hasattr(frame, "_txBody") else None
        is_cell = cell is not False
        if not is_cell and bp is not None and bp.get("wrap") == "none":
            return          # a text box that does not wrap (a table cell always wraps)
        if bp is not None and bp.get("vert") not in (None, "horz"):
            return          # vertical text: not measured across
        if hasattr(cell, "get") and cell.get("vert") not in (None, "horz"):
            return
        for text, m, pt, _lh in _fit_paragraphs(sh, frame, fonts, heading):
            if m is None:
                seen["unmeasured"] += 1
                continue
            seen["measured"] += 1
            for seg in (x for x in text.split("\n") if x.strip()):
                lines, widest = _fit_wrap(seg, m, width_px)
                words = seg.split()
                if widest > width_px + 0.5:
                    add("broken_word", where, seg,
                        f"a word {widest:.0f} px wide in {width_px:.0f} px at {pt:g} pt: "
                        f"PowerPoint breaks it in the middle")
                elif len(words) <= 2 and len(lines) > 1:
                    add("short_label_wraps", where, seg,
                        f"a {len(words)}-word label wraps onto {len(lines)} lines "
                        f"({width_px:.0f} px at {pt:g} pt)")
                elif lines and lines[-1] > (near_limit if len(lines) == 1
                                            else near_limit_wrapped) * width_px:
                    add("near_limit", where, seg,
                        (f"it uses {100 * lines[-1] / width_px:.0f}% of the {width_px:.0f} px "
                         f"width at {pt:g} pt: PowerPoint may wrap it onto a second line")
                        if len(lines) == 1 else
                        (f"its last line uses {100 * lines[-1] / width_px:.0f}% of the "
                         f"{width_px:.0f} px width at {pt:g} pt: PowerPoint may add a line"))

    def rows_needed(sh, tbl):
        """[(set height px, needed height px)] per row."""
        out = []
        spans = []        # (first row, rows spanned, needed px) for vertically merged cells
        cols = [int(c.width or 0) / EMU_PER_PX_AT_1280 for c in tbl.columns]
        for r in tbl.rows:
            set_h = int(r.height or 0) / EMU_PER_PX_AT_1280
            need = 0.0
            for ci, cell in enumerate(r.cells):
                try:
                    tc = cell._tc
                    if tc.get("hMerge") or tc.get("vMerge"):
                        continue
                    span = int(tc.get("gridSpan", "1"))
                    rspan = int(tc.get("rowSpan", "1"))
                except Exception:
                    span, rspan = 1, 1
                w = sum(cols[ci:ci + span]) - (
                    int(cell.margin_left if cell.margin_left is not None else _FIT_CELL_LR_EMU)
                    + int(cell.margin_right if cell.margin_right is not None else _FIT_CELL_LR_EMU)
                ) / EMU_PER_PX_AT_1280
                label = f"{_fit_label(sh)} row {len(out) + 1} col {ci + 1}"
                tcpr = tc.find("{http://schemas.openxmlformats.org/drawingml/2006/main}tcPr")
                check_frame(sh, cell.text_frame, w, False, label,
                            cell=tcpr if tcpr is not None else True)
                h = (int(cell.margin_top if cell.margin_top is not None else _FIT_CELL_TB_EMU)
                     + int(cell.margin_bottom if cell.margin_bottom is not None else _FIT_CELL_TB_EMU)
                     ) / EMU_PER_PX_AT_1280
                # PowerPoint's row: margins + each line's pitch, less a fifth of
                # the last line's size (measured on Arial 10 to 16 pt, 2026-10-09)
                last_pt = 0.0
                for text, m, pt, lh in _fit_paragraphs(sh, cell.text_frame, fonts, False):
                    n = len(_fit_wrap(text, m, w)[0]) if m is not None else text.count("\n") + 1
                    h += n * lh
                    last_pt = pt
                if last_pt:
                    h -= 0.2 * last_pt * 96 / 72
                if rspan > 1:
                    spans.append((len(out), rspan, h))     # shared by the rows it spans
                else:
                    need = max(need, h)
            out.append((set_h, need))
        # a merged cell grows only the last row it spans, and only by what the
        # spanned rows together lack
        for first, rspan, h in spans:
            rows = out[first:first + rspan]
            have = sum(max(s, n) for s, n in rows)
            if rows and h > have:
                s, n = rows[-1]
                out[first + len(rows) - 1] = (s, max(s, n) + (h - have))
        return out

    slide_h_px = slide_height_emu(slide) / EMU_PER_PX_AT_1280
    tops = []           # top-level shapes with text or a fill: what a growing table can run into
    for o in slide.shapes:
        try:
            ox, oy = int(o.left or 0) / EMU_PER_PX_AT_1280, int(o.top or 0) / EMU_PER_PX_AT_1280
            ow, oh = int(o.width or 0) / EMU_PER_PX_AT_1280, int(o.height or 0) / EMU_PER_PX_AT_1280
        except Exception:
            continue
        if ow <= 0 or oh <= 0 or (ow >= 1200 and oh >= 700):
            continue
        tops.append((o._element, ox, oy, ox + ow, oy + oh, _fit_label(o)))

    for sh, depth in _fit_shapes(slide.shapes):
        name = _fit_label(sh)
        try:
            ph_t = int(sh.placeholder_format.type) if sh.is_placeholder else None
        except Exception:
            ph_t = None
        if ph_t == 13 or name.lower().startswith("page-number"):
            continue                                       # the template's page number
        if getattr(sh, "has_table", False) and sh.has_table:
            rows = rows_needed(sh, sh.table)
            grows = [(i + 1, s, n) for i, (s, n) in enumerate(rows) if n > s + _FIT_TOLERANCE_PX]
            if grows:
                i, s, n = grows[0]
                add("row_grows", name, "",
                    f"{len(grows)} row(s) need more height than set (row {i}: "
                    f"{n:.0f} px of text in a {s:.0f} px row): PowerPoint makes them taller")
            frame_h = int(sh.height or 0) / EMU_PER_PX_AT_1280
            total = sum(max(s, n) for s, n in rows)
            top = int(sh.top or 0) / EMU_PER_PX_AT_1280
            left = int(sh.left or 0) / EMU_PER_PX_AT_1280
            right = left + int(sh.width or 0) / EMU_PER_PX_AT_1280
            grown = top + total
            if depth == 0 and grows and total > frame_h + _FIT_TOLERANCE_PX:
                # Growing into empty space below is only a flag (row_grows);
                # growing into another shape, past the body area or off the
                # page is a stop.
                hit = None
                for o in tops:
                    if o[0] is sh._element:
                        continue
                    ox0, oy0, ox1, oy1, oname = o[1:]
                    if (top + frame_h - _FIT_TOLERANCE_PX <= oy0 < grown - _FIT_TOLERANCE_PX
                            and min(ox1, right) - max(ox0, left) > 4):
                        hit = (oname, oy0)
                        break
                limit = body_bottom_px or slide_h_px
                if hit:
                    add("table_overflow", name, "",
                        f"the table grows from {frame_h:.0f} to {total:.0f} px tall and runs into "
                        f"{hit[0]!r} (which starts at {hit[1]:.0f} px)")
                elif grown > limit + _FIT_TOLERANCE_PX:
                    add("table_overflow", name, "",
                        f"the table grows from {frame_h:.0f} to {total:.0f} px tall, its bottom "
                        f"at {grown:.0f} px, past the "
                        f"{'body area bottom' if body_bottom_px else 'page bottom'} at {limit:.0f} px")
            continue
        if not getattr(sh, "has_text_frame", False) or not sh.has_text_frame:
            continue
        if not (sh.text_frame.text or "").strip():
            continue
        try:
            w_emu = int(sh.width or 0)
        except Exception:
            w_emu = 0
        l_in = _fit_shape_inset(sh, "lIns")
        r_in = _fit_shape_inset(sh, "rIns")
        width_px = (w_emu - l_in - r_in) / EMU_PER_PX_AT_1280
        check_frame(sh, sh.text_frame, width_px, ph_t in (1, 3) or name.lower() == "title", name)
    return {"findings": findings, **seen}


def fit_problem_line(f: dict) -> str:
    """One plain line for a fit finding."""
    what = {"broken_word": "Word broken in the middle",
            "table_overflow": "Table runs past its space",
            "short_label_wraps": "Short label wraps",
            "near_limit": "Text close to wrapping",
            "row_grows": "Table rows taller than set"}.get(f.get("kind"), "Text fit")
    txt = f" \"{f['text']}\"" if f.get("text") else ""
    return f"{what}: {f.get('shape')}{txt}, {f.get('detail')}"


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class BoxPx(BaseModel):
    """A bounding box in 1280x720 reference-canvas px coordinates."""
    x_px: int
    y_px: int
    w_px: int
    h_px: int
    font_pt: int | None = None
    anchor: Literal["top", "middle", "bottom"] = "top"


class LayoutChrome(BaseModel):
    """Chrome spec for one named layout in the client template."""
    name: str
    layout_class: Literal["body-canonical", "bespoke"]
    text_role: Literal["dark_on_light", "light_on_dark"]
    background: Literal["light", "dark"]
    has_page_number: bool
    # Position fields — populated only for bespoke layouts; None for
    # body-canonical (canonical_*_box() constants supply the geometry).
    title: BoxPx | None = None
    subtitle: BoxPx | None = None
    footnote: BoxPx | None = None
    source: BoxPx | None = None
    page_number: BoxPx | None = None
    # Body-canonical layout-inheritance fields.
    # For body-canonical layouts ONLY:
    #   title_placeholder_idx: which inherited placeholder holds the title
    #     (so finalize_deck writes the slide title text into the layout's
    #      title placeholder rather than drawing a free-floating textbox).
    #   subtitle_placeholder_idx: same idea for the subtitle. When set, the
    #     worker skips drawing a free-floating subtitle textbox and finalize
    #     populates the inherited subtitle placeholder instead. Subtitle
    #     drift was traced to the absence of
    #     this field — the worker drew subtitle at a hardcoded canonical
    #     position while the real subtitle placeholder sat empty.
    #   body_top_y_px / body_bottom_y_px: drawable zone between the inherited
    #     title placeholder bottom and the footer placeholder top — patterns
    #     compose body content inside this zone.
    # For bespoke layouts these remain None (covers/dividers keep today's
    # strip-and-redraw path).
    title_placeholder_idx: int | None = None
    subtitle_placeholder_idx: int | None = None
    body_top_y_px: int | None = None
    body_bottom_y_px: int | None = None
    # Title placeholder geometry (px) + controlled title font size, captured for
    # body-canonical layouts. Additive/optional (older chrome.yml files omit
    # them → None → callers fall back to canonical). Used to (a) render the
    # free-floating takeaway line as wide as the title, and (b) populate the
    # title placeholder at a consistent title_font_pt. Also feed the title-wrap
    # fit calc (finalize) which already reads title_box_width_px / title_font_pt.
    title_box_x_px: int | None = None
    title_box_y_px: int | None = None
    title_box_width_px: int | None = None
    title_box_height_px: int | None = None
    title_font_pt: int | None = None
    # The layout's source-line slot when it is an ordinary text (BODY)
    # placeholder named "Source" / "Sources" / "Footnote" near the bottom,
    # rather than a PowerPoint footer placeholder. Without it the source line
    # had nowhere to go on such templates (2026-10-06). finalize writes the
    # sketch's source line (template field 'footer') into this idx first.
    # Older chrome.yml files omit it -> None -> footer placeholder only.
    source_placeholder_idx: int | None = None
    # The layout's own section-tag slot: a BODY placeholder named "Breadcrumb"
    # / "Section" / "Tracker" (_chrome_schema.SECTION_TAG_SLOT_NAMES) in the
    # top band of the page. finalize writes the brief's section tag into it,
    # in the template's own style (2026-10-14). Older chrome.yml files omit
    # it -> None -> the loose section-tag box above the title.
    section_tag_placeholder_idx: int | None = None
    # What the layout really looks like behind the body (scripts/_template_bg):
    # its background color ('RRGGBB'; the first color for a gradient, None for a
    # picture) and kind (solid / gradient / picture / pattern / theme-style),
    # and the left/right edges of its text area in px. Sketches are drawn on
    # this background and inside these margins. Older chrome.yml files omit
    # them -> None -> build prep reads them from the template instead.
    background_hex: str | None = None
    background_kind: str | None = None
    body_left_px: int | None = None
    body_right_px: int | None = None
    # body_overlay_hex retained for backward-compat with existing chrome.yml
    # files; never populated by current register_template and unread by any
    # downstream code. Slated for removal once existing templates are
    # re-registered.
    body_overlay_hex: str | None = None


class ChromeSpec(BaseModel):
    """Top-level chrome.yml document — version + sha8 + per-layout chrome."""
    schema_version: int = CHROME_SCHEMA_VERSION_CURRENT
    source_template_sha8: str
    layouts: dict[str, LayoutChrome]


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ChromeSidecarMissingError(RuntimeError):
    """Raised when chrome.yml is absent OR a required field is None.

    Silent fallback to hardcoded defaults is the slot-mapping bug class.
    Helpers MUST raise this rather than substitute a default — production-grade
    bar requires the operator to re-register the template instead of shipping
    a slide built against guessed geometry.

    See feedback_sidecar_fallback_must_be_loud.md.
    """


class ChromeSchemaError(RuntimeError):
    """Raised when chrome.yml fails validation or has unsupported version."""


class ChromeLayoutMissingError(RuntimeError):
    """Raised when a slide references a layout name that does not exist in
    the loaded chrome.yml.

    Silent fallback to a default layout was the bug that hid a
    chrome regression — slides resolved to a stand-in layout
    whose geometry didn't match the actual template. Helpers MUST raise this
    instead of substituting a default.

    See feedback_sidecar_fallback_must_be_loud.md.
    """


# Note: LegacyTemplateLayoutError (raised when an older flat sidecar layout
# is detected) lives in twins/client_theme.py, where it's the only thing
# that raises it. The duplicate definition here was removed —
# previously both files defined the same name with different parent classes
# (RuntimeError vs FileNotFoundError), which would have caught operators by
# surprise if anyone tried to except-block both.


# ---------------------------------------------------------------------------
# Loader / validator
# ---------------------------------------------------------------------------

def validate_chrome_dict(raw: dict[str, Any]) -> ChromeSpec:
    """Validate a parsed dict against ChromeSpec. Raises ChromeSchemaError on failure."""
    version = raw.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ChromeSchemaError(
            f"chrome.yml schema_version={version!r} not supported. "
            f"Supported: {SUPPORTED_SCHEMA_VERSIONS}. "
            f"Re-register the template (register_template.py propose -> commit)."
        )
    try:
        return ChromeSpec.model_validate(raw)
    except ValidationError as e:
        raise ChromeSchemaError(
            f"chrome.yml failed validation:\n{e}"
        ) from e


def load_chrome_yml(chrome_yml_path: Path) -> ChromeSpec:
    """Load + validate <template-stem>.chrome.yml.

    Raises ChromeSidecarMissingError if the file does not exist;
    ChromeSchemaError on validation failure.
    """
    if not chrome_yml_path.exists():
        raise ChromeSidecarMissingError(
            f"chrome.yml not found at {chrome_yml_path}. "
            f"Register the template first: "
            f"register_template.py propose -> commit."
        )
    import yaml
    raw = yaml.safe_load(chrome_yml_path.read_text(encoding="utf-8")) or {}
    return validate_chrome_dict(raw)


def dump_chrome_yml(spec: ChromeSpec, chrome_yml_path: Path) -> None:
    """Serialize ChromeSpec to YAML at the given path."""
    import yaml
    chrome_yml_path.parent.mkdir(parents=True, exist_ok=True)
    data = spec.model_dump(mode="python", exclude_none=False)
    text = yaml.safe_dump(data, sort_keys=False, default_flow_style=False)
    chrome_yml_path.write_text(text, encoding="utf-8")
