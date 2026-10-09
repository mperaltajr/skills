#!/usr/bin/env python3
"""translate_alarm_calibrate.py — how noisy is the alarm on good translations?

For every option in a replay work dir: translate the design, render it with
LibreOffice, and record the alarm's numbers per element. The limits in
scripts/translate_alarm.py sit just above this noise. Also writes, per option,
the elements that fired, so false alarms can be looked at.

  py -3 tests/translate_alarm_calibrate.py --work <replay work dir> [--work ...]
Writes <first work>/alarm_calibration.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))

import translate_html as T  # noqa: E402
import translate_alarm as A  # noqa: E402
from twins.html_emit import build  # noqa: E402


def plans_for(work_dirs: list[Path]):
    """(option name, plan, design array) for every option with a design."""
    from playwright.sync_api import sync_playwright
    out = []
    with sync_playwright() as pw:
        from _browser import launch
        br = launch(pw)
        page = br.new_page(viewport={"width": 1280, "height": 720})
        for w in work_dirs:
            for od in sorted(p for p in (w / "opts").iterdir() if p.is_dir()):
                html = next((od / "script").glob("option_?.html"), None)
                if not html:
                    continue
                data = T.extract(page, html, True)
                plan, _ = T.plan_from_extract(data, True)
                out.append((od.name, plan, A.load_rgb(data["_shot"])))
        br.close()
    return out


def build_all(items, tmp: Path) -> list[Path]:
    tmp.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, plan, _ in items:
        prs, _ = build(T._public_plan(plan))
        p = tmp / f"{name}.pptx"
        prs.save(str(p))
        paths.append(p)
    return paths


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, type=Path, action="append")
    args = ap.parse_args(argv)
    items = plans_for(args.work)
    natives = A.render_many(build_all(items, args.work[0] / "alarm_tmp"))
    rows, fired = [], {}
    for (name, plan, design), native in zip(items, natives):
        if native is None:
            print(f"  render failed: {name}")
            continue
        for r in A.compare(plan.ops, design, native):
            r["option"] = name
            rows.append(r)
            if r["fired"]:
                fired.setdefault(name, []).append(f"{r['name']} {r['fired']} color={r['color']} "
                                                  f"ink={r['ink_design']}->{r['ink_native']} "
                                                  f"shift={r['shift']}")

    def pct(key, q):
        v = sorted(r[key] for r in rows)
        return v[min(len(v) - 1, int(q * len(v)))] if v else None

    summary = {"options": len(items), "elements": len(rows),
               "options_with_alarm": len(fired),
               "elements_fired": sum(1 for r in rows if r["fired"]),
               "color_p95": pct("color", .95), "color_p99": pct("color", .99), "color_max": pct("color", 1),
               "shift_p95": pct("shift", .95), "shift_p99": pct("shift", .99), "shift_max": pct("shift", 1),
               "ink_rel_p95": pct("ink_rel", .95), "ink_rel_p99": pct("ink_rel", .99),
               "ink_color_p99": pct("ink_color", .99), "ink_color_max": pct("ink_color", 1),
               "residual_p95": pct("residual", .95), "residual_p99": pct("residual", .99),
               "residual_max": pct("residual", 1)}
    (args.work[0] / "alarm_calibration.json").write_text(
        json.dumps({"summary": summary, "fired": fired, "rows": rows}, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    for k, v in list(fired.items())[:30]:
        for line in v[:4]:
            print(f"  {k}: {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
