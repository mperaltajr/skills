#!/usr/bin/env python3
"""publish_cleanup.py — free the space a finished deck no longer needs.

Run when the user says the deck is good. A build keeps a PowerPoint file and
preview image for every option of every slide, picked or not, a set of render
images for every quality-check round, and page images of the final deck. On
the 09/29 investor decks that was about 90% of the folder; the decks
themselves were 18 MB of 610.

KEPT (everything needed to deliver the deck, and to edit it with Slide Lab
later):
  - every PowerPoint file at the top of the session folder (the deck)
  - FINAL-CHECK.html, the storyline (dot-dash) files, COMPILED.md, RESULT*.md
  - _session/ files: brief, DECISIONS.md, feedback (not its _qc* folders)
  - the deck's records: _meta.json, _state.json, picks.json, source_ledger.json
  - for each slide: _prompt.md, _context.md, _prior_feedback.md, and the
    picked option's design and scripts (html / py / native py + plan / reports)

DELETED:
  - options the user did not pick (all their files)
  - the picked option's page images and per-option PowerPoint files: finalize
    regenerates them from the kept design if the deck is ever edited
  - _session/_qc* render images (written notes in them are kept), final_pngs/, _raw/,
    _render_tmp/, slide_NN/_prev/ (replaced options), REVIEW.html and
    GATE3-PREVIEW.html (picks are recorded), __pycache__/

Editing the deck later still works: rebuild or insert a slide as usual; the
next finalize rebuilds the images and PowerPoint files from the kept designs.

Run:  py -3 scripts/publish_cleanup.py --out <session folder> [--dry-run]
      py -3 scripts/publish_cleanup.py --scan <folder>    (list finished decks; deletes nothing)
Exit: 0 cleaned (or dry run) | 2 not a session folder | 5 nothing published yet
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _state  # noqa: E402

KEEP_OPTION_SUFFIXES = (".html", ".py", ".json", ".md")
ROOT_DELETE_DIRS = ("final_pngs", "_raw", "_render_tmp", "__pycache__")
ROOT_DELETE_FILES = ("REVIEW.html", "GATE3-PREVIEW.html")
SLIDE_DELETE_DIRS = ("_prev", "_raw", "_render_tmp", "__pycache__")
OPTION_RE = re.compile(r"^option_([A-F])(?:[._])")


def _size(p: Path) -> int:
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def _kept_letters(out: Path) -> dict[str, set[str]] | None:
    """{slide_NN: letters to keep} from the recorded picks; None when unknown."""
    picks = (_state.read_state(out).get("review") or {}).get("picks")
    if not picks and (out / "picks.json").exists():
        try:
            picks = json.loads((out / "picks.json").read_text(encoding="utf-8"))
        except Exception:
            picks = None
    if not isinstance(picks, dict) or not picks:
        return None
    kept = {}
    for k, v in picks.items():
        vals = v if isinstance(v, list) else [v]
        kept[k] = {x for x in vals if isinstance(x, str) and len(x) == 1 and x != "-"}
    return kept


def plan(out: Path) -> tuple[list[Path], dict]:
    """(paths to delete, notes)."""
    kept = _kept_letters(out)
    victims: list[Path] = []
    for d in ROOT_DELETE_DIRS:
        if (out / d).is_dir():
            victims.append(out / d)
    for f in ROOT_DELETE_FILES:
        if (out / f).is_file():
            victims.append(out / f)
    sess = out / "_session"
    if sess.is_dir():
        for qc in (p for p in sess.iterdir() if p.is_dir() and p.name.startswith("_qc")):
            # renders go; written notes (e.g. qc-flags-*.md, the user's reasons
            # for overriding a finding) stay
            notes_inside = [f for f in qc.rglob("*") if f.is_file() and f.suffix.lower() in (".md", ".txt", ".json")]
            if notes_inside:
                victims += [f for f in qc.rglob("*") if f.is_file() and f not in notes_inside]
            else:
                victims.append(qc)
    for sd in sorted(out.glob("slide_[0-9][0-9]")):
        if not sd.is_dir():
            continue
        for d in SLIDE_DELETE_DIRS:
            if (sd / d).is_dir():
                victims.append(sd / d)
        letters = kept.get(sd.name) if kept is not None else None
        for f in sd.iterdir():
            m = OPTION_RE.match(f.name)
            if not m or not f.is_file():
                continue
            picked = letters is None or m.group(1) in letters
            if not picked:
                victims.append(f)                       # an option nobody picked
            elif not f.name.endswith(KEEP_OPTION_SUFFIXES):
                victims.append(f)                       # regenerable image / pptx
    return victims, {"picks_known": kept is not None, "kept": kept}


def scan(root: Path) -> int:
    """List every finished deck (a session folder with a .pptx at its top)
    under root, with what a cleanup would free. Deletes nothing: the user
    chooses which decks are final, then each gets --out."""
    rows = []
    for meta in root.rglob("_meta.json"):
        sess = meta.parent
        if "slide_" in sess.name or not list(sess.glob("*.pptx")):
            continue
        if ((_state.read_state(sess).get("published_cleanup")) or {}).get("at"):
            continue                                     # already cleaned
        victims, _n = plan(sess)
        latest = max((f.stat().st_mtime for f in sess.rglob("*") if f.is_file()), default=0)
        compiled = bool((_state.read_state(sess).get("stages") or {}).get("compile"))
        rows.append((sum(_size(v) for v in victims), _size(sess), sess, latest, compiled))
    if not rows:
        print(f"No finished, uncleaned decks under {root}.")
        return 0
    rows.sort(key=lambda r: -r[0])
    print(f"{len(rows)} finished deck(s) under {root} (largest saving first):")
    import time
    now = time.time()
    for freed, total, sess, latest, compiled in rows:
        age = now - latest
        when = (f"changed {int(age // 3600)}h ago, MAY BE IN PROGRESS" if age < 86400
                else f"last changed {datetime.fromtimestamp(latest).strftime('%Y-%m-%d')}")
        status = "compiled" if compiled else "deck file present"
        print(f"  {freed / 1e6:7.1f} MB of {total / 1e6:7.1f} MB  {sess}  ({status}; {when})")
    print(f"Total that could be freed: {sum(r[0] for r in rows) / 1e6:.1f} MB. Ask the user which "
          "decks are final, then run --out on each.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Free the space a published deck no longer needs.")
    ap.add_argument("--out", type=Path, help="The deck's session folder.")
    ap.add_argument("--scan", type=Path, help="List finished decks under this folder; delete nothing.")
    ap.add_argument("--dry-run", action="store_true", help="Show what would go; delete nothing.")
    args = ap.parse_args(argv)
    if args.scan:
        return scan(args.scan.resolve())
    if not args.out:
        ap.error("give --out <session folder> or --scan <folder>")
    out = args.out.resolve()

    if not out.is_dir() or not (out / "_meta.json").exists():
        print(f"REFUSED: {out} is not a Slide Lab session folder (no _meta.json).")
        return 2
    if out == Path(out.anchor) or out == Path.home() or HERE.parent in [out, *out.parents]:
        print(f"REFUSED: {out} is not a deck's session folder.")
        return 2
    decks = sorted(p.name for p in out.glob("*.pptx"))
    compiled = bool((_state.read_state(out).get("stages") or {}).get("compile"))
    if not decks:
        print("REFUSED: no published deck (.pptx) in this folder yet. Compile the deck "
              "first; this cleanup is for after the user has said it is good.")
        return 5

    victims, notes = plan(out)
    freed = sum(_size(p) for p in victims)
    total = _size(out)
    print(f"Deck(s) kept: {', '.join(decks)}" + ("" if compiled else "  (no compile record; older build)"))
    if not notes["picks_known"]:
        print("  No recorded picks: every option's design is kept; only images, "
              "renders and scratch are removed.")
    print(f"{'Would free' if args.dry_run else 'Freeing'} {freed / 1e6:.1f} MB of "
          f"{total / 1e6:.1f} MB ({len(victims)} files/folders):")
    groups: dict[str, int] = {}
    for p in victims:
        rel = p.relative_to(out)
        if p.parent.name.startswith("slide_") and OPTION_RE.match(p.name):
            key = "option images, PowerPoint files and unpicked options"
        else:
            key = re.sub(r"slide_\d\d", "slide_NN", str(rel.parent / rel.name if p.is_dir() else rel.name))
        groups[key] = groups.get(key, 0) + _size(p)
    for k, v in sorted(groups.items(), key=lambda x: -x[1]):
        print(f"  {v / 1e6:8.1f} MB  {k}")
    if args.dry_run:
        return 0

    for p in victims:
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        elif p.exists():
            p.unlink()

    # Finalize expects every option letter recorded for a slide; only the
    # picked ones remain, so record that.
    kept = notes["kept"]
    if kept:
        meta_p = out / "_meta.json"
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        for s in meta.get("slides", []):
            k = f"slide_{int(s.get('n', 0)):02d}"
            if k in kept and s.get("options"):
                s["options"] = sorted(kept[k] & set(s["options"])) or s["options"][:1]
        meta_p.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    try:
        st = _state.read_state(out)
        st["published_cleanup"] = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                   "freed_bytes": freed, "decks": decks}
        _state._write(out, st)
    except Exception:
        pass
    print(f"[ok] freed {freed / 1e6:.1f} MB; folder is now {_size(out) / 1e6:.1f} MB.")
    print("     To edit this deck later, rebuild or insert a slide as usual; the next "
          "finalize regenerates the page images and PowerPoint files from the kept designs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
