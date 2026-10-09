#!/usr/bin/env python3
"""translate_gonogo.py — is translate_html.py good enough to replace the agent?

Re-translates every option in one or more replay work dirs (made by
translate_replay.py, which also rendered the agent's version) with the CURRENT
script, renders all of them in one pass with the default renderer (PowerPoint
on Windows when installed; --engine picks one), and measures the bar the
script has to clear before settings.json can say "translator": "script":

  opens cleanly       0 PowerPoint openability problems
  no lost text        every character the design shows is in the slide
  fallback            at most 15% of options need the agent for any element
  same lines          at least 98% of text boxes break into as many lines as
                      the design, and no word is split mid-word
  alarm               how often the per-element self-check fires on real work

It also writes blind comparison sheets (design | X | Y, agent and script in
random order) for the side-by-side judgment, with the key kept separately.

  py -3 tests/translate_gonogo.py --out <dir> --work <replay dir> [--work ...]
Writes <out>/gonogo.json, <out>/blind/*.png, <out>/blind_key.json.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SKILL.parent / "slide-qc" / "scripts"))

import translate_html as T  # noqa: E402
import translate_alarm as A  # noqa: E402
from translate_replay import _norm_chars, pptx_text  # noqa: E402
from twins.html_emit import build  # noqa: E402

BREAKERS = " -/\u2013\u2014"   # a line may end after these without splitting a word


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--work", required=True, type=Path, action="append")
    ap.add_argument("--engine", default="auto", choices=("auto", "libreoffice", "powerpoint"),
                    help="The program that renders (auto: the default renderer, PowerPoint "
                         "on Windows when installed; safe with PowerPoint open).")
    args = ap.parse_args(argv)
    out = args.out
    (out / "pptx").mkdir(parents=True, exist_ok=True)
    (out / "blind").mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright
    from pptx import Presentation
    from pptx_openability import check_openability
    from PIL import Image

    items = []
    with sync_playwright() as pw:
        from _browser import launch
        br = launch(pw)
        page = br.new_page(viewport={"width": 1280, "height": 720})
        for w in args.work:
            for od in sorted(p for p in (w / "opts").iterdir() if p.is_dir()):
                html = next((od / "script").glob("option_?.html"), None)
                if not html:
                    continue
                res = {"key": od.name, "set": w.name}
                try:
                    data = T.extract(page, html, True)
                    plan, fields = T.plan_from_extract(data, True)
                    if any(f["kind"] == "canvas" for f in plan.fallbacks):
                        # older design, not on the 1280x720 canvas: all to the agent
                        res.update(old_canvas=True, open_issues=[], text_chars=0, text_missing=0,
                                   fallback=plan.fallbacks, warnings=[])
                        items.append((od, res, None, None, None))
                        continue
                    items.append((od, res, plan, None, data))
                except Exception as exc:
                    res["error"] = f"{type(exc).__name__}: {exc}"
                    items.append((od, res, None, None, None))
        br.close()

    # The converter's own self-check, as in a build: a native table or a
    # one-box list that renders differently steps down to its fallback and is
    # rendered again. Elements that would go to the agent are only recorded
    # (hand_over=False), so the text and line checks below see every element.
    live = [(plan, data) for od, res, plan, shot, data in items if plan is not None]
    T.self_check(live, engine=args.engine, hand_over=False)

    rng = random.Random(20261001)
    blind_key = {}
    line_total = line_match = 0
    mismatches, midword, alarms = [], [], []
    for od, res, plan, shot, data in items:
        if plan is None:
            continue
        prs, _ = build(T._public_plan(plan))
        pp = out / "pptx" / f"{od.name}.pptx"
        prs.save(str(pp))
        res["open_issues"] = [x["issue"][:120] for x in
                              check_openability(Presentation(str(pp)))]
        # Everything the design shows, by character count (so a field's
        # whitespace can't stop it being taken out), less the template's
        # fields (the graft draws those) and text the design itself hides
        # (covered or clipped).
        fields = {k: v for k, v in (data.get("fields") or {}).items() if k != "subtitle"}
        want = _norm_chars(data.get("visible_text", ""))
        for v in fields.values():
            want = want - _norm_chars(v or "")
        for t in data["texts"]:
            if t.get("covered") or t.get("clipped"):
                want = want - _norm_chars("".join(r.get("t", "") for r in t["runs"]))
        missing = want - _norm_chars(pptx_text(pp))
        # characters inside elements handed to the agent are its to draw
        res["text_in_agent_elements"] = bool(plan.fallbacks)
        res["text_chars"] = sum(want.values())
        res["text_missing"] = sum(missing.values())
        res["fallback"] = plan.fallbacks
        res["warnings"] = [x["code"] for x in plan.warnings]
        res["native"] = T.native_counts(plan)
        got = getattr(plan, "_last_render", None)
        if not got:
            res["error"] = "render failed" + (" (PowerPoint could not open or export it)"
                                              if args.engine == "powerpoint" else "")
            continue
        native, cs = got
        # same lines
        t, m, rows, mw = _lines(od, plan, cs)
        line_total += t; line_match += m; mismatches += rows; midword += mw
        # alarm: what the self-check would hand to the agent
        fired = plan.self_check.get("fired") or []
        res["alarm"] = [f"{r['element']} {r['what']}" for r in fired]
        alarms += [{"option": od.name, "name": r["element"], "fired": r["what"]} for r in fired]
        # blind sheet: design | X | Y
        agent_png = od / "render_agent" / "slide_01.png"
        if agent_png.exists():
            shot = A.load_rgb(data["_shot"])
            ims = {"design": Image.fromarray(shot.astype("uint8")),
                   "agent": Image.open(agent_png).convert("RGB").resize((1280, 720)),
                   "script": Image.fromarray(native.astype("uint8"))}
            order = ["agent", "script"]
            rng.shuffle(order)
            sheet = Image.new("RGB", (3840, 720), "white")
            for j, k in enumerate(["design"] + order):
                sheet.paste(ims[k], (1280 * j, 0))
            name = f"b{len(blind_key) + 1:03d}.png"
            sheet.resize((2400, 450)).save(out / "blind" / name)
            blind_key[name] = {"key": od.name, "X": order[0], "Y": order[1]}

    done = [r for _, r, plan, _, _ in items if "error" not in r]
    cur = [r for r in done if not r.get("old_canvas")]
    n = len(done)
    summary = {
        "options": len(items),
        "errors": len(items) - n,
        "open_failures": sum(1 for r in done if r["open_issues"]),
        "text_lost_options": sum(1 for r in done if r["text_missing"] > 0),
        "text_missing_chars": sum(r["text_missing"] for r in done),
        "text_total_chars": sum(r["text_chars"] for r in done),
        "old_canvas_options": sum(1 for r in done if r.get("old_canvas")),
        # In use, an element that trips the self-check also goes to the agent,
        # so "needs the agent" = a fallback element or a self-check hit.
        "needs_agent_options": sum(1 for r in done if r["fallback"] or r.get("alarm")),
        "needs_agent_rate": round(sum(1 for r in done if r["fallback"] or r.get("alarm")) / n, 4)
        if n else None,
        "needs_agent_rate_current_format": round(
            sum(1 for r in cur if r["fallback"] or r.get("alarm")) / len(cur), 4) if cur else None,
        "text_boxes": line_total,
        "same_lines_rate": round(line_match / line_total, 4) if line_total else None,
        "midword_breaks": len(midword),
        "alarm_options": sum(1 for r in done if r.get("alarm")),
        "alarm_elements": len(alarms),
        "warning_counts": dict(Counter(w for r in done for w in r["warnings"])),
        "native_table_options": sum(1 for r in done if (r.get("native") or {}).get("native_tables")),
        "native_tables": sum((r.get("native") or {}).get("native_tables", 0) for r in done),
        "single_box_list_options": sum(1 for r in done if (r.get("native") or {}).get("single_box_lists")),
        "single_box_lists": sum((r.get("native") or {}).get("single_box_lists", 0) for r in done),
    }
    (out / "gonogo.json").write_text(json.dumps(
        {"summary": summary, "line_mismatches": mismatches, "midword": midword,
         "alarms": alarms, "results": [r for _, r, *_ in items]}, indent=1), encoding="utf-8")
    (out / "blind_key.json").write_text(json.dumps(blind_key, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    for r in mismatches[:20]:
        print(f"  LINES {r['option']} [{r['id']}] design {r['design_lines']} vs "
              f"{r.get('pptx_lines', r.get('problem'))}: {r['text'][:50]}")
    for r in midword[:10]:
        print(f"  MID-WORD {r['option']} [{r['id']}]: {r['at']!r}")
    for r in alarms[:20]:
        print(f"  ALARM {r['option']} {r['name']} {r['fired']}")
    for r in done:
        if r["open_issues"] or r["text_missing"]:
            print(f"  {r['key']}: open={r['open_issues'][:1]} missing={r['text_missing']}")
    return 0


def _lines(od, plan, cs):
    """Do the text boxes break into the same lines as the design, and is any
    word split mid-word? Uses the alarm's own matching of text to the PDF."""
    ops, _owner = A.expand_ops(plan.ops)      # a table's cells count as text boxes
    found = A.match_text(ops, cs)
    total = match = 0
    rows, midword = [], []
    for i, o in enumerate(ops):
        if o["op"] != "text" or not o.get("_lines"):
            continue
        raw = A.op_text(o)
        if not raw.strip():
            continue
        total += 1
        if i not in found:
            rows.append({"option": od.name, "id": o.get("_id"), "problem": "text not found",
                         "design_lines": o["_lines"], "text": raw[:70]})
            continue
        keep = [k for k, ch in enumerate(raw) if not ch.isspace()]
        mine = [cs[k] for k in found[i]]
        brk = A.line_breaks(mine)
        for k in brk:
            prev = raw[keep[k - 1]]
            if not raw[keep[k - 1] + 1:keep[k]] and prev not in BREAKERS:
                midword.append({"option": od.name, "id": o.get("_id"),
                                "at": raw[max(0, keep[k - 1] - 10):keep[k] + 10]})
        if len(brk) + 1 == o["_lines"]:
            match += 1
        else:
            rows.append({"option": od.name, "id": o.get("_id"), "design_lines": o["_lines"],
                         "pptx_lines": len(brk) + 1, "text": raw[:70]})
    return total, match, rows, midword


if __name__ == "__main__":
    sys.exit(main())
