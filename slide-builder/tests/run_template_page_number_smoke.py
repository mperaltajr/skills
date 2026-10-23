#!/usr/bin/env python3
"""Smoke: a template with no page-number setting still gives numbered pages.

Seen on a client template (2026-10-23): its slide master and layouts had no
header/footer setting (<p:hf>), so PowerPoint added new slides with slide
numbering off and a page added in PowerPoint had no page number, although
every layout had a working slide-number box. Separately, the registration
mock slide had no page number, because python-pptx's add_slide skips the
layout's slide-number box.

A template is generated here (python-pptx's default master and layouts carry
no <p:hf>; one layout also gets an <p:extLst> so the schema order is tested),
then registered the way a real registration writes its files. Checks:
  1  build-template.pptx: the master and every layout have
     <p:hf hdr="0" ftr="0" dt="0"/>, before <p:txStyles> on the master and
     before <p:extLst> on the layout that has one
  2  the registration printed the page-number note and the one-line offer
     with the add-page-numbers command
  3  the original template is byte for byte unchanged
  4  the mock slide has a slide-number box holding a slide-number field, and
     the self-test reports "page number shows"
  5  add-page-numbers on a COPY of the original adds the setting, changes only
     the master and layout parts, and a second run does nothing
  6  when PowerPoint is installed: AddSlide on two layouts of the build copy
     (opened read-only through ppt_safe) gives a visible slide-number box
     showing the slide's number; on the original it does not

Run:  py -3 slide-builder/tests/run_template_page_number_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCRIPTS = SKILL / "scripts"
QC = SKILL.parent / "slide-qc" / "scripts"
for _d in (HERE, SKILL, SCRIPTS, QC):
    sys.path.insert(0, str(_d))

import run_layout_inheritance_smoke as fixture  # noqa: E402
import _paths as _p  # noqa: E402
import register_template as rt  # noqa: E402
from lxml import etree  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402
from twins.composer import is_page_number_shape, has_slidenum_field  # noqa: E402

LAYOUT = "body_canonical_light"
EXT_LAYOUT = "section_divider"   # gets an <p:extLst> before registration


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _children(el) -> list[str]:
    return [etree.QName(c).localname for c in el]


def _make_template(path: Path) -> None:
    fixture.build_fixture(path)
    prs = Presentation(str(path))
    for lay in prs.slide_masters[0].slide_layouts:
        if lay.name == EXT_LAYOUT:
            ext = etree.SubElement(lay._element, qn("p:extLst"))
            etree.SubElement(ext, qn("p:ext"), uri="{DCECCB84-F9BA-43D5-87BE-67443E8EF086}")
    prs.save(str(path))
    p2 = Presentation(str(path))
    assert p2.slide_masters[0]._element.find(qn("p:hf")) is None, "setup: master has <p:hf>"
    assert all(l._element.find(qn("p:hf")) is None for l in p2.slide_masters[0].slide_layouts), \
        "setup: a layout has <p:hf>"


def _check_hf(prs) -> None:
    for m in prs.slide_masters:
        kids = _children(m._element)
        assert "hf" in kids, f"master has no <p:hf>: {kids}"
        hf = m._element.find(qn("p:hf"))
        assert (hf.get("hdr"), hf.get("ftr"), hf.get("dt"), hf.get("sldNum")) == ("0", "0", "0", None), \
            f"master <p:hf> attributes wrong: {dict(hf.attrib)}"
        if "txStyles" in kids:
            assert kids.index("hf") == kids.index("txStyles") - 1, f"master order wrong: {kids}"
        for lay in m.slide_layouts:
            kids = _children(lay._element)
            assert "hf" in kids, f"layout {lay.name!r} has no <p:hf>: {kids}"
            if "extLst" in kids:
                assert kids.index("hf") == kids.index("extLst") - 1, \
                    f"layout {lay.name!r} order wrong: {kids}"
            else:
                assert kids[-1] == "hf", f"layout {lay.name!r}: <p:hf> not last: {kids}"
    ext_kids = next(_children(l._element) for l in prs.slide_masters[0].slide_layouts
                    if l.name == EXT_LAYOUT)
    assert ext_kids[-2:] == ["hf", "extLst"], f"extLst layout order wrong: {ext_kids}"


def _ppt_add_slides(pptx: Path) -> list[tuple[str, bool, str, int]]:
    import ppt_safe
    out = []
    with ppt_safe.session() as (app, _):
        with ppt_safe.opened(app, pptx) as pres:
            lays = pres.SlideMaster.CustomLayouts
            for li in range(1, lays.Count + 1):
                lay = lays(li)
                if lay.Name not in (LAYOUT, EXT_LAYOUT):
                    continue
                sl = pres.Slides.AddSlide(pres.Slides.Count + 1, lay)
                num = [s for s in range(1, sl.Shapes.Count + 1)
                       if sl.Shapes(s).Type == 14 and sl.Shapes(s).PlaceholderFormat.Type == 13]
                txt = sl.Shapes(num[0]).TextFrame.TextRange.Text if num else ""
                out.append((lay.Name, bool(num), txt, int(sl.HeadersFooters.SlideNumber.Visible)))
    return out


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="tpl_page_number_smoke_"))
    try:
        tpl = tmp / "no_hf_template.pptx"
        _make_template(tpl)
        sha_before = _sha(tpl)

        print("[1] Registration adds the page-number setting to the build copy")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            fixture.register_fixture(tpl)
        log = buf.getvalue()
        build_tpl = _p.build_template_pptx(tpl)
        assert build_tpl.exists(), f"no build copy at {build_tpl}"
        _check_hf(Presentation(str(build_tpl)))
        print("    ok: master and every layout have <p:hf hdr=0 ftr=0 dt=0>, in schema order")

        print("[2] The user is told, with a one-line offer")
        assert "NOTE (page numbers)" in log, f"no page-number note:\n{log[-1500:]}"
        assert "your original file was not changed" in log, log[-1500:]
        assert "Want me to fix that in your original file too?" in log, log[-1500:]
        assert "add-page-numbers" in log, log[-1500:]
        print("    ok: note + offer + command printed")

        print("[3] The original template is untouched")
        assert _sha(tpl) == sha_before, "registration changed the original template"
        assert Presentation(str(tpl)).slide_masters[0]._element.find(qn("p:hf")) is None
        print("    ok: original byte for byte the same")

        print("[4] The mock slide has a page number")
        tj = _p.theme_json(tpl)
        data = json.loads(tj.read_text(encoding="utf-8"))
        data["default_content_layout"] = LAYOUT
        tj.write_text(json.dumps(data, indent=2), encoding="utf-8")
        fails, infos = rt._render_mock_page_selftest(tpl)
        assert fails == [], f"self-test failed: {fails}"
        assert any(i.startswith("page number shows") for i in infos), infos
        mock = Presentation(str(_p.selftest_pptx(tpl)))
        nums = [sh for sh in mock.slides[0].shapes if is_page_number_shape(sh)]
        assert nums, "mock slide has no slide-number box"
        assert any(sh.is_placeholder and int(sh.placeholder_format.type) == 13 for sh in nums), \
            "the page number is not the layout's slide-number placeholder"
        assert all(has_slidenum_field(sh) for sh in nums), "slide-number box holds no field"
        print("    ok: slide-number placeholder with a slide-number field; self-test says so")

        print("[5] add-page-numbers fixes a copy of the original, on request only")
        orig2 = tmp / "copy_of_original.pptx"
        shutil.copy2(tpl, orig2)
        cmd = [sys.executable, str(SCRIPTS / "register_template.py"), "add-page-numbers", str(orig2)]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, r.stdout + r.stderr
        assert "Added the page-number setting" in r.stdout, r.stdout
        _check_hf(Presentation(str(orig2)))
        with zipfile.ZipFile(tpl) as a, zipfile.ZipFile(orig2) as b:
            assert a.namelist() == b.namelist(), "part list changed"
            changed = [n for n in a.namelist() if a.read(n) != b.read(n)]
        assert changed and all(n.startswith(("ppt/slideMasters/", "ppt/slideLayouts/"))
                               and n.endswith(".xml") for n in changed), changed
        r2 = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        assert r2.returncode == 0 and "Nothing to do" in r2.stdout, r2.stdout + r2.stderr
        print(f"    ok: {len(changed)} master/layout parts changed, nothing else; second run is a no-op")

        print("[6] PowerPoint: a page added on the build copy gets a page number")
        import render_slides as RS
        if sys.platform == "win32" and RS.powerpoint_available():
            before = _ppt_add_slides(tpl)
            after = _ppt_add_slides(build_tpl)
            for name, has, txt, vis in before:
                print(f"    original   {name:22s} number box {'yes' if has else 'no '} text={txt!r} visible={vis}")
            for name, has, txt, vis in after:
                print(f"    build copy {name:22s} number box {'yes' if has else 'no '} text={txt!r} visible={vis}")
            assert len(after) == 2, after
            assert all(has and vis != 0 for _n, has, _t, vis in after), after
            assert [t for *_x, t, _v in after] == ["1", "2"] or \
                sorted(t for *_x, t, _v in after) == ["1", "2"], after
            assert all(vis == 0 for *_x, vis in before), \
                "setup: PowerPoint numbered new slides on the original (test template not missing <p:hf>?)"
            print("    ok: visible slide-number box showing its number on each new page")
        else:
            print("    skipped: PowerPoint is not installed here")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
