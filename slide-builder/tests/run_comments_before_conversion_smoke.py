#!/usr/bin/env python3
"""Smoke test: comments on a pick are applied before conversion (2026-10-09).

  1. the page's Feedback block is parsed; a comment asking for another design
     (the "Wrong layout / structure" chip, "try a chart instead") is a
     redesign request, a plain note is an edit; a chat comment must be the
     user's own words
  2. picks with feedback on one slide: the other picks convert, the commented
     one does not (recorded "edit first", with an edit request for the worker);
     the final check refuses while the comment is pending
  3. --edits-done refuses while the design is unchanged; after the edit in
     place it marks the comment applied, keeps the pick (same letter, marked
     edited) and converts it; the final check then builds
  4. picks without feedback record no comments
  5. a redesign comment starts a Replace round (the pick is not kept, the
     comment goes to _prior_feedback.md, the user is asked one or three);
     a comment on a left-out slide is recorded as not needed; finish marks
     the redesign comment applied
  6. the delivery list (check_done) shows every comment and how it was applied

Run:  py -3 slide-builder/tests/run_comments_before_conversion_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

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

SKETCH = ('<html><body style="margin:0"><div class="slide-canvas" style="position:relative;'
          'width:1280px;height:720px;font-family:Arial">'
          '<div data-shape-id="box" style="position:absolute;left:100px;top:220px;width:300px;'
          'height:120px;background:#1f4e79"></div>'
          '<p data-shape-id="note" style="position:absolute;left:100px;top:380px;margin:0;'
          'font-size:16px">{text}</p></div></body></html>')


def _sketch(out: Path, n: int, text: str) -> Path:
    p = out / f"slide_{n:02d}" / "option_A.html"
    p.write_text(SKETCH.format(text=text), encoding="utf-8")
    return p


def _message(out: Path, picks: dict, feedback: str = "") -> str:
    """The page's Build my deck message: plain Picks line + Feedback block."""
    body = _state.canonical_picks(picks)
    tok = _state.read_state(out)["review"]["token"]
    plain = " ".join(f"{int(k.split('_')[1])}{v}" for k, v in sorted(picks.items()))
    msg = (f"Build my Slide Lab deck.\nFolder: {out}\n"
           f"Picks: {plain} (check {_state.approval_check(tok, body)})\n")
    return msg + feedback


def unit() -> None:
    print("[1] the Feedback block is parsed and each comment classified")
    block = ("Feedback:\n  slide_02:\n    quick: Too dense, simplify; Fix a number / wording\n"
             "    headline: shorter title\n  slide_03:\n    quick: Wrong layout / structure\n"
             "  slide_04:\n    other: try a chart instead\n")
    fb = RP.parse_feedback("Picks: 1A (check 00000000)\n" + block)
    assert set(fb) == {"slide_02", "slide_03", "slide_04"}, fb
    assert fb["slide_02"]["headline"] == "shorter title", fb
    assert not RP.asks_for_redesign(fb["slide_02"])
    assert RP.asks_for_redesign(fb["slide_03"]), "the layout chip is a redesign request"
    assert RP.asks_for_redesign(fb["slide_04"]), "'try a chart instead' is a redesign request"
    flat = RP.parse_feedback(block.replace("  ", ""))   # indentation lost in a paste
    assert flat == fb, flat
    got, why = RP.chat_comments("use 1A 2A, and on 2 make the title shorter",
                                ["2: make the title shorter"])
    assert not why and got["slide_02"]["note"] == "make the title shorter", (got, why)
    _, why = RP.chat_comments("use 1A 2A", ["2: make the title shorter"])
    assert why, "a comment the user did not type was accepted"
    print("    ok")


def sketch_flow() -> None:
    saved = os.environ.get("SLIDE_LAB_TRANSLATOR")
    os.environ["SLIDE_LAB_TRANSLATOR"] = "script"
    tmp, out = H.new_build(3)
    try:
        for n in (1, 2, 3):
            _sketch(out, n, f"A short note for slide {n}.")
        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out).returncode == 0

        print("[2] the commented pick waits; only the others convert")
        msg = _message(out, {"slide_01": "A", "slide_02": "A", "slide_03": "A"},
                       "Feedback:\n  slide_02:\n    headline: Make the title shorter\n")
        r = H.run("record_picks.py", "--out", out, "--approved", msg)
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-800:]
        native = {n: out / f"slide_{n:02d}" / "option_A_native.py" for n in (1, 2, 3)}
        assert native[1].exists() and native[3].exists(), r.stdout[-1500:]
        assert not native[2].exists(), "the commented slide was converted before its edit"
        st = _state.read_state(out)
        pend = _state.pending_comments(st, "edit")
        assert [c["slide"] for c in pend] == ["slide_02"], st.get("comments")
        assert "Make the title shorter" in pend[0]["text"]
        req = out / "slide_02" / "_edit_request.md"
        assert req.exists() and "EDIT IN PLACE" in req.read_text(encoding="utf-8")
        assert "--edits-done" in r.stdout and "EDIT FIRST" in r.stdout, r.stdout[-1500:]
        # (finalize itself refuses too: a picked sketch is not converted yet)
        r = H.run("build_review.py", "--out", out, "--final")
        assert r.returncode != 0 and "waits on the user's comment" in r.stderr, r.stderr[-800:]
        print("    ok: slides 1 and 3 converted, slide 2 held; final check refused")

        print("[3] --edits-done: refused before the edit, then applies and converts")
        r = H.run("record_picks.py", "--out", out, "--edits-done")
        assert r.returncode == 5 and "has not changed" in r.stdout, r.stdout[-800:]
        time.sleep(1.1)   # the stamp has one-second resolution
        _sketch(out, 2, "A shorter note.")
        r = H.run("record_picks.py", "--out", out, "--edits-done")
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-800:]
        assert native[2].exists(), "the edited pick was not converted"
        assert "kept as is" not in r.stdout or "slide 2" not in r.stdout
        st = _state.read_state(out)
        assert not _state.pending_comments(st), st.get("comments")
        c = st["comments"][0]
        assert c["status"] == "applied" and "edited in place" in c["applied_how"], c
        mem = st["pick_memory"]["slide_02"]
        assert mem["letter"] == "A" and mem["edited"], mem
        assert st["review"]["picks"]["slide_02"] == "A"
        assert H.finalize(out).returncode == 0
        r = H.run("build_review.py", "--out", out, "--final")
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-800:]
        print("    ok: comment applied, pick kept (edited), every pick converted, final check built")

        print("[6] the delivery list shows the applied comment")
        lines = "\n".join(check_done.comment_lines(st["comments"]))
        assert "Make the title shorter" in lines and "edited in place" in lines, lines
        print("    ok")
    finally:
        if saved is None:
            os.environ.pop("SLIDE_LAB_TRANSLATOR", None)
        else:
            os.environ["SLIDE_LAB_TRANSLATOR"] = saved
        H.cleanup(tmp)


def direct_flow() -> None:
    tmp, out = H.new_build(3)
    try:
        for n in (1, 2, 3):
            H.write_option(out, n, "A")
        assert H.finalize(out).returncode == 0
        assert H.run("build_review.py", "--out", out).returncode == 0

        print("[4] picks without feedback record no comments")
        r = H.run("record_picks.py", "--out", out, "--approved",
                  _message(out, {"slide_01": "A", "slide_02": "A", "slide_03": "A"}))
        assert r.returncode == 0, r.stdout[-1200:]
        assert not _state.read_state(out).get("comments"), "comments recorded from nothing"
        assert "finalize_deck.py" in r.stdout
        print("    ok")

        print("[5] a redesign comment is a Replace round; a left-out comment is not needed")
        msg = _message(out, {"slide_01": "A", "slide_02": "A", "slide_03": "-"},
                       "Feedback:\n  slide_02:\n    quick: Wrong layout / structure\n"
                       "    other: try a chart instead\n"
                       "  slide_03:\n    other: drop this one\n")
        r = H.run("record_picks.py", "--out", out, "--approved", msg)
        assert r.returncode == 0, r.stdout[-1500:]
        assert "One new design or three" in r.stdout and "THREE preselected" in r.stdout, \
            r.stdout[-1500:]
        st = _state.read_state(out)
        assert st["redesign_round"]["slides"] == [2], st.get("redesign_round")
        assert st["redesign_round"]["kept"] == {"slide_01": "A", "slide_03": "-"}
        assert "slide_02" not in st["pick_memory"], "the redesigned slide's pick was kept"
        kinds = {c["slide"]: (c["kind"], c["status"]) for c in st["comments"]}
        assert kinds == {"slide_02": ("redesign", "pending"),
                         "slide_03": ("left_out", "not_needed")}, kinds
        prior = (out / "slide_02" / "_prior_feedback.md").read_text(encoding="utf-8")
        assert "try a chart instead" in prior, prior
        r = H.run("build_deck.py", "--slide", "2", "--out", out, "--template", H.TEMPLATE,
                  "--pattern", "direct")
        assert r.returncode == 0, r.stdout[-1200:] + r.stderr[-600:]
        H.write_option(out, 2, "A")
        r = H.run("redesign_round.py", "finish", "--out", out)
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-800:]
        st = _state.read_state(out)
        assert st["review"]["picks"] == {"slide_01": "A", "slide_02": "A", "slide_03": "-"}
        c2 = next(c for c in st["comments"] if c["slide"] == "slide_02")
        assert c2["status"] == "applied" and "redesigned" in c2["applied_how"], c2
        lines = "\n".join(check_done.comment_lines(st["comments"]))
        assert "redesigned" in lines and "left out" in lines, lines
        print("    ok: redesign round recorded, comment applied by finish, delivery lists both")
    finally:
        H.cleanup(tmp)


def main() -> int:
    unit()
    direct_flow()
    sketch_flow()
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
