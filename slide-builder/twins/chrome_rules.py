"""Chrome normalization: the takeaway, footnotes and source line in fixed places.

Owner's rule (2026-10-08): on every finished slide Slide Lab places the
takeaway, the footnote(s) and the source line itself, in one fixed position
and size, whatever the designer drew:

  takeaway   directly under the title, at the title's text left edge, in the
             template's own Subtitle-slot size (else 16 pt), not bold, in the
             template's main text color; the same on every slide of the deck
  source     in the bottom band at the template's source position (its
             registered Source slot, else its footer slot, else Slide Lab's
             standard source line), at the title's text left edge, 9 pt, even
             where the template centers its footer box
  footnotes  directly above the source line, stacked upward when there are
             several, same left edge, 9 pt

normalize_chrome() runs per slide in finalize (scripts/finalize_deck.py), so
it holds for every path (direct, sketch, redesign, QC fix), and on the
registration mock slide (scripts/register_template.py). Roles are found from
the template's fields (registered takeaway / source slot ids, SUBTITLE and
FOOTER placeholders) and, for loose shapes, by one rule in
scripts/_chrome_schema.py (is_page_takeaway, note_role): the takeaway is a box
named exactly "subtitle", or "subtitle-..." in the top 35% of the page (never a
"takeaway..." name: that is a bottom band); a "source..." / "footnote..." box
counts only in the bottom 25% of the page or when its text starts like a
source or note. A shape that matches nothing is not moved.

place_section_tag() draws the brief's section tag (the small label above the
title) in one fixed style per template (owner's decision, 2026-10-09).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from pptx.oxml.ns import qn

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import _chrome_schema as CS  # noqa: E402

_DEFAULT_INSET_EMU = 91440            # PowerPoint's default inner margin, 0.1 in
_EMU_PX = CS.EMU_PER_PX_AT_1280
_TITLE_TYPES = (1, 3)
_SUBTITLE_TYPES = (4,)
_FOOTER_TYPES = (15,)
_SLIDE_NUMBER_TYPES = (13,)


def _ph_type(shape):
    try:
        if not shape.is_placeholder:
            return None
        return int(shape.placeholder_format.type or 0)
    except Exception:
        return None


def _ph_idx(shape):
    try:
        return int(shape.placeholder_format.idx) if shape.is_placeholder else None
    except Exception:
        return None


def _inset(shape, attr: str) -> int:
    """Effective inner margin (EMU): the shape's own, else its layout's and
    master's placeholder, else PowerPoint's default."""
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
    return _DEFAULT_INSET_EMU


def _text_of(shape) -> str:
    try:
        return (shape.text_frame.text or "").strip() if shape.has_text_frame else ""
    except Exception:
        return ""


def _name(shape) -> str:
    try:
        return (shape.name or "").strip().lower()
    except Exception:
        return ""


def _size_from(el) -> float | None:
    """A text size (pt) written on a placeholder: its list style's first
    level, else any run, end-of-paragraph or default run size."""
    if el is None:
        return None
    lst = el.find(".//" + qn("a:lstStyle"))
    if lst is not None:
        node = lst.find(qn("a:lvl1pPr") + "/" + qn("a:defRPr"))
        if node is not None and node.get("sz"):
            return int(node.get("sz")) / 100
    for tag in ("a:rPr", "a:endParaRPr", "a:defRPr"):
        for node in el.iter(qn(tag)):
            if node.get("sz"):
                return int(node.get("sz")) / 100
    return None


def _slot_size_pt(layout, idx: int) -> float | None:
    """The takeaway slot's own text size on `layout` (placeholder idx), read
    through the layout and then the master, as PowerPoint inherits it."""
    ph = next((p for p in layout.placeholders if _ph_idx(p) == idx), None)
    if ph is None:
        return None
    size = _size_from(ph._element)
    if size:
        return size
    master = layout.slide_master
    t = _ph_type(ph) or 2
    for mp in master.placeholders:
        mt = _ph_type(mp)
        if (t in _TITLE_TYPES and mt in _TITLE_TYPES) or (t not in _TITLE_TYPES and mt == 2):
            size = _size_from(mp._element)
            if size:
                return size
    ts = master._element.find(qn("p:txStyles"))
    if ts is not None:
        node = ts.find(qn("p:bodyStyle") + "/" + qn("a:lvl1pPr") + "/" + qn("a:defRPr"))
        if node is not None and node.get("sz"):
            return int(node.get("sz")) / 100
    return None


def template_takeaway_pt(prs, chrome_spec=None, layout_chrome=None) -> float:
    """The deck's one takeaway size: the template's own Subtitle-slot size
    when a registered layout has a takeaway slot, else 16 pt."""
    from twins.composer import _find_named_layout
    cands = []
    if layout_chrome is not None and getattr(layout_chrome, "subtitle_placeholder_idx", None) is not None:
        cands.append((layout_chrome.name, layout_chrome.subtitle_placeholder_idx))
    for name, lc in (getattr(chrome_spec, "layouts", None) or {}).items():
        if getattr(lc, "subtitle_placeholder_idx", None) is not None:
            cands.append((name, lc.subtitle_placeholder_idx))
    for name, idx in cands:
        lay = _find_named_layout(prs, name)
        if lay is None:
            continue
        size = _slot_size_pt(lay, int(idx))
        if size:
            return float(size)
    return float(CS.CHROME_TAKEAWAY_FONT_PT)


def _title_geometry(slide, layout_chrome) -> tuple[int, int, int]:
    """(text left, text right, box bottom) of the slide's title, in EMU."""
    left, right, _top, bottom = _title_frame(slide, layout_chrome)
    return left, right, bottom


def _title_frame(slide, layout_chrome) -> tuple[int, int, int, int]:
    """(text left, text right, box top, box bottom) of the slide's title, in EMU."""
    t_idx = getattr(layout_chrome, "title_placeholder_idx", None) if layout_chrome else None
    title = next((sh for sh in slide.shapes if _ph_type(sh) in _TITLE_TYPES
                  or (t_idx is not None and _ph_idx(sh) == t_idx)), None)
    if title is None:
        title = next((sh for sh in slide.shapes if _name(sh).startswith("title")
                      and getattr(sh, "has_text_frame", False)), None)
    if title is None:
        try:
            title = next((ph for ph in slide.slide_layout.placeholders
                          if _ph_type(ph) in _TITLE_TYPES), None)
        except Exception:
            title = None
    if title is not None and title.left is not None and title.width:
        left, width = int(title.left), int(title.width)
        top, height = int(title.top or 0), int(title.height or 0)
        return (left + _inset(title, "lIns"), left + width - _inset(title, "rIns"),
                top, top + height)
    tx = getattr(layout_chrome, "title_box_x_px", None) if layout_chrome else None
    tw = getattr(layout_chrome, "title_box_width_px", None) if layout_chrome else None
    ty = getattr(layout_chrome, "title_box_y_px", None) if layout_chrome else None
    th = getattr(layout_chrome, "title_box_height_px", None) if layout_chrome else None
    if None in (tx, tw, ty, th):
        b = CS.canonical_title_box()
        tx, tw, ty, th = b.x_px, b.w_px, b.y_px, b.h_px
    return (tx * _EMU_PX + _DEFAULT_INSET_EMU, (tx + tw) * _EMU_PX - _DEFAULT_INSET_EMU,
            ty * _EMU_PX, (ty + th) * _EMU_PX)


def source_top_emu(slide, layout_chrome) -> int:
    """The template's source position (EMU from the top of the slide): the
    registered Source slot on the layout, else the layout's footer slot,
    else the layout's recorded source box / Slide Lab's standard one."""
    s_idx = getattr(layout_chrome, "source_placeholder_idx", None) if layout_chrome else None
    try:
        layout_phs = list(slide.slide_layout.placeholders)
    except Exception:
        layout_phs = []
    if s_idx is not None:
        ph = next((p for p in layout_phs if _ph_idx(p) == s_idx), None)
        if ph is not None and ph.top is not None:
            return int(ph.top)
    ph = next((p for p in layout_phs if _ph_type(p) in _FOOTER_TYPES), None)
    if ph is not None and ph.top is not None:
        return int(ph.top)
    box = None
    if layout_chrome is not None:
        try:
            from twins.helpers import _chrome_box_for
            box = _chrome_box_for(layout_chrome, "source")
        except Exception:
            box = None
    box = box or CS.canonical_source_box()
    return int(box.y_px) * _EMU_PX


def drawn_takeaway_top_emu(title_bottom_emu: int) -> int:
    """Where a takeaway with no template slot goes: just under the title box."""
    return int(title_bottom_emu) + CS.CHROME_TAKEAWAY_GAP_PX * _EMU_PX


def section_tag_top_emu(title_top_emu: int) -> int:
    """Top of the section tag box: just above the title box (may be < 0,
    meaning there is no room)."""
    return int(title_top_emu) - CS.SECTION_TAG_GAP_PX * _EMU_PX - CS.SECTION_TAG_H_PX * _EMU_PX


def _set_runs(shape, *, size_pt=None, bold=None, color_scheme=None,
              clear_italic=False) -> None:
    for p in shape.text_frame.paragraphs:
        pPr = p._p.get_or_add_pPr()
        pPr.set("algn", "l")
        for a in ("indent", "marL"):
            if pPr.get(a) is not None:
                del pPr.attrib[a]
        holders = [r._r.get_or_add_rPr() for r in p.runs]
        end = p._p.find(qn("a:endParaRPr"))
        if end is not None:
            holders.append(end)
        for rpr in holders:
            if size_pt is not None:
                rpr.set("sz", str(int(round(size_pt * 100))))
            if bold is not None:
                rpr.set("b", "1" if bold else "0")
            if clear_italic and rpr.get("i") is not None:
                del rpr.attrib["i"]
            if color_scheme:
                for tag in ("a:solidFill", "a:gradFill", "a:noFill", "a:pattFill"):
                    for f in rpr.findall(qn(tag)):
                        rpr.remove(f)
                fill = rpr.makeelement(qn("a:solidFill"), {})
                fill.append(fill.makeelement(qn("a:schemeClr"), {"val": color_scheme}))
                # solidFill comes before the font and link children of rPr
                later = {qn(t) for t in ("a:highlight", "a:uLnTx", "a:uLn", "a:uFillTx",
                                          "a:uFill", "a:latin", "a:ea", "a:cs", "a:sym",
                                          "a:hlinkClick", "a:hlinkMouseOver", "a:rtl",
                                          "a:extLst")}
                anchor = next((c for c in rpr if c.tag in later), None)
                if anchor is not None:
                    anchor.addprevious(fill)
                else:
                    rpr.append(fill)


def _set_frame(shape, *, left: int, top: int, width: int, height: int | None) -> None:
    shape.left, shape.top = int(left), int(top)
    shape.width = int(max(width, _EMU_PX))
    if height is not None:
        shape.height = int(height)
    bp = shape.text_frame._txBody.find(qn("a:bodyPr"))
    if bp is not None:
        # no inner margin left, top or bottom: the text itself sits at the
        # placed edge, whether the box is the template's slot or a drawn one
        for ins in ("lIns", "tIns", "bIns"):
            bp.set(ins, "0")
        bp.set("wrap", "square")
        bp.set("anchor", "t")


def _lines_estimate(text: str, width_emu: int, size_pt: float) -> int:
    """Rough line count for a short note line (an average letter is half an em)."""
    width_px = max(1.0, width_emu / _EMU_PX)
    per_line = max(8, int(width_px / (size_pt * 96 / 72 * 0.5)))
    return max(1, sum(max(1, -(-len(para) // per_line)) for para in (text or "").split("\n")))


def normalize_chrome(slide, layout_chrome=None, *, takeaway_pt: float | None = None,
                     on_dark: bool | None = None) -> dict:
    """Place the slide's takeaway, footnotes and source line by the owner's
    rule (module docstring). Returns {"takeaway", "source", "footnotes"}:
    how many of each were placed."""
    done = {"takeaway": 0, "source": 0, "footnotes": 0}
    if layout_chrome is not None and getattr(layout_chrome, "layout_class", "") == "bespoke" \
            and not getattr(layout_chrome, "has_page_number", True):
        return done          # a cover or section divider keeps its own art-directed lines
    if on_dark is None:
        on_dark = getattr(layout_chrome, "text_role", "dark_on_light") == "light_on_dark"
    t_pt = float(takeaway_pt or CS.CHROME_TAKEAWAY_FONT_PT)
    note_pt = float(CS.CHROME_NOTE_FONT_PT)
    text_left, text_right, title_bottom = _title_geometry(slide, layout_chrome)
    width = max(_EMU_PX * 40, text_right - text_left)
    slide_h = CS.slide_height_emu(slide)
    sub_idx = getattr(layout_chrome, "subtitle_placeholder_idx", None) if layout_chrome else None
    src_idx = getattr(layout_chrome, "source_placeholder_idx", None) if layout_chrome else None

    takeaways, sources, notes, page_nums = [], [], [], []
    for sh in slide.shapes:
        if not getattr(sh, "has_text_frame", False):
            continue
        t, idx, name = _ph_type(sh), _ph_idx(sh), _name(sh)
        if t in _SLIDE_NUMBER_TYPES or name.startswith("page-number"):
            page_nums.append(sh)
            continue
        if not _text_of(sh):
            continue
        # One rule for which shape is the takeaway / source / footnote
        # (_chrome_schema.is_page_takeaway / note_role): a bottom band named
        # "takeaway-bar" or a body row named "source-1" is left alone.
        if CS.is_page_takeaway(sh, slide_h, sub_idx):
            takeaways.append(sh)
        elif (src_idx is not None and idx == src_idx) or t in _FOOTER_TYPES:
            sources.append(sh)
        else:
            role = CS.note_role(sh, slide_h)
            if role == "source":
                sources.append(sh)
            elif role == "footnote":
                notes.append(sh)

    # takeaway: the layout's slot keeps its own height position; a drawn line
    # goes just under the title. Only a second copy of the real takeaway (a
    # shape that passed the same rule, with the same text) is deleted.
    takeaways.sort(key=lambda s: (0 if s.is_placeholder else 1,
                                  0 if _name(s) == "subtitle" else 1))
    for extra in takeaways[1:]:
        if _text_of(extra) == _text_of(takeaways[0]):
            extra._element.getparent().remove(extra._element)
    for sh in takeaways[:1]:
        if sh.is_placeholder and sh.top is not None:
            top, height = int(sh.top), int(sh.height or CS.CANONICAL_SUBTITLE_H * _EMU_PX)
        else:
            top = drawn_takeaway_top_emu(title_bottom)
            height = max(int(sh.height or 0), CS.CANONICAL_SUBTITLE_H * _EMU_PX)
        _set_frame(sh, left=text_left, top=top, width=width, height=height)
        _set_runs(sh, size_pt=t_pt, bold=False, clear_italic=True,
                  color_scheme="bg1" if on_dark else "tx1")
        done["takeaway"] += 1

    # source line: the template slot first; any further source lines stack
    # above it like footnotes
    sources.sort(key=lambda s: (0 if s.is_placeholder else 1, -int(s.top or 0)))
    src_top = source_top_emu(slide, layout_chrome)
    right = text_right
    for pn in page_nums:
        try:
            if pn.left is not None and int(pn.left) > text_left and \
                    abs(int(pn.top or 0) - src_top) < 40 * _EMU_PX:
                right = min(right, int(pn.left) - CS.CHROME_PAGE_NUMBER_GAP_PX * _EMU_PX)
        except Exception:
            pass
    src_w = max(_EMU_PX * 40, right - text_left)
    line_h = int(round(note_pt * 1.2 * 96 / 72 * _EMU_PX))
    stack_top = src_top
    if sources:
        sh = sources[0]
        h = _lines_estimate(_text_of(sh), src_w, note_pt) * line_h
        _set_frame(sh, left=text_left, top=src_top, width=src_w, height=h)
        _set_runs(sh, size_pt=note_pt)
        done["source"] += 1
        notes = sources[1:] + notes

    def _order(s):
        m = re.search(r"(\d+)", _name(s))
        return (int(m.group(1)) if m else 999, int(s.top or 0))
    for sh in sorted(notes, key=_order, reverse=True):
        h = _lines_estimate(_text_of(sh), src_w, note_pt) * line_h
        top = stack_top - CS.CHROME_NOTE_GAP_PX * _EMU_PX - h
        _set_frame(sh, left=text_left, top=top, width=src_w, height=h)
        _set_runs(sh, size_pt=note_pt)
        stack_top = top
        done["footnotes"] += 1
    return done


# ---------------------------------------------------------------------------
# Section tag: the small label above the title (owner's decision, 2026-10-09)
# ---------------------------------------------------------------------------

class SectionTagNoRoomError(RuntimeError):
    """The template's title box sits too close to the top of the page for the
    section tag. Raised instead of guessing another place for it."""


def _no_tag_page(layout_chrome, page_type: str) -> bool:
    if (page_type or "").strip().lower() in CS.SECTION_TAG_SKIP_PAGE_TYPES:
        return True
    if (layout_chrome is not None
            and getattr(layout_chrome, "layout_class", "") == "bespoke"
            and not getattr(layout_chrome, "has_page_number", True)):
        return True               # a cover or a section divider
    name = (getattr(layout_chrome, "name", "") or "").lower()
    return any(w in name for w in ("cover", "divider", "closing"))


def remove_section_tags(slide) -> int:
    """Delete every shape named exactly "section-tag" (never by its text)."""
    gone = 0
    for sh in list(slide.shapes):
        if _name(sh) == CS.SECTION_TAG_NAME:
            sh._element.getparent().remove(sh._element)
            gone += 1
    return gone


def place_section_tag(slide, layout_chrome, text: str | None, *, accent_hex: str,
                      on_dark: bool | None = None, page_type: str = "") -> bool:
    """Draw the brief's section tag above the title in the template's fixed
    style; True when one was drawn.

    Any earlier "section-tag" shape is removed first, so running finalize
    again still leaves one. Nothing is drawn for an empty tag or "(none)", or
    on a cover, divider or closing page. Raises SectionTagNoRoomError when the
    title box leaves no room above it (never guesses another place)."""
    from pptx.util import Emu
    remove_section_tags(slide)
    text = " ".join((text or "").split())
    if not text or text.lower() in ("(none)", "none") or _no_tag_page(layout_chrome, page_type):
        return False
    if on_dark is None:
        on_dark = getattr(layout_chrome, "text_role", "dark_on_light") == "light_on_dark"
    text_left, text_right, title_top, _bottom = _title_frame(slide, layout_chrome)
    h = CS.SECTION_TAG_H_PX * _EMU_PX
    top = section_tag_top_emu(title_top)
    if top < 0:
        lname = getattr(layout_chrome, "name", "(unknown)") if layout_chrome else "(unknown)"
        raise SectionTagNoRoomError(
            f"The section tag {text!r} goes just above the title, but on layout {lname!r} the "
            f"title box starts {int(title_top / _EMU_PX)} px from the top of the page: there "
            f"is no room for a {CS.SECTION_TAG_H_PX} px label above it. Slide Lab does not guess "
            f"another place. Ask the user where the section tag should go on this template "
            f"(or leave the brief's Section tag empty for these pages).")
    width = max(_EMU_PX * 40, text_right - text_left)
    box = slide.shapes.add_textbox(Emu(int(text_left)), Emu(int(top)), Emu(int(width)), Emu(int(h)))
    box.name = CS.SECTION_TAG_NAME
    tf = box.text_frame
    tf.word_wrap = True
    bp = tf._txBody.find(qn("a:bodyPr"))
    for ins in ("lIns", "tIns", "rIns", "bIns"):
        bp.set(ins, "0")
    bp.set("anchor", "b")
    p = tf.paragraphs[0]
    p._p.get_or_add_pPr().set("algn", "l")
    run = p.add_run()
    run.text = text
    rpr = run._r.get_or_add_rPr()
    rpr.set("sz", str(int(round(CS.SECTION_TAG_FONT_PT * 100))))
    rpr.set("b", "1")
    rpr.set("cap", "small")
    fill = rpr.makeelement(qn("a:solidFill"), {})
    color = "FFFFFF" if on_dark else (accent_hex or "").lstrip("#").upper()[:6]
    if len(color) == 6:
        fill.append(fill.makeelement(qn("a:srgbClr"), {"val": color}))
    else:
        fill.append(fill.makeelement(qn("a:schemeClr"), {"val": "accent1"}))
    rpr.append(fill)
    rpr.append(rpr.makeelement(qn("a:latin"), {"typeface": "+mn-lt"}))
    return True



# ---------------------------------------------------------------------------
# The same chrome for the review sketches (2026-10-13)
# ---------------------------------------------------------------------------
#
# Designers used to style the title and takeaway in their sketches by guess:
# sizes from 26 to 37 px, tops from 30 to 62 px, takeaways in three colors,
# because prep never gave them the template's values. The finished deck was
# right (finalize styles these itself); the pictures the user picked from
# were not. chrome_style() returns the values finalize uses, read from the
# same places (the layout's title box, chrome.yml's title size, the
# template's Subtitle-slot size, the theme's text color, the section tag's
# fixed style). Prep writes them as slide_NN/_chrome.css (chrome_css) and in
# plain words in _context.md (chrome_plain_words); render_html.py adds the
# CSS last, so every sketch picture shows the template's real title,
# takeaway and section tag. The HTML file is never changed, and the
# converter reads it without this CSS.

_A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
_DEFAULT_TB_INSET_EMU = 45720         # PowerPoint's default top/bottom margin, 0.05 in
_SCHEME_TO_SLOT = {"tx1": "dk1", "tx2": "dk2", "bg1": "lt1", "bg2": "lt2"}


def _theme_of(master) -> dict:
    """{'colors': {dk1: 'RRGGBB', ...}, 'major': font, 'minor': font,
    'clrmap': {tx1: dk1, ...}} for a slide master."""
    from lxml import etree
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT
    out = {"colors": {}, "major": "", "minor": "", "clrmap": dict(_SCHEME_TO_SLOT)}
    try:
        cm = master._element.find(qn("p:clrMap"))
        if cm is not None:
            for k in ("tx1", "tx2", "bg1", "bg2"):
                if cm.get(k):
                    out["clrmap"][k] = cm.get(k)
    except Exception:
        pass
    try:
        theme = etree.fromstring(master.part.part_related_by(RT.THEME).blob)
    except Exception:
        return out
    a = "{%s}" % _A_NS
    scheme = theme.find(f".//{a}clrScheme")
    if scheme is not None:
        for slot in scheme:
            name = etree.QName(slot).localname
            srgb = slot.find(f"{a}srgbClr")
            sysc = slot.find(f"{a}sysClr")
            if srgb is not None and srgb.get("val"):
                out["colors"][name] = srgb.get("val").upper()
            elif sysc is not None and sysc.get("lastClr"):
                out["colors"][name] = sysc.get("lastClr").upper()
    for kind, key in (("majorFont", "major"), ("minorFont", "minor")):
        node = theme.find(f".//{a}{kind}/{a}latin")
        if node is not None:
            out[key] = node.get("typeface") or ""
    return out


def scheme_hex(val: str, theme: dict) -> str | None:
    """A theme color name (tx1, bg1, accent1, dk2 ...) as 'RRGGBB'."""
    slot = (theme.get("clrmap") or {}).get(val, _SCHEME_TO_SLOT.get(val, val))
    return (theme.get("colors") or {}).get(slot)


def _resolve_color(fill_parent, theme: dict) -> str | None:
    """'RRGGBB' of the <a:solidFill> under fill_parent (an rPr / defRPr), or None."""
    if fill_parent is None:
        return None
    fill = fill_parent.find(qn("a:solidFill"))
    if fill is None:
        return None
    srgb = fill.find(qn("a:srgbClr"))
    if srgb is not None and srgb.get("val"):
        return srgb.get("val").upper()
    sch = fill.find(qn("a:schemeClr"))
    if sch is not None and sch.get("val"):
        return scheme_hex(sch.get("val"), theme)
    return None


def _resolve_font(rpr, theme: dict) -> str | None:
    if rpr is None:
        return None
    latin = rpr.find(qn("a:latin"))
    if latin is None or not latin.get("typeface"):
        return None
    face = latin.get("typeface")
    if face.startswith("+mj"):
        return theme.get("major") or None
    if face.startswith("+mn"):
        return theme.get("minor") or None
    return face


def _title_style(layout, title_ph, theme: dict) -> dict:
    """The template's own title text style: {size_pt, bold, color, font,
    line_pct}, read from the layout's title slot, then the master's title
    slot, then the master's title text style (as PowerPoint inherits it)."""
    chain = []
    if title_ph is not None:
        lst = title_ph._element.find(".//" + qn("a:lstStyle"))
        if lst is not None:
            chain.append(lst.find(qn("a:lvl1pPr")))
    master = layout.slide_master
    for mp in master.placeholders:
        if _ph_type(mp) in _TITLE_TYPES:
            lst = mp._element.find(".//" + qn("a:lstStyle"))
            if lst is not None:
                chain.append(lst.find(qn("a:lvl1pPr")))
            break
    ts = master._element.find(qn("p:txStyles"))
    if ts is not None:
        chain.append(ts.find(qn("p:titleStyle") + "/" + qn("a:lvl1pPr")))
    style = {"size_pt": None, "bold": None, "color": None, "font": None, "line_pct": None}
    for ppr in chain:
        if ppr is None:
            continue
        d = ppr.find(qn("a:defRPr"))
        if d is not None:
            if style["size_pt"] is None and d.get("sz"):
                style["size_pt"] = int(d.get("sz")) / 100
            if style["bold"] is None and d.get("b") is not None:
                style["bold"] = d.get("b") in ("1", "true")
            if style["color"] is None:
                style["color"] = _resolve_color(d, theme)
            if style["font"] is None:
                style["font"] = _resolve_font(d, theme)
        if style["line_pct"] is None:
            sp = ppr.find(qn("a:lnSpc") + "/" + qn("a:spcPct"))
            if sp is not None and sp.get("val"):
                style["line_pct"] = int(sp.get("val")) / 100000
    return style


def _bp_inset(shape, attr: str, default: int) -> int:
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
    return default


def chrome_style(layout_chrome, prs, accent_hex: str = "", *, on_dark: bool | None = None,
                 page_type: str = "", takeaway_pt: float | None = None,
                 section_tag: str | None = None) -> dict | None:
    """The title, takeaway and section tag exactly as finalize styles them on
    this layout, in px at 1280 x 720. None for a cover, divider or other
    art-directed layout (they keep their own lines) or no layout at all.

    {'layout', 'on_dark', 'body_top',
     'title':    {left, top, width, height, pad_l, pad_r, pad_t, pad_b,
                  size_pt, bold, color, font, line_height, anchor: 'bottom'},
     'takeaway': {left, top, width, size_pt, bold: False, color, font,
                  line_height, from_slot},
     'section_tag': {text, left, top, width, height, size_pt, bold: True,
                     small_caps: True, color, font} or None,
     'section_tag_note': why there is none (or '')}"""
    if layout_chrome is None or prs is None:
        return None
    if getattr(layout_chrome, "layout_class", "") == "bespoke" \
            and not getattr(layout_chrome, "has_page_number", True):
        return None
    from twins.composer import _find_named_layout
    layout = _find_named_layout(prs, getattr(layout_chrome, "name", ""))
    if layout is None:
        return None
    layout_dark = getattr(layout_chrome, "text_role", "dark_on_light") == "light_on_dark"
    if on_dark is None:
        on_dark = layout_dark
    theme = _theme_of(layout.slide_master)
    t_idx = getattr(layout_chrome, "title_placeholder_idx", None)
    title_ph = next((p for p in layout.placeholders
                     if (t_idx is not None and _ph_idx(p) == t_idx)
                     or _ph_type(p) in _TITLE_TYPES), None)
    px = float(_EMU_PX)
    if title_ph is not None and title_ph.left is not None and title_ph.width:
        bl, bt = int(title_ph.left), int(title_ph.top or 0)
        bw, bh = int(title_ph.width), int(title_ph.height or 0)
        il = _bp_inset(title_ph, "lIns", _DEFAULT_INSET_EMU)
        ir = _bp_inset(title_ph, "rIns", _DEFAULT_INSET_EMU)
        it = _bp_inset(title_ph, "tIns", _DEFAULT_TB_INSET_EMU)
        ib = _bp_inset(title_ph, "bIns", _DEFAULT_TB_INSET_EMU)
    else:
        tx = getattr(layout_chrome, "title_box_x_px", None)
        ty = getattr(layout_chrome, "title_box_y_px", None)
        tw = getattr(layout_chrome, "title_box_width_px", None)
        th = getattr(layout_chrome, "title_box_height_px", None)
        if None in (tx, ty, tw, th):
            b = CS.canonical_title_box()
            tx, ty, tw, th = b.x_px, b.y_px, b.w_px, b.h_px
        bl, bt, bw, bh = tx * _EMU_PX, ty * _EMU_PX, tw * _EMU_PX, th * _EMU_PX
        il = ir = _DEFAULT_INSET_EMU
        it = ib = _DEFAULT_TB_INSET_EMU
    ts = _title_style(layout, title_ph, theme)
    title_pt = float(getattr(layout_chrome, "title_font_pt", None) or ts["size_pt"]
                     or CS.CANONICAL_TITLE_FONT_PT)
    if on_dark and not layout_dark:
        title_color = "FFFFFF"          # a dark-variant page: finalize draws the title white
    else:
        title_color = (ts["color"] or scheme_hex("bg1" if on_dark else "tx1", theme)
                       or ("FFFFFF" if on_dark else "000000"))
    text_left, text_right = bl + il, bl + bw - ir
    text_w = max(_EMU_PX * 40, text_right - text_left)
    title = {"left": round(bl / px, 1), "top": round(bt / px, 1),
             "width": round(bw / px, 1), "height": round(bh / px, 1),
             "pad_l": round(il / px, 1), "pad_r": round(ir / px, 1),
             "pad_t": round(it / px, 1), "pad_b": round(ib / px, 1),
             "size_pt": title_pt, "bold": True if ts["bold"] is None else bool(ts["bold"]),
             "color": title_color, "font": ts["font"] or theme.get("major") or "",
             "line_height": round(1.2 * (ts["line_pct"] or 1.0), 3), "anchor": "bottom"}

    # takeaway: the layout's slot keeps its own top; otherwise just under the title
    s_idx = getattr(layout_chrome, "subtitle_placeholder_idx", None)
    slot = next((p for p in layout.placeholders
                 if (s_idx is not None and _ph_idx(p) == s_idx) or _ph_type(p) in _SUBTITLE_TYPES),
                None)
    if slot is not None and slot.top is not None:
        t_top, from_slot = int(slot.top), True
    else:
        t_top, from_slot = drawn_takeaway_top_emu(bt + bh), False
    t_pt = float(takeaway_pt or template_takeaway_pt(prs, None, layout_chrome))
    if on_dark and not layout_dark:
        t_color = "FFFFFF"
    else:
        t_color = scheme_hex("bg1" if on_dark else "tx1", theme) or ("FFFFFF" if on_dark else "000000")
    takeaway = {"left": round(text_left / px, 1), "top": round(t_top / px, 1),
                "width": round(text_w / px, 1),
                "size_pt": t_pt, "bold": False, "color": t_color,
                "font": theme.get("minor") or "", "line_height": 1.2, "from_slot": from_slot}

    tag, tag_note = None, ""
    text = " ".join((section_tag or "").split())
    if not text or text.lower() in ("(none)", "none"):
        tag_note = "the brief gives this page no section tag"
    elif _no_tag_page(layout_chrome, page_type):
        tag_note = "no section tag on a cover, divider or closing page"
    else:
        top = section_tag_top_emu(bt)
        if top < 0:
            tag_note = ("the title box sits too close to the top of the page for the section "
                        "tag; finalize will stop and ask where it goes")
        else:
            color = "FFFFFF" if on_dark else ((accent_hex or "").lstrip("#").upper()[:6]
                                              or scheme_hex("accent1", theme) or "000000")
            tag = {"text": text, "left": round(text_left / px, 1), "top": round(top / px, 1),
                   "width": round(text_w / px, 1),
                   "height": float(CS.SECTION_TAG_H_PX), "size_pt": float(CS.SECTION_TAG_FONT_PT),
                   "bold": True, "small_caps": True, "color": color,
                   "font": theme.get("minor") or ""}
    try:
        from twins.helpers import body_zone_for_chrome
        body_top = int(body_zone_for_chrome(layout_chrome)[0])
    except Exception:
        body_top = None
    return {"layout": getattr(layout_chrome, "name", ""), "on_dark": bool(on_dark),
            "body_top": body_top, "title": title, "takeaway": takeaway,
            "section_tag": tag, "section_tag_note": tag_note}


def _css_px(v: float) -> str:
    return f"{float(v):.2f}".rstrip("0").rstrip(".") + "px"


def _css_font(face: str, fallback_var: str) -> str:
    face = (face or "").replace('"', "").replace("\\", "").strip()
    return (f'"{face}", var({fallback_var}, sans-serif)' if face
            else f"var({fallback_var}, sans-serif)")


def _css_string(text: str) -> str:
    out = []
    for ch in text:
        if ch in '"\\':
            out.append("\\" + ch)
        elif ord(ch) < 32:
            out.append(" ")
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


# Selectors are doubled so they outrank a designer's class or id rule; every
# value is !important and the sheet goes in last, so the template wins.
CHROME_TITLE_SELECTOR = 'html body [data-template-field="title"][data-template-field="title"]'
CHROME_TAKEAWAY_SELECTORS = (
    'html body [data-template-field="subtitle"][data-template-field="subtitle"]',
    'html body [data-shape-id="subtitle"][data-shape-id="subtitle"]')


def chrome_css(style: dict) -> str:
    """slide_NN/_chrome.css for a chrome_style() result. render_html.py adds
    it last when it draws the sketch; nothing else reads it."""
    t, k, g = style["title"], style["takeaway"], style.get("section_tag")
    pt_px = 96 / 72
    take_sel = ", ".join(CHROME_TAKEAWAY_SELECTORS)
    take_kids = ", ".join(s + " *" for s in CHROME_TAKEAWAY_SELECTORS)
    lines = [
        "/* Slide Lab: the template's title, takeaway and section tag on this layout",
        f"   ({style.get('layout') or 'layout'}). Written by prep (build_deck.py); render_html.py",
        "   adds it last when it draws the sketch, so the picture shows what finalize",
        "   puts on the slide. Do not edit, copy or restyle these: mark the title and",
        "   takeaway with data-template-field and leave their styling to Slide Lab. */",
        ":root {",
        f"  --chrome-title-top: {_css_px(t['top'])};",
        f"  --chrome-title-bottom: {_css_px(t['top'] + t['height'])};",
        f"  --chrome-takeaway-top: {_css_px(k['top'])};",
    ]
    if style.get("body_top") is not None:
        lines.append(f"  --chrome-body-top: {_css_px(style['body_top'])};")
    lines += [
        "}",
        CHROME_TITLE_SELECTOR + " {",
        "  position: fixed !important; transform: none !important; margin: 0 !important;",
        f"  left: {_css_px(t['left'])} !important; top: {_css_px(t['top'])} !important;",
        f"  width: {_css_px(t['width'])} !important; height: {_css_px(t['height'])} !important;",
        "  min-height: 0 !important; max-height: none !important;",
        "  box-sizing: border-box !important;",
        f"  padding: {_css_px(t['pad_t'])} {_css_px(t['pad_r'])} {_css_px(t['pad_b'])} "
        f"{_css_px(t['pad_l'])} !important;",
        "  display: flex !important; flex-direction: column !important;",
        "  justify-content: flex-end !important; align-items: stretch !important;",
        f"  font-family: {_css_font(t['font'], '--brand-heading-font')} !important;",
        f"  font-size: {_css_px(t['size_pt'] * pt_px)} !important;",
        f"  font-weight: {700 if t['bold'] else 400} !important; font-style: normal !important;",
        f"  line-height: {t['line_height']} !important; color: #{t['color']} !important;",
        "  text-align: left !important; text-transform: none !important;",
        "  letter-spacing: normal !important; white-space: normal !important;",
        "  background: transparent !important; border: 0 !important; box-shadow: none !important;",
        "  overflow: visible !important; visibility: visible !important; opacity: 1 !important;",
        "  z-index: 2147483000 !important;",
        "}",
        CHROME_TITLE_SELECTOR + " * {",
        "  font: inherit !important; color: inherit !important; letter-spacing: inherit !important;",
        "  text-transform: none !important; margin: 0 !important; padding: 0 !important;",
        "  background: transparent !important; border: 0 !important;",
        "}",
        take_sel + " {",
        "  position: fixed !important; transform: none !important; margin: 0 !important;",
        f"  left: {_css_px(k['left'])} !important; top: {_css_px(k['top'])} !important;",
        f"  width: {_css_px(k['width'])} !important; height: auto !important;",
        "  min-height: 0 !important; max-height: none !important;",
        "  box-sizing: border-box !important; padding: 0 !important; display: block !important;",
        f"  font-family: {_css_font(k['font'], '--brand-body-font')} !important;",
        f"  font-size: {_css_px(k['size_pt'] * pt_px)} !important;",
        "  font-weight: 400 !important; font-style: normal !important;",
        f"  line-height: {k['line_height']} !important; color: #{k['color']} !important;",
        "  text-align: left !important; text-transform: none !important;",
        "  letter-spacing: normal !important; white-space: normal !important;",
        "  background: transparent !important; border: 0 !important; box-shadow: none !important;",
        "  overflow: visible !important; visibility: visible !important; opacity: 1 !important;",
        "  z-index: 2147483000 !important;",
        "}",
        take_kids + " {",
        "  font: inherit !important; color: inherit !important; letter-spacing: inherit !important;",
        "  text-transform: none !important; background: transparent !important;",
        "}",
    ]
    if g:
        lines += [
            "html body::after {",
            f"  content: {_css_string(g['text'])} !important;",
            "  position: fixed !important; box-sizing: border-box !important;",
            f"  left: {_css_px(g['left'])} !important; top: {_css_px(g['top'])} !important;",
            f"  width: {_css_px(g['width'])} !important; height: {_css_px(g['height'])} !important;",
            "  display: flex !important; align-items: flex-end !important;",
            "  margin: 0 !important; padding: 0 !important; overflow: visible !important;",
            f"  font-family: {_css_font(g['font'], '--brand-body-font')} !important;",
            f"  font-size: {_css_px(g['size_pt'] * pt_px)} !important;",
            "  font-weight: 700 !important; font-style: normal !important;",
            "  font-variant: small-caps !important; line-height: 1.2 !important;",
            f"  color: #{g['color']} !important; white-space: nowrap !important;",
            "  background: transparent !important; z-index: 2147483000 !important;",
            "  pointer-events: none !important;",
            "}",
        ]
    return "\n".join(lines) + "\n"


def chrome_plain_words(style: dict) -> str:
    """The same values in plain words, for _context.md."""
    t, k, g = style["title"], style["takeaway"], style.get("section_tag")
    line_px = t["size_pt"] * 96 / 72 * t["line_height"]
    title_lines = max(1, int((t["height"] - t["pad_t"] - t["pad_b"] + 1) // line_px))
    per_line = int(k["width"] / (k["size_pt"] * 96 / 72 * 0.5))
    where = "the template's takeaway slot" if k["from_slot"] else "just under the title box"
    out = [
        f"- **Title:** {t['size_pt']:g} pt, {'bold' if t['bold'] else 'regular'}, "
        f"color #{t['color']}{', ' + t['font'] if t['font'] else ''}, in the template's title box "
        f"(left {t['left']:g} px, top {t['top']:g} px, {t['width']:g} x {t['height']:g} px), "
        f"bottom-aligned: a longer title grows upward. The box holds about {title_lines} "
        f"line(s) at this size. Keep the title to 2 lines at most: 3 or more lines is a "
        f"Major finding on the review page.",
        f"- **Takeaway:** {k['size_pt']:g} pt, regular, color #{k['color']}"
        f"{', ' + k['font'] if k['font'] else ''}, from left {k['left']:g} px, top "
        f"{k['top']:g} px ({where}), {k['width']:g} px wide: about {per_line} characters "
        f"a line.",
    ]
    if g:
        out.append(f"- **Section tag:** \"{g['text']}\", {g['size_pt']:g} pt bold small "
                   f"capitals, color #{g['color']}, just above the title (top {g['top']:g} px). "
                   f"Slide Lab draws it; do not draw it or mark it.")
    else:
        out.append(f"- **Section tag:** none on this page ({style.get('section_tag_note') or 'none'}).")
    if style.get("body_top") is not None:
        out.append(f"- Body content starts at or below `--body-top` ({style['body_top']} px). "
                   f"Anything above it sits under the title or takeaway, in the picture and "
                   f"on the slide; the review page flags it as Major.")
    return "\n".join(out)
