#!/usr/bin/env python3
"""Smoke test for removing a slide (build_deck.py --delete N), the reverse of
--insert, and for the one helper both use (_state.shift_slide_records).

  1. a 4-slide build with every slide-numbered record seeded (picks, the
     per-option QC records, pick memory, comments, chat approvals, a redesign
     round, the copied-page ledger, page reviews, an automatic fix)
  2. insert at 2: every record moves up one (the insert used to move only
     picks and the QC records)
  3. delete 2 with the 4-slide brief: picks.json comes back byte for byte,
     the _meta.json slides and the _state.json slide records are the ones
     from step 1; the folder is kept in _session/removed_slides/, its id is
     retired in slide_ids.json, the ruling on it is listed and NOT re-tagged,
     a deck ruling naming a moved page number is listed, a sealed brief is
     sealed again, the final check is cleared, the next QC reads every page,
     and an automatic fix from before is refused for undo
  4. refusals that change nothing: a brief that is not one slide shorter, a
     brief missing a different slide than N, an N out of range
  5. --retire / --move of a ruling need the user's words
  6. (Windows) a slide folder in use: retried, then exit 5, nothing changed;
     once free the delete works

Run:  py -3 slide-builder/tests/run_delete_slide_smoke.py
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_layout_inheritance_smoke as fixture  # noqa: E402


def _brief(tpl: Path, slides: list[tuple[str, str]], front_extra: str = "") -> str:
    head = (f"---\nclient_template: {tpl}\ndeck_type: Smoke test\n"
            f"default_layout: body_canonical_light\nmode: template-fill\n{front_extra}---\n\n"
            f"## Deck-level design notes\n\nDelete smoke fixture.\n\n")
    body = ""
    for i, (sid, title) in enumerate(slides, 1):
        body += (f"## Slide {i} — {title}\n\n**Slide id:** {sid}\n"
                 f"**Layout:** body_canonical_light\n"
                 f"**Archetype:** Synthesis / Findings\n"
                 f"**Governing thought:** {title} governing thought.\n"
                 f"**So-what:** {title} so-what.\n"
                 f"**Evidence:** N/A.\n\n")
    return head + body


S4 = [("alpha", "Alpha"), ("beta", "Beta"), ("gamma", "Gamma"), ("delta", "Delta")]
S5 = [S4[0], ("newone", "Inserted page")] + S4[1:]


def _run(script: str, *args: str, env=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                          capture_output=True, text=True, env=env, encoding="utf-8",
                          errors="replace")


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _slide_records(out: Path) -> dict:
    st = _j(out / "_state.json")
    return {"by_option": st["qc"]["by_option"], "blocks": st["qc"]["blocks"],
            "pick_memory": st["pick_memory"],
            "comments": [(c["slide"], c["text"], c["status"]) for c in st["comments"]],
            "approvals": [a["bound"] for a in st["chat_approvals"]],
            "redesign_round": st["redesign_round"],
            "by_slide": st["source_ledger"]["by_slide"],
            "ledger": _j(out / "source_ledger.json")["pages"]}


def _meta_view(out: Path) -> dict:
    m = _j(out / "_meta.json")
    return {"slides": m["slides"], "pps": m.get("pattern_per_slide"),
            "count": m["slide_count"]}


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="delete_slide_smoke_"))
    holder = None
    agents = tmp / "agents"
    shutil.copytree(HERE.parent / "agents", agents)
    env = {k: v for k, v in os.environ.items() if k != "SLIDE_LAB_OPTIONS_PER_SLIDE"}
    env.update({"SLIDE_LAB_AGENTS_DIR": str(agents), "SLIDE_LAB_SETTINGS_LOCAL": "none",
                "SLIDE_LAB_NO_OPEN": "1"})
    try:
        tpl = tmp / fixture.FIXTURE_PPTX.name
        if fixture.FIXTURE_PPTX.exists():
            shutil.copy2(fixture.FIXTURE_PPTX, tpl)
        else:
            fixture.build_fixture(tpl)
        fixture.register_fixture(tpl)
        sess = tmp / "deck" / "_session"
        sess.mkdir(parents=True)
        out = tmp / "deck" / "build"
        b4 = sess / "narrative-brief-4.md"
        b4.write_text(_brief(tpl, S4), encoding="utf-8")

        print("[1] a 4-slide build with every slide-numbered record seeded")
        r = _run("build_deck.py", "--brief", str(b4), "--template", str(tpl), "--out", str(out),
                 "--confirm-template", env=env)
        assert r.returncode == 0, r.stderr[-1500:]
        (out / "picks.json").write_text(json.dumps(
            {"slide_01": "A", "slide_02": "A", "slide_03": "A", "slide_04": "A"}, indent=2),
            encoding="utf-8")
        st = _j(out / "_state.json")
        st["qc"] = {"by_option": {f"slide_0{n}/A": {"blocks": 1 if n == 3 else 0,
                                                     "reasons": ["x"] if n == 3 else []}
                                  for n in range(1, 5)}, "blocks": 1, "detail": ""}
        st["pick_memory"] = {f"slide_0{n}": {"letter": "A", "stamp": f"s{n}"} for n in range(1, 5)}
        st["comments"] = [{"id": 1, "slide": "slide_03", "text": "bigger chart",
                           "kind": "edit", "status": "applied"}]
        st["chat_approvals"] = [{"kind": "qc_fix", "words": "fix those",
                                 "bound": {"slides": "2,3,4"}},
                                {"kind": "qc_undo", "words": "undo slide 4",
                                 "bound": {"slide": "slide_04"}}]
        st["redesign_round"] = {"slides": [3], "three": [3], "kept": {"slide_04": "A"}}
        st["source_ledger"] = {"unresolved": 1, "by_slide": {"slide_03": {"rows": 1}}}
        (out / "_state.json").write_text(json.dumps(st, indent=2), encoding="utf-8")
        (out / "source_ledger.json").write_text(json.dumps({"schema": 2, "pages": {
            "slide_03": {"slide": 3, "rows": [{"id": "slide_03:$5m", "slide": 3,
                                               "figure": "$5m", "resolution": None}]}}},
            indent=2), encoding="utf-8")
        (out / "RESULT-slide-03.md").write_text("slide 3 report", encoding="utf-8")
        picks0 = (out / "picks.json").read_bytes()
        meta0 = _meta_view(out)
        rec0 = _slide_records(out)
        print("    ok")

        print("[2] insert at 2: every slide-numbered record moves up one")
        b5 = sess / "narrative-brief-5.md"
        b5.write_text(_brief(tpl, S5), encoding="utf-8")
        r = _run("build_deck.py", "--brief", str(b5), "--template", str(tpl), "--out", str(out),
                 "--insert", "2", "--confirm-template", env=env)
        assert r.returncode == 0, r.stderr[-1500:]
        rec1 = _slide_records(out)
        assert set(rec1["by_option"]) == {"slide_01/A", "slide_03/A", "slide_04/A", "slide_05/A"}
        assert rec1["by_option"]["slide_04/A"]["blocks"] == 1, rec1["by_option"]
        assert set(rec1["pick_memory"]) == {"slide_01", "slide_03", "slide_04", "slide_05"}
        assert rec1["comments"][0][0] == "slide_04", rec1["comments"]
        assert rec1["approvals"][0]["slides"] == "3,4,5", rec1["approvals"]
        assert rec1["approvals"][1]["slide"] == "slide_05", rec1["approvals"]
        assert rec1["redesign_round"]["slides"] == [4] and rec1["redesign_round"]["three"] == [4]
        assert list(rec1["ledger"]) == ["slide_04"], rec1["ledger"]
        assert rec1["ledger"]["slide_04"]["rows"][0]["id"] == "slide_04:$5m"
        assert rec1["ledger"]["slide_04"]["rows"][0]["slide"] == 4
        assert list(rec1["by_slide"]) == ["slide_04"]
        assert (out / "RESULT-slide-04.md").exists() and not (out / "RESULT-slide-03.md").exists()
        m1 = _j(out / "_meta.json")
        assert [s["slide_id"] for s in sorted(m1["slides"], key=lambda e: e["n"])] == \
            ["alpha", "newone", "beta", "gamma", "delta"], m1["slides"]
        print("    ok: QC records, pick memory, comments, approvals, redesign round, ledger, "
              "reports")

        # Records about the inserted page, made after the insert.
        st = _j(out / "_state.json")
        st["auto_fixes"] = [{"round": 1, "slides": "2", "findings": "slide 2 [overflow]",
                             "before": {"slide_02": {"dir": str(out / "slide_02" / "_autofix_prev"
                                                            / "x"), "pick": "A"}},
                             "status": "fixed"}]
        st["vision_pages"] = {"slides": 5, "renderer": "r", "dpi": 96, "template_fp": "t",
                              "pages": {str(n): {"hash": f"h{n}"} for n in range(1, 6)}}
        st["final_check"] = {"token": "abc", "digests": {}}
        st["review"] = {"token": "tok", "content_hash": st.get("content_hash"),
                        "picks": {"slide_01": "A", "slide_02": "A", "slide_03": "A",
                                  "slide_04": "A", "slide_05": "A"}}
        (out / "_state.json").write_text(json.dumps(st, indent=2), encoding="utf-8")
        p = _j(out / "picks.json")
        p["slide_02"] = "A"
        (out / "picks.json").write_text(json.dumps(p, indent=2), encoding="utf-8")
        sd = sess
        (sd / "rulings.json").write_text(json.dumps({"schema": 1, "rulings": [
            {"n": 1, "id": "newone", "topic": "baseline", "quote": "show the baseline number",
             "reading": "", "at": "2026-10-26T10:00:00"},
            {"n": 2, "id": "deck", "topic": "cut", "quote": "page 4 can go later",
             "reading": "", "at": "2026-10-26T10:01:00"}]}, indent=2), encoding="utf-8")
        rulings_before = (sd / "rulings.json").read_text(encoding="utf-8")

        print("[4] refusals change nothing")
        snap = sorted(p.name for p in out.iterdir())
        state_b = (out / "_state.json").read_bytes()
        for brief_text, n, why in (
                (_brief(tpl, S5), 2, "not one slide shorter"),
                (_brief(tpl, [S5[0], S5[1], S5[3], S5[4]]), 2, "a different slide missing"),
                (_brief(tpl, S4), 9, "out of range")):
            bad = sess / "bad.md"
            bad.write_text(brief_text, encoding="utf-8")
            r = _run("build_deck.py", "--delete", str(n), "--out", str(out), "--brief", str(bad),
                     env=env)
            assert r.returncode == 2, (why, r.returncode, r.stdout[-500:], r.stderr[-500:])
            assert sorted(p.name for p in out.iterdir()) == snap, why
            assert (out / "_state.json").read_bytes() == state_b, why
        assert "Nothing was changed" in r.stderr or "out of range" in r.stderr, r.stderr
        print("    ok: three refusals, exit 2, nothing changed")

        if sys.platform == "win32":
            print("[6] a slide folder in use stops the delete with nothing changed")
            locked = out / "slide_04"
            holder = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)",
                                       str(out)], cwd=str(locked))
            b4_after = sess / "narrative-brief-4b.md"
            b4_after.write_text(_brief(tpl, S4), encoding="utf-8")
            picks_b = (out / "picks.json").read_bytes()
            meta_b = (out / "_meta.json").read_bytes()
            r = _run("build_deck.py", "--delete", "2", "--out", str(out), "--brief",
                     str(b4_after), env=env)
            assert r.returncode == 5, (r.returncode, r.stdout[-800:], r.stderr[-1500:])
            assert "the delete stopped because Windows would not rename" in r.stderr, r.stderr
            assert str(locked) in r.stderr and "Nothing was changed" in r.stderr, r.stderr
            assert holder.poll() is None, "the delete ended a process it did not start"
            assert sorted(p.name for p in out.iterdir()) == snap
            assert (out / "slide_02").is_dir() and (out / "slide_05").is_dir()
            assert (out / "picks.json").read_bytes() == picks_b
            assert (out / "_meta.json").read_bytes() == meta_b
            assert (out / "_state.json").read_bytes() == state_b
            assert not (sess / "removed_slides").exists() or not any(
                (sess / "removed_slides").iterdir()), "an empty archive folder was left"
            holder.kill()                       # the one process this test started
            holder.wait(timeout=30)
            holder = None
            print("    ok: exit 5, the holder left running, every folder and record unchanged")
        else:
            print("[6] skipped (Windows only: folders lock only there)")

        print("[3] delete 2 with the 4-slide brief (sealed after the slide was taken out "
              "of a sealed brief)")
        b4s = sess / "narrative-brief-4s.md"
        b4s.write_text(_brief(tpl, S5), encoding="utf-8")
        r = _run("seal_brief.py", "--brief", str(b4s), "--accepted", "smoke fixture", env=env)
        assert r.returncode == 0, r.stdout[-800:]
        fm = re.match(r"\A---\n(.*?)\n---\n", b4s.read_text(encoding="utf-8"), re.S).group(1)
        gate = "".join(ln + "\n" for ln in fm.split("\n") if ln.startswith("storyline_gate"))
        b4s.write_text(_brief(tpl, S4, front_extra=gate), encoding="utf-8")
        r = _run("build_deck.py", "--delete", "2", "--out", str(out), "--brief", str(b4s),
                 env=env)
        assert r.returncode == 0, (r.stdout[-1500:], r.stderr[-1500:])
        o = r.stdout
        assert "Deleted slide 2 (newone)" in o, o
        assert "sealing it again" in o and "[ok] sealed" in o, o
        import seal_brief
        import build_deck
        txt = b4s.read_text(encoding="utf-8")
        fm2, _ = build_deck.extract_front_matter(txt)
        assert seal_brief._fingerprint_as_prep_reads(txt) == fm2["storyline_gate_sha"], \
            "the brief was not sealed again"
        if "storyline_gate_accepted" in gate:
            assert "smoke fixture" in fm2.get("storyline_gate_accepted", ""), fm2
        # Round trip: back to step 1.
        assert (out / "picks.json").read_bytes() == picks0, (out / "picks.json").read_text()
        assert _meta_view(out) == meta0, (_meta_view(out), meta0)
        rec3 = _slide_records(out)
        assert rec3 == rec0, json.dumps({"now": rec3, "was": rec0}, indent=1)[:3000]
        assert (out / "RESULT-slide-03.md").read_text(encoding="utf-8") == "slide 3 report"
        print("    ok: picks.json byte for byte, _meta.json slides and _state.json slide "
              "records as before the insert")
        arch = list((sess / "removed_slides").iterdir())
        assert len(arch) == 1 and arch[0].name.startswith("02_newone_"), arch
        assert (arch[0] / "slide_02" / "_prompt.md").exists(), "the removed folder was not kept"
        rr = _j(arch[0] / "removed_records.json")
        assert rr["id"] == "newone" and rr["records"]["picks"] == {"slide_02": "A"}, rr
        reg = _j(sess / "slide_ids.json")
        assert reg["ids"]["newone"].get("retired"), reg
        assert (sd / "rulings.json").read_text(encoding="utf-8") == rulings_before, \
            "rulings were changed by the delete"
        assert "RULINGS on the removed slide (newone)" in o and "R1 baseline" in o, o
        assert "R2 [deck]: \"page 4 can go later\"" in o, o
        assert "--move <R> --to" in o and "--retire <R>" in o, o
        st = _j(out / "_state.json")
        assert "final_check" not in st, "the final check was not cleared"
        assert st["review"]["picks"] == {"slide_01": "A", "slide_02": "A", "slide_03": "A",
                                         "slide_04": "A"}, st["review"]
        assert st["review"]["content_hash"] == st["content_hash"], "review not re-bound"
        assert st["stages"]["prep"]["step"] == "delete"
        assert "build_review.py --out" in o and "--final" in o, o
        import qc_pages
        man = {"slides": 4, "renderer": "r", "dpi": 96, "template_fp": "t",
               "pages": [{"page": n, "hash": f"h{n}"} for n in range(1, 5)]}
        a = qc_pages.assess(st, {**man, "slides": 5})
        assert a["full"] and any("renumbered" in x for x in a["reasons"]), a
        assert qc_pages.unreviewed_pages(st, {**man, "slides": 5}) == [1, 2, 3, 4]
        import apply_qc_fix
        rc = apply_qc_fix.undo(out, 2, "undo slide 2", st, _j(out / "picks.json"))
        assert rc == 5, rc
        print("    ok: folder kept, id retired, rulings listed and untouched, sealed again, "
              "final check cleared, review kept, full QC re-read, old undo refused")

        print("[5] --retire / --move need the user's words")
        tr = tmp / "t.jsonl"
        tr.write_text(json.dumps({"type": "user", "message": {
            "role": "user", "content": "retire the baseline one, it went with the page"}}) + "\n",
            encoding="utf-8")
        envt = {**env, "SLIDE_LAB_TRANSCRIPT": str(tr)}
        r = _run("add_ruling.py", "--out", str(out), "--retire", "1", "--user-said",
                 "you can drop it", env=envt)
        assert r.returncode == 4, r.stdout
        r = _run("add_ruling.py", "--out", str(out), "--move", "1", "--to", "nosuch",
                 "--user-said", "retire the baseline one", env=envt)
        assert r.returncode == 3, r.stdout
        r = _run("add_ruling.py", "--out", str(out), "--retire", "1", "--user-said",
                 "retire the baseline one", env=envt)
        assert r.returncode == 0, r.stdout
        data = _j(sd / "rulings.json")
        assert data["rulings"][0]["retired"] and data["rulings"][0]["quote"] == \
            "show the baseline number" and data["rulings"][0]["id"] == "newone"
        md = (sd / "rulings.md").read_text(encoding="utf-8")
        assert "## Slide id: newone (slide removed" in md and "(retired: slide removed)" in md, md
        r = _run("add_ruling.py", "--out", str(out), "--move", "2", "--to", "gamma",
                 "--user-said", "retire the baseline one", env=envt)
        assert r.returncode == 0, r.stdout
        data = _j(sd / "rulings.json")
        assert data["rulings"][2]["id"] == "gamma" and data["rulings"][2]["quote"] == \
            "page 4 can go later" and data["rulings"][1]["replaced_by"] == 3, data
        print("    ok: refused without the user's words; retired and moved with them, "
              "quotes unchanged")

        print("\nSMOKE PASSED.")
        return 0
    finally:
        if holder is not None:
            holder.kill()
            holder.wait(timeout=30)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
