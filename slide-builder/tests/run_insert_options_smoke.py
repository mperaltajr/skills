#!/usr/bin/env python3
"""Smoke test: an insert says how many designs it was set up for, a locked
slide folder stops it with a plain message, and finalize uses what was built on a
half-built slide (items 5 and 6 of the 2026-10-13 report; 2026-10-27 decision).

  0. the design count comes from settings: 1 in the published settings.json,
     3 from a settings.local.json, the env var over both; a default full
     build makes one design per slide
  1. build_deck.py --insert N prints the frozen design count (one by
     default) and how to change it; --options 3 prints three
  2. a slide folder held by another program (a process whose working folder
     is inside it): the insert retries, then exits 5 with "Windows would not
     rename", lists that process read-only (its PID), ends nothing, and
     leaves every folder where it was; once it is gone, the insert works
  3. finalize_deck.py exits 11 for a three-design slide with no design at
     all; once option A alone is built it uses what was built (owner's
     decision, 2026-10-27): exit 0, a note, and _meta.json unchanged
  4. REVIEW.html has a "+3 designs" control whose message carries a "Three
     designs for:" line; redesign_round.py start --three N records it, and
     build_deck.py --slide N then builds three (a plain Replace builds one)

The only process this test ends is the one it started itself in step 2.

Run:  py -3 slide-builder/tests/run_insert_options_smoke.py
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
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

import run_layout_inheritance_smoke as fixture  # noqa: E402
from run_insert_slice_smoke import _brief  # noqa: E402


def _run(script: str, *args: str, env=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                          capture_output=True, text=True, env=env)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="insert_options_smoke_"))
    holder = None
    # The repo's own agent files, in a temp folder (prep checks them; the real
    # ~/.claude/agents is never touched).
    agents = tmp / "agents"
    shutil.copytree(HERE.parent / "agents", agents)
    # The published settings only: no option count pinned, no local file.
    env3 = {k: v for k, v in os.environ.items() if k != "SLIDE_LAB_OPTIONS_PER_SLIDE"}
    env3.update({"SLIDE_LAB_AGENTS_DIR": str(agents), "SLIDE_LAB_SETTINGS_LOCAL": "none"})
    try:
        print("[0] the count comes from settings: 1 published, a local file wins, env wins")
        probe = [sys.executable, "-c", "import sys; sys.path.insert(0, r'%s'); import _paths; "
                 "print(_paths.options_per_slide())" % SCRIPTS]
        r = subprocess.run(probe, capture_output=True, text=True, env=env3)
        assert r.stdout.strip() == "1", r.stdout + r.stderr
        local = tmp / "settings.local.json"
        local.write_text('{"options_per_slide": 3}', encoding="utf-8")
        r = subprocess.run(probe, capture_output=True, text=True,
                           env={**env3, "SLIDE_LAB_SETTINGS_LOCAL": str(local)})
        assert r.stdout.strip() == "3", r.stdout + r.stderr
        r = subprocess.run(probe, capture_output=True, text=True,
                           env={**env3, "SLIDE_LAB_SETTINGS_LOCAL": str(local),
                                "SLIDE_LAB_OPTIONS_PER_SLIDE": "2"})
        assert r.stdout.strip() == "2", r.stdout + r.stderr
        print("    ok: 1 from settings.json, 3 from settings.local.json, 2 from the env")

        tpl = tmp / fixture.FIXTURE_PPTX.name
        if fixture.FIXTURE_PPTX.exists():
            shutil.copy2(fixture.FIXTURE_PPTX, tpl)
        else:
            fixture.build_fixture(tpl)
        fixture.register_fixture(tpl)
        out = tmp / "build"
        b3 = tmp / "b3.md"
        b3.write_text(_brief(tpl, ["Alpha", "Beta", "Gamma"]), encoding="utf-8")
        r = _run("build_deck.py", "--brief", str(b3), "--template", str(tpl),
                 "--out", str(out), "--confirm-template", env=env3)
        assert r.returncode == 0, r.stderr[-800:]
        meta = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
        assert all(s["options"] == ["A"] for s in meta["slides"]), meta["slides"]
        assert "Produce the **1 option(s)**" in (out / "slide_01" / "_prompt.md").read_text(
            encoding="utf-8")
        print("    ok: a default full build makes one design per slide")

        print("[1] the insert prints its frozen design count")
        b4 = tmp / "b4.md"
        b4.write_text(_brief(tpl, ["Alpha", "NEW", "Beta", "Gamma"]), encoding="utf-8")
        r = _run("build_deck.py", "--brief", str(b4), "--template", str(tpl), "--out", str(out),
                 "--insert", "2", "--confirm-template", env=env3)
        assert r.returncode == 0, r.stderr[-800:]
        assert "set up for 1 design(s): option A " in r.stdout, r.stdout
        assert "Never tell a worker a different number" in r.stdout, r.stdout
        assert "--slide 2 --options 3" in r.stdout, r.stdout
        meta = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
        s2 = next(s for s in meta["slides"] if s["n"] == 2)
        assert s2["options"] == ["A"], s2
        b5 = tmp / "b5.md"
        b5.write_text(_brief(tpl, ["Alpha", "NEW", "Beta", "Gamma", "THREE"]), encoding="utf-8")
        r = _run("build_deck.py", "--brief", str(b5), "--template", str(tpl), "--out", str(out),
                 "--insert", "5", "--options", "3", "--confirm-template", env=env3)
        assert r.returncode == 0, r.stderr[-800:]
        assert "set up for 3 design(s): option A, B, C" in r.stdout, r.stdout
        assert "--slide 5 --options 1" in r.stdout, r.stdout
        print("    ok: one by default, three with --options 3, and how to change it")

        print("[2] a locked slide folder stops the insert with a plain message")
        if sys.platform == "win32":
            locked = out / "slide_04"
            # A process sitting in the folder (its working folder), naming the
            # build folder on its command line, as the agent shell did.
            holder = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)",
                                       str(out)], cwd=str(locked))
            before = sorted(p.name for p in out.glob("slide_*"))
            b6 = tmp / "b6.md"
            b6.write_text(_brief(tpl, ["Alpha", "X", "NEW", "Beta", "Gamma", "THREE"]),
                          encoding="utf-8")
            r = _run("build_deck.py", "--brief", str(b6), "--template", str(tpl),
                     "--out", str(out), "--insert", "2", "--confirm-template", env=env3)
            assert r.returncode == 5, (r.returncode, r.stderr[-1500:])
            err = r.stderr
            assert "Windows would not rename the folder" in err, err
            assert str(locked) in err, err
            assert f"PID {holder.pid}" in err, err
            assert "nothing was ended" in err and "--end" in err, err
            assert "Nothing was changed" in err, err
            assert holder.poll() is None, "the insert ended a process it did not start"
            after = sorted(p.name for p in out.glob("slide_*"))
            assert after == before, (before, after)
            m2 = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
            assert m2["slide_count"] == 5, m2["slide_count"]
            holder.kill()                       # the one process this test started
            holder.wait(timeout=30)
            holder = None
            r = _run("build_deck.py", "--brief", str(b6), "--template", str(tpl),
                     "--out", str(out), "--insert", "2", "--confirm-template", env=env3)
            assert r.returncode == 0, r.stderr[-800:]
            print("    ok: exit 5, the holder listed and left running, nothing moved; "
                  "works once it is gone")
        else:
            print("    skipped (Windows only: folders lock only there)")

        print("[3] finalize: option A without B and C uses what was built")
        n3 = 6 if sys.platform == "win32" else 5      # the three-design slide, after [2]
        sd = out / f"slide_{n3:02d}"
        meta_before = (out / "_meta.json").read_bytes()
        r = _run("finalize_deck.py", "--out", str(out), "--template", str(tpl),
                 "--slide", str(n3), env=env3)
        assert r.returncode == 11, ("no design at all is still missing",
                                    r.returncode, r.stdout[-800:], r.stderr[-800:])
        (sd / "option_A.html").write_text(
            "<html><body><div data-template-field='title'>X</div></body></html>",
            encoding="utf-8")
        r = _run("finalize_deck.py", "--out", str(out), "--template", str(tpl),
                 "--slide", str(n3), env=env3)
        assert r.returncode == 0, (r.returncode, r.stdout[-800:], r.stderr[-800:])
        assert f"slide {n3}: set up for 3 design(s) (ABC), 1 built (A); using what was built" \
            in r.stdout, r.stdout
        assert "--options 1" not in r.stdout + r.stderr, "no re-prep advice for a built slide"
        assert (out / "_meta.json").read_bytes() == meta_before, "_meta.json must not change"
        print("    ok: no design is exit 11; one of three built is a one-design slide "
              "(exit 0, _meta.json untouched)")

        print("[4] +3 designs in review: three new designs next round; plain Replace: one")
        page = (out / "REVIEW.html")
        r = _run("build_review.py", "--out", str(out), env={**env3, "SLIDE_LAB_NO_OPEN": "1"})
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-800:]
        h = page.read_text(encoding="utf-8")
        assert "+3 DESIGNS" in h and "pickThree(" in h, "no +3 designs control on the cards"
        assert "takes longer and uses more tokens" in h
        assert "Three designs for: " in h and "--three " in h, "the page message has no three line"
        r = _run("redesign_round.py", "start", "--out", str(out), "--slides", "1,3",
                 "--three", "1", env=env3)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "slide 1: 3 new designs" in r.stdout and "slide 3: 1 new design" in r.stdout, r.stdout
        for n, want in ((1, ["A", "B", "C"]), (3, ["A"])):
            r = _run("build_deck.py", "--template", str(tpl), "--out", str(out),
                     "--slide", str(n), "--confirm-template", env=env3)
            assert r.returncode == 0, r.stderr[-800:]
            m = json.loads((out / "_meta.json").read_text(encoding="utf-8"))
            got = next(s for s in m["slides"] if s["n"] == n)["options"]
            assert got == want, (n, got)
        p1 = (out / "slide_01" / "_prompt.md").read_text(encoding="utf-8")
        assert "Produce the **3 option(s)**" in p1, "the worker prompt must ask for three"
        r = _run("redesign_round.py", "start", "--out", str(out), "--slides", "2",
                 "--three", "4", env=env3)
        assert r.returncode == 5, r.stdout
        print("    ok: +3 -> A, B, C in _meta.json and the prompt; plain Replace -> A only")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        if holder is not None:
            holder.kill()
            holder.wait(timeout=30)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
