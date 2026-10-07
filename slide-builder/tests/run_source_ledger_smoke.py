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
    or has not resolved each slot;
  * a PDF page or a picture (no shape tree) gets an honest ledger: no rows, the
    whole page recorded as checked by eye only, compile proceeds, and delivery
    says so (before 2026-10-06 `build` crashed and the pin could never compile).

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
        _state.record_review(out)
        # The rest of the approval chain, so the ledger is the only thing
        # standing between this build and a compile.
        _state.record_picks(out, {"slide_01": "A"})
        tok = _state.record_final_check(out, {})
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

        _visual_pages(tmp, env)
        _pinned_pdf_compiles(tmp)
        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _fictional_page(path: Path) -> None:
    """A made-up one-page PDF or picture (never a client file)."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (1280, 720), "white")
    d = ImageDraw.Draw(img)
    d.text((80, 80), "Sample page: output grows to 12 units by year 3", fill="black")
    d.rectangle((80, 200, 600, 400), outline="black")
    img.save(str(path))


def _visual_pages(tmp: Path, env: dict) -> None:
    import check_done
    print("[7] a PDF or a picture: an honest ledger, checked by eye only")
    for suffix in (".pdf", ".png"):
        out = tmp / f"build_{suffix[1:]}"; out.mkdir()
        page = tmp / f"sample_page{suffix}"
        _fictional_page(page)
        _state.record_prep(out, "h", out)
        _state.record_review(out)
        _state.record_picks(out, {"slide_01": "A"})
        tok = _state.record_final_check(out, {})
        r = subprocess.run([sys.executable, str(SCRIPTS / "source_ledger.py"), "build",
                            "--out", str(out), "--deck", str(page), "--slide", "1"],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stdout[-400:] + r.stderr[-800:]
        assert "CHECKED BY EYE ONLY" in r.stdout, r.stdout
        led = json.loads((out / "source_ledger.json").read_text(encoding="utf-8"))
        assert led["rows"] == [], "nothing on a PDF or picture may be claimed as bound"
        assert led["source_kind"] == "visual", led
        assert len(led["unreachable"]) == 1 and "by eye only" in led["unreachable"][0]["why"]
        st = _state.read_state(out)["source_ledger"]
        assert st["visual_only"] and st["unresolved"] == 0 and st["unreachable"] == 1, st
        ok, why = _state.check_compile_allowed(out, tok)
        assert ok, f"compile still refused for a {suffix} page: {why}"
        qc = json.loads((out / "brief_qc.json").read_text(encoding="utf-8"))
        assert "by eye only" in qc["summary"], qc["summary"]
        line = check_done.supplied_page_line(st)
        assert "CHECKED BY EYE ONLY" in line, line
        # status keeps the record honest
        subprocess.run([sys.executable, str(SCRIPTS / "source_ledger.py"), "status",
                        "--out", str(out)], capture_output=True, text=True, env=env)
        assert _state.read_state(out)["source_ledger"]["visual_only"], "status lost the flag"
        print(f"    ok ({suffix}): {led['unreachable'][0]['why'][:70]}...")
    r = subprocess.run([sys.executable, str(SCRIPTS / "source_ledger.py"), "build",
                        "--out", str(tmp / "build_pdf"), "--deck", str(tmp / "sample_page.pdf"),
                        "--slide", "2"], capture_output=True, text=True, env=env)
    assert r.returncode == 2 and "out of range" in r.stderr, r.stderr[-400:]
    other = tmp / "page.docx"; other.write_bytes(b"not a page")
    r = subprocess.run([sys.executable, str(SCRIPTS / "source_ledger.py"), "build",
                        "--out", str(tmp / "build_pdf"), "--deck", str(other)],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 2 and "Traceback" not in r.stderr and "PDF" in r.stderr, r.stderr
    print("    ok: a page past the PDF's end and an unsupported file are refused plainly")


def _pinned_pdf_compiles(tmp: Path) -> None:
    """[8] the real pipeline: a slide pinned to a PDF page compiles once the
    ledger is built from that PDF (before: build crashed, compile refused)."""
    print("[8] a slide pinned to a PDF page compiles")
    sys.path.insert(0, str(HERE))
    import _e2e_harness as H
    page = tmp / "pinned_page.pdf"
    _fictional_page(page)
    root = Path(tempfile.mkdtemp(prefix="slidelab_pin_pdf_"))
    try:
        brief = root / "brief.md"
        slides = H.SLIDE.format(n=1).replace(
            "**Slide type:** Content",
            f"**Slide type:** Content\n**Pinned source page:** {page.name} slide 1")
        brief.write_text(H.BRIEF.format(slides=slides), encoding="utf-8")
        assert H.run("seal_brief.py", "--brief", brief, "--accepted", "test brief").returncode == 0
        out = root / "out"
        r = H.run("build_deck.py", "--brief", brief, "--template", H.TEMPLATE,
                  "--out", out, "--pattern", "direct")
        assert r.returncode == 0, r.stderr[-800:]
        H.write_option(out, 1)
        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out).returncode == 0
        tok = _state.read_state(out)["review"]["token"]
        body = _state.canonical_picks({"slide_01": "A"})
        assert H.run("record_picks.py", "--out", out, "--approved",
                     f"PICKS {body} CHECK {_state.approval_check(tok, body)}").returncode == 0
        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out, "--final").returncode == 0
        ftok = _state.read_state(out)["final_check"]["token"]
        r = H.run("compile_picks.py", "--out", out, "--final-token", ftok)
        assert r.returncode == 5 and "never reconciled" in r.stdout, r.stdout[-600:]
        r = H.run("source_ledger.py", "build", "--out", out, "--deck", page, "--slide", "1")
        assert r.returncode == 0, r.stdout[-600:] + r.stderr[-800:]
        r = H.run("compile_picks.py", "--out", out, "--final-token", ftok)
        assert r.returncode == 0, r.stdout[-1500:]
        print("    ok: refused before the ledger, compiled after it")
    finally:
        H.cleanup(root)


if __name__ == "__main__":
    sys.exit(main())
