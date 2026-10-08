#!/usr/bin/env python3
"""Smoke test: the review page warns when most pages look alike.

A 29-page sketch deck came back almost all cards and tables (2026-10-08). The
only deck-wide check read the pattern from option_X.py headers, which sketch
options do not have, so it never ran; and it compared split names, which
cannot see "cards everywhere". Each sketch now says its visual form on its
canvas (data-visual-form), and the review page counts them. Checks, on
fictional sketches:

  1. six pages, four tagged "cards": the form count and a warning show;
  2. three pages in a row with one form: the run is named;
  3. a sketch with no form tag is reported as unknown, not skipped;
  4. a varied deck shows the count with no warning;
  5. the card notes flag an unknown icon and a brief source line the
     sketch left out of its footer.

Run:  py -3 slide-builder/tests/run_visual_form_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import build_review as R  # noqa: E402

PAGE = ('<html><body><div class="slide-canvas"{form}>'
        '<p data-template-field="footer">Source: fictional</p>{extra}</div></body></html>')


def deck(tmp: Path, forms: list, extra: dict | None = None, metas: dict | None = None) -> list:
    out = tmp / f"o{len(list(tmp.iterdir()))}"
    for n, f in enumerate(forms, 1):
        sd = out / f"slide_{n:02d}"
        sd.mkdir(parents=True)
        attr = f' data-visual-form="{f}"' if f else ""
        (sd / "option_A.html").write_text(
            PAGE.format(form=attr, extra=(extra or {}).get(n, "")), encoding="utf-8")
    return [R.scan_slide(out, n, (metas or {}).get(n)) for n in range(1, len(forms) + 1)]


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="visual_form_"))
    try:
        print("[1] four of six pages are cards")
        slides = deck(tmp, ["cards", "table", "cards", "chart", "cards", "cards"])
        res = R.compute_form_warnings(slides)
        assert res["counts"] == {"cards": 4, "table": 1, "chart": 1}, res
        assert any("4 of 6 pages" in w and "cards" in w for w in res["warnings"]), res
        banner = R.render_form_banner(slides)
        assert "Many pages look alike" in banner and "cards 4" in banner, banner
        print("    ok")

        print("[2] three in a row")
        res = R.compute_form_warnings(deck(tmp, ["chart", "flow", "flow", "flow", "table", "cards"]))
        assert any("slides 2, 3, 4 in a row are all flow" in w for w in res["warnings"]), res
        print("    ok")

        print("[3] an untagged sketch is unknown, not skipped")
        slides = deck(tmp, ["chart", None, "flow", "table"])
        res = R.compute_form_warnings(slides)
        assert res["unknown"] == [2] and len(res["pages"]) == 4, res
        assert "form unknown" in R.render_form_banner(slides)
        print("    ok")

        print("[4] a varied deck: count, no warning")
        slides = deck(tmp, ["chart", "flow", "table", "cards", "timeline", "hero-number"])
        res = R.compute_form_warnings(slides)
        assert not res["warnings"], res
        b = R.render_form_banner(slides)
        assert "Visual forms" in b and "look alike" not in b, b
        print("    ok")

        print("[5] card notes: unknown icon, source line left out")
        slides = deck(tmp, ["cards", "chart"],
                      extra={1: '<i data-icon-name="no-such-icon"></i>'},
                      metas={2: {"source": "Fictional survey 2026"}})
        n1 = slides[0]["options"][0]["sketch_notes"]
        assert any(n["code"] == "ICON_UNKNOWN" and n["severity"] == "Major" for n in n1), n1
        # Slide 2 has a footer element, so a source is there: no note.
        assert not slides[1]["options"][0]["sketch_notes"]
        sd = tmp / "nofoot" / "slide_01"
        sd.mkdir(parents=True)
        (sd / "option_A.html").write_text('<div class="slide-canvas" data-visual-form="text"></div>',
                                          encoding="utf-8")
        s = R.scan_slide(tmp / "nofoot", 1, {"source": "Fictional survey 2026"})
        notes = s["options"][0]["sketch_notes"]
        assert any(n["code"] == "SOURCE_LINE_MISSING" for n in notes), notes
        assert "SOURCE_LINE_MISSING" in R.render_sketch_notes(s)
        print("    ok")
        print("SMOKE PASSED.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
