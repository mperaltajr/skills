#!/usr/bin/env python3
"""Smoke test: finalize names pending work and says plainly when it refused
(items A1 and A2 of the 2026-10-06 session report).

A1: with no picks recorded and two options already converted but waiting on
the translator agent, finalize said "3 sketch design(s) not converted (nobody
has picked yet) ... nothing to do" and exited 0, over two half-converted
options. A2: its refusals went only to the error stream, so with that stream
filtered a refused run looked like a rebuild, and an old picture nearly passed
for the fixed one.

  1. sketches with no picks and nothing converted: exit 0, and the output says
     the next step (the user picks) instead of "nothing to do"
  2. options B and C converted before any pick, waiting on the agent: exit 11,
     the normal output names slide 1 option B and option C and the next step,
     and ends with a plain REFUSED line
  3. once the picks are recorded and the agent has finished, finalize passes
     with no REFUSED line

Run:  py -3 slide-builder/tests/run_finalize_pending_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))
import _e2e_harness as H  # noqa: E402
import _state  # noqa: E402


def main() -> int:
    saved = os.environ.get("SLIDE_LAB_TRANSLATOR")
    os.environ["SLIDE_LAB_TRANSLATOR"] = "script"
    tmp, out = H.new_build(1)
    try:
        sd = out / "slide_01"
        for L in "ABC":
            H.write_sketch(out, 1, L, text=f"Design {L}.")

        print("[1] no picks, nothing converted: says the next step")
        r = H.finalize(out)
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-800:]
        assert "nothing to do" not in r.stdout, r.stdout[-800:]
        assert "until the user picks" in r.stdout and "record_picks.py" in r.stdout, \
            r.stdout[-800:]
        assert "REFUSED" not in r.stdout
        print("    ok")

        print("[2] B and C converted before any pick, waiting on the agent")
        for L in "BC":
            r = H.run("translate_html.py", "--out", out, "--slide", "1", "--letter", L)
            assert (sd / f"option_{L}_native.py").exists(), r.stdout[-800:] + r.stderr[-800:]
            assert "# FALLBACK_PENDING:" in (sd / f"option_{L}_native.py").read_text(
                encoding="utf-8")
        r = H.finalize(out)
        assert r.returncode == 11, f"exit {r.returncode}\n{r.stdout[-1500:]}"
        assert "nothing to do" not in r.stdout, r.stdout[-1500:]
        assert "slide 1 option B" in r.stdout and "slide 1 option C" in r.stdout, \
            r.stdout[-1500:]
        assert "option A" not in r.stdout.split("waiting on the translator agent")[1], \
            "the unconverted, unpicked option A is not pending work"
        assert "next: record the user's picks" in r.stdout, r.stdout[-1500:]
        assert "FALLBACK MODE" in r.stdout
        last = [ln for ln in r.stdout.splitlines() if ln.strip()][-1]
        assert last.startswith("REFUSED (exit 11): nothing rebuilt"), last
        assert "converted before the user's picks were recorded" in r.stderr, r.stderr[-800:]
        print(f"    ok: exit 11; last line: {last[:60]}...")

        print("[3] picks recorded and the agent finished: finalize passes")
        assert H.run("build_review.py", "--out", out).returncode == 0
        tok = _state.read_state(out)["review"]["token"]
        r = H.run("record_picks.py", "--out", out, "--approved",
                  f"Picks: 1BC (check {_state.approval_check(tok, 'slide_01=BC')})")
        assert r.returncode == 0, r.stdout
        for L in "BC":
            H.agent_finishes(sd / f"option_{L}_native.py")
        r = H.finalize(out)
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-800:]
        assert "REFUSED" not in r.stdout
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
