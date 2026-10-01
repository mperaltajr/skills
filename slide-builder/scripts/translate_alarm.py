#!/usr/bin/env python3
"""translate_alarm.py — does each translated element look like the design?

The translator agent looked at its own render and fixed what was off. The
script can't look, so this does the looking for it, one element at a time:
inside each element's box it compares the design (Chrome's screenshot) with
the PowerPoint render (LibreOffice) on three things:

  color     the average color of the box (wrong fill, wrong text color,
            a missing shape)
  ink       how much of the box is covered by marks that differ from the
            background (missing or extra text, wrong size, an extra line)
  position  where those marks sit (shifted text or shapes)

Rendering noise between the two engines is small and steady, so a threshold
just above it catches real defects. An element that trips the alarm is taken
out of the script's drawing and handed to the agent (fallback mode), which
redraws only those elements.

Thresholds are calibrated on real translations; see
tests/translate_alarm_calibrate.py and tests/translate_alarm_seeded.py.
"""
from __future__ import annotations

import io
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

SKILL = Path(__file__).resolve().parents[1]
if str(SKILL) not in sys.path:
    sys.path.insert(0, str(SKILL))

W, H = 1280, 720
PAD = 3
INK_DIST = 60          # a pixel is "ink" when this far (RGB distance) from the background

# Limits, set just above the noise between Chrome and LibreOffice on ~3,000
# real elements (tests/translate_alarm_calibrate.py) and checked against
# planted defects (tests/translate_alarm_seeded.py).
# Text, from where its letters landed:
SCALE_LIMIT = 0.04        # letters 4% wider/narrower than designed (size, spacing)
HEIGHT_LIMIT = 0.15       # letters 15% taller/shorter (size, on short labels)
TEXT_SHIFT_X = 3.0        # px a line's anchor (left, center or right) moved
TEXT_SHIFT_Y = 4.0        # px the text moved up or down
TEXT_COLOR_LIMIT = 20.0   # RGB distance, box average
TEXT_INK_COLOR_LIMIT = 52.0  # RGB distance, the letters' own (core) color
# Shapes and lines, from pixels:
COLOR_LIMIT = 14.0        # RGB distance between the boxes' average colors
INK_REL_LIMIT = 0.3       # relative change in how much is marked ...
INK_ABS_LIMIT = 0.02      # ... and at least this much (fully dark px per box px)
SHIFT_LIMIT = 4.0         # px the render must move to line up with the design
RESIDUAL_LIMIT = 0.3      # share of the (softened) marks still different once lined up


def load_rgb(src) -> np.ndarray:
    """PNG path or bytes to a float RGB array at 1280x720."""
    im = Image.open(io.BytesIO(src) if isinstance(src, (bytes, bytearray)) else src)
    im = im.convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.BILINEAR)
    return np.asarray(im, dtype=np.float32)


def render_many(pptxs: list[Path]) -> list[np.ndarray | None]:
    """Render page 1 of each PPTX with LibreOffice, all in one soffice call."""
    return [r[0] if r else None for r in render_full(pptxs)]


def _powerpoint_pdfs(pptxs: list[Path]) -> None:
    """PDF beside each PPTX, exported by PowerPoint itself (Windows, opt-in,
    PowerPoint must be closed). A file PowerPoint refuses gets no PDF."""
    import win32com.client
    app = win32com.client.DispatchEx("PowerPoint.Application")
    try:
        for p in pptxs:
            try:
                pres = app.Presentations.Open(str(p), True, False, False)  # read-only, no window
                pres.SaveAs(str(p.with_suffix(".pdf")), 32)                 # 32 = PDF
                pres.Close()
            except Exception:
                pass
    finally:
        app.Quit()


def render_full(pptxs: list[Path], engine: str = "libreoffice") -> list[tuple[np.ndarray, list] | None]:
    """(image, characters) for page 1 of each PPTX, from one render pass.
    The characters are where the renderer actually put each letter.
    engine "powerpoint" uses PowerPoint itself (validation runs only)."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slide-qc" / "scripts"))
    from render_slides import _resolve_soffice
    import pypdfium2 as pdfium
    out: list = []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        staged = []
        for i, p in enumerate(pptxs):
            dst = td / f"s{i:04d}.pptx"
            dst.write_bytes(Path(p).read_bytes())
            staged.append(dst)
        if engine == "powerpoint":
            _powerpoint_pdfs(staged)
        else:
            for i in range(0, len(staged), 20):
                subprocess.run([_resolve_soffice(),
                                f"-env:UserInstallation=file:///{(td / 'lo_profile').as_posix()}",
                                "--headless", "--norestore", "--nologo", "--nodefault",
                                "--convert-to", "pdf", "--outdir", str(td),
                                *[str(s) for s in staged[i:i + 20]]],
                               capture_output=True, timeout=600)
        for s in staged:
            pdf = s.with_suffix(".pdf")
            if not pdf.exists():
                out.append(None)
                continue
            doc = pdfium.PdfDocument(str(pdf))
            page = doc[0]
            bmp = page.render(scale=W / page.get_width())
            im = bmp.to_pil().convert("RGB")
            chars = _page_chars(page)
            page.close(); doc.close()
            out.append((load_rgb_from_pil(im), chars))
    return out


def pdf_chars(pdf: Path) -> list[dict]:
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(pdf))
    page = doc[0]
    try:
        return _page_chars(page)
    finally:
        page.close(); doc.close()


def _page_chars(page) -> list[dict]:
    """Visible characters, in 1280x720 px with the origin top-left. Boxes are
    the font's full box (not the ink), so an apostrophe sits on its line."""
    k = W / page.get_width()
    Hp = page.get_height()
    tp = page.get_textpage()
    out = []
    for i in range(tp.count_chars()):
        # pdfium reports a hyphen that ends a line as U+FFFE
        ch = tp.get_text_range(i, 1).replace("\ufffe", "-")
        if not ch.strip():
            continue
        l, b, r, t = tp.get_charbox(i, loose=True)
        out.append({"ch": ch, "x0": l * k, "x1": r * k, "top": (Hp - t) * k,
                    "base": (Hp - b) * k, "h": (t - b) * k})
    tp.close()
    return out


def op_text(o: dict) -> str:
    return "\n".join("".join(r["t"] for r in p) for p in o["paragraphs"])


def match_text(ops: list[dict], chars: list[dict]) -> dict[int, list[int]]:
    """{op index: indexes into chars} for every text op found in the PDF.

    Longest text first; among repeats, the occurrence nearest the box. The PDF
    can list another text's characters in the middle of a paragraph (a big
    numeral overlapping a card's body), so up to MAX_SKIP foreign characters
    may sit between two of ours.
    """
    import re
    MAX_SKIP = 8
    page_s = "".join(c["ch"] for c in chars)
    used = [False] * len(chars)
    found = {}
    order = sorted((i for i, o in enumerate(ops) if o["op"] == "text"),
                   key=lambda i: -len(op_text(ops[i])))
    for i in order:
        o = ops[i]
        needle = "".join(ch for ch in op_text(o) if not ch.isspace())
        if not needle:
            continue
        head = needle[:12]
        best = None
        for m in re.finditer(re.escape(head), page_s):
            a = m.start()
            if any(used[a:a + len(head)]):
                continue
            idx, k, skipped = [], a, 0
            for ch in needle:
                while k < len(chars) and (used[k] or chars[k]["ch"] != ch) and skipped <= MAX_SKIP:
                    k += 1
                    skipped += 1
                if k >= len(chars) or skipped > MAX_SKIP:
                    idx = None
                    break
                idx.append(k)
                k += 1
                skipped = 0
            if not idx:
                continue
            d = abs(chars[a]["x0"] - o["x"]) + abs(chars[a]["top"] - o["y"])
            if best is None or d < best[0]:
                best = (d, idx)
        if best:
            for k in best[1]:
                used[k] = True
            found[i] = best[1]
    return found


def line_breaks(cs: list[dict]) -> list[int]:
    """Indexes k where character k starts a new line."""
    if not cs:
        return []
    hmed = sorted(c["h"] for c in cs)[len(cs) // 2] or 8
    out, last = [], cs[0]["base"]
    for k in range(1, len(cs)):
        if abs(cs[k]["base"] - last) > 0.5 * hmed:
            out.append(k)
            last = cs[k]["base"]
    return out


def text_geometry(o: dict, cs: list[dict]) -> dict | None:
    """Where LibreOffice put this text's characters vs where Chrome drew them.

    Each line in the render should be the design's line moved and, because
    sizes snap to the allowed list, scaled by a known amount. Per line:

    scale      measured stretch over the expected one (1.0 = as designed);
               off when the size, weight or letter spacing differs
    offset_x   how far the line's anchor moved (its left edge, center or
               right edge, by alignment); off when moved or misaligned
    offset_y   how far the text moved vertically
    lines      lines in the render vs the design; more lines can overflow
    reflowed   a word sits on a different line (same number of lines)
    """
    g = o.get("_glyphs") or []
    if not g or not cs:
        return None
    if len(cs) != len(g):
        # A bullet the planner added sits in front; compare from the end.
        n = min(len(cs), len(g))
        cs, g = cs[len(cs) - n:], g[len(g) - n:]
    # line index of every character, in the design and in the render
    hs = sorted(q[3] - q[1] for q in g)
    hmed = hs[len(hs) // 2] or 8
    gl, last, k = [], None, -1
    for q in g:
        if last is None or abs(q[1] - last) > 0.5 * hmed:
            k += 1
            last = q[1]
        gl.append(k)
    brk = set(line_breaks(cs))
    nl, k = [], 0
    for idx in range(len(cs)):
        if idx in brk:
            k += 1
        nl.append(k)
    lines_design, lines_native = gl[-1] + 1, nl[-1] + 1

    # expected stretch: the snapped point size over the design's size
    from_px = [r["size_px"] for p in o["paragraphs"] for r in p if r["t"].strip()]
    exp = 1.0
    if from_px:
        try:
            from twins.helpers import snap_font_pt  # noqa: E402
            px = max(from_px)
            # vs the design's size: covers both the snap to the allowed list
            # and a deliberate one-size step down to keep the line breaks
            exp = snap_font_pt(px * 0.75) / (float(o.get("_design_px") or px) * 0.75)
        except Exception:
            exp = 1.0

    dy = np.array([(c["top"] + c["base"]) / 2 - (q[1] + q[3]) / 2 for c, q in zip(cs, g)])
    offset_y = float(np.median(dy))

    # Stretch, fitted on runs of characters that share a line in both (a
    # word that moved to the next line starts a new run).
    runs, start = [], 0
    for i in range(1, len(g) + 1):
        if i == len(g) or gl[i] != gl[i - 1] or nl[i] != nl[i - 1]:
            runs.append(list(range(start, i)))
            start = i
    scales = []
    for idx in runs:
        xc = np.array([g[i][0] for i in idx])
        xn = np.array([cs[i]["x0"] for i in idx])
        if len(idx) >= 3 and xc.max() - xc.min() >= 30:
            s_, _a = np.polyfit(xc, xn, 1)
            scales.append((float(s_) / exp, float(xc.max() - xc.min())))
    scale = None
    if scales:
        w = np.array([q[1] for q in scales])
        scale = float(np.average([q[0] for q in scales], weights=w))

    # Size from letter height, for text too short to measure a stretch.
    hc = np.median([q[3] - q[1] for q in g])
    hn = np.median([c["h"] for c in cs])
    hscale = float(hn / hc / exp) if hc > 0 else None

    # Anchor of every line that holds the same characters in both.
    align = o.get("align", "left")
    offsets, reflowed = [], False
    for L in range(lines_design):
        idx = [i for i in range(len(g)) if gl[i] == L]
        same = len({nl[i] for i in idx}) == 1 and             sum(1 for v in nl if v == nl[idx[0]]) == len(idx)
        if not same:
            reflowed = True
            continue
        c0, c1 = g[idx[0]][0], g[idx[-1]][2]
        n0, n1 = cs[idx[0]]["x0"], cs[idx[-1]]["x1"]
        if align == "center":
            offsets.append((n0 + n1) / 2 - (c0 + c1) / 2)
        elif align == "right":
            offsets.append(n1 - c1)
        else:
            offsets.append(n0 - c0)
    if not offsets and align in ("left", "right", "justify", "start", "end"):
        # Every line reflowed (a word moved to the next line). Lines still
        # usually START on the same character in both (END, for right-aligned
        # text), and that edge must not move.
        n = len(g)
        for i in range(n):
            if align in ("right", "end"):
                last_d = i == n - 1 or gl[i + 1] != gl[i]
                last_n = i == n - 1 or nl[i + 1] != nl[i]
                if last_d and last_n:
                    offsets.append(cs[i]["x1"] - g[i][2])
            else:
                first_d = i == 0 or gl[i - 1] != gl[i]
                first_n = i == 0 or nl[i - 1] != nl[i]
                if first_d and first_n:
                    offsets.append(cs[i]["x0"] - g[i][0])
    return {"scale": round(scale, 4) if scale is not None else None,
            "hscale": round(hscale, 4) if hscale is not None else None,
            "offset_x": round(float(np.median(offsets)), 2) if offsets else None,
            "offset_y": round(offset_y, 2),
            "lines_design": lines_design, "lines_native": lines_native,
            "reflowed": reflowed, "chars": len(g)}


def text_ink(o: dict, cs: list[dict], design: np.ndarray, native: np.ndarray) -> float | None:
    """Ink inside the letters' own boxes, render over design (1.0 = same).
    Catches a different weight, which barely changes letter widths."""
    g = o.get("_glyphs") or []
    if not g or not cs:
        return None
    n = min(len(cs), len(g))
    cs, g = cs[len(cs) - n:], g[len(g) - n:]

    def ink(img, boxes):
        tot = area = 0.0
        for x0, y0, x1, y1 in boxes:
            x0, y0 = max(0, int(round(x0))), max(0, int(round(y0)))
            x1, y1 = min(W, int(round(x1))), min(H, int(round(y1)))
            if x1 - x0 < 1 or y1 - y0 < 2:
                continue
            crop = img[y0:y1, x0:x1]
            ring = np.concatenate([crop[0], crop[-1]])
            bg = np.median(ring, axis=0)
            tot += float(_weights(crop, bg).sum())
            area += crop.shape[0] * crop.shape[1]
        return tot / area if area else 0.0

    d = ink(design, [(q[0], q[1], q[2], q[3]) for q in g])
    nv = ink(native, [(c["x0"], c["top"], c["x1"], c["base"]) for c in cs])
    return nv / d if d > 1e-4 else None


def load_rgb_from_pil(im: Image.Image) -> np.ndarray:
    if im.size != (W, H):
        im = im.resize((W, H), Image.BILINEAR)
    return np.asarray(im, dtype=np.float32)


def region(o: dict) -> tuple[int, int, int, int] | None:
    """The box to compare for one plan op, in px (x0, y0, x1, y1)."""
    if o["op"] in ("connector", "freeform"):
        xs = [p[0] for p in o["points"]]
        ys = [p[1] for p in o["points"]]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    elif o["op"] == "text":
        # The design's ink, plus a line below and a little to the right: an
        # extra wrapped line or a run-on shows up there.
        x, y, w, h = o.get("_ink") or (o["x"], o["y"], o["w"], o["h"])
        lh = o.get("line_height_px") or 0
        x0, y0, x1, y1 = x, y, x + w + 0.15 * lh, y + h + lh
    else:
        x0, y0, x1, y1 = o["x"], o["y"], o["x"] + o["w"], o["y"] + o["h"]
    x0, y0 = max(0, int(x0 - PAD)), max(0, int(y0 - PAD))
    x1, y1 = min(W, int(x1 + PAD + 1)), min(H, int(y1 + PAD + 1))
    if x1 - x0 < 2 or y1 - y0 < 2:
        return None
    return x0, y0, x1, y1


def _name(o: dict, i: int) -> str:
    return o.get("name") or f"{o['op']}#{i}"


SEARCH = 14            # px searched in each direction for a better fit


def _weights(img: np.ndarray, bg: np.ndarray) -> np.ndarray:
    """0..1 per pixel: how strongly it differs from the background."""
    return np.clip(np.linalg.norm(img - bg, axis=2) / 255.0, 0, 1)


def _blur(w: np.ndarray) -> np.ndarray:
    """Soften by ~1.5px so the two renderers' edge smoothing doesn't count."""
    from PIL import ImageFilter
    im = Image.fromarray((np.clip(w, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(1.5)), dtype=np.float32) / 255.0


def _edges(w: np.ndarray) -> np.ndarray:
    """Where the marks change: a moved panel's edges stop lining up even when
    its inside looks the same."""
    gy, gx = np.gradient(w)
    return np.hypot(gx, gy)


def _align(wD: np.ndarray, native: np.ndarray, r, bg, mask, edges: bool = False) -> tuple[float, float, float]:
    """(shift px, residual unmoved, residual at the best move).

    residual = share of the marks that differ: sum|design - render| over
    sum(design + render), 0 when identical, 1 when nothing overlaps. Every
    move up to SEARCH px is tried; among moves about as good as the best,
    the smallest wins (a plain line fits equally well slid along itself).
    """
    x0, y0, x1, y1 = r
    h, w = wD.shape
    P = SEARCH + 1
    win = np.pad(native, ((P, P), (P, P), (0, 0)), mode="edge")[y0:y1 + 2 * P, x0:x1 + 2 * P]
    wN = _blur(_weights(win, bg))
    if edges:
        wD, wN = _edges(wD), _edges(wN)
    m = mask.astype(np.float32)
    wD = wD * m

    def res(dx, dy):
        n = wN[P + dy:P + dy + h, P + dx:P + dx + w] * m
        tot = float((wD + n).sum())
        return float(np.abs(wD - n).sum()) / tot if tot > 1e-6 else 0.0

    def pick(errs):
        lo = min(errs.values())
        near = [k for k, v in errs.items() if v <= lo * 1.08 + 0.01]
        return min(near, key=lambda k: (k[0] ** 2 + k[1] ** 2, errs[k]))

    e0 = res(0, 0)
    if e0 < 0.02:
        return 0.0, e0, e0
    errs = {(dx, dy): res(dx, dy) for dy in range(-SEARCH, SEARCH + 1, 2)
            for dx in range(-SEARCH, SEARCH + 1, 2)}
    bx, by = pick(errs)
    for dy in (by - 1, by, by + 1):
        for dx in (bx - 1, bx, bx + 1):
            if abs(dx) <= SEARCH and abs(dy) <= SEARCH and (dx, dy) not in errs:
                errs[(dx, dy)] = res(dx, dy)
    bx, by = pick(errs)
    e = errs[(bx, by)]
    if e > 0.6 * e0:        # moving doesn't really help: not a position problem
        return 0.0, e0, e0
    return float(np.hypot(bx, by)), e0, e


def compare(ops: list[dict], design: np.ndarray, native: np.ndarray,
            chars: list[dict] | None = None) -> list[dict]:
    """One row per element: its numbers and whether it trips the alarm.

    Text is judged by where its letters landed (from the PDF's characters)
    and by its color; shapes and lines by their pixels. Pass the render's
    characters (render_full) to judge text; without them text gets only the
    pixel checks.
    """
    found = match_text(ops, chars) if chars is not None else {}
    # A renderer that substitutes a font (LibreOffice picked a brand
    # family's condensed face for its plain name) makes every text in that font wider or
    # narrower by the same ratio. A translation defect hits one element, so a
    # ratio shared by 3+ texts in one font is taken as the renderer's and
    # divided out (reported as font_ratios).
    flat = [region(o) for o in ops if o.get("_flattened") and region(o)]
    geos, by_font, by_font_h = {}, {}, {}
    for i, k in found.items():
        o = ops[i]
        if o["op"] == "text" and o.get("_glyphs"):
            g = text_geometry(o, [chars[j] for j in k]) or {}
            geos[i] = g
            runs = [r for p in o["paragraphs"] for r in p if r["t"].strip()]
            if g.get("scale") is not None and runs and not o.get("_cased"):
                by_font.setdefault((runs[0]["font"], runs[0].get("bold")), []).append(g["scale"])
            if g.get("hscale") is not None and runs:
                by_font_h.setdefault(runs[0]["font"], []).append(g["hscale"])
    font_ratio, font_hratio = {}, {}
    for f, v in by_font.items():
        if len(v) >= 3:
            med = float(np.median(v))
            if abs(med - 1) > SCALE_LIMIT and float(np.median(np.abs(np.array(v) - med))) < 0.015:
                font_ratio[f] = med
    # Letter height depends on how each engine reads the font's vertical
    # metrics; a height ratio shared across a font's texts is the renderer's.
    for f, v in by_font_h.items():
        if len(v) >= 3:
            med = float(np.median(v))
            if abs(med - 1) > 0.03 and float(np.median(np.abs(np.array(v) - med))) < 0.03:
                font_hratio[f] = med
    compare.font_ratios = {f"{f[0]}{' bold' if f[1] else ''}": round(r, 3) for f, r in font_ratio.items()}
    # Text cut out of shapes: just the letters' own box, so a swatch or a
    # rule beside a label is still judged.
    texts = []
    for i, o in enumerate(ops):
        if o["op"] == "text":
            x, y, w, h = o.get("_ink") or (o["x"], o["y"], o["w"], o["h"])
            texts.append((i, (int(x - 2), int(y - 2), int(x + w + 3), int(y + h + 3))))
    rows = []
    for i, o in enumerate(ops):
        r = region(o)
        if r is None:
            continue
        x0, y0, x1, y1 = r
        D = design[y0:y1, x0:x1]
        N = native[y0:y1, x0:x1]
        mask = np.ones(D.shape[:2], dtype=bool)
        is_text = o["op"] == "text"
        if not is_text:
            # A shape is judged without the text drawn on it; that text is
            # judged on its own, so one wrong word doesn't flag the card too.
            for j, tr in texts:
                if tr:
                    a0, b0 = max(tr[0], x0) - x0, max(tr[1], y0) - y0
                    a1, b1 = min(tr[2], x1) - x0, min(tr[3], y1) - y0
                    if a1 > a0 and b1 > b0:
                        mask[b0:b1, a0:a1] = False
        if mask.sum() < 4:
            continue
        ring = np.concatenate([D[0], D[-1], D[:, 0], D[:, -1]])
        bg = np.median(ring, axis=0)
        color = float(np.linalg.norm(D[mask].mean(0) - N[mask].mean(0)))
        wD = _weights(D, bg) * mask
        wN = _weights(N, bg) * mask
        n = mask.sum()
        cD, cN = wD.sum() / n, wN.sum() / n
        ink_rel = abs(cD - cN) / max(cD, cN, 1e-6)
        # The marks' own color, weighted toward their solid core (cubed
        # weights): smoothed letter edges blend with the background and hid
        # a recolor in plain averages.
        ink_color = 0.0
        cD3, cN3 = wD ** 3, wN ** 3
        if cD3.sum() > 1 and cN3.sum() > 1:
            ink_color = float(np.linalg.norm((D * cD3[..., None]).sum((0, 1)) / cD3.sum()
                                             - (N * cN3[..., None]).sum((0, 1)) / cN3.sum()))
        row = {"i": i, "name": _name(o, i), "op": o["op"], "box": r,
               "color": round(color, 2), "ink_color": round(ink_color, 2),
               "ink_design": round(float(cD), 4), "ink_native": round(float(cN), 4),
               "ink_rel": round(float(ink_rel), 3)}
        reasons = []
        # A gradient flattened to one color is the rule, not a defect: its box
        # average and the box average of text on it are expected to differ.
        on_flat = any(f[0] <= x0 + 4 and f[1] <= y0 + 4 and x1 - 4 <= f[2] and y1 - 4 <= f[3]
                      for f in flat)
        if is_text:
            if (color > TEXT_COLOR_LIMIT and not on_flat) or (ink_color > TEXT_INK_COLOR_LIMIT and max(cD, cN) > INK_ABS_LIMIT):
                reasons.append("color")
            if chars is not None and o.get("_glyphs"):
                if i not in found:
                    reasons.append("missing")
                else:
                    geo = dict(geos.get(i) or {})
                    runs = [r for p in o["paragraphs"] for r in p if r["t"].strip()]
                    fr = font_ratio.get((runs[0]["font"], runs[0].get("bold"))) if runs else None
                    if fr and geo.get("scale") is not None:
                        geo["scale"] = round(geo["scale"] / fr, 4)
                    hr = font_hratio.get(runs[0]["font"]) if runs else None
                    if hr and geo.get("hscale") is not None:
                        geo["hscale"] = round(geo["hscale"] / hr, 4)
                    row.update(geo)
                    if geo.get("lines_native", 0) > geo.get("lines_design", 99):
                        reasons.append("lines")
                    # protected casing ("TaaS" in an all-caps line) is narrower on purpose
                    if o.get("_cased"):
                        geo["scale"] = None
                    if (geo.get("scale") is not None and abs(geo["scale"] - 1) > SCALE_LIMIT) or \
                            (geo.get("scale") is None and geo.get("hscale") is not None
                             and abs(geo["hscale"] - 1) > HEIGHT_LIMIT):
                        reasons.append("size")
                    if (geo.get("offset_x") is not None and abs(geo["offset_x"]) > TEXT_SHIFT_X) or \
                            abs(geo.get("offset_y") or 0) > TEXT_SHIFT_Y:
                        reasons.append("position")
            elif ink_rel > INK_REL_LIMIT and abs(cD - cN) > INK_ABS_LIMIT:
                reasons.append("ink")
        else:
            # Softened and edge maps are made before the text is cut out, so
            # the cut-out's border doesn't read as an edge.
            soft = _blur(_weights(D, bg))
            shift, res0, res = _align(soft, native, r, bg, mask) if (cD > 0 or cN > 0) \
                else (0.0, 0.0, 0.0)
            if cD > 0 or cN > 0:
                shift = max(shift, _align(soft, native, r, bg, mask, edges=True)[0])
            row.update(shift=round(shift, 2), residual=round(res, 3))
            if color > COLOR_LIMIT and not o.get("_flattened"):
                reasons.append("color")
            if ink_rel > INK_REL_LIMIT and abs(cD - cN) > INK_ABS_LIMIT:
                reasons.append("ink")
            if shift > SHIFT_LIMIT:
                reasons.append("position")
            if res > RESIDUAL_LIMIT and max(cD, cN) > INK_ABS_LIMIT:
                reasons.append("shape")
        row["fired"] = reasons
        rows.append(row)
    return rows
