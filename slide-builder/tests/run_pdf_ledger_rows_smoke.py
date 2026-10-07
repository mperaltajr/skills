#!/usr/bin/env python3
"""Smoke test: a pinned PDF page with a text layer lists its figures as rows.

Owner decision (2026-10-06): when the supplied page is a PDF whose text can be
read, compile waits until the user resolves each figure on it, the same as for
a PowerPoint page. Scans and pictures stay "checked by eye only" (batch 1).

With a made-up PDF (never a client file):
  1. a two-page PDF with text: `build --slide 1` lists only the lines that carry
     a figure, as rows with no resolution; a picture on the page goes to the
     vision pass; the record says 2 unresolved and the compile gate refuses
  2. resolving the rows (bind_from_brief / replace_with + replacement) and
     running `status` lets the gate pass; the delivery line is the normal one,
     not "checked by eye only"
  3. `--slide 2` reads the second page's lines
  4. a PDF with no text layer (a scanned page) is still "checked by eye only"

Run:  py -3 slide-builder/tests/run_pdf_ledger_rows_smoke.py
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

import _state  # noqa: E402
import check_done  # noqa: E402

PAGE_1 = ["Sample heading for a made-up page",
          "Output grows to 12 units by year 3",
          "Plain words without any figure here",
          "Margin reaches 40% in the test case"]
PAGE_2 = ["Second page of the made-up file", "Costs fall by 5x over the period"]


def _text_pdf(path: Path, picture: Path) -> None:
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(path), pagesize=landscape(letter))
    y = 540
    for line in PAGE_1:
        c.drawString(72, y, line)
        y -= 28
    c.drawImage(str(picture), 400, 100, width=160, height=90)
    c.showPage()
    y = 540
    for line in PAGE_2:
        c.drawString(72, y, line)
        y -= 28
    c.showPage()
    c.save()


def _picture(path: Path) -> None:
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (320, 180), "white")
    ImageDraw.Draw(img).text((20, 20), "a chart with 7 bars", fill="black")
    img.save(str(path))


def _gated_out(tmp: Path, name: str) -> tuple[Path, str]:
    out = tmp / name
    out.mkdir()
    _state.record_prep(out, "h", out)
    _state.record_review(out)
    _state.record_picks(out, {"slide_01": "A"})
    return out, _state.record_final_check(out, {})


def _ledger(env, out: Path, deck: Path, slide: int) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / "source_ledger.py"), "build",
                           "--out", str(out), "--deck", str(deck), "--slide", str(slide)],
                          capture_output=True, text=True, env=env)


def main() -> int:
    env = dict(os.environ, SLIDE_LAB_NO_OPEN="1")
    tmp = Path(tempfile.mkdtemp(prefix="slidelab_pdf_rows_"))
    try:
        pic = tmp / "pic.png"
        _picture(pic)
        pdf = tmp / "made_up_page.pdf"
        _text_pdf(pdf, pic)

        print("[1] a PDF with text: figure lines become rows; compile refuses")
        out, tok = _gated_out(tmp, "build_rows")
        r = _ledger(env, out, pdf, 1)
        assert r.returncode == 0, r.stdout[-400:] + r.stderr[-800:]
        assert "BY EYE ONLY" not in r.stdout, r.stdout
        led = json.loads((out / "source_ledger.json").read_text(encoding="utf-8"))
        assert led["source_kind"] == "pdf_text", led["source_kind"]
        texts = [row["source_text"] for row in led["rows"]]
        assert texts == [PAGE_1[1], PAGE_1[3]], texts
        assert all(row["resolution"] is None and row["kind"] == "pdf_text"
                   for row in led["rows"]), led["rows"]
        assert [u["kind"] for u in led["unreachable"]] == ["picture"], led["unreachable"]
        st = _state.read_state(out)["source_ledger"]
        assert st["unresolved"] == 2 and not st["visual_only"] and st["unreachable"] == 1, st
        ok, why = _state.check_compile_allowed(out, tok)
        assert not ok and "unreconciled" in why, (ok, why)
        print(f"    ok: {len(texts)} rows, 1 picture to the vision pass; refused: {why[:60]}...")

        print("[2] resolved rows let the compile through; normal delivery line")
        led["rows"][0]["resolution"] = "bind_from_brief"
        led["rows"][1]["resolution"] = "replace_with"
        (out / "source_ledger.json").write_text(json.dumps(led), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPTS / "source_ledger.py"), "status",
                            "--out", str(out)], capture_output=True, text=True, env=env)
        assert r.returncode == 1, "replace_with without a replacement is not resolved"
        led["rows"][1]["replacement"] = "Margin reaches 45% in the test case"
        (out / "source_ledger.json").write_text(json.dumps(led), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPTS / "source_ledger.py"), "status",
                            "--out", str(out)], capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stdout
        ok, why = _state.check_compile_allowed(out, tok)
        assert ok, why
        line = check_done.supplied_page_line(_state.read_state(out)["source_ledger"])
        assert "BY EYE ONLY" not in line and "1 surface(s)" in line, line
        print("    ok")

        print("[3] --slide 2 reads the second page")
        out2, _ = _gated_out(tmp, "build_page2")
        assert _ledger(env, out2, pdf, 2).returncode == 0
        led2 = json.loads((out2 / "source_ledger.json").read_text(encoding="utf-8"))
        assert [row["source_text"] for row in led2["rows"]] == [PAGE_2[1]], led2["rows"]
        assert led2["rows"][0]["addr"].startswith("p2/"), led2["rows"][0]["addr"]
        print("    ok")

        print("[4] a scanned PDF (no text layer) is still checked by eye only")
        from PIL import Image
        scan = tmp / "scanned_page.pdf"
        Image.open(pic).save(str(scan))
        out3, tok3 = _gated_out(tmp, "build_scan")
        r = _ledger(env, out3, scan, 1)
        assert r.returncode == 0 and "CHECKED BY EYE ONLY" in r.stdout, r.stdout
        led3 = json.loads((out3 / "source_ledger.json").read_text(encoding="utf-8"))
        assert led3["source_kind"] == "visual" and led3["rows"] == [], led3
        assert "scan" in led3["unreachable"][0]["why"], led3["unreachable"]
        assert _state.check_compile_allowed(out3, tok3)[0]
        print("    ok")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
