"""_ppt_snapshot.py — what the user has open in PowerPoint, for tests.

snapshot() -> (running, sorted full names of the open presentations).
Attaches to a running PowerPoint only; never starts, opens, closes or quits
anything. Tests take one before and one after and assert they are equal, so
a test that touched the user's decks fails loudly.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slide-qc" / "scripts"))


def snapshot() -> tuple[bool, list[str]]:
    if sys.platform != "win32":
        return False, []
    import ppt_safe
    if not ppt_safe.powerpoint_running():
        return False, []
    try:
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        app = win32com.client.GetActiveObject("PowerPoint.Application")
        return True, sorted(ppt_safe.open_names(app))
    except Exception:
        return True, ["<could not attach>"]
