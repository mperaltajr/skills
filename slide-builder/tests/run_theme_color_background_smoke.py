#!/usr/bin/env python3
"""Smoke test: a layout whose background is a THEME color is classified by it.

Registration's dark-background check only read plain hex colors (srgbClr).
One client template's four near-black layouts set their background as schemeClr tx1, so
the check saw nothing, fell back to the light master and called all four
dark_on_light, while chrome.yml recorded their background_hex as 0A0011
(2026-10-14).

On a freshly built copy of Slide Lab's own test template:
  1. a layout background of schemeClr tx1 (dark text color) -> light_on_dark
  2. a layout background of schemeClr bg1 (light) -> dark_on_light
  3. a theme background style (bgRef) tinted tx1 -> light_on_dark
  4. a plain dark hex layout background still -> light_on_dark
  5. a layout that sets no background follows a theme-color master (tx1)

Run:  py -3 slide-builder/tests/run_theme_color_background_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(HERE))

from lxml import etree  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402

import register_template as RT  # noqa: E402
import run_layout_inheritance_smoke as fixture  # noqa: E402


def _set_bg(element, *, scheme: str | None = None, srgb: str | None = None,
            ref_idx: int | None = None) -> None:
    """Replace element's <p:bg> with a solid fill (or a bgRef) of one color."""
    csld = element.find(qn("p:cSld"))
    old = csld.find(qn("p:bg"))
    if old is not None:
        csld.remove(old)
    bg = etree.Element(qn("p:bg"))
    if ref_idx is not None:
        holder = etree.SubElement(bg, qn("p:bgRef"), idx=str(ref_idx))
    else:
        pr = etree.SubElement(bg, qn("p:bgPr"))
        holder = etree.SubElement(pr, qn("a:solidFill"))
    if scheme:
        etree.SubElement(holder, qn("a:schemeClr"), val=scheme)
    else:
        etree.SubElement(holder, qn("a:srgbClr"), val=srgb)
    if ref_idx is None:
        etree.SubElement(pr, qn("a:effectLst"))
    csld.insert(0, bg)


def _clear_bg(element) -> None:
    csld = element.find(qn("p:cSld"))
    old = csld.find(qn("p:bg"))
    if old is not None:
        csld.remove(old)


def main() -> None:
    tpl = Path(tempfile.mkdtemp()) / "layout_diverse_template.pptx"
    fixture.build_fixture(tpl)
    prs = Presentation(str(tpl))
    master = prs.slide_masters[0]
    layouts = list(master.slide_layouts)
    assert len(layouts) >= 2, "fixture needs two layouts"
    lay = layouts[0]
    # A light master, as that client template's is, so a missed layout color falls to light.
    _set_bg(master.element, srgb="FFFFFF")

    _set_bg(lay.element, scheme="tx1")
    assert RT._detect_text_role_for_layout(lay) == ("light_on_dark", "dark"), \
        "schemeClr tx1 layout background must be dark"
    print("  ok: schemeClr tx1 layout background -> light_on_dark")

    _set_bg(lay.element, scheme="bg1")
    assert RT._detect_text_role_for_layout(lay) == ("dark_on_light", "light")
    print("  ok: schemeClr bg1 layout background -> dark_on_light")

    _set_bg(lay.element, scheme="tx1", ref_idx=1001)
    assert RT._detect_text_role_for_layout(lay) == ("light_on_dark", "dark")
    print("  ok: bgRef 1001 tinted tx1 -> light_on_dark")

    _set_bg(lay.element, srgb="0A0011")
    assert RT._detect_text_role_for_layout(lay) == ("light_on_dark", "dark")
    print("  ok: plain hex 0A0011 still -> light_on_dark")

    _clear_bg(lay.element)
    _set_bg(master.element, scheme="tx1")
    assert RT._detect_text_role_for_layout(lay) == ("light_on_dark", "dark"), \
        "a layout with no background must follow a theme-color master"
    print("  ok: no layout background, master schemeClr tx1 -> light_on_dark")

    print("SMOKE PASSED.")


if __name__ == "__main__":
    main()
