"""_paths.py — single source of truth for every pipeline artifact filename.

Every Slide Lab pipeline script (build_deck.py, finalize_deck.py,
build_gate_preview.py, compile_picks.py, build_review.py, register_template.py)
imports from here instead of hardcoding filename strings. This keeps writers
and readers in lockstep: renaming an artifact is a one-line change.

Convention
----------
- Top-level deck artifacts live at <out_dir>/*.
- Per-slide artifacts live at <out_dir>/slide_NN/*.
- Per-option artifacts live at <out_dir>/slide_NN/option_X.*.
- Slide numbers are zero-padded to 2 digits ("slide_01", not "slide_1").
- Option letters are uppercase ("A", "B", "C").

If you find a hardcoded artifact filename in a pipeline script, it belongs
here. Add the helper, swap the hardcoded string for the helper call, and
add the helper to the manifest at the bottom of this file so the contract
test (`_contract.py`) sees it.
"""
from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Filename constants — for callers that already have a slide_dir Path in scope
# (e.g., discovered via iterdir) and want to depend on the registry for the
# bare filename string. Prefer the helper functions below when out_dir + n are
# both available; use these constants only when refactoring to the helper
# would force a larger interface change.
# ---------------------------------------------------------------------------

META_JSON          = "_meta.json"
FINALIZE_META_JSON = "_finalize_meta.json"
DISPATCH_PLAN_MD   = "dispatch_plan.md"
GATE3_PREVIEW_HTML = "GATE3-PREVIEW.html"
REVIEW_HTML        = "REVIEW.html"
PICKS_JSON         = "picks.json"
BRIEF_QC_JSON      = "brief_qc.json"

PROMPT_MD          = "_prompt.md"
PATTERN_PICK_MD    = "_pattern_pick.md"
RAW_DIR            = "_raw"
RENDER_TMP_DIR     = "_render_tmp"


def option_py_name(letter: str)          -> str: return f"option_{letter}.py"
def option_pptx_name(letter: str)        -> str: return f"option_{letter}.pptx"
def option_png_name(letter: str)         -> str: return f"option_{letter}.png"
def option_mmd_name(letter: str)         -> str: return f"option_{letter}.mmd"
def option_mermaid_png_name(letter: str) -> str: return f"option_{letter}-mermaid.png"
def option_qc_json_name(letter: str)     -> str: return f"option_{letter}.qc.json"


# ---------------------------------------------------------------------------
# Slide / option key formatting (string-only — used as dict keys)
# ---------------------------------------------------------------------------

def slide_key(n: int) -> str:
    """Zero-padded slide id, e.g. 'slide_07'. Used as dict keys and dir names."""
    return f"slide_{n:02d}"


def option_letters() -> tuple[str, str, str]:
    """The three canonical option letters."""
    return ("A", "B", "C")


# ---------------------------------------------------------------------------
# Top-level deck artifacts (under <out_dir>/)
# ---------------------------------------------------------------------------

def meta_json(out_dir: Path) -> Path:
    """<out>/_meta.json — canonical deck manifest. Writer: build_deck.py."""
    return out_dir / "_meta.json"


def finalize_meta_json(out_dir: Path) -> Path:
    """<out>/_finalize_meta.json — finalize-stage status. Writer: finalize_deck.py."""
    return out_dir / "_finalize_meta.json"


def dispatch_plan_md(out_dir: Path) -> Path:
    """<out>/dispatch_plan.md — parent-session agent-dispatch plan. Writer: build_deck.py."""
    return out_dir / "dispatch_plan.md"


def gate3_preview_html(out_dir: Path) -> Path:
    """<out>/GATE3-PREVIEW.html — visual sanity gate. Writer: build_gate_preview.py."""
    return out_dir / "GATE3-PREVIEW.html"


def review_html(out_dir: Path) -> Path:
    """<out>/REVIEW.html — pick + QC review surface. Writer: build_review.py."""
    return out_dir / "REVIEW.html"


def picks_json(out_dir: Path) -> Path:
    """<out>/picks.json — user-authored option picks. Writer: chat orchestrator."""
    return out_dir / "picks.json"


def brief_qc_json(out_dir: Path) -> Path:
    """<out>/brief_qc.json — historical orphan reader; see Phase 4 follow-on."""
    return out_dir / "brief_qc.json"


# ---------------------------------------------------------------------------
# Per-slide artifacts (under <out_dir>/slide_NN/)
# ---------------------------------------------------------------------------

def slide_dir(out_dir: Path, n: int) -> Path:
    """<out>/slide_NN/ — per-slide directory."""
    return out_dir / slide_key(n)


def prompt_md(out_dir: Path, n: int) -> Path:
    """<out>/slide_NN/_prompt.md — agent prompt. Writer: build_deck.py."""
    return slide_dir(out_dir, n) / "_prompt.md"


def pattern_pick_md(out_dir: Path, n: int) -> Path:
    """<out>/slide_NN/_pattern_pick.md — agent's chosen pattern + verb. Writer: per-slide agent."""
    return slide_dir(out_dir, n) / "_pattern_pick.md"


# ---------------------------------------------------------------------------
# Per-option artifacts (under <out_dir>/slide_NN/option_X.*)
# ---------------------------------------------------------------------------

def option_py(out_dir: Path, n: int, letter: str) -> Path:
    """<out>/slide_NN/option_X.py — per-option build script. Writer: per-slide agent."""
    return slide_dir(out_dir, n) / f"option_{letter}.py"


def option_pptx(out_dir: Path, n: int, letter: str) -> Path:
    """<out>/slide_NN/option_X.pptx — themed per-option PPTX. Writer: finalize_deck.py."""
    return slide_dir(out_dir, n) / f"option_{letter}.pptx"


def option_png(out_dir: Path, n: int, letter: str) -> Path:
    """<out>/slide_NN/option_X.png — rendered per-option thumbnail. Writer: finalize_deck.py."""
    return slide_dir(out_dir, n) / f"option_{letter}.png"


def option_mmd(out_dir: Path, n: int, letter: str) -> Path:
    """<out>/slide_NN/option_X.mmd — Mermaid fallback spec. Writer: per-slide agent (FALLBACK_MERMAID only)."""
    return slide_dir(out_dir, n) / f"option_{letter}.mmd"


def option_mermaid_png(out_dir: Path, n: int, letter: str) -> Path:
    """<out>/slide_NN/option_X-mermaid.png — rendered Mermaid PNG. Writer: render_mermaid.py."""
    return slide_dir(out_dir, n) / f"option_{letter}-mermaid.png"


def option_qc_json(out_dir: Path, n: int, letter: str) -> Path:
    """<out>/slide_NN/option_X.qc.json — slide-qc per-option vision check. Writer: build_review.py (calls slide-qc)."""
    return slide_dir(out_dir, n) / f"option_{letter}.qc.json"


def option_raw_pptx(out_dir: Path, n: int, letter: str) -> Path:
    """<out>/slide_NN/_raw/option_X.pptx — unthemed raw PPTX from agent script. Writer: finalize_deck.py (pre-graft archive)."""
    return slide_dir(out_dir, n) / "_raw" / f"option_{letter}.pptx"


def render_tmp_dir(pptx: Path) -> Path:
    """<sibling>/_render_tmp/<stem>/ — scratch dir for LibreOffice PNG renders."""
    return pptx.parent / "_render_tmp" / pptx.stem


# ---------------------------------------------------------------------------
# Template-relative artifacts (under <template>.parent/)
# ---------------------------------------------------------------------------
# These live next to the source .pptx — produced by register_template.py at
# one-time registration, consumed by build_deck.py + finalize_deck.py at
# every build. brand.yml / theme.json follow the same convention but are
# referenced directly via tpl.with_name(...) in register_template.py for
# historical reasons; chrome.yml (v0.2) goes through the registry from the
# start.

def chrome_yml(template_pptx: Path) -> Path:
    """<template-stem>.chrome.yml — per-layout chrome geometry sidecar.
    Writer: register_template.py. Readers: finalize_deck.py, build_deck.py.
    See scripts/_chrome_schema.py for the ChromeSpec model + canonical
    body-canonical positions.
    """
    return template_pptx.with_name(f"{template_pptx.stem}.chrome.yml")


# ---------------------------------------------------------------------------
# Manifest — consumed by _contract.py
# ---------------------------------------------------------------------------
# Each entry: (path-helper name, writer script, reader scripts list)
# A writer script is the only script that creates the artifact. Reader scripts
# load it. Orphans (no writer, or no reader) flagged with `accepted: True` are
# known historical drift that the contract test ignores.
#
# IMPORTANT: this manifest is the authoritative pipeline-contract record. If
# you add a new artifact helper above, add it here too — the contract test
# (_contract.py) walks this list and greps the writer/reader scripts.

ARTIFACT_MANIFEST: list[dict] = [
    # Top-level deck
    {"name": "meta_json",          "writer": "build_deck.py",         "readers": ["finalize_deck.py", "compile_picks.py", "build_review.py", "build_gate_preview.py"]},
    {"name": "finalize_meta_json", "writer": "finalize_deck.py",      "readers": ["build_review.py"]},
    {"name": "dispatch_plan_md",   "writer": "build_deck.py",         "readers": [], "accepted": True, "reason": "Consumed by parent chat session, not a pipeline script"},
    {"name": "gate3_preview_html", "writer": "build_gate_preview.py", "readers": [], "accepted": True, "reason": "Terminal artifact — opened by user in browser"},
    {"name": "review_html",        "writer": "build_review.py",       "readers": [], "accepted": True, "reason": "Terminal artifact — opened by user in browser"},
    {"name": "picks_json",         "writer": "chat orchestrator",     "readers": ["compile_picks.py"], "accepted": True, "reason": "Written by chat session, not by a pipeline script"},
    {"name": "brief_qc_json",      "writer": "(unbuilt)",             "readers": ["build_review.py"], "accepted": True, "reason": "Accepted orphan. build_review.py renders a graceful 'not found' banner when the file is absent. v2 prep does not yet emit brief_qc.json; resolved per Phase 4 P4.27 (2026-05-26) as 'keep reader, defer writer until brief-time QC becomes a feature.'"},

    # Per-slide
    {"name": "prompt_md",          "writer": "build_deck.py",         "readers": ["build_gate_preview.py", "build_review.py", "finalize_deck.py"]},
    {"name": "pattern_pick_md",    "writer": "per-slide agent",       "readers": ["build_gate_preview.py"], "accepted": True, "reason": "Written by per-slide worker agent, not by a pipeline script"},

    # Per-option
    {"name": "option_py",          "writer": "per-slide agent",       "readers": ["finalize_deck.py", "build_gate_preview.py", "build_review.py"], "accepted": True, "reason": "Written by per-slide worker agent"},
    {"name": "option_pptx",        "writer": "finalize_deck.py",      "readers": ["compile_picks.py", "build_review.py"]},
    {"name": "option_png",         "writer": "finalize_deck.py",      "readers": ["build_gate_preview.py", "build_review.py"]},
    {"name": "option_mmd",         "writer": "per-slide agent",       "readers": ["finalize_deck.py"], "accepted": True, "reason": "Written by per-slide worker agent (FALLBACK_MERMAID only)"},
    {"name": "option_mermaid_png", "writer": "finalize_deck.py",      "readers": ["finalize_deck.py"], "note": "finalize_deck.py constructs the path and invokes render_mermaid.py via subprocess; render_mermaid.py is brand-agnostic and writes wherever --output points."},
    {"name": "option_qc_json",     "writer": "build_review.py",       "readers": ["build_review.py"]},
    {"name": "option_raw_pptx",    "writer": "finalize_deck.py",      "readers": [], "accepted": True, "reason": "Audit archive — not re-read"},

    # Template-relative (v0.2)
    {"name": "chrome_yml",         "writer": "register_template.py",  "readers": ["finalize_deck.py", "build_deck.py"], "accepted": True, "reason": "v0.2 P1.1: helper + manifest entry land first; writer wires in P1.2; readers wire in P1.3 / P1.4. Drops accepted once readers reference _p.chrome_yml."},
]
