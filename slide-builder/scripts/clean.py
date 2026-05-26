"""clean.py — clear ephemeral artifacts from a Slide Lab output directory.

Removes intermediate build state so a re-run starts from a known-clean
position. Preserves picks.json (user-authored input) and never touches files
outside the named output directory.

Removed by default:
  - <out>/_raw/ (per-slide unthemed PPTX archive — finalize_deck.py output)
  - <out>/_render_tmp/ (LibreOffice scratch dirs anywhere under out)
  - <out>/slide_NN/option_*.png (intermediate thumbnails)
  - <out>/slide_NN/option_*.pptx (themed per-option PPTX)
  - <out>/slide_NN/option_*-mermaid.png (rendered Mermaid PNGs)
  - <out>/slide_NN/_render_tmp/ (any leftover LibreOffice scratch)
  - <out>/_meta.json (deck manifest — stale by definition after a clean)
  - <out>/_finalize_meta.json (stale)
  - <out>/GATE3-PREVIEW.html (terminal — regenerate after re-run)
  - <out>/REVIEW.html (terminal — regenerate after re-run)
  - any __pycache__/ under out

Preserved:
  - <out>/picks.json (user picks)
  - <out>/slide_NN/_prompt.md (agent prompts — re-running build_deck rewrites)
  - <out>/slide_NN/option_*.py (agent build scripts — re-running finalize will
    re-execute them and produce fresh option_X.pptx + .png)
  - <out>/dispatch_plan.md

Usage:
  py -3 scripts/clean.py --out <out_dir>
  py -3 scripts/clean.py --out <out_dir> --deep      # also removes option_*.py
                                                     # and _prompt.md (full reset)

Exit codes:
  0  Removed cleanly
  2  --out missing or not a directory
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _paths as _p


def _safe_rm(path: Path) -> tuple[int, int]:
    """Remove a file or directory tree. Returns (files_removed, dirs_removed)."""
    if not path.exists():
        return 0, 0
    if path.is_file() or path.is_symlink():
        path.unlink()
        return 1, 0
    if path.is_dir():
        # Count first
        n_files = sum(1 for _ in path.rglob("*") if _.is_file())
        n_dirs  = sum(1 for _ in path.rglob("*") if _.is_dir()) + 1
        shutil.rmtree(path)
        return n_files, n_dirs
    return 0, 0


def clean(out_dir: Path, deep: bool = False) -> dict:
    removed = {"files": 0, "dirs": 0}

    # Top-level deck artifacts
    for path in [
        _p.meta_json(out_dir),
        _p.finalize_meta_json(out_dir),
        _p.gate3_preview_html(out_dir),
        _p.review_html(out_dir),
    ]:
        f, d = _safe_rm(path)
        removed["files"] += f
        removed["dirs"] += d

    # __pycache__ anywhere under out
    for cache in out_dir.rglob("__pycache__"):
        f, d = _safe_rm(cache)
        removed["files"] += f
        removed["dirs"] += d

    # Per-slide and per-option
    for slide_dir in sorted(out_dir.glob("slide_*")):
        if not slide_dir.is_dir():
            continue
        # _raw archive + _render_tmp scratch
        for sub in [slide_dir / _p.RAW_DIR, slide_dir / _p.RENDER_TMP_DIR]:
            f, d = _safe_rm(sub)
            removed["files"] += f
            removed["dirs"] += d

        # Per-option themed PPTX + thumbnails (not the .py source unless --deep)
        for letter in _p.option_letters():
            for pat in (
                slide_dir / _p.option_pptx_name(letter),
                slide_dir / _p.option_png_name(letter),
                slide_dir / _p.option_mermaid_png_name(letter),
                slide_dir / _p.option_qc_json_name(letter),
            ):
                f, d = _safe_rm(pat)
                removed["files"] += f
                removed["dirs"] += d
            if deep:
                # Remove agent's build scripts + Mermaid specs
                for pat in (
                    slide_dir / _p.option_py_name(letter),
                    slide_dir / _p.option_mmd_name(letter),
                ):
                    f, d = _safe_rm(pat)
                    removed["files"] += f
                    removed["dirs"] += d

        # _pattern_pick.md (regenerable from re-dispatch)
        f, d = _safe_rm(slide_dir / _p.PATTERN_PICK_MD)
        removed["files"] += f
        removed["dirs"] += d

        # In deep mode also remove the prompt and the now-empty slide dir
        if deep:
            f, d = _safe_rm(slide_dir / _p.PROMPT_MD)
            removed["files"] += f
            removed["dirs"] += d
            # If the slide_dir is empty, drop it
            try:
                next(slide_dir.iterdir())
            except StopIteration:
                slide_dir.rmdir()
                removed["dirs"] += 1

    # In deep mode also clear dispatch_plan.md (regenerable from build_deck)
    if deep:
        f, d = _safe_rm(_p.dispatch_plan_md(out_dir))
        removed["files"] += f
        removed["dirs"] += d

    return removed


def main() -> int:
    ap = argparse.ArgumentParser(description="Clean ephemeral artifacts from a Slide Lab output dir.")
    ap.add_argument("--out", type=Path, required=True, help="Output directory to clean")
    ap.add_argument("--deep", action="store_true",
                    help="Also remove agent build scripts (option_*.py), prompts, dispatch plan — full reset to pre-build state.")
    args = ap.parse_args()

    out = args.out.resolve()
    if not out.exists() or not out.is_dir():
        sys.stderr.write(f"ERROR: --out is not a directory: {out}\n")
        return 2

    print(f"Cleaning {out}{' (deep)' if args.deep else ''}")
    result = clean(out, deep=args.deep)
    print(f"  removed: {result['files']} files, {result['dirs']} dirs")
    if not args.deep:
        print(f"  preserved: picks.json, slide_NN/_prompt.md, slide_NN/option_*.py, dispatch_plan.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
