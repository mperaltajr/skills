#!/usr/bin/env python3
"""icon_svg.py — SVG previews of the icon library, and the one place that knows them.

The icon library (`slide-builder/icons/<name>.xml`) is DrawingML: the exact
shapes `icon_helper.insert_icon()` puts on a slide. A browser cannot draw
DrawingML, so a sketch that asked for `<i data-icon-name="gear">` showed a
blank gap on the review page, and the translator dropped the icon from the
finished slide without a word (2026-10-08).

This module converts each icon's XML into a small SVG once (`--build`), and
the SVGs ship in `icons/svg/`. The conversion reads the same geometry the
slide gets (custom paths, rectangles, ellipses, nested groups, flips), so the
preview is the picture that lands in the deck. Every filled shape is drawn in
`currentColor`, so the designer's CSS color carries through, as the icon is
tinted with one color on the slide too.

It also owns the names designers may use:
  icons/checked-icons.json   the short list of names whose pictures were
                             checked by eye to match the name. About half of
                             the library's names do not match their pictures
                             (the names were assigned by position in the
                             source deck), so designers pick from this list.

Used by:
  render_html.py     draws icons into the sketch before the screenshot
  translate_html.py  draws them the same way before reading the page, and
                     emits an `icon` step per icon (inserted as the vector
                     icon by twins/html_emit.py through icon_helper)

Run:
  py -3 scripts/icon_svg.py --build            (re)write icons/svg/*.svg
  py -3 scripts/icon_svg.py --sheet out.html   a picture sheet of every icon
  py -3 scripts/icon_svg.py --sheet out.html --names gear,globe
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ICONS = HERE.parent / "icons"
SVG_DIR = ICONS / "svg"
CHECKED_JSON = ICONS / "checked-icons.json"

_A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
_P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
_SCALE = 1000          # the longer side of every preview's viewBox
_KAPPA = 0.5522847498  # cubic Bezier circle constant


# ---------------------------------------------------------------------------
# DrawingML -> SVG
# ---------------------------------------------------------------------------

def _mul(m, n):
    """Compose affine maps (a, b, c, d, e, f): x' = a x + c y + e, y' = b x + d y + f.
    Returns m after n (apply n first)."""
    a, b, c, d, e, f = m
    A, B, C, D, E, F = n
    return (a * A + c * B, b * A + d * B, a * C + c * D, b * C + d * D,
            a * E + c * F + e, b * E + d * F + f)


def _ap(m, x, y):
    a, b, c, d, e, f = m
    return a * x + c * y + e, b * x + d * y + f


def _box(xfrm):
    off, ext = xfrm.find(_A + "off"), xfrm.find(_A + "ext")
    x = float(off.get("x", 0)) if off is not None else 0.0
    y = float(off.get("y", 0)) if off is not None else 0.0
    w = float(ext.get("cx", 0)) if ext is not None else 0.0
    h = float(ext.get("cy", 0)) if ext is not None else 0.0
    return x, y, w, h


def _place(xfrm, src):
    """The map from a shape's own space `src` (x, y, w, h) onto its xfrm box,
    with the xfrm's flips and rotation (about the box center)."""
    x, y, w, h = _box(xfrm)
    sx0, sy0, sw, sh = src
    m = (w / sw if sw else 1.0, 0.0, 0.0, h / sh if sh else 1.0, 0.0, 0.0)
    m = _mul(m, (1, 0, 0, 1, -sx0, -sy0))
    m = _mul((1, 0, 0, 1, x, y), m)
    cx, cy = x + w / 2, y + h / 2
    if xfrm.get("flipH") == "1":
        m = _mul((-1, 0, 0, 1, 2 * cx, 0), m)
    if xfrm.get("flipV") == "1":
        m = _mul((1, 0, 0, -1, 0, 2 * cy), m)
    rot = float(xfrm.get("rot", 0)) / 60000.0
    if rot:
        r = math.radians(rot)
        cs, sn = math.cos(r), math.sin(r)
        m = _mul((cs, sn, -sn, cs, cx - cs * cx + sn * cy, cy - sn * cx - cs * cy), m)
    return m


def _fmt(v: float) -> str:
    r = round(v)
    return str(int(r))


def _path_d(m, cmds) -> str:
    out = []
    for op, pts in cmds:
        if op == "Z":
            out.append("Z")
            continue
        xy = []
        for (px, py) in pts:
            X, Y = _ap(m, px, py)
            xy.append(f"{_fmt(X)} {_fmt(Y)}")
        out.append(op + " ".join(xy))
    return "".join(out)


def _shape_cmds(sp):
    """(commands in the shape's own space, that space as (x, y, w, h)) or None
    when the shape draws nothing fillable."""
    sppr = sp.find(_P + "spPr")
    if sppr is None:
        return None
    if sppr.find(_A + "noFill") is not None:
        return None
    xfrm = sppr.find(_A + "xfrm")
    if xfrm is None:
        return None
    _x, _y, w, h = _box(xfrm)
    cust = sppr.find(_A + "custGeom")
    prst = sppr.find(_A + "prstGeom")
    paths = []
    if cust is not None:
        for path in cust.iter(_A + "path"):
            if path.get("fill") == "none":
                continue
            pw = float(path.get("w") or w or 1)
            ph = float(path.get("h") or h or 1)
            cmds = []
            for el in path:
                tag = el.tag.replace(_A, "")
                pts = [(float(pt.get("x")), float(pt.get("y"))) for pt in el.iter(_A + "pt")]
                if tag == "moveTo":
                    cmds.append(("M", pts))
                elif tag == "lnTo":
                    cmds.append(("L", pts))
                elif tag == "cubicBezTo":
                    cmds.append(("C", pts))
                elif tag == "quadBezTo":
                    cmds.append(("Q", pts))
                elif tag == "close":
                    cmds.append(("Z", []))
                # arcTo: not used by any icon in the library
            paths.append(((0.0, 0.0, pw, ph), cmds))
    elif prst is not None:
        kind = prst.get("prst")
        if kind == "rect":
            cmds = [("M", [(0, 0)]), ("L", [(w, 0)]), ("L", [(w, h)]), ("L", [(0, h)]), ("Z", [])]
        elif kind == "ellipse":
            rx, ry = w / 2, h / 2
            kx, ky = rx * _KAPPA, ry * _KAPPA
            cmds = [("M", [(w, ry)]),
                    ("C", [(w, ry + ky), (rx + kx, h), (rx, h)]),
                    ("C", [(rx - kx, h), (0, ry + ky), (0, ry)]),
                    ("C", [(0, ry - ky), (rx - kx, 0), (rx, 0)]),
                    ("C", [(rx + kx, 0), (w, ry - ky), (w, ry)]), ("Z", [])]
        else:
            return None
        paths.append(((0.0, 0.0, w, h), cmds))
    return xfrm, paths


def _walk(el, m, out):
    tag = el.tag.replace(_P, "")
    if tag == "grpSp":
        gp = el.find(_P + "grpSpPr")
        xfrm = gp.find(_A + "xfrm") if gp is not None else None
        if xfrm is None:
            return
        ch_off, ch_ext = xfrm.find(_A + "chOff"), xfrm.find(_A + "chExt")
        src = (float(ch_off.get("x", 0)) if ch_off is not None else 0.0,
               float(ch_off.get("y", 0)) if ch_off is not None else 0.0,
               float(ch_ext.get("cx", 0)) if ch_ext is not None else 0.0,
               float(ch_ext.get("cy", 0)) if ch_ext is not None else 0.0)
        gm = _mul(m, _place(xfrm, src))
        for ch in el:
            if ch.tag in (_P + "grpSp", _P + "sp"):
                _walk(ch, gm, out)
    elif tag == "sp":
        got = _shape_cmds(el)
        if not got:
            return
        xfrm, paths = got
        for src, cmds in paths:
            d = _path_d(_mul(m, _place(xfrm, src)), cmds)
            if d:
                out.append(d)


def xml_to_svg(xml_path: Path) -> str | None:
    """The SVG text for one icon file, or None when it cannot be previewed
    (a picture icon, or nothing fillable)."""
    from lxml import etree
    root = etree.parse(str(xml_path)).getroot()
    tag = root.tag.replace(_P, "")
    if tag == "grpSp":
        xfrm = root.find(_P + "grpSpPr").find(_A + "xfrm")
    elif tag == "sp":
        xfrm = root.find(_P + "spPr").find(_A + "xfrm")
    else:
        return None
    x, y, w, h = _box(xfrm)
    if w <= 0 or h <= 0:
        return None
    k = _SCALE / max(w, h)
    W, H = max(1, round(w * k)), max(1, round(h * k))
    m = (k, 0.0, 0.0, k, -x * k, -y * k)
    ds: list[str] = []
    _walk(root, m, ds)
    if not ds:
        return None
    body = "".join(f'<path d="{d}"/>' for d in ds)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'fill="currentColor" fill-rule="evenodd">{body}</svg>')


# ---------------------------------------------------------------------------
# Library access
# ---------------------------------------------------------------------------

_SVG_CACHE: dict[str, str | None] = {}
_CHECKED: dict | None = None


def library_names() -> list[str]:
    return sorted(p.stem for p in ICONS.glob("*.xml"))


def exists(name: str) -> bool:
    return bool(name) and (ICONS / f"{name}.xml").exists()


def svg_for(name: str) -> str | None:
    """The shipped preview SVG for a library icon, or None (unknown name, or
    an icon that has no preview)."""
    if name in _SVG_CACHE:
        return _SVG_CACHE[name]
    p = SVG_DIR / f"{name}.svg"
    val = p.read_text(encoding="utf-8") if (name and p.exists()) else None
    _SVG_CACHE[name] = val
    return val


def checked() -> dict:
    """{name: {"shows": ..., "use_for": ...}} for the eye-checked names."""
    global _CHECKED
    if _CHECKED is None:
        try:
            data = json.loads(CHECKED_JSON.read_text(encoding="utf-8"))
            _CHECKED = {d["name"]: d for d in data.get("icons", [])}
        except (OSError, ValueError, KeyError):
            _CHECKED = {}
    return _CHECKED


def status(name: str) -> str:
    """'checked' | 'unchecked' (in the library, picture not checked against
    its name) | 'no-preview' | 'unknown'."""
    if not exists(name):
        return "unknown"
    if svg_for(name) is None:
        return "no-preview"
    return "checked" if name in checked() else "unchecked"


def manifest(names) -> dict:
    """{name: svg text or None} for the names a page uses, for the browser."""
    return {n: svg_for(n) if exists(n) else None for n in sorted(set(names)) if n}


# ---------------------------------------------------------------------------
# Browser side: draw icons into a sketch (render_html and translate_html both
# run this, so the review picture and the translator's reading agree)
# ---------------------------------------------------------------------------

# Returns the names the page asks for. `<img src=".../icons/<name>.svg">` is
# the other spelling the design guide allows; it is turned into the same
# `<i data-icon-name>` element first, keeping its size, class and style.
ICON_NAMES_JS = r"""() => {
  for (const img of Array.from(document.querySelectorAll('img[src]'))) {
    const m = (img.getAttribute('src') || '').match(/(?:^|\/)icons\/([A-Za-z0-9_.\-]+?)\.(?:svg|png|xml)$/);
    if (!m) continue;
    const r = img.getBoundingClientRect();
    const i = document.createElement('i');
    for (const a of Array.from(img.attributes)) if (a.name !== 'src' && a.name !== 'alt') i.setAttribute(a.name, a.value);
    i.setAttribute('data-icon-name', m[1]);
    i.style.display = getComputedStyle(img).display === 'inline' ? 'inline-block' : getComputedStyle(img).display;
    if (r.width) i.style.width = r.width + 'px';
    if (r.height) i.style.height = r.height + 'px';
    img.replaceWith(i);
  }
  return Array.from(new Set(Array.from(document.querySelectorAll('[data-icon-name]'))
    .map(e => (e.getAttribute('data-icon-name') || '').trim())));
}"""

# Fills each `[data-icon-name]` element with its SVG, colored by
# `data-icon-color` when set, else the element's CSS color. An element with
# no size of its own gets 24 px (the design guide's anchor size). An unknown
# name gets a labeled dashed box, never a silent gap.
ICON_DRAW_JS = r"""(lib) => {
  const out = [];
  for (const el of Array.from(document.querySelectorAll('[data-icon-name]'))) {
    if (el.getAttribute('data-icon-drawn')) continue;
    const name = (el.getAttribute('data-icon-name') || '').trim();
    const cs = getComputedStyle(el);
    if (cs.display === 'inline') el.style.display = 'inline-block';
    let r = el.getBoundingClientRect();
    if (r.width < 1) el.style.width = (parseFloat(cs.height) > 0 ? cs.height : '24px');
    r = el.getBoundingClientRect();
    if (r.height < 1) el.style.height = r.width + 'px';
    if (el.getAttribute('data-icon-color')) el.style.color = el.getAttribute('data-icon-color');
    el.style.lineHeight = '0';
    el.style.flexShrink = '0';
    const svg = lib[name];
    if (svg) {
      el.innerHTML = svg;
      const s = el.firstElementChild;
      s.setAttribute('width', '100%'); s.setAttribute('height', '100%');
      s.setAttribute('preserveAspectRatio', 'xMidYMid meet');
      s.setAttribute('aria-hidden', 'true');
      s.style.display = 'block';
      el.setAttribute('data-icon-drawn', 'icon');
    } else {
      el.innerHTML = '';
      el.style.boxSizing = 'border-box';
      el.style.border = '1px dashed #999999';
      el.style.position = el.style.position || (cs.position === 'static' ? 'relative' : cs.position);
      el.style.overflow = 'hidden';
      const lab = document.createElement('span');
      lab.textContent = '[' + (name || '?') + ']';
      lab.style.cssText = 'position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);' +
        'font:8px Arial,sans-serif;color:#999999;text-align:center;line-height:1;word-break:break-all;';
      el.appendChild(lab);
      el.setAttribute('data-icon-drawn', 'placeholder');
    }
    out.push(name);
  }
  return out;
}"""


def draw_icons(page) -> list[dict]:
    """Draw every icon the loaded page asks for. Returns one warning per name
    that is not a checked library icon: {"code", "name", "detail"}."""
    names = page.evaluate(ICON_NAMES_JS) or []
    if not names:
        return []
    page.evaluate(ICON_DRAW_JS, manifest(names))
    return [w for w in (warning_for(n) for n in names) if w]


def warning_for(name: str) -> dict | None:
    st = status(name)
    if st == "checked":
        return None
    if st == "unknown":
        return {"code": "ICON_UNKNOWN", "name": name,
                "detail": f'icon "{name}" is not in the icon library; a labeled placeholder '
                          "is drawn instead. Use a name from icons/checked-icons.json."}
    if st == "no-preview":
        return {"code": "ICON_NO_PREVIEW", "name": name,
                "detail": f'icon "{name}" has no picture that can be drawn; a labeled '
                          "placeholder is drawn instead. Use a name from icons/checked-icons.json."}
    return {"code": "ICON_NOT_CHECKED", "name": name,
            "detail": f'icon "{name}" is in the library but not on the checked list, so its '
                      "picture may not match its name (about half the names do not). Look at "
                      "the sketch, or use a name from icons/checked-icons.json."}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_all() -> tuple[int, int, int]:
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    made = skipped = total = 0
    keep = set()
    for p in sorted(ICONS.glob("*.xml")):
        svg = xml_to_svg(p)
        if svg is None:
            skipped += 1
            continue
        out = SVG_DIR / f"{p.stem}.svg"
        out.write_text(svg, encoding="utf-8", newline="\n")
        keep.add(out.name)
        made += 1
        total += len(svg.encode("utf-8"))
    for old in SVG_DIR.glob("*.svg"):
        if old.name not in keep:
            old.unlink()
    return made, skipped, total


def sheet_html(names: list[str], cols: int = 10, color: str = "#1F3A93") -> str:
    cells = []
    for n in names:
        svg = svg_for(n) or ""
        st = status(n)
        mark = {"checked": "&#10003; ", "unchecked": "", "no-preview": "(no preview) ",
                "unknown": "(unknown) "}[st]
        cells.append(f'<div class="c"><i data-icon-name="{n}" style="color:{color}">{svg}</i>'
                     f'<div class="n">{mark}{n}</div></div>')
    return ("<!DOCTYPE html><html><head><meta charset='utf-8'><style>"
            "body{font:12px Arial,sans-serif;margin:16px}"
            f".g{{display:grid;grid-template-columns:repeat({cols},1fr);gap:12px}}"
            ".c{text-align:center}.c i{display:block;width:64px;height:64px;margin:0 auto}"
            ".c i svg{width:100%;height:100%}.n{margin-top:4px;word-break:break-all}"
            "</style></head><body><div class='g'>" + "".join(cells) + "</div></body></html>")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--build", action="store_true", help="(re)write icons/svg/*.svg")
    ap.add_argument("--sheet", type=Path, help="write a picture sheet (HTML) of the icons")
    ap.add_argument("--names", help="comma-separated names for --sheet (default: all; "
                                    "'checked' for the checked list)")
    args = ap.parse_args(argv)
    if args.build:
        made, skipped, total = build_all()
        print(f"[ok] wrote {made} previews to {SVG_DIR} ({total / 1e6:.1f} MB); "
              f"{skipped} icon(s) have no preview")
    if args.sheet:
        if args.names == "checked":
            names = sorted(checked())
        elif args.names:
            names = [n.strip() for n in args.names.split(",") if n.strip()]
        else:
            names = library_names()
        args.sheet.write_text(sheet_html(names), encoding="utf-8")
        print(f"[ok] sheet of {len(names)} icon(s): {args.sheet}")
    if not (args.build or args.sheet):
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
