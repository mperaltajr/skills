#!/usr/bin/env python3
"""Smoke test: what the translator agent draws lands where the design stacks it.

The agent's code runs after the converter's plan is drawn, so every shape it
added landed on top of everything: an arrow drawn over its label (2026-10-12).
translate_html.py now records where each element left to the agent sits in
the stacking order, and the generated option_X_native.py calls
html_emit.restack_fallbacks after the agent's block. Everything here is made
up (a fictional growth chart), never client content.

  1. a curved arrow drawn under its label (the 10/12 case, a full-slide svg):
     the agent's shape ends up under the label
  2. a drawing that is on top in the design stays on top
  3. two elements: shapes named <id> / <id>-N go to their own places; a
     shape named after neither stops the script with the fix
  4. running restack again changes nothing
  5. a script written before this (no restack call, its own addprevious)
     builds exactly as written
  6. every plan step draws exactly one top-level shape (table, list, icon,
     picture, text, shapes)

Needs Playwright's Chromium (no renderer: the self-check is skipped).
Run:  py -3 slide-builder/tests/run_fallback_stacking_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))

import translate_html as T  # noqa: E402
from twins import html_emit  # noqa: E402

HEAD = """<!doctype html><html><head><meta charset="utf-8"><style>
body { margin: 0; }
.slide-canvas { position: relative; width: 1280px; height: 720px; background: #fff;
  font-family: Arial, sans-serif; color: #1a1a1a; overflow: hidden; }
.abs { position: absolute; }
.label { position: absolute; left: 300px; top: 400px; width: 260px; height: 36px; background: #2f5d8a;
  color: #fff; font-size: 16px; line-height: 36px; text-align: center; }
.bar { position: absolute; left: 700px; top: 300px; width: 80px; height: 300px; background: #c8d6e5; }
</style></head><body><div class="slide-canvas">
<div class="abs" data-template-field="title" style="left:53px;top:40px;font-size:32px">Orders grew every quarter</div>
"""
CURVE = ('<svg class="abs" data-shape-id="{id}" style="left:0;top:0;width:1280px;height:720px" '
         'width="1280" height="720"><path d="M150 560 C 300 300, 450 300, 640 330" fill="none" '
         'stroke="#2f5d8a" stroke-width="3"/></svg>\n')
LABEL = '<div class="label" data-shape-id="growth-label">Orders up about 40%</div>\n'
BAR = '<div class="bar" data-shape-id="q4-bar"></div>\n'
TAIL = "</div></body></html>"

AGENT = '''    from pptx.util import Emu
    for n, name in enumerate({names}):
        b = slide.shapes.build_freeform(Emu(150 * 9525), Emu((560 - n) * 9525), scale=1.0)
        b.add_line_segments([(Emu(400 * 9525), Emu(330 * 9525)), (Emu(640 * 9525), Emu(330 * 9525))],
                            close=False)
        sh = b.convert_to_shape()
        sh.name = name
'''


def _convert(td: Path, body: str, tag: str) -> Path:
    d = td / tag
    d.mkdir()
    html = d / "option_A.html"
    html.write_text(HEAD + body + TAIL, encoding="utf-8")
    T.translate_many([(html, d, "A", True)], check=False)
    return d


def _draw(d: Path, names: list[str]) -> subprocess.CompletedProcess:
    """Play the agent: draw shapes named `names` in the fallback block, mark done, run."""
    npy = d / "option_A_native.py"
    src = npy.read_text(encoding="utf-8")
    assert "restack_fallbacks(slide, PLAN)" in src, "the template must call restack_fallbacks"
    assert src.index("# --- END FALLBACK ELEMENTS ---") < src.index("restack_fallbacks(slide, PLAN)")
    src = src.replace("    # (none)\n", AGENT.format(names=names), 1)
    src = src.replace("# FALLBACK_PENDING:", "# FALLBACK_DONE: drew the curves #", 1)
    npy.write_text(src, encoding="utf-8")
    return subprocess.run([sys.executable, str(npy)], cwd=str(d), capture_output=True, text=True)


def _order(d: Path) -> list[str]:
    from pptx import Presentation
    prs = Presentation(str(d / "option_A_native.pptx"))
    return [s.name for s in prs.slides[0].shapes]


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        print("[1] a curved arrow under its label")
        d = _convert(td, CURVE.format(id="growth-arrow") + LABEL, "under")
        plan = json.loads((d / "option_A_native.plan.json").read_text(encoding="utf-8"))
        fb, = plan["fallbacks"]
        assert fb["id"] == "growth-arrow" and fb["draw_under"] == "growth-label", fb
        rep = json.loads((d / "option_A_translation_report.json").read_text(encoding="utf-8"))
        assert rep["fallback"][0]["draw_under"] == "growth-label", rep["fallback"]
        head = (d / "option_A_native.py").read_text(encoding="utf-8")
        assert "#   growth-arrow: name its shapes growth-arrow" in head, head[:600]
        r = _draw(d, ["growth-arrow"])
        assert r.returncode == 0, r.stderr
        order = _order(d)
        assert order.index("growth-arrow") < order.index("growth-label"), order
        print("    ok: drawn under the label", order)

        print("[2] a drawing on top in the design stays on top")
        d = _convert(td, LABEL + CURVE.format(id="top-arrow"), "top")
        plan = json.loads((d / "option_A_native.plan.json").read_text(encoding="utf-8"))
        assert plan["fallbacks"][0]["draw_under"] is None and \
            plan["fallbacks"][0]["draw_after_n"] is None, plan["fallbacks"]
        r = _draw(d, ["anything"])           # one element: every new shape is its
        assert r.returncode == 0, r.stderr
        order = _order(d)
        assert order[-1] == "anything", order
        print("    ok: still on top")

        print("[3] two elements: names decide; a stray name stops the script")
        body = CURVE.format(id="arrow-a") + BAR + CURVE.format(id="arrow-b") + LABEL
        d = _convert(td, body, "two")
        plan = json.loads((d / "option_A_native.plan.json").read_text(encoding="utf-8"))
        by = {f["id"]: f for f in plan["fallbacks"]}
        assert by["arrow-a"]["draw_under"] == "q4-bar" and by["arrow-b"]["draw_under"] == "growth-label", by
        r = _draw(d, ["arrow-b-1", "arrow-a", "arrow-b-2"])
        assert r.returncode == 0, r.stderr
        order = _order(d)
        assert order.index("arrow-a") < order.index("q4-bar") < order.index("arrow-b-1") \
            < order.index("arrow-b-2") < order.index("growth-label"), order
        print("    ok:", order)
        d2 = _convert(td, body, "stray")
        r = _draw(d2, ["arrow-a", "my-curve"])
        assert r.returncode != 0 and "STOP" in r.stderr and "my-curve" in r.stderr \
            and "shape.name" in r.stderr, (r.returncode, r.stderr[-800:])
        print("    ok: a stray name stops with the fix")

        print("[4] restack again: nothing moves")
        from pptx import Presentation  # noqa: F401
        plan = json.loads((d / "option_A_native.plan.json").read_text(encoding="utf-8"))
        prs, slide = html_emit.build(plan)
        for name in ("arrow-a", "arrow-b"):
            sh = slide.shapes.add_shape(1, 0, 0, 9525, 9525)
            sh.name = name
        html_emit.restack_fallbacks(slide, plan)
        once = [s.name for s in slide.shapes]
        html_emit.restack_fallbacks(slide, plan)
        assert [s.name for s in slide.shapes] == once, once
        print("    ok: same order")

        print("[5] a script from before this builds as written")
        d = _convert(td, CURVE.format(id="old-arrow") + LABEL, "old")
        npy = d / "option_A_native.py"
        src = npy.read_text(encoding="utf-8")
        src = src.replace("from twins.html_emit import build, restack_fallbacks", "from twins.html_emit import build")
        src = src.replace("    # Puts the agent's shapes where the design stacks them (by their names).\n"
                          "    restack_fallbacks(slide, PLAN)\n", "")
        src = src.replace("    # (none)\n", AGENT.format(names=["old-arrow"]) +
                          "    label = [s for s in slide.shapes if s.name == 'growth-label'][0]\n"
                          "    slide.shapes._spTree.remove(sh._element)\n"
                          "    slide.shapes._spTree.append(sh._element)\n", 1)
        src = src.replace("# FALLBACK_PENDING:", "# FALLBACK_DONE: old style #", 1)
        npy.write_text(src, encoding="utf-8")
        r = subprocess.run([sys.executable, str(npy)], cwd=str(d), capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        order = _order(d)
        assert order[-1] == "old-arrow", order           # its own choice, untouched
        print("    ok: untouched")

        print("[6] every plan step draws exactly one top-level shape")
        from PIL import Image
        Image.new("RGB", (40, 30), (120, 150, 180)).save(td / "pic.png")
        body = ('<table class="abs" data-shape-id="t" style="left:60px;top:150px;border-collapse:collapse">'
                '<tr><td style="padding:6px;border-bottom:1px solid #999">A</td><td style="padding:6px">1</td></tr>'
                '<tr><td style="padding:6px">B</td><td style="padding:6px">2</td></tr></table>'
                '<ul class="abs" data-shape-id="l" style="left:400px;top:150px;margin:0;font-size:16px">'
                '<li>One point</li><li>Another point</li></ul>'
                f'<img class="abs" data-shape-id="p" src="{(td / "pic.png").as_uri()}" '
                'style="left:800px;top:150px;width:80px;height:60px;border-radius:50%;object-fit:cover">'
                '<svg class="abs" style="left:900px;top:300px" width="100" height="40"><line x1="0" y1="20" '
                'x2="100" y2="20" stroke="#333" stroke-width="2"/><circle cx="50" cy="20" r="6" fill="#333"/></svg>'
                + BAR + LABEL)
        d = _convert(td, body, "steps")
        plan = json.loads((d / "option_A_native.plan.json").read_text(encoding="utf-8"))
        prs, slide = html_emit.build(plan)
        steps = slide.part._slidelab_plan_shapes
        assert len(steps) == len(plan["ops"]) and all(len(s) == 1 for s in steps), \
            [(o["op"], len(s)) for o, s in zip(plan["ops"], steps)]
        kinds = {o["op"] for o in plan["ops"]}
        assert {"table", "text", "picture", "shape", "connector"} <= kinds, kinds
        print(f"    ok: {len(steps)} steps, kinds {sorted(kinds)}")
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
