#!/usr/bin/env python3
"""source_ledger.py — reconcile the figures on a SUPPLIED page before it ships.

The problem this solves. When a user hands over a page to be reproduced (a
one-pager, a mockup), replicating it faithfully also replicates its numbers. In
a real build that shipped "$300B / 6-12 months / 3x" when the brief already
carried the verified "~$450B / sold out / ~4x". So the fix for "you dropped my
page" silently becomes "you shipped my stale numbers".

Why this is a LEDGER and not a differ. A differ would compare each figure on the
page against the brief and pass or fail. It cannot: the brief has no typed
numeric field, only prose, so deciding that "6-12 months" and "sold out" denote
the same quantity is a semantic judgment the machine does not own. A differ that
reported "0 conflicts" would be asserting exactly that judgment, and the rest of
the pipeline would consume it as a recorded fact. That is false assurance, which
is a worse failure than the one we started with.

So the machine records only what it genuinely knows: *this figure-bearing slot
has not been resolved by a human*. Each slot takes exactly one of:

    bind_from_brief   the value comes from the brief, not the source page
    keep_source       the human states this source value is still correct
    replace_with      the human supplies a value

`null` is not a resolution. Unresolved slots block the compile.

Only figure-bearing slots are listed. A dense one-pager has 30-40 text surfaces;
prompting on all of them produces a bulk-accept reflex, which is how always-on
signals went blind in this pipeline before.

Run:
  py -3 scripts/source_ledger.py build  --out <out> --deck <page.pptx> --slide N
  py -3 scripts/source_ledger.py status --out <out>
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _extract  # noqa: E402
import _paths as _p  # noqa: E402
import _state  # noqa: E402

from pptx import Presentation  # noqa: E402

LEDGER_NAME = "source_ledger.json"
RESOLUTIONS = ("bind_from_brief", "keep_source", "replace_with")


def ledger_path(out_dir: Path) -> Path:
    return Path(out_dir) / LEDGER_NAME


def _load(out_dir: Path) -> dict:
    p = ledger_path(out_dir)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def tally(ledger: dict) -> tuple[int, int, int]:
    """Return (unresolved, keep_source, total) over the ledger's rows."""
    rows = ledger.get("rows", []) or []
    unresolved = sum(1 for r in rows if r.get("resolution") not in RESOLUTIONS)
    # replace_with without a replacement is not resolved either.
    unresolved += sum(1 for r in rows
                      if r.get("resolution") == "replace_with"
                      and not str(r.get("replacement") or "").strip())
    keeps = sum(1 for r in rows if r.get("resolution") == "keep_source")
    return unresolved, keeps, len(rows)


def _write_brief_qc(out_dir: Path, ledger: dict) -> None:
    """Render the ledger into the brief_qc.json shape REVIEW.html already reads.

    build_review has rendered this banner for a long time with no writer (the
    path is an accepted orphan in the manifest). This is that writer.
    """
    unresolved, keeps, total = tally(ledger)
    unreachable = ledger.get("unreachable", []) or []
    blocking, warnings = [], []
    for r in ledger.get("rows", []):
        if r.get("resolution") not in RESOLUTIONS or (
                r.get("resolution") == "replace_with"
                and not str(r.get("replacement") or "").strip()):
            blocking.append(
                f"slide {r.get('slide')} {r.get('addr')}: {r.get('source_text')!r} "
                f"carried from the supplied page and not yet reconciled")
    for u in unreachable:
        warnings.append(f"{u.get('addr')}: {u.get('why')} — NOT checked; "
                        f"the vision pass is responsible for this surface")
    # Deliberately never a green "0 conflicts": silence must not read as a pass.
    summary = (f"Supplied page: {total} figure-bearing slot(s), "
               f"{total - unresolved} resolved, {keeps} kept from source, "
               f"{len(unreachable)} surface(s) unreadable and referred to vision QC.")
    _p.brief_qc_json(out_dir).write_text(
        json.dumps({"summary": summary, "blocking": blocking, "warnings": warnings},
                   indent=2), encoding="utf-8")


def cmd_build(args) -> int:
    out_dir = Path(args.out)
    deck = Path(args.deck)
    if not out_dir.exists():
        print(f"[error] out dir not found: {out_dir}", file=sys.stderr)
        return 2
    if not deck.exists():
        print(f"[error] supplied page not found: {deck}", file=sys.stderr)
        return 2

    prs = Presentation(str(deck))
    slides = list(prs.slides)
    n = args.slide
    if not (1 <= n <= len(slides)):
        print(f"[error] --slide {n} out of range (deck has {len(slides)})", file=sys.stderr)
        return 2

    surfaces, unreachable = _extract.walk_slide(slides[n - 1], n)
    rows = []
    for s in surfaces:
        if not _extract.has_figure(s["text"]):
            continue          # prompt only where a figure actually lives
        rows.append({
            "slide": args.target_slide or n,
            "addr": s["addr"],
            "kind": s["kind"],
            "shape_name": s["name"],
            "source_text": s["text"],
            "resolution": None,          # bind_from_brief | keep_source | replace_with
            "replacement": None,         # required when resolution == replace_with
            "note": "",
        })

    ledger = {
        "source_page": str(deck.resolve()),
        "source_slide": n,
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "_how_to": ("Set `resolution` on every row to one of: bind_from_brief "
                    "(take the value from the brief), keep_source (you confirm the "
                    "page's value is still right), replace_with (+ set `replacement`). "
                    "null is not a resolution and blocks the compile."),
        "rows": rows,
        "unreachable": unreachable,
    }
    ledger_path(out_dir).write_text(json.dumps(ledger, indent=2, ensure_ascii=False),
                                    encoding="utf-8")
    _write_brief_qc(out_dir, ledger)
    unresolved, keeps, total = tally(ledger)
    _state.record_source_ledger(out_dir, unresolved, keeps, len(unreachable))

    print(f"[ok] wrote {ledger_path(out_dir)}")
    print(f"     {total} figure-bearing slot(s) to reconcile, {unresolved} unresolved.")
    if unreachable:
        print(f"     {len(unreachable)} surface(s) could NOT be read "
              f"(picture / SmartArt / embedded object). They are NOT checked here; "
              f"the slide-qc vision pass is responsible for them.")
    print("     compile_picks.py will refuse until every row is resolved.")
    return 0


def cmd_status(args) -> int:
    out_dir = Path(args.out)
    ledger = _load(out_dir)
    if not ledger:
        print(f"[info] no {LEDGER_NAME} in {out_dir} — no supplied page pinned.")
        return 0
    unresolved, keeps, total = tally(ledger)
    _write_brief_qc(out_dir, ledger)
    _state.record_source_ledger(out_dir, unresolved, keeps,
                                len(ledger.get("unreachable", []) or []))
    print(f"[ok] {total} slot(s): {total - unresolved} resolved, {unresolved} unresolved, "
          f"{keeps} kept from source.")
    for r in ledger.get("rows", []):
        if r.get("resolution") not in RESOLUTIONS:
            print(f"     UNRESOLVED {r['addr']}: {r['source_text']!r}")
    return 1 if unresolved else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Reconcile figures on a supplied page.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Enumerate figure-bearing slots from a supplied page.")
    b.add_argument("--out", required=True)
    b.add_argument("--deck", required=True, help="The supplied page (.pptx).")
    b.add_argument("--slide", type=int, default=1, help="Which slide of that file.")
    b.add_argument("--target-slide", type=int, default=None,
                   help="Slide number in the deck being built (defaults to --slide).")
    b.set_defaults(func=cmd_build)
    s = sub.add_parser("status", help="Re-tally the ledger and record it.")
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_status)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
