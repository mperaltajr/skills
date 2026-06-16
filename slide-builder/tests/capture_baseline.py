#!/usr/bin/env python3
"""Capture baseline PNGs for Pattern B regression testing (Spec 5 §5).

Run on the CURRENT (pre-Pattern-B) pipeline to snapshot what "good" looks
like. Re-run after every Pattern B build via `regression_check.py` to
catch silent regressions (Pattern B Quality Guarantee #3).

The script does NOT build a deck — it copies already-rendered PNGs from a
build directory you point it at. Build the deck normally first
(`build_deck.py` → workers → `finalize_deck.py`), then run this against
the resulting build dir.

Usage
-----
    py -3 tests/capture_baseline.py \
        --source "C:/path/to/build" \
        --name otc \
        [--include final_pngs]   # also snapshot finalized slide_NN.png

The build dir is expected to contain per-slide subfolders named
`slide_NN/` with `option_A.png` / `option_B.png` / `option_C.png` inside.
Optionally a sibling `final_pngs/slide_NN.png` directory from
finalize_deck.

Output
------
    tests/baselines/<name>/
        slide_01_A_baseline.png
        slide_01_B_baseline.png
        ...
        final_01_baseline.png       (if --include final_pngs)
        manifest.json               (capture date, git SHA, source path)

Baselines are intentionally NOT committed to the repo (they may contain
client-confidential renders). They live locally for regression testing.
See `.gitignore` for the exclusion rule.

See also
--------
- `_decisions/pattern-b/spec-5-fidelity-measurement.md` §5
- `regression_check.py` (the consumer of these baselines)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BASELINE_ROOT = THIS_DIR / "baselines"


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=THIS_DIR, text=True
        ).strip()
    except Exception:
        return "unknown"


def _sha256_short(p: Path) -> str:
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    return h[:16]


def capture(source: Path, name: str, include_final: bool) -> Path:
    if not source.exists() or not source.is_dir():
        raise SystemExit(f"source build dir not found: {source}")

    dest = BASELINE_ROOT / name
    if dest.exists():
        # Preserve previous capture by renaming; never silently overwrite.
        ts = _dt.datetime.now().strftime("%Y%m%dT%H%M%S")
        archive = BASELINE_ROOT / f"{name}.archived-{ts}"
        dest.rename(archive)
        print(f"  archived previous baseline -> {archive.name}")
    dest.mkdir(parents=True, exist_ok=True)

    captured: list[dict] = []
    # Per-slide option_X.png from worker output
    for slide_dir in sorted(source.glob("slide_*")):
        if not slide_dir.is_dir():
            continue
        try:
            slide_n = int(slide_dir.name.split("_")[1])
        except (IndexError, ValueError):
            continue
        for letter in ("A", "B", "C"):
            png = slide_dir / f"option_{letter}.png"
            if png.exists():
                dst = dest / f"slide_{slide_n:02d}_{letter}_baseline.png"
                shutil.copy2(png, dst)
                captured.append({
                    "slide_n": slide_n,
                    "kind": "option",
                    "option": letter,
                    "source": str(png.relative_to(source)),
                    "sha256_16": _sha256_short(dst),
                    "bytes": dst.stat().st_size,
                })

    # Finalized slide_NN.png (post-graft, themed) — recommended for the
    # "Quality Guarantee #3 no silent regression" check.
    if include_final:
        final_dir = source / "final_pngs"
        if not final_dir.exists():
            print(f"  warning: --include final_pngs but {final_dir} not found")
        else:
            for png in sorted(final_dir.glob("slide_*.png")):
                try:
                    slide_n = int(png.stem.split("_")[1])
                except (IndexError, ValueError):
                    continue
                dst = dest / f"final_{slide_n:02d}_baseline.png"
                shutil.copy2(png, dst)
                captured.append({
                    "slide_n": slide_n,
                    "kind": "final",
                    "option": None,
                    "source": str(png.relative_to(source)),
                    "sha256_16": _sha256_short(dst),
                    "bytes": dst.stat().st_size,
                })

    manifest = {
        "name": name,
        "captured_at_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "git_sha": _git_sha(),
        "source": str(source),
        "include_final": include_final,
        "count": len(captured),
        "files": captured,
    }
    (dest / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return dest


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--source", required=True, type=Path,
        help="Build directory containing slide_NN/option_X.png files.",
    )
    ap.add_argument(
        "--name", required=True,
        help="Label for this baseline set (e.g. 'otc'). Becomes the "
             "subdirectory name under tests/baselines/.",
    )
    ap.add_argument(
        "--include", action="append", default=[],
        choices=["final_pngs"],
        help="Optional extra artifact set to capture. 'final_pngs' "
             "snapshots the post-finalize themed PPTX renders too.",
    )
    args = ap.parse_args()

    dest = capture(
        source=args.source.resolve(),
        name=args.name,
        include_final="final_pngs" in args.include,
    )
    manifest = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    print(f"Captured {manifest['count']} PNG(s) -> {dest}")
    print(f"  git SHA: {manifest['git_sha']}")
    print(f"  manifest: {dest / 'manifest.json'}")


if __name__ == "__main__":
    main()
