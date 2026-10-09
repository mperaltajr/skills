#!/usr/bin/env python3
"""Smoke test: automatic QC fixes (owner's decision, 2026-10-09).

A fictional 3-slide deck with one Critical, two layout Majors and one content
Major:

  0. qc_fix_policy reads the tag and the severity only from their place,
     splits only before "slide N", never goes automatic without a known tag,
     asks a Critical content finding, and lets a tag only make a decision more
     cautious (every string from the 2026-10-09 validation of item 3)
  1. qc_fix_policy classes the Critical and the two layout Majors "auto" and
     the content Major "ask" (tags and untagged text both)
  2. apply_qc_fix.py --auto refuses the content finding (the user decides it)
     and refuses a slide whose design was not kept first (--snapshot), an
     untagged finding (listing the valid keys), and a finding for a slide
     not in --slides or for no slide
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
MAJ2 = "slide 3 [arrow_into_box] Major: an arrowhead runs into the box it points at"
CONTENT = "slide 3 Major: the 42 percent figure is not in the brief"

# (finding, expected decision, expected category) for every string in the
# 2026-10-09 validation of item 3 (confirmer, challenger, judge).
POLICY_CASES = [
    # the word "critical" in the text is not the severity
    ("slide 4 [headline] Major: headline misses the critical number", "ask", "headline"),
    ("slide 4 [number_not_in_brief] Major: the 12% is critical for the ask", "ask",
     "number_not_in_brief"),
    ("slide 4 Major: bullets not parallel, the critical bullet", "ask", "bullets_parallel"),
    # the word "advisory" in the text does not drop a layout finding
    ("slide 4 [overflow] Major: the advisory note box is cut off", "auto", "overflow"),
    # a wrong layout tag on a content finding is asked
    ("slide 4 [overflow] Major: 42% not in brief", "ask", "overflow"),
    ("slide 4 [overflow] Major: \"42%\" is not in the brief", "ask", "overflow"),
    ("slide 4 [palette] Major: headline is a topic label, rewrite", "ask", "palette"),
    ("slide 4 [text_size] Major: 4 body sizes -> reword the headline to fit", "ask",
     "text_size"),
    ("slide 4 [arrow_into_box] Major: wrong number in the arrow label", "ask",
     "arrow_into_box"),
    # untagged phrase matches never go automatic
    ("slide 4 Major: wrong number in the arrow label", "ask", "number_not_in_brief"),
    ("slide 4 Major: placeholder for the revenue number", "ask", "sample_text"),
    ("slide 4 Major: an arrowhead runs into the box", "ask", "arrow_into_box"),
    ("slide 4 Critical: body text cut off at the bottom", "ask", "overflow"),
    ("slide 4 Advisory: whitespace uneven", "none", ""),
    # a Critical content finding is asked (owner's decision)
    ("slide 4 [headline] Critical: title is a topic label", "ask", "headline"),
    # slide-qc's hyphenated / spaced tags and the aliases
    ("slide 4 [text-size] Major: 4 body text sizes", "auto", "text_size"),
    ("slide 4 [text size] Major: body text under the size floor", "auto", "text_size"),
    ("slide 4 [template-sample-text] Critical: <Customize with your text> left on the slide",
     "auto", "sample_text"),
    ("slide 4 [placeholder-prompt] Major: [add source here or delete] left on the slide",
     "auto", "sample_text"),
    ("slide 4 [buzzword] Major: synergy, leverage", "ask", "buzzwords"),
    ("slide 4 [repeats-title] Major: the takeaway under the title repeats the title", "ask",
     "repeats_title"),
    ("slide 4 [title-load] Advisory: a 2-line title, a takeaway and a band", "ask",
     "title_load"),
    ("slide 4 [Overflow] MAJOR: text cut off", "auto", "overflow"),
    # the real retry from the Kinfield v3.1 session
    ("slide 38 [text_size] Major: 4 body text sizes (10.5, 12, 14, 16 pt) on option A",
     "auto", "text_size"),
    # unknown tag, no severity in its place: never automatic
    ("slide 4 [spacing] Major: uneven gaps", "ask", ""),
    ("slide 4 [overflow] text cut off", "ask", "overflow"),
    ("slide 4 [overflow] Advisory: tight right margin", "none", "overflow"),
    # the 2026-10-09 chart and period keys stay automatic
    ("slide 4 [final_period] Major: 2 text items end with a final period", "auto",
     "final_period"),
    ("slide 4 [chart_header] Major: the chart has no header line", "auto", "chart_header"),
    ("slide 4 [legend_position] Major: the legend is at the bottom", "auto",
     "legend_position"),
]


def _policy() -> None:
    print("[0] the policy reads tag and severity only from their place")
    for text, want_d, want_c in POLICY_CASES:
        got = P.decide(text)
        assert got == (want_d, want_c), f"{text!r}: got {got}, want {(want_d, want_c)}"
    # splitting: only before "slide N"; fix detail stays with its finding
    rows = P.classify("slide 38 [text_size] Major: 4 body sizes; fix: shorten the labels "
                      "to 12 pt; slide 39 [overflow] Major: text cut off")
    assert [(r["slide"], r["decision"]) for r in rows] == [(38, "auto"), (39, "auto")], rows
    assert "shorten the labels" in rows[0]["finding"], rows
    rows = P.classify("slide 38 [text_size] Major: 4 body sizes\nfix: keep 12 and 14 pt\n"
                      "slide 40 [chrome] Major: takeaway not under the title")
    assert [(r["slide"], r["decision"]) for r in rows] == [(38, "auto"), (40, "auto")], rows
    assert "keep 12 and 14" in rows[0]["finding"]
    rows = P.classify("slide 38 [text_size] Major: 4 body sizes (shorten the labels; "
                      "keep the chart)")
    assert len(rows) == 1 and rows[0]["decision"] == "auto", rows
    rows = P.classify("slide 38 [text_size] Major: 4 body sizes; reword the headline to fit")
    assert len(rows) == 1 and rows[0]["decision"] == "ask", \
        "fix detail that rewrites words did not make the finding a question"
    rows = P.classify("slide 3 [overflow] Major: text cut off; Slide 5 [headline] Major: "
                      "topic label")
    assert [(r["slide"], r["decision"]) for r in rows] == [(3, "auto"), (5, "ask")], rows
    assert P.parse("slide 4 [overflow] Major: x")["severity"] == "major", "severity not read"
    assert P.normalize_tag("Template-Sample Text") == "sample_text"
    for alias, key in P.ALIASES.items():
        assert key in P.CATEGORIES, alias
    print(f"    ok ({len(POLICY_CASES)} findings, 5 splits)")


def _rebuild(out: Path, n: int, size: int) -> None:
    """Stand in for the one-design rebuild of a flagged slide."""
    time.sleep(1.1)
    body = H.OPTION_SCRIPT.format(n=n, L="A", skill=str(H.SKILL)).replace(
        "font_size_pt=18", f"font_size_pt={size}")
    H.write_option(out, n, "A", body=body)


def main() -> int:
    _policy()
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
        r = H.run("apply_qc_fix.py", "--out", out, "--slides", "3", "--auto",
                  "slide 3 Major: an arrowhead runs into the box it points at")
        assert r.returncode == 5 and "never fixed automatically" in r.stdout and \
            "arrow_into_box" in r.stdout and "final_period" in r.stdout, r.stdout[-800:]
        r = H.run("apply_qc_fix.py", "--out", out, "--slides", "1", "--auto", MAJ1)
        assert r.returncode == 5 and "must name one of the slides" in r.stdout, r.stdout[-800:]
        r = H.run("apply_qc_fix.py", "--out", out, "--slides", "1", "--auto",
                  "[overflow] Critical: body text cut off")
        assert r.returncode == 5 and "must name one of the slides" in r.stdout, r.stdout[-800:]
        print("    ok (also: an untagged finding, with the valid keys listed, and a finding "
              "for a slide not in --slides or for no slide)")

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
