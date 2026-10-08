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
    return idx


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

    regular = min(pool, key=lambda f: (abs(f["weight"] - 400), _style_rank(f), f["path"]))
    heavy = [f for f in pool if f["weight"] >= 600 or f["bold"]]
    bold = min(heavy, key=lambda f: (abs(f["weight"] - 700), 0 if f["bold"] else 1,
                                     f["path"])) if heavy else None
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
        for dirs in (([os.path.dirname(path)],) if here not in installed_dirs else ()) + (None,):
            hit = pick_family_faces(me["typo_family"], dirs)
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
