#!/usr/bin/env python3
"""Smoke test: the page-number graft must PRESERVE the template's character
formatting (size, color, typeface), at BOTH call sites.

Background. Auto-number fields (<a:fld type="slidenum">) do not render under
LibreOffice headless, so the pipeline replaces them with literal text. But on many
templates the field's own <a:rPr> is the ONLY carrier of size/color/typeface: the
layout AND master can both ship an empty <a:lstStyle/>. Dropping the field used to
discard all three, so the number fell back to the presentation default (~13pt
black) and double digits stacked vertically in a narrow box. That is the
"page numbers render large" defect.

There are TWO places that rewrite a slide-number placeholder:
  1. twins/composer.py::write_literal_run_preserving_field (used by finalize's graft)
  2. scripts/compile_picks.py::_restamp_page_number (re-stamps position at compile)
A fix to only one lets compile re-introduce the defect. This test covers both.

Run:  py -3 slide-builder/tests/run_page_number_format_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))

from lxml import etree  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402
from pptx.util import Inches  # noqa: E402

from twins.composer import write_literal_run_preserving_field  # noqa: E402

FIELD_XML = (
    '<a:fld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'id="{4D2A7B31-0000-0000-0000-000000000001}" type="slidenum">'
    '<a:rPr lang="en-US" sz="800">'
    '<a:solidFill><a:srgbClr val="8A93A0"/></a:solidFill>'
    '<a:latin typeface="Arial"/></a:rPr>'
    '<a:t>2</a:t></a:fld>'
)


def _para_with_field():
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    tb = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(1), Inches(0.3))
    para = tb.text_frame.paragraphs[0]
    para._p.append(etree.fromstring(FIELD_XML))
    return prs, slide, tb, para


def _assert_formatting(rpr, where: str):
    assert rpr is not None, f"{where}: run has NO rPr — formatting was lost"
    assert rpr.get("sz") == "800", f"{where}: size lost (sz={rpr.get('sz')})"
    latin = rpr.find(qn("a:latin"))
    assert latin is not None and latin.get("typeface") == "Arial", f"{where}: typeface lost"
    assert rpr.find(qn("a:solidFill")) is not None, f"{where}: color lost"


def main() -> int:
    print("[1] composer graft keeps the field's size, color and typeface")
    _prs, _s, _tb, para = _para_with_field()
    run = write_literal_run_preserving_field(para, 7)
    _assert_formatting(run._r.find(qn("a:rPr")), "composer")
    assert run.text == "7", run.text
    assert para._p.find(qn("a:fld")) is None, "field must be replaced (LibreOffice can't render it)"
    print("    ok: 8pt / 8A93A0 / Arial preserved; field replaced by a literal run")

    print("[2] a caller-supplied size still wins over the inherited formatting")
    _prs2, _s2, _tb2, para2 = _para_with_field()
    run2 = write_literal_run_preserving_field(para2, 3)
    from pptx.util import Pt
    run2.font.size = Pt(28)
    assert run2._r.find(qn("a:rPr")).get("sz") == "2800", "explicit override must win"
    print("    ok: explicit font_pt override still applies")

    print("[3] compile-time re-stamp does not strip the formatting")
    # _restamp_page_number's field-only branch must use the preserving writer.
    import inspect
    import compile_picks
    src = inspect.getsource(compile_picks._restamp_page_number)
    assert "write_literal_run_preserving_field" in src, (
        "_restamp_page_number no longer uses the format-preserving writer; a "
        "field-only placeholder would fall through to tf.text and lose its rPr, "
        "re-creating the defect at compile time")
    assert "tf.text = str(position)" in src, "unexpected: the no-paragraph fallback vanished"
    print("    ok: compile re-stamp routes field-only placeholders through the writer")

    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
