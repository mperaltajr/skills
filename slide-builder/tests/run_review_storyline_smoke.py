#!/usr/bin/env python3
"""Smoke test: REVIEW.html shows the approved storyline as written (item 16
of the 2026-10-13 report).

The panel used to be rebuilt from the brief: the designers' bullets
("Supporting points:", ALL CAPS labels), a "Slide N —" prefix and every
headline twice. Now:

  1. an .html storyline: shown inline, its text equal to the file's visible
     text, its own styles, scripts and on* handlers gone, no em-dash added
  2. an .md storyline: turned into simple HTML, same text
  3. warnings, one line each: the file is missing; it changed after prep; the
     brief is newer than it; a Word file is linked, not shown
  4. headline drift by text: an exact match is silent, a close one shows both
     wordings, a storyline headline on no slide is listed, a slide with no
     storyline headline (cover) is never flagged
  5. the check after writing the page stops on "Supporting points:", an ALL
     CAPS designer label or an em-dash
  6. the pointer: emit_dot_dash.py writes approved_storyline into the brief
     and the seal stays valid; a pointer to a storyline written by hand is
     kept; designer wording in the brief's bullets is refused (emit_dot_dash
     and seal_brief, decision D); prep records path, size, time and hash
  7. end to end: build_review.py on a prepped build shows the file, and exits
     6 (page not opened) when the file carries designer wording

Run:  py -3 slide-builder/tests/run_review_storyline_smoke.py
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(REPO / "storyline-helper" / "scripts"))

import _e2e_harness as H  # noqa: E402
import review_storyline as R  # noqa: E402
import emit_dot_dash as E  # noqa: E402
import seal_brief  # noqa: E402

HTML_STORY = """<!doctype html><html><head><title>Tab title</title>
<style>body { max-width: 820px; } h1 { color: red; } ul li { color: blue; }</style>
<script>alert('x')</script></head>
<body onload="steal()">
<h1>The investor storyline</h1>
<p class="dot">1. Demand for compute is outrunning supply</p>
<p class="note" onclick="steal()">Buyers wait six to twelve months for new hardware.</p>
<p class="dot">2. Kinfield buys what others cannot use</p>
<ul><li>Used GPUs at scale</li><li>A tested standard</li></ul>
<p class="dot">3. Revenue reaches 26% of Year 5 revenue</p>
<p class="dot">4. A brand new idea nobody built</p>
<script>more()</script><iframe src="x.html">frame text</iframe>
</body></html>"""

HTML_TEXT = ["The investor storyline",
             "1. Demand for compute is outrunning supply",
             "Buyers wait six to twelve months for new hardware.",
             "2. Kinfield buys what others cannot use",
             "Used GPUs at scale", "A tested standard",
             "3. Revenue reaches 26% of Year 5 revenue",
             "4. A brand new idea nobody built"]

MD_STORY = """# The storyline

**1. Demand for compute is outrunning supply**

- Buyers wait six to twelve months.
- Prices hold.

**2. Kinfield buys what others cannot use**

A short paragraph of *plain* prose.
"""

CARDS = [{"n": 1, "title": "Cover"},
         {"n": 2, "title": "Demand for compute is outrunning supply"},
         {"n": 3, "title": "Kinfield buys what other buyers cannot use"},
         {"n": 4, "title": "Revenue reaches 26% of revenue by Year 5"}]


def words(t: str) -> str:
    return " ".join(t.split())


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="review_storyline_"))
    try:
        print("[1] an .html storyline is shown inline as written, safely")
        sp = tmp / "storyline.html"
        sp.write_text(HTML_STORY, encoding="utf-8")
        rec = {"path": str(sp), "sha256": hashlib.sha256(sp.read_bytes()).hexdigest(),
               "mtime": sp.stat().st_mtime}
        p = R.build_panel({"storyline": rec}, {"governing": "G"}, CARDS)
        h = p["html"]
        for bad in ("<script", "<style", "onclick", "onload", "steal(", "alert(", "<iframe",
                    "frame text", "max-width: 820px", "Tab title", "<a "):
            assert bad not in h, f"{bad!r} reached the panel"
        assert words(p["expected"]) == words(" ".join(HTML_TEXT)), p["expected"]
        assert R.EM_DASH not in h and "Slide 1 " not in p["expected"]
        assert "Approved storyline: storyline.html, last changed" in h, h[:400]
        assert R.check_panel(f"<html>{h}</html>", p["expected"]) == [], \
            R.check_panel(f"<html>{h}</html>", p["expected"])
        assert not any("changed after" in w for w in p["warnings"]), p["warnings"]
        print("    ok: same text, no styles, scripts, handlers or frames, labelled with the file")

        print("[2] an .md storyline is turned into simple HTML with the same text")
        mp = tmp / "clean_FINAL.md"
        mp.write_text(MD_STORY, encoding="utf-8")
        p2 = R.build_panel({"storyline": {"path": str(mp)}}, {}, CARDS)
        assert "<li>Buyers wait six to twelve months.</li>" in p2["html"], p2["html"]
        assert "<strong>1. Demand for compute is outrunning supply</strong>" in p2["html"]
        assert "<em>plain</em>" in p2["html"]
        assert words(p2["expected"]) == words(
            "The storyline 1. Demand for compute is outrunning supply Buyers wait six to "
            "twelve months. Prices hold. 2. Kinfield buys what others cannot use A short "
            "paragraph of plain prose."), p2["expected"]
        print("    ok")

        print("[3] missing, changed since prep, brief newer, Word file")
        p3 = R.build_panel({"storyline": {"path": str(tmp / "gone.html")}},
                           {"governing": "G", "slides": []}, CARDS)
        assert any("missing" in w for w in p3["warnings"]), p3["warnings"]
        assert "The slide headlines, in order" in p3["html"]
        rec_old = dict(rec, sha256="0" * 64)
        brief = tmp / "brief.md"
        brief.write_text("---\na: b\n---\n", encoding="utf-8")
        os.utime(sp, (time.time() - 3600, time.time() - 3600))
        p4 = R.build_panel({"storyline": rec_old, "brief": str(brief)}, {}, CARDS)
        assert sum("changed after the slides were prepped" in w for w in p4["warnings"]) == 1
        assert sum("The brief was changed after the storyline" in w for w in p4["warnings"]) == 1
        dx = tmp / "Storyline.docx"
        dx.write_bytes(b"PK fake")
        p5 = R.build_panel({"storyline": {"path": str(dx)}}, {}, CARDS)
        assert any("Word file" in w and "<a href=" in w for w in p5["warnings"]), p5["warnings"]
        assert "open Storyline.docx" in p5["html"]
        print("    ok: one line each")

        print("[4] headline drift is matched by text, not slide number")
        drift = [w for w in p["warnings"] if "headline" in w]
        assert not any("Demand for compute" in w for w in drift), drift      # exact: silent
        assert any(w.startswith("Slide 3 headline differs") and "others cannot use" in w
                   and "other buyers cannot use" in w for w in drift), drift
        assert any(w.startswith("Slide 4 headline differs") for w in drift), drift
        assert any(w.startswith("Storyline headline not on any slide") and "brand new idea" in w
                   for w in drift), drift
        assert not any("Cover" in w for w in drift), drift                   # never flagged
        print(f"    ok: {len(drift)} line(s): 2 close (both wordings), 1 not on any slide")

        print("[5] the check stops designer wording and em-dashes")
        for bad, what in (("<p>Supporting points: a, b</p>", "Supporting points"),
                          ("<p>SECTION LIST — show all six sections</p>", "ALL CAPS"),
                          ("<p>A claim — with a dash</p>", "em-dash")):
            b = tmp / "bad.html"
            b.write_text(f"<html><body>{bad}</body></html>", encoding="utf-8")
            pb = R.build_panel({"storyline": {"path": str(b)}}, {}, CARDS)
            probs = R.check_panel(pb["html"], pb["expected"])
            assert any(what in x for x in probs), (what, probs)
        assert R.check_panel("<p>x</p>", "x") == ["the storyline panel is missing from REVIEW.html"]
        print("    ok")

        print("[6] the pointer: written by emit_dot_dash, kept by the seal; decision D")
        bt = tmp / "_session"
        bt.mkdir()
        bp = bt / "narrative-brief-demo.md"
        bp.write_text(H.BRIEF.format(slides="".join(H.SLIDE.format(n=i) for i in (1, 2))),
                      encoding="utf-8")
        r = H.run("seal_brief.py", "--brief", bp, "--accepted", "test brief")
        assert r.returncode == 0, r.stdout + r.stderr
        sealed_sha = E.front_matter_value(bp.read_text(encoding="utf-8"), "storyline_gate_sha")
        r = H.run_path(REPO / "storyline-helper" / "scripts" / "emit_dot_dash.py", bp)
        assert r.returncode == 0, r.stdout + r.stderr
        txt = bp.read_text(encoding="utf-8")
        ptr = E.front_matter_value(txt, "approved_storyline")
        assert ptr and Path(ptr).name == "dot-dash-demo.html" and Path(ptr).exists(), ptr
        assert seal_brief._fingerprint_as_prep_reads(txt) == sealed_sha, \
            "adding the pointer broke the seal"
        # A re-seal keeps the pointer.
        r = H.run("seal_brief.py", "--brief", bp, "--accepted", "test brief")
        assert r.returncode == 0 and E.front_matter_value(
            bp.read_text(encoding="utf-8"), "approved_storyline") == ptr, r.stdout
        # A hand-written prose storyline in the pointer is kept by emit_dot_dash.
        hand = tmp / "Prose_Storyline.html"
        hand.write_text("<html><body><p class='dot'>1. Claim number 1 is stated plainly "
                        "here</p></body></html>", encoding="utf-8")
        bp.write_text(E.set_front_matter_value(bp.read_text(encoding="utf-8"),
                                               "approved_storyline", str(hand)), encoding="utf-8")
        r = H.run_path(REPO / "storyline-helper" / "scripts" / "emit_dot_dash.py", bp)
        assert r.returncode == 0 and "Kept approved_storyline" in r.stdout, r.stdout
        assert E.front_matter_value(bp.read_text(encoding="utf-8"), "approved_storyline") == str(hand)
        # Decision D: designer wording in a bullet is refused, nothing written.
        bad = tmp / "_session2"
        bad.mkdir()
        bb = bad / "narrative-brief-bad.md"
        bb.write_text(bp.read_text(encoding="utf-8").replace(
            "- Point two for slide 1", "- Supporting points: growth, margin").replace(
            "- Point three for slide 2", "- SECTION LIST — show all six sections"),
            encoding="utf-8")
        r = H.run_path(REPO / "storyline-helper" / "scripts" / "emit_dot_dash.py", bb)
        assert r.returncode == 2 and "NOT WRITTEN" in r.stdout, r.stdout + r.stderr
        assert "slide 1" in r.stdout and "slide 2" in r.stdout and "Editorial emphasis" in r.stdout
        assert not (tmp / "dot-dash-bad.html").exists()
        r = H.run("seal_brief.py", "--brief", bb)
        assert r.returncode == 3 and "designer" in r.stdout, r.stdout
        ok_bold = E.designer_wording("### Slide 1 — X\n- **WHY IT GROWS** — demand\n"
                                     "- EBITDA: $1.2B in Year 5\n- GPU — fine\n")
        assert ok_bold == [], ok_bold
        print("    ok: pointer written, seal valid and kept, hand-written pointer kept, "
              "designer wording refused")

        print("[7] end to end: prep records it, REVIEW shows it, exit 6 on designer wording")
        if not H.TEMPLATE.exists():
            import run_layout_inheritance_smoke as fixture
            fixture.build_fixture(H.TEMPLATE)
            fixture.register_fixture(H.TEMPLATE)
        btmp, out = H.new_build(2)
        try:
            meta_brief = Path(json.loads((out / "_meta.json").read_text(encoding="utf-8"))["brief"])
            story = btmp / "Approved_Storyline.html"
            story.write_text("<html><body><h1>Storyline</h1><p class='dot'>1. Claim number 1 "
                             "is stated plainly here</p><p class='dot'>2. Claim number 2 is "
                             "stated plainly here</p></body></html>", encoding="utf-8")
            meta_brief.write_text(E.set_front_matter_value(meta_brief.read_text(encoding="utf-8"),
                                  "approved_storyline", str(story)), encoding="utf-8")
            r = H.run("build_deck.py", "--brief", meta_brief, "--template", H.TEMPLATE,
                      "--out", out, "--pattern", "direct", "--confirm-template")
            assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
            assert "Approved storyline recorded" in r.stdout, r.stdout[-800:]
            m = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
            st = m.get("storyline") or {}
            assert Path(st.get("path", "")) == story.resolve() and st.get("size") and \
                st.get("mtime") and len(st.get("sha256", "")) == 64, st
            for n in (1, 2):
                H.write_option(out, n)
            r = H.run("build_review.py", "--out", out)
            assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
            page = (out / "REVIEW.html").read_text(encoding="utf-8")
            i, j = page.find(R.START), page.find(R.END)
            panel_text = R.text_of(page[i:j])
            assert words(panel_text) == words("Storyline 1. Claim number 1 is stated plainly "
                                              "here 2. Claim number 2 is stated plainly here"), panel_text
            assert "Approved storyline: Approved_Storyline.html" in page
            assert "Point one for slide" not in page[i:j]
            assert not [w for w in r.stdout.splitlines() if "headline" in w and "WARNING" in w], r.stdout
            story.write_text("<html><body><p>Supporting points: one, two</p></body></html>",
                             encoding="utf-8")
            r = H.run("build_review.py", "--out", out, "--open")
            assert r.returncode == 6 and "NOT opened" in r.stdout, r.stdout[-1500:]
            assert "changed after the slides were prepped" in r.stdout, r.stdout[-1500:]
            # No pointer: headlines only, the governing thought once, no prefix.
            st_path = out / "_meta.json"
            m = json.loads(st_path.read_text(encoding="utf-8"))
            m.pop("storyline", None)
            st_path.write_text(json.dumps(m, indent=2), encoding="utf-8")
            r = H.run("build_review.py", "--out", out)
            assert r.returncode == 0, r.stdout[-1500:]
            page = (out / "REVIEW.html").read_text(encoding="utf-8")
            pt = R.text_of(page[page.find(R.START):page.find(R.END)]).splitlines()
            assert pt[0].startswith("The test deck proves"), pt
            assert pt[1:] == ["Claim number 1 is stated plainly here",
                              "Claim number 2 is stated plainly here"], pt
            print("    ok")
        finally:
            H.cleanup(btmp)

        print("\nSMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
