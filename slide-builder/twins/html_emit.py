"""html_emit.py — draw a translation plan into a native, editable PowerPoint slide.

translate_html.py reads a worker's HTML design in the browser that drew it and
turns it into a plan: a list of shapes and text boxes, in paint order, with
every geometry and style decision already made. This module only draws that
plan. Keeping the drawing here (rather than in each generated script) means a
fix to how something is drawn applies to every slide on the next finalize.

Each op kind maps to plain python-pptx: rectangles, rounded rectangles, ovals,
triangles, freeform polygons and polylines, straight connectors, and text boxes
with styled runs. No charts, no embedded objects, no pictures of text.

The rules that used to live as prose in the translator agent's instructions are
code here, applied the same way every time:
  - no shadow is effectRef idx="0", never a deleted <p:style> child
  - letter spacing is the raw spc attribute at px x 75
  - line spacing is exact points from the computed line-height
  - font sizes snap to PowerPoint's grid
  - one-line text never wraps
"""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

from twins.helpers import set_letter_spacing, snap_font_pt

CANVAS_W, CANVAS_H = 1280, 720

_ALIGN = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER,
          "right": PP_ALIGN.RIGHT, "justify": PP_ALIGN.JUSTIFY}
_KIND = {"rect": MSO_SHAPE.RECTANGLE, "rounded": MSO_SHAPE.ROUNDED_RECTANGLE,
         "oval": MSO_SHAPE.OVAL, "triangle": MSO_SHAPE.ISOSCELES_TRIANGLE}
_DASH = {"dashed": MSO_LINE.DASH, "dotted": MSO_LINE.ROUND_DOT}


def E(px: float) -> Emu:
    return Emu(int(round(px * 9525)))


def _no_shadow(shape) -> None:
    """LibreOffice draws the theme's preset shadow on any autoshape; the designs
    are flat. effectRef idx="0" says "no effect" while keeping <p:style> whole:
    deleting the child instead is what made PowerPoint refuse a deck."""
    eff = shape._element.find(".//" + qn("a:effectRef"))
    if eff is not None:
        eff.set("idx", "0")


def _fill(shape, color, alpha: float = 1.0) -> None:
    if not color:
        shape.fill.background()
        return
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(color)
    if alpha < 0.999:
        srgb = shape._element.spPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
        srgb.append(srgb.makeelement(qn("a:alpha"), {"val": str(int(round(alpha * 100000)))}))


def _line(shape, line) -> None:
    if not line:
        shape.line.fill.background()
        return
    shape.line.color.rgb = RGBColor.from_string(line["color"])
    shape.line.width = E(line["w"])
    if line.get("dash") in _DASH:
        shape.line.dash_style = _DASH[line["dash"]]


def _shape(slide, op) -> None:
    sp = slide.shapes.add_shape(_KIND[op["kind"]], E(op["x"]), E(op["y"]),
                                E(max(op["w"], 0.5)), E(max(op["h"], 0.5)))
    if op["kind"] == "rounded" and op.get("radius_ratio") is not None:
        sp.adjustments[0] = op["radius_ratio"]
    if op.get("rotation"):
        sp.rotation = op["rotation"]
    _fill(sp, op.get("fill"), op.get("alpha", 1.0))
    _line(sp, op.get("line"))
    _no_shadow(sp)
    if op.get("name"):
        sp.name = op["name"]


def _freeform(slide, op) -> None:
    pts = op["points"]
    if len(pts) < 2:
        return
    builder = slide.shapes.build_freeform(E(pts[0][0]), E(pts[0][1]), scale=1.0)
    builder.add_line_segments([(E(x), E(y)) for x, y in pts[1:]], close=bool(op.get("closed")))
    sp = builder.convert_to_shape()
    _fill(sp, op.get("fill") if op.get("closed") else None, op.get("alpha", 1.0))
    _line(sp, op.get("line"))
    _no_shadow(sp)
    if op.get("name"):
        sp.name = op["name"]


def _connector(slide, op) -> None:
    (x1, y1), (x2, y2) = op["points"]
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1), E(y1), E(x2), E(y2))
    _line(c, op.get("line"))
    # Connectors carry the same theme style, shadow included.
    _no_shadow(c)
    if op.get("name"):
        c.name = op["name"]


def _text(slide, op) -> None:
    tb = slide.shapes.add_textbox(E(op["x"]), E(op["y"]), E(max(op["w"], 1)), E(max(op["h"], 1)))
    if op.get("name"):
        tb.name = op["name"]
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.auto_size = MSO_AUTO_SIZE.NONE
    # One-line text never wraps. PowerPoint and LibreOffice set a font slightly
    # wider than Chrome, so a box that fits in Chrome by a pixel would break a
    # short word mid-word ("Taa S"). Letting it overhang is the lesser error.
    tf.word_wrap = bool(op.get("wrap"))
    lh_pt = op["line_height_px"] * 0.75
    for i, para in enumerate(op["paragraphs"]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = _ALIGN.get(op.get("align", "left"), PP_ALIGN.LEFT)
        p.line_spacing = Pt(lh_pt)
        for r in para:
            if not r["t"]:
                continue
            run = p.add_run()
            run.text = r["t"]
            f = run.font
            if r.get("font"):
                f.name = r["font"]
            f.size = Pt(snap_font_pt(r["size_px"] * 0.75))
            f.bold = bool(r.get("bold"))
            f.italic = bool(r.get("italic"))
            if r.get("color"):
                f.color.rgb = RGBColor.from_string(r["color"])
            if r.get("letter_spacing_px"):
                set_letter_spacing(run, r["letter_spacing_px"])


_DRAW = {"shape": _shape, "freeform": _freeform, "connector": _connector, "text": _text}


def build(plan: dict):
    """Draw a plan onto a fresh 1280x720 slide. Returns (prs, slide)."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = E(CANVAS_W), E(CANVAS_H)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    for op in plan["ops"]:
        _DRAW[op["op"]](slide, op)
    return prs, slide


def build_and_save(plan: dict, out_path) -> None:
    prs, _ = build(plan)
    prs.save(str(Path(out_path)))
