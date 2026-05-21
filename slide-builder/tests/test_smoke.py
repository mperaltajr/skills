r"""Slide Lab orchestrator smoke test.

Fully local end-to-end test of the prep -> finalize -> review pipeline.
No real Claude API calls; uses pre-canned option_X.py scripts to simulate
the agent dispatch step.

Run:
    py -3 "%USERPROFILE%\.claude\skills\slide-builder\tests\test_smoke.py"
    py -3 "...\test_smoke.py" --keep   # skip cleanup for debugging

Exit 0 = all assertions passed. Exit 1 = at least one failed.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path


# ---------------------------------------------------------------------------
# Hard-coded paths
# ---------------------------------------------------------------------------
SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"

BUILD_SCRIPT = SCRIPTS / "build_deck.py"
FINALIZE_SCRIPT = SCRIPTS / "finalize_deck.py"
REVIEW_SCRIPT = SCRIPTS / "build_review.py"

import os
_brief = os.environ.get("SLIDELAB_TEST_BRIEF", "")
_template = os.environ.get("SLIDELAB_TEST_TEMPLATE", "")
_canned = os.environ.get("SLIDELAB_TEST_CANNED", "")
BRIEF = Path(_brief) if _brief else None
TEMPLATE = Path(_template) if _template else None
CANNED_ROOT = Path(_canned) if _canned else None

SUBPROCESS_TIMEOUT = 180  # seconds — LibreOffice can be slow on cold start.

DESIGNER_BRIEF_MARKER = "<<<DESIGNER_BRIEF_START>>>"


# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------
class StepFailure(AssertionError):
    pass


_results: list[tuple[str, bool, str]] = []


def step(name: str):
    def deco(fn):
        def wrapped(*args, **kwargs):
            print(f"\n[STEP] {name}")
            print("-" * 72)
            try:
                out = fn(*args, **kwargs)
                _results.append((name, True, ""))
                print(f"  -> PASS")
                return out
            except Exception as e:
                tb = traceback.format_exc()
                _results.append((name, False, f"{type(e).__name__}: {e}"))
                print(f"  -> FAIL: {type(e).__name__}: {e}")
                print(tb)
                raise StepFailure(name) from e
        return wrapped
    return deco


# ---------------------------------------------------------------------------
# Subprocess helper
# ---------------------------------------------------------------------------
def run_py(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    cmd = ["py", "-3", str(script), *args]
    print(f"  $ {' '.join(cmd)}")
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=SUBPROCESS_TIMEOUT,
    )
    if proc.stdout:
        tail = "\n".join(proc.stdout.splitlines()[-15:])
        print(f"  stdout (tail):\n{tail}")
    if proc.returncode != 0 and proc.stderr:
        tail = "\n".join(proc.stderr.splitlines()[-15:])
        print(f"  stderr (tail):\n{tail}")
    return proc


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------
@step("preflight: required inputs exist")
def preflight():
    # External fixtures (brief, client template, canned-options corpus) are
    # supplied via env vars and live outside this repo. If any of the three is
    # unset, the test SKIPS — it doesn't fail. This keeps the smoke test usable
    # for fresh-cloners who haven't pointed SLIDELAB_TEST_BRIEF / _TEMPLATE /
    # _CANNED at their own fixtures yet.
    if BRIEF is None or TEMPLATE is None or CANNED_ROOT is None:
        msg = (
            "SKIPPED: external fixtures not set. To enable this test, point\n"
            "  SLIDELAB_TEST_BRIEF    -> a narrative brief .md file\n"
            "  SLIDELAB_TEST_TEMPLATE -> a client .pptx template\n"
            "  SLIDELAB_TEST_CANNED   -> a folder of slide_NN/option_X.py canned outputs\n"
            "  (see slide-builder/README.md for fixture format)"
        )
        print(msg)
        raise SystemExit(0)
    for p in (BUILD_SCRIPT, FINALIZE_SCRIPT, REVIEW_SCRIPT, BRIEF, TEMPLATE):
        assert p.exists(), f"missing: {p}"
    for n in (1, 2):
        for letter in ("A", "B", "C"):
            p = CANNED_ROOT / f"slide_{n:02d}" / f"option_{letter}.py"
            assert p.exists(), f"missing canned option: {p}"


@step("part A: run build_deck.py --slides 2")
def part_a(tmp: Path):
    proc = run_py(
        BUILD_SCRIPT,
        "--brief", str(BRIEF),
        "--template", str(TEMPLATE),
        "--out", str(tmp),
        "--slides", "2",
    )
    assert proc.returncode == 0, f"build exited {proc.returncode}"

    for n in (1, 2):
        prompt = tmp / f"slide_{n:02d}" / "_prompt.md"
        assert prompt.exists(), f"missing prompt: {prompt}"
        text = prompt.read_text(encoding="utf-8")
        assert DESIGNER_BRIEF_MARKER in text, (
            f"designer-brief marker missing in {prompt} "
            f"(found {len(text)} chars; head={text[:120]!r})"
        )
        # Sanity: the inlined brief should be substantial.
        assert len(text) > 5000, f"prompt suspiciously small: {len(text)} chars"

    assert (tmp / "dispatch_plan.md").exists()
    assert (tmp / "_meta.json").exists()


@step("simulate agents: copy canned option_X.py into slide dirs")
def copy_canned(tmp: Path):
    for n in (1, 2):
        src_dir = CANNED_ROOT / f"slide_{n:02d}"
        dst_dir = tmp / f"slide_{n:02d}"
        for letter in ("A", "B", "C"):
            src = src_dir / f"option_{letter}.py"
            dst = dst_dir / f"option_{letter}.py"
            shutil.copy2(src, dst)
            assert dst.exists()


@step("part B: run finalize_deck.py")
def part_b(tmp: Path):
    proc = run_py(
        FINALIZE_SCRIPT,
        "--out", str(tmp),
        "--template", str(TEMPLATE),
    )
    assert proc.returncode == 0, f"finalize exited {proc.returncode}"

    result_md = tmp / "RESULT.md"
    assert result_md.exists(), "RESULT.md not written"
    body = result_md.read_text(encoding="utf-8")

    # Pull the counts line ("Built ... **X / Y**") for each metric.
    def count_for(label: str) -> tuple[int, int]:
        m = re.search(rf"{label}.*?\*\*(\d+)\s*/\s*(\d+)\*\*", body)
        assert m, f"could not parse '{label}' count line in RESULT.md"
        return int(m.group(1)), int(m.group(2))

    built_ok, built_total = count_for("Built")
    themed_ok, themed_total = count_for("Themed")
    rendered_ok, rendered_total = count_for("Rendered")

    print(f"  Built    : {built_ok}/{built_total}")
    print(f"  Themed   : {themed_ok}/{themed_total}")
    print(f"  Rendered : {rendered_ok}/{rendered_total}")

    assert (built_ok, built_total) == (6, 6), f"built {built_ok}/{built_total}, want 6/6"
    assert (themed_ok, themed_total) == (6, 6), f"themed {themed_ok}/{themed_total}, want 6/6"
    assert (rendered_ok, rendered_total) == (6, 6), f"rendered {rendered_ok}/{rendered_total}, want 6/6"


@step("part C: run build_review.py")
def part_c(tmp: Path):
    proc = run_py(
        REVIEW_SCRIPT,
        "--out", str(tmp),
    )
    assert proc.returncode == 0, f"review exited {proc.returncode}"

    review = tmp / "REVIEW.html"
    assert review.exists(), "REVIEW.html not written"
    size = review.stat().st_size
    print(f"  REVIEW.html size: {size:,} bytes")
    assert size > 25 * 1024, f"REVIEW.html too small: {size} bytes (want > 25KB)"

    body = review.read_text(encoding="utf-8")
    required_tokens = ["storyline-section", "qc-brief-banner", "card", "feedback-grid"]
    missing = [t for t in required_tokens if t not in body]
    assert not missing, f"REVIEW.html missing tokens: {missing}"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Slide Lab orchestrator smoke test")
    ap.add_argument("--keep", action="store_true", help="Skip cleanup of temp dir")
    args = ap.parse_args()

    print("=" * 72)
    print("SLIDE LAB ORCHESTRATOR SMOKE TEST")
    print("=" * 72)

    tmp = Path(tempfile.mkdtemp(prefix="slidelab_smoke_"))
    print(f"temp dir: {tmp}")
    start = time.time()

    failed = False
    try:
        try:
            preflight()
            part_a(tmp)
            copy_canned(tmp)
            part_b(tmp)
            part_c(tmp)
        except StepFailure:
            failed = True
    finally:
        elapsed = time.time() - start
        print("\n" + "=" * 72)
        print("SUMMARY")
        print("=" * 72)
        for name, ok, err in _results:
            tag = "PASS" if ok else "FAIL"
            extra = f" -- {err}" if err else ""
            print(f"  [{tag}] {name}{extra}")
        all_pass = all(ok for _, ok, _ in _results) and not failed
        print("-" * 72)
        print(f"overall  : {'PASS' if all_pass else 'FAIL'}")
        print(f"elapsed  : {elapsed:.1f}s")
        print(f"temp dir : {tmp}")
        if args.keep:
            print("(kept on disk — --keep flag)")
        else:
            try:
                shutil.rmtree(tmp, ignore_errors=True)
                print("(cleaned up)")
            except Exception as e:
                print(f"(cleanup error, ignored: {e})")
        print("=" * 72)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())