#!/usr/bin/env python3
"""Smoke test: automatic QC fixes (owner's decision, 2026-10-09).

A fictional 3-slide deck with one Critical, two layout Majors and one content
Major:

  1. qc_fix_policy classes the Critical and the two layout Majors "auto" and
     the content Major "ask" (tags and untagged text both)
  2. apply_qc_fix.py --auto refuses the content finding (the user decides it)
     and refuses a slide whose design was not kept first (--snapshot)
  3. after --snapshot and the rebuild, --auto fixes the three without any
     approval: recorded as an automatic fix with the finding text (not as a
     chat approval), the deck compiled, before/after pictures printed
  4. a second automatic round runs; a third is refused
  5. "undo slide 1" restores slide 1's design from before its fix, byte for
     byte, compiles, and the record says it was undone
  6. the delivery list (check_done) shows "fixed automatically" with the
     findings and the undo

Run:  py -3 slide-builder/tests/run_auto_qc_fix_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))
import _e2e_harness as H  # noqa: E402
import _state  # noqa: E402
import check_done  # noqa: E402
import qc_fix_policy as P  # noqa: E402

CRIT = "slide 1 [overflow] Critical: body text cut off at the bottom edge"
MAJ1 = "slide 2 [text_size] Major: body text under the size floor"
MAJ2 = "slide 3 Major: an arrowhead runs into the box it points at"
CONTENT = "slide 3 Major: the 42 percent figure is not in the brief"


def _rebuild(out: Path, n: int, size: int) -> None:
    """Stand in for the one-design rebuild of a flagged slide."""
    time.sleep(1.1)
    body = H.OPTION_SCRIPT.format(n=n, L="A", skill=str(H.SKILL)).replace(
        "font_size_pt=18", f"font_size_pt={size}")
    H.write_option(out, n, "A", body=body)


def main() -> int:
    print("[1] the policy: Critical + layout Majors automatic, content Major asked")
    rows = P.classify("; ".join([CRIT, MAJ1, MAJ2, CONTENT]))
    assert [r["decision"] for r in rows] == ["auto", "auto", "auto", "ask"], rows
    assert rows[2]["category"] == "arrow_into_box" and rows[3]["category"] == \
        "number_not_in_brief", rows
    assert P.decide("slide 4 Major: headline is a topic label")[0] == "ask"
    assert P.decide("slide 4 Major: something nobody listed")[0] == "ask"
    assert P.decide("slide 4 Advisory: whitespace uneven")[0] == "none"
    print("    ok")

    tmp, out = H.new_build(3)
    try:
        for n in (1, 2, 3):
            H.write_option(out, n, "A")
        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out).returncode == 0
        body = _state.canonical_picks({f"slide_{n:02d}": "A" for n in (1, 2, 3)})
        tok = _state.read_state(out)["review"]["token"]
        r = H.run("record_picks.py", "--out", out, "--approved",
                  f"PICKS {body} CHECK {_state.approval_check(tok, body)}")
        assert r.returncode == 0, r.stdout[-1200:]
        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out, "--final").returncode == 0
        ftok = _state.read_state(out)["final_check"]["token"]
        assert H.run("compile_picks.py", "--out", out, "--final-token", ftok).returncode == 0
        original = (out / "slide_01" / "option_A.py").read_bytes()

        print("[2] the content finding and a slide with no kept design are refused")
        r = H.run("apply_qc_fix.py", "--out", out, "--slides", "3", "--auto", CONTENT)
        assert r.returncode == 5 and "not automatic fixes" in r.stdout, r.stdout[-800:]
        r = H.run("apply_qc_fix.py", "--out", out, "--slides", "1", "--auto", CRIT)
        assert r.returncode == 5 and "--snapshot" in r.stdout, r.stdout[-800:]
        print("    ok")

        print("[3] round 1: the three automatic findings fixed without approval")
        r = H.run("apply_qc_fix.py", "--out", out, "--slides", "1,2,3", "--snapshot")
        assert r.returncode == 0, r.stdout[-800:]
        for n in (1, 2, 3):
            _rebuild(out, n, 16)
        r = H.run("apply_qc_fix.py", "--out", out, "--slides", "1,2,3",
                  "--auto", "; ".join([CRIT, MAJ1, MAJ2]))
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-800:]
        assert "before" in r.stdout and "after" in r.stdout, r.stdout[-1200:]
        st = _state.read_state(out)
        fixes = st.get("auto_fixes") or []
        assert len(fixes) == 1 and fixes[0]["round"] == 1, fixes
        assert "cut off" in fixes[0]["findings"] and "arrowhead" in fixes[0]["findings"]
        assert "42 percent" not in fixes[0]["findings"]
        assert not [a for a in st.get("chat_approvals") or [] if a["kind"] == "qc_fix"], \
            "an automatic fix was recorded as the user's approval"
        assert _state.compiled_deck(out).exists()
        print("    ok: recorded as fixed automatically, deck compiled")

        print("[4] round 2 runs; a third round is refused")
        assert H.run("apply_qc_fix.py", "--out", out, "--slides", "2",
                     "--snapshot").returncode == 0
        _rebuild(out, 2, 14)
        r = H.run("apply_qc_fix.py", "--out", out, "--slides", "2", "--auto", MAJ1)
        assert r.returncode == 0, r.stdout[-1500:]
        assert H.run("apply_qc_fix.py", "--out", out, "--slides", "2",
                     "--snapshot").returncode == 0
        r = H.run("apply_qc_fix.py", "--out", out, "--slides", "2", "--auto", MAJ1)
        assert r.returncode == 5 and "automatic rounds are done" in r.stdout, r.stdout[-800:]
        assert len(_state.read_state(out)["auto_fixes"]) == 2
        print("    ok")

        print("[5] undo slide 1 restores its design from before the fix")
        r = H.run("apply_qc_fix.py", "--out", out, "--undo", "1", "--approved", "undo slide 1")
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-800:]
        assert (out / "slide_01" / "option_A.py").read_bytes() == original, \
            "slide 1 is not the design from before its fix"
        st = _state.read_state(out)
        assert "slide_01" in st["auto_fixes"][0].get("undone_slides", []), st["auto_fixes"][0]
        print("    ok")

        print("[6] the delivery list")
        lines = "\n".join(check_done.auto_fix_lines(st["auto_fixes"]))
        assert "fixed automatically" in lines and "cut off" in lines, lines
        assert "undone by the user on slide_01" in lines, lines
        print("    ok")
    finally:
        H.cleanup(tmp)
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
