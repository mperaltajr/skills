"""Start the headless browser that renders design sketches.

Tries Playwright's own Chromium first. When that is missing (its download is
often blocked on corporate networks), falls back to a browser that is already
on the machine: Microsoft Edge (every Windows PC), then Google Chrome.

SLIDE_LAB_BROWSER=edge|chrome|chromium forces one choice (used to test the
fallback against the bundled Chromium).
"""
from __future__ import annotations

import os

_CHANNELS = {"chromium": None, "edge": "msedge", "chrome": "chrome"}


def launch(pw, **kwargs):
    """Return a launched browser; raise the first error if nothing starts."""
    forced = (os.environ.get("SLIDE_LAB_BROWSER") or "").strip().lower()
    order = [forced] if forced in _CHANNELS else ["chromium", "edge", "chrome"]
    first_error = None
    for name in order:
        channel = _CHANNELS[name]
        try:
            if channel:
                return pw.chromium.launch(channel=channel, **kwargs)
            return pw.chromium.launch(**kwargs)
        except Exception as exc:  # not installed / cannot start
            first_error = first_error or exc
    raise first_error
