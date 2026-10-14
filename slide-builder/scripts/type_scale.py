#!/usr/bin/env python3
"""type_scale.py: does a slide keep to the house type scale? (owner's rule, 2026-10-05)

  - Body text is 12 pt by default. When the content truly cannot be cut
    further it may go down to 11 or 10.5 pt, never lower. 10.5 to 11 pt is
    reported as a note (Advisory); under 10.5 pt is a finding (Major).
  - A slide uses at most 3 body text sizes.
  - Text in native tables counts like any text box (2026-10-08).
  - Exceptions: sources, footnotes and chart text (axis, ticks, legend, data
    labels) may be smaller, but never under 9 pt. Title, takeaway and the
    template's own footer and page number are set by the template and not
    counted. One large "hero" figure (24 pt or more) is not counted either.
  - Slide Lab's own review labels (the "Option B" badge compile_picks.py
    stamps on an all-options deck, shape name chrome-option-badge) are not
    slide content: skipped entirely, neither checked nor counted as a size.
    Only the exact names Slide Lab stamps are skipped; a designer's shape
    named chrome-anything is still checked.

Which text is an exception is read from the shape's name (designers name
chart pieces chart-..., sources source-..., footnotes footnote-...; common
older names such as tick-label, c-ylab, legend are recognized too), from the
template slot a placeholder fills (a layout slot named "Source", "Sources",
"Footnote" or "Foot Note", by the same naming rule template registration
uses, _chrome_schema.slot_role_from_name; 2026-10-13: finalize writes the
brief's source into that slot, so the slot, not the words, says it is a
source), and from the text itself (a line starting "Source:", "Sources:",
"Note:" or "Notes:" WITH the colon, so a chart title "Sources, five-year
total" is body text; or a numbered footnote in the bottom band).

Used by build_review.py (FINAL-CHECK.html), finalize and slide-qc's
hygiene check (Major findings: fix, or give a reason to keep it; notes are
Advisory and never block).

Run:  py -3 type_scale.py <deck.pptx>     prints the findings per slide
"""
from __future__ import annotations

import html as _h
import re
import sys
from pathlib import Path

BODY_DEFAULT_PT = 12.0   # the size to design at
BODY_MIN_PT = 10.5       # lowest allowed, only when content cannot be cut
EXCEPTION_MIN_PT = 9.0
MAX_BODY_SIZES = 3
HERO_MIN_PT = 24.0

_A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
# Exception text, recognized by shape name
EXEMPT_NAME = re.compile(
    r"(^|[-_ ])(chart|axis|tick|ticks|ylab|xlab|legend|leg|gridline|source|sources|"
    r"footnote|footnotes|fn)([-_ \d]|$)", re.I)
TEMPLATE_NAME = re.compile(r"^(subtitle|title)$", re.I)
# "Takeaway" is skipped only as a template placeholder (a registered takeaway
# slot); a designer's loose box named "takeaway" is a bottom band or card and is
# checked like any text (2026-10-09).
TEMPLATE_SLOT_NAME = re.compile(r"^takeaway$", re.I)
# Shapes Slide Lab itself stamps on a compiled deck (review labeling, not
# content). Exact names only, so a worker cannot dodge the check by naming a
# shape chrome-something. Add a name here when a script starts stamping one.
PIPELINE_CHROME_NAMES = frozenset({"chrome-option-badge", "section-tag"})  # section-tag: the label finalize draws above the title (chrome_rules.place_section_tag)
SOURCE_TEXT = re.compile(r"^\s*(source|sources|note|notes)\s*:", re.I)
FOOTNOTE_TEXT = re.compile(r"^\s*(\d{1,2}[.)]|\*|†)\s")
# placeholder types: 1 title, 3 centered title, 4 subtitle, 13 slide number,
# 15 footer, 16 date
TEMPLATE_PH = {1, 3, 4, 13, 15, 16}


def _size(run, para) -> float | None:
    if run.font.size is not None:
        return run.font.size.pt
    ppr = para._p.find(_A + "pPr")
    if ppr is not None:
        d = ppr.find(_A + "defRPr")
        if d is not None and d.get("sz"):
            return int(d.get("sz")) / 100
    return None  # inherited from the template layout: the template's choice


def _shapes(shapes):
    for sh in shapes:
        if sh.shape_type == 6:  # group
            yield from _shapes(sh.shapes)
        else:
            yield sh


def _is_source_slot(slide, sh) -> bool:
    """True when `sh` is a placeholder filling the layout's Source / Footnote
    slot (the layout placeholder with the same idx is named like one), or is
    itself named like one ("Foot Note", "Sources 3")."""
    if not getattr(sh, "is_placeholder", False):
        return False
    try:
        from _chrome_schema import slot_role_from_name
    except Exception:
        return False
    names = [sh.name or ""]
    try:
        idx = sh.placeholder_format.idx
        for lp in slide.slide_layout.placeholders:
            if lp.placeholder_format.idx == idx:
                names.append(lp.name or "")
                break
    except Exception:
        pass
    for n in names:
        role = slot_role_from_name(n)
        if role and role[0] == "source":
            return True
    return False


def check_slide(slide, slide_h: int) -> dict:
    """{'small_body': [(pt, text)] under 10.5, 'below_default': [(pt, text)]
        10.5 to 11, 'small_exception': [(pt, text)], 'body_sizes': [pt, ...],
        'too_many_sizes': bool}"""
    small_body, below_default, small_exc, body_sizes = [], [], [], set()
    for sh in _shapes(slide.shapes):
        if getattr(sh, "has_table", False) and sh.has_table:
            # a native table: every cell's text counts like a text box's
            frames = [c.text_frame for row in sh.table.rows for c in row.cells]
        elif getattr(sh, "has_text_frame", False) and sh.has_text_frame:
            if sh.is_placeholder and sh.placeholder_format.type in TEMPLATE_PH:
                continue
            frames = [sh.text_frame]
        else:
            continue
        name = sh.name or ""
        if TEMPLATE_NAME.match(name) or name in PIPELINE_CHROME_NAMES:
            continue
        if TEMPLATE_SLOT_NAME.match(name) and sh.is_placeholder:
            continue
        exempt_shape = bool(EXEMPT_NAME.search(name)) or _is_source_slot(slide, sh)
        bottom = (sh.top or 0) > slide_h * 0.85
        for para in (p for tf in frames for p in tf.paragraphs):
            text = "".join(r.text for r in para.runs).strip()
            if not text:
                continue
            exempt = (exempt_shape or SOURCE_TEXT.match(text) is not None
                      or (bottom and FOOTNOTE_TEXT.match(text) is not None))
            for run in para.runs:
                if not run.text.strip():
                    continue
                pt = _size(run, para)
                if pt is None:
                    continue
                if exempt:
                    if pt < EXCEPTION_MIN_PT:
                        small_exc.append((pt, text))
                    break
                if pt >= HERO_MIN_PT:
                    continue
                body_sizes.add(pt)
                if pt < BODY_MIN_PT:
                    small_body.append((pt, text))
                    break
                if pt < BODY_DEFAULT_PT:
                    below_default.append((pt, text))
                    break
    return {"small_body": small_body, "below_default": below_default,
            "small_exception": small_exc,
            "body_sizes": sorted(body_sizes),
            "too_many_sizes": len(body_sizes) > MAX_BODY_SIZES}


def problems(result: dict) -> list[str]:
    """Major problems in plain English, empty when the slide keeps to the scale."""
    out = []
    sb = result["small_body"]
    if sb:
        smallest = min(p for p, _ in sb)
        out.append(f"{len(sb)} piece(s) of body text under {BODY_MIN_PT:g} pt "
                   f"(smallest {smallest:g} pt), e.g. \"{sb[0][1][:50]}\"")
    if result["too_many_sizes"]:
        sizes = ", ".join(f"{p:g}" for p in result["body_sizes"])
        out.append(f"{len(result['body_sizes'])} body text sizes ({sizes} pt); "
                   f"keep to {MAX_BODY_SIZES}")
    se = result["small_exception"]
    if se:
        out.append(f"{len(se)} source, footnote or chart label(s) under "
                   f"{EXCEPTION_MIN_PT:g} pt, e.g. \"{se[0][1][:50]}\"")
    return out


def notes(result: dict) -> list[str]:
    """Advisory: body text below the 12 pt default but within the 10.5 pt floor."""
    bd = result.get("below_default") or []
    if not bd:
        return []
    sizes = ", ".join(f"{p:g}" for p in sorted({p for p, _ in bd}))
    return [f"{len(bd)} piece(s) of body text below the {BODY_DEFAULT_PT:g} pt default "
            f"({sizes} pt), e.g. \"{bd[0][1][:50]}\""]


# ---------------------------------------------------------------- line spacing
# Exact line spacing ("exactly N pt", a:spcPts) tighter than the font needs
# (2026-10-13 report item 10: 439 of 545 paragraphs on 23 of 30 pages, and it
# did not show in the pictures). Two checks, in px at 96 dpi:
#   - lines touch: a paragraph that can show more than one line, at a pitch
#     smaller than the font's capital height plus its descent, so the letters
#     of one line meet the next line's. Major (layout, fixed automatically as
#     an overlap).
#   - capitals above the box: the first line of a top-anchored box sits so
#     high that its capitals reach more than CAPS_ABOVE_PX above the box (its
#     frame when selected). Advisory: only visible when the box is selected.
# The converter's own one-line boxes (spacing 0.8 x size, translate_html
# TIGHT_SINGLE) are drawn higher with a top inset since 2026-10-13
# (top_pad_px), so they pass both: one line cannot touch another, and the
# inset covers the capitals.
CAPS_ABOVE_PX = 1.0
TOUCH_MARGIN_PX = 0.5
_ARIAL = (0.905, 0.212, 0.716)   # ascent, descent, capital height (em)


def _font_metrics(face: str, bold: bool):
    """(ascent, descent, capital height) in em, and PowerPoint's first
    baseline function, from translate_html; Arial's values without it."""
    try:
        import translate_html as _T
        asc, desc, _n = _T.vertical_metrics(face, bold)
        return (asc, desc, _T.cap_height(face, bold)), _T.ppt_first_baseline
    except Exception:
        return _ARIAL, None


def _first_baseline_fallback(L: float, S: float, asc: float, desc: float) -> float:
    """translate_html.ppt_first_baseline, when it cannot be imported."""
    import math
    Lr = round(L * 0.75) / 0.75
    if round(L * 0.75) > math.floor(1.2 * S * 0.75 + 1e-6):
        return 0.75 * Lr
    return max(0.75 * Lr, Lr - 1.2 * S * desc / (asc + desc))


def _theme_faces(slide) -> dict:
    """{"+mn-lt": minor latin face, "+mj-lt": major latin face} of the
    slide's theme; {} when it cannot be read."""
    try:
        master = slide.slide_layout.slide_master
        for rel in master.part.rels.values():
            if rel.reltype.endswith("/theme"):
                from lxml import etree
                root = etree.fromstring(rel.target_part.blob)
                out = {}
                for tag, key in (("minorFont", "+mn-lt"), ("majorFont", "+mj-lt")):
                    el = root.find(".//" + _A + tag + "/" + _A + "latin")
                    if el is not None and el.get("typeface"):
                        out[key] = el.get("typeface")
                return out
    except Exception:
        pass
    return {}


def _face(run, faces: dict) -> str:
    name = run.font.name or "+mn-lt"
    return faces.get(name, "Arial") if name.startswith("+") else name


def _wraps(runs, para, inner_w: float, faces: dict) -> bool:
    """Does this paragraph wrap onto a second line in its box? Measured with
    the real font files (translate_html._wrapped_lines, as PowerPoint sets
    the text); without them, at an average letter width of half the size."""
    rs = [{"t": r.text, "font": _face(r, faces), "bold": bool(r.font.bold),
           "size_px": (_size(r, para) or 12) / 0.75} for r in runs]
    try:
        import translate_html as _T
        n = _T._wrapped_lines([rs], max(1.0, inner_w))
        if n is not None:
            return n > 1
    except Exception:
        pass
    return sum(len(r["t"]) * 0.5 * r["size_px"] for r in rs) > inner_w


def _para_space(p, tag: str, L: float | None) -> float:
    """Space before or after a paragraph (a:spcBef / a:spcAft), in px. A
    percentage is of the line (L px); 0 when there is none."""
    el = p._p.find(_A + "pPr/" + _A + tag)
    if el is None:
        return 0.0
    pts = el.find(_A + "spcPts")
    if pts is not None:
        return int(pts.get("val") or 0) / 100 / 0.75
    pct = el.find(_A + "spcPct")
    if pct is not None and L:
        return int(pct.get("val") or 0) / 100000 * L
    return 0.0


def line_spacing_slide(slide) -> dict:
    """{'touch': [(spacing pt, size pt, text)], 'caps_above': [(px, text)]}
    for paragraphs with exact line spacing (see above)."""
    touch, caps = [], []
    faces = None
    for sh in _shapes(slide.shapes):
        if not (getattr(sh, "has_text_frame", False) and sh.has_text_frame):
            continue
        tf = sh.text_frame
        body = tf._txBody.find(_A + "bodyPr")
        anchor = body.get("anchor") if body is not None else None
        if anchor is None and getattr(sh, "is_placeholder", False):
            anchor = "inherited"            # the layout decides; not known here
        anchor = anchor or "t"

        def _ins(attr, default):
            v = body.get(attr) if body is not None else None
            return (int(v) if v is not None else default) / 9525
        tins, bins = _ins("tIns", 45720), _ins("bIns", 45720)
        inner_h = ((sh.height or 0) / 9525) - tins - bins
        inner_w = ((sh.width or 0) / 9525) - _ins("lIns", 91440) - _ins("rIns", 91440)
        wrap = (body.get("wrap") if body is not None else None) != "none"
        if faces is None:
            faces = _theme_faces(slide)
        paras =[p for p in tf.paragraphs if "".join(r.text for r in p.runs).strip()]
        prev_after = None              # px after the previous paragraph; None = first
        for i, p in enumerate(paras):
            spc = p._p.find(_A + "pPr/" + _A + "lnSpc/" + _A + "spcPts")
            runs = [r for r in p.runs if r.text.strip()]
            sizes = [(_size(r, p), r) for r in runs]
            sizes = [(s, r) for s, r in sizes if s]
            if spc is None or not sizes:
                prev_after = _para_space(p, "spcAft", None)
                continue
            S_pt, big = max(sizes, key=lambda t: t[0])
            S, L = S_pt / 0.75, int(spc.get("val")) / 100 / 0.75
            (asc, desc, cap), fb = _font_metrics(_face(big, faces), bool(big.font.bold))
            need = (cap + desc) * S - TOUCH_MARGIN_PX
            text = "".join(r.text for r in p.runs).strip()
            # Lines touch only where a line sits above this one: inside the
            # paragraph (a line break, or text that wraps in the box) at pitch
            # L, or the previous paragraph's last line, at L plus the space
            # after it and before this one.
            inside = (p._p.find(_A + "br") is not None
                      or (wrap and _wraps(runs, p, inner_w, faces)))
            between = (prev_after is not None
                       and L + prev_after + _para_space(p, "spcBef", L) < need)
            if (inside and L < need) or between:
                touch.append((round(L * 0.75, 1), S_pt, text))
            prev_after = _para_space(p, "spcAft", L)
            if i == 0 and anchor == "t":
                above = cap * S - (tins + (fb or _first_baseline_fallback)(L, S, asc, desc))
                if above > CAPS_ABOVE_PX:
                    caps.append((round(above, 1), text))
    return {"touch": touch, "caps_above": caps}


def line_spacing_problems(result: dict) -> list[str]:
    """Major: lines set so tight their letters meet."""
    t = result.get("touch") or []
    if not t:
        return []
    L, S, text = t[0]
    return [f"{len(t)} paragraph(s) with exact line spacing tighter than the font needs, so "
            f"the letters of one line meet the next (e.g. {L:g} pt spacing on {S:g} pt text, "
            f"\"{text[:50]}\")"]


def line_spacing_notes(result: dict) -> list[str]:
    """Advisory: capitals above the text box (seen only when it is selected)."""
    c = result.get("caps_above") or []
    if not c:
        return []
    px, text = max(c, key=lambda t: t[0])
    return [f"{len(c)} text box(es) whose first line is set so tight that the capitals reach "
            f"above the box (up to {px:g} px; shows only when the box is selected), e.g. "
            f"\"{text[:50]}\""]


def check_pptx(path: Path, with_notes: bool = False):
    """[(slide n, problems)], or [(slide n, problems, notes)] with_notes."""
    from pptx import Presentation
    prs = Presentation(str(path))
    out = []
    for i, s in enumerate(prs.slides, 1):
        r = check_slide(s, prs.slide_height)
        out.append((i, problems(r), notes(r)) if with_notes else (i, problems(r)))
    return out


def html_block(rows) -> str:
    """FINAL-CHECK.html block. rows: (slide label, problems[, notes])."""
    bad = [(r[0], r[1]) for r in rows if r[1]]
    low = [(r[0], r[2]) for r in rows if len(r) > 2 and r[2]]
    if not bad and not low:
        return ('<div class="srccheck ok">Every slide keeps body text at 12 pt, '
                'in at most 3 sizes.</div>')
    parts = []
    if bad:
        trs = "".join(f"<tr><td>{_h.escape(k)}</td><td>{_h.escape('; '.join(p))}</td></tr>"
                      for k, p in bad)
        parts.append('<div class="srccheck"><b>Text size: fix these.</b> Body text is 12 pt, '
                     'and never under 10.5 pt, in at most 3 sizes per slide (sources, '
                     'footnotes and chart labels may go down to 9 pt). Fix these, or say why '
                     f'one should stay.<table>{trs}</table></div>')
    if low:
        trs = "".join(f"<tr><td>{_h.escape(k)}</td><td>{_h.escape('; '.join(p))}</td></tr>"
                      for k, p in low)
        parts.append('<div class="srccheck ok"><b>Text size: below the 12 pt default.</b> '
                     'Allowed down to 10.5 pt when the content cannot be cut; check it '
                     f'still reads well.<table>{trs}</table></div>')
    return "".join(parts)


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print(__doc__)
        return 2
    found = 0
    for n, probs in check_pptx(Path(argv[0])):
        for p in probs:
            print(f"slide {n}: {p}")
            found += 1
    print("OK: every slide keeps to the type scale." if not found else f"{found} finding(s).")
    return 0 if not found else 1


if __name__ == "__main__":
    sys.exit(main())
