"""_install.py — is the agent Claude Code will dispatch the one in this repo?

Claude Code dispatches `slide-builder-worker` and `slide-builder-translator`
from ~/.claude/agents/, not from slide-builder/agents/. The start-of-session
git pull refreshes this repo only. So every fix written into the repo copy is
invisible at runtime until someone copies the file over, and nothing said so:
on 2026-09-30 the installed copies turned out to be from 18 June, and every
translator fix since (the rule that keeps decks openable in PowerPoint, the
takeaway rule, the chart ban, the label-wrap rule) had never reached a running
agent.

build_deck.py calls check_installed_agents() before any agent is dispatched and
refuses to prep on a mismatch.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
AGENT_NAMES = ("slide-builder-worker", "slide-builder-translator")


def installed_agents_dir() -> Path:
    """Where Claude Code loads user agents from. Overridable for tests."""
    override = os.environ.get("SLIDE_LAB_AGENTS_DIR")
    return Path(override) if override else Path.home() / ".claude" / "agents"


def _digest(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def check_installed_agents() -> list[str]:
    """Return one line per agent whose installed copy is missing or differs."""
    problems: list[str] = []
    dest = installed_agents_dir()
    for name in AGENT_NAMES:
        src = SKILL_ROOT / "agents" / f"{name}.md"
        inst = dest / f"{name}.md"
        if not src.exists():
            continue  # a repo without the agent has nothing to compare
        if not inst.exists():
            problems.append(f"{name}: not installed at {inst}")
        elif _digest(src) != _digest(inst):
            problems.append(f"{name}: installed copy differs from the repo")
    return problems


def copy_command() -> str:
    """The one-liner that fixes it, for the refusal message."""
    dest = installed_agents_dir()
    src = SKILL_ROOT / "agents"
    return "\n".join(
        f'  copy "{src / (n + ".md")}" "{dest / (n + ".md")}"' for n in AGENT_NAMES)
