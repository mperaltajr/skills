#!/usr/bin/env python3
"""Smoke test for the review gate: what the user approves is exactly what ships.

The order (owner's decision, 2026-09-30):
  REVIEW.html -> record_picks.py (check-coded picks) -> translate picks ->
  finalize -> build_review.py --final (FINAL-CHECK.html) -> compile --final-token

Verifies, at the level of the recorded state:
  1. prep records content-hash + canonical out; compile refused before review
  2. build_review mints a token bound to the content hash, and REUSES it while
     nothing changed (a fresh token per rebuild voided commands already copied)
  3. record_picks accepts the page's line and refuses an edited, forged,
     partial or stale one
  4. the page keys picks to a per-slide stamp, offers Replace these (not the old
     +more picker) and an All options button that warns about cost
  5. a missing preview is called out on the page
  6. a re-prep clears the review, the picks and the final check
  7. the final check binds compile to the bytes the user saw, and any finalize
     clears it

Run:  py -3 slide-builder/tests/run_review_gate_smoke.py   (python3 on macOS/Linux)
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import _state  # noqa: E402


def _minimal_deck(out: Path) -> None:
    for n in (1, 2):
        d = out / f"slide_0{n}"
        d.mkdir(parents=True)
        (d / "option_A.py").write_text("# option A\n", encoding="utf-8")
        (d / "option_B.py").write_text("# option B\n", encoding="utf-8")
        (d / "option_A.pptx").write_bytes(b"PK demo A")
        (d / "option_B.pptx").write_bytes(b"PK demo B")
        (d / "option_A.png").write_bytes(b"\x89PNG demo")
        (d / "option_B.png").write_bytes(b"\x89PNG demo")
        (d / "_prompt.md").write_text(f"**Slide title:** Demo {n}\n", encoding="utf-8")
    (out / "_meta.json").write_text(json.dumps({
        "schema_version": 3, "template": "t.pptx", "brief": "b.md", "out": str(out),
        "client_slug": "demo", "slide_count": 2, "generated_at": "2026-01-01T00:00:00",
        "slides": [{"n": n, "title": f"Demo {n}", "page_type": "Content", "layout": "L",
                    "options": ["A", "B"]} for n in (1, 2)],
        "deck_meta": {"deck_type": "x", "governing_thought": "g", "audience": "a"},
    }), encoding="utf-8")


def _run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True,
                          env={**os.environ, "PYTHONPATH": str(SCRIPTS)})


def _line(token, picks):
    body = _state.canonical_picks(picks)
    return f"PICKS {body} CHECK {_state.approval_check(token, body)}"


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="review_gate_smoke_"))
    try:
        out = tmp / "build"
        _minimal_deck(out)

        print("[1] prep records content-hash + canonical out; compile refused pre-review")
        _state.record_prep(out, "hashV1", out)
        st = _state.read_state(out)
        assert st["content_hash"] == "hashV1" and st.get("review") is None, st
        assert Path(st["canonical_out"]).resolve() == out.resolve(), st
        assert not _state.check_compile_allowed(out, "anything")[0]
        print("    ok")

        print("[2] build_review mints a token bound to the content, and reuses it")
        r = _run("build_review.py", "--out", out)
        assert r.returncode == 0, r.stderr[-600:]
        tok = _state.read_state(out)["review"]["token"]
        assert _state.read_state(out)["review"]["content_hash"] == "hashV1"
        assert _run("build_review.py", "--out", out).returncode == 0
        assert _state.read_state(out)["review"]["token"] == tok, (
            "rebuilding the page with nothing changed minted a new token, which "
            "voids a command the user already copied")
        html = (out / "REVIEW.html").read_text(encoding="utf-8")
        assert "--review-token" not in html, "the bare-token compile command is back"
        print(f"    ok: token {tok[:6]}... stable across rebuilds of the page")

        print("[3] record_picks: the page's line is accepted; anything else is not")
        both = {"slide_01": "B", "slide_02": "A"}
        assert _run("record_picks.py", "--out", out, "--approved",
                    _line(tok, both).replace("slide_01=B", "slide_01=A")).returncode == 5, \
            "an edited pick must be refused"
        assert _run("record_picks.py", "--out", out, "--approved",
                    _line("deadbeefdeadbeef", both)).returncode == 5, "forged token"
        assert _run("record_picks.py", "--out", out, "--approved",
                    _line(tok, {"slide_01": "B"})).returncode == 5, "partial picks"
        assert _run("record_picks.py", "--out", out, "--approved",
                    _line(tok, {"slide_01": "C", "slide_02": "A"})).returncode == 5, \
            "a pick of an option that does not exist"
        r = _run("record_picks.py", "--out", out, "--approved", _line(tok, both))
        assert r.returncode == 0, r.stdout
        assert _state.read_state(out)["review"]["picks"] == both
        print("    ok: edited / forged / partial / nonexistent refused; real line recorded")

        print("[4] the page: stamped picks, Replace these, All options with a warning")
        assert "{ l: letter, s: STAMPS[sid] }" in html, "picks are not stamped"
        assert "window.__STAMPS__" in html
        assert "REPLACE THESE" in html and "more-opt" not in html.split("<script>")[0], \
            "Replace these missing, or the old +more picker still rendered"
        assert 'id="btn-all"' in html and "the conversion cost" in html, \
            "All options button or its cost warning is missing"
        print("    ok")

        print("[5] a missing preview is surfaced in the page, not just the log")
        (out / "slide_01" / "option_A.png").unlink()
        assert _run("build_review.py", "--out", out).returncode == 0
        html2 = (out / "REVIEW.html").read_text(encoding="utf-8")
        assert "have no rendered preview" in html2
        assert "Do not approve a deck you could not look at" in html2
        print("    ok")

        print("[6] a re-prep clears the review, the picks and the final check")
        _state.record_final_check(out, {"slide_01/B": "x"})
        _state.record_prep(out, "hashV2", out)
        st = _state.read_state(out)
        assert not st.get("review") and not st.get("final_check"), st
        r = _run("record_picks.py", "--out", out, "--approved", _line(tok, both))
        assert r.returncode == 5, "the old page's line must not record after a rebuild"
        print("    ok")

        print("[7] the final check binds compile to the bytes the user saw")
        tok = _state.record_review(out)
        _state.record_picks(out, both)
        themed = {k: out / k.split("/")[0] / f"option_{k.split('/')[1]}.pptx"
                  for k in ("slide_01/B", "slide_02/A")}
        ftok = _state.record_final_check(
            out, {k: _state.file_digest(p) for k, p in themed.items()})
        path_for = themed.__getitem__
        assert _state.check_compile_allowed(out, ftok, path_for)[0]
        assert not _state.check_compile_allowed(out, "wrong", path_for)[0]
        themed["slide_02/A"].write_bytes(b"PK changed after the final check")
        ok, why = _state.check_compile_allowed(out, ftok, path_for)
        assert not ok and "changed after the final" in why, why
        _state.begin_finalize(out)
        assert not _state.read_state(out).get("final_check"), \
            "a finalize must clear the final check: it writes files the user has not seen"
        print("    ok: token + bytes both checked; finalize clears the check")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
