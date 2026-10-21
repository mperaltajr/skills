#!/usr/bin/env python3
"""Smoke test: the section tag goes into the template's own slot, and is never
drawn in a highlight color too pale to read.

Owner's approval (2026-10-14): a client template's highlight is a pale
yellow #FFFB89, so the loose section tag above the title came out pale yellow on
white (1.08 to 1). The template has its own "Breadcrumb" text slot where the
tag goes. Now:

  1. names: _chrome_schema.is_section_tag_slot_name reads "Breadcrumb",
     "Section", "Section tag", "Tracker" (numbering suffix ignored) and
     nothing else
  2. contrast: _chrome_schema.contrast_ratio and chrome_rules.readable_tag_color
     keep a readable highlight and swap a pale one for the main text color
  3. registration: register_template._section_tag_slot_idx finds the slot
     only in the top band, above the title; LayoutChrome keeps the field
     through chrome.yml
  4. finalize's place_section_tag writes the tag into the slot (after the
     empty slot was removed, as finalize does), keeps the template's style,
     leaves one tag after a second run, none for "(none)", and white text on
     a dark version of a light layout
  5. without a slot: the loose tag uses the highlight when it reads, the text
     color when it does not
  6. the review sketch's chrome_style / chrome_css show the slot's own style

No renderer needed.
Run:  py -3 slide-builder/tests/run_section_tag_slot_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path
from types import SimpleNamespace

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))

from lxml import etree  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402

import _chrome_schema as CS  # noqa: E402
import register_template as RT  # noqa: E402
from twins import chrome_rules as CR  # noqa: E402
from twins.composer import remove_empty_placeholders  # noqa: E402

EMU = 9525
SLOT_IDX = 20   # the default deck already uses idx 10 for its date slot
SLOT_XML = (
    '<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
    '<p:nvSpPr><p:cNvPr id="{id}" name="{name}"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
    '<p:nvPr><p:ph type="body" idx="{idx}"/></p:nvPr></p:nvSpPr>'
    '<p:spPr><a:xfrm><a:off x="521208" y="{y}"/><a:ext cx="11155680" cy="190195"/></a:xfrm>'
    '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
    '<p:txBody><a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0" anchor="b"><a:noAutofit/></a:bodyPr>'
    '<a:lstStyle><a:lvl1pPr marL="0" indent="0"><a:buNone/>'
    '<a:defRPr sz="1000" b="1"><a:solidFill><a:srgbClr val="6F6F6F"/></a:solidFill></a:defRPr>'
    '</a:lvl1pPr></a:lstStyle><a:p><a:r><a:rPr lang="en-US"/><a:t>Section name</a:t></a:r></a:p>'
    '</p:txBody></p:sp>')


def _template(slot_y_px: int | None = 43, name: str = "Breadcrumb") -> Presentation:
    """python-pptx's default deck, widescreen, with a Breadcrumb slot on the
    'Title Only' layout and the title moved down to y=69 px (as on that client template)."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = 12192000, 6858000
    layout = prs.slide_layouts[5]
    title = next(ph for ph in layout.placeholders if ph.placeholder_format.type == 1)
    title.left, title.top, title.width, title.height = 521208, 69 * EMU, 11155680, 77 * EMU
    if slot_y_px is not None:
        tree = layout.shapes._spTree
        tree.append(etree.fromstring(SLOT_XML.format(
            id=40, name=name, idx=SLOT_IDX, y=slot_y_px * EMU)))
    return prs


def _lc(**kw):
    base = dict(name="Title Only", layout_class="body-canonical", text_role="dark_on_light",
                background="light", has_page_number=True, title_placeholder_idx=0,
                subtitle_placeholder_idx=None, section_tag_placeholder_idx=SLOT_IDX,
                background_hex="FFFFFF", title_font_pt=28)
    base.update(kw)
    return SimpleNamespace(**base)


def _tags(slide):
    return [sh for sh in slide.shapes if sh.name == CS.SECTION_TAG_NAME]


def _reload(prs):
    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return Presentation(buf)


def main() -> int:
    print("[1] slot names")
    for good in ("Breadcrumb", "Breadcrumb 3", "breadcrumb placeholder", "Section",
                 "Section tag", "Tracker 2", "Section name"):
        assert CS.is_section_tag_slot_name(good), good
    for bad in ("Subtitle", "Body", "Text Placeholder 2", "Section header text",
                "Source", "Title 1", "", None):
        assert not CS.is_section_tag_slot_name(bad), bad
    print("    ok")

    print("[2] contrast")
    r = CS.contrast_ratio("FFFB89", "FFFFFF")
    assert r is not None and r < 1.2, r
    assert round(CS.contrast_ratio("6F6F6F", "FFFFFF"), 2) == 5.02
    assert round(CS.contrast_ratio("000000", "FFFFFF"), 1) == 21.0
    assert CS.contrast_ratio("xyz", "FFFFFF") is None
    theme = {"colors": {"dk1": "1A1A1A", "lt1": "FFFFFF", "accent1": "2F5597"},
             "clrmap": {"tx1": "dk1", "bg1": "lt1"}}
    assert CR.readable_tag_color("#FFFB89", theme, "FFFFFF") == "1A1A1A"
    assert CR.readable_tag_color("1F4E79", theme, "FFFFFF") == "1F4E79"
    assert CR.readable_tag_color("", theme, None) == "2F5597"      # theme accent, readable
    # a page whose text color itself does not read: black or white, whichever reads
    assert CR.readable_tag_color("FFFB89", {"colors": {"dk1": "EEEEEE"},
                                            "clrmap": {"tx1": "dk1"}}, "FFFFFF") == "000000"
    print("    ok: pale highlight -> text color; readable highlight kept")

    print("[3] registration finds the slot only in the top band, above the title")
    prs = _template()
    assert RT._section_tag_slot_idx(prs.slide_layouts[5]) == SLOT_IDX
    assert RT._section_tag_slot_idx(prs.slide_layouts[1]) is None          # no slot
    assert RT._section_tag_slot_idx(_template(slot_y_px=600).slide_layouts[5]) is None
    assert RT._section_tag_slot_idx(_template(slot_y_px=100).slide_layouts[5]) is None  # under title top
    assert RT._section_tag_slot_idx(_template(name="Notes").slide_layouts[5]) is None
    assert RT._section_tag_slot_idx(_template(name="Tracker").slide_layouts[5]) == SLOT_IDX
    spec = CS.ChromeSpec(source_template_sha8="abcd1234", layouts={
        "Title Only": CS.LayoutChrome(name="Title Only", layout_class="body-canonical",
                                      text_role="dark_on_light", background="light",
                                      has_page_number=True, section_tag_placeholder_idx=SLOT_IDX)})
    again = CS.ChromeSpec.model_validate(spec.model_dump())
    assert again.layouts["Title Only"].section_tag_placeholder_idx == SLOT_IDX
    old = CS.LayoutChrome(name="x", layout_class="body-canonical", text_role="dark_on_light",
                          background="light", has_page_number=True)
    assert old.section_tag_placeholder_idx is None                         # older chrome.yml
    print("    ok")

    print("[4] finalize writes the tag into the slot, in the template's style")
    prs = _template()
    layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = "A title"
    remove_empty_placeholders(slide)                  # finalize removes the empty slot first
    assert not any(sh.is_placeholder and sh.placeholder_format.idx == SLOT_IDX
                   for sh in slide.shapes)
    assert CR.place_section_tag(slide, _lc(), "The market", accent_hex="#FFFB89")
    assert CR.place_section_tag(slide, _lc(), "The market", accent_hex="#FFFB89")  # second run
    tags = _tags(slide)
    assert len(tags) == 1, [sh.name for sh in slide.shapes]
    t = tags[0]
    assert t.is_placeholder and t.placeholder_format.idx == SLOT_IDX
    assert t.text_frame.text == "The market"
    rpr = t._element.find(".//" + qn("a:rPr"))
    assert rpr.find(qn("a:solidFill")) is None and rpr.get("sz") is None \
        and rpr.get("cap") is None, "slot text must inherit the template's style"
    assert t._element.find(qn("p:spPr")).find(qn("a:xfrm")) is None, "position is inherited"
    prs2 = _reload(prs)
    t2 = _tags(prs2.slides[0])[0]
    assert int(t2.top) == 43 * EMU and int(t2.left) == 521208, (t2.top, t2.left)
    assert len({sh.shape_id for sh in prs2.slides[0].shapes}) == len(prs2.slides[0].shapes)
    # "(none)" clears it
    assert not CR.place_section_tag(slide, _lc(), "(none)", accent_hex="#FFFB89")
    assert not _tags(slide)
    # a dark version of a light layout: white text in the slot
    assert CR.place_section_tag(slide, _lc(), "The market", accent_hex="#FFFB89", on_dark=True)
    fill = _tags(slide)[0]._element.find(".//" + qn("a:rPr") + "/" + qn("a:solidFill"))
    assert fill is not None and fill.find(qn("a:srgbClr")).get("val") == "FFFFFF"
    # covers and dividers still carry no tag
    assert not CR.place_section_tag(slide, _lc(), "The market", accent_hex="", page_type="divider")
    print("    ok: one tag, in the slot, inherits size / weight / color / place")

    print("[5] without a slot: the loose tag reads")
    for accent, want in (("#FFFB89", None), ("#1F4E79", "1F4E79")):
        prs = _template(slot_y_px=None)
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = "A title"
        assert CR.place_section_tag(slide, _lc(section_tag_placeholder_idx=None), "The market",
                                    accent_hex=accent)
        t = _tags(slide)[0]
        assert not t.is_placeholder
        val = t._element.find(".//" + qn("a:rPr") + "/" + qn("a:solidFill") + "/"
                              + qn("a:srgbClr")).get("val")
        if want is None:
            assert val != "FFFB89" and CS.contrast_ratio(val, "FFFFFF") >= 4.5, val
        else:
            assert val == want, val
    print("    ok: the pale yellow falls back to the text color, a dark blue is kept")

    print("[6] the review sketch shows the slot's own style")
    prs = _template()
    st = CR.chrome_style(_lc(), prs, "#FFFB89", section_tag="The market")
    g = st["section_tag"]
    assert g["from_slot"] and g["size_pt"] == 10 and g["bold"] and not g["small_caps"], g
    assert g["color"] == "6F6F6F" and abs(g["top"] - 43) < 1 and abs(g["left"] - 521208 / EMU) < 1, g
    css = CR.chrome_css(st)
    assert "font-variant: normal" in css and "#6F6F6F" in css
    assert "own section-tag slot" in CR.chrome_plain_words(st)
    st = CR.chrome_style(_lc(section_tag_placeholder_idx=None), _template(slot_y_px=None),
                         "#FFFB89", section_tag="The market")
    g = st["section_tag"]
    assert not g["from_slot"] and g["small_caps"] and g["color"] != "FFFB89", g
    print("    ok")

    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
