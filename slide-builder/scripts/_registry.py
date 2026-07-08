"""Persistent, self-healing registry of registered client templates.

Purpose
-------
Slide Lab needs to offer the user a pick-list of templates they have already
set up, instead of guessing or assuming a `.pptx` path. Historically a template
was "registered" only in the sense that its per-template sidecar folder
(`<stem>/brand.yml` + `theme.json` + `chrome.yml`) existed on disk next to the
`.pptx`; nothing enumerated them. This module is that missing index.

Design
------
- The index lives MACHINE-LOCAL at ``~/.claude/slide_lab_registry.json`` — a
  sibling of the ``~/.claude/skills/`` repo, so ``git pull`` never touches it,
  and it needs no .gitignore entry. The filename is deliberately flat (not under
  a ``slide-lab/`` dir) so nobody confuses it with the ``skills/slide-lab/`` skill.
- The sidecars on disk are the SOURCE OF TRUTH; this file is a cache. Every read
  path (``list_templates``) runs ``reconcile()`` first, which:
    * prunes entries whose ``.pptx`` or build copy vanished, and
    * rediscovers sidecar bundles sitting in the user's OneDrive / Documents
      folders (reusing the bounded disk scan in ``_contract``).
  So the index self-corrects and effectively follows the user across machines
  (the sidecars travel via OneDrive; the local index is rebuilt from them).
- Writes are atomic (temp file + ``os.replace``) so a crash mid-write can't
  corrupt the index. Registrations are rare + single-user-per-machine, so no
  cross-process lock is taken; a lost update is one reconcile away from healing.

Entry shape (one per template)::

    {
      "display_name":          "Acme — Template2",
      "template_path":         "<abs path to the source .pptx>",
      "build_template_path":   "<abs path a build should open>",  # == template_path
                                    # until Stage 3 sets it to the normalized copy
      "template_sha8":         "a1b2c3d4",
      "default_content_layout":"2_Title & Text 01",
      "brand_primary_hex":     "#0B5FFF",
      "brand_accent_hex":      "#FF6A00",
      "registered_at":         "<iso8601>",   # from the sidecar (who/when registered)
      "registered_by":         "<username>",
      "last_seen_at":          "<iso8601>"     # refreshed by reconcile()
    }

Identity / dedup key: the casefolded, resolved ``template_path`` — two on-disk
copies of the same template are two entries; re-registering the same file updates
its entry in place. The SHA is NOT the key (copies share a SHA).
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import _paths as _p

REGISTRY_PATH: Path = Path.home() / ".claude" / "slide_lab_registry.json"
REGISTRY_SCHEMA_VERSION = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _key(template_path: str | Path) -> str:
    """Dedup/identity key: casefolded resolved absolute path."""
    try:
        return str(Path(template_path).resolve()).casefold()
    except (OSError, ValueError):
        return str(template_path).casefold()


def _empty_registry() -> dict[str, Any]:
    return {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "updated_at": None,
        "templates": [],
    }


def load_registry() -> dict[str, Any]:
    """Read + parse the registry JSON. Never raises: a missing or corrupt file
    yields a fresh empty skeleton. Pure read — does NOT reconcile."""
    try:
        obj = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return _empty_registry()
    if not isinstance(obj, dict) or not isinstance(obj.get("templates"), list):
        return _empty_registry()
    obj.setdefault("schema_version", REGISTRY_SCHEMA_VERSION)
    return obj


def _write_registry(obj: dict[str, Any]) -> None:
    """Atomically persist the registry (temp file in the same dir + os.replace)."""
    obj["updated_at"] = _now()
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".slide_lab_registry.", suffix=".tmp",
                               dir=str(REGISTRY_PATH.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2)
        os.replace(tmp, REGISTRY_PATH)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def _display_name(pptx: Path) -> str:
    """Human-friendly label: '<Client> — <Stem>'. Reuses build_deck's slug logic
    so the name matches the rest of the pipeline; falls back to the stem."""
    try:
        from build_deck import detect_client_slug  # lazy: avoid import cost/cycles
        slug = detect_client_slug(pptx, None)
        client = slug.replace("-", " ").title() if slug else ""
    except Exception:
        client = ""
    return f"{client} — {pptx.stem}" if client else pptx.stem


def _entry_from_template(pptx: Path) -> Optional[dict[str, Any]]:
    """Build one registry entry by reading the template's ``theme.json`` sidecar.

    Returns None if theme.json is absent/unreadable — i.e. the template isn't
    actually registered. Single source used by BOTH the write hook and
    rediscovery so a freshly-registered entry and a rediscovered one are identical.
    """
    pptx = Path(pptx)
    try:
        theme = json.loads(_p.theme_json(pptx).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    brand = theme.get("brand") or {}
    template_path = str(pptx.resolve())
    build_template_path = theme.get("build_template_path") or template_path
    return {
        "display_name": _display_name(pptx),
        "template_path": template_path,
        "build_template_path": build_template_path,
        "template_sha8": (theme.get("template_sha") or "")[:8],
        "default_content_layout": theme.get("default_content_layout") or "",
        "brand_primary_hex": (brand.get("primary_hex") or "").strip(),
        "brand_accent_hex": (brand.get("accent_hex") or "").strip(),
        "registered_at": theme.get("registered_at") or "",
        "registered_by": theme.get("registered_by") or "",
        "last_seen_at": _now(),
    }


def add_or_update(entry: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Insert-or-replace ``entry`` keyed on its resolved ``template_path``.
    A None entry (e.g. ``_entry_from_template`` found no sidecar) is a no-op.
    Returns the persisted registry object."""
    reg = load_registry()
    if not entry or not entry.get("template_path"):
        return reg
    k = _key(entry["template_path"])
    reg["templates"] = [t for t in reg["templates"]
                        if _key(t.get("template_path", "")) != k]
    reg["templates"].append(entry)
    reg["templates"].sort(key=lambda t: t.get("display_name", "").casefold())
    _write_registry(reg)
    return reg


def reconcile() -> dict[str, Any]:
    """Self-heal, then persist:
      1. prune entries whose template_path OR build_template_path no longer exist;
      2. rediscover sidecar bundles under the user's scan roots (reusing the
         bounded scan in ``_contract``) and add any not already present;
      3. refresh ``last_seen_at`` on survivors.
    Returns the reconciled registry object."""
    reg = load_registry()
    survivors: list[dict[str, Any]] = []
    seen: set[str] = set()
    for t in reg["templates"]:
        tp = t.get("template_path", "")
        bt = t.get("build_template_path", "") or tp
        if tp and Path(tp).exists() and (not bt or Path(bt).exists()):
            t["last_seen_at"] = _now()
            survivors.append(t)
            seen.add(_key(tp))

    # Rediscover from disk. Reuse the bounded scan; ask for a higher cap than the
    # diagnostic default so a real template library isn't silently truncated.
    try:
        import _contract
        pairs = _contract._opportunistic_chrome_yml_pairs(cap=200, max_depth=6)
    except Exception:
        pairs = []
    for _chrome_yml, pptx in pairs:
        if _key(pptx) in seen:
            continue
        entry = _entry_from_template(Path(pptx))
        if entry:
            survivors.append(entry)
            seen.add(_key(pptx))

    survivors.sort(key=lambda t: t.get("display_name", "").casefold())
    reg["templates"] = survivors
    _write_registry(reg)
    return reg


def list_templates(reconcile_first: bool = True) -> list[dict[str, Any]]:
    """Consumer-facing accessor: reconcile (default) then return the sorted list.
    This is what the front-door pick-list and the ``register_template.py list``
    subcommand call."""
    reg = reconcile() if reconcile_first else load_registry()
    return reg.get("templates", [])
