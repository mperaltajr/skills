#!/usr/bin/env python3
"""arrow_ends.py — does any arrowhead run into a box?

On cycle and flow diagrams the arrows came out ending inside the boxes they
point at, and only the final visual check caught it (2026-10-06). The defect
started in the design sketch, so the converter copying the sketch faithfully
kept it. This is the deterministic check: every arrowhead must stop at least
GAP_PX clear of any box. A box that holds the whole arrow (a panel behind the
diagram) does not count.

Two callers, one rule:
  * translate_html.py checks the DESIGN (SVG lines and paths with arrow
    markers against the design's boxes) and records any hit as a warning in
    the translation report, which the review page shows;
  * the translator agent's self-check runs this on the DRAWN slide
    (scripts/selfcheck_render.py), since arrows are drawn by the agent:
    connectors and freeforms whose line has a head or tail arrow.

Run:
  py -3 scripts/arrow_ends.py <slide.pptx> [--slide N] [--gap 6]
      [--report option_X_translation_report.json]
Exit 0 = no arrowhead at a box, 1 = at least one (listed), 2 = bad input.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

EMU_PER_PX = 9525
GAP_PX = 6.0                 # an arrowhead closer than this to a box touches it
CODE = "MAJOR_ARROW_END_AT_BOX"
_BACKDROP_SHARE = 0.6        # a box this big a share of the slide is a backdrop


# ---------------------------------------------------------------------------
# Geometry (shared with translate_html.py)
# ---------------------------------------------------------------------------

def gap_to_box(px: float, py: float, box: tuple) -> float:
    """Distance from a point to a box (x, y, w, h); negative = inside (how deep)."""
    x, y, w, h = box
    dx = max(x - px, 0.0, px - (x + w))
    dy = max(y - py, 0.0, py - (y + h))
    if dx == 0.0 and dy == 0.0:
        return -min(px - x, x + w - px, py - y, y + h - py)
    return math.hypot(dx, dy)


def _holds(box: tuple, pts) -> bool:
    x, y, w, h = box
    return all(x - 1 <= px <= x + w + 1 and y - 1 <= py <= y + h + 1 for px, py in pts)


def find_hits(arrows: list[dict], boxes: list[dict], gap_px: float = GAP_PX,
              canvas=(1280, 720)) -> list[dict]:
    """arrows: {'name', 'points': [(x, y), ...], 'heads': [(x, y, 'start'|'end'), ...]}
    boxes: {'name', 'box': (x, y, w, h)}. Returns one finding per arrowhead that
    is inside a box or within gap_px of one (the nearest such box)."""
    area = canvas[0] * canvas[1]
    hits = []
    for a in arrows:
        pts = a.get("points") or [(hx, hy) for hx, hy, _ in a["heads"]]
        for hx, hy, which in a["heads"]:
            best = None
            for b in boxes:
                bx = b["box"]
                if bx[2] <= 0 or bx[3] <= 0 or bx[2] * bx[3] > _BACKDROP_SHARE * area:
                    continue
                if _holds(bx, pts):
                    continue          # a panel behind the whole arrow
                d = gap_to_box(hx, hy, bx)
                if d < gap_px and (best is None or d < best[0]):
                    best = (d, b)
            if best is not None:
                d, b = best
                hits.append({"arrow": a.get("name") or "", "end": which,
                             "x": round(hx, 1), "y": round(hy, 1),
                             "box": b.get("name") or "", "gap_px": round(d, 1),
                             "inside": d < 0})
    return hits


def describe(hit: dict) -> str:
    where = (f"{abs(hit['gap_px']):.0f} px inside" if hit["inside"]
             else f"{hit['gap_px']:.0f} px from")
    return (f"arrow {hit['arrow'] or '(unnamed)'} ends {where} box "
            f"{hit['box'] or '(unnamed)'} at ({hit['x']:.0f}, {hit['y']:.0f}); "
            f"stop the arrowhead at least {GAP_PX + 2:.0f} px short of the box edge")


# ---------------------------------------------------------------------------
# Reading a drawn slide
# ---------------------------------------------------------------------------

def _q(tag: str) -> str:
    from pptx.oxml.ns import qn
    return qn(tag)


class _Xf:
    """Child-to-slide coordinate map of nested groups (EMU -> px)."""

    def __init__(self, parent=None, off=(0, 0), chOff=(0, 0), scale=(1.0, 1.0)):
        self.parent, self.off, self.chOff, self.scale = parent, off, chOff, scale

    def apply(self, x: float, y: float) -> tuple[float, float]:
        x = self.off[0] + (x - self.chOff[0]) * self.scale[0]
        y = self.off[1] + (y - self.chOff[1]) * self.scale[1]
        return self.parent.apply(x, y) if self.parent else (x, y)


def _xfrm(el):
    sppr = el.find(_q("p:spPr"))
    if sppr is None:
        sppr = el.find(_q("p:grpSpPr"))
    xf = sppr.find(_q("a:xfrm")) if sppr is not None else None
    if xf is None:
        return None
    off, ext = xf.find(_q("a:off")), xf.find(_q("a:ext"))
    if off is None or ext is None:
        return None
    return {"x": int(off.get("x")), "y": int(off.get("y")),
            "w": int(ext.get("cx")), "h": int(ext.get("cy")),
            "flipH": xf.get("flipH") in ("1", "true"), "flipV": xf.get("flipV") in ("1", "true"),
            "rot": int(xf.get("rot") or 0) / 60000.0, "el": xf}


def _place(g: dict, u: float, v: float) -> tuple[float, float]:
    """A point at (u, v) inside the shape's own box (EMU from its top-left),
    flipped and rotated as the shape is, in its parent's coordinates."""
    if g["flipH"]:
        u = g["w"] - u
    if g["flipV"]:
        v = g["h"] - v
    x, y = g["x"] + u, g["y"] + v
    if g["rot"]:
        cx, cy = g["x"] + g["w"] / 2, g["y"] + g["h"] / 2
        t = math.radians(g["rot"])
        x, y = (cx + (x - cx) * math.cos(t) - (y - cy) * math.sin(t),
                cy + (x - cx) * math.sin(t) + (y - cy) * math.cos(t))
    return x, y


def _line_el(el):
    sppr = el.find(_q("p:spPr"))
    return sppr.find(_q("a:ln")) if sppr is not None else None


def _heads(el) -> tuple[bool, bool]:
    ln = _line_el(el)
    if ln is None:
        return False, False
    def on(tag):
        e = ln.find(_q(tag))
        return e is not None and (e.get("type") or "none") != "none"
    return on("a:headEnd"), on("a:tailEnd")


def _visible(el, kind: str) -> bool:
    """Has a visible fill ('fill') or outline ('line'), own or from its style."""
    sppr = el.find(_q("p:spPr"))
    if kind == "fill":
        if el.tag == _q("p:pic"):
            return True
        for t in ("a:solidFill", "a:gradFill", "a:pattFill", "a:blipFill"):
            if sppr is not None and sppr.find(_q(t)) is not None:
                return True
        if sppr is not None and sppr.find(_q("a:noFill")) is not None:
            return False
        ref = el.find(_q("p:style") + "/" + _q("a:fillRef"))
    else:
        ln = sppr.find(_q("a:ln")) if sppr is not None else None
        if ln is not None:
            if ln.find(_q("a:noFill")) is not None:
                return False
            if ln.find(_q("a:solidFill")) is not None or ln.find(_q("a:gradFill")) is not None:
                return True
        ref = el.find(_q("p:style") + "/" + _q("a:lnRef"))
    return ref is not None and (ref.get("idx") or "0") != "0"


def _path_ends(el, g: dict):
    """(start, end, all points) of an open custom-geometry path, in the shape's
    parent coordinates (EMU); None when the path is closed or unreadable."""
    cg = el.find(_q("p:spPr") + "/" + _q("a:custGeom"))
    if cg is None:
        return None
    pts, first, last, closed = [], None, None, False
    for path in cg.iter(_q("a:path")):
        pw = int(path.get("w") or 0) or g["w"] or 1
        ph = int(path.get("h") or 0) or g["h"] or 1
        sx, sy = (g["w"] / pw if pw else 1.0), (g["h"] / ph if ph else 1.0)
        for cmd in path:
            if not isinstance(cmd.tag, str):
                continue
            name = cmd.tag.split("}")[-1]
            if name == "close":
                closed = True
                continue
            for pt in cmd.iter(_q("a:pt")):
                p = _place(g, int(pt.get("x")) * sx, int(pt.get("y")) * sy)
                pts.append(p)
                if first is None:
                    first = p
                last = p
    if closed or first is None or last is None:
        return None
    return first, last, pts


def read_slide(slide) -> tuple[list[dict], list[dict]]:
    """(arrows, boxes) of one python-pptx slide, in px."""
    arrows, boxes = [], []

    def walk(container, xf: _Xf):
        for el in container:
            if not isinstance(el.tag, str):
                continue
            tag = el.tag.split("}")[-1]
            if tag == "grpSp":
                g = _xfrm(el)
                if g is None:
                    walk(el, xf)
                    continue
                ch = g["el"]
                choff, chext = ch.find(_q("a:chOff")), ch.find(_q("a:chExt"))
                co = (int(choff.get("x")), int(choff.get("y"))) if choff is not None else (g["x"], g["y"])
                ce = (int(chext.get("cx")), int(chext.get("cy"))) if chext is not None else (g["w"], g["h"])
                walk(el, _Xf(xf, (g["x"], g["y"]), co,
                             (g["w"] / ce[0] if ce[0] else 1.0, g["h"] / ce[1] if ce[1] else 1.0)))
                continue
            if tag not in ("sp", "cxnSp", "pic"):
                continue
            g = _xfrm(el)
            if g is None:
                continue
            nv = el.find(".//" + _q("p:cNvPr"))
            name = nv.get("name") if nv is not None else ""
            head, tail = _heads(el)
            prst = el.find(_q("p:spPr") + "/" + _q("a:prstGeom"))
            prst = prst.get("prst") if prst is not None else None
            is_line = tag == "cxnSp" or (prst or "").startswith(
                ("line", "straightConnector", "bentConnector", "curvedConnector"))
            ends = None
            if is_line:
                a, b = _place(g, 0, 0), _place(g, g["w"], g["h"])
                ends = (a, b, [a, b])
            elif head or tail:
                ends = _path_ends(el, g)
            if ends is not None:
                if head or tail:
                    s, e, pts = ends
                    to_px = lambda p: tuple(c / EMU_PER_PX for c in xf.apply(*p))  # noqa: E731
                    heads = ([(*to_px(s), "start")] if head else []) + \
                            ([(*to_px(e), "end")] if tail else [])
                    arrows.append({"name": name, "heads": heads,
                                   "points": [to_px(p) for p in pts]})
                continue
            if _visible(el, "fill") or _visible(el, "line"):
                corners = [xf.apply(*_place(g, u, v)) for u, v in
                           ((0, 0), (g["w"], 0), (0, g["h"]), (g["w"], g["h"]))]
                xs = [c[0] / EMU_PER_PX for c in corners]
                ys = [c[1] / EMU_PER_PX for c in corners]
                boxes.append({"name": name, "box": (min(xs), min(ys),
                                                    max(xs) - min(xs), max(ys) - min(ys))})

    walk(slide.shapes._spTree, _Xf())
    return arrows, boxes


def check_pptx(pptx: Path, slide_no: int = 1, gap_px: float = GAP_PX) -> list[dict]:
    from pptx import Presentation
    prs = Presentation(str(pptx))
    slide = prs.slides[slide_no - 1]
    arrows, boxes = read_slide(slide)
    canvas = (int(prs.slide_width) / EMU_PER_PX, int(prs.slide_height) / EMU_PER_PX)
    return find_hits(arrows, boxes, gap_px, canvas)


def merge_into_report(report: Path, hits: list[dict], source: str = "drawn") -> None:
    """Replace this source's arrow warnings in a translation report with `hits`."""
    try:
        rep = json.loads(report.read_text(encoding="utf-8"))
    except Exception:
        rep = {}
    warns = [w for w in rep.get("warnings", []) or []
             if not (isinstance(w, dict) and w.get("code") == CODE and w.get("source") == source)]
    warns += [{"code": CODE, "source": source, "detail": f"{source}: " + describe(h)}
              for h in hits]
    rep["warnings"] = warns
    report.write_text(json.dumps(rep, indent=1), encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Flag arrowheads that run into a box.")
    ap.add_argument("pptx", type=Path)
    ap.add_argument("--slide", type=int, default=1)
    ap.add_argument("--gap", type=float, default=GAP_PX)
    ap.add_argument("--report", type=Path, help="Record the findings in this translation report.")
    args = ap.parse_args(argv)
    if not args.pptx.exists():
        print(f"ERROR: {args.pptx} not found")
        return 2
    hits = check_pptx(args.pptx, args.slide, args.gap)
    if args.report:
        merge_into_report(args.report, hits)
    if not hits:
        print(f"[ok] arrow ends: no arrowhead within {args.gap:.0f} px of a box")
        return 0
    print(f"ARROW ENDS: {len(hits)} arrowhead(s) at a box:")
    for h in hits:
        print("  - " + describe(h))
    return 1


if __name__ == "__main__":
    sys.exit(main())
