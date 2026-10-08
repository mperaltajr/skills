"""Start the headless browser that renders design sketches.

Tries Playwright's own Chromium first. When that is missing (its download is
often blocked on corporate networks), falls back to a browser that is already
on the machine: Microsoft Edge (every Windows PC), then Google Chrome.

SLIDE_LAB_BROWSER=edge|chrome|chromium forces one choice (used to test the
fallback against the bundled Chromium).

Every page opened through the returned browser drops a design's @font-face
rule that points a font installed on this computer at a font file. A designer
once pointed the brand family at a copied file that held its narrow face, so
the review picture and the conversion were drawn about a quarter narrower
than the finished slide (2026-10-08). The installed font is what PowerPoint
uses, so it is what the sketch must be drawn in. Each removal is printed as a
warning and recorded on the page as window.__slidelabFontFaceRemoved.
"""
from __future__ import annotations

import json
import os
import sys

_CHANNELS = {"chromium": None, "edge": "msedge", "chrome": "chrome"}

# Runs in the page before its own scripts: removes the rules on
# DOMContentLoaded and again on load (stylesheets that arrive late), before
# anything is measured or photographed.
_STRIP_JS = r"""(() => {
  const FAMS = new Set(__FAMS__);
  const norm = s => (s || '').trim().replace(/^["']|["']$/g, '').trim().toLowerCase();
  window.__slidelabFontFaceRemoved = window.__slidelabFontFaceRemoved || [];
  function scrub(owner) {
    let rules;
    try { rules = owner.cssRules; } catch (e) { return; }
    if (!rules) return;
    for (let i = rules.length - 1; i >= 0; i--) {
      const r = rules[i];
      if (r.type === 5) {                        // CSSRule.FONT_FACE_RULE
        const fam = norm(r.style.getPropertyValue('font-family'));
        const src = r.style.getPropertyValue('src') || '';
        if (FAMS.has(fam) && /url\(/i.test(src)) {
          owner.deleteRule(i);
          window.__slidelabFontFaceRemoved.push(fam);
          console.warn('SLIDELAB_FONT_FACE_REMOVED ' + fam);
        }
      } else if (r.type === 3) {                 // @import
        if (r.styleSheet) scrub(r.styleSheet);
      } else if (r.cssRules) {                   // @media, @supports, @layer
        scrub(r);
      }
    }
  }
  function run() { for (const sh of Array.from(document.styleSheets)) scrub(sh); }
  document.addEventListener('DOMContentLoaded', run);
  window.addEventListener('load', run);
})();"""


def _installed_families() -> list[str]:
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from _chrome_schema import installed_families
        return sorted(installed_families())
    except Exception:
        return []


def _on_console(msg) -> None:
    try:
        text = msg.text
    except Exception:
        return
    if text.startswith("SLIDELAB_FONT_FACE_REMOVED "):
        fam = text.split(" ", 1)[1]
        sys.stderr.write(
            f"WARN: the design had an @font-face rule pointing the installed font "
            f"{fam!r} at a font file; it was removed, so the sketch is drawn in the "
            f"installed font, the one the finished slide uses. Do not load "
            f"installed fonts from files.\n")


class _Context:
    def __init__(self, ctx):
        self._ctx = ctx

    def __getattr__(self, name):
        return getattr(self._ctx, name)

    def new_page(self, *a, **kw):
        page = self._ctx.new_page(*a, **kw)
        page.on("console", _on_console)
        return page


class _Browser:
    """The launched browser, with the font-file rule removal on every page."""

    def __init__(self, browser, script: str):
        self._browser = browser
        self._script = script

    def __getattr__(self, name):
        return getattr(self._browser, name)

    def new_context(self, *a, **kw):
        ctx = self._browser.new_context(*a, **kw)
        ctx.add_init_script(self._script)
        return _Context(ctx)

    def new_page(self, *a, **kw):
        return self.new_context(*a, **kw).new_page()


def launch(pw, **kwargs):
    """Return a launched browser; raise the first error if nothing starts."""
    forced = (os.environ.get("SLIDE_LAB_BROWSER") or "").strip().lower()
    order = [forced] if forced in _CHANNELS else ["chromium", "edge", "chrome"]
    # Lets the page read its own stylesheets when they are separate local
    # files, so a font rule in a linked file can be removed too.
    args = list(kwargs.pop("args", None) or [])
    if "--allow-file-access-from-files" not in args:
        args.append("--allow-file-access-from-files")
    script = _STRIP_JS.replace("__FAMS__", json.dumps(_installed_families()))
    first_error = None
    for name in order:
        channel = _CHANNELS[name]
        try:
            if channel:
                return _Browser(pw.chromium.launch(channel=channel, args=args, **kwargs), script)
            return _Browser(pw.chromium.launch(args=args, **kwargs), script)
        except Exception as exc:  # not installed / cannot start
            first_error = first_error or exc
    raise first_error
