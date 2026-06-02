"""migrate_template_layout.py — one-shot: flat sidecar layout -> subfolder.

Pre-v0.4 templates dumped ~9 sidecar files plus a `<stem>.thumbnails/`
directory flat into `_templates/`, prefixed with the template stem:

    _templates/
      FDX Template.pptx
      FDX Template.brand.yml
      FDX Template.theme.json
      FDX Template.chrome.yml
      FDX Template.preview.pptx
      FDX Template.preview.png
      FDX Template.palette.png
      FDX Template.register.html
      FDX Template.register.proposal.json
      FDX Template.register.picks.json
      FDX Template.thumbnails/

v0.4 moves them into a per-template subfolder so the `_templates/` root
contains only the .pptx files and one subfolder per template:

    _templates/
      FDX Template.pptx
      FDX Template/
        brand.yml
        theme.json
        chrome.yml
        preview.pptx
        ...
        thumbnails/

Usage
-----
    py -3 slide-builder/scripts/migrate_template_layout.py <templates_dir>

`<templates_dir>` is the directory holding the .pptx files (e.g.
`C:/.../OneDrive - Accenture/Claude Projects/_templates`).

Behavior
--------
For every .pptx in the directory:
  - Detect flat-layout sidecars (anything matching `<stem>.<suffix>` for
    known suffixes, plus the `<stem>.thumbnails/` directory).
  - Create `<stem>/` subfolder if absent.
  - MOVE each flat artifact into `<stem>/<suffix>`. The `<stem>.` prefix is
    stripped on the new name; `<stem>.thumbnails/` becomes `<stem>/thumbnails/`.
  - Skip the .pptx itself.
  - Report what moved.

Idempotent: re-running on an already-migrated template is a no-op.
Refuses to overwrite an existing subfolder file (would indicate a partial
prior migration or hand-edits that need operator review).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

# Known sidecar suffixes (everything after `<stem>.`) produced by
# register_template.py. Order = report order. Keep in sync with _paths.py.
KNOWN_SIDECAR_SUFFIXES = [
    "brand.yml",
    "theme.json",
    "chrome.yml",
    "chrome.commit_method.txt",
    "preview.pptx",
    "preview.png",
    "palette.png",
    "register.html",
    "register.proposal.json",
    "register.picks.json",
]
KNOWN_SIDECAR_DIRS = ["thumbnails"]


def discover_flat_artifacts(template_pptx: Path) -> tuple[list[Path], list[Path]]:
    """Return (files, dirs) that match the flat layout for this template."""
    stem = template_pptx.stem
    parent = template_pptx.parent
    files: list[Path] = []
    for suffix in KNOWN_SIDECAR_SUFFIXES:
        candidate = parent / f"{stem}.{suffix}"
        if candidate.exists() and candidate.is_file():
            files.append(candidate)
    dirs: list[Path] = []
    for suffix in KNOWN_SIDECAR_DIRS:
        candidate = parent / f"{stem}.{suffix}"
        if candidate.exists() and candidate.is_dir():
            dirs.append(candidate)
    return files, dirs


def migrate_one(template_pptx: Path) -> dict:
    """Migrate a single template. Returns a per-template report dict."""
    stem = template_pptx.stem
    parent = template_pptx.parent
    target_dir = parent / stem

    files, dirs = discover_flat_artifacts(template_pptx)
    if not files and not dirs:
        return {"template": template_pptx.name, "status": "nothing-to-migrate",
                "moved": [], "skipped": [], "conflicts": []}

    target_dir.mkdir(parents=True, exist_ok=True)

    moved: list[str] = []
    skipped: list[str] = []
    conflicts: list[str] = []

    for src in files:
        suffix = src.name[len(stem) + 1:]  # strip "<stem>."
        dst = target_dir / suffix
        if dst.exists():
            conflicts.append(f"{src.name} -> {dst.relative_to(parent)} (target exists)")
            continue
        shutil.move(str(src), str(dst))
        moved.append(f"{src.name} -> {dst.relative_to(parent)}")

    for src in dirs:
        suffix = src.name[len(stem) + 1:]
        dst = target_dir / suffix
        if dst.exists():
            conflicts.append(f"{src.name}/ -> {dst.relative_to(parent)}/ (target exists)")
            continue
        shutil.move(str(src), str(dst))
        moved.append(f"{src.name}/ -> {dst.relative_to(parent)}/")

    status = "ok" if not conflicts else "partial-conflicts"
    return {
        "template": template_pptx.name,
        "status": status,
        "moved": moved,
        "skipped": skipped,
        "conflicts": conflicts,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("USAGE: py -3 migrate_template_layout.py <templates_dir>")
        return 2
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}")
        return 2

    pptx_files = sorted(p for p in root.glob("*.pptx") if p.is_file())
    if not pptx_files:
        print(f"  no .pptx files found in {root}")
        return 0

    print("=" * 72)
    print(f"Migrating templates in: {root}")
    print(f"  found {len(pptx_files)} .pptx file(s)")
    print("=" * 72)

    all_ok = True
    for tpl in pptx_files:
        print(f"\n[{tpl.name}]")
        report = migrate_one(tpl)
        if report["status"] == "nothing-to-migrate":
            print(f"  nothing to migrate (already in subfolder layout or no sidecars)")
            continue
        for line in report["moved"]:
            print(f"  moved:    {line}")
        for line in report["conflicts"]:
            print(f"  CONFLICT: {line}")
            all_ok = False
        if report["status"] == "ok":
            print(f"  -> ok")
        else:
            print(f"  -> partial-conflicts ({len(report['conflicts'])})")

    print("\n" + "=" * 72)
    if all_ok:
        print("Migration complete. _templates/ root now contains only .pptx "
              "files and per-template subfolders.")
    else:
        print("Migration finished WITH CONFLICTS. Operator must resolve the "
              "conflicting target files (likely hand-edits or a partial prior "
              "migration). Inspect the listed sources + targets, decide which "
              "wins, then move manually.")
    print("=" * 72)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
