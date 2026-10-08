#!/usr/bin/env python3
"""Smoke test: a slide's source line is never dropped without a word.

The sketch path carries the source line as the template field 'footer', and
finalize writes it into the layout's FOOTER placeholder. On a template whose
source slot is an ordinary text (BODY) placeholder, or that has none, there
was no FOOTER placeholder to find and the line vanished silently
(2026-10-06). Now it is drawn as a text box at the template's source position
and finalize prints a warning.

On a COPY of the bundled test template (the fixture is never changed):
  1. the stock layout (a real FOOTER placeholder) keeps the line in the
     placeholder; nothing extra is drawn, no warning
  2. the same layout with its footer slot turned into a BODY placeholder named
     "Source": the line appears as a shape named 'source' at the template's
     source position, and a warning names the slide and the layout

Run:  py -3 slide-builder/tests/run_source_line_fallback_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))

from pptx import Presentation  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402

import finalize_deck as fd  # noqa: E402
from _chrome_schema import load_chrome_yml  # noqa: E402
from twins.composer import clone_missing_chrome_placeholders  # noqa: E402
from twins.helpers import _chrome_box_for  # noqa: E402

FIXTURE = HERE / "fixtures" / "layout_diverse_template.pptx"
# The fixture's sidecar folder (written by run_layout_inheritance_smoke.py). The
# old flat path (layout_diverse_template.chrome.yml) exists only on machines
# that registered the fixture long ago, so a fresh clone failed here.
import _paths as _p  # noqa: E402
CHROME = _p.chrome_yml(FIXTURE)
LAYOUT = "body_canonical_light"
SOURCE = "Source: sample data for the test, not real"


def _footer_to_body(src: Path, dst: Path) -> None:
    """The copy's footer slot becomes a BODY placeholder named 'Source'."""
    prs = Presentation(str(src))
    lay = next(l for l in prs.slide_layouts if l.name == LAYOUT)
    changed = 0
    for ph in lay.placeholders:
        if int(ph.placeholder_format.type) == 15:
            el = ph._element.find(".//" + qn("p:nvPr")).find(qn("p:ph"))
            el.set("type", "body")
            el.set("idx", "20")
            ph._element.find(".//" + qn("p:cNvPr")).set("name", "Source")
            changed += 1
    assert changed == 1, f"expected one footer slot on {LAYOUT}, found {changed}"
    prs.save(str(dst))


def _finish(template: Path):
    prs = Presentation(str(template))
    lay = next(l for l in prs.slide_layouts if l.name == LAYOUT)
    chrome = load_chrome_yml(CHROME).layouts[LAYOUT]
    slide = prs.slides.add_slide(lay)
    clone_missing_chrome_placeholders(slide, lay)
    src = Presentation().slides.add_slide(Presentation().slide_layouts[6])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fd._apply_body_canonical_finishing(
            slide, prs, chrome, src, 3,
            template_fields_override={"title": "A test title", "footer": SOURCE})
    return slide, chrome, buf.getvalue()


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="slidelab_source_line_"))
    try:
        stock = tmp / "stock.pptx"
        shutil.copy2(FIXTURE, stock)
        body = tmp / "source_as_body.pptx"
        _footer_to_body(stock, body)

        print("[1] stock layout: the line goes into the footer placeholder")
        slide, _chrome, out = _finish(stock)
        holders = [s for s in slide.placeholders
                   if int(s.placeholder_format.type) == 15 and SOURCE in s.text_frame.text]
        assert holders, "the stock layout lost its source line"
        assert not [s for s in slide.shapes if s.name == "source"], "drew a second copy"
        assert "WARN" not in out, out
        print("    ok")

        print("[2] footer slot is a BODY 'Source' slot: drawn at the source position, warned")
        slide, chrome, out = _finish(body)
        texts = [s for s in slide.shapes if getattr(s, "has_text_frame", False)
                 and SOURCE in s.text_frame.text]
        assert texts, "the source line was dropped silently"
        shape = texts[0]
        assert shape.name == "source" and not shape.is_placeholder, shape.name
        box = _chrome_box_for(chrome, "source")
        # Owner's chrome rule (2026-10-08): the source line starts at the
        # title's text left edge, at the template's source height.
        from twins.chrome_rules import _title_geometry
        text_left = _title_geometry(slide, chrome)[0]
        assert abs(int(shape.left) - text_left) < 9525 and \
            abs(int(shape.top) / 9525 - box.y_px) < 1, (shape.left, shape.top, text_left, box)
        assert "WARN" in out and "slide 3" in out and LAYOUT in out, out
        print(f"    ok: at x={text_left / 9525:.0f} (title's text edge), y={box.y_px} px; "
              f"{out.strip()[:90]}...")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
