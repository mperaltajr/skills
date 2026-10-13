#!/usr/bin/env python3
"""one_deck.py — render many one-slide decks as ONE deck, then split the pages.

Opening a deck is most of a render's cost in PowerPoint (and a LibreOffice
start is most of it there), so the converter's self-check and finalize's
renders put every slide of a round into one temporary deck, render that once,
and hand each page back to the slide it came from (owner's decision,
2026-10-09).

  - Slides merge only with decks built on the same template (same masters,
    layouts, theme, table styles, slide size and default text). A deck that
    differs goes into a deck of its own, so nothing is drawn on a template
    it was not built on.
  - Every slide is shown in the temporary deck (a PDF drops hidden slides,
    which would move every later page onto the wrong slide), and the page
    count is checked against the slide count before any page is handed back.
  - If the merged deck fails to render (PowerPoint refuses a whole file for
    one bad slide), it is split in halves and rendered again, down to single
    decks, so only the slide that really fails is reported as failed.
  - Page numbers are frozen in the temporary deck (2026-10-13). A page
    number is a slide-number field, which the renderer computes from the
    slide's place in the deck it draws. In a merged deck that place is wrong
    (the brief's slide 2 sat 4th and showed "4"), and a one-slide deck always
    showed "1". So every slide-number field in the TEMPORARY deck becomes a
    plain run holding the number the option file stored (the brief's number),
    with the same formatting. A one-slide render draws a frozen temporary
    copy, never the option file itself. Option files and the finished deck
    keep their real fields.

Public:
  render_pngs(srcs, pngs, dpi, renderer=None) -> {index: error}
      the FIRST slide of each srcs[i] as pngs[i]
  pdf_pages(srcs, workdir, renderer=None)    -> list of (pdf, page) or error
      the FIRST slide of each srcs[i] as page `page` (0-based) of `pdf`
"""
from __future__ import annotations

import hashlib
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
for _p in (str(SKILL), str(HERE), str(SKILL.parent / "slide-qc" / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import render_slides as RS  # noqa: E402

_STRUCT = re.compile(r"ppt/(slideLayouts|slideMasters|theme)/|ppt/tableStyles\.xml$")


def signature(pptx: Path) -> str:
    """Same string = built on the same template, so safe to merge."""
    h = hashlib.sha1()
    with zipfile.ZipFile(pptx) as z:
        for info in sorted(z.infolist(), key=lambda i: i.filename):
            if _STRUCT.match(info.filename):
                h.update(f"{info.filename}:{info.CRC}:{info.file_size};".encode())
        pres = z.read("ppt/presentation.xml")
    # presentation.xml minus the slide list and extensions (sections), which
    # differ from deck to deck without changing how a slide looks
    pres = re.sub(rb"<p:sldIdLst>.*?</p:sldIdLst>|<p:sldIdLst/>", b"", pres, flags=re.S)
    pres = re.sub(rb"<p:extLst>.*?</p:extLst>", b"", pres, flags=re.S)
    h.update(pres)
    return h.hexdigest()


_A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
_SLIDE_PART = re.compile(r"ppt/slides/slide\d+\.xml$")


def freeze_fields_in_element(root) -> int:
    """Replace every slide-number field under `root` (an lxml element) with
    a plain run holding the field's stored number, keeping its <a:rPr>.
    A field with no stored text is left alone. Returns how many changed."""
    import copy
    a = "{%s}" % _A_NS
    n = 0
    for fld in list(root.iter(a + "fld")):
        if (fld.get("type") or "").lower() != "slidenum":
            continue
        t = fld.find(a + "t")
        if t is None or not (t.text or "").strip():
            continue
        run = fld.makeelement(a + "r", {})
        rpr = fld.find(a + "rPr")
        if rpr is not None:
            run.append(copy.deepcopy(rpr))
        nt = run.makeelement(a + "t", {})
        nt.text = t.text
        run.append(nt)
        fld.addprevious(run)
        fld.getparent().remove(fld)
        n += 1
    return n


def freeze_page_numbers(src: Path, dst: Path) -> int:
    """Write `dst` = `src` with every slide-number field on its slides frozen
    to the number it stores (see freeze_fields_in_element). Only for
    temporary render decks. `src` may equal `dst`. Returns how many fields
    changed (0 = dst is a plain copy)."""
    from lxml import etree
    src, dst = Path(src), Path(dst)
    with zipfile.ZipFile(src) as z:
        items = [(info, z.read(info.filename)) for info in z.infolist()]
    total = 0
    out_items = []
    for info, data in items:
        if _SLIDE_PART.match(info.filename) and b'"slidenum"' in data:
            root = etree.fromstring(data)
            k = freeze_fields_in_element(root)
            if k:
                total += k
                data = etree.tostring(root, xml_declaration=True,
                                      encoding="UTF-8", standalone=True)
        out_items.append((info, data))
    if total == 0 and src == dst:
        return 0
    tmp = dst.with_name(dst.name + ".freeze.tmp")
    with zipfile.ZipFile(tmp, "w") as zo:
        for info, data in out_items:
            zo.writestr(info, data, compress_type=info.compress_type)
    tmp.replace(dst)
    return total


def merge(srcs: list[Path], dst: Path) -> None:
    """dst = the first slide of every src, in order, on the first src's
    template. All srcs must share one signature()."""
    from pptx import Presentation
    from twins.composer import copy_shape_with_parts
    base = Presentation(str(srcs[0]))
    # keep only the first slide of the base deck
    lst = base.slides._sldIdLst
    for sid in list(lst)[1:]:
        base.part.drop_rel(sid.rId)
        lst.remove(sid)
    layouts = {str(l.part.partname): l for m in base.slide_masters for l in m.slide_layouts}
    for src in srcs[1:]:
        sp = Presentation(str(src))
        s = sp.slides[0]
        new = base.slides.add_slide(layouts[str(s.slide_layout.part.partname)])
        sld = new._element
        for child in list(sld):
            sld.remove(child)
        memo: dict = {}
        for child in s._element:
            sld.append(copy_shape_with_parts(child, s.part, new.part, memo))
        for k, v in s._element.attrib.items():
            sld.set(k, v)
    for s in base.slides:
        s._element.attrib.pop("show", None)
        # the renderer would number each page by its place in THIS deck
        freeze_fields_in_element(s._element)
    base.save(str(dst))


def _groups(srcs: list[Path], errors: dict) -> list[list[int]]:
    by_sig: dict[str, list[int]] = {}
    for i, p in enumerate(srcs):
        try:
            sig = signature(p)
        except Exception as exc:  # noqa: BLE001
            errors[i] = f"could not read {Path(p).name}: {type(exc).__name__}: {exc}"
            continue
        by_sig.setdefault(sig, []).append(i)
    return list(by_sig.values())


def _render_group(srcs, idx, td: Path, render_one, errors: dict, depth=0):
    """render_one(deck, n_slides, idx) renders a deck holding the first slide
    of each srcs[i] for i in idx, in order; raises on failure. On failure the
    group is halved until single decks, so only a failing slide is reported."""
    if len(idx) == 1:
        # never render the option file itself: its page-number field would
        # show "1" (the slide is first in its own file)
        src = Path(srcs[idx[0]])
        deck = td / f"one_{depth}_{idx[0]:04d}{src.suffix or '.pptx'}"
        try:
            freeze_page_numbers(src, deck)
        except Exception as exc:  # noqa: BLE001
            print(f"  (could not freeze the page number of {src.name} for its preview: "
                  f"{type(exc).__name__}: {exc}; the preview may show page 1)",
                  file=sys.stderr)
            deck = src
    else:
        deck = td / f"deck_{depth}_{idx[0]:04d}_{len(idx)}.pptx"
        try:
            merge([srcs[i] for i in idx], deck)
        except Exception as exc:  # noqa: BLE001
            print(f"  (could not put {len(idx)} slides in one deck: {type(exc).__name__}: "
                  f"{exc}; rendering them in smaller decks)", file=sys.stderr)
            deck = None
    if deck is not None:
        try:
            render_one(deck, len(idx), idx)
            return
        except Exception as exc:  # noqa: BLE001
            if len(idx) == 1:
                errors[idx[0]] = str(exc)
                return
            print(f"  (a deck of {len(idx)} slides did not render; splitting it so "
                  f"only the slide that fails is reported)", file=sys.stderr)
    half = len(idx) // 2
    _render_group(srcs, idx[:half], td, render_one, errors, depth + 1)
    _render_group(srcs, idx[half:], td, render_one, errors, depth + 1)


def render_pngs(srcs: list[Path], pngs: list[Path], dpi: int = 120,
                renderer: str | None = None) -> dict[int, str]:
    """pngs[i] = the first slide of srcs[i]. Returns {i: error} for the
    slides that did not render (the rest rendered)."""
    srcs, pngs = [Path(p) for p in srcs], [Path(p) for p in pngs]
    errors: dict[int, str] = {}
    if not srcs:
        return errors
    import _scratch
    with _scratch.temp_dir("one_deck_") as tdn:
        td = Path(tdn)
        k = [0]

        def render_one(deck, n, idx):
            k[0] += 1
            out = td / f"png{k[0]}"
            import contextlib, io
            with contextlib.redirect_stdout(io.StringIO()):
                RS.render(deck, out, dpi, renderer=renderer, quiet=True)
            got = sorted(out.glob("slide_*.png"))
            want = n if len(idx) > 1 else 1
            if len(got) < want or (len(idx) > 1 and len(got) != n):
                raise RuntimeError(f"{len(got)} page(s) came back for {n} slide(s)")
            for j, i in enumerate(idx):
                pngs[i].parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(out / f"slide_{j + 1:02d}.png", pngs[i])

        for g in _groups(srcs, errors):
            _render_group(srcs, g, td, render_one, errors)
    return errors


def pdf_pages(srcs: list[Path], workdir: Path,
              renderer: str | None = None) -> list:
    """For each srcs[i]: (pdf path, 0-based page) of its first slide, or an
    error string. The PDFs live in workdir (the caller cleans it)."""
    srcs = [Path(p) for p in srcs]
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    errors: dict[int, str] = {}
    out: list = [None] * len(srcs)
    k = [0]

    def render_one(deck, n, idx):
        k[0] += 1
        pdf, _eng = RS.to_pdf(deck, workdir / f"pdf{k[0]}", renderer=renderer)
        pages = RS._pdf_pages(pdf)
        if (len(idx) > 1 and pages != n) or pages < 1:
            raise RuntimeError(f"{pages} page(s) came back for {n} slide(s)")
        for j, i in enumerate(idx):
            out[i] = (pdf, j)

    for g in _groups(srcs, errors):
        _render_group(srcs, g, workdir, render_one, errors)
    for i, e in errors.items():
        out[i] = e
    return out
