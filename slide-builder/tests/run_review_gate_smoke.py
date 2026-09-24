#!/usr/bin/env python3
"""Smoke test for the review-gate backbone (Rules 1 + 2): the build state
manifest (_state.json) and the review-approval token.

Verifies the mechanical chain that makes the human review un-bypassable by drift:
  1. prep records the deck content-hash + canonical out-dir and clears any prior
     approval; compile is refused before a review exists;
  2. build_review.py mints a token, embeds it ONLY inside REVIEW.html, and records
     it in _state.json bound to the current content-hash;
  3. the right token is accepted, a wrong/forged token is refused;
  4. a (re)build (re-prep) invalidates the token, so a stale review cannot compile.

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
    (out / "slide_01").mkdir(parents=True)
    (out / "slide_01" / "option_A.pptx").write_bytes(b"PK demo")
    (out / "slide_01" / "option_A.png").write_bytes(b"\x89PNG demo")
    (out / "slide_01" / "_prompt.md").write_text("**Slide title:** Demo\n", encoding="utf-8")
    (out / "_meta.json").write_text(json.dumps({
        "schema_version": 3, "template": "t.pptx", "brief": "b.md", "out": str(out),
        "client_slug": "demo", "slide_count": 1, "generated_at": "2026-01-01T00:00:00",
        "slides": [{"n": 1, "title": "Demo", "page_type": "Cover", "layout": "L", "options": ["A"]}],
        "deck_meta": {"deck_type": "x", "governing_thought": "g", "audience": "a"},
    }), encoding="utf-8")


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="review_gate_smoke_"))
    try:
        out = tmp / "build"
        _minimal_deck(out)

        print("[1] prep records content-hash + canonical out; compile refused pre-review")
        _state.record_prep(out, "hashV1", out)
        st = _state.read_state(out)
        assert st["content_hash"] == "hashV1", st
        assert st.get("review") is None, "prep must not leave an approval"
        assert Path(st["canonical_out"]).resolve() == out.resolve(), st
        ok, _ = _state.check_compile_allowed(out, "anything")
        assert not ok, "compile must refuse before any review"
        print("    ok")

        print("[2] build_review mints the token into REVIEW.html + _state.json")
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "build_review.py"), "--out", str(out)],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS)})
        assert r.returncode == 0, f"build_review failed:\n{r.stderr[-600:]}"
        st = _state.read_state(out)
        tok = st["review"]["token"]
        html = (out / "REVIEW.html").read_text(encoding="utf-8")
        assert tok in html, "token not surfaced in REVIEW.html"
        assert "__REVIEW_TOKEN__" in html, "token JS var missing from REVIEW.html"
        assert st["review"]["content_hash"] == "hashV1", "token not bound to content-hash"
        print(f"    ok: token {tok[:6]}... embedded + recorded")

        print("[3] right token accepted; forged token refused")
        ok, _ = _state.check_compile_allowed(out, tok)
        assert ok, "the minted token must be accepted"
        ok, _ = _state.check_compile_allowed(out, "deadbeefdeadbeef")
        assert not ok, "a forged token must be refused"
        print("    ok")

        print("[4] a rebuild (re-prep) invalidates the token -> stale review refused")
        _state.record_prep(out, "hashV2", out)   # content changed / rebuilt
        ok, why = _state.check_compile_allowed(out, tok)
        assert not ok, "a stale review token must be refused after a rebuild"
        print(f"    ok: {why[:56]}")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
