#!/usr/bin/env python3
"""Smoke test: publish_cleanup.py frees a published deck's build files and the
deck stays editable.

  - refuses a folder that is not a session (exit 2) and one with no published
    deck yet (exit 5)
  - --scan lists finished decks (flagging recent ones) and deletes nothing
  - a dry run deletes nothing
  - deletes unpicked options, the picked option's images and per-option
    PowerPoint files, _session/_qc* renders (keeping notes such as
    qc-flags-*.md), final_pngs/, _prev/, REVIEW.html
  - keeps the deck, the brief and decisions, the records, and the picked
    option's design/script
  - records only the picked letters in _meta.json, and finalize then rebuilds
    the deleted images and PowerPoint files from the kept script (exit 0)

Run:  py -3 slide-builder/tests/run_publish_cleanup_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _e2e_harness as H  # noqa: E402


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
        assert r.returncode == 0, r.stdout[-1200:]
        (out / "picks.json").write_text(json.dumps({"slide_01": "A", "slide_02": "A"}), encoding="utf-8")

        print("[1] refusals")
        r = H.run("publish_cleanup.py", "--out", tmp)
        assert r.returncode == 2, r.stdout
        r = H.run("publish_cleanup.py", "--out", out)
        assert r.returncode == 5 and "no published deck" in r.stdout, r.stdout
        print("    ok: not a session -> 2; nothing published -> 5")

        # publish: a deck at the top, plus the usual leftovers
        shutil.copy2(out / "slide_01" / "option_A.pptx", out / "Client Deck.pptx")
        (out / "_session").mkdir(exist_ok=True)
        (out / "_session" / "narrative-brief-x.md").write_text("brief", encoding="utf-8")
        (out / "_session" / "_qc2").mkdir()
        (out / "_session" / "_qc2" / "slide_01.png").write_bytes(b"x" * 1000)
        (out / "_session" / "_qc").mkdir()
        (out / "_session" / "_qc" / "slide_01.png").write_bytes(b"x" * 1000)
        (out / "_session" / "_qc" / "qc-flags-2026-10-02.md").write_text("reason", encoding="utf-8")
        (out / "final_pngs").mkdir()
        (out / "final_pngs" / "p1.png").write_bytes(b"x" * 1000)
        (out / "slide_01" / "_prev").mkdir(exist_ok=True)
        (out / "slide_01" / "_prev" / "old.py").write_text("old", encoding="utf-8")
        (out / "REVIEW.html").write_text("<html></html>", encoding="utf-8")

        print("[1b] --scan lists the finished deck and deletes nothing")
        before_scan = sorted(str(p) for p in out.rglob("*"))
        r = H.run("publish_cleanup.py", "--scan", tmp)
        assert r.returncode == 0 and tmp.name in r.stdout and "MAY BE IN PROGRESS" in r.stdout, r.stdout
        assert sorted(str(p) for p in out.rglob("*")) == before_scan
        print("    ok")

        print("[2] a dry run deletes nothing")
        before = sorted(str(p) for p in out.rglob("*"))
        r = H.run("publish_cleanup.py", "--out", out, "--dry-run")
        assert r.returncode == 0 and "Would free" in r.stdout, r.stdout
        assert sorted(str(p) for p in out.rglob("*")) == before
        print("    ok")

        print("[3] the cleanup")
        r = H.run("publish_cleanup.py", "--out", out)
        assert r.returncode == 0 and "[ok] freed" in r.stdout, r.stdout[-800:]
        s1 = out / "slide_01"
        assert not list(s1.glob("option_B*")), "the unpicked option is still there"
        assert (s1 / "option_A.py").exists(), "the picked option's script was deleted"
        assert not (s1 / "option_A.pptx").exists() and not list(s1.glob("option_A*.png"))
        assert (out / "_session" / "_qc" / "qc-flags-2026-10-02.md").exists(), "QC notes were deleted"
        assert not (out / "_session" / "_qc" / "slide_01.png").exists()
        for gone in ("_session/_qc2", "final_pngs", "slide_01/_prev", "REVIEW.html"):
            assert not (out / gone).exists(), gone
        for kept in ("Client Deck.pptx", "_session/narrative-brief-x.md", "_meta.json",
                     "picks.json", "slide_01/_prompt.md"):
            assert (out / kept).exists(), kept
        meta = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
        assert next(s for s in meta["slides"] if s["n"] == 1)["options"] == ["A"], meta["slides"][0]
        print("    ok: unpicked + regenerable files gone; deck, brief, records, picked script kept")

        print("[4] the deck is still editable: finalize rebuilds from the kept script")
        r = H.finalize(out)
        assert r.returncode == 0, r.stdout[-1200:]
        assert (s1 / "option_A.pptx").exists(), "finalize did not regenerate the option"
        print("    ok")
    finally:
        H.cleanup(tmp)
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
