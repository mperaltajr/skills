#!/usr/bin/env python3
"""Smoke test: prep refuses when the dispatched agents are not the repo's.

Claude Code dispatches the worker and translator from ~/.claude/agents/, not
from slide-builder/agents/. On 2026-09-30 the installed copies were three months
stale, so every translator fix since June existed only in the repo and had never
reached a running agent. build_deck.py now compares the two before dispatch.

Run:  py -3 slide-builder/tests/run_install_check_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import contextlib
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))

import _install  # noqa: E402


def _prep_stderr(agents_dir: Path) -> tuple[int, str]:
    """Run build_deck's pre-dispatch check against a given agents folder."""
    os.environ["SLIDE_LAB_AGENTS_DIR"] = str(agents_dir)
    import build_deck
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = build_deck.stage1_sanity_check(Path("not-a-registered-template.pptx"))
    return rc, err.getvalue()


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="install_check_"))
    try:
        for name in _install.AGENT_NAMES:
            shutil.copy(SKILL / "agents" / f"{name}.md", tmp / f"{name}.md")

        print("1. matching copies pass the agent check")
        rc, err = _prep_stderr(tmp)
        assert "not the ones in this repo" not in err, err
        print("    ok: prep moves on to the template checks")

        print("2. a stale translator stops prep before any agent is dispatched")
        with (tmp / "slide-builder-translator.md").open("a", encoding="utf-8") as fh:
            fh.write("\n<!-- an older copy -->\n")
        rc, err = _prep_stderr(tmp)
        assert rc == 7, rc
        assert "slide-builder-translator: installed copy differs" in err, err
        assert "copy " in err, "the refusal must print the command that fixes it"
        print("    ok: exit 7 with the copy command")

        print("3. a missing worker stops prep")
        (tmp / "slide-builder-worker.md").unlink()
        rc, err = _prep_stderr(tmp)
        assert rc == 7 and "slide-builder-worker: not installed" in err, err
        print("    ok: exit 7")
    finally:
        os.environ.pop("SLIDE_LAB_AGENTS_DIR", None)
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
