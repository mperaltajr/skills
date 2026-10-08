#!/usr/bin/env python3
"""translate_html.py — turn a picked HTML design into editable native PowerPoint.

This does the job the slide-builder-translator agent used to do for every
option, as a script. An audit of 228 real agent translations found the job is
almost entirely mechanical (read each element's position and style from the
browser, map it to a shape) and that the agents did it inconsistently: six
different letter-spacing factors, opposite baseline nudges, improvised XML
edits that made PowerPoint refuse a deck, and the same five corrections
rediscovered by eye every session. Here each rule is written down once.

What it reads: the design opened in the same headless Chromium that drew it,
so flex, grid and calc() are already resolved into boxes.
What it writes, next to the HTML, keeping the contract finalize already reads:
  option_X_native.py           runs the plan; finalize executes it unchanged
  option_X_native.plan.json    every shape and text box, decided
  option_X_translation_report.json   counts, warnings, fallbacks (fixed schema)

What it does NOT draw: anything it cannot translate faithfully (curved SVG
paths, rotated or skewed elements, images, vertical text). Those are listed
in the report as fallback elements and the script is marked FALLBACK_PENDING;
finalize refuses it until the slide-builder-translator agent has drawn just
those elements (see the agent's "Fallback mode").

Run:
  py -3 scripts/translate_html.py --out <out_dir> --slide 4 --letter B
  py -3 scripts/translate_html.py --html <file.html> --emit <dir>   (standalone)
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(HERE))

TRANSLATOR_VERSION = "script-1"
CANVAS_W, CANVAS_H = 1280, 720

# ---------------------------------------------------------------------------
# Browser side: read the laid-out page
# ---------------------------------------------------------------------------

EXTRACT_JS = r"""
(opts) => {
  const canvas = document.querySelector('.slide-canvas') || document.querySelector('.slide') || document.body;
  const cr = canvas.getBoundingClientRect();
  const ox = cr.x, oy = cr.y;
  const R = (r) => ({x: r.x - ox, y: r.y - oy, w: r.width, h: r.height});
  // Where Chrome drew each visible character: [left, top, right, bottom]. The
  // alarm compares these with where LibreOffice put the same characters.
  const glyphBoxes = (nodes) => {
    const out = [];
    const rg = document.createRange();
    for (const n of nodes) {
      const t = n.textContent;
      for (let i = 0; i < t.length; i++) {
        if (/\s/.test(t[i])) continue;
        const j = (t.codePointAt(i) > 0xffff) ? i + 2 : i + 1;
        rg.setStart(n, i); rg.setEnd(n, j);
        const q = rg.getBoundingClientRect();
        out.push([+(q.left - ox).toFixed(1), +(q.top - oy).toFixed(1), +(q.right - ox).toFixed(1), +(q.bottom - oy).toFixed(1)]);
        if (j === i + 2) i++;
      }
    }
    return out;
  };
  const transparent = (c) => !c || c === 'transparent' || /rgba\([^)]*,\s*0\)$/.test(c);
  const out = {boxes: [], texts: [], svgs: [], icons: [], fallbacks: [], fields: {}, notes: [],
    canvas: {w: cr.width, h: cr.height}};
  let order = 0;

  // 1. Materialize ::before / ::after as real spans, so they lay out and can be
  //    measured like any element (a DOM walk cannot see pseudo-elements; ~5% of
  //    designs draw bullets and accent bars with them).
  const style = document.createElement('style');
  style.textContent = '[data-pm-b]::before{content:none!important}[data-pm-a]::after{content:none!important}';
  document.head.appendChild(style);
  for (const el of Array.from(canvas.querySelectorAll('*'))) {
    if (el.closest('svg')) continue;
    for (const [p, attr, first] of [['::before', 'data-pm-b', true], ['::after', 'data-pm-a', false]]) {
      const ps = getComputedStyle(el, p);
      if (!ps || ps.content === 'none' || ps.content === 'normal' || ps.display === 'none') continue;
      const span = document.createElement('span');
      for (let i = 0; i < ps.length; i++) {
        const name = ps[i];
        if (name === 'content') continue;
        span.style.setProperty(name, ps.getPropertyValue(name));
      }
      let txt = ps.content;
      txt = /^["'].*["']$/.test(txt) ? txt.slice(1, -1) : '';
      span.textContent = txt.replace(/\\([0-9a-fA-F]{2,6})\s?/g, (m, h) => String.fromCodePoint(parseInt(h, 16)));
      span.setAttribute('data-pseudo', p);
      el.setAttribute(attr, '');
      if (first) el.insertBefore(span, el.firstChild); else el.appendChild(span);
    }
  }

  const visible = (cs) => cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0.01;
  const effOpacity = (el) => { let o = 1; for (let a = el; a && a !== document.documentElement; a = a.parentElement) o *= parseFloat(getComputedStyle(a).opacity || 1); return o; };
  const isRotated = (cs) => { const t = cs.transform; if (!t || t === 'none') return false; const m = t.match(/matrix\(([^)]+)\)/); if (!m) return true; const v = m[1].split(',').map(parseFloat); return Math.abs(v[1]) > 1e-3 || Math.abs(v[2]) > 1e-3; };
  const skip = new Set();
  const markSubtree = (el) => { skip.add(el); el.querySelectorAll('*').forEach(e => skip.add(e)); };

  // 2. Template fields: the graft owns title / footer / page number. The
  //    takeaway is drawn as a body shape named "subtitle" when the layout has no
  //    subtitle placeholder; otherwise it goes to the placeholder too.
  for (const el of canvas.querySelectorAll('[data-template-field]')) {
    const name = el.getAttribute('data-template-field');
    out.fields[name] = el.innerText.replace(/\s+/g, ' ').trim();
    if (!(name === 'subtitle' && opts.subtitleAsShape)) markSubtree(el);
  }

  const all = [canvas, ...canvas.querySelectorAll('*')];
  for (const el of all) {
    if (skip.has(el)) continue;
    const tag = el.tagName.toLowerCase();
    if (el.closest('svg') && tag !== 'svg') continue;
    const cs = getComputedStyle(el);
    if (!visible(cs)) { if (cs.display === 'none') markSubtree(el); continue; }
    const r = el.getBoundingClientRect();
    const sid = el.getAttribute('data-shape-id') || el.getAttribute('data-template-field') || '';

    // A library icon (drawn into the page by icon_svg.draw_icons): one icon
    // step, inserted as the real vector icon. It used to vanish silently.
    if (el.hasAttribute('data-icon-name')) {
      out.icons.push({name: (el.getAttribute('data-icon-name') || '').trim(), ...R(r), color: cs.color,
        drawn: el.getAttribute('data-icon-drawn') || '', id: sid, order: order++});
      markSubtree(el); continue;
    }

    if (isRotated(cs)) {
      out.fallbacks.push({kind: 'rotated', reason: 'rotated or skewed element', id: sid, ...R(r), order: order++});
      markSubtree(el); continue;
    }
    if (cs.writingMode && cs.writingMode !== 'horizontal-tb') {
      out.fallbacks.push({kind: 'vertical-text', reason: 'vertical writing mode', id: sid, ...R(r), order: order++});
      markSubtree(el); continue;
    }
    if (tag === 'img' || tag === 'canvas' || tag === 'video' || tag === 'iframe' || tag === 'picture') {
      out.fallbacks.push({kind: tag, reason: tag + ' element', id: sid, ...R(r), order: order++});
      markSubtree(el); continue;
    }
    if (tag === 'svg') {
      out.svgs.push(readSvg(el, sid));
      continue;
    }

    // Box
    const sides = ['Top','Right','Bottom','Left'].map(s => ({w: parseFloat(cs['border'+s+'Width']) || 0, c: cs['border'+s+'Color'], s: cs['border'+s+'Style']}));
    const liveSides = sides.filter(s => s.w > 0 && s.s !== 'none' && s.s !== 'hidden' && !transparent(s.c));
    const inline = cs.display === 'inline';
    const bgimg = cs.backgroundImage;
    if (bgimg && bgimg !== 'none' && /url\(/.test(bgimg)) {
      out.fallbacks.push({kind: 'background-image', reason: 'background image', id: sid, ...R(r), order: order++});
    }
    const hasBg = !transparent(cs.backgroundColor) || (bgimg && /gradient/.test(bgimg));
    if ((hasBg || liveSides.length) && r.width >= 0 && r.height >= 0 && el !== canvas || (el === canvas && hasBg)) {
      const rects = inline ? Array.from(el.getClientRects()) : [r];
      for (const q of rects) {
        out.boxes.push({...R(q), bg: cs.backgroundColor, bgimg, sides,
          radii: [cs.borderTopLeftRadius, cs.borderTopRightRadius, cs.borderBottomRightRadius, cs.borderBottomLeftRadius],
          opacity: effOpacity(el), shadow: cs.boxShadow !== 'none', filter: cs.filter !== 'none',
          id: sid, tag, canvas: el === canvas, order: order++});
      }
    }

    // Text block: an element that is not inline, plus its inline descendants.
    if (!inline) {
      const runs = [];
      const ownRects = [];
      const textNodes = [];
      const collect = (n) => {
        for (const c of n.childNodes) {
          if (c.nodeType === 3) {
            if (!c.textContent.length) continue;
            const pcs = getComputedStyle(c.parentElement);
            const rg = document.createRange(); rg.selectNodeContents(c);
            const rs = Array.from(rg.getClientRects()).filter(q => q.width > 0.3 && q.height > 0.3);
            rs.forEach(q => ownRects.push(q));
            textNodes.push(c);
            runs.push({t: c.textContent, color: pcs.color, fw: pcs.fontWeight, fi: pcs.fontStyle,
              fs: parseFloat(pcs.fontSize), ff: pcs.fontFamily, ls: pcs.letterSpacing, tt: pcs.textTransform,
              td: pcs.textDecorationLine, op: effOpacity(c.parentElement), ws: pcs.whiteSpace,
              first: rs.length ? {x: rs[0].left - ox, y: rs[0].top - oy, r: rs[0].right - ox, h: rs[0].height} : null,
              last: rs.length ? {x: rs[rs.length-1].left - ox, r: rs[rs.length-1].right - ox, y: rs[rs.length-1].top - oy, h: rs[rs.length-1].height} : null});
          } else if (c.nodeType === 1) {
            if (skip.has(c)) continue;
            const ccs = getComputedStyle(c);
            if (!visible(ccs)) continue;
            if (c.tagName.toLowerCase() === 'br') { runs.push({br: true}); continue; }
            if (ccs.display === 'inline') collect(c);
          }
        }
      };
      collect(el);
      const joined = runs.filter(x => !x.br).map(x => x.t).join('');
      if (joined.trim().length && ownRects.length) {
        let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
        const lineTops = [];
        for (const q of ownRects.slice().sort((a, b) => a.top - b.top)) {
          x0 = Math.min(x0, q.left); y0 = Math.min(y0, q.top); x1 = Math.max(x1, q.right); y1 = Math.max(y1, q.bottom);
          if (!lineTops.length || q.top - lineTops[lineTops.length - 1] > q.height * 0.5) lineTops.push(q.top);
        }
        const firstLineH = Math.max(...ownRects.filter(q => Math.abs(q.top - y0) < 2).map(q => q.height));
        const pl = parseFloat(cs.paddingLeft) + parseFloat(cs.borderLeftWidth), pr = parseFloat(cs.paddingRight) + parseFloat(cs.borderRightWidth);
        const pt = parseFloat(cs.paddingTop) + parseFloat(cs.borderTopWidth), pb = parseFloat(cs.paddingBottom) + parseFloat(cs.borderBottomWidth);
        // Hidden behind something painted later, or clipped away by an ancestor?
        // Only something that paints over the text counts: a transparent
        // container or the empty middle of an SVG ring on top does not hide
        // it. Every line has to be hidden, not just the middle point.
        const paints = (e) => {
          const tag = e.tagName.toLowerCase();
          if (tag === 'img' || tag === 'canvas' || tag === 'video') return true;
          if (e.closest('svg')) return tag !== 'svg' && tag !== 'g';
          const s = getComputedStyle(e);
          if (s.backgroundImage && s.backgroundImage !== 'none') return true;
          const m = s.backgroundColor.match(/rgba?\(([^)]+)\)/);
          if (!m) return false;
          const v = m[1].split(',').map(parseFloat);
          return (v.length < 4 || v[3] > 0.9) && effOpacity(e) > 0.9;
        };
        const hiddenAt = (px, py) => {
          for (const e of document.elementsFromPoint(px, py)) {
            if (e === el || el.contains(e) || e.contains(el)) return false;
            if (paints(e)) return true;
          }
          return false;
        };
        const samples = ownRects.filter(q => q.width > 0 && q.height > 0)
          .map(q => [q.left + q.width / 2, q.top + q.height / 2]);
        const covered = samples.length > 0 && samples.every(([px, py]) => hiddenAt(px, py));
        let clipped = false;
        for (let a = el.parentElement; a && a !== canvas.parentElement; a = a.parentElement) {
          const acs = getComputedStyle(a);
          if (acs.overflow === 'hidden' || acs.overflowX === 'hidden' || acs.overflowY === 'hidden') {
            const ar = a.getBoundingClientRect();
            if (x1 <= ar.left || x0 >= ar.right || y1 <= ar.top || y0 >= ar.bottom) { clipped = true; break; }
          }
        }
        out.texts.push({box: R(r), content: {x: r.x - ox + pl, y: r.y - oy + pt, w: r.width - pl - pr, h: r.height - pt - pb},
          ink: {x: x0 - ox, y: y0 - oy, w: x1 - x0, h: y1 - y0}, lines: lineTops.length, firstLineH,
          glyphs: glyphBoxes(textNodes),
          runs, align: cs.textAlign, lh: cs.lineHeight, fs: parseFloat(cs.fontSize), ws: cs.whiteSpace,
          display: cs.display, jc: cs.justifyContent, covered, clipped,
          listItem: cs.display === 'list-item' && cs.listStyleType !== 'none',
          id: sid, tf: el.getAttribute('data-template-field') || (el.closest('[data-template-field]') ? el.closest('[data-template-field]').getAttribute('data-template-field') : null),
          order: order++});
      }
    }
  }

  // SVG: map the primitives these designs use (line, polyline, polygon, rect,
  // circle, ellipse, text, straight-segment paths). Anything else, or anything
  // decorated in a way shapes cannot carry, sends the whole SVG to the agent.
  function readSvg(svg, sid) {
    const r = svg.getBoundingClientRect();
    const res = {id: sid, ...R(r), order: order++, items: [], unsupported: [], arrows: []};
    const pt = (el, x, y) => { const m = el.getScreenCTM(); const p = new DOMPoint(x, y).matrixTransform(m); return [p.x - ox, p.y - oy]; };
    for (const el of svg.querySelectorAll('*')) {
      const tag = el.tagName.toLowerCase();
      if (['defs','title','desc','g','style','tspan','lineargradient','radialgradient','stop','clippath','mask','marker','symbol'].includes(tag)) {
        if (['lineargradient','radialgradient','clippath','mask','marker','symbol'].includes(tag)) res.unsupported.push(tag);
        continue;
      }
      const cs = getComputedStyle(el);
      if (!visible(cs)) continue;
      const mEnd = !!el.getAttribute('marker-end') || cs.markerEnd !== 'none';
      const mStart = !!el.getAttribute('marker-start') || cs.markerStart !== 'none';
      if (mEnd || mStart) {
        // Where the arrow's ends are, for the arrow-end check (scripts/arrow_ends.py).
        // The element itself still goes to the agent.
        try {
          if (!el.closest('defs, marker, symbol') && typeof el.getTotalLength === 'function') {
            const L = el.getTotalLength(), pts = [];
            for (let k = 0; k <= 8; k++) { const q = el.getPointAtLength(L * k / 8); pts.push(pt(el, q.x, q.y)); }
            res.arrows.push({pts, start: mStart, end: mEnd, id: el.getAttribute('data-shape-id') || el.id || ''});
          }
        } catch (e) {}
        res.unsupported.push('arrow marker'); continue;
      }
      if (cs.strokeDasharray && cs.strokeDasharray !== 'none' && (tag === 'circle' || tag === 'ellipse')) { res.unsupported.push('dashed ring'); continue; }
      const st = {fill: cs.fill, fillOp: parseFloat(cs.fillOpacity) * parseFloat(cs.opacity), stroke: cs.stroke,
                  sw: parseFloat(cs.strokeWidth) || 0, dash: cs.strokeDasharray && cs.strokeDasharray !== 'none',
                  def: !!el.closest('defs, marker, symbol')};
      if (/url\(/.test(st.fill) || /url\(/.test(st.stroke)) { res.unsupported.push('gradient paint'); continue; }
      const A = (n) => parseFloat(el.getAttribute(n) || 0);
      if (tag === 'line') res.items.push({k: 'poly', closed: false, pts: [pt(el, A('x1'), A('y1')), pt(el, A('x2'), A('y2'))], ...st});
      else if (tag === 'polyline' || tag === 'polygon') {
        const nums = (el.getAttribute('points') || '').trim().split(/[\s,]+/).map(parseFloat);
        const pts = []; for (let i = 0; i + 1 < nums.length; i += 2) pts.push(pt(el, nums[i], nums[i+1]));
        res.items.push({k: 'poly', closed: tag === 'polygon', pts, ...st});
      } else if (tag === 'rect') {
        const x = A('x'), y = A('y'), w = A('width'), h = A('height');
        if (A('rx') > 0 || A('ry') > 0) { res.unsupported.push('rounded svg rect'); continue; }
        res.items.push({k: 'poly', closed: true, pts: [pt(el,x,y), pt(el,x+w,y), pt(el,x+w,y+h), pt(el,x,y+h)], ...st});
      } else if (tag === 'circle' || tag === 'ellipse') {
        const cx = A('cx'), cy = A('cy'), rx = tag === 'circle' ? A('r') : A('rx'), ry = tag === 'circle' ? A('r') : A('ry');
        const a = pt(el, cx - rx, cy - ry), b = pt(el, cx + rx, cy + ry);
        res.items.push({k: 'oval', x: Math.min(a[0], b[0]), y: Math.min(a[1], b[1]), w: Math.abs(b[0]-a[0]), h: Math.abs(b[1]-a[1]), ...st});
      } else if (tag === 'path') {
        const d = el.getAttribute('d') || '';
        if (/[CcQqSsTtAa]/.test(d)) { res.unsupported.push('curved path'); continue; }
        const toks = d.match(/[MmLlHhVvZz]|-?[\d.]+(?:e-?\d+)?/g) || [];
        let i = 0, cmd = 'M', x = 0, y = 0, sx = 0, sy = 0; const subs = []; let cur = null;
        const num = () => parseFloat(toks[i++]);
        while (i < toks.length) {
          if (/[A-Za-z]/.test(toks[i])) cmd = toks[i++];
          if (cmd === 'Z' || cmd === 'z') { if (cur) { cur.closed = true; } x = sx; y = sy; cmd = 'M'; continue; }
          if (cmd === 'M' || cmd === 'm') { const nx = num(), ny = num(); x = cmd === 'm' ? x + nx : nx; y = cmd === 'm' ? y + ny : ny; sx = x; sy = y; cur = {pts: [[x, y]], closed: false}; subs.push(cur); cmd = cmd === 'm' ? 'l' : 'L'; continue; }
          if (cmd === 'L' || cmd === 'l') { const nx = num(), ny = num(); x = cmd === 'l' ? x + nx : nx; y = cmd === 'l' ? y + ny : ny; }
          else if (cmd === 'H' || cmd === 'h') { const nx = num(); x = cmd === 'h' ? x + nx : nx; }
          else if (cmd === 'V' || cmd === 'v') { const ny = num(); y = cmd === 'v' ? y + ny : ny; }
          else { i++; continue; }
          if (cur) cur.pts.push([x, y]);
        }
        for (const s of subs) res.items.push({k: 'poly', closed: s.closed, pts: s.pts.map(p => pt(el, p[0], p[1])), ...st});
      } else if (tag === 'text') {
        const bb = el.getBoundingClientRect();
        res.items.push({k: 'text', t: el.textContent.replace(/\s+/g, ' ').trim(), x: bb.left - ox, y: bb.top - oy, w: bb.width, h: bb.height,
          fs: parseFloat(cs.fontSize), ff: cs.fontFamily, fw: cs.fontWeight, color: cs.fill, anchor: cs.textAnchor || el.getAttribute('text-anchor') || 'start'});
      } else res.unsupported.push(tag);
    }
    return res;
  }

  out.pseudo_count = canvas.querySelectorAll('[data-pseudo]').length;
  out.visible_text = canvas.innerText;
  return out;
}
"""

# ---------------------------------------------------------------------------
# Python side: decide what to draw
# ---------------------------------------------------------------------------

_RGB = re.compile(r"rgba?\(([^)]+)\)")


def parse_color(s):
    """CSS color -> (hex, alpha), or None for transparent/none."""
    if not s or s in ("transparent", "none", "currentcolor"):
        return None
    m = _RGB.match(s.strip())
    if m:
        parts = [p for p in re.split(r"[,\s/]+", m.group(1).strip()) if p]
        try:
            r, g, b = (int(round(float(p))) for p in parts[:3])
        except ValueError:
            return None
        a = float(parts[3]) if len(parts) > 3 else 1.0
        if a <= 0.001:
            return None
        return ("%02X%02X%02X" % (r, g, b), a)
    m = re.match(r"#([0-9a-fA-F]{6})$", s.strip())
    if m:
        return (m.group(1).upper(), 1.0)
    m = re.match(r"#([0-9a-fA-F]{3})$", s.strip())
    if m:
        return ("".join(c * 2 for c in m.group(1)).upper(), 1.0)
    return None


def _px(v, ref: float = 0.0) -> float:
    if v in (None, "", "normal", "auto"):
        return 0.0
    v = str(v).strip()
    if v.endswith("%"):
        return float(v[:-1]) / 100 * ref
    try:
        return float(v.replace("px", "").split()[0])
    except ValueError:
        return 0.0


def _gradient_mid(bgimg):
    cols = re.findall(r"rgba?\([^)]+\)|#[0-9a-fA-F]{3,6}\b", bgimg or "")
    return parse_color(cols[len(cols) // 2]) if cols else None


def _split_top(s: str) -> list[str]:
    """Split on commas that are not inside parentheses."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


_SIDES = {"to top": 0, "to right": 90, "to bottom": 180, "to left": 270,
          "to top right": 45, "to right top": 45, "to bottom right": 135, "to right bottom": 135,
          "to bottom left": 225, "to left bottom": 225, "to top left": 315, "to left top": 315}


def _linear_gradient(bgimg: str, w: float, h: float) -> dict | None:
    """A single CSS linear-gradient as {"angle": css degrees, "stops": [[0..1,
    hex, alpha], ...]}; None for anything else (radial, conic, repeating,
    several layers), which is flattened to one color instead."""
    layers = _split_top(bgimg or "")
    if len(layers) != 1:
        return None
    m = re.match(r"^linear-gradient\((.*)\)$", layers[0].strip(), re.S)
    if not m:
        return None
    parts = _split_top(m.group(1))
    angle = 180.0
    first = parts[0].strip().lower()
    if first.startswith("to "):
        if first not in _SIDES:
            return None
        angle = float(_SIDES[first])
        if " " in first[3:] and w > 0 and h > 0:
            # corner directions follow the box's own diagonal
            # (the gradient runs perpendicular to the other diagonal)
            a = math.degrees(math.atan2(h, w))
            angle = {45: a, 135: 180 - a, 225: 180 + a, 315: 360 - a}[_SIDES[first]] % 360
        parts = parts[1:]
    elif re.match(r"^-?[\d.]+(deg|turn|rad|grad)$", first):
        v, unit = re.match(r"^(-?[\d.]+)(\w+)$", first).groups()
        angle = float(v) * {"deg": 1, "turn": 360, "rad": 57.29578, "grad": 0.9}[unit]
        parts = parts[1:]
    stops = []
    length = abs(w * math.sin(math.radians(angle))) + abs(h * math.cos(math.radians(angle))) \
        if (w and h) else 0
    for p in parts:
        cm = re.match(r"^(rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}|[a-z]+)\s*(.*)$", p.strip())
        if not cm:
            return None
        col = parse_color(cm.group(1))
        if col is None:
            col = (None, 0.0)              # transparent: fades its neighbor's color
        pos = None
        rest = cm.group(2).strip().split()
        if rest:
            r = rest[0]
            if r.endswith("%"):
                pos = float(r[:-1]) / 100
            elif r.endswith("px") and length:
                pos = float(r[:-2]) / length
        stops.append([pos, col[0], col[1]])
    if len(stops) < 2:
        return None
    # missing positions: first 0, last 1, the rest spread evenly between known ones
    if stops[0][0] is None:
        stops[0][0] = 0.0
    if stops[-1][0] is None:
        stops[-1][0] = 1.0
    i = 0
    while i < len(stops):
        if stops[i][0] is None:
            j = i
            while stops[j][0] is None:
                j += 1
            a, b = stops[i - 1][0], stops[j][0]
            for k in range(i, j):
                stops[k][0] = a + (b - a) * (k - i + 1) / (j - i + 1)
            i = j
        i += 1
    for k, s_ in enumerate(stops):
        s_[0] = min(1.0, max(0.0, s_[0]))
        if s_[1] is None:
            near = [q for q in stops[k + 1:] + stops[:k][::-1] if q[1]]
            if not near:
                return None
            s_[1] = near[0][1]
    return {"angle": angle % 360, "stops": stops}


GENERIC_FAMILIES = {"sans-serif": "Arial", "serif": "Times New Roman", "monospace": "Consolas",
                    "system-ui": "Segoe UI", "-apple-system": "Segoe UI", "ui-sans-serif": "Arial"}


def _family(ff: str) -> str:
    """The font Chrome actually drew with: the first family in the stack that
    is installed. Naming an uninstalled first choice ("Helvetica Neue")
    made PowerPoint and LibreOffice substitute a different, wider font."""
    stack = [f.strip().strip('"\'') for f in (ff or "").split(",") if f.strip()]
    if not stack:
        return ""
    fams = _family_index()
    installed = {f for (f, _s) in fams} | {f"{f} {s}" for (f, s) in fams}
    for f in stack:
        if f.lower() in GENERIC_FAMILIES:
            return GENERIC_FAMILIES[f.lower()]
        if f.lower() in installed:
            return f
    return stack[0]


def _bold(fw) -> bool:
    try:
        return int(fw) >= 600
    except (TypeError, ValueError):
        return str(fw) in ("bold", "bolder")


class Plan:
    def __init__(self):
        self.ops: list[dict] = []
        self.warnings: list[dict] = []
        self.fallbacks: list[dict] = []
        self.kill = {"gradients_flattened": 0, "shadows_stripped": 0, "filters_dropped": 0,
                     "opacity_on_text_normalized": 0, "text_decorations_stripped": 0}
        self.counts = {"shapes": 0, "texts": 0, "svg_items": 0, "pseudo_elements": 0,
                       "boxes_grown_for_clearance": 0, "wrap_adjusted": 0,
                       "covered_text_skipped": 0, "triangles": 0,
                       "self_check_handed_over": 0}
        self.self_check = {"ran": False, "fired": []}
        # The template's own background on this slide's layout ('RRGGBB'),
        # when known (a build's slide); None when translating a loose file.
        self.template_bg: str | None = None
        # The design's canvas color when it was left to the template (not drawn).
        self.canvas_bg: str | None = None

    def warn(self, code, detail):
        self.warnings.append({"code": code, "detail": detail})


# --- boxes -----------------------------------------------------------------

# A canvas this close (RGB distance) to the template's background IS the
# template's background.
CANVAS_MATCH = 3.0
# A fill this close to what is behind it does not show (PALE_FILL_ON_BACKGROUND).
PALE_FILL_LIMIT = 10.0
PALE_FILL_MIN_AREA = 0.02 * 1280 * 720     # only panels, not dots and rules


def _color_distance(a: str, b: str) -> float:
    from _template_bg import color_distance
    return color_distance(a, b)


def _mix(fg: str, bg: str, alpha: float) -> str:
    f = [int(fg[i:i + 2], 16) for i in (0, 2, 4)]
    g = [int(bg[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(a * alpha + b * (1 - alpha)):02X}" for a, b in zip(f, g))


def _check_pale_fills(plan: "Plan") -> None:
    """Warn when a large fill nearly matches what is behind it: the slide's
    background (the template's, when known) or the panel it sits on. A pale
    panel designed and approved on white vanished on a gray-blue master
    (2026-10-06). Advisory: the review page shows it."""
    designed_bg = plan.canvas_bg or "FFFFFF"          # what the designer saw
    slide_bg = plan.template_bg or designed_bg        # what the deck will show
    filled = [o for o in plan.ops if o.get("op") == "shape" and o.get("fill")
              and o.get("_box") and o.get("_filled")]

    def _against(o, bg):
        x, y, w, h = o["_box"]
        under = bg
        for u in reversed([u for u in filled if u["_order"] < o["_order"]]):
            ux, uy, uw, uh = u["_box"]
            if ux - 1 <= x and uy - 1 <= y and x + w <= ux + uw + 1 and y + h <= uy + uh + 1:
                under = _mix(u["fill"], bg, float(u.get("alpha") or 1.0))
                break
        return _mix(o["fill"], under, float(o.get("alpha") or 1.0)), under

    for o in filled:
        x, y, w, h = o["_box"]
        if w * h < PALE_FILL_MIN_AREA:
            continue
        seen, under = _against(o, slide_bg)
        line = o.get("line") or {}
        if line.get("color") and line.get("w", 0) >= 0.5 and \
                _color_distance(line["color"], under) > PALE_FILL_LIMIT:
            continue          # an outline shows the panel's edge
        d = _color_distance(seen, under)
        # Exactly the color behind it, as designed, is deliberate (a white card
        # holding a one-sided accent bar, a mask): on 99 past designs that was
        # 89 of 94 hits. It is a defect only when the design showed it and the
        # deck's background swallows it, or when a tint nearly matches.
        d_design = _color_distance(*_against(o, designed_bg))
        if (1.0 <= d <= PALE_FILL_LIMIT) or (d < 1.0 and d_design >= 1.0):
            what = ("the template's background" if under == plan.template_bg
                    else "the slide's background" if under == slide_bg else "the panel behind it")
            plan.warn("PALE_FILL_ON_BACKGROUND",
                      f"{o.get('name') or 'a panel'} ({w:.0f}x{h:.0f} px) is #{seen}, "
                      f"{d:.0f} away from {what} (#{under}): it will barely show. Give it "
                      "a visibly different fill or an outline")


def _check_arrow_ends(plan: "Plan", data: dict) -> None:
    """The design's arrows (SVG lines and paths with arrow markers) must stop
    clear of every box (scripts/arrow_ends.py). On cycle diagrams the sketch's
    arrowheads touched the boxes and the converter copied that (2026-10-06)."""
    import arrow_ends as AE
    arrows = []
    for s in data.get("svgs") or []:
        for a in s.get("arrows") or []:
            pts = [tuple(p) for p in a.get("pts") or []]
            if len(pts) < 2:
                continue
            heads = ([(pts[0][0], pts[0][1], "start")] if a.get("start") else []) + \
                    ([(pts[-1][0], pts[-1][1], "end")] if a.get("end") else [])
            arrows.append({"name": a.get("id") or s.get("id") or "", "points": pts,
                           "heads": heads})
    if not arrows:
        return
    boxes = []
    for b in data.get("boxes") or []:
        if b.get("canvas"):
            continue
        live = any(sd["w"] > 0 and sd["s"] not in ("none", "hidden") and parse_color(sd["c"])
                   for sd in b.get("sides") or [])
        if parse_color(b.get("bg")) or live:
            boxes.append({"name": b.get("id") or b.get("tag") or "", "box": (b["x"], b["y"], b["w"], b["h"])})
    for s in data.get("svgs") or []:
        for it in s.get("items") or []:
            if it.get("def") or not (parse_color(it.get("fill")) or parse_color(it.get("stroke"))):
                continue
            if it["k"] == "oval":
                boxes.append({"name": s.get("id") or "svg shape",
                              "box": (it["x"], it["y"], it["w"], it["h"])})
            elif it["k"] == "poly" and it.get("closed") and len(it.get("pts") or []) >= 3:
                xs, ys = [p[0] for p in it["pts"]], [p[1] for p in it["pts"]]
                boxes.append({"name": s.get("id") or "svg shape",
                              "box": (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))})
    for h in AE.find_hits(arrows, boxes):
        plan.warnings.append({"code": AE.CODE, "source": "design",
                              "detail": "design: " + AE.describe(h)})


def _plan_box(plan: Plan, b: dict, order_key) -> None:
    x, y, w, h = b["x"], b["y"], b["w"], b["h"]
    if b.get("shadow"):
        plan.kill["shadows_stripped"] += 1
    if b.get("filter"):
        plan.kill["filters_dropped"] += 1
    sides = b["sides"]
    live = [s for s in sides if s["w"] > 0 and s["s"] not in ("none", "hidden") and parse_color(s["c"])]

    # CSS triangle: a zero-size box drawn entirely by borders, one side colored
    # and its two neighbors transparent. The point is opposite the colored side.
    zero_content = (abs(w - (sides[1]["w"] + sides[3]["w"])) < 1.0
                    and abs(h - (sides[0]["w"] + sides[2]["w"])) < 1.0)
    if zero_content and len(live) == 1 and parse_color(b.get("bg")) is None:
        side = sides.index(live[0])
        neighbors = [sides[(side + 1) % 4], sides[(side + 3) % 4]]
        if all(n["w"] > 0 for n in neighbors):
            col = parse_color(live[0]["c"])
            rot = {0: 180, 1: 270, 2: 0, 3: 90}[side]   # colored top -> points down
            sw, sh, sx, sy = w, h, x, y
            if rot in (90, 270):
                # The triangle shape points up; turned sideways its width and
                # height swap, so draw it swapped and keep the same center.
                sw, sh = h, w
                sx, sy = x + (w - sw) / 2, y + (h - sh) / 2
            plan.ops.append({"op": "shape", "kind": "triangle", "x": sx, "y": sy, "w": sw, "h": sh,
                             "rotation": rot, "fill": col[0], "alpha": col[1] * b["opacity"],
                             "name": b.get("id") or None, "_order": order_key})
            plan.counts["triangles"] += 1
            return

    if b.get("canvas"):
        col = parse_color(b["bg"])
        if not col or col[0] == "FFFFFF":
            plan.canvas_bg = "FFFFFF"
            return
        if plan.template_bg and _color_distance(col[0], plan.template_bg) <= CANVAS_MATCH:
            # The design is drawn on the template's own background, which the
            # slide already has. A full-slide rectangle in that color would only
            # cover the master's own artwork (2026-10-06).
            plan.canvas_bg = col[0]
            plan.counts["canvas_left_to_template"] = 1
            return
    col = parse_color(b["bg"])
    flattened = False
    gradient = None
    if b.get("bgimg") and "gradient" in b["bgimg"]:
        # A gradient paints over the background color. A single linear one
        # is drawn natively; radial, conic or layered ones become one color.
        gradient = _linear_gradient(b["bgimg"], w, h)
        col = _gradient_mid(b["bgimg"]) or col
        if gradient is None:
            plan.kill["gradients_flattened"] += 1
            flattened = True
    if w < 0.5 or h < 0.5:
        return
    uniform = len(live) == 4 and len({(round(s["w"], 1), s["c"], s["s"]) for s in live}) == 1
    radii = [_px(r, min(w, h)) for r in b["radii"]]
    rad = max(radii)
    if rad > 0.5 and len({round(r) for r in radii}) > 1:
        plan.warn("MIXED_CORNER_RADII", f"{b.get('id') or b['tag']}: drawn with one radius")
    if col or uniform:
        if rad >= min(w, h) / 2 - 0.5 and abs(w - h) < 1.0:
            kind, ratio = "oval", None
        elif rad > 0.5:
            kind, ratio = "rounded", min(0.5, rad / max(1.0, min(w, h)))
        else:
            kind, ratio = "rect", None
        line = None
        if uniform:
            lc = parse_color(live[0]["c"])
            line = {"color": lc[0], "w": live[0]["w"], "dash": live[0]["s"]}
        bw = live[0]["w"] if uniform else 0
        plan.ops.append({"op": "shape", "kind": kind, "radius_ratio": ratio,
                         "x": x + bw / 2, "y": y + bw / 2, "w": w - bw, "h": h - bw,
                         "fill": col[0] if col else None,
                         "alpha": (col[1] if col else 1.0) * b["opacity"],
                         "line": line, "name": b.get("id") or None, "_order": order_key,
                         "_box": (x, y, w, h), "_filled": bool(col), "_flattened": flattened})
        if gradient:
            plan.ops[-1]["gradient"] = gradient
        plan.counts["shapes"] += 1
    if live and not uniform:
        # One-sided borders: python-pptx outlines are all-or-nothing, so each
        # bordered side is its own thin bar at that edge.
        for i, s in enumerate(sides):
            c = parse_color(s["c"]) if s["w"] > 0 and s["s"] not in ("none", "hidden") else None
            if not c:
                continue
            bw = s["w"]
            geo = [(x, y, w, bw), (x + w - bw, y, bw, h), (x, y + h - bw, w, bw), (x, y, bw, h)][i]
            plan.ops.append({"op": "shape", "kind": "rect", "x": geo[0], "y": geo[1], "w": geo[2],
                             "h": geo[3], "fill": c[0], "alpha": c[1] * b["opacity"],
                             "line": None, "_order": order_key + 0.001 * (i + 1)})
            plan.counts["shapes"] += 1
            if s["s"] in ("dashed", "dotted"):
                plan.warn("DASHED_EDGE_AS_SOLID", f"{b.get('id') or b['tag']}: one-sided {s['s']} border drawn solid")


# --- text ------------------------------------------------------------------

_FONT_CACHE: dict = {}
_FAMILIES: dict | None = None


def _family_index() -> dict:
    """{(family, style): path} from the fonts' own name tables, cached on disk.

    The shared font index is keyed by FILE name (arial.ttf), so looking up the
    CSS family ("Arial") found nothing, and the wrap check silently did nothing.
    """
    global _FAMILIES
    if _FAMILIES is not None:
        return _FAMILIES
    import tempfile
    cache = Path(tempfile.gettempdir()) / "slidelab_font_families.json"
    try:
        _FAMILIES = {tuple(k.split("|", 1)): v for k, v in
                     json.loads(cache.read_text(encoding="utf-8")).items()}
        return _FAMILIES
    except Exception:
        pass
    _FAMILIES = {}
    try:
        from PIL import ImageFont
        from _chrome_schema import _font_index
        for path in set(_font_index().values()):
            try:
                fam, sty = ImageFont.truetype(path, 10).getname()
            except Exception:
                continue
            _FAMILIES.setdefault(((fam or "").lower(), (sty or "").lower()), path)
        cache.write_text(json.dumps({f"{k[0]}|{k[1]}": v for k, v in _FAMILIES.items()}),
                         encoding="utf-8")
    except Exception:
        pass
    return _FAMILIES


_FACES = None


def _face_table() -> dict:
    """{family (lowercase): [face, ...]} for every installed font, cached on disk.

    A face: path, weight, width, italic, and its PowerPoint name: the legacy
    family (name id 1) plus whether that is the family's Bold style (id 2).
    Chrome groups faces by the typographic family (id 16, else id 1) and picks
    by weight; PowerPoint knows each face by its legacy family + bold on/off
    ("Brand Sans Medium", or "Brand Sans" + bold for the Bold face).
    """
    global _FACES
    if _FACES is not None:
        return _FACES
    import tempfile
    cache = Path(tempfile.gettempdir()) / "slidelab_font_faces.json"
    try:
        _FACES = json.loads(cache.read_text(encoding="utf-8"))
        return _FACES
    except Exception:
        pass
    _FACES = {}
    try:
        from fontTools.ttLib import TTFont
        from _chrome_schema import _font_index
        for path in sorted(set(_font_index().values())):
            try:
                f = TTFont(path, lazy=True, fontNumber=0)
                n = f["name"]
                fam1, sty2 = n.getDebugName(1) or "", n.getDebugName(2) or ""
                typo = n.getDebugName(16) or fam1
                os2 = f["OS/2"]
                face = {"path": path, "weight": int(os2.usWeightClass), "width": int(os2.usWidthClass),
                        "italic": bool(os2.fsSelection & 1) or "italic" in sty2.lower(),
                        "ppt_name": fam1, "ppt_bold": "bold" in sty2.lower()}
            except Exception:
                continue
            for key in {typo.lower(), fam1.lower()}:
                _FACES.setdefault(key, []).append(face)
        cache.write_text(json.dumps(_FACES), encoding="utf-8")
    except Exception:
        pass
    return _FACES


def _pick_weight(faces: list[dict], w: int) -> dict:
    """CSS font matching by weight: 400-500 look up to 500 then down; above
    500 look up then down; below 400 look down then up."""
    ws = sorted({f["weight"] for f in faces})
    if w in ws:
        best = w
    elif 400 <= w <= 500:
        up = [x for x in ws if w < x <= 500]
        down = [x for x in ws if x < w]
        best = up[0] if up else (down[-1] if down else min(x for x in ws if x > w))
    elif w > 500:
        up = [x for x in ws if x > w]
        best = up[0] if up else max(x for x in ws if x < w)
    else:
        down = [x for x in ws if x < w]
        best = down[-1] if down else min(x for x in ws if x > w)
    return next(f for f in faces if f["weight"] == best)


def _face(ff: str, fw, italic: bool = False) -> tuple[str, bool]:
    """(font name, bold) as PowerPoint needs it to draw the face Chrome drew.

    Weight 600 and up is always the base family with bold on. Naming the
    heavy face instead (Arial at 800 is "Arial Black", a brand family at 600
    its own "Semibold" face) did not survive: finalize's theme pass swaps
    every font name that is not the theme font for the theme font, and the
    weight went with the name, so the text shipped regular, in PowerPoint
    too (2026-10-06). extract() draws 600+ at 700 before measuring, so the
    self-check compares against the face that actually ships.

    Below 600, Chrome picks a face by weight from everything installed under
    the family (a brand family at 500 is often its own "Medium" face), and
    that face is named the way PowerPoint knows it.
    """
    fam = _family(ff)
    try:
        w = int(fw)
    except (TypeError, ValueError):
        w = 700 if str(fw) in ("bold", "bolder") else 400
    if w >= 600:
        return fam, True
    faces = [f for f in _face_table().get(fam.lower(), []) if f["italic"] == italic] or \
        _face_table().get(fam.lower(), [])
    normal = [f for f in faces if f["width"] == 5] or faces
    if not normal:
        return fam, w >= 600
    face = _pick_weight(normal, w)
    return face["ppt_name"] or fam, face["ppt_bold"]


class _Measure:
    """Text width from the font file's own advance widths: exact at any size
    (PIL rounds each letter to whole pixels at small sizes, so 13px and 13.3px
    measured the same)."""

    def __init__(self, metrics, size_px: float):
        self.cmap, self.adv, self.upm, self.default = metrics
        self.k = size_px / self.upm

    def getlength(self, s: str) -> float:
        return sum(self.adv.get(self.cmap.get(ord(ch)), self.default) for ch in s) * self.k


_METRICS: dict = {}


def _font(family: str, bold: bool, size_px: float):
    """A measurer for this face and size, or None when the font file can't be found."""
    key = (family.lower(), bold, round(size_px, 2))
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    fams = _family_index()
    fam = family.lower()
    path = _face_path(family, bold) or next((p for (f, s), p in fams.items() if f == fam), None)
    font = None
    if path:
        if path not in _METRICS:
            try:
                from fontTools.ttLib import TTFont
                f = TTFont(path, lazy=True, fontNumber=0)
                hmtx = f["hmtx"].metrics
                adv = {g: m[0] for g, m in hmtx.items()}
                _METRICS[path] = (f.getBestCmap() or {}, adv, f["head"].unitsPerEm,
                                  adv.get(".notdef", f["head"].unitsPerEm // 2))
            except Exception:
                _METRICS[path] = None
        if _METRICS[path]:
            font = _Measure(_METRICS[path], max(1.0, float(size_px)))
    _FONT_CACHE[key] = font
    return font


_DESC_CACHE: dict = {}


def _face_path(face: str, bold: bool):
    """Font file for a PowerPoint font name + bold flag."""
    faces = [f for f in _face_table().get(face.lower(), []) if f["ppt_name"].lower() == face.lower()
             and not f["italic"]]
    hit = next((f for f in faces if f["ppt_bold"] == bold), None) or (faces[0] if faces else None)
    return hit["path"] if hit else None


def _descent_gap(face: str, bold: bool) -> float:
    """Windows descent minus typographic descent, in em (0 when unknown)."""
    key = (face.lower(), bold)
    if key not in _DESC_CACHE:
        gap = 0.0
        path = _face_path(face, bold)
        if path:
            try:
                from fontTools.ttLib import TTFont
                f = TTFont(path, lazy=True)
                upm = f["head"].unitsPerEm
                o = f["OS/2"]
                if not (o.fsSelection & 128):      # USE_TYPO_METRICS off: Chrome uses win metrics
                    gap = (o.usWinDescent - abs(o.sTypoDescender)) / upm
            except Exception:
                gap = 0.0
        _DESC_CACHE[key] = gap
    return _DESC_CACHE[key]


def _snapped_px(size_px: float) -> float:
    from twins.helpers import snap_font_pt
    return snap_font_pt(size_px * 0.75) / 0.75


def _wrapped_lines(paragraphs, width_px: float) -> int | None:
    """Greedy word-wrap line count, measured with the real font files (as
    PowerPoint will set the text, which is slightly wider than Chrome). None if
    a font is missing."""
    total = 0
    for para in paragraphs:
        words, widths = [], []
        for r in para:
            # measured at the size PowerPoint will use (snapped to the allowed list)
            f = _font(r.get("font") or "", r.get("bold", False), _snapped_px(r["size_px"]))
            if f is None:
                return None
            for wd in re.split(r"(\s+)", r["t"]):
                if wd:
                    words.append(wd)
                    widths.append(f.getlength(wd) + (r.get("letter_spacing_px") or 0) * len(wd))
        lines, cur = 1, 0.0
        for wd, wl in zip(words, widths):
            if wd.isspace():
                cur += wl
                continue
            if cur > 0 and cur + wl > width_px:
                lines += 1
                cur = wl
            else:
                cur += wl
        total += lines
    return total


def _plan_text(plan: Plan, t: dict, order_key, name=None) -> None:
    from twins.helpers import upper_preserving_terms
    if t.get("covered"):
        plan.counts["covered_text_skipped"] += 1
        plan.warn("TEXT_HIDDEN_IN_DESIGN", f"{t.get('id') or 'text'}: covered by a later shape in the design; not drawn")
        return
    if t.get("clipped"):
        plan.warn("TEXT_HIDDEN_IN_DESIGN", f"{t.get('id') or 'text'}: clipped away by its container; not drawn")
        return
    pre = t["ws"] in ("pre", "pre-wrap", "pre-line", "break-spaces")
    paras: list[list[dict]] = [[]]
    prev_last = None
    for r in t["runs"]:
        if r.get("br"):
            paras.append([])
            prev_last = None
            continue
        txt = r["t"]
        if not pre:
            txt = re.sub(r"\s+", " ", txt)
        # Side-by-side pieces with a visible gap but no space between them
        # ("$1.2B" and "to" set as separate spans with a margin): keep the gap.
        if prev_last and r.get("first") and paras[-1] and not paras[-1][-1]["t"].endswith(" ") \
                and not txt.startswith(" ") \
                and r["first"]["y"] < prev_last["y"] + prev_last.get("h", r["first"]["h"]) \
                and prev_last["y"] < r["first"]["y"] + r["first"]["h"] \
                and r["first"]["x"] - prev_last["r"] > 0.2 * r["fs"]:
            # Same line = the pieces overlap vertically (a 32px figure and a
            # 16px "to" share a baseline, not a top). Spaces sized to the gap.
            gap = r["first"]["x"] - prev_last["r"]
            txt = " " * max(1, round(gap / (0.28 * r["fs"]))) + txt
        if r.get("last"):
            prev_last = r["last"]
        if r["tt"] == "uppercase":
            txt = upper_preserving_terms(txt)          # "TaaS" keeps its casing
        elif r["tt"] == "lowercase":
            txt = txt.lower()
        elif r["tt"] == "capitalize":
            txt = txt.title()
        if r.get("td") and r["td"] != "none":
            plan.kill["text_decorations_stripped"] += 1
        col = parse_color(r["color"])
        if (col and col[1] < 0.999) or r.get("op", 1) < 0.999:
            plan.kill["opacity_on_text_normalized"] += 1
        face, bold = _face(r["ff"], r["fw"])
        run = {"t": txt, "font": face, "size_px": r["fs"], "bold": bold,
               "italic": r["fi"] == "italic", "color": col[0] if col else None,
               "letter_spacing_px": _px(r["ls"]) if r["ls"] != "normal" else 0}
        parts = txt.split("\n") if pre else [txt]
        for k, part in enumerate(parts):
            if k:
                paras.append([])
            paras[-1].append(dict(run, t=part))
    for p in paras:
        if p:
            p[0]["t"] = p[0]["t"].lstrip()
            p[-1]["t"] = p[-1]["t"].rstrip()
    paras = [p for p in paras if "".join(x["t"] for x in p).strip()] or []
    if not paras:
        return
    if t.get("listItem"):
        paras[0].insert(0, dict(paras[0][0], t="• "))

    fs = t["fs"]
    lh = _px(t["lh"]) if t["lh"] not in ("normal", None) else fs * 1.15
    lines = max(1, t["lines"])
    ink, cont = t["ink"], t["content"]
    align = t["align"] if t["align"] in ("left", "center", "right", "justify") else \
        {"start": "left", "end": "right"}.get(t["align"], "left")
    if t["display"] in ("flex", "inline-flex", "grid") and t.get("jc") == "center":
        align = "center"
    x, w = cont["x"], cont["w"]
    if w < 2:
        x, w = ink["x"], ink["w"]
    elif align in ("left", "justify") and ink["w"] > 0:
        right = cont["x"] + cont["w"]
        x = ink["x"]
        w = max(right - x, ink["w"])
    elif align == "center" and ink["w"] > 0:
        cx = ink["x"] + ink["w"] / 2
        half = max(ink["w"] / 2, min(cx - cont["x"], cont["x"] + cont["w"] - cx))
        x, w = cx - half, 2 * half
    elif align == "right" and ink["w"] > 0:
        right = max(ink["x"] + ink["w"], cont["x"] + cont["w"])
        w = max(right - cont["x"], ink["w"])
        x = right - w
    # First baseline. Chrome puts it at (top of the first line's text box) +
    # ascent; LibreOffice and PowerPoint with exact line spacing put it at
    # (box top) + line height - descent. Ascent + descent is the first line's
    # text-box height, so the box top that lands both baselines in the same
    # place is: ink top + that height - line height. Measured, so it holds for
    # any font and for large numerals, where a fixed nudge did not.
    flh = t.get("firstLineH") or fs * 1.15
    y = ink["y"] + flh - lh
    # Chrome's descent comes from the font's Windows metrics, LibreOffice's
    # from its typographic ones. Equal for Arial; Arial Black differs by a
    # tenth of an em, which put heavy numerals ~7px low.
    r0 = next((r for p in paras for r in p if r["t"].strip()), None)
    if r0:
        y -= _descent_gap(r0["font"], r0["bold"]) * r0["size_px"]
    h = max(lh * lines, ink["h"]) + 2
    single = lines == 1 and len(paras) == 1
    wrap = not (single or t["ws"] == "nowrap")
    design_px = max((r["size_px"] for p in paras for r in p if r["t"].strip()), default=fs)
    cased = any(r.get("tt") == "uppercase" and upper_preserving_terms(r["t"]) != r["t"].upper()
                for r in t["runs"] if not r.get("br"))

    # Will PowerPoint wrap it into more lines than Chrome did? Measured with
    # the real font files. Widen a little first, then step the font down one.
    if wrap:
        predicted = _wrapped_lines(paras, w)
        if predicted is not None and predicted > lines:
            grown = False
            for extra in (0.02, 0.04, 0.06):
                nw = w * (1 + extra)
                if _wrapped_lines(paras, nw) <= lines:
                    if align == "center":
                        x -= (nw - w) / 2
                    elif align == "right":
                        x -= nw - w
                    w, grown = nw, True
                    break
            if not grown:
                from twins.helpers import snap_font_pt
                for p in paras:
                    for r in p:
                        pt = snap_font_pt(r["size_px"] * 0.75)
                        r["size_px"] = max(8.0, pt - 1) / 0.75
            plan.counts["wrap_adjusted"] += 1
            plan.warn("WRAP_ADJUSTED", f"{t.get('id') or 'text'}: would wrap to "
                      f"{predicted} lines in PowerPoint vs {lines} in the design; "
                      + ("widened" if grown else "font stepped down one size"))
        elif predicted is not None and predicted < lines:
            # Fits on fewer lines than the design (Chrome broke at a width the
            # PowerPoint text just clears): narrow the box toward the design's
            # widest line until the breaks match, so the card keeps its shape.
            nw = w
            while nw - 2 >= ink["w"]:
                nw -= 2
                if _wrapped_lines(paras, nw) == lines:
                    if align == "center":
                        x += (w - nw) / 2
                    elif align == "right":
                        x += w - nw
                    w = nw
                    plan.counts["wrap_adjusted"] += 1
                    plan.warn("WRAP_ADJUSTED", f"{t.get('id') or 'text'}: would fit on "
                              f"{predicted} lines in PowerPoint vs {lines} in the design; "
                              "narrowed to keep the design's line breaks")
                    break

    plan.ops.append({"op": "text", "x": x, "y": y, "w": w, "h": h, "align": align,
                     "line_height_px": lh, "wrap": wrap, "paragraphs": paras,
                     "name": name or (t.get("id") or None), "_order": order_key,
                     "_ink": (ink["x"], ink["y"], ink["w"], ink["h"]), "_single": single,
                     "_lines": lines, "_id": t.get("id") or "", "_glyphs": t.get("glyphs") or [],
                     "_design_px": design_px, "_cased": cased})
    plan.counts["texts"] += 1


# --- svg -------------------------------------------------------------------

def _plan_icon(plan: Plan, ic: dict) -> None:
    """One library icon: inserted at the same spot and color as the sketch
    drew it (the picture fitted into its box, keeping its shape, as the
    browser did). An unknown name keeps its step: icon_helper draws a labeled
    placeholder there, and the warning comes from icon_svg.draw_icons."""
    import icon_svg
    name = ic.get("name") or ""
    x, y, w, h = ic["x"], ic["y"], ic["w"], ic["h"]
    if w < 1 or h < 1:
        plan.warn("ICON_NO_SIZE", f'icon "{name}" has no size on the page; not inserted')
        return
    svg = icon_svg.svg_for(name) if ic.get("drawn") == "icon" else None
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg or "")
    if m:
        vw, vh = int(m.group(1)), int(m.group(2))
        k = min(w / vw, h / vh)
        fw, fh = vw * k, vh * k
        x, y, w, h = x + (w - fw) / 2, y + (h - fh) / 2, fw, fh
    col = parse_color(ic.get("color"))
    plan.ops.append({"op": "icon", "name": name, "x": x, "y": y, "w": w, "h": h,
                     "color": col[0] if col else "000000",
                     "placeholder": not bool(m), "_order": ic["order"]})
    plan.counts["icons"] = plan.counts.get("icons", 0) + 1


def _plan_svg(plan: Plan, s: dict) -> None:
    if s["unsupported"]:
        plan.fallbacks.append({"kind": "svg", "id": s.get("id") or "", "x": s["x"], "y": s["y"],
                               "w": s["w"], "h": s["h"],
                               "reason": "svg with " + ", ".join(sorted(set(s["unsupported"])))})
        return
    for i, it in enumerate(s["items"]):
        k = s["order"] + 0.0001 * (i + 1)
        fill = parse_color(it.get("fill"))
        stroke = parse_color(it.get("stroke"))
        line = {"color": stroke[0], "w": it["sw"], "dash": "dashed" if it.get("dash") else None} \
            if stroke and it.get("sw", 0) > 0 else None
        if it["k"] == "poly":
            if len(it["pts"]) == 2 and not it["closed"]:
                plan.ops.append({"op": "connector", "points": it["pts"], "line": line, "_order": k})
            else:
                plan.ops.append({"op": "freeform", "points": it["pts"], "closed": it["closed"],
                                 "fill": fill[0] if fill and it["closed"] else None,
                                 "alpha": (fill[1] if fill else 1) * it.get("fillOp", 1),
                                 "line": line, "_order": k})
        elif it["k"] == "oval":
            plan.ops.append({"op": "shape", "kind": "oval", "x": it["x"], "y": it["y"],
                             "w": it["w"], "h": it["h"], "fill": fill[0] if fill else None,
                             "alpha": (fill[1] if fill else 1) * it.get("fillOp", 1),
                             "line": line, "_order": k})
        elif it["k"] == "text" and it["t"]:
            col = parse_color(it["color"])
            align = {"middle": "center", "end": "right"}.get(it["anchor"], "left")
            plan.ops.append({"op": "text", "x": it["x"], "y": it["y"], "w": it["w"] + 4, "h": it["h"],
                             "align": align, "line_height_px": it["h"], "wrap": False,
                             "paragraphs": [[{"t": it["t"], "font": _face(it["ff"], it["fw"])[0],
                                              "size_px": it["fs"],
                                              "bold": _face(it["ff"], it["fw"])[1], "italic": False,
                                              "color": col[0] if col else None}]],
                             "_order": k})
        plan.counts["svg_items"] += 1


# --- clearance ---------------------------------------------------------------

def _apply_clearance(plan: Plan) -> None:
    """Text sitting right on the edge of the filled box behind it gets room.
    LibreOffice and PowerPoint can set text a few pixels off Chrome, enough to
    push the last line past a dark band's edge. Deliberately overhanging text
    (big numerals breaking out of a card) is left alone."""
    boxes = [o for o in plan.ops if o["op"] == "shape" and o.get("_filled") and o.get("_box")]
    for t in (o for o in plan.ops if o["op"] == "text" and o.get("_ink")):
        ix, iy, iw, ih = t["_ink"]
        holders = [b for b in boxes if b["_order"] < t["_order"]
                   and b["_box"][0] - 1 <= ix and ix + iw <= b["_box"][0] + b["_box"][2] + 1
                   and b["_box"][1] - 1 <= iy and iy + ih <= b["_box"][1] + b["_box"][3] + 1]
        if not holders:
            continue
        b = min(holders, key=lambda q: q["_box"][2] * q["_box"][3])
        bx, by, bw, bh = b["_box"]
        gap_bottom = (by + bh) - (iy + ih)
        if 0 <= gap_bottom < 4:
            grow = 6 - gap_bottom
            b["h"] += grow
            b["_box"] = (bx, by, bw, bh + grow)
            plan.counts["boxes_grown_for_clearance"] += 1
        gap_right = (bx + bw) - (ix + iw)
        if t.get("_single") and t["align"] == "left" and 0 <= gap_right < 4:
            grow = 6 - gap_right
            b["w"] += grow
            b["_box"] = (bx, by, bw + grow, bh)
            plan.counts["boxes_grown_for_clearance"] += 1


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

HEAVY_TO_BOLD_JS = r"""() => {
  let n = 0;
  for (const el of document.querySelectorAll('*')) {
    const w = parseInt(getComputedStyle(el).fontWeight, 10);
    if (w >= 600 && w !== 700) { el.style.setProperty('font-weight', '700', 'important'); n++; }
  }
  return n;
}"""


def extract(page, html: Path, subtitle_as_shape: bool) -> dict:
    page.goto(html.resolve().as_uri())
    page.wait_for_load_state("load")
    try:
        page.evaluate("document.fonts.ready")
    except Exception:
        pass
    page.wait_for_timeout(100)
    # Library icons are drawn exactly as render_html drew them for the review,
    # so the boxes and the self-check's reference image include them.
    import icon_svg
    icon_warnings = icon_svg.draw_icons(page)
    # PowerPoint gets bold on/off only (see _face): draw every weight from 600
    # up at 700, so the boxes, wraps and the self-check's reference image are
    # those of the face that ships, not of a heavier face the deck cannot keep.
    page.evaluate(HEAVY_TO_BOLD_JS)
    # The design as the alarm compares it: without the fields the template
    # draws (title, footer, page number), since the script doesn't draw them.
    page.evaluate("""(sas) => { for (const el of document.querySelectorAll('[data-template-field]')) {
        if (sas && el.getAttribute('data-template-field') === 'subtitle') continue;
        el.dataset.alarmHidden = el.style.visibility; el.style.visibility = 'hidden'; } }""",
                  subtitle_as_shape)
    cx, cy = page.evaluate("""() => { const c = document.querySelector('.slide-canvas') || document.querySelector('.slide') || document.body;
        const r = c.getBoundingClientRect(); return [r.x, r.y]; }""")
    shot = page.screenshot(clip={"x": cx, "y": cy, "width": CANVAS_W, "height": CANVAS_H})
    page.evaluate("""() => { for (const el of document.querySelectorAll('[data-alarm-hidden]')) {
        el.style.visibility = el.dataset.alarmHidden; delete el.dataset.alarmHidden; } }""")
    data = page.evaluate(EXTRACT_JS, {"subtitleAsShape": subtitle_as_shape})
    data["_shot"] = shot
    data["icon_warnings"] = icon_warnings
    return data


def plan_from_extract(data: dict, subtitle_as_shape: bool,
                      template_bg: str | None = None) -> tuple[Plan, dict]:
    """template_bg: the slide layout's own background ('RRGGBB'), when the
    slide belongs to a build. A canvas of that color is left to the template
    instead of drawn as a full-slide rectangle over the master's artwork."""
    plan = Plan()
    plan.template_bg = (template_bg or "").upper().lstrip("#") or None
    fields = {k: v for k, v in (data.get("fields") or {}).items()
              if not (k == "subtitle" and subtitle_as_shape)}
    cv = data.get("canvas") or {}
    if abs((cv.get("w") or CANVAS_W) - CANVAS_W) > 1 or abs((cv.get("h") or CANVAS_H) - CANVAS_H) > 1:
        # Not on the fixed 1280x720 canvas the design spec requires (an older
        # 1600x900 design, say). Every coordinate would be off; the agent
        # translates the whole slide instead of the script guessing a rescale.
        plan.fallbacks.append({"kind": "canvas", "id": "", "x": 0, "y": 0, "w": CANVAS_W,
                               "h": CANVAS_H, "reason": f"design is {cv.get('w'):.0f}x{cv.get('h'):.0f}, "
                                                        "not the 1280x720 canvas; translate the whole slide"})
        return plan, fields
    items = [(b["order"], "box", b) for b in data["boxes"]]
    items += [(t["order"], "text", t) for t in data["texts"]]
    items += [(s["order"], "svg", s) for s in data["svgs"]]
    items += [(ic["order"], "icon", ic) for ic in data.get("icons") or []]
    for w in data.get("icon_warnings") or []:
        plan.warn(w["code"], w["detail"])
    for f in data["fallbacks"]:
        plan.fallbacks.append({k: f.get(k) for k in ("kind", "id", "x", "y", "w", "h", "reason")})
    for _, kind, it in sorted(items, key=lambda z: z[0]):
        if kind == "box":
            _plan_box(plan, it, it["order"])
        elif kind == "text":
            name = "subtitle" if it.get("tf") == "subtitle" and subtitle_as_shape else None
            _plan_text(plan, it, it["order"], name=name)
        elif kind == "icon":
            _plan_icon(plan, it)
        else:
            _plan_svg(plan, it)
    _apply_clearance(plan)
    plan.ops.sort(key=lambda o: o["_order"])
    plan.counts["pseudo_elements"] = int(data.get("pseudo_count") or 0)
    _check_pale_fills(plan)
    _check_arrow_ends(plan, data)
    return plan, fields


def _public_plan(plan: Plan) -> dict:
    return {"version": TRANSLATOR_VERSION,
            "ops": [{k: v for k, v in o.items() if not k.startswith("_")} for o in plan.ops]}


NATIVE_TEMPLATE = '''# {name} -- translated by translate_html.py ({version}), deterministic.
# The plan is in {plan_name}; twins/html_emit.py draws it.
{fields_block}
{fallback_line}import json
import sys
from pathlib import Path

sys.path.insert(0, r"{skill}")
from twins.html_emit import build  # noqa: E402

HERE = Path(__file__).resolve().parent
PLAN = json.loads((HERE / "{plan_name}").read_text(encoding="utf-8"))


def build_slide():
    prs, slide = build(PLAN)
    # --- FALLBACK ELEMENTS: drawn by slide-builder-translator (agent) ---
    # (none)
    # --- END FALLBACK ELEMENTS ---
    return prs


if __name__ == "__main__":
    build_slide().save(str(Path(__file__).resolve().with_suffix(".pptx")))
'''


def _fields_block(fields: dict) -> str:
    lines = ["# __template_fields__ = {"]
    for k in ("title", "subtitle", "footer", "page_number"):
        if k in fields and fields[k]:
            lines.append(f"#     {k!r}: {json.dumps(fields[k], ensure_ascii=False)},")
    lines.append("# }")
    return "\n".join(lines)


def write_outputs(html: Path, emit_dir: Path, letter: str, plan: Plan, fields: dict,
                  visible_text: str) -> dict:
    stem = f"option_{letter}_native"
    plan_name = f"{stem}.plan.json"
    (emit_dir / plan_name).write_text(json.dumps(_public_plan(plan), indent=1), encoding="utf-8")
    fb = ""
    if plan.fallbacks:
        fb = (f"# FALLBACK_PENDING: {len(plan.fallbacks)} element(s) need the "
              f"slide-builder-translator agent; see option_{letter}_translation_report.json\n")
    (emit_dir / f"{stem}.py").write_text(NATIVE_TEMPLATE.format(
        name=f"{stem}.py", version=TRANSLATOR_VERSION, plan_name=plan_name,
        fields_block=_fields_block(fields), fallback_line=fb, skill=str(SKILL)), encoding="utf-8")
    report = {
        "translator": TRANSLATOR_VERSION,
        "html": str(html),
        "css_kill_list_applied": plan.kill,
        "warnings": plan.warnings,
        "counts": plan.counts,
        "fallback": plan.fallbacks,
        "self_check": plan.self_check,
        "needs_agent": bool(plan.fallbacks),
        "html_sha256": _sha256(html),
        "template_fields": fields,
        "visible_text_chars": len(re.sub(r"\s+", "", visible_text or "")),
    }
    (emit_dir / f"option_{letter}_translation_report.json").write_text(
        json.dumps(report, indent=1), encoding="utf-8")
    return report


def _sha256(path: Path) -> str:
    import hashlib
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return ""


def fallback_pending(native_py: Path) -> bool:
    """True while the translator agent still has elements to draw."""
    try:
        return "# FALLBACK_PENDING:" in Path(native_py).read_text(encoding="utf-8")
    except OSError:
        return False


def needs_conversion(html: Path, emit_dir: Path, letter: str) -> bool:
    """Does this design need converting (again)?

    Yes when there is no option_X_native.py yet, or the design changed after
    it was written (the report records the design's fingerprint; an older
    report without one falls back to file times). No otherwise: converting
    again rewrites option_X_native.py from scratch, which erased what the
    translator agent had drawn in fallback mode and marked it pending again,
    so a QC fix or redesign looped on "run the agent" for ever (2026-10-06).
    """
    native = Path(emit_dir) / f"option_{letter}_native.py"
    if not native.exists():
        return True
    try:
        rep = json.loads((Path(emit_dir) / f"option_{letter}_translation_report.json")
                         .read_text(encoding="utf-8"))
    except Exception:
        rep = {}
    sha = rep.get("html_sha256") if isinstance(rep, dict) else None
    if sha:
        return sha != _sha256(html)
    return Path(html).stat().st_mtime > native.stat().st_mtime


def convert_picked(out: Path, items: list[tuple[int, str]]) -> list[Path]:
    """Convert the picked sketch options that need it; keep the rest as they are.

    items: (slide number, letter). Returns the option_X_native.py files that
    still wait on the translator agent (fallback mode): the ones just
    converted with elements left over, and the ones kept whose agent part is
    not drawn yet. Prints one line per option kept as is.
    """
    jobs, waiting = [], []
    for n, letter in items:
        sd = out / f"slide_{n:02d}"
        html = sd / f"option_{letter}.html"
        if not html.exists():
            continue
        native = sd / f"option_{letter}_native.py"
        if needs_conversion(html, sd, letter):
            jobs.append(job_for(out, n, letter))
            continue
        if fallback_pending(native):
            waiting.append(native)
        else:
            print(f"[ok] slide {n} option {letter}: already converted from the current "
                  "design; kept as is (nothing the translator agent drew is redone)")
    if jobs:
        for r in translate_many(jobs):
            if r["needs_agent"]:
                h = Path(r["html"])
                waiting.append(h.with_name(h.stem + "_native.py"))
    return waiting


def _subtitle_as_shape(out: Path, slide_n: int) -> bool:
    """True when this slide's layout has no subtitle placeholder (the takeaway is
    then drawn as a body shape named 'subtitle', which finalize recognizes)."""
    try:
        import _paths as _p
        from _chrome_schema import load_chrome_yml
        meta = json.loads(_p.meta_json(out).read_text(encoding="utf-8"))
        slide = next(s for s in meta["slides"] if s.get("n") == slide_n)
        spec = load_chrome_yml(_p.chrome_yml(Path(meta["template"])))
        lc = spec.layouts.get(slide.get("layout") or "")
        return lc is None or getattr(lc, "subtitle_placeholder_idx", None) is None
    except Exception:
        return True


_TEMPLATES: dict = {}   # template opened once per run, not once per slide


def _title_text_span(out: Path, slide_n: int) -> tuple[float, float] | None:
    """(left, width) in px of the title's TEXT on this slide's layout: the
    title box (chrome.yml's title_box_x_px / title_box_width_px, else the
    layout's title placeholder) less its inner left and right margins. The
    takeaway drawn as a shape has no inner margin, so this is where its text
    must sit to line up with the title's. None when it can't be read."""
    try:
        import _paths as _p
        from _chrome_schema import load_chrome_yml
        from pptx import Presentation
        meta = json.loads(_p.meta_json(out).read_text(encoding="utf-8"))
        slide = next(s for s in meta["slides"] if s.get("n") == slide_n)
        layout_name = slide.get("layout") or ""
        tpl = Path(meta["template"])
        spec = load_chrome_yml(_p.chrome_yml(tpl))
        lc = spec.layouts.get(layout_name)
        key = (str(tpl), tpl.stat().st_mtime)
        prs = _TEMPLATES.get(key)
        if prs is None:
            prs = _TEMPLATES[key] = Presentation(str(tpl))
        layout = next(l for l in prs.slide_layouts if l.name == layout_name)
        t_idx = getattr(lc, "title_placeholder_idx", None) if lc else None
        ph = next((p for p in layout.placeholders if t_idx is not None
                   and p.placeholder_format.idx == t_idx), None) or next(
            p for p in layout.placeholders if int(p.placeholder_format.type or 0) in (1, 3))
        x = getattr(lc, "title_box_x_px", None) if lc else None
        w = getattr(lc, "title_box_width_px", None) if lc else None
        if x is None or w is None:
            x, w = int(ph.left) / 9525, int(ph.width) / 9525
        from pptx.oxml.ns import qn

        def _ins(attr):
            for el in (ph._element, getattr(ph, "_base_placeholder", None)):
                el = getattr(el, "_element", el)
                bp = el.find(".//" + qn("a:bodyPr")) if el is not None else None
                if bp is not None and bp.get(attr) is not None:
                    return int(bp.get(attr)) / 9525
            return 91440 / 9525          # PowerPoint's default inner margin
        lin, rin = _ins("lIns"), _ins("rIns")
        return float(x) + lin, float(w) - lin - rin
    except Exception:
        return None


def _template_bg(out: Path, slide_n: int) -> str | None:
    """This slide's layout background ('RRGGBB'): chrome.yml's record, else
    read from the template. None when unknown or a picture."""
    try:
        import _paths as _p
        import _template_bg as TB
        from _chrome_schema import load_chrome_yml
        meta = json.loads(_p.meta_json(out).read_text(encoding="utf-8"))
        slide = next(s for s in meta["slides"] if s.get("n") == slide_n)
        tpl = Path(meta["template"])
        lc = None
        try:
            lc = load_chrome_yml(_p.chrome_yml(tpl)).layouts.get(slide.get("layout") or "")
        except Exception:
            pass
        f = TB.facts_for(tpl, slide.get("layout") or "", lc)
        # For a gradient or pattern this is its first color, the one prep gave
        # the designer for the canvas: a canvas of that color is still the
        # template's background and is left to it.
        return f["bg_hex"] if f.get("bg_hex") and f.get("bg_kind") != "picture" else None
    except Exception:
        return None


def job_for(out: Path, slide_n: int, letter: str) -> tuple:
    """The translate_many job for one picked option of a build."""
    sd = out / f"slide_{slide_n:02d}"
    sas = _subtitle_as_shape(out, slide_n)
    return (sd / f"option_{letter}.html", sd, letter, sas,
            _title_text_span(out, slide_n) if sas else None, _template_bg(out, slide_n))


def snap_subtitle(plan: "Plan", span: tuple[float, float] | None) -> None:
    """Line the takeaway drawn as a shape up with the title: its text starts
    where the title's text starts and spans the same width. The design's
    height position is kept. Workers are not told the title's left edge, so
    the sketch's x was a guess, and the line came out indented under the
    title (2026-10-06). Runs after the self-check, which compares against the
    design as drawn."""
    if not span:
        return
    op = next((o for o in plan.ops if o.get("op") == "text" and o.get("name") == "subtitle"),
              None)
    if op is None:
        return
    x, w = span
    if w <= 0 or (abs(op["x"] - x) < 0.5 and abs(op["w"] - w) < 0.5):
        return
    lines = op.get("_lines")
    predicted = _wrapped_lines(op["paragraphs"], w)
    if lines and predicted and predicted > lines:
        op["h"] = op["h"] * predicted / lines
    op["x"], op["w"] = x, w
    plan.counts["subtitle_aligned_to_title"] = 1


def self_check(items: list[tuple["Plan", dict]]) -> None:
    """Render every translated slide once and hand any element that came out
    looking different from the design to the agent (scripts/translate_alarm.py).

    items: (plan, extracted data) pairs; plans are changed in place. If the
    render can't run (no LibreOffice), every plan gets a SELF_CHECK_SKIPPED
    warning and keeps all its elements.
    """
    import tempfile
    import translate_alarm as A
    from twins.html_emit import build
    try:
        with tempfile.TemporaryDirectory() as td:
            paths = []
            for k, (plan, _) in enumerate(items):
                prs, _s = build(_public_plan(plan))
                if plan.canvas_bg and plan.canvas_bg != "FFFFFF":
                    # The canvas was left to the template's background; the
                    # check's blank slide gets that color instead, so it
                    # compares like with like.
                    from pptx.dml.color import RGBColor
                    _s.background.fill.solid()
                    _s.background.fill.fore_color.rgb = RGBColor.from_string(plan.canvas_bg)
                paths.append(Path(td) / f"t{k:03d}.pptx")
                prs.save(str(paths[-1]))
            rendered = A.render_full(paths)
    except Exception as exc:
        for plan, _ in items:
            plan.warn("SELF_CHECK_SKIPPED", f"could not render to compare ({type(exc).__name__})")
        return
    for (plan, data), got in zip(items, rendered):
        if not got:
            plan.warn("SELF_CHECK_SKIPPED", "the slide did not render")
            continue
        native, chars = got
        fired = [r for r in A.compare(plan.ops, A.load_rgb(data["_shot"]), native, chars)
                 if r["fired"]]
        plan.self_check = {"ran": True, "fired": [
            {"element": r["name"], "what": r["fired"]} for r in fired]}
        for font, ratio in (getattr(A.compare, "font_ratios", None) or {}).items():
            plan.warn("RENDER_FONT_RATIO", f"the check's renderer drew every {font} text at "
                      f"{ratio:.0%} of its width (a substituted font); allowed for, not a defect")
        for r in sorted(fired, key=lambda r: -r["i"]):
            x0, y0, x1, y1 = r["box"]
            plan.fallbacks.append({
                "kind": "self-check", "id": plan.ops[r["i"]].get("name") or "",
                "x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0,
                "reason": "came out looking different from the design ("
                          + ", ".join(r["fired"]) + ")"})
            del plan.ops[r["i"]]
        plan.counts["self_check_handed_over"] = len(fired)


def translate_many(jobs: list[tuple], check: bool = True) -> list[dict]:
    """jobs: (html, emit_dir, letter, subtitle_as_shape[, title_text_span[, template_bg]]);
    job_for() builds one for a build's slide. One browser for all, then one
    LibreOffice pass for the self-check."""
    from playwright.sync_api import sync_playwright
    done = []
    with sync_playwright() as pw:
        from _browser import launch
        browser = launch(pw)
        page = browser.new_page(viewport={"width": CANVAS_W, "height": CANVAS_H})
        for html, emit_dir, letter, sas, *rest in jobs:
            data = extract(page, html, sas)
            plan, fields = plan_from_extract(data, sas, rest[1] if len(rest) > 1 else None)
            done.append((html, emit_dir, letter, plan, fields, data, rest[0] if rest else None))
        browser.close()
    if check and done:
        self_check([(d[3], d[5]) for d in done])
    for d in done:
        snap_subtitle(d[3], d[6])
    return [write_outputs(html, emit_dir, letter, plan, fields, data.get("visible_text", ""))
            for html, emit_dir, letter, plan, fields, data, _span in done]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Translate picked HTML designs to native PowerPoint.")
    ap.add_argument("--out", type=Path, help="Build output dir.")
    ap.add_argument("--slide", type=int, help="Slide number.")
    ap.add_argument("--letter", help="Option letter.")
    ap.add_argument("--html", type=Path, help="Standalone: an HTML file to translate.")
    ap.add_argument("--emit", type=Path, help="Standalone: where to write the outputs.")
    ap.add_argument("--no-self-check", action="store_true",
                    help="Skip rendering and comparing with the design (debugging only).")
    args = ap.parse_args(argv)
    if args.html:
        emit = args.emit or args.html.parent
        emit.mkdir(parents=True, exist_ok=True)   # a manual run used to crash here
        letter = re.match(r"option_([A-Z])", args.html.name)
        jobs = [(args.html, emit, letter.group(1) if letter else "A", True)]
    elif args.out and args.slide and args.letter:
        sd = args.out / f"slide_{args.slide:02d}"
        html = sd / f"option_{args.letter}.html"
        if not html.exists():
            print(f"ERROR: no design at {html}")
            return 2
        jobs = [job_for(args.out, args.slide, args.letter)]
    else:
        ap.error("give --out/--slide/--letter, or --html")
    for rep in translate_many(jobs, check=not args.no_self_check):
        c = rep["counts"]
        print(f"[ok] {Path(rep['html']).parent.name}/{Path(rep['html']).name}: "
              f"{c['shapes']} shapes, {c['texts']} text boxes, {c['svg_items']} drawing items"
              + (f"; {len(rep['fallback'])} element(s) need the agent" if rep["fallback"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
