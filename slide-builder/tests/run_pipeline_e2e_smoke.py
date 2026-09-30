#!/usr/bin/env python3
"""End-to-end smoke: the real scripts, run in order, on the bundled template.

Every other smoke calls functions with hand-built state. This runs prep, a
worker-shaped option script per slide, finalize, review and compile as separate
processes, the way a build does, and checks that what each stage records is
what actually happened.

Cases (each one shipped, or could have shipped, a wrong deck before):
  1. clean build: finalize records every option, compile succeeds
  2. finalize never ran: compile refuses
  3. an option script crashes: finalize exits non-zero, records that option as
     blocked by name, and compile refuses to ship it
  4. finalize --slide 1 after that must NOT wipe slide 2's block
  5. a sketch slide with HTML but no native script: exit 11 says to run the
     translator, not the worker

Run:  py -3 slide-builder/tests/run_pipeline_e2e_smoke.py   (about a minute)
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))

import _e2e_harness as H  # noqa: E402
import _state  # noqa: E402

CRASHING_SCRIPT = "# Slide 2 option A — crashes on purpose\nraise RuntimeError('boom')\n"


def _review_and_pick(out: Path, picks: dict) -> str:
    r = H.run("build_review.py", "--out", out)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    token = (_state.read_state(out).get("review") or {}).get("token")
    assert token, "build_review did not mint a token"
    (out / "picks.json").write_text(json.dumps(picks), encoding="utf-8")
    return token


def _compile(out: Path, token: str):
    return H.run("compile_picks.py", "--out", out, "--picks", out / "picks.json",
                 "--review-token", token)


def main() -> int:
    print("[1] clean build compiles, and finalize records every option")
    tmp, out = H.new_build(2)
    try:
        print("[2] compile before finalize is refused")
        H.write_option(out, 1)
        H.write_option(out, 2)
        tok = _review_and_pick(out, {"slide_01": "A", "slide_02": "A"})
        r = _compile(out, tok)
        assert r.returncode == 5 and "has not run" in r.stdout, r.stdout[-800:]
        print("    ok: refused with nothing finalized")

        r = H.finalize(out)
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
        st = _state.read_state(out)
        assert st["finalize"]["status"] == "ok", st["finalize"]
        assert set(st["qc"]["by_option"]) == {"slide_01/A", "slide_02/A"}, st["qc"]
        tok = _review_and_pick(out, {"slide_01": "A", "slide_02": "A"})
        r = _compile(out, tok)
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
        assert (out / "final_deck.pptx").exists()
        comp = _state.read_state(out)["stages"]["compile"]
        assert comp["kind"] == "picks" and comp["slides"] == 2 and comp["digest"], comp
        print("    ok: finalize status ok, two option records, compile exit 0, "
              "compile recorded with its output and slide count")

        print("[1a] vision pass + check_done over the real compiled deck")
        deck = out / "final_deck.pptx"
        r = H.run("check_done.py", "--out", out)
        assert r.returncode == 1 and "no vision pass" in r.stdout, r.stdout
        r = H.run("record_vision_qc.py", "--out", out, "--deck", deck,
                  "--slides-reviewed", 2, "--criticals", 0, "--majors", 0,
                  "--advisories", 1)
        assert r.returncode == 0, r.stdout + r.stderr
        r = H.run("check_done.py", "--out", out)
        assert r.returncode == 0 and "DELIVERABLE (final deck)" in r.stdout, r.stdout
        print("    ok: refused before the vision pass, deliverable after")

        print("[1b] a partial pick is refused; --drop makes the omission explicit")
        good_digest = _state.file_digest(out / "final_deck.pptx")
        tok = _review_and_pick(out, {"slide_01": "A"})
        r = _compile(out, tok)
        assert r.returncode == 5 and "slide 2" in r.stdout, r.stdout[-800:]
        assert _state.file_digest(out / "final_deck.pptx") == good_digest, (
            "a refused compile touched the previous deck")
        r = H.run("compile_picks.py", "--out", out, "--picks", out / "picks.json",
                  "--review-token", tok, "--drop", "2")
        assert r.returncode == 0, r.stdout[-1500:]
        assert _state.read_state(out)["stages"]["compile"]["slides"] == 1
        print("    ok: refused without a pick for slide 2; --drop 2 compiles a 1-slide deck")

        print("[1c] a deck that fails its integrity check never replaces the good one")
        good_digest = _state.file_digest(out / "final_deck.pptx")
        tok = _review_and_pick(out, {"slide_01": "A", "slide_02": "A"})
        import contextlib, io, os
        import compile_picks
        _orig = compile_picks._report_integrity
        compile_picks._report_integrity = lambda p: 6   # force the failure
        argv = sys.argv
        sys.argv = ["compile_picks.py", "--out", str(out), "--picks",
                    str(out / "picks.json"), "--review-token", tok]
        os.environ["SLIDE_LAB_OPTIONS_PER_SLIDE"] = "1"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = compile_picks.main()
        finally:
            compile_picks._report_integrity = _orig
            sys.argv = argv
        assert rc == 6, rc
        assert _state.file_digest(out / "final_deck.pptx") == good_digest, (
            "the good deck was replaced by one that failed the check")
        assert (out / "final_deck.REJECTED.pptx").exists()
        assert not (out / "final_deck.incoming.pptx").exists()
        print("    ok: exit 6, previous final_deck.pptx untouched, rejected file set aside")
    finally:
        H.cleanup(tmp)

    print("[3] a crashing option script is recorded as blocked, by name")
    tmp, out = H.new_build(2)
    try:
        H.write_option(out, 1)
        H.write_option(out, 2, body=CRASHING_SCRIPT)
        r = H.finalize(out)
        assert r.returncode == 15, f"expected exit 15, got {r.returncode}\n{r.stdout[-1500:]}"
        by = _state.read_state(out)["qc"]["by_option"]
        assert by["slide_02/A"]["blocks"] > 0, by
        assert "did not build" in " ".join(by["slide_02/A"]["reasons"]), by
        assert by["slide_01/A"]["blocks"] == 0, by
        tok = _review_and_pick(out, {"slide_01": "A", "slide_02": "A"})
        r = _compile(out, tok)
        assert r.returncode == 5 and "slide_02/A" in r.stdout, r.stdout[-800:]
        print("    ok: exit 15, slide_02/A blocked, compile refuses naming it")

        print("[4] finalize --slide 1 must not wipe slide 2's block")
        r = H.finalize(out, "--slide", "1")
        assert r.returncode == 0, r.stdout[-1500:]
        by = _state.read_state(out)["qc"]["by_option"]
        assert by.get("slide_02/A", {}).get("blocks", 0) > 0, (
            f"slide 2's block vanished after finalize --slide 1: {by}")
        tok = _review_and_pick(out, {"slide_01": "A", "slide_02": "A"})
        r = _compile(out, tok)
        assert r.returncode == 5 and "slide_02/A" in r.stdout, r.stdout[-800:]
        print("    ok: slide 2 still blocked, compile still refuses")
    finally:
        H.cleanup(tmp)

    print("[4b] a rebuild moves the old option files aside")
    tmp, out = H.new_build(2)
    try:
        H.write_option(out, 1)
        H.write_option(out, 2)
        assert H.finalize(out).returncode == 0
        brief = tmp / "brief.md"
        r = H.run("build_deck.py", "--brief", brief, "--template", H.TEMPLATE,
                  "--out", out, "--pattern", "direct", "--confirm-template", "--slide", "2")
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
        left = sorted(p.name for p in (out / "slide_02").glob("option_*"))
        assert left == [], f"old option files left in place after a rebuild: {left}"
        assert list((out / "slide_02" / "_prev").glob("*/option_A.py")), "not kept in _prev"
        r = H.finalize(out, "--slide", "2")
        assert r.returncode == 11, (
            "with the old files gone, finalize must report slide 2 as missing, not "
            f"quietly rebuild the old design (exit {r.returncode})")
        print("    ok: old files in _prev/, finalize waits for the new design")
    finally:
        H.cleanup(tmp)

    print("[5] a designed-but-untranslated sketch slide points at the translator")
    tmp, out = H.new_build(2)
    try:
        H.write_option(out, 1)
        (out / "slide_02" / "option_A.html").write_text("<html></html>", encoding="utf-8")
        r = H.finalize(out)
        assert r.returncode == 11, r.returncode
        msg = r.stdout + r.stderr
        assert "slide-builder-translator" in msg and "slide_02/option_A" in msg, msg[-1200:]
        print("    ok: exit 11 names the translator for slide_02/option_A")
    finally:
        H.cleanup(tmp)

    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
