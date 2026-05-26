"""_log.py — tee pipeline-script stdout/stderr to <out>/build.log.

Every pipeline script (build_deck, finalize_deck, compile_picks, build_review,
build_gate_preview) calls `attach(out_dir, script_name)` at the start of main()
to mirror its console output into a single per-build log file.

The log is append-only across multiple script invocations in the same out_dir,
so a typical build (build_deck → finalize_deck → build_gate_preview → ...) lands
in one file with section banners.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import TextIO


class _Tee:
    def __init__(self, original: TextIO, log_handle: TextIO) -> None:
        self._original = original
        self._log = log_handle

    def write(self, data: str) -> int:
        self._original.write(data)
        try:
            self._log.write(data)
            self._log.flush()
        except Exception:
            pass
        return len(data)

    def flush(self) -> None:
        try:
            self._original.flush()
        except Exception:
            pass
        try:
            self._log.flush()
        except Exception:
            pass

    def __getattr__(self, item):
        return getattr(self._original, item)


_attached: dict[str, object] = {}


def attach(out_dir: Path, script_name: str) -> None:
    """Tee stdout + stderr to <out>/build.log. Safe to call once per script.

    Writes a section banner with timestamp + script name when called.
    Subsequent calls in the same process are no-ops (re-attaching would
    double-write).
    """
    if _attached.get("active"):
        return
    try:
        out_dir = Path(out_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        log_path = out_dir / "build.log"
        log_handle = open(log_path, "a", encoding="utf-8")
    except Exception:
        # Logging is best-effort. If we can't open the log, don't break the build.
        return

    ts = datetime.now().isoformat(timespec="seconds")
    banner = f"\n{'=' * 70}\n[{ts}] {script_name}\n{'=' * 70}\n"
    log_handle.write(banner)
    log_handle.flush()

    sys.stdout = _Tee(sys.stdout, log_handle)
    sys.stderr = _Tee(sys.stderr, log_handle)
    _attached["active"] = True
    _attached["handle"] = log_handle
    _attached["path"] = log_path
