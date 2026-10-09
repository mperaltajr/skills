"""_qc_helper.py — stand in for slide-qc's vision round in tests.

Not a production path. The tests need a recorded quality-check round without
a person reading pictures, so this does what an honest reviewer does: it
takes this round's codes from the plan (in memory; a real session reads them
off the pictures), quotes each page's own text, and writes the notes.

  fake_render(out, deck)  page images + render_manifest.json without a
                          renderer (one distinct picture per page; `vary`
                          changes the picture of the pages listed)
  read_round(out, ...)    plan + notes + record_vision_qc.py; returns
                          (exit code, output, plan)
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HERE.parents[1] / "slide-qc" / "scripts"))

import qc_pages  # noqa: E402
import render_manifest as RM  # noqa: E402
import _state  # noqa: E402


def _n_slides(deck) -> int:
    from pptx import Presentation
    return len(Presentation(str(deck)).slides)


def fake_render(out, deck, renderer: str = "libreoffice", dpi: int = 150,
                vary: dict | None = None) -> dict:
    """slide_NN.png per page in out/_qc plus the manifest. vary={page: tag}
    draws those pages differently (a changed page)."""
    from PIL import Image, ImageDraw
    qc = qc_pages.qc_dir(out)
    qc.mkdir(parents=True, exist_ok=True)
    for p in qc.glob("slide_*.png"):
        p.unlink()
    for n in range(1, _n_slides(deck) + 1):
        im = Image.new("RGB", (400, 225), (250, 250, 250))
        d = ImageDraw.Draw(im)
        d.text((20, 20), f"page {n} {(vary or {}).get(n, '')}", fill=(0, 0, 0))
        d.rectangle([20, 60, 20 + 30 * n % 360, 120], fill=(30, 60, 120))
        im.save(qc / f"slide_{n:02d}.png")
    return RM.write(qc, deck, renderer, dpi, writer="test")


def _quote(text: str) -> str:
    for line in text.splitlines():
        w = line.split()
        if len(re.findall(r"[A-Za-z0-9%$]+", line)) >= 3:
            return " ".join(w[:6])
    return ""


def fill_notes(out, plan: dict, findings: dict | None = None,
               look_findings: list | None = None, skip_pages=(), wrong_code_pages=(),
               bad_quote_pages=(), skip_look=False, deck=None) -> dict:
    codes = plan["_codes"]
    deck = deck or plan["deck"]
    texts = qc_pages.page_texts(deck)
    notes_p = qc_pages.qc_dir(out) / qc_pages.NOTES
    notes = json.loads(notes_p.read_text(encoding="utf-8"))
    for e in notes["pages"]:
        n = e["page"]
        if n in skip_pages:
            continue
        e["code"] = "XXXXXX" if n in wrong_code_pages else codes[f"page:{n}"]
        q = _quote(texts[n - 1])
        if q:
            e["quote"] = "words that are on no page" if n in bad_quote_pages else q
        else:
            e["seen"] = "a plain page with shapes and no text"
        e["findings"] = list((findings or {}).get(n, []))
    if not skip_look:
        for f in notes["deck_look"]["codes"]:
            notes["deck_look"]["codes"][f] = codes[f"look:{f}"]
    notes["deck_look"]["findings"] = list(look_findings or [])
    notes_p.write_text(json.dumps(notes, indent=2), encoding="utf-8")
    return notes


def record(out, *extra) -> tuple[int, str]:
    import record_vision_qc
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = record_vision_qc.main(["--out", str(out), *map(str, extra)])
    return rc, buf.getvalue()


def read_round(out, deck=None, findings=None, look_findings=None, also=None,
               record_args=(), **fill) -> tuple[int, str, dict]:
    """One honest round: plan, read every page in it, record."""
    plan = qc_pages.make_plan(out, deck, also=also, _return_codes=True)
    fill_notes(out, plan, findings, look_findings, deck=deck, **fill)
    rc, o = record(out, *(["--deck", str(deck)] if deck else []), *record_args)
    return rc, o, plan
