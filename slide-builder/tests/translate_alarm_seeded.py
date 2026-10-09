#!/usr/bin/env python3
"""translate_alarm_seeded.py — does the alarm catch defects we plant?

Takes real designs from replay work dirs, translates each, then plants ONE
realistic defect in one visible element (moved, resized, recolored, deleted,
wrong weight, squeezed so it wraps, misaligned, ...). Every planted slide is
rendered (--engine; PowerPoint by default on Windows) and the alarm is run against the untouched design.
A defect counts as caught when the alarm fires on that exact element.

A plant that changes nothing visible (fading a white card on a white page) is
not counted. Bold flipped is reported on its own: at body sizes the two
renderers differ by as much as regular vs bold, so weight is guarded by a
direct test of the font choice instead (run_translate_smoke).

The go/no-go bar: at least 19 of 20 visible defects caught (95%).

  py -3 tests/translate_alarm_seeded.py --work <replay dir> [--per 2] [--seed 1] [--engine powerpoint]
Writes <work>/alarm_seeded.json.
"""
from __future__ import annotations

import argparse
import copy
import json
import random
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402

import translate_alarm as A  # noqa: E402
from translate_alarm_calibrate import plans_for  # noqa: E402
import translate_html as T  # noqa: E402
from twins.html_emit import build  # noqa: E402


def _visible(o, design) -> bool:
    """Is there something to see in this element's box in the design?"""
    r = A.region(o)
    if r is None:
        return False
    x0, y0, x1, y1 = r
    if o["op"] == "shape" and (o["w"] * o["h"] < 60 or o.get("alpha", 1) < 0.5):
        return False
    if o["op"] == "text" and not any(rr["t"].strip() for p in o["paragraphs"] for rr in p):
        return False
    D = design[y0:y1, x0:x1]
    ring = np.concatenate([D[0], D[-1], D[:, 0], D[:, -1]])
    return float(np.linalg.norm(D - np.median(ring, 0), axis=2).mean()) > 6


def _runs(o):
    return [r for p in o["paragraphs"] for r in p]


def _far_color(hexcol: str | None) -> str:
    if not hexcol:
        return "C00000"
    v = int(hexcol, 16)
    r, g, b = v >> 16, (v >> 8) & 255, v & 255
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return "C00000" if lum < 128 and r < 150 else ("1F4E79" if lum >= 128 else "E8A33D")


# (name, applies to, mutate(op) -> op or None for delete)
def _shift(dx, dy):
    def f(o):
        if o["op"] in ("connector", "freeform"):
            o["points"] = [[p[0] + dx, p[1] + dy] for p in o["points"]]
        else:
            o["x"] += dx
            o["y"] += dy
        return o
    return f


def _scale_font(k):
    def f(o):
        for r in _runs(o):
            r["size_px"] *= k
        return o
    return f


def _recolor_text(o):
    for r in _runs(o):
        r["color"] = _far_color(r.get("color"))
    return o


def _toggle_bold(o):
    for r in _runs(o):
        r["bold"] = not r["bold"]
    return o


def _squeeze(o):
    o["w"] *= 0.55
    o["wrap"] = True
    return o


def _center(o):
    o["align"] = "center" if o["align"] != "center" else "left"
    return o


def _spacing(o):
    for r in _runs(o):
        r["letter_spacing_px"] = (r.get("letter_spacing_px") or 0) + 3
    return o


def _refill(o):
    o["fill"] = _far_color(o.get("fill"))
    return o


def _shrink(o):
    o["w"] *= 0.7
    return o


def _fade(o):
    o["alpha"] = 0.3
    return o


DEFECTS = [
    ("text moved right 12px", "text", _shift(12, 0)),
    ("text moved down 10px", "text", _shift(0, 10)),
    ("text 30% larger", "text", _scale_font(1.3)),
    ("text 25% smaller", "text", _scale_font(0.75)),
    ("text wrong color", "text", _recolor_text),
    ("text missing", "text", lambda o: None),
    ("text bold flipped", "text", _toggle_bold),
    ("text box squeezed (extra lines)", "text", _squeeze),
    ("text alignment flipped", "text", _center),
    ("text letter spacing +3px", "text", _spacing),
    ("shape wrong fill", "shape", _refill),
    ("shape missing", "shape", lambda o: None),
    ("shape moved 12px", "shape", _shift(12, 0)),
    ("shape moved down 10px", "shape", _shift(0, 10)),
    ("shape 30% narrower", "shape", _shrink),
    ("shape faded", "shape", _fade),
]


def _applies(kind, o, design) -> bool:
    if o["op"] != kind:
        return False
    if not _visible(o, design):
        return False
    if kind == "text":
        r = A.region(o)
        ink_w = (o.get("_ink") or (0, 0, o["w"], 0))[2]
        name = None
        return r is not None and ink_w > 8 and name is None
    if kind == "shape":
        return o.get("fill") is not None and o["w"] >= 6 and o["h"] >= 2
    return True


def _meaningful(defect, o) -> bool:
    """Skip plants that don't change what's drawn (center-aligning text that
    already fills its box; squeezing a one-word label)."""
    if defect == "text alignment flipped":
        ink_w = (o.get("_ink") or (0, 0, o["w"], 0))[2]
        return o["w"] - ink_w > 40
    if defect == "text box squeezed (extra lines)":
        txt = " ".join(r["t"] for r in _runs(o))
        return len(txt.split()) >= 4
    if defect == "shape moved 12px" or defect == "shape 30% narrower":
        return o["w"] >= 20
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, type=Path, action="append")
    ap.add_argument("--per", type=int, default=2, help="defects planted per design")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--engine", default="auto", choices=("auto", "libreoffice", "powerpoint"),
                    help="the program that renders (auto: PowerPoint on Windows when installed)")
    args = ap.parse_args(argv)
    rng = random.Random(args.seed)
    items = plans_for(args.work)
    rng.shuffle(items)

    plants, di = [], 0
    for k, (name, plan, design) in enumerate(items):
        for _ in range(args.per):
            for _ in range(len(DEFECTS)):
                dname, kind, fn = DEFECTS[di % len(DEFECTS)]
                di += 1
                cands = [i for i, o in enumerate(plan.ops)
                         if _applies(kind, o, design) and _meaningful(dname, o)]
                if cands:
                    break
            else:
                continue
            i = rng.choice(cands)
            pub = T._public_plan(plan)
            mutated = fn(copy.deepcopy(pub["ops"][i]))
            ops = [o for j, o in enumerate(pub["ops"]) if j != i] if mutated is None else \
                [mutated if j == i else o for j, o in enumerate(pub["ops"])]
            plants.append({"option": name, "defect": dname, "index": i, "k": k,
                           "element": plan.ops[i].get("name") or f"{plan.ops[i]['op']}#{i}",
                           "_ops": ops})

    # Render every planted slide and, to judge whether a plant shows at all,
    # the same slide untouched.
    with tempfile.TemporaryDirectory() as td:
        paths = []
        for k, (name, plan, design) in enumerate(items):
            prs, _ = build(T._public_plan(plan))
            paths.append(Path(td) / f"c{k:03d}.pptx")
            prs.save(str(paths[-1]))
        for k, p in enumerate(plants):
            prs, _ = build({"version": "seeded", "ops": p["_ops"]})
            paths.append(Path(td) / f"p{k:04d}.pptx")
            prs.save(str(paths[-1]))
        out = A.render_full(paths, engine=args.engine)
        engines = dict(A.LAST_RENDER_ENGINES)    # which program drew each page
    clean, planted = out[:len(items)], out[len(items):]

    rows = []
    for j, (p, got) in enumerate(zip(plants, planted)):
        name, plan, design = items[p["k"]]
        if not got or not clean[p["k"]]:
            rows.append({"option": p["option"], "defect": p["defect"], "result": "render failed"})
            continue
        native, chars = got
        # Visible at all? Strongly changed pixels near the element vs the clean render.
        x0, y0, x1, y1 = A.region(plan.ops[p["index"]])
        x0, y0, x1, y1 = max(0, x0 - 16), max(0, y0 - 16), min(A.W, x1 + 16), min(A.H, y1 + 16)
        diff = np.abs(native[y0:y1, x0:x1] - clean[p["k"]][0][y0:y1, x0:x1]).max(2)
        if int((diff > 60).sum()) < 20:
            rows.append({"option": p["option"], "defect": p["defect"], "result": "not visible"})
            continue
        res = A.compare(plan.ops, design, native, chars, engine=engines.get(len(items) + j))
        hit = next((r for r in res if r["i"] == p["index"]), None)
        ok = bool(hit and hit["fired"])
        rows.append({"option": p["option"], "defect": p["defect"], "element": p["element"],
                     "caught": ok, "fired": hit["fired"] if hit else None,
                     "numbers": {k: hit.get(k) for k in ("color", "ink_color", "ink_rel", "shift",
                                                          "residual", "scale", "hscale",
                                                          "offset_x", "offset_y")} if hit else None,
                     "also_fired": [r["name"] for r in res if r["fired"] and r["i"] != p["index"]]})
    judged = [r for r in rows if "caught" in r]
    weight = [r for r in judged if r["defect"] == "text bold flipped"]
    rest = [r for r in judged if r["defect"] != "text bold flipped"]
    summary = {"planted": len(plants), "visible": len(judged),
               "not_visible": sum(1 for r in rows if r.get("result") == "not visible"),
               "caught": sum(r["caught"] for r in judged),
               "rate": round(sum(r["caught"] for r in judged) / len(judged), 4) if judged else None,
               "rate_without_weight": round(sum(r["caught"] for r in rest) / len(rest), 4) if rest else None,
               "weight_caught": f"{sum(r['caught'] for r in weight)}/{len(weight)}"}
    by = {}
    for r in judged:
        b = by.setdefault(r["defect"], [0, 0])
        b[0] += r["caught"]; b[1] += 1
    summary["by_defect"] = {k: f"{v[0]}/{v[1]}" for k, v in sorted(by.items())}
    (args.work[0] / "alarm_seeded.json").write_text(json.dumps({"summary": summary, "rows": rows},
                                                               indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    for r in judged:
        if not r["caught"] and r["defect"] != "text bold flipped":
            print(f"  MISSED {r['option'][-22:]} {r['defect']} on {r.get('element')}: {r.get('numbers')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
