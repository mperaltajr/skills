#!/usr/bin/env python3
"""Smoke test: a one-option redesign skips the second picking page.

  1. start refuses a Keep line whose check code does not match
  2. start records the kept pick; the slide is rebuilt with one option
  3. finish picks the single new design, keeps slide 1's pick, finalizes,
     writes FINAL-CHECK.html, and records the shortcut as an override
  4. finish refuses when a redesigned slide has two options
  5. --keep-previous ("rebuild slide N" on a built deck) keeps the other
     slides' picks from picks.json

Run:  py -3 slide-builder/tests/run_redesign_round_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))
import _e2e_harness as H  # noqa: E402
import _state  # noqa: E402


def main() -> int:
    tmp, out = H.new_build(2)
    try:
        H.write_option(out, 1, "A")
        H.write_option(out, 2, "A")
        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out).returncode == 0
        tok = _state.read_state(out)["review"]["token"]
        kept_body = "slide_01=A"
        good = f"Keep: 1A (check {_state.approval_check(tok, kept_body)})"

        print("[1] a Keep line with the wrong check code is refused")
        r = H.run("redesign_round.py", "start", "--out", out, "--slides", "2",
                  "--kept", "Keep: 1B (check " + _state.approval_check(tok, kept_body) + ")")
        assert r.returncode == 5, r.stdout
        print("    ok")

        print("[2] start records the kept pick; slide 2 is rebuilt with one option")
        r = H.run("redesign_round.py", "start", "--out", out, "--slides", "2", "--kept", good)
        assert r.returncode == 0, r.stdout
        r = H.run("build_deck.py", "--slide", "2", "--out", out, "--template", H.TEMPLATE,
                  "--pattern", "direct")
        assert r.returncode == 0, r.stdout[-1200:] + r.stderr[-600:]
        H.write_option(out, 2, "A")
        assert H.finalize(out, "--slide", "2").returncode == 0

        print("[4] finish refuses when the redesign has two options")
        H.write_option(out, 2, "B")
        r = H.run("redesign_round.py", "finish", "--out", out)
        assert r.returncode == 5 and "2 options" in r.stdout, r.stdout
        for p in (out / "slide_02").glob("option_B*"):
            p.unlink()
        print("    ok")

        print("[3] finish goes straight to the final check")
        r = H.run("redesign_round.py", "finish", "--out", out)
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-800:]
        st = _state.read_state(out)
        assert st["review"]["picks"] == {"slide_01": "A", "slide_02": "A"}, st["review"]
        assert (out / "FINAL-CHECK.html").exists()
        assert st.get("final_check", {}).get("token"), "no final-check record"
        assert any(o["override"] == "single_option_redesign_picked" for o in st.get("overrides", []))
        assert "redesign_round" not in st
        print("    ok: picks kept + new design picked, FINAL-CHECK.html written")

        print("[5] rebuild slide N on a built deck keeps the other picks from picks.json")
        (out / "picks.json").write_text('{"slide_01": "A", "slide_02": "A"}', encoding="utf-8")
        r = H.run("redesign_round.py", "start", "--out", out, "--slides", "1", "--keep-previous")
        assert r.returncode == 0, r.stdout
        assert _state.read_state(out)["redesign_round"]["kept"] == {"slide_02": "A"}
        r = H.run("build_deck.py", "--slide", "1", "--out", out, "--template", H.TEMPLATE,
                  "--pattern", "direct")
        assert r.returncode == 0, r.stdout[-1200:] + r.stderr[-600:]
        H.write_option(out, 1, "A")
        assert H.finalize(out, "--slide", "1").returncode == 0
        r = H.run("redesign_round.py", "finish", "--out", out)
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-800:]
        assert _state.read_state(out)["review"]["picks"] == {"slide_01": "A", "slide_02": "A"}
        print("    ok")
    finally:
        H.cleanup(tmp)
    _agent_part_survives()
    print("SMOKE PASSED.")


def _agent_part_survives() -> None:
    """[6] finish does not convert again a redesign the translator agent
    finished (2026-10-06: it did, erased the agent's drawing, exited 3 again)."""
    import os
    print("[6] finish keeps a redesign the translator agent finished")
    saved = os.environ.get("SLIDE_LAB_TRANSLATOR")
    os.environ["SLIDE_LAB_TRANSLATOR"] = "script"
    tmp, out = H.new_build(2)
    try:
        native = out / "slide_02" / "option_A_native.py"
        H.write_option(out, 1, "A")
        H.write_sketch(out, 2, "A")
        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out).returncode == 0
        tok = _state.read_state(out)["review"]["token"]
        body = _state.canonical_picks({"slide_01": "A", "slide_02": "A"})
        r = H.run("record_picks.py", "--out", out, "--approved",
                  f"PICKS {body} CHECK {_state.approval_check(tok, body)}")
        assert r.returncode == 0 and native.exists(), r.stdout[-1200:]
        H.agent_finishes(native)
        assert H.finalize(out).returncode == 0

        r = H.run("redesign_round.py", "start", "--out", out, "--slides", "2", "--keep-previous")
        assert r.returncode == 0, r.stdout
        H.write_sketch(out, 2, "A", text="The redesigned note.")
        r = H.run("redesign_round.py", "finish", "--out", out)
        assert r.returncode == 3, r.stdout[-1500:]
        finished = H.agent_finishes(native)
        r = H.run("redesign_round.py", "finish", "--out", out)
        assert r.returncode == 0, (
            f"exit {r.returncode}: the finished redesign was converted again "
            f"(the loop)\n{r.stdout[-1500:]}")
        assert native.read_text(encoding="utf-8") == finished, \
            "the agent's drawing was rewritten"
        assert (out / "FINAL-CHECK.html").exists()
        print("    ok: second finish exit 0, the agent's part byte-identical")
    finally:
        if saved is None:
            os.environ.pop("SLIDE_LAB_TRANSLATOR", None)
        else:
            os.environ["SLIDE_LAB_TRANSLATOR"] = saved
        H.cleanup(tmp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
