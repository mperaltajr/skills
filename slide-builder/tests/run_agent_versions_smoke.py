#!/usr/bin/env python3
"""Smoke test: the agent-file check says WHICH version is installed, installs
back up first, and a build stops when the agent files change mid-build.

Validated fix from the Kinfield v3.1 session report (item 5, approved
2026-10-09). Worktree builders had copied unmerged agent files into the shared
~/.claude/agents folder; the refusal only said "differs", and a swap and
restore around prep made the prep check certify slides built by an unmerged
agent.

  1. the refusal names the version, from git history: an older version from
     main (copy the repo over), a newer one from main (update this checkout),
     an unmerged branch X (merge branch X first), no committed version (local
     edits: back them up first); without git it falls back, never crashes
  2. doctor.py fix and the printed command back up the installed files to
     _backup_<date>/ (as .md.bak, never loaded as agents) and keep the last few
  3. prep records the installed fingerprints; compile (exit 7) and check_done
     stop when they changed, and say to start a new Claude session

Never touches the real ~/.claude/agents: every step points SLIDE_LAB_AGENTS_DIR
at a temp folder, and the git cases run in a temp repository.

Run:  py -3 slide-builder/tests/run_agent_versions_smoke.py
"""
from __future__ import annotations

import _test_temp  # noqa: F401,E402  (temp folders under the scratch root, deleted at exit)
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SKILL.parent / "slide-qc" / "scripts"))

import _install  # noqa: E402
import _state  # noqa: E402

REAL_AGENTS = Path.home() / ".claude" / "agents"


def _git(repo: Path, *args) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout.strip()


def _real_snapshot() -> dict:
    if not REAL_AGENTS.exists():
        return {}
    return {p.name: p.stat().st_mtime_ns for p in REAL_AGENTS.rglob("*") if p.is_file()}


def main() -> int:
    before = _real_snapshot()
    tmp = Path(tempfile.mkdtemp(prefix="agent_versions_"))
    old_env = os.environ.get("SLIDE_LAB_AGENTS_DIR")
    try:
        agents = tmp / "agents"
        agents.mkdir()
        os.environ["SLIDE_LAB_AGENTS_DIR"] = str(agents)
        for n in _install.AGENT_NAMES:
            shutil.copy(SKILL / "agents" / f"{n}.md", agents / f"{n}.md")
        assert _install.check_installed_agents() == []

        print("1a. an older committed version of this repo is named, with what to do")
        repo_root = SKILL.parent
        rel = "slide-builder/agents/slide-builder-worker.md"
        cur = _install.git_blob_hash(SKILL / "agents" / "slide-builder-worker.md")
        hist = _git(repo_root, "log", "--format=%H", "main", "--", rel).splitlines()
        older = next((c for c in hist[1:]
                      if _git(repo_root, "rev-parse", f"{c}:{rel}") != cur), None)
        if older:
            data = subprocess.run(["git", "-C", str(repo_root), "show", f"{older}:{rel}"],
                                  capture_output=True).stdout
            (agents / "slide-builder-worker.md").write_bytes(data)
            lines = _install.check_installed_agents()
            assert any("older version from main" in x and "copy the repo version over" in x
                       for x in lines), lines
            print("    ok:", lines[0][:150], "...")
        else:
            print("    (skipped: the worker file has one version on main)")
        shutil.copy(SKILL / "agents" / "slide-builder-worker.md", agents / "slide-builder-worker.md")

        print("1b. the four cases in a temp repository (main, newer main, branch, local)")
        repo = tmp / "repo"
        (repo / "slide-builder" / "agents").mkdir(parents=True)
        _git(repo, "init", "-q", "-b", "main")
        _git(repo, "config", "user.email", "t@example.com")
        _git(repo, "config", "user.name", "t")
        f = repo / "slide-builder" / "agents" / "slide-builder-worker.md"
        f.write_text("v1\n", encoding="utf-8")
        _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "v1")
        c1 = _git(repo, "rev-parse", "HEAD")
        f.write_text("v2\n", encoding="utf-8")
        _git(repo, "commit", "-q", "-am", "v2")
        _git(repo, "checkout", "-q", "-b", "feature-x")
        f.write_text("v3 unmerged\n", encoding="utf-8")
        _git(repo, "commit", "-q", "-am", "v3")
        _git(repo, "checkout", "-q", "main")
        saved = (_install.REPO_ROOT, _install.SKILL_ROOT)
        _install.REPO_ROOT, _install.SKILL_ROOT = repo, repo / "slide-builder"
        try:
            inst = tmp / "probe.md"
            inst.write_text("v1\n", encoding="utf-8")
            v = _install.which_version(inst)
            assert v["kind"] == "main_older" and "copy the repo version over" in v["do"], v
            inst.write_text("v3 unmerged\n", encoding="utf-8")
            v = _install.which_version(inst)
            assert v["kind"] == "branch" and v["branch"] == "feature-x", v
            assert "merge branch feature-x" in v["do"], v
            inst.write_text("someone's hand edit\n", encoding="utf-8")
            v = _install.which_version(inst)
            assert v["kind"] == "uncommitted" and "back it up first" in v["do"], v
            _git(repo, "checkout", "-q", c1)                  # this checkout is behind main
            inst.write_text("v2\n", encoding="utf-8")
            v = _install.which_version(inst)
            assert v["kind"] == "main_newer" and "git pull" in v["do"], v
            _git(repo, "checkout", "-q", "main")
            # the full refusal line, through check_installed_agents
            os.environ["SLIDE_LAB_AGENTS_DIR"] = str(tmp)
            shutil.copy(inst, tmp / "slide-builder-worker.md")
            (tmp / "slide-builder-worker.md").write_text("v3 unmerged\n", encoding="utf-8")
            lines = _install.check_installed_agents()
            assert any("unmerged version from branch feature-x" in x for x in lines), lines
            print("    ok: older main / newer main / branch feature-x / local edits")

            print("1c. without git the check falls back and never crashes")
            real_git = _install._git

            def _no_git(*a, **k):
                raise FileNotFoundError("git")
            _install._git = _no_git
            try:
                lines = _install.check_installed_agents()
                assert any(x.endswith("installed copy differs from the repo") for x in lines), lines
            finally:
                _install._git = real_git
            print("    ok:", [x for x in lines if "worker" in x][0])
        finally:
            _install.REPO_ROOT, _install.SKILL_ROOT = saved
            os.environ["SLIDE_LAB_AGENTS_DIR"] = str(agents)

        print("1d. build_deck's refusal carries the diagnosis and the new-session line")
        (agents / "slide-builder-translator.md").write_text("hand edit\n", encoding="utf-8")
        import build_deck
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = build_deck.stage1_sanity_check(Path("not-a-registered-template.pptx"))
        e = err.getvalue()
        assert rc == 7 and "local edits" in e and "start a new Claude session" in e, e
        assert e.index("_backup_") < e.rindex("slide-builder-translator.md\""), \
            "the printed command must back up before it copies"
        print("    ok: exit 7, says which version, backs up before copying")

        print("2. doctor fix backs up first, as .md.bak in a subfolder, keeps the last few")
        for i in range(1, 8):
            (agents / f"_backup_2026-01-0{i}").mkdir()
        import doctor
        msg = doctor.fix_agents()
        assert "start a new Claude session" in msg and "_backup_" in msg, msg
        backups = sorted(p.name for p in agents.glob("_backup_*"))
        assert len(backups) == _install.KEEP_BACKUPS, backups
        newest = agents / backups[-1]
        assert (newest / "slide-builder-translator.md.bak").read_text(encoding="utf-8") == "hand edit\n"
        assert not list(newest.glob("*.md")), "a backup must never be a loadable .md agent"
        assert _install.check_installed_agents() == [], "fix copied the repo files over"
        print(f"    ok: {msg[:110]}...")

        print("3. prep records the fingerprints; compile and check_done stop on a change")
        out = tmp / "build"
        out.mkdir()
        _state.record_prep(out, "h", out)
        rec = _state.read_state(out)["agents"]["installed"]
        assert rec == _install.installed_fingerprints() and all(rec.values()), rec
        assert _install.changed_since_prep(_state.read_state(out)) == ""
        with (agents / "slide-builder-worker.md").open("a", encoding="utf-8") as fh:
            fh.write("\n<!-- swapped mid-build -->\n")
        why = _install.changed_since_prep(_state.read_state(out))
        assert "slide-builder-worker" in why and "start a new Claude session" in why, why
        env = {**os.environ, "SLIDE_LAB_AGENTS_DIR": str(agents), "SLIDE_LAB_NO_OPEN": "1"}
        r = subprocess.run([sys.executable, str(SCRIPTS / "compile_picks.py"), "--out", str(out)],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 7 and "changed after this build was prepared" in r.stdout, \
            r.stdout[-800:] + r.stderr[-800:]
        r = subprocess.run([sys.executable, str(SCRIPTS / "check_done.py"), "--out", str(out)],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 1, r.stdout
        # check_done stops at "no compile" first; give it a compile to reach the check
        deck = out / "d.pptx"
        from pptx import Presentation
        p = Presentation(); p.slides.add_slide(p.slide_layouts[6]); p.save(str(deck))
        _state.begin_finalize(out); _state.end_finalize(out, "ok")
        _state.record_compile(out, output=deck, slides=1)
        r = subprocess.run([sys.executable, str(SCRIPTS / "check_done.py"), "--out", str(out)],
                           capture_output=True, text=True, env=env)
        assert r.returncode == 1 and "changed after this build was prepared" in r.stdout, r.stdout
        print("    ok: compile exit 7, check_done refuses, both say start a new session")
    finally:
        if old_env is None:
            os.environ.pop("SLIDE_LAB_AGENTS_DIR", None)
        else:
            os.environ["SLIDE_LAB_AGENTS_DIR"] = old_env
        shutil.rmtree(tmp, ignore_errors=True)
    assert _real_snapshot() == before, "the real ~/.claude/agents folder must never change"
    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
