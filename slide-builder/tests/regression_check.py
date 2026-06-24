#!/usr/bin/env python3
"""Compare a fresh build against captured baselines (Spec 5 §6).

Run after each Pattern B commit. Reports per-PNG SSIM scores
and exits non-zero if any score drops below the Major threshold (0.85)
— that is, when a previously-clean slide visibly diverges.

Usage
-----
    py -3 tests/regression_check.py \
        --name otc \
        --build-dir "C:/path/to/fresh/build" \
        [--threshold 0.85] \
        [--json out.json]

The build dir must mirror the layout the baseline was captured against:
`slide_NN/option_X.png` (and, if `final_*_baseline.png` exists in the
baseline set, a sibling `final_pngs/slide_NN.png`).

Exit codes
----------
    0 — every baseline matched (SSIM >= threshold) AND no current PNG is missing
    1 — at least one regression detected
    2 — usage / missing baseline / config error

See also
--------
- `_decisions/pattern-b/spec-5-fidelity-measurement.md` §6
- `capture_baseline.py` (writes the baselines this script reads)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BASELINE_ROOT = THIS_DIR / "baselines"

# Per Spec 5 §3 + Decision 5. Surface anything below `major` as a regression;
# the build itself enforces `critical` separately inside finalize_deck.
DEFAULT_THRESHOLD = 0.85


def _measure(baseline_png: Path, current_png: Path) -> dict:
    from skimage.metrics import structural_similarity as ssim
    from skimage.io import imread

    if not current_png.exists():
        return {"status": "missing-current", "current": str(current_png)}

    b_img = imread(baseline_png)
    c_img = imread(current_png)
    if b_img.shape != c_img.shape:
        return {
            "status": "dimension-mismatch",
            "baseline_shape": list(b_img.shape),
            "current_shape": list(c_img.shape),
        }
    score = float(ssim(
        b_img, c_img,
        data_range=255,
        channel_axis=-1 if b_img.ndim == 3 else None,
        win_size=7,
    ))
    return {"status": "measured", "ssim": score}


def _resolve_current_png(build_dir: Path, baseline_name: str) -> Path:
    """Map a baseline filename back to its expected location in build_dir.

    `slide_NN_X_baseline.png` -> `build_dir/slide_NN/option_X.png`
    `final_NN_baseline.png`   -> `build_dir/final_pngs/slide_NN.png`
    """
    parts = baseline_name.removesuffix("_baseline.png").split("_")
    if parts[0] == "slide" and len(parts) == 3:
        n_str, letter = parts[1], parts[2]
        return build_dir / f"slide_{int(n_str):02d}" / f"option_{letter}.png"
    if parts[0] == "final" and len(parts) == 2:
        n = int(parts[1])
        return build_dir / "final_pngs" / f"slide_{n:02d}.png"
    raise ValueError(f"unrecognised baseline filename: {baseline_name}")


def check(name: str, build_dir: Path, threshold: float) -> list[dict]:
    baseline_set = BASELINE_ROOT / name
    if not baseline_set.exists():
        raise SystemExit(
            f"no baseline set named '{name}' under {BASELINE_ROOT}. "
            f"Capture first with `capture_baseline.py --name {name} "
            f"--source <build_dir>`."
        )

    results: list[dict] = []
    for baseline_png in sorted(baseline_set.glob("*_baseline.png")):
        current_png = _resolve_current_png(build_dir, baseline_png.name)
        outcome = _measure(baseline_png, current_png)
        entry = {
            "baseline": baseline_png.name,
            "current": str(current_png),
            **outcome,
        }
        if outcome["status"] == "measured":
            entry["regression"] = outcome["ssim"] < threshold
        else:
            entry["regression"] = True
        results.append(entry)
    return results


def _summary(results: list[dict], threshold: float) -> tuple[int, int, int]:
    """Return (n_total, n_regressions, n_missing_or_mismatch)."""
    n_total = len(results)
    n_reg = sum(1 for r in results if r.get("regression"))
    n_mm = sum(1 for r in results if r["status"] != "measured")
    return n_total, n_reg, n_mm


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--name", required=True,
        help="Baseline set name (matches a subdir under tests/baselines/).",
    )
    ap.add_argument(
        "--build-dir", required=True, type=Path,
        help="Fresh build directory to compare against the baseline.",
    )
    ap.add_argument(
        "--threshold", type=float, default=DEFAULT_THRESHOLD,
        help=f"SSIM threshold below which a slide is flagged as a "
             f"regression (default {DEFAULT_THRESHOLD}, per Decision 5 "
             f"+ Spec 5 §3).",
    )
    ap.add_argument(
        "--json", type=Path, default=None,
        help="Optional: also write the full results list to this JSON file.",
    )
    args = ap.parse_args()

    try:
        results = check(
            name=args.name,
            build_dir=args.build_dir.resolve(),
            threshold=args.threshold,
        )
    except SystemExit:
        raise
    except Exception as exc:
        print(f"regression check failed to run: {exc}", file=sys.stderr)
        sys.exit(2)

    n_total, n_reg, n_mm = _summary(results, args.threshold)
    print(f"Compared {n_total} baseline(s) against {args.build_dir}")
    if n_total == 0:
        print("  (no baselines found — did capture_baseline.py run?)")
    for r in results:
        status = r["status"]
        if status == "measured":
            mark = "FAIL" if r["regression"] else "ok  "
            print(f"  {mark}  {r['baseline']:32s}  SSIM={r['ssim']:.4f}")
        else:
            print(f"  FAIL  {r['baseline']:32s}  {status}")

    print(f"Summary: {n_reg} regression(s), {n_mm} missing/mismatch")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps({
                "name": args.name,
                "build_dir": str(args.build_dir),
                "threshold": args.threshold,
                "summary": {"total": n_total, "regressions": n_reg, "missing": n_mm},
                "results": results,
            }, indent=2),
            encoding="utf-8",
        )
        print(f"  results -> {args.json}")

    sys.exit(0 if n_reg == 0 else 1)


if __name__ == "__main__":
    main()
