#!/usr/bin/env python3
"""Smoke test for the supplied-page figure ledger.

Two real failures collide in this feature. A supplied one-pager was replaced by
an exec-summary nobody asked for; and a faithful replica shipped the source's
stale numbers ($300B / 6-12 months / 3x) when the brief already had the verified
values. Fixing the first naively causes the second.

The ledger's contract, which this test pins down:
  * only FIGURE-BEARING slots are listed (prompting on all 30+ text surfaces
    produces a bulk-accept reflex, which is how always-on signals went blind);
  * table cells and grouped shapes ARE included (that is where a one-pager keeps
    its numbers);
  * surfaces that cannot be read at all are reported, never silently passed;
  * an unresolved row BLOCKS the compile;
  * the machine never claims the figures match the brief, only that a human has
    or has not resolved each slot.

Run:  py -3 slide-builder/tests/run_source_ledger_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from pptx import Presentation  # noqa: E402
from pptx.util import Inches  # noqa: E402

import _state  # noqa: E402

TINY_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000a49444154789c6360000002000100ffff03000006000557bfabd4000000"
    "0049454e44ae426082")


def _supplied_page(path: Path, png: Path):
    prs = Presentation()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    tb = s.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(6), Inches(0.6))
    tb.text_frame.text = "Market reaches $300B by 2027"
    note = s.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(6), Inches(0.4))
    note.text_frame.text = "Prepared for the steering committee"   # no figure
    t = s.shapes.add_table(2, 2, Inches(0.5), Inches(1.2), Inches(5), Inches(1)).table
    t.cell(0, 0).text = "Lead time"; t.cell(0, 1).text = "6-12 months"
    t.cell(1, 0).text = "Upside";    t.cell(1, 1).text = "3x"
    png.write_bytes(TINY_PNG)
    s.shapes.add_picture(str(png), Inches(6), Inches(2), Inches(1), Inches(1))
    prs.save(str(path))


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="source_ledger_smoke_"))
    try:
        out = tmp / "build"; out.mkdir()
        page = tmp / "one_pager.pptx"
        _supplied_page(page, tmp / "x.png")
        _state.record_prep(out, "h", out)
        tok = _state.record_review(out)
        env = {**os.environ, "PYTHONPATH": str(SCRIPTS)}

        print("[1] only figure-bearing slots are listed, incl. table cells")
        r = subprocess.run([sys.executable, str(SCRIPTS / "source_ledger.py"), "build",
                            "--out", str(out), "--deck", str(page), "--slide", "1"],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stderr[-400:]
        led = json.loads((out / "source_ledger.json").read_text(encoding="utf-8"))
        texts = [row["source_text"] for row in led["rows"]]
        assert "6-12 months" in texts and "3x" in texts, f"table figures missed: {texts}"
        assert any("$300B" in t for t in texts), texts
        assert not any("steering committee" in t for t in texts), \
            "a non-figure surface was listed; that is the bulk-accept failure mode"
        print(f"    ok: {len(texts)} figure slot(s), prose left out")

        print("[2] unreadable surfaces are reported, not silently passed")
        assert led["unreachable"], "the picture should be reported as unreadable"
        assert "picture" in led["unreachable"][0]["why"]
        print(f"    ok: {led['unreachable'][0]['why']}")

        print("[3] unresolved rows BLOCK the compile")
        ok, why = _state.check_compile_allowed(out, tok)
        assert not ok and "unreconciled" in why, why
        print("    ok: compile refused while figures are unreconciled")

        print("[4] replace_with needs an actual replacement")
        for row in led["rows"]:
            row["resolution"] = "replace_with"      # but no replacement value
        (out / "source_ledger.json").write_text(json.dumps(led), encoding="utf-8")
        subprocess.run([sys.executable, str(SCRIPTS / "source_ledger.py"), "status",
                        "--out", str(out)], capture_output=True, text=True, env=env)
        ok, _ = _state.check_compile_allowed(out, tok)
        assert not ok, "an empty replacement must not count as resolved"
        print("    ok: a blank replacement is not a resolution")

        print("[5] resolving every row releases the compile")
        for row in led["rows"]:
            if row["source_text"] == "6-12 months":
                row["resolution"] = "replace_with"; row["replacement"] = "sold out"
            elif "$300B" in row["source_text"]:
                row["resolution"] = "bind_from_brief"
            else:
                row["resolution"] = "keep_source"
        (out / "source_ledger.json").write_text(json.dumps(led), encoding="utf-8")
        subprocess.run([sys.executable, str(SCRIPTS / "source_ledger.py"), "status",
                        "--out", str(out)], capture_output=True, text=True, env=env)
        ok, why = _state.check_compile_allowed(out, tok)
        assert ok, f"compile still refused after reconciliation: {why}"
        print("    ok: compile released once every slot is resolved by a human")

        print("[6] the review banner never reports a green 'no conflicts'")
        qc = json.loads((out / "brief_qc.json").read_text(encoding="utf-8"))
        assert "kept from source" in qc["summary"], qc["summary"]
        assert "unreadable" in qc["summary"], qc["summary"]
        assert any("NOT checked" in w for w in qc["warnings"]), qc["warnings"]
        st = _state.read_state(out)["source_ledger"]
        assert st["keep_source"] >= 1 and st["unreachable"] >= 1, st
        print(f"    ok: {qc['summary']}")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
