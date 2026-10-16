#!/usr/bin/env python3
"""check_visual_type.py: does each design show the visual the user chose?

Owner's decision (2026-10-16): a slide marked "Must use" on the Storyline tab
that comes back as another kind of visual is redone automatically before the
user sees the designs. This reads, per option:

  - the designer's tag: `data-visual="<name>"` on the sketch canvas, or the
    `# Visual: <name>` header line of a direct-path script (and the older
    `data-visual-form` when there is no tag);
  - simple signals on the page: a <table>, a chart <svg>, an <img> (on a
    script: add_table, add_chart, add_picture).

A Must use slide fails when the tag names another visual, when the page lacks
what that visual needs (a table needs a table, a chart a chart, a photo a
picture), or when there is no tag and the signals do not show it. A
suggestion is only reported ("follows it" / "does not", with the designer's
reason).

build_review.py runs this before it shows the designs: a failed Must use
slide is prepped again (build_deck.py --slide N, the reason in
slide_NN/_prior_feedback.md) once; the parent sends its worker, renders it and
runs build_review.py again. A second miss is shown on the card instead.

  py -3 scripts/check_visual_type.py --out <build>
Exit: 0 every Must use slide follows its visual | 1 at least one does not | 2 bad usage
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _paths as _p  # noqa: E402
import _visuals as V  # noqa: E402

TAG_RE = re.compile(r"""data-visual\s*=\s*["']([^"']+)["']""", re.I)
WHY_RE = re.compile(r"""data-visual-why\s*=\s*["']([^"']+)["']""", re.I)
FORM_RE = re.compile(r"""data-visual-form\s*=\s*["']([^"']+)["']""", re.I)
PY_TAG_RE = re.compile(r"^#\s*Visual:\s*(.+?)\s*$", re.M | re.I)
PY_WHY_RE = re.compile(r"^#\s*Visual why:\s*(.+?)\s*$", re.M | re.I)
ICON_SVG_RE = re.compile(r"<i\b[^>]*data-icon-name[^>]*>.*?</i>", re.I | re.S)


def _signals_html(text: str) -> set[str]:
    body = ICON_SVG_RE.sub("", text)
    body = re.sub(r"<style\b.*?</style>|<script\b.*?</script>", "", body, flags=re.I | re.S)
    out = set()
    if re.search(r"<table\b", body, re.I) or re.search(r"""data-native\s*=\s*["']table""", body, re.I):
        out.add("table")
    for m in re.finditer(r"<svg\b.*?</svg>", body, re.I | re.S):
        s = m.group(0)
        # an arrow or a divider is not a chart: a chart has several bars, a
        # plotted line, or names itself a chart
        if (len(re.findall(r"<rect\b", s, re.I)) >= 3 or re.search(r"<polyline\b", s, re.I)
                or re.search(r"chart|axis|series|plot", s, re.I)):
            out.add("svg")
    # chart pieces drawn as boxes are named chart-... (prompt.md)
    if re.search(r"""data-shape-id\s*=\s*["']chart-""", body, re.I):
        out.add("svg")
    if re.search(r"<img\b", body, re.I):
        out.add("img")
    return out


def _signals_py(text: str) -> set[str]:
    out = set()
    if re.search(r"add_table\s*\(|native_table|\btable\(", text):
        out.add("table")
    if re.search(r"add_chart\s*\(|chart_data|XL_CHART_TYPE|bar_chart|line_chart", text):
        out.add("svg")
    if re.search(r"add_picture\s*\(|picture\(", text):
        out.add("img")
    return out


def read_option(path: Path) -> dict:
    """{tag, why, form, signals} for one option file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"tag": None, "why": "", "form": "", "signals": set()}
    if path.suffix.lower() == ".py":
        m = PY_TAG_RE.search(text[:3000])
        w = PY_WHY_RE.search(text[:3000])
        return {"tag": (m.group(1) if m else None), "why": (w.group(1) if w else ""),
                "form": "", "signals": _signals_py(text)}
    m = TAG_RE.search(text)
    w = WHY_RE.search(text)
    f = FORM_RE.search(text)
    return {"tag": (m.group(1) if m else None), "why": (w.group(1) if w else ""),
            "form": (f.group(1).strip().lower() if f else ""), "signals": _signals_html(text)}


def judge(wanted: str, opt: dict) -> tuple[bool | None, str]:
    """(follows, reason). None = cannot tell from the file."""
    if wanted == V.ANY:
        return True, "designer's choice"
    need = V.needed_signal(wanted)
    tag = V.canonical(opt.get("tag") or "") if opt.get("tag") else None
    if opt.get("tag") and not tag:
        return False, f"tagged \"{opt['tag']}\", which is not one of the visual names"
    if tag and tag != wanted:
        return False, f"the design is {tag}"
    if need and need not in opt["signals"]:
        what = {"table": "no table", "svg": "no chart", "img": "no picture"}[need]
        return False, (f"tagged {wanted} but the page has {what}" if tag
                       else f"the page has {what}")
    if tag == wanted:
        return True, "tagged " + wanted
    form = opt.get("form")
    if form:
        if form in V.forms_for(wanted):
            return True, f"its form is {form}"
        return False, f"its form is {form}"
    if need:
        return True, "the page has the " + {"table": "table", "svg": "chart", "img": "picture"}[need]
    return None, "no tag on the design, so it cannot be told from the file"


def option_files(slide_dir: Path, letters) -> list[tuple[str, Path]]:
    out = []
    for L in letters:
        for name in (f"option_{L}.html", f"option_{L}.py"):
            f = slide_dir / name
            if f.exists():
                out.append((L, f))
                break
    return out


def check(out_dir: Path, meta: dict | None = None) -> list[dict]:
    """One entry per slide with a recorded visual: {n, wanted, lock, options:
    [{letter, follows, reason, why}], mismatch (a Must use option that does
    not follow)}."""
    if meta is None:
        try:
            meta = json.loads(_p.meta_json(out_dir).read_text(encoding="utf-8"))
        except Exception:
            return []
    res = []
    for s in meta.get("slides") or []:
        vis = s.get("visual") or {}
        if not vis.get("name") or not isinstance(s.get("n"), int):
            continue
        sd = _p.slide_dir(out_dir, s["n"])
        letters = s.get("options") or list(_p.option_letters())
        opts = []
        for L, f in option_files(sd, letters):
            o = read_option(f)
            ok, why = judge(vis["name"], o)
            opts.append({"letter": L, "follows": ok, "reason": why, "why": o.get("why") or "",
                         "tag": o.get("tag")})
        firm = vis.get("lock") == "must use"
        res.append({"n": s["n"], "wanted": vis["name"], "lock": vis.get("lock", "suggestion"),
                    "options": opts,
                    "mismatch": firm and any(o["follows"] is False for o in opts)})
    return res


def card_line(entry: dict | None) -> str:
    """The line on the design card: "You picked: <visual> (<lock>). Design
    follows it / does not ..."."""
    if not entry:
        return ""
    head = f"You picked: {entry['wanted']} ({entry['lock']})."
    if entry["wanted"] == V.ANY:
        return f"You picked: {V.ANY}."
    bits = []
    multi = len(entry["options"]) > 1
    for o in entry["options"]:
        who = f"Option {o['letter']} " if multi else "Design "
        if o["follows"] is True:
            bits.append(who + "follows it.")
        elif o["follows"] is False:
            bits.append(who + f"does not ({o['reason']})"
                        + (f"; the designer's reason: {o['why']}" if o["why"] else "") + ".")
        else:
            bits.append(who + "cannot be checked (it has no visual tag); look at it.")
    return head + " " + " ".join(bits)


def write_redo_feedback(out_dir: Path, entry: dict) -> Path:
    sd = _p.slide_dir(out_dir, entry["n"])
    sd.mkdir(parents=True, exist_ok=True)
    fb = sd / "_prior_feedback.md"
    bad = "; ".join(f"option {o['letter']}: {o['reason']}" for o in entry["options"]
                    if o["follows"] is False)
    note = (f"\n\n## Wrong kind of visual (checked automatically)\n\nThe user chose "
            f"**{entry['wanted']}** on the Storyline tab and marked it **Must use**. The last "
            f"design did not follow it ({bad}). Draw a {entry['wanted']} this time, and tag it "
            f"data-visual=\"{entry['wanted']}\" (or `# Visual: {entry['wanted']}`).\n")
    old = fb.read_text(encoding="utf-8") if fb.exists() else "# Prior feedback\n"
    fb.write_text(old.rstrip() + note, encoding="utf-8")
    return fb


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check each design's visual against the user's choice.")
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    res = check(a.out)
    if not res:
        print("No slide has a visual recorded (no Storyline tab choices); nothing to check.")
        return 0
    for e in res:
        print(f"  slide {e['n']}: {card_line(e)}" + ("  <- MUST USE, redo" if e["mismatch"] else ""))
    bad = [e["n"] for e in res if e["mismatch"]]
    if bad:
        print(f"Must use visual not followed on slide(s) {', '.join(map(str, bad))}. "
              "build_review.py redoes them before it shows the designs.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
