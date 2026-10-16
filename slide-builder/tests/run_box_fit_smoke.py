#!/usr/bin/env python3
"""Smoke: text boxes are fitted to their text, and nothing that must stay
does not (fit_boxes.py, owner's decisions 2026-10-16).

A 13-page test deck has, on every page: a title placeholder, three one-line
boxes (left, centered, right), three wrapping boxes (top, middle, bottom
anchored), and boxes that must never change: a page-number box with a
slide-number field, a filled box, an outlined box, a shrink-text-on-overflow
box, a box a connector is attached to, a justified box, a body placeholder
that inherits shrink-on-overflow from the master, and one that inherits a
fill from its layout.

Without PowerPoint (always run):
  [1] SLIDE_LAB_NO_POWERPOINT=1: skipped with the note, the file unchanged
  [2] the proof loop with a stand-in measurer: a box whose text "moves" goes
      back, a page that "looks different" gets every box back, a proof that
      never passes keeps the deck exactly as it was
With PowerPoint (Windows; read-only through ppt_safe):
  [3] fit: 0 moved, 0 changed pages; each kept box has the same geometry;
      every placeholder's geometry is byte-identical (owner, 2026-10-16:
      nothing from the template adjusts, not even its height), and so are
      the loose source line and section tag; one-line boxes keep their
      aligned side; wrapping boxes keep their anchored edge; left, right
      and bottom margins become 0 (top kept): a box whose 0.54" right
      margin forced wrapping comes out narrower, margin 0, same lines and
      same pixels
  [4] the same fit again changes nothing (same result twice)
  [5] page reorder: page 5 moved to position 12 still shows its page number
      on one line
  [6] one more short word in every title and wrapping box wraps exactly as
      it does in the unfitted deck
  [7] the command line fits only the pages asked for and never writes over
      the original
  [8] compile: a 2-slide build records box_fit in the compile record and
      COMPILED.md, and check_done prints the fit line

Run:  py -3 slide-builder/tests/run_box_fit_smoke.py
Prints "SMOKE PASSED." on success.
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import contextlib
import copy
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(SKILL.parent / "slide-qc" / "scripts"))

import fit_boxes as FB  # noqa: E402
from lxml import etree  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402
from pptx.util import Emu, Inches, Pt  # noqa: E402

N_PAGES = 13
KEEP = ("page-number", "filled", "outlined", "shrink", "glued", "justified",
        "source", "section-tag", "Title", "Text Placeholder", "Content Placeholder")


def _xml(s):
    return etree.fromstring(s)


def _box(slide, name, x, y, w, h, text, align=PP_ALIGN.LEFT, wrap=False,
         anchor=MSO_ANCHOR.TOP, size=14):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    bp = tf._txBody.find(qn("a:bodyPr"))
    for c in list(bp):
        bp.remove(c)                                   # no autofit: fixed size box
    tf.text = text
    for p in tf.paragraphs:
        p.alignment = align
        for r in p.runs:
            r.font.size = Pt(size)
    return tb


def build_deck(path: Path) -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    master = prs.slide_masters[0]
    # Title: no shrink-on-overflow, so it is a candidate (height only).
    for ph in master.placeholders:
        if int(ph.placeholder_format.type) == 1:
            bp = ph._element.find(f"{qn('p:txBody')}/{qn('a:bodyPr')}")
            for c in list(bp):
                if c.tag == qn("a:normAutofit"):
                    bp.remove(c)
    layout = prs.slide_layouts[4]                       # Comparison
    for ph in layout.placeholders:
        if ph.placeholder_format.idx == 3:              # inherits a FILL from the layout
            sp = ph._element.find(qn("p:spPr"))
            sp.append(_xml('<a:solidFill xmlns:a="http://schemas.openxmlformats.org/'
                           'drawingml/2006/main"><a:srgbClr val="DDEEFF"/></a:solidFill>'))
            bp = ph._element.find(f"{qn('p:txBody')}/{qn('a:bodyPr')}")
            for c in list(bp):
                bp.remove(c)
            bp.append(_xml('<a:noAutofit xmlns:a="http://schemas.openxmlformats.org/'
                           'drawingml/2006/main"/>'))
    for n in range(1, N_PAGES + 1):
        s = prs.slides.add_slide(layout)
        for ph in list(s.placeholders):
            idx = ph.placeholder_format.idx
            if idx == 0:
                ph.text = f"Revenue grows on page {n}"
            elif idx == 1:
                ph.text = "Inherits shrink on overflow"
            elif idx == 3:
                ph.text = "Inherits a fill"
            else:
                ph._element.getparent().remove(ph._element)
        _box(s, "one-left", 0.6, 2.0, 6, 0.6, "Margin 41%")
        _box(s, "one-center", 0.6, 2.7, 6, 0.6, "Centered label", align=PP_ALIGN.CENTER)
        _box(s, "one-right", 6.8, 2.0, 6, 0.6, "Right label", align=PP_ALIGN.RIGHT)
        _box(s, "wrap-top", 0.6, 3.5, 5.5, 2.0, "Costs fall by a third", wrap=True)
        _box(s, "wrap-middle", 6.8, 3.5, 5.5, 2.0, "Middle anchored note", wrap=True,
             anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        _box(s, "wrap-bottom", 0.6, 5.6, 5.5, 1.2,
             "Bottom anchored text that runs long enough to wrap onto a second line here",
             wrap=True, anchor=MSO_ANCHOR.BOTTOM)
        pn = _box(s, "page-number", 12.0, 7.0, 1.0, 0.4, "", align=PP_ALIGN.RIGHT, size=10)
        p = pn.text_frame.paragraphs[0]
        for r in list(p._p.findall(qn("a:r"))):
            p._p.remove(r)
        p._p.append(_xml(
            '<a:fld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'id="{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}" type="slidenum">'
            f'<a:rPr lang="en-US" sz="1000"/><a:t>{n}</a:t></a:fld>'))
        f = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7), Inches(5.6), Inches(3), Inches(0.9))
        f.name = "filled"
        f.text_frame.text = "Filled"
        f.fill.solid()
        f.fill.fore_color.rgb = RGBColor(0xEE, 0xEE, 0xEE)
        o = _box(s, "outlined", 10.2, 5.6, 2.8, 0.9, "Outlined")
        o.line.color.rgb = RGBColor(0x33, 0x33, 0x33)
        sh = _box(s, "shrink", 7.0, 6.6, 3.0, 0.8, "Shrinks on overflow")
        sh.text_frame._txBody.find(qn("a:bodyPr")).append(
            _xml('<a:normAutofit xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>'))
        g = _box(s, "glued", 0.6, 1.2, 3.0, 0.6, "Glued")
        c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(4), Inches(1.5),
                                   Inches(5), Inches(1.5))
        c.begin_connect(g, 3)
        _box(s, "justified", 9.0, 1.2, 4.0, 0.7, "Justified text box",
             align=PP_ALIGN.JUSTIFY, wrap=True)
        # A right margin of 0.54" used to force wrapping (Leo deck v4.2 hand edit)
        iw = _box(s, "inset-wrap", 9.0, 2.7, 4.0, 1.4,
                  "Revenue from the new region grows faster than the core business",
                  wrap=True)
        iw.text_frame._txBody.find(qn("a:bodyPr")).set("rIns", str(int(Inches(0.54))))
        # Slide Lab's fixed slots drawn as loose boxes: never fitted
        _box(s, "source", 0.6, 6.9, 9.0, 0.4, "Source: test data", size=9)
        _box(s, "section-tag", 0.6, 0.2, 6.0, 0.4, "THE MARKET", size=10)
    prs.save(str(path))


def geometry(path: Path) -> list[dict]:
    """Per page: {shape name: (x, y, cx, cy)}, inherited values included."""
    out = []
    for s in Presentation(str(path)).slides:
        out.append({sh.name: (int(sh.left), int(sh.top), int(sh.width), int(sh.height))
                    for sh in s.shapes})
    return out


def _spPr_xml(path: Path) -> list[dict]:
    res = []
    for s in Presentation(str(path)).slides:
        res.append({sh.name: etree.tostring(sh._element.find(qn("p:spPr")) if
                                            sh._element.find(qn("p:spPr")) is not None
                                            else sh._element)
                    for sh in s.shapes})
    return res


def _key_of(path: Path, page: int, name: str):
    s = list(Presentation(str(path)).slides)[page - 1]
    return (page, int(next(sh.shape_id for sh in s.shapes if sh.name == name)))


# ---------------------------------------------------------------- stand-in engine
class FakeEngine:
    """Measures from the file: the text sits where it sat in the original,
    unless the box is in `move` (its text 'moves' once fitted). Pages in
    `look` are drawn differently once any box on them was fitted."""
    engine_name = "stand-in"

    def __init__(self, orig: Path, move=(), look=()):
        self.orig_geo = geometry(orig)
        self.move, self.look = set(move), set(look)

    @contextlib.contextmanager
    def __call__(self):
        yield self

    def _facts(self, page, name, geo):
        x, y, cx, cy = (v / FB.PT for v in geo)
        ox, oy, ocx, ocy = (v / FB.PT for v in self.orig_geo[page - 1][name])
        moved = name in self.move and (x, y, cx, cy) != (ox, oy, ocx, ocy)
        return {"L": x, "T": y, "W": cx, "H": cy, "bl": ox + 7.2 + (3 if moved else 0),
                "bt": oy + 3.6, "bw": 40.0, "bh": 14.0, "lines": 1, "anchor": "t",
                "align": "l", "wrap": False, "mL": 7.2, "mR": 7.2, "mT": 3.6, "mB": 3.6,
                "em": 14.0}

    def measure(self, pptx, keys):
        slides = list(Presentation(str(pptx)).slides)
        res = {}
        for page, sid in keys:
            sh = next(s for s in slides[page - 1].shapes if int(s.shape_id) == sid)
            res[(page, sid)] = self._facts(page, sh.name, (int(sh.left), int(sh.top),
                                                           int(sh.width), int(sh.height)))
        return res

    def render(self, pptx, pages, out_dir):
        from PIL import Image
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        geo = geometry(Path(pptx))
        res = {}
        for p in pages:
            img = Image.new("RGB", (200, 100), "white")
            if p in self.look and geo[p - 1] != self.orig_geo[p - 1]:
                img.paste((0, 0, 0), (0, 0, 20, 20))
            res[p] = Path(out_dir) / f"page_{p:03d}.png"
            img.save(res[p])
        return res


def test_no_powerpoint(deck: Path, work: Path) -> None:
    print("[1] without PowerPoint: skipped with a note, file unchanged")
    d = work / "noppt.pptx"
    d.write_bytes(deck.read_bytes())
    os.environ["SLIDE_LAB_NO_POWERPOINT"] = "1"
    try:
        rec = FB.fit_deck(d)
    finally:
        os.environ.pop("SLIDE_LAB_NO_POWERPOINT", None)
    assert rec["status"] == "skipped" and rec["note"] == FB.NO_PPT_NOTE, rec
    assert d.read_bytes() == deck.read_bytes()
    assert "skipped" in FB.summary_lines(rec)[0]
    print("    ok")


def test_proof_loop(deck: Path, work: Path) -> None:
    print("[2] the proof loop puts boxes back by itself (stand-in measurer)")
    d = work / "loop.pptx"
    d.write_bytes(deck.read_bytes())
    k_move = "one-left"
    eng = FakeEngine(d, move=[k_move], look=[3])
    rec = FB.fit_deck(d, engine_factory=eng, log=lambda s: None)
    assert rec["status"] == "fitted", rec
    assert rec["moved"] == 0 and rec["pixel_pages_changed"] == 0, rec
    assert rec["reverted_pages"] == [3], rec
    geo_b, geo_a = geometry(deck), geometry(d)
    for i in range(N_PAGES):
        assert geo_a[i][k_move] == geo_b[i][k_move], f"page {i + 1}: moving box was not put back"
    assert geo_a[2] == geo_b[2], "page 3 looked different but kept a fitted box"
    assert geo_a[0]["one-center"] != geo_b[0]["one-center"], "nothing fitted on page 1"
    assert rec["rounds"] == 3, rec          # round 1: moved; round 2: page 3; round 3: clean
    # A proof that never passes keeps the deck exactly as it was.
    d2 = work / "loop2.pptx"
    d2.write_bytes(deck.read_bytes())
    eng2 = FakeEngine(d2, move=["one-left", "one-center", "one-right", "wrap-top"],
                      look=list(range(1, N_PAGES + 1)))
    FB.MAX_ROUNDS, saved = 1, FB.MAX_ROUNDS
    try:
        rec2 = FB.fit_deck(d2, engine_factory=eng2, log=lambda s: None)
    finally:
        FB.MAX_ROUNDS = saved
    assert rec2["status"] == "unchanged" and d2.read_bytes() == deck.read_bytes(), rec2
    print(f"    ok: {rec['reverted_boxes']} box(es) put back, page 3 reverted whole, "
          "a failing proof leaves the file as it was")


def _measure(path: Path, names) -> dict:
    """{(page, name): lines} measured by PowerPoint."""
    keys = {}
    for i, s in enumerate(Presentation(str(path)).slides, 1):
        for sh in s.shapes:
            if sh.name in names or any(sh.name.startswith(n) for n in names):
                keys[(i, int(sh.shape_id))] = (i, sh.name)
    with FB._powerpoint_engine() as eng:
        m = eng.measure(path, list(keys))
    return {keys[k]: v for k, v in m.items()}


def _add_word(src: Path, dst: Path, names, word: str) -> None:
    prs = Presentation(str(src))
    for s in prs.slides:
        for sh in s.shapes:
            if sh.name in names or (sh.is_placeholder and sh.placeholder_format.idx == 0):
                r = sh.text_frame.paragraphs[0].runs[-1]
                r.text = r.text + " " + word
    prs.save(str(dst))


def test_powerpoint(deck: Path, work: Path) -> None:
    print("[3] PowerPoint fit: proof passes, kept boxes untouched")
    d = work / "fit.pptx"
    d.write_bytes(deck.read_bytes())
    rec = FB.fit_deck(d, log=lambda s: print("    " + s))
    for ln in FB.summary_lines(rec):
        print("    " + ln)
    assert rec["status"] == "fitted", rec
    assert rec["moved"] == 0 and rec["pixel_pages_changed"] == 0, rec
    sk = rec["skipped_by_rule"]
    assert sk.get("holds a field (page number, date, footer)") == N_PAGES, sk
    # title + a body that inherits shrink-on-overflow + a body that inherits a fill
    assert sk.get("template slot (placeholder)") == 3 * N_PAGES, sk
    assert sk.get("Slide Lab fixed slot (takeaway, footnote, source, section tag)") == 2 * N_PAGES, sk
    assert sk.get("shrinks text on overflow") == N_PAGES, sk
    assert sk.get("visible fill or outline") == 2 * N_PAGES, sk      # filled, outlined
    assert sk.get("a connector is attached") == N_PAGES, sk
    assert sk.get("justified text") == N_PAGES, sk
    gb, ga = geometry(deck), geometry(d)
    xb, xa = _spPr_xml(deck), _spPr_xml(d)
    for i in range(N_PAGES):
        for name in xb[i]:
            if name.startswith(KEEP) or name.startswith("Straight"):
                assert xa[i][name] == xb[i][name], f"page {i + 1}: {name} changed"
    # Every placeholder's xfrm (or its absence) is byte-identical (owner, 2026-10-16:
    # nothing from the template adjusts, not even its height).
    for sb, sa in zip(Presentation(str(deck)).slides, Presentation(str(d)).slides):
        pb = {p.shape_id: p._element.find(f"{qn('p:spPr')}/{qn('a:xfrm')}") for p in sb.placeholders}
        pa = {p.shape_id: p._element.find(f"{qn('p:spPr')}/{qn('a:xfrm')}") for p in sa.placeholders}
        assert pb.keys() == pa.keys() and pb
        for k in pb:
            xb_ = etree.tostring(pb[k]) if pb[k] is not None else None
            xa_ = etree.tostring(pa[k]) if pa[k] is not None else None
            assert xb_ == xa_, f"placeholder {k} geometry changed"
    LI, BI, RI = 91440, 45720, int(Inches(0.54))        # default left/bottom inset, the 0.54" one
    for i in range(N_PAGES):
        a, b = ga[i], gb[i]
        # the left inset became box geometry: the text's left edge is where it was
        assert abs(a["one-left"][0] - (b["one-left"][0] + LI)) <= 1 and a["one-left"][2] < b["one-left"][2]
        assert abs((a["one-center"][0] + a["one-center"][2] / 2)
                   - (b["one-center"][0] + b["one-center"][2] / 2)) <= 2
        assert a["one-center"][2] < b["one-center"][2]
        assert abs((a["one-right"][0] + a["one-right"][2])
                   - (b["one-right"][0] + b["one-right"][2] - LI)) <= 1
        assert a["wrap-top"][1] == b["wrap-top"][1] and a["wrap-top"][3] < b["wrap-top"][3]
        assert abs((a["wrap-bottom"][1] + a["wrap-bottom"][3])
                   - (b["wrap-bottom"][1] + b["wrap-bottom"][3] - BI)) <= 1
        assert a["wrap-bottom"][3] < b["wrap-bottom"][3]
        assert a["wrap-top"][2] <= b["wrap-top"][2]
        # the 0.54" right margin is gone: a narrower box
        assert a["inset-wrap"][2] <= b["inset-wrap"][2] - RI - LI + 1, (a["inset-wrap"], b["inset-wrap"])
    for s in Presentation(str(d)).slides:
        for sh in s.shapes:
            if sh.name in ("one-left", "one-center", "one-right", "wrap-top", "wrap-middle",
                           "wrap-bottom", "inset-wrap"):
                bp = sh.text_frame._txBody.find(qn("a:bodyPr"))
                assert (bp.get("lIns"), bp.get("rIns"), bp.get("bIns")) == ("0", "0", "0"), sh.name
                assert bp.get("tIns") is None, f"{sh.name}: the top margin must stay"
    mb, ma = _measure(deck, ["inset-wrap"]), _measure(d, ["inset-wrap"])
    assert mb and all(mb[k]["lines"] == ma[k]["lines"] >= 2 for k in mb), (mb, ma)
    print(f"    ok: right margin 0.54\" -> 0, narrower box, same {next(iter(mb.values()))['lines']} lines")
    print(f"    ok: {rec['fitted']} fitted in {rec['seconds']} s")

    print("[4] the same fit again changes nothing")
    d2 = work / "fit_again.pptx"
    d2.write_bytes(d.read_bytes())
    rec2 = FB.fit_deck(d2, log=lambda s: None)
    assert rec2["status"] == "unchanged" and d2.read_bytes() == d.read_bytes(), rec2
    print("    ok")

    print("[5] page 5 moved to position 12: its page number stays on one line")
    r = work / "reordered.pptx"
    prs = Presentation(str(d))
    lst = prs.slides._sldIdLst
    ids = list(lst)
    five = ids[4]
    lst.remove(five)
    ids[11].addnext(five)
    prs.save(str(r))
    m = _measure(r, ["page-number"])
    assert len(m) == N_PAGES
    for (page, _n), facts in m.items():
        assert facts.get("lines") == 1, f"page {page}: page number on {facts.get('lines')} lines"
    print("    ok: every page number on one line")

    print("[6] one more short word wraps exactly as in the unfitted deck")
    # The title keeps its layout width; a wrapping box keeps at least 1
    # character or 10% of its width spare, so a one-letter word still fits.
    names = ["wrap-top", "wrap-middle", "wrap-bottom"]
    ub, ua = work / "word_before.pptx", work / "word_after.pptx"
    _add_word(deck, ub, names, "a")
    _add_word(d, ua, names, "a")
    mb, ma = _measure(ub, names + ["Title"]), _measure(ua, names + ["Title"])
    assert mb.keys() == ma.keys() and mb
    for k in mb:
        assert mb[k]["lines"] == ma[k]["lines"], f"{k}: {mb[k]['lines']} -> {ma[k]['lines']} lines"
    print(f"    ok: {len(mb)} boxes, same line counts")

    print("[7] command line: only the pages asked for; original never overwritten")
    src = work / "outside.pptx"
    src.write_bytes(deck.read_bytes())
    assert FB.main([str(src), "--pages", "2", "--out", str(src)]) == 2
    assert FB.main([str(src), "--pages", "2"]) == 0
    out = work / "outside_fitted.pptx"
    assert src.read_bytes() == deck.read_bytes() and out.exists()
    go = geometry(out)
    assert go[1] != gb[1], "page 2 not fitted"
    for i in range(N_PAGES):
        if i != 1:
            assert go[i] == gb[i], f"page {i + 1} changed but was not asked for"
    print("    ok")


def test_compile() -> None:
    print("[8] compile records the fit; check_done prints it")
    import _e2e_harness as H
    import _state
    tmp, out = H.new_build(2)
    try:
        for i in (1, 2):
            H.write_option(out, i)
        picks = {f"slide_{i:02d}": "A" for i in (1, 2)}
        r = H.run("build_review.py", "--out", out)
        assert r.returncode == 0, r.stdout[-2000:]
        token = _state.read_state(out)["review"]["token"]
        body = _state.canonical_picks(picks)
        r = H.run("record_picks.py", "--out", out, "--approved",
                  f"PICKS {body} CHECK {_state.approval_check(token, body)}")
        assert r.returncode == 0, r.stdout[-2000:]
        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out, "--final").returncode == 0
        tok = _state.read_state(out)["final_check"]["token"]
        r = H.run("compile_picks.py", "--out", out, "--final-token", tok)
        assert r.returncode == 0, r.stdout[-3000:]
        assert "[3b] Fit text boxes" in r.stdout, r.stdout[-2000:]
        bf = _state.read_state(out)["stages"]["compile"].get("box_fit")
        assert bf and bf["status"] in ("fitted", "unchanged", "skipped"), bf
        if FB.powerpoint_here():
            assert bf["status"] in ("fitted", "unchanged") and bf["engine"] == "PowerPoint", bf
        md = (out / "COMPILED.md").read_text(encoding="utf-8")
        assert "## Text boxes fitted to their text" in md
        r = H.run("check_done.py", "--out", out)
        assert "text-box fit failed" not in r.stdout, r.stdout[-1500:]
        # check_done refuses a failed fit with the recompile step
        st = _state.read_state(out)
        st["stages"]["compile"]["box_fit"] = {"status": "error", "note": "test"}
        _state._write(out, st)
        r = H.run("check_done.py", "--out", out)
        assert r.returncode == 1 and "text-box fit failed" in r.stdout, r.stdout[-1500:]
        print(f"    ok: compile recorded box_fit status {bf['status']}, "
              f"{bf.get('fitted', 0)} fitted")
    finally:
        H.cleanup(tmp)


def main() -> int:
    work = Path(tempfile.mkdtemp(prefix="boxfit_smoke_"))
    deck = work / "deck.pptx"
    build_deck(deck)
    test_no_powerpoint(deck, work)
    test_proof_loop(deck, work)
    if FB.powerpoint_here():
        test_powerpoint(deck, work)
    else:
        print("[3-7] skipped: PowerPoint is not on this computer")
    test_compile()
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
