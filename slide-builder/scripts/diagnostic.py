"""diagnostic.py — bundle a Slide Lab output directory for bug reports.

Collects the artifacts a maintainer needs to debug a build failure without
needing access to the user's machine:

  - <out>/_meta.json
  - <out>/_finalize_meta.json (if present)
  - <out>/build.log (if present)
  - <out>/slide_NN/_prompt.md (every slide's agent prompt)
  - <out>/slide_NN/option_X.qc.json (every slide-qc result)
  - <out>/slide_NN/option_X.py (every agent's build script)

Excludes:
  - Binary PPTX / PNG (too large for bug-report zips)
  - The client template itself
  - The user's source brief (likely contains client-sensitive material)

Usage:
  py -3 scripts/diagnostic.py --out <out_dir>
  py -3 scripts/diagnostic.py --out <out_dir> --zip <path-to-output.zip>

If --zip is omitted, writes to <out>/_diagnostic-<timestamp>.zip.
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _paths as _p


def _add_if_exists(zf: zipfile.ZipFile, path: Path, arcname: str) -> bool:
    if path.exists() and path.is_file():
        zf.write(path, arcname=arcname)
        return True
    return False


def collect(out_dir: Path, zip_path: Path) -> dict:
    counts = {"meta": 0, "prompts": 0, "qc": 0, "py": 0, "log": 0, "skipped": 0}
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Top-level
        if _add_if_exists(zf, _p.meta_json(out_dir), "_meta.json"):
            counts["meta"] += 1
        if _add_if_exists(zf, _p.finalize_meta_json(out_dir), "_finalize_meta.json"):
            counts["meta"] += 1
        if _add_if_exists(zf, out_dir / "build.log", "build.log"):
            counts["log"] += 1
        if _add_if_exists(zf, _p.dispatch_plan_md(out_dir), "dispatch_plan.md"):
            counts["prompts"] += 1

        # Per slide
        for sd in sorted(out_dir.glob("slide_*")):
            if not sd.is_dir():
                continue
            slide_name = sd.name
            if _add_if_exists(zf, sd / _p.PROMPT_MD, f"{slide_name}/_prompt.md"):
                counts["prompts"] += 1
            if _add_if_exists(zf, sd / _p.PATTERN_PICK_MD, f"{slide_name}/_pattern_pick.md"):
                counts["prompts"] += 1
            for letter in _p.option_letters():
                if _add_if_exists(zf, sd / _p.option_qc_json_name(letter),
                                  f"{slide_name}/{_p.option_qc_json_name(letter)}"):
                    counts["qc"] += 1
                if _add_if_exists(zf, sd / _p.option_py_name(letter),
                                  f"{slide_name}/{_p.option_py_name(letter)}"):
                    counts["py"] += 1

        # Add a tiny README so the bug reporter knows what's in the zip
        readme = (
            "Slide Lab diagnostic bundle\n"
            "============================\n\n"
            f"Source: {out_dir}\n"
            f"Generated: {datetime.now().isoformat(timespec='seconds')}\n\n"
            "Contents:\n"
            "  _meta.json, _finalize_meta.json, build.log, dispatch_plan.md (if present)\n"
            "  slide_NN/_prompt.md, slide_NN/_pattern_pick.md (per slide)\n"
            "  slide_NN/option_X.qc.json, slide_NN/option_X.py (per option)\n\n"
            "Excluded: PPTX, PNG, source brief, client template.\n"
        )
        zf.writestr("_diagnostic_readme.txt", readme)
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description="Bundle a Slide Lab output dir for a bug report.")
    ap.add_argument("--out", type=Path, required=True, help="Build output directory")
    ap.add_argument("--zip", type=Path, default=None,
                    help="Output zip path (default: <out>/_diagnostic-<timestamp>.zip)")
    args = ap.parse_args()

    out = args.out.resolve()
    if not out.exists() or not out.is_dir():
        sys.stderr.write(f"ERROR: --out is not a directory: {out}\n")
        return 2

    if args.zip is None:
        ts = datetime.now().strftime("%Y%m%dT%H%M%S")
        zip_path = out / f"_diagnostic-{ts}.zip"
    else:
        zip_path = args.zip.resolve()

    print(f"Collecting diagnostic bundle from {out}")
    counts = collect(out, zip_path)
    print(f"  meta files:    {counts['meta']}")
    print(f"  prompts:       {counts['prompts']}")
    print(f"  qc reports:    {counts['qc']}")
    print(f"  agent scripts: {counts['py']}")
    print(f"  build.log:     {counts['log']}")
    print(f"  output: {zip_path}")
    print(f"  size: {zip_path.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
