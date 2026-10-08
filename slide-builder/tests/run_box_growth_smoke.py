#!/usr/bin/env python3
"""Smoke test: the converter's box growth no longer pushes thin boxes into each other.

To keep text off a box's bottom edge the converter grew any filled box whose
text sat close to that edge, without looking at what was below. Thin stacked
boxes always qualified, so each grew into the next, and the self-check (run
after the growth, against the approved design) read every grown box as drawn
wrong and sent it to the slow agent: 21 elements on one real slide
(2026-10-08). Owner's rule: grow only into empty space, by a few px, keeping
a gap to the next shape, and grow after the self-check.

On a made-up tight stack of thin solid and dashed boxes, plus one box with
room below:
  - 0 elements go to the agent (the self-check compares the design as drawn)
  - no finished box overlaps its neighbor, and each keeps a gap
  - a box with empty space below still grows

Needs Playwright's Chromium and LibreOffice, like the other render smokes.
Run:  py -3 slide-builder/tests/run_box_growth_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(SKILL.parent / "slide-qc" / "scripts"))

import translate_html as T  # noqa: E402

LABELS = ["Planning and review", "Supplier catalog", "Agency fees", "Plan design",
          "Processing", "Rate cards", "Relocation", "Program spend", "Survey tools",
          "Checks and audits", "Events budget", "Travel fees", "Coaching", "Starter kits"]
TOP, PITCH, LEAF_H = 150, 21, 20


def _page() -> str:
    rows = []
    for i, label in enumerate(LABELS):
        cls = "dash" if i % 2 else "solid"
        rows.append(f'<div class="t leaf {cls}" data-shape-id="leaf-{i + 1}" '
                    f'style="top:{TOP + i * PITCH}px">{label}</div>')
    # one box with plenty of room below it
    rows.append('<div class="t roomy solid" data-shape-id="roomy" style="top:150px">'
                'Room below this one</div>')
    return """<!doctype html><html><head><meta charset="utf-8"><style>
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
.slide-canvas { position: relative; width: 1280px; height: 720px; background: #FFFFFF;
  overflow: hidden; font-family: Arial; }
.t { position: absolute; display: flex; align-items: center; white-space: nowrap;
  font-family: Arial; font-size: 16px; line-height: 20px; color: #1A1A1A; padding: 0 12px; }
.leaf { left: 640px; width: 480px; height: 20px; }
.roomy { left: 120px; width: 380px; height: 20px; }
.solid { background: #F2F0F8; border: 1px solid #D8D2EA; border-radius: 2px; }
.dash { background: #FFFFFF; border: 1.25px dashed #9C90C0; border-radius: 2px; }
</style></head><body><div class="slide-canvas">
""" + "\n".join(rows) + "\n</div></body></html>"


def _outer(op: dict) -> tuple[float, float, float, float]:
    lw = ((op.get("line") or {}).get("w") or 0) / 2
    return op["x"] - lw, op["y"] - lw, op["x"] + op["w"] + lw, op["y"] + op["h"] + lw


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        html = td / "option_A.html"
        html.write_text(_page(), encoding="utf-8")
        rep = T.translate_many([(html, td, "A", True)])[0]
        plan = json.loads((td / "option_A_native.plan.json").read_text(encoding="utf-8"))

    print("[1] nothing goes to the agent")
    assert rep["self_check"]["ran"], rep["self_check"]
    assert rep["fallback"] == [], [f["id"] + ": " + f["reason"] for f in rep["fallback"]]
    print(f"    ok: 0 elements to the agent ({len(LABELS)} stacked boxes, half dashed)")

    print("[2] no finished box overlaps its neighbor")
    boxes = {o["name"]: o for o in plan["ops"] if o.get("op") == "shape" and o.get("name")}
    for i in range(1, len(LABELS)):
        a, b = _outer(boxes[f"leaf-{i}"]), _outer(boxes[f"leaf-{i + 1}"])
        assert a[3] <= b[1] + 0.01, f"leaf-{i} bottom {a[3]:.2f} runs into leaf-{i + 1} top {b[1]:.2f}"
    tallest = max(_outer(boxes[f"leaf-{i}"])[3] - _outer(boxes[f"leaf-{i}"])[1]
                  for i in range(1, len(LABELS)))
    assert tallest <= LEAF_H + 0.01, f"a stacked box grew to {tallest:.2f}px with no room"
    print("    ok: every stacked box stays inside its own row")

    print("[3] a box with room below still grows, keeping a gap")
    r = _outer(boxes["roomy"])
    assert r[3] - r[1] > LEAF_H + 0.5, f"the roomy box did not grow ({r[3] - r[1]:.2f}px)"
    assert r[3] - r[1] <= LEAF_H + 6.01, r
    assert rep["counts"]["boxes_grown_for_clearance"] >= 1, rep["counts"]
    print(f"    ok: grew from {LEAF_H}px to {r[3] - r[1]:.1f}px; "
          f"{rep['counts'].get('boxes_kept_no_room', 0)} box(es) kept their size for lack of room")

    print("[4] growth stops short of a neighbor below, by the gap")
    p = T.Plan()
    p.ops = [
        {"op": "shape", "x": 0, "y": 0, "w": 100, "h": 20, "_box": (0, 0, 100, 20),
         "_filled": True, "_order": 0},
        {"op": "text", "x": 5, "y": 2, "w": 80, "h": 18, "align": "left",
         "_ink": (5, 4, 60, 15), "_order": 1},
        {"op": "shape", "x": 0, "y": 24, "w": 100, "h": 20, "_box": (0, 24, 100, 20),
         "_filled": True, "_order": 2},
    ]
    T._apply_clearance(p)
    assert abs(p.ops[0]["h"] - (24 - T.CLEARANCE_GAP_PX)) < 0.01, p.ops[0]
    print(f"    ok: 4px of space below -> grew {p.ops[0]['h'] - 20:.0f}px, "
          f"{T.CLEARANCE_GAP_PX:.0f}px gap kept")

    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
