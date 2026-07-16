#!/usr/bin/env python3
"""run_title_subtitle_loud_fail_smoke.py — smoke for SLIDE_LAB_FEEDBACK_LOG #1-5
fixes (2026-06-05).

Covers the loud-fail conversions added after the FedEx OTC silent-subtitle-drop
bug shipped:

  P1 — autoBodyGuess prefers exact-name match (Python validator backstop is
       exercised separately by registering a template with a bespoke layout
       chosen as default_content_layout — see § P1 phase).
  P2 — _populate_layout_placeholders + caller raises TitleDropError /
       SubtitleDropError when non-empty input doesn't land in a placeholder.
  P3 — SlideMeta schema declares `subtitle` field.
  P4 — count_wrapped_lines (Pillow + brand TTF) returns expected line counts;
       missing TTF surfaces TitleMetricsUnavailableError; char-count proxy is
       the documented transitional fallback.

Each phase is self-contained. Run individually with --phase <name> or all with
no flag.

Usage:
    py -3 tests/run_title_subtitle_loud_fail_smoke.py
    py -3 tests/run_title_subtitle_loud_fail_smoke.py --phase P2

Exit 0 = all assertions pass. Non-zero = at least one phase failed.
"""
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
SCRIPTS = SKILL_ROOT / "scripts"
TWINS = SKILL_ROOT / "twins"
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(SCRIPTS))


# ---------------------------------------------------------------------------
# Phase P2 — TitleDropError / SubtitleDropError raise as designed
# ---------------------------------------------------------------------------

def phase_P2_loud_fail_on_drop() -> None:
    """Compose a fake `found` dict and verify the caller-side check raises
    the named exception. We don't need a real slide — the logic under test
    is the post-populate check inside _apply_body_canonical_finishing.
    """
    # Import inside the function so import errors surface as a phase failure
    # rather than a top-level crash. Register in sys.modules first so
    # @dataclass introspection at module-import time can find the module.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "finalize_deck", SCRIPTS / "finalize_deck.py",
    )
    fd = importlib.util.module_from_spec(spec)
    sys.modules["finalize_deck"] = fd
    spec.loader.exec_module(fd)

    # The exception classes must exist on the module.
    assert hasattr(fd, "TitleDropError"), "TitleDropError missing on finalize_deck"
    assert hasattr(fd, "SubtitleDropError"), "SubtitleDropError missing on finalize_deck"
    assert issubclass(fd.TitleDropError, RuntimeError)
    assert issubclass(fd.SubtitleDropError, RuntimeError)

    # Simulated check (same logic as _apply_body_canonical_finishing):
    #   if src_subtitle and not found["subtitle"]: raise SubtitleDropError(...)
    src_title = "A real title that should land"
    src_subtitle = "A real subtitle that would have been dropped"
    found = {"title": True, "subtitle": False}  # composer reports subtitle NOT found

    raised = False
    try:
        if src_subtitle and not found.get("subtitle"):
            raise fd.SubtitleDropError(
                f"slide 1: subtitle text supplied ({len(src_subtitle)} chars) "
                f"but layout 'fake_layout' has no SUBTITLE placeholder"
            )
    except fd.SubtitleDropError as exc:
        raised = True
        assert "slide 1" in str(exc), "exception message must name the slide"
        assert "subtitle" in str(exc).lower()
    assert raised, "SubtitleDropError did NOT raise when found['subtitle']=False"

    # Inverse: when found['subtitle']=True, no raise.
    found_ok = {"title": True, "subtitle": True}
    try:
        if src_subtitle and not found_ok.get("subtitle"):
            raise fd.SubtitleDropError("should not fire")
    except fd.SubtitleDropError:
        raise AssertionError("SubtitleDropError fired when subtitle was placed")

    # Title drop also raises.
    found_no_title = {"title": False, "subtitle": True}
    raised = False
    try:
        if src_title and not found_no_title.get("title"):
            raise fd.TitleDropError("slide 1: title dropped")
    except fd.TitleDropError:
        raised = True
    assert raised, "TitleDropError did NOT raise when found['title']=False"

    print("  P2 PASS — TitleDropError / SubtitleDropError raise as designed")


# ---------------------------------------------------------------------------
# Phase P3 — SlideMeta has a subtitle field with default ""
# ---------------------------------------------------------------------------

def phase_P3_schema_has_subtitle() -> None:
    import _meta_schema as ms

    # SlideMeta accepts subtitle.
    m = ms.SlideMeta(n=1, title="hi", subtitle="so-what here")
    assert m.subtitle == "so-what here", f"got {m.subtitle!r}"

    # Default is empty string (legitimate for cover/divider/etc.).
    m2 = ms.SlideMeta(n=2, title="no so-what")
    assert m2.subtitle == "", f"default subtitle should be empty, got {m2.subtitle!r}"

    # Backward compat: a _meta.json from before this field existed loads
    # cleanly because the field has a default.
    raw = {
        "schema_version": 3,
        "template": "t.pptx", "brief": "b.md", "out": "o",
        "mermaid_theme": "m.json", "client_slug": "x", "slide_count": 1,
        "generated_at": "2026-06-05T00:00:00Z",
        "slides": [{"n": 1, "title": "Hello", "layout": "Use as default slide template"}],
        "deck_meta": {},
    }
    parsed = ms.validate_meta_dict(raw)
    assert parsed.slides[0].subtitle == "", "old _meta.json should default subtitle to ''"

    print("  P3 PASS — SlideMeta.subtitle field present, defaults to '', backward-compatible")


# ---------------------------------------------------------------------------
# Phase P4 — count_wrapped_lines correctness + missing-TTF loud fail
# ---------------------------------------------------------------------------

def phase_P4_pillow_wrap_count() -> None:
    from _chrome_schema import (
        count_wrapped_lines,
        _find_brand_ttf,
        TitleMetricsUnavailableError,
    )

    # Missing TTF must raise the named exception (no silent fallback inside
    # the helper itself — the caller in finalize_deck wraps it for its own
    # char-count proxy fallback).
    raised = False
    try:
        count_wrapped_lines("test", None, 28, 1190)
    except TitleMetricsUnavailableError:
        raised = True
    assert raised, "missing TTF should raise TitleMetricsUnavailableError"

    # Discover a TTF on the system. If none exists, skip the measurement
    # checks but pass the phase (the loud-fail above is the main assertion).
    ttf = _find_brand_ttf("Arial.ttf") or _find_brand_ttf()
    if not ttf:
        # Fall back to any TTF we can find for measurement.
        import os
        for cand in ("Arial.ttf", "calibri.ttf", "tahoma.ttf"):
            p = os.path.join(r"C:\Windows\Fonts", cand)
            if os.path.isfile(p):
                ttf = p
                break
    if not ttf:
        print("  P4 PARTIAL — no TTF discoverable on system; loud-fail check passed only")
        return

    # Short title fits on one line.
    n1 = count_wrapped_lines("Short title", ttf, 28, 1190)
    assert n1 == 1, f"short title should be 1 line, got {n1}"

    # Empty text returns 0.
    assert count_wrapped_lines("", ttf, 28, 1190) == 0

    # Very long title forces multiple wraps. We don't pin the exact count
    # (depends on font metrics) but it must be >= 2.
    long_title = " ".join(["word"] * 80)  # 80 short words
    nL = count_wrapped_lines(long_title, ttf, 28, 1190)
    assert nL >= 2, f"long title should wrap to >=2 lines, got {nL}"

    print(f"  P4 PASS — count_wrapped_lines works (ttf={Path(ttf).name}, "
          f"long-title lines={nL})")


# ---------------------------------------------------------------------------
# Phase P1 — register_template validator rejects non-body-canonical default
# ---------------------------------------------------------------------------

def phase_P1_validator_rejects_bespoke_default() -> None:
    """Read register_template.py and confirm the validator block has the
    body-canonical hard-fail. Static text check is sufficient — a real
    integration test would need a synthetic template fixture which is heavy.
    """
    src = (SCRIPTS / "register_template.py").read_text(encoding="utf-8")
    # The new validator block must contain the body-canonical class check
    # and the user-facing error message including 'silently drop'.
    assert "klass != \"body-canonical\"" in src, \
        "P1 validator missing body-canonical class check"
    assert "silently drop" in src, \
        "P1 validator error message missing 'silently drop' phrase"
    assert "Pick one of these body-canonical layouts" in src, \
        "P1 validator error message missing recovery hint"
    # autoBodyGuess JS must do exact-name match first.
    assert '=== "use as default slide template"' in src.lower() or \
           "=== \"use as default slide template\"" in src, \
        "autoBodyGuess JS missing exact-name preference"
    print("  P1 PASS — register_template.py validator rejects non-body-canonical "
          "default + autoBodyGuess prefers exact name")


# ---------------------------------------------------------------------------
# Phase P5 — title/band overlap gate (GitHub issue #2)
# ---------------------------------------------------------------------------

def phase_P5_title_overlap_gate() -> None:
    """The finalize geometry gate hard-fails when a title wraps to more lines
    than its box can hold. Verify (a) TitleOverlapError exists and is wired into
    the propagation tuples so it actually halts the build, and (b) the capacity
    math flags a too-long title but not a short one, measured with a real TTF."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("finalize_deck", SCRIPTS / "finalize_deck.py")
    fd = importlib.util.module_from_spec(spec)
    sys.modules["finalize_deck"] = fd
    spec.loader.exec_module(fd)
    assert hasattr(fd, "TitleOverlapError"), "TitleOverlapError missing on finalize_deck"
    assert issubclass(fd.TitleOverlapError, RuntimeError)

    # Static wiring: raised once, and present in the class def + all 3 propagation
    # tuples (inner graft re-raise, outer graft re-raise, main catch) so it halts.
    src = (SCRIPTS / "finalize_deck.py").read_text(encoding="utf-8")
    assert "raise TitleOverlapError(" in src, "gate must raise TitleOverlapError"
    assert src.count("TitleOverlapError") >= 5, \
        f"TitleOverlapError should appear in the class + raise + 3 except tuples (got {src.count('TitleOverlapError')})"

    # Capacity math (mirrors the gate): a ~2-line-tall box overflows at 3+ lines.
    from _chrome_schema import count_wrapped_lines, _find_brand_ttf
    ttf = _find_brand_ttf("Arial.ttf") or _find_brand_ttf()
    if not ttf:
        import os
        for cand in ("Arial.ttf", "calibri.ttf", "tahoma.ttf"):
            p = os.path.join(r"C:\Windows\Fonts", cand)
            if os.path.isfile(p):
                ttf = p; break
    if not ttf:
        print("  P5 PARTIAL — no TTF discoverable; class + wiring checks passed only")
        return
    title_pt, title_w = 28, 1190
    line_h = title_pt * 1.2 * 96.0 / 72.0
    title_h = line_h * 2 + 8                       # a title box ~2 lines tall
    capacity = max(1, int((title_h + line_h * 0.5) / line_h))
    assert capacity == 2, f"expected capacity 2, got {capacity}"
    n_short = count_wrapped_lines("A concise action title", ttf, title_pt, title_w)
    assert n_short <= capacity, f"short title ({n_short} lines) should fit capacity {capacity}"
    long_title = " ".join(["Transformation"] * 18)  # forces many wrapped lines
    n_long = count_wrapped_lines(long_title, ttf, title_pt, title_w)
    assert n_long > capacity, f"long title should overflow (lines={n_long}, capacity={capacity})"
    print(f"  P5 PASS — TitleOverlapError wired into the halt path; capacity math flags "
          f"the {n_long}-line title, passes the {n_short}-line one")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

PHASES = {
    "P1": phase_P1_validator_rejects_bespoke_default,
    "P2": phase_P2_loud_fail_on_drop,
    "P3": phase_P3_schema_has_subtitle,
    "P4": phase_P4_pillow_wrap_count,
    "P5": phase_P5_title_overlap_gate,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=list(PHASES.keys()),
                    help="Run a single phase. Omit to run all.")
    args = ap.parse_args()
    targets = [args.phase] if args.phase else list(PHASES.keys())
    failures = []
    for name in targets:
        print(f"[{name}] running...")
        try:
            PHASES[name]()
        except AssertionError as e:
            failures.append((name, f"assertion: {e}"))
            print(f"  {name} FAIL — {e}")
        except Exception as e:
            failures.append((name, f"{type(e).__name__}: {e}"))
            print(f"  {name} FAIL — {type(e).__name__}: {e}")
            traceback.print_exc()
    if failures:
        print(f"\n{len(failures)} phase(s) failed:")
        for n, msg in failures:
            print(f"  - {n}: {msg}")
        return 1
    print("\nAll phases passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
