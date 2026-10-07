#!/usr/bin/env python3
"""Smoke test: each option's self-check renders into its own folder.

The translator agent rendered into the slide folder and renamed the
renderer's slide_01.png, so two agents converting options B and C of one slide
at the same time shared one picture: option_B_native.png and
option_C_native.png were byte-identical though the designs differed, and one
option was checked against the other's render (2026-10-06).
scripts/selfcheck_render.py renders each option into
slide_NN/_render_tmp/option_X_native/ and copies the result.

With two made-up drawn slides in ONE slide folder:
  1. two self-checks started at the same moment (two processes, as two agents
     would) both succeed and write different pictures, each showing its own
     design; each was rendered in its own folder; a stale slide_01.png in the
     slide folder is left alone
  2. option C has an arrow running into its box: exit 1, listed, and recorded
     in option_C_translation_report.json; option B's report stays clean
  3. the translator agent's instructions use this script, not a shared render

Run:  py -3 slide-builder/tests/run_selfcheck_folder_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SCRIPTS))

from lxml import etree  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402
from pptx.util import Emu  # noqa: E402

PX = 9525


def _drawn(path: Path, x: int, color: str, arrow_into_box: bool) -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(1280 * PX), Emu(720 * PX)
    s = prs.slides.add_slide(prs.slide_layouts[6])
    box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(x * PX), Emu(200 * PX),
                             Emu(400 * PX), Emu(300 * PX))
    box.name = "panel"
    box.fill.solid()
    box.fill.fore_color.rgb = RGBColor.from_string(color)
    if arrow_into_box:
        c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Emu((x - 200) * PX), Emu(350 * PX),
                                   Emu((x + 20) * PX), Emu(350 * PX))
        c.name = "arrow"
        etree.SubElement(c.line._get_or_add_ln(), qn("a:tailEnd"), type="triangle")
    prs.save(str(path))


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="slidelab_selfcheck_"))
    try:
        sd = tmp / "slide_01"
        sd.mkdir()
        _drawn(sd / "option_B_native.pptx", 100, "C0392B", False)    # red, left
        _drawn(sd / "option_C_native.pptx", 760, "1F4E9E", True)     # blue, right
        for letter in "BC":
            (sd / f"option_{letter}_translation_report.json").write_text(
                json.dumps({"warnings": []}), encoding="utf-8")
        stale = sd / "slide_01.png"
        stale.write_bytes(b"an old shared render")

        print("[1] two self-checks at once: two folders, two different pictures")
        procs = {L: subprocess.Popen([sys.executable, str(SCRIPTS / "selfcheck_render.py"),
                                      str(sd / f"option_{L}_native.pptx")],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                 for L in "BC"}
        res = {L: (p.wait(timeout=600), p.stdout.read(), p.stderr.read()) for L, p in procs.items()}
        if any("LibreOffice" in r[1] and "not found" in r[1] for r in res.values()):
            print("    skipped: LibreOffice is not installed here")
            print("SMOKE PASSED.")
            return 0
        assert res["B"][0] == 0, res["B"]
        assert res["C"][0] == 1, res["C"]
        b_png, c_png = sd / "option_B_native.png", sd / "option_C_native.png"
        assert b_png.exists() and c_png.exists()
        assert _md5(b_png) != _md5(c_png), "both options got the same picture"
        from PIL import Image
        for png, (x, y), want in ((b_png, (300, 350), "red"), (c_png, (960, 350), "blue")):
            im = Image.open(png).convert("RGB")
            r, g, b = im.getpixel((int(x * im.width / 1280), int(y * im.height / 720)))
            assert (r > 150 and b < 100) if want == "red" else (b > 120 and r < 80), \
                (png.name, (r, g, b))
        for L in "BC":
            own = sd / "_render_tmp" / f"option_{L}_native" / "slide_01.png"
            assert own.exists(), own
            assert _md5(own) == _md5(sd / f"option_{L}_native.png")
        assert stale.read_bytes() == b"an old shared render", "the shared slide_01.png was touched"
        print("    ok: B is red, C is blue, each from its own folder")

        print("[2] the arrow into C's box is listed and recorded; B stays clean")
        assert "ARROW ENDS" in res["C"][1] and "inside" in res["C"][1], res["C"][1]
        rc = json.loads((sd / "option_C_translation_report.json").read_text(encoding="utf-8"))
        assert [w["code"] for w in rc["warnings"]] == ["MAJOR_ARROW_END_AT_BOX"], rc
        rb = json.loads((sd / "option_B_translation_report.json").read_text(encoding="utf-8"))
        assert rb["warnings"] == [], rb
        print("    ok")

        print("[3] the translator agent's instructions use it")
        md = (SKILL / "agents" / "slide-builder-translator.md").read_text(encoding="utf-8")
        assert "scripts/selfcheck_render.py" in md
        assert "rename to `option_A_native.png`" not in md, "the shared-render step is still there"
        print("    ok")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
