#!/usr/bin/env python3
"""Smoke test: the parent's direct edit (owner's decision, 2026-10-09).

For a color, a font size or wording the user gave word for word, on a
direct-path page (the picked option_X.py), the main session may edit the
script itself, no worker. It is recorded and listed at delivery.

  1. before compile: record_picks.py --edits-done --edited-by-parent "2: ..."
     refuses an unchanged design and a slide not waiting on an edit; after the
     edit it marks the comment applied "by the parent", records the edit and
     prints the look-at-the-picture reminder
  2. after compile: apply_qc_fix.py --approved ... --edited-by-parent "..."
     compiles, records the edit and lists the new pictures to look at; it is
     refused with --auto, and for a sketch page (the worker route stays)
  3. check_done lists every edit as "edited by parent"

Run:  py -3 slide-builder/tests/run_parent_edit_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))
import _e2e_harness as H  # noqa: E402
import _state  # noqa: E402
import check_done  # noqa: E402
import record_picks as RP  # noqa: E402


def _message(out: Path, picks: dict, feedback: str = "") -> str:
    body = _state.canonical_picks(picks)
    tok = _state.read_state(out)["review"]["token"]
    plain = " ".join(f"{int(k.split('_')[1])}{v}" for k, v in sorted(picks.items()))
    return (f"Build my Slide Lab deck.\nFolder: {out}\n"
            f"Picks: {plain} (check {_state.approval_check(tok, body)})\n{feedback}")


def _edit(out: Path, n: int, size: int) -> None:
    time.sleep(1.1)   # the design stamp has one-second resolution
    H.write_option(out, n, "A", body=H.OPTION_SCRIPT.format(
        n=n, L="A", skill=str(H.SKILL)).replace("font_size_pt=18", f"font_size_pt={size}"))


def main() -> int:
    saved = os.environ.get("SLIDE_LAB_TRANSLATOR")
    os.environ["SLIDE_LAB_TRANSLATOR"] = "script"
    tmp, out = H.new_build(3)
    try:
        H.write_option(out, 1, "A")
        H.write_option(out, 2, "A")
        H.write_sketch(out, 3, "A")
        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out).returncode == 0
        picks = {"slide_01": "A", "slide_02": "A", "slide_03": "A"}
        r = H.run("record_picks.py", "--out", out, "--approved", _message(
            out, picks, "Feedback:\n  slide_02:\n    other: make the text 16 pt\n"))
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-800:]
        assert [c["slide"] for c in _state.pending_comments(_state.read_state(out), "edit")] \
            == ["slide_02"]
        H.agent_finishes(out / "slide_03" / "option_A_native.py")

        print("[1] before compile: --edits-done --edited-by-parent")
        r = H.run("record_picks.py", "--out", out, "--edits-done",
                  "--edited-by-parent", "2: text to 16 pt")
        assert r.returncode == 5 and "has not changed" in r.stdout, r.stdout[-800:]
        _edit(out, 2, 16)
        r = H.run("record_picks.py", "--out", out, "--edits-done",
                  "--edited-by-parent", "1: text to 16 pt")
        assert r.returncode == 5 and "not waiting on an edit" in r.stdout, r.stdout[-800:]
        r = H.run("record_picks.py", "--out", out, "--edited-by-parent", "2: x")
        assert r.returncode == 2, r.stdout[-800:]
        got, why = RP._parent_edits(out, ["3: bar color"], ["slide_03"], picks)
        assert got is None and "sketch pages keep the worker" in why, why
        r = H.run("record_picks.py", "--out", out, "--edits-done",
                  "--edited-by-parent", "2: body text to 16 pt, as the user wrote")
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-800:]
        assert "colors can be told apart" in r.stdout, r.stdout[-1500:]
        st = _state.read_state(out)
        pe = st.get("parent_edits") or []
        assert len(pe) == 1 and pe[0]["slides"] == "slide_02" and "16 pt" in pe[0]["what"], pe
        c = st["comments"][0]
        assert c["status"] == "applied" and "by the parent" in c["applied_how"], c
        print("    ok: refused unchanged / not waiting / sketch; recorded after the edit")

        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out, "--final").returncode == 0
        ftok = _state.read_state(out)["final_check"]["token"]
        r = H.run("compile_picks.py", "--out", out, "--final-token", ftok)
        assert r.returncode == 0, r.stdout[-1500:]

        print("[2] after compile: apply_qc_fix.py --approved --edited-by-parent")
        r = H.run("apply_qc_fix.py", "--out", out, "--slides", "1", "--auto",
                  "slide 1 [text_size] Major: x", "--edited-by-parent", "title 28 pt")
        assert r.returncode == 2, r.stdout[-800:]
        r = H.run("apply_qc_fix.py", "--out", out, "--slides", "3",
                  "--approved", "make the bar teal", "--edited-by-parent", "bar to brand Teal")
        assert r.returncode == 5 and "sketch page" in r.stdout, r.stdout[-800:]
        _edit(out, 1, 14)
        r = H.run("apply_qc_fix.py", "--out", out, "--slides", "1",
                  "--approved", "make the body 14 pt", "--edited-by-parent", "body text to 14 pt")
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-800:]
        assert "colors can be told apart" in r.stdout and "slide_01" in r.stdout, r.stdout[-1500:]
        st = _state.read_state(out)
        pe = st.get("parent_edits") or []
        assert len(pe) == 2 and pe[1]["slides"] == "1" and \
            pe[1]["words"] == "make the body 14 pt", pe
        print("    ok: refused with --auto and on a sketch page; recorded and compiled")

        print("[3] the delivery list")
        lines = "\n".join(check_done.parent_edit_lines(pe))
        assert "edited by parent" in lines and "16 pt" in lines and "14 pt" in lines, lines
        print("    ok")
    finally:
        if saved is None:
            os.environ.pop("SLIDE_LAB_TRANSLATOR", None)
        else:
            os.environ["SLIDE_LAB_TRANSLATOR"] = saved
        H.cleanup(tmp)
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
