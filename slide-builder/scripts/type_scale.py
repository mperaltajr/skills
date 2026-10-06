#!/usr/bin/env python3
"""type_scale.py: does a slide keep to the house type scale? (owner's rule, 2026-10-05)

  - Body text is 12 pt by default. When the content truly cannot be cut
    further it may go down to 11 or 10.5 pt, never lower. 10.5 to 11 pt is
    reported as a note (Advisory); under 10.5 pt is a finding (Major).
  - A slide uses at most 3 body text sizes.
  - Exceptions: sources, footnotes and chart text (axis, ticks, legend, data
    labels) may be smaller, but never under 9 pt. Title, takeaway and the
    template's own footer and page number are set by the template and not
    counted. One large "hero" figure (24 pt or more) is not counted either.

Which text is an exception is read from the shape's name (designers name
chart pieces chart-..., sources source-..., footnotes footnote-...; common
older names such as tick-label, c-ylab, legend are recognized too) and from
the text itself (a line starting "Source" or "Note", or a numbered footnote
in the bottom band).

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
TEMPLATE_NAME = re.compile(r"^(subtitle|takeaway|title)$", re.I)
SOURCE_TEXT = re.compile(r"^\s*(source|sources|note|notes)\b", re.I)
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


def check_slide(slide, slide_h: int) -> dict:
    """{'small_body': [(pt, text)] under 10.5, 'below_default': [(pt, text)]
        10.5 to 11, 'small_exception': [(pt, text)], 'body_sizes': [pt, ...],
        'too_many_sizes': bool}"""
    small_body, below_default, small_exc, body_sizes = [], [], [], set()
    for sh in _shapes(slide.shapes):
        if not getattr(sh, "has_text_frame", False) or not sh.has_text_frame:
            continue
        if sh.is_placeholder and sh.placeholder_format.type in TEMPLATE_PH:
            continue
        name = sh.name or ""
        if TEMPLATE_NAME.match(name):
            continue
        exempt_shape = bool(EXEMPT_NAME.search(name))
        bottom = (sh.top or 0) > slide_h * 0.85
        for para in sh.text_frame.paragraphs:
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
