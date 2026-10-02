#!/usr/bin/env python3
"""doctor.py — is Slide Lab installed and ready on this computer?

  py -3 slide-builder/scripts/doctor.py          check only, changes nothing
  py -3 slide-builder/scripts/doctor.py fix      check, then fix the local pieces

Prints one table: piece / OK or NOT OK / what to do. Exit 0 when everything a
build needs is in place, 1 otherwise.

`fix` only does local, low-risk things: copies the two agent files Claude Code
runs, adds Slide Lab's permissions to ~/.claude/settings.json (merging, never
overwriting), and creates the local work folder plus a Desktop shortcut. It
never downloads or installs anything. Package installs and the browser
download are printed as commands so Claude runs each one visibly, where the
computer's own approval prompt can show.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
REPO = SKILL.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "slide-qc" / "scripts"))

WINDOWS = platform.system() == "Windows"
PY = "py -3" if WINDOWS else "python3"
REQS = REPO / "requirements.txt"

# import name -> what it is for, in plain words
PACKAGES = [
    ("pptx", "python-pptx", "builds PowerPoint files"),
    ("lxml", "lxml", "reads PowerPoint internals"),
    ("yaml", "pyyaml", "reads the brief"),
    ("pydantic", "pydantic", "checks build and template data"),
    ("pypdfium2", "pypdfium2", "turns rendered slides into pictures"),
    ("PIL", "Pillow", "pictures"),
    ("matplotlib", "matplotlib", "charts"),
    ("numpy", "numpy", "charts and checks"),
    ("openpyxl", "openpyxl", "Excel chart data"),
    ("fontTools", "fonttools", "measures text for the translator"),
    ("docx", "python-docx", "Word version of the storyline"),
    ("playwright", "playwright", "renders design sketches"),
]

AGENT_ALLOWS = ["Agent(slide-builder-worker)", "Agent(slide-builder-translator)"]
BASE_ALLOWS = ["Bash", "PowerShell", "Read", "Write", "Edit", "Glob", "Grep",
               "WebFetch", "Agent(Explore)", "Agent(Plan)"] + AGENT_ALLOWS

WORK_DIR = Path.home() / "Slide Lab" / "sessions"
SYNC_WORDS = ("onedrive", "dropbox", "google drive", "icloud", "box sync")


def _row(rows, piece, ok, todo="", required=True):
    rows.append({"piece": piece, "ok": ok, "todo": todo, "required": required})


# ---------------------------------------------------------------- checks
def check_python(rows):
    v = sys.version_info
    ok = v >= (3, 10)
    _row(rows, f"Python {v.major}.{v.minor}", ok,
         "" if ok else "Install Python 3.10 or newer (company software portal "
                       "or python.org), then run this check again.")


def check_packages(rows):
    missing = []
    for mod, pip_name, _why in PACKAGES:
        try:
            importlib.import_module(mod)
        except Exception:
            missing.append(pip_name)
    if missing:
        _row(rows, "Python packages", False,
             f"Missing: {', '.join(missing)}. Run:  {PY} -m pip install --user "
             f"-r \"{REQS}\"")
    else:
        _row(rows, "Python packages", True)


def check_browser(rows):
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        _row(rows, "Browser for rendering designs", False,
             "Install the Python packages first (row above).")
        return
    from _browser import launch
    tried = {}
    for name in ("chromium", "edge", "chrome"):
        os.environ["SLIDE_LAB_BROWSER"] = name
        try:
            with sync_playwright() as pw:
                b = launch(pw)
                b.close()
            tried[name] = True
            break
        except Exception:
            tried[name] = False
    os.environ.pop("SLIDE_LAB_BROWSER", None)
    if tried.get("chromium"):
        _row(rows, "Browser for rendering designs", True)
    elif any(tried.values()):
        which = "Microsoft Edge" if tried.get("edge") else "Google Chrome"
        _row(rows, "Browser for rendering designs", True,
             f"Using {which} (Playwright's own Chromium is not installed; "
             f"optional:  {PY} -m playwright install chromium)")
    else:
        _row(rows, "Browser for rendering designs", False,
             f"Run:  {PY} -m playwright install chromium   (if the download "
             f"is blocked, install Microsoft Edge or Google Chrome instead)")


def check_libreoffice(rows):
    try:
        from render_slides import _resolve_soffice, render_libre
        _resolve_soffice()
    except Exception:
        _row(rows, "LibreOffice", False,
             "Install LibreOffice from the company software portal (or "
             "libreoffice.org). It is required: template registration, the "
             "final check page and the quality check all use it.")
        return
    try:
        from pptx import Presentation
        with tempfile.TemporaryDirectory() as td:
            deck = Path(td) / "doctor.pptx"
            prs = Presentation()
            prs.slides.add_slide(prs.slide_layouts[0]).shapes.title.text = "Slide Lab check"
            prs.save(str(deck))
            import contextlib, io
            with contextlib.redirect_stdout(io.StringIO()):
                render_libre(deck, Path(td) / "png", 40)
            ok = any((Path(td) / "png").glob("*.png"))
    except Exception:
        ok = False
    _row(rows, "LibreOffice", ok,
         "" if ok else "LibreOffice is installed but could not convert a test "
                       "slide. Close any open LibreOffice windows and run this "
                       "check again.")


def _digest(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def check_agents(rows):
    from _install import check_installed_agents
    problems = check_installed_agents()
    _row(rows, "Slide Lab agents", not problems,
         "" if not problems else "Run:  " + f"{PY} \"{Path(__file__)}\" fix")


def _settings_path() -> Path:
    return Path.home() / ".claude" / "settings.json"


def _load_settings() -> tuple[dict, bool]:
    p = _settings_path()
    if not p.exists():
        return {}, False
    raw = p.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return json.loads(raw.decode("utf-8-sig") or "{}"), bom


def check_settings(rows):
    try:
        data, _ = _load_settings()
    except Exception:
        _row(rows, "Claude settings", False,
             f"{_settings_path()} is not valid JSON. Ask Claude to repair it.")
        return
    allow = set(((data.get("permissions") or {}).get("allow")) or [])
    missing = [a for a in AGENT_ALLOWS if a not in allow]
    _row(rows, "Claude settings", not missing,
         "" if not missing else "Without these, Claude asks \"allow?\" for "
         f"every slide. Run:  {PY} \"{Path(__file__)}\" fix", required=False)


def _under_sync(p: Path) -> bool:
    return any(w in str(p).lower() for w in SYNC_WORDS)


def check_work_folder(rows):
    ok = WORK_DIR.is_dir()
    if ok and _under_sync(WORK_DIR.resolve()):
        _row(rows, "Local work folder", False,
             f"{WORK_DIR} is inside a synced folder (OneDrive or similar), "
             "which makes builds slow. Use a folder on the local drive.",
             required=False)
        return
    _row(rows, "Local work folder", ok,
         f"{WORK_DIR}" if ok else f"Run:  {PY} \"{Path(__file__)}\" fix   "
         f"(creates {WORK_DIR} and a Desktop shortcut)", required=False)


def run_checks() -> list[dict]:
    rows: list[dict] = []
    check_python(rows)
    check_packages(rows)
    check_browser(rows)
    check_libreoffice(rows)
    check_agents(rows)
    check_settings(rows)
    check_work_folder(rows)
    return rows


# ---------------------------------------------------------------- fixes
def fix_agents() -> str:
    from _install import AGENT_NAMES, installed_agents_dir
    dest = installed_agents_dir()
    dest.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in AGENT_NAMES:
        src = SKILL / "agents" / f"{name}.md"
        if src.exists() and (not (dest / src.name).exists()
                             or _digest(src) != _digest(dest / src.name)):
            shutil.copy2(src, dest / src.name)
            copied.append(name)
    return ("copied " + ", ".join(copied) + " (restart Claude to load them)") if copied else ""


def fix_settings() -> str:
    data, bom = _load_settings()
    perms = data.setdefault("permissions", {})
    allow = perms.setdefault("allow", [])
    added = [a for a in BASE_ALLOWS if a not in allow and (WINDOWS or a != "PowerShell")]
    if not added:
        return ""
    allow.extend(added)
    p = _settings_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        shutil.copy2(p, p.with_name("settings.backup-before-slide-lab.json"))
    text = json.dumps(data, indent=2)
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
    return "added to Claude settings: " + ", ".join(added)


def _desktop() -> Path | None:
    if WINDOWS:
        try:
            out = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "[Environment]::GetFolderPath('Desktop')"],
                capture_output=True, text=True, timeout=30).stdout.strip()
            return Path(out) if out else None
        except Exception:
            return None
    d = Path.home() / "Desktop"
    return d if d.is_dir() else None


def fix_work_folder() -> str:
    msgs = []
    if not WORK_DIR.is_dir():
        WORK_DIR.mkdir(parents=True, exist_ok=True)
        msgs.append(f"created {WORK_DIR}")
    desk = _desktop()
    if desk and desk.is_dir():
        if WINDOWS:
            lnk = desk / "Slide Lab.lnk"
            if not lnk.exists():
                ps = ("$s=(New-Object -ComObject WScript.Shell).CreateShortcut("
                      f"'{lnk}'); $s.TargetPath='{WORK_DIR.parent}'; $s.Save()")
                r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                                   capture_output=True, text=True, timeout=30)
                if r.returncode == 0:
                    msgs.append(f"Desktop shortcut: {lnk}")
        else:
            link = desk / "Slide Lab"
            if not link.exists():
                try:
                    link.symlink_to(WORK_DIR.parent)
                    msgs.append(f"Desktop shortcut: {link}")
                except OSError:
                    pass
    return "; ".join(msgs)


# ---------------------------------------------------------------- output
def print_table(rows) -> None:
    w = max(len(r["piece"]) for r in rows)
    print()
    print(f"  {'Piece'.ljust(w)}  Status   What to do")
    print(f"  {'-' * w}  -------  ----------")
    for r in rows:
        status = "OK" if r["ok"] else ("NOT OK" if r["required"] else "missing")
        print(f"  {r['piece'].ljust(w)}  {status.ljust(7)}  {r['todo']}")
    print()


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] not in ("check", "fix"):
        print(__doc__)
        return 2
    if argv and argv[0] == "fix":
        for fn in (fix_agents, fix_settings, fix_work_folder):
            try:
                msg = fn()
            except Exception as exc:
                msg = f"{fn.__name__} failed: {type(exc).__name__}: {exc}"
            if msg:
                print(f"  [fixed] {msg}")
    rows = run_checks()
    print_table(rows)
    bad = [r for r in rows if r["required"] and not r["ok"]]
    if bad:
        print("  Slide Lab is NOT ready yet. Do the steps above in order, then "
              "run this check again.")
        return 1
    print("  Slide Lab is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
