"""Slide Lab v2 deck compiler — combine user-picked themed slides into one final deck.

True near-verbatim fork from slide-builder/scripts/compile_picks.py. The only
v2-specific change is the sys.path setup: v2 doesn't carry its own twins/
module, so we point at slide-builder/'s shared infrastructure explicitly.

Inputs:
  --out PATH    Orchestrator output dir (the one that has _meta.json, slide_NN/ dirs, etc.)
  --picks       Either a JSON file path OR a JSON string mapping slide_NN -> letter.
                Example string: {"slide_01":"A","slide_02":"C",...}
                If omitted, reads <out>/picks.json if present.
  --final PATH  Final deck path (default: <out>/final_deck.pptx)

What it does (unchanged from v1):
  1. Open the client template (path from <out>/_meta.json).
  2. _clear_existing_slides() — strip template stock slides + named sections.
  3. For each slide in numeric order, open <out>/slide_NN/option_<X>.pptx
     and copy its single slide's shapes into a new blank slide in the final deck
     (deepcopy(shape.element) + append to _spTree).
  4. Save to --final.
  5. Render every slide of the final deck to PNG via render_libre → output to
     <out>/final_pngs/.
  6. Write <out>/COMPILED.md summarizing picks, output path, slide count,
     render success/fail, opens-cleanly status.

The themed PPTX is already client-branded by finalize_deck.py — we do
NOT re-graft or re-theme here. Just combine. Mermaid-fallback options
were already assembled into themed PPTX at finalize time and look identical
to native options from this script's perspective.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import traceback
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Optional

# Path setup: twins/ is local to this skill (re-homed Phase 2 cleanup
# 2026-05-26); render_slides lives in the sibling slide-qc skill.
SKILL_ROOT = Path(__file__).resolve().parents[1]              # slide-builder/
QC_SCRIPTS = SKILL_ROOT.parent / "slide-qc" / "scripts"       # render_slides
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(QC_SCRIPTS))

import _paths as _p  # noqa: E402

from pptx import Presentation  # noqa: E402
from twins.composer import (  # noqa: E402
    _clear_existing_slides,
    _find_blank_layout,
    _strip_layout_placeholders,
)


# ---------------------------------------------------------------------------
# Pick parsing — unchanged from v1
# ---------------------------------------------------------------------------
def parse_picks(arg: Optional[str], out_dir: Path) -> dict[str, str]:
    """Resolve --picks. Accepts:
      - None             -> read <out>/picks.json
      - existing file    -> json.load
      - JSON string      -> json.loads
    Normalizes keys to 'slide_NN' (zero-padded) and uppercases letters.
    """
    if arg is None:
        candidate = _p.picks_json(out_dir)
        if not candidate.exists():
            raise SystemExit(f"--picks not given and {candidate} does not exist")
        raw = candidate.read_text(encoding="utf-8")
    else:
        as_path = Path(arg)
        if as_path.exists():
            raw = as_path.read_text(encoding="utf-8")
        else:
            raw = arg

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"--picks: invalid JSON ({e})")

    if not isinstance(data, dict):
        raise SystemExit(f"--picks: expected object, got {type(data).__name__}")

    normalized: dict[str, str] = {}
    for k, v in data.items():
        m = re.match(r"slide[_\-]?(\d+)", str(k), re.IGNORECASE)
        if not m:
            raise SystemExit(f"--picks: bad key {k!r}, expected like 'slide_01'")
        key = _p.slide_key(int(m.group(1)))
        letter = str(v).strip().upper()
        if not letter:
            raise SystemExit(f"--picks: empty letter for {key}")
        normalized[key] = letter
    return normalized


# ---------------------------------------------------------------------------
# Slide copying — unchanged from v1
# ---------------------------------------------------------------------------
def copy_picked_slide_into(dst_prs, src_pptx: Path) -> int:
    """Open `src_pptx`, append its first slide's shapes onto a new blank slide
    in `dst_prs`. Returns the shape count copied.
    """
    src_prs = Presentation(str(src_pptx))
    src_slide = src_prs.slides[0]

    blank = _find_blank_layout(dst_prs)
    new_slide = dst_prs.slides.add_slide(blank)
    _strip_layout_placeholders(new_slide)

    sp_tree = new_slide.shapes._spTree
    count = 0
    for shape in src_slide.shapes:
        sp_tree.append(deepcopy(shape.element))
        count += 1
    return count


# ---------------------------------------------------------------------------
# COMPILED.md — unchanged from v1
# ---------------------------------------------------------------------------
COMPILED_TEMPLATE = """# Slide Lab v2 compiled deck

Generated: {ts}

Out dir   : `{out}`
Template  : `{template}`
Final deck: `{final}`

## Picks

| Slide | Pick | Source PPTX | Shapes copied | Status |
|-------|------|-------------|---------------|--------|
{rows}

## Result

- Final slide count: **{slide_count}**
- Opens cleanly (python-pptx reload): **{opens}**
- Renders attempted: **{render_total}**
- Renders succeeded: **{render_ok}**
- Renders failed   : **{render_fail}**

## Failures

{failures}
"""


# ---------------------------------------------------------------------------
# Main — unchanged from v1 (only the header message changed for v2)
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Compile picked themed slides into a final deck.")
    ap.add_argument("--out", required=True, type=Path, help="Orchestrator output dir")
    ap.add_argument("--picks", default=None, help="picks.json path OR JSON string")
    ap.add_argument("--final", default=None, type=Path,
                    help="Final deck path (default: <out>/final_deck.pptx)")
    args = ap.parse_args()

    from _log import attach as _log_attach
    _log_attach(args.out, "compile_picks.py")

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    out_dir: Path = args.out
    if not out_dir.exists():
        print(f"ERROR: out dir not found: {out_dir}")
        return 2

    meta_path = _p.meta_json(out_dir)
    if not meta_path.exists():
        print(f"ERROR: _meta.json not found at {meta_path}")
        return 2
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    from _meta_schema import validate_warn
    validate_warn(meta, source="compile_picks")
    template_path = Path(meta["template"])
    if not template_path.exists():
        print(f"ERROR: template (from _meta.json) not found: {template_path}")
        return 2

    picks = parse_picks(args.picks, out_dir)
    final_path: Path = args.final or (out_dir / "final_deck.pptx")
    final_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("Slide Lab v2 deck compiler")
    print(f"  out      : {out_dir}")
    print(f"  template : {template_path}")
    print(f"  picks    : {len(picks)} entries")
    print(f"  final    : {final_path}")
    print("=" * 72)

    print("\n[1] Open template + clear existing slides + sections")
    dst_prs = Presentation(str(template_path))
    _clear_existing_slides(dst_prs)

    print("\n[2] Copy picked themed slides")
    rows: list[str] = []
    failures: list[str] = []
    ordered_keys = sorted(picks.keys(), key=lambda k: int(k.split("_")[1]))
    copied_count = 0
    for key in ordered_keys:
        letter = picks[key]
        src = out_dir / key / _p.option_pptx_name(letter)
        if not src.exists():
            msg = f"missing source: {src}"
            failures.append(f"- **{key} pick {letter}**: {msg}")
            rows.append(f"| {key} | {letter} | `{src.name}` | - | FAIL ({msg}) |")
            print(f"  {key} pick {letter}  FAIL ({msg})")
            continue
        try:
            n_shapes = copy_picked_slide_into(dst_prs, src)
            copied_count += 1
            rows.append(f"| {key} | {letter} | `{src.name}` | {n_shapes} | ok |")
            print(f"  {key} pick {letter}  ok (shapes={n_shapes})")
        except Exception as e:
            tb = traceback.format_exc().strip().splitlines()[-1]
            msg = f"{type(e).__name__}: {e} | {tb}"
            failures.append(f"- **{key} pick {letter}**: {msg}")
            rows.append(f"| {key} | {letter} | `{src.name}` | - | FAIL ({msg[:60]}...) |")
            print(f"  {key} pick {letter}  FAIL ({msg[:80]})")

    print(f"\n[3] Save final deck -> {final_path}")
    dst_prs.save(str(final_path))
    print(f"  saved ({final_path.stat().st_size:,} bytes)")

    print("\n[4] Verify opens cleanly")
    opens = False
    slide_count = 0
    try:
        verify = Presentation(str(final_path))
        slide_count = len(verify.slides)
        opens = True
        print(f"  ok - slide count = {slide_count}")
    except Exception as e:
        print(f"  FAIL: {type(e).__name__}: {e}")
        failures.append(f"- **reload**: {type(e).__name__}: {e}")

    print("\n[5] Render every slide to PNG")
    pngs_dir = out_dir / "final_pngs"
    render_total = 0
    render_ok = 0
    render_fail = 0
    try:
        from render_slides import render_libre
        render_libre(final_path, pngs_dir, dpi=120)
        pngs = sorted(pngs_dir.glob("slide_*.png"))
        render_total = max(slide_count, len(pngs))
        render_ok = len(pngs)
        render_fail = max(0, render_total - render_ok)
        print(f"  rendered {render_ok} png(s) into {pngs_dir}")
    except Exception as e:
        tb = traceback.format_exc().strip().splitlines()[-1]
        msg = f"{type(e).__name__}: {e} | {tb}"
        print(f"  FAIL: {msg}")
        failures.append(f"- **render**: {msg}")
        render_total = slide_count
        render_fail = slide_count

    print("\n[6] Write COMPILED.md")
    content = COMPILED_TEMPLATE.format(
        ts=datetime.now().isoformat(timespec="seconds"),
        out=out_dir,
        template=template_path,
        final=final_path,
        rows="\n".join(rows) if rows else "| (no picks) |",
        slide_count=slide_count,
        opens="yes" if opens else "NO",
        render_total=render_total,
        render_ok=render_ok,
        render_fail=render_fail,
        failures="\n".join(failures) if failures else "(none)",
    )
    compiled_md = out_dir / "COMPILED.md"
    compiled_md.write_text(content, encoding="utf-8")
    print(f"  {compiled_md}")

    print("\n" + "=" * 72)
    print("DONE - compile complete.")
    print(f"  Copied  : {copied_count} / {len(picks)}")
    print(f"  Opens   : {'yes' if opens else 'NO'}")
    print(f"  Slides  : {slide_count}")
    print(f"  Renders : {render_ok} / {render_total}")
    print(f"  Report  : {compiled_md}")
    print(f"  Deck    : {final_path}")
    print("=" * 72)

    return 0 if (opens and render_fail == 0 and not failures) else 1


if __name__ == "__main__":
    sys.exit(main())
