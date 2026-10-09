#!/usr/bin/env python3
"""publish_cleanup.py — free the space a finished deck no longer needs.

Run when the user says the deck is good. A build keeps a PowerPoint file and
preview image for every option of every slide, picked or not, a set of render
images for every quality-check round, and page images of the final deck. A
finished 2-slide deck was 125 MB and a 33-slide one 146 MB; the decks
themselves were a few MB.

KEPT (everything needed to deliver the deck, and to edit it with Slide Lab
later; a slide folder trimmed to this list was rebuilt by finalize,
build_review --final and compile into the same deck, 2026-10-08):
  - the deck(s) at the top of the session folder (a byte-identical second
    copy named final_deck.pptx, from builds before 2026-10-08, is removed and
    the records point at the topic-named deck)
  - FINAL-CHECK.html, the storyline (dot-dash) files, COMPILED.md, RESULT*.md
  - _session/ files: brief, DECISIONS.md, feedback, the user's own assets and
    copied pages (not its _qc* folders or old-decks/)
  - the deck's records: _meta.json, _state.json, picks.json,
    source_ledger.json, _finalize_meta.json
  - for each slide, only the picked option's design and scripts:
    option_X.py or option_X_native.py, option_X_native.plan.json,
    option_X_translation_report.json (finalize refuses to rebuild without it),
    option_X.html, its pictures in img/ (named X_*), any other file the kept
    design or script names (e.g. a headshots/ folder), and _prior_feedback.md

DELETED:
  - options the user did not pick (all their files)
  - everything else in slide folders: per-option PowerPoint files, every
    image (option, sketch, native, probe), qc.json, _prompt.md, _context.md,
    _context_ack.txt (build_deck.py --slide N writes these again from the
    brief), _raw/, _prev/, _render_tmp/, __pycache__/, scratch
  - at the top: _qc*/ render folders (written notes in them are kept),
    final_pngs/, _raw/, _render_tmp/, __pycache__/, REVIEW.html,
    GATE3-PREVIEW.html, a rejected or half-written deck (*.REJECTED.pptx,
    *.incoming.pptx)
  - in _session/: _qc*/ render images (written notes kept), old-decks/ (Slide
    Lab's own earlier compiles, written only by compile_picks.py),
    __pycache__/

Editing the deck later still works: rebuild or insert a slide as usual; the
next finalize rebuilds the images and PowerPoint files from the kept designs.

compile_picks.py also calls compile_cleanup() after every successful compile:
it removes only what is clearly temporary (render scratch folders and the
options the user did not pick), so a QC fix can still rebuild the picked ones.

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

ROOT_DELETE_DIRS = ("final_pngs", "_raw", "_render_tmp", "__pycache__")
ROOT_DELETE_FILES = ("REVIEW.html", "GATE3-PREVIEW.html")
SESSION_DELETE_DIRS = ("old-decks", "__pycache__")
# Never kept in a slide folder, even when a kept script names them.
SLIDE_ALWAYS_DELETE = {"_prev", "_raw", "_render_tmp", "__pycache__", "_prompt.md",
                       "_context.md", "_context_ack.txt"}
SLIDE_KEEP_FILES = ("_prior_feedback.md",)
NOTE_SUFFIXES = (".md", ".txt", ".json")
# Temporary render folders compile removes on its own (no say-so needed).
COMPILE_TEMP_ROOT = ("_qc_tmp", "_qc_pre", "_render_tmp", "_raw")
COMPILE_TEMP_SLIDE = ("_raw", "_render_tmp")
OPTION_RE = re.compile(r"^option_([A-F])(?:[._])")
IMG_RE = re.compile(r"^([A-F])_")


def _size(p: Path) -> int:
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def _picked_files(letter: str) -> set[str]:
    """The files of a picked option that a rebuild needs."""
    return {f"option_{letter}.py", f"option_{letter}_native.py",
            f"option_{letter}_native.plan.json", f"option_{letter}_translation_report.json",
            f"option_{letter}.html"}


def _letters_from_picks(picks: dict) -> dict[str, set[str]]:
    kept = {}
    for k, v in picks.items():
        vals = v if isinstance(v, list) else [v]
        kept[k] = {x for x in vals if isinstance(x, str) and len(x) == 1 and x != "-"}
    return kept


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
    return _letters_from_picks(picks)


def _letters_on_disk(sd: Path) -> set[str]:
    found = set()
    for f in sd.iterdir():
        m = OPTION_RE.match(f.name)
        if m and f.is_file():
            found.add(m.group(1))
    return found


def _notes_rule(folder: Path) -> list[Path]:
    """A render folder goes, but written notes in it (qc-flags-*.md, the
    user's reasons for overriding a finding) stay."""
    files = [f for f in folder.rglob("*") if f.is_file()]
    notes = [f for f in files if f.suffix.lower() in NOTE_SUFFIXES]
    if notes:
        return [f for f in files if f not in notes]
    return [folder]


def _slide_victims(sd: Path, letters: set[str]) -> list[Path]:
    """Everything in one slide folder except the picked options' rebuild files."""
    keep = set(SLIDE_KEEP_FILES)
    for L in letters:
        keep |= _picked_files(L)
    # Text of the kept designs and scripts: a file or folder they name (a
    # headshots/ folder, a picture loaded by path) is kept too.
    kept_text = ""
    for name in keep:
        f = sd / name
        if f.is_file() and f.suffix in (".py", ".html", ".json"):
            try:
                kept_text += f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                pass

    def named(p: Path) -> bool:
        return bool(kept_text) and p.name in kept_text

    def picked_picture(g: Path) -> bool:
        m = IMG_RE.match(g.name)
        return bool(m and m.group(1) in letters)

    victims: list[Path] = []
    for f in sd.iterdir():
        if f.name in keep and f.is_file():
            continue
        if f.name in SLIDE_ALWAYS_DELETE or OPTION_RE.match(f.name):
            victims.append(f)
            continue
        if f.is_dir() and f.name == "img":
            pics = [g for g in f.rglob("*") if g.is_file()]
            gone = [g for g in pics if not picked_picture(g) and not named(g)]
            victims += [f] if gone and len(gone) == len(pics) else gone
            continue
        if named(f):
            continue
        victims.append(f)
    return victims


def _duplicate_build_deck(out: Path) -> Path | None:
    """final_deck.pptx when it is a byte-identical second copy of a
    topic-named deck at the top (builds before 2026-10-08 wrote both)."""
    fd = out / "final_deck.pptx"
    if not fd.is_file():
        return None
    dig = _state.file_digest(fd)
    for p in out.glob("*.pptx"):
        if p.name != fd.name and p.is_file() and _state.file_digest(p) == dig:
            return fd
    return None


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
    victims += [p for p in sorted(out.glob("*.pptx")) if p.is_file()
                and (p.name.endswith(".REJECTED.pptx") or p.name.endswith(".incoming.pptx"))]
    dup = _duplicate_build_deck(out)
    if dup:
        victims.append(dup)
    for qc in sorted(p for p in out.iterdir() if p.is_dir() and p.name.startswith("_qc")):
        victims += _notes_rule(qc)
    sess = out / "_session"
    if sess.is_dir():
        for qc in sorted(p for p in sess.iterdir() if p.is_dir() and p.name.startswith("_qc")):
            victims += _notes_rule(qc)
        for d in SESSION_DELETE_DIRS:
            if (sess / d).is_dir():
                victims.append(sess / d)
    for sd in sorted(out.glob("slide_[0-9][0-9]")):
        if not sd.is_dir():
            continue
        letters = kept.get(sd.name) if kept is not None else None
        if letters is None:
            letters = _letters_on_disk(sd)          # no picks: keep every design
        victims += _slide_victims(sd, letters)
    return victims, {"picks_known": kept is not None, "kept": kept, "duplicate_deck": dup}


def _repoint_records(out: Path, old: Path) -> None:
    """The records named the duplicate about to be deleted; point them at the
    identical topic-named deck so check_done still finds the deck it verifies."""
    dig = _state.file_digest(old)
    target = next((p for p in sorted(out.glob("*.pptx"))
                   if p != old and p.is_file() and _state.file_digest(p) == dig), None)
    if target is None:
        return
    st = _state.read_state(out)
    changed = False
    recs = [((st.get("stages") or {}).get("compile") or {}), (st.get("vision_qc") or {})]
    for rec in recs:
        for field in ("output", "deck"):
            if rec.get(field) and Path(rec[field]).resolve() == old.resolve():
                rec[field] = str(target.resolve())
                changed = True
    if changed:
        _state._write(out, st)


def _delete(paths: list[Path]) -> None:
    for p in paths:
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        elif p.exists():
            try:
                p.unlink()
            except OSError:
                pass


def _record_kept_options(out: Path, kept: dict[str, set[str]]) -> None:
    """Finalize expects every option letter recorded for a slide; only the
    picked ones remain, so record that."""
    meta_p = out / "_meta.json"
    try:
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
    except Exception:
        return
    for s in meta.get("slides", []):
        k = f"slide_{int(s.get('n', 0)):02d}"
        if k in kept and kept[k] and s.get("options"):
            s["options"] = sorted(kept[k] & set(s["options"])) or s["options"][:1]
    meta_p.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def compile_cleanup(out: Path, picks: dict, remove_unpicked: bool = True) -> str:
    """After a successful compile: delete what is clearly temporary (render
    scratch at the top and in slide folders) and the options the user did not
    pick. The picked options keep all their files until the user says the
    deck is good (a QC fix rebuilds from them). Slides left out of the deck
    are not touched (the user may put them back), and nothing is unpicked
    after an all-options comparison deck (remove_unpicked=False: it exists so
    a choice can still be made). Returns a one-line report."""
    out = Path(out)
    before = _size(out)
    victims: list[Path] = [out / d for d in COMPILE_TEMP_ROOT if (out / d).is_dir()]
    kept = _letters_from_picks(picks or {}) if remove_unpicked else {}
    for sd in sorted(out.glob("slide_[0-9][0-9]")):
        if not sd.is_dir():
            continue
        victims += [sd / d for d in COMPILE_TEMP_SLIDE if (sd / d).is_dir()]
        letters = kept.get(sd.name)
        if not letters:
            continue                                   # left out, or not in this deck
        for f in sd.iterdir():
            m = OPTION_RE.match(f.name)
            if m and f.is_file() and m.group(1) not in letters:
                victims.append(f)
        img = sd / "img"
        if img.is_dir():
            for g in img.iterdir():
                m = IMG_RE.match(g.name)
                if g.is_file() and m and m.group(1) not in letters:
                    victims.append(g)
    _delete(victims)
    _record_kept_options(out, {k: v for k, v in kept.items() if v})
    after = _size(out)
    what = ("render scratch and the options not picked removed" if remove_unpicked
            else "render scratch removed; every option kept for the comparison deck")
    return (f"  folder size {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB ({what}; the rest "
            f"goes when the user says the deck is good: publish_cleanup.py)")


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
    compiled = bool((_state.read_state(out).get("stages") or {}).get("compile"))
    if not list(out.glob("*.pptx")):
        print("REFUSED: no published deck (.pptx) in this folder yet. Compile the deck "
              "first; this cleanup is for after the user has said it is good.")
        return 5

    victims, notes = plan(out)
    gone = {p.name for p in victims if p.parent == out}
    decks = sorted(p.name for p in out.glob("*.pptx") if p.name not in gone)
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

    if notes["duplicate_deck"]:
        _repoint_records(out, notes["duplicate_deck"])
    _delete(victims)
    if notes["kept"]:
        _record_kept_options(out, notes["kept"])
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
