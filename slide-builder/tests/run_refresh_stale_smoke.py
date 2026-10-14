#!/usr/bin/env python3
"""Smoke test: a design edited after it was converted reaches the deck, and
what the translator agent drew survives when nothing it draws changed
(items 7 and 8 step 5 of the 2026-10-13 report).

Before: record_picks only converted a pick with no script yet, --edits-done
said "Nothing to do" when no comment was waiting, finalize built whatever
plan was on disk, and converting again rewrote the script from scratch, so
the agent's drawing was lost for good (it was not even in _prev).

  a  the design file changed but converts the same: drawing kept
  b  only the title changed: the script header carries the new title,
     drawing kept
  c  the body changed on a slide the agent never drew on: converted again
  d  the body changed beside the agent's element: drawing kept; the agent's
     element itself changed: the slide waits on the agent with the old
     drawing pasted in as comments, and the old script is in
     _prev_translation/
  -  a hand run of translate_html.py --slide over the agent's drawing is
     refused unless --force
  -  --edits-done with no comment waiting converts a design edited in chat;
     --edited-by-parent is accepted on a sketch page and recorded
  -  finalize converts a changed pick by itself (a-c) and stops with the
     FALLBACK MODE step for d
  -  compile refuses a design changed after finalize, naming the slide and
     the command

Needs tests/fixtures/layout_diverse_template.pptx (gitignored): build it with
py -3 slide-builder/tests/run_layout_inheritance_smoke.py --rebuild.
Run:  py -3 slide-builder/tests/run_refresh_stale_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))
import _e2e_harness as H  # noqa: E402
import _state  # noqa: E402

SKETCH = (
    '<html><body style="margin:0"><div class="slide-canvas" style="position:relative;'
    'width:1280px;height:720px;font-family:Arial">'
    '<h1 data-template-field="title" style="position:absolute;left:60px;top:30px;margin:0;'
    'font-size:28px">{title}</h1>'
    '<div data-shape-id="box" style="position:absolute;left:100px;top:220px;width:300px;'
    'height:120px;background:#1f4e79"></div>'
    '<p data-shape-id="note" style="position:absolute;left:100px;top:380px;margin:0;'
    'font-size:16px">{note}</p>'
    '<div data-shape-id="tag" style="position:absolute;left:700px;top:300px;'
    'transform:rotate(-20deg);font-size:16px">{tag}</div>'
    '{extra}</div></body></html>')
PLAIN = (
    '<html><body style="margin:0"><div class="slide-canvas" style="position:relative;'
    'width:1280px;height:720px;font-family:Arial">'
    '<p data-shape-id="note" style="position:absolute;left:100px;top:380px;margin:0;'
    'font-size:16px">{note}</p></div></body></html>')


def _sketch(out: Path, n: int, title="A plain title", note="A short note.", tag="Rotated tag",
            extra="") -> None:
    time.sleep(1.1)        # design stamps have one-second resolution
    (out / f"slide_{n:02d}" / "option_A.html").write_text(
        SKETCH.format(title=title, note=note, tag=tag, extra=extra), encoding="utf-8")


def _plain(out: Path, n: int, note: str) -> None:
    time.sleep(1.1)
    (out / f"slide_{n:02d}" / "option_A.html").write_text(PLAIN.format(note=note),
                                                           encoding="utf-8")


def _report(out: Path, n: int) -> dict:
    return json.loads((out / f"slide_{n:02d}" / "option_A_translation_report.json")
                      .read_text(encoding="utf-8"))


def _native(out: Path, n: int) -> str:
    return (out / f"slide_{n:02d}" / "option_A_native.py").read_text(encoding="utf-8")


def _picks_line(out: Path, picks: dict) -> str:
    body = _state.canonical_picks(picks)
    tok = _state.read_state(out)["review"]["token"]
    return f"PICKS {body} CHECK {_state.approval_check(tok, body)}"


def main() -> int:
    saved = {k: os.environ.get(k) for k in ("SLIDE_LAB_TRANSLATOR", "SLIDE_LAB_AGENTS_DIR")}
    agents = Path(tempfile.mkdtemp(prefix="slidelab_agents_"))
    for f in (HERE.parent / "agents").glob("*.md"):
        shutil.copy2(f, agents / f.name)
    os.environ["SLIDE_LAB_TRANSLATOR"] = "script"
    os.environ["SLIDE_LAB_AGENTS_DIR"] = str(agents)
    tmp, out = H.new_build(2)
    try:
        import translate_html as T
        _sketch(out, 1)
        _plain(out, 2, "First words.")
        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out).returncode == 0
        r = H.run("record_picks.py", "--out", out, "--approved",
                  _picks_line(out, {"slide_01": "A", "slide_02": "A"}))
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-800:]
        assert "# FALLBACK_PENDING:" in _native(out, 1)
        fp0 = {f["id"]: f.get("fp") for f in _report(out, 1)["fallback"]}
        assert fp0 and all(fp0.values()), f"every element left to the agent has a fingerprint: {fp0}"
        drawn = H.agent_finishes(out / "slide_01" / "option_A_native.py")
        block = drawn.split("# --- FALLBACK ELEMENTS")[1].split("# --- END FALLBACK")[0]

        print("[a] the design file changed, converts the same: drawing kept")
        _sketch(out, 1, extra="<!-- a note to self -->")
        assert T.needs_conversion(out / "slide_01" / "option_A.html", out / "slide_01", "A")
        got = T.refresh_stale(out, [(1, "A")])
        assert got == [], got
        rep = _report(out, 1)
        assert rep["retranslation"]["case"] == "a" and rep["retranslation"]["drawing"] == "kept", \
            rep["retranslation"]
        assert block in _native(out, 1) and "# FALLBACK_DONE:" in _native(out, 1)
        assert "restack_fallbacks(slide, PLAN)" in _native(out, 1)
        assert not T.needs_conversion(out / "slide_01" / "option_A.html", out / "slide_01", "A")
        snaps = list((out / "slide_01" / T.PREV_TRANSLATION_DIR).iterdir())
        assert snaps and (snaps[0] / "option_A_native.py").exists(), snaps
        assert not (out / "slide_01" / "_prev").exists(), "a translation snapshot is not a design"
        print("    ok")

        print("[b] only the title changed: the header carries it, drawing kept")
        _sketch(out, 1, title="A sharper title", extra="<!-- a note to self -->")
        T.refresh_stale(out, [(1, "A")])
        rep = _report(out, 1)
        assert rep["retranslation"]["case"] == "b" and rep["retranslation"]["drawing"] == "kept", \
            rep["retranslation"]
        assert "A sharper title" in _native(out, 1).split("import json")[0]
        assert block in _native(out, 1)
        print("    ok")

        print("[c] the body changed, nothing drawn by the agent: converted again")
        _plain(out, 2, "Second words.")
        T.refresh_stale(out, [(2, "A")])
        rep = _report(out, 2)
        assert rep["retranslation"]["case"] == "c", rep["retranslation"]
        assert "Second words" in (out / "slide_02" / "option_A_native.plan.json").read_text(
            encoding="utf-8")
        print("    ok")

        print("[d] the body changed beside the agent's element: drawing kept")
        _sketch(out, 1, title="A sharper title", note="A longer note than before.")
        T.refresh_stale(out, [(1, "A")])
        rep = _report(out, 1)
        assert rep["retranslation"] == {**rep["retranslation"], "case": "d", "drawing": "kept"}, \
            rep["retranslation"]
        assert rep["needs_agent"] is False and block in _native(out, 1)
        print("    ok")

        print("[d] the agent's element changed: waits on the agent, old drawing pasted in")
        _sketch(out, 1, title="A sharper title", note="A longer note than before.",
                tag="Turned label")
        got = T.refresh_stale(out, [(1, "A")])
        assert got == [out / "slide_01" / "option_A_native.py"], got
        rep = _report(out, 1)
        ri = rep["retranslation"]
        assert ri["drawing"] == "pending" and "tag" in ri["why"], ri
        src = _native(out, 1)
        assert src.startswith("# option_A_native.py") and "# FALLBACK_PENDING: 1" in src
        assert "previous drawing" in src.split("import json")[0]
        assert "# --- PREVIOUS DRAWING" in src and "# | _m.name = \"agent-drawn-mark\"" in src, src
        assert "agent-drawn-mark" not in "\n".join(
            ln for ln in src.splitlines() if not ln.strip().startswith("#")), "pasted as comments"
        assert any("agent-drawn-mark" in (d / "option_A_native.py").read_text(encoding="utf-8")
                   for d in (out / "slide_01" / T.PREV_TRANSLATION_DIR).iterdir()), \
            "the drawn script is kept in _prev_translation"
        # converting again before the agent ran keeps the pasted drawing
        _sketch(out, 1, title="A sharper title", note="Another note.", tag="Turned label")
        T.refresh_stale(out, [(1, "A")])
        assert "# | _m.name = \"agent-drawn-mark\"" in _native(out, 1)
        print("    ok")

        print("[-] a hand run of translate_html.py over the agent's drawing")
        H.agent_finishes(out / "slide_01" / "option_A_native.py")
        r = H.run("translate_html.py", "--out", out, "--slide", "1", "--letter", "A")
        assert r.returncode == 5 and "REFUSED" in r.stdout and "--force" in r.stdout, \
            r.stdout[-800:]
        r = H.run("translate_html.py", "--out", out, "--slide", "1", "--letter", "A", "--force")
        assert r.returncode == 0 and "drawing is kept" in r.stdout, r.stdout[-800:]
        print("    ok: refused, then --force kept the drawing")

        print("[-] --edits-done with no comment waiting converts a chat edit")
        _plain(out, 2, "Third words, from chat.")
        r = H.run("record_picks.py", "--out", out, "--edits-done",
                  "--edited-by-parent", "2: the user's words for the note")
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-800:]
        assert "Nothing to do" not in r.stdout
        assert "converting them again" in r.stdout and "slide 2 option A" in r.stdout, \
            r.stdout[-1500:]
        assert "Third words" in (out / "slide_02" / "option_A_native.plan.json").read_text(
            encoding="utf-8")
        pe = _state.read_state(out).get("parent_edits") or []
        assert pe and pe[-1]["slides"] == "slide_02", pe
        assert "look at its new picture" in r.stdout, r.stdout[-1500:]
        r = H.run("record_picks.py", "--out", out, "--edits-done")
        assert r.returncode == 0 and "nothing changed" in r.stdout, r.stdout[-800:]
        print("    ok")

        print("[-] finalize converts a changed pick itself")
        _plain(out, 2, "Fourth words.")
        r = H.finalize(out)
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-800:]
        assert "converting them again" in r.stdout and "slide 2 option A" in r.stdout, \
            r.stdout[-2000:]
        assert "Fourth words" in (out / "slide_02" / "option_A_native.plan.json").read_text(
            encoding="utf-8")
        print("    ok")

        print("[-] compile refuses a design changed after finalize")
        assert H.run("build_review.py", "--out", out, "--final").returncode == 0
        ftok = _state.read_state(out)["final_check"]["token"]
        _plain(out, 2, "Fifth words, after the final check.")
        r = H.run("compile_picks.py", "--out", out, "--final-token", ftok)
        assert r.returncode == 5 and "slide_02/A" in r.stdout and "finalize_deck.py" in r.stdout, \
            r.stdout[-1500:]
        print("    ok")

        print("[-] finalize stops with the FALLBACK MODE step when the agent's element changed")
        _sketch(out, 1, title="A sharper title", note="Another note.", tag="A new label")
        r = H.finalize(out)
        assert r.returncode == 11, r.stdout[-2000:] + r.stderr[-800:]
        assert "FALLBACK MODE" in r.stdout and "slide 1 option A" in r.stdout, r.stdout[-2000:]
        assert "previous drawing pasted in" in r.stdout, r.stdout[-2000:]
        print("    ok")
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        H.cleanup(tmp)
        shutil.rmtree(agents, ignore_errors=True)
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
