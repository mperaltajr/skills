#!/usr/bin/env python3
"""Smoke test: compile leaves ONE deck at the top of the folder, named after
the topic, and removes clearly temporary files on its own (2026-10-08).

  - the deck is written once as "<topic>.pptx" (the brief's title); no
    final_deck.pptx copy beside it; the path is recorded and
    _state.compiled_deck() finds it; check_done and record_vision_qc (with no
    --deck) work on it
  - after the compile: render scratch (_qc_tmp/, _qc_pre/, _render_tmp/,
    _raw/ at the top and in slide folders) and the options the user did not
    pick (and their img/ pictures) are gone; the picked option keeps all its
    files; _meta.json lists only the picked letters; _qc/ is kept; the output
    has a one-line folder size report
  - a later compile on a folder from an older build (final_deck.pptx copy,
    final_deck.REJECTED.pptx, several old decks) leaves one deck at the top,
    removes the rejected file, and keeps one previous version in
    _session/old-decks/
  - finalize still runs after the cleanup (the deck stays editable)

Run:  py -3 slide-builder/tests/run_one_deck_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))
import _e2e_harness as H  # noqa: E402
import _state  # noqa: E402


def _line(token: str, picks) -> str:
    body = _state.canonical_picks(picks)
    return f"PICKS {body} CHECK {_state.approval_check(token, body)}"


def _record(out: Path, picks) -> None:
    r = H.run("build_review.py", "--out", out)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    token = _state.read_state(out)["review"]["token"]
    r = H.run("record_picks.py", "--out", out, "--approved", _line(token, picks))
    assert r.returncode == 0, r.stdout[-1500:]


def _final_and_compile(out: Path):
    r = H.run("build_review.py", "--out", out, "--final")
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    tok = _state.read_state(out)["final_check"]["token"]
    return H.run("compile_picks.py", "--out", out, "--final-token", tok)


def main() -> int:
    tmp, out = H.new_build(2)
    try:
        H.write_option(out, 1, "A")
        H.write_option(out, 1, "B")
        H.write_option(out, 2, "A")
        meta = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
        for s in meta["slides"]:
            s["options"] = ["A", "B"] if s["n"] == 1 else ["A"]
        (out / "_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        r = H.finalize(out)
        assert r.returncode == 0, r.stdout[-1500:]
        picks = {"slide_01": "A", "slide_02": "A"}
        _record(out, picks)
        # leftovers a build makes
        img = out / "slide_01" / "img"
        img.mkdir(exist_ok=True)
        (img / "A_pic.png").write_bytes(b"x" * 100)
        (img / "B_pic.png").write_bytes(b"x" * 100)
        for d in ("_qc_tmp", "_qc_pre", "_render_tmp", "_qc"):
            (out / d).mkdir(exist_ok=True)
            (out / d / "slide_01.png").write_bytes(b"x" * 1000)
        assert (out / "slide_01" / "_raw").is_dir(), "finalize should leave a _raw archive"

        print("[1] compile writes one deck, named after the topic")
        r = _final_and_compile(out)
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-1500:]
        decks = sorted(p.name for p in out.glob("*.pptx"))
        assert decks == ["Pipeline test.pptx"], decks
        assert _state.compiled_deck(out) == (out / "Pipeline test.pptx").resolve(), _state.compiled_deck(out)
        assert "deck to share:" in r.stdout and "Pipeline test.pptx" in r.stdout
        print("    ok:", decks)

        print("[2] compile removed render scratch and the option not picked")
        assert "folder size" in r.stdout and "MB ->" in r.stdout, r.stdout[-800:]
        for gone in ("_qc_tmp", "_qc_pre", "_render_tmp", "slide_01/_raw", "slide_02/_raw",
                     "slide_01/img/B_pic.png"):
            assert not (out / gone).exists(), gone
        assert not list((out / "slide_01").glob("option_B*")), "the unpicked option is still there"
        for kept in ("_qc/slide_01.png", "slide_01/option_A.py", "slide_01/option_A.pptx",
                     "slide_01/img/A_pic.png", "slide_01/_prompt.md"):
            assert (out / kept).exists(), kept
        meta = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
        assert next(s for s in meta["slides"] if s["n"] == 1)["options"] == ["A"]
        print("    ok")

        print("[3] the recorded deck is what check_done and record_vision_qc use")
        r = H.run("record_vision_qc.py", "--out", out, "--slides-reviewed", 2,
                  "--criticals", 0, "--majors", 0)
        assert r.returncode == 0, r.stdout + r.stderr
        r = H.run("check_done.py", "--out", out)
        assert r.returncode == 0 and "Pipeline test.pptx" in r.stdout, r.stdout
        print("    ok")

        print("[4] a folder from an older build ends with one deck and one old version")
        topic = out / "Pipeline test.pptx"
        shutil.copy2(topic, out / "final_deck.pptx")          # the old second copy
        (out / "final_deck.REJECTED.pptx").write_bytes(b"x" * 1000)
        old = out / "_session" / "old-decks"
        old.mkdir(parents=True, exist_ok=True)
        for i in range(3):
            (old / f"final_deck.2026100{i}T000000.pptx").write_bytes(b"x" * 1000)
        r = H.finalize(out)
        assert r.returncode == 0, "finalize after the compile cleanup: " + r.stdout[-1500:]
        r = _final_and_compile(out)
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-1500:]
        decks = sorted(p.name for p in out.glob("*.pptx"))
        assert decks == ["Pipeline test.pptx"], decks
        olds = [p.name for p in old.iterdir()]
        assert len(olds) == 1 and olds[0].startswith("Pipeline test."), olds
        print("    ok: top", decks, "| old-decks", olds)
    finally:
        H.cleanup(tmp)
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
