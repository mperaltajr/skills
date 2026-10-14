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

The browser's own profile (Playwright makes a fresh one for every launch, in
the temp folder of its driver process) goes under the Slide Lab scratch root
and is deleted afterwards: wrap sync_playwright() in scratch_env() (owner's
decision 2026-10-09, one scratch area).

The driver and the browser start with their working folder in that scratch
folder, never in a session or slide folder: a process sitting in a folder
locks it on Windows, and a slide folder that could not be renamed stopped an
insert three times (2026-10-13).

Every render has a time limit (owner's decision 2026-10-13): wrap the block in
render_deadline(). The whole render gets SLIDE_LAB_RENDER_TIMEOUT seconds
(default 120) and each slow step (icon drawing, closing the browser, reading
one slide) SLIDE_LAB_RENDER_STEP_TIMEOUT seconds (default 30). Past either,
the run ends ONLY the processes it started and recorded (the driver and its
browser, never anything found by name), deletes its scratch folder and exits
4 with "timed out, re-run". Six leftover headless browsers from earlier days
were found on the owner's computer before this.

Before the time limit starts, every render takes one of the computer's render
slots (render_slot(), from slide-qc/scripts/render_slot.py; default 16 at once,
SLIDE_LAB_RENDER_SLOTS). The slot goes outside render_deadline(), so waiting
for one is never counted as render time (owner's decision 2026-10-14).
"""
from __future__ import annotations

import contextlib
import json
import os
import shutil
import sys
import threading
import time

_TEMP_VARS = ("TMP", "TEMP", "TMPDIR")
_SCRATCH: list = []              # scratch folders open now (deleted on a time-out)
_SAVED_CWD: list = []            # working folder to go back to once the browser runs
_DEADLINE: list = []             # the render_deadline in force, if any


@contextlib.contextmanager
def scratch_env():
    """For the with-block: the temp folder seen by processes started now (the
    Playwright driver, which makes the browser profile there) is a fresh
    folder under the scratch root, marked in use; it is deleted afterwards.

        with scratch_env(), sync_playwright() as pw:
            browser = launch(pw, headless=True)
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import _scratch
        import tempfile
        folder = __import__("pathlib").Path(
            tempfile.mkdtemp(prefix=f"{os.getpid()}_", dir=str(_scratch.scratch_dir("_browser"))))
    except Exception:
        yield None                                     # no scratch root: change nothing
        return
    saved = {k: os.environ.get(k) for k in _TEMP_VARS}
    _SCRATCH.append(folder)
    try:
        with _scratch.in_use(folder):
            for k in _TEMP_VARS:
                os.environ[k] = str(folder)
            # The driver starts next (sync_playwright) and the browser inherits
            # its working folder: make that the scratch folder. launch() goes
            # back to the caller's folder once the browser is up.
            try:
                _SAVED_CWD.append(os.getcwd())
                os.chdir(folder)
            except OSError:
                pass
            yield folder
    finally:
        _restore_cwd()
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        if folder in _SCRATCH:
            _SCRATCH.remove(folder)
        shutil.rmtree(folder, ignore_errors=True)


def _restore_cwd() -> None:
    while _SAVED_CWD:
        d = _SAVED_CWD.pop()
        try:
            os.chdir(d)
        except OSError:
            pass


# ---------------------------------------------------------------- time limit
def _seconds(env: str, default: float) -> float:
    try:
        v = float(os.environ.get(env) or default)
        return v if v > 0 else default
    except ValueError:
        return default


def render_timeout() -> float:
    """Seconds a whole render may take (SLIDE_LAB_RENDER_TIMEOUT, default 120)."""
    return _seconds("SLIDE_LAB_RENDER_TIMEOUT", 120.0)


def step_timeout() -> float:
    """Seconds one slow step may take (SLIDE_LAB_RENDER_STEP_TIMEOUT, default 30)."""
    return _seconds("SLIDE_LAB_RENDER_STEP_TIMEOUT", 30.0)


class _Deadline:
    def __init__(self, what: str, seconds: float, retry: str):
        self.what, self.seconds, self.retry = what, seconds, retry
        self.own: dict = {}                          # pid -> start time, recorded
        self._fired = threading.Lock()
        self.fired = threading.Event()               # set once the time limit is hit
        self._timer = threading.Timer(seconds, self._fire,
                                      args=(f"the whole render took over {int(seconds)} s",))
        self._timer.daemon = True

    def record_own(self) -> None:
        """Record the processes this run started (the driver, the browser and
        theirs). Only these are ever ended."""
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import _procs
            for r in _procs.descendants(os.getpid()):
                self.own.setdefault(r["pid"], r.get("started"))
            for f in list(_SCRATCH):
                try:
                    (f / "_slidelab_pids.txt").write_text(
                        "\n".join(f"{p} {s or ''}" for p, s in self.own.items()),
                        encoding="utf-8")
                except OSError:
                    pass
        except Exception:
            pass

    @contextlib.contextmanager
    def step(self, name: str, seconds: float | None = None):
        secs = seconds or step_timeout()
        t = threading.Timer(secs, self._fire, args=(f"{name} took over {int(secs)} s",))
        t.daemon = True
        t.start()
        try:
            yield
        finally:
            t.cancel()

    def _fire(self, reason: str) -> None:
        if not self._fired.acquire(blocking=False):
            return
        self.fired.set()          # the main thread now waits for this exit (below)
        folders = list(_SCRATCH)
        try:
            self.record_own()
            import _procs
            results = _procs.end(list(self.own.items()))
            time.sleep(0.5)
            for f in folders:
                for _ in range(5):
                    shutil.rmtree(f, ignore_errors=True)
                    if not f.exists():
                        break
                    time.sleep(0.5)
            ended = [str(p) for p, ok, why in results if ok and why == "ended"]
            stuck = [f"{p} ({why})" for p, ok, why in results if not ok]
        except Exception as exc:                    # never hang here either
            ended, stuck = [], [f"could not list its processes ({exc})"]
        here = os.path.dirname(os.path.abspath(__file__))
        lines = [
            f"ERROR: {self.what} timed out: {reason}.",
            "Slide Lab ended only the processes this run started"
            + (f" (PID {', '.join(ended)})" if ended else "")
            + " and deleted its scratch folder. Nothing else was touched.",
        ]
        if stuck:
            lines.append("Could not end: " + ", ".join(stuck) + ". Run doctor.py (below) and "
                         "show the user its list; end nothing without their yes.")
        lines += [
            "To allow more time, set SLIDE_LAB_RENDER_TIMEOUT (seconds, now "
            f"{int(render_timeout())}) before the command.",
            f"If it times out again, run: py -3 \"{os.path.join(here, 'doctor.py')}\"",
            f"Next: run the same command again ({self.retry}).",
        ]
        try:
            sys.stderr.write("\n".join(lines) + "\n")
            sys.stderr.flush()
            sys.stdout.flush()
        except Exception:
            pass
        os._exit(4)


def render_slot(what: str = "the render"):
    """One of the computer's render slots (slide-qc/scripts/render_slot.py),
    held for the with-block. Put it OUTSIDE render_deadline(), so time spent
    waiting for a slot does not count toward the time limit:

        with render_slot("render_html.py"), render_deadline("render_html.py"), \\
                scratch_env(), sync_playwright() as pw:
    """
    qc = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "slide-qc", "scripts")
    if qc not in sys.path:
        sys.path.append(qc)
    try:
        import render_slot as _rs
    except ImportError:                        # slide-qc not beside slide-builder
        return contextlib.nullcontext()
    return _rs.render_slot(what)


@contextlib.contextmanager
def render_deadline(what: str = "the render", seconds: float | None = None,
                    retry: str = "timed out, re-run"):
    """The time limit for one browser run. Put it OUTSIDE scratch_env():

        with render_deadline("render_html.py"), scratch_env(), sync_playwright() as pw:
    """
    dl = _Deadline(what, seconds or render_timeout(), retry)
    _DEADLINE.append(dl)
    dl._timer.start()
    try:
        yield dl
    finally:
        # Ending the browser makes the main thread's call fail at once; wait
        # here for the time-limit thread to finish its clean-up and exit 4,
        # instead of dying first with a traceback and no message.
        if dl.fired.is_set():
            time.sleep(60)
        dl._timer.cancel()
        if dl in _DEADLINE:
            _DEADLINE.remove(dl)


def step(name: str, seconds: float | None = None):
    """A per-step limit inside the render_deadline in force (none without one)."""
    return _DEADLINE[-1].step(name, seconds) if _DEADLINE else contextlib.nullcontext()


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
        try:                                   # each load, wait and screenshot: 30 s
            page.set_default_timeout(step_timeout() * 1000)
        except Exception:
            pass
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

    def close(self, *a, **kw):
        # Twice the step limit: on a busy computer (several builds at once)
        # closing alone took over 30 s while nothing was stuck (2026-10-13).
        with step("closing the browser", 2 * step_timeout()):
            return self._browser.close(*a, **kw)


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
    try:
        for name in order:
            channel = _CHANNELS[name]
            try:
                if channel:
                    b = pw.chromium.launch(channel=channel, args=args, **kwargs)
                else:
                    b = pw.chromium.launch(args=args, **kwargs)
            except Exception as exc:  # not installed / cannot start
                first_error = first_error or exc
                continue
            if _DEADLINE:
                _DEADLINE[-1].record_own()
            return _Browser(b, script)
    finally:
        _restore_cwd()                 # the browser is up: back to the caller's folder
    raise first_error
