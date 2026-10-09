#!/usr/bin/env python3
"""ppt_safe.py — render with PowerPoint without disturbing the user's PowerPoint.

Every Slide Lab path that draws slides with PowerPoint goes through here:
the fallback when LibreOffice is not installed, the converter's self-check,
and slide-qc's optional PowerPoint pass. The rules, in one place:

  - attach to PowerPoint (start it if it is not running); never a second copy
  - open OUR file read-only, without a window
  - export, then close only the presentation we opened
  - quit PowerPoint only if it was not running before we started AND nothing
    is open in it afterwards (no presentation, no window, not visible). If
    the user opens PowerPoint while a render runs, their PowerPoint is the
    one we started; it now holds their file, so it stays open.
  - never touch, save or close a presentation we did not open
  - one render at a time (a lock shared by every Slide Lab process), so two
    renders never drive PowerPoint at once. Renders are serial and slower
    than LibreOffice's.

Windows only (pywin32 + PowerPoint).
"""
from __future__ import annotations

import contextlib
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

PP_SAVE_AS_PDF = 32
LOCK_TIMEOUT_S = 900
_THREAD_LOCK = threading.Lock()


def powerpoint_running() -> bool:
    """True if a POWERPNT.EXE process is running (assume yes if unsure)."""
    try:
        out = subprocess.check_output(
            ["tasklist", "/FI", "IMAGENAME eq POWERPNT.EXE", "/FO", "CSV", "/NH"],
            stderr=subprocess.DEVNULL, text=True, timeout=20)
        return "POWERPNT.EXE" in out.upper()
    except Exception:
        return True


@contextlib.contextmanager
def _process_lock():
    """One PowerPoint render at a time across every Slide Lab process."""
    path = Path(tempfile.gettempdir()) / "slidelab_powerpoint_render.lock"
    fh = open(path, "a+b")
    got = False
    deadline = time.monotonic() + LOCK_TIMEOUT_S
    try:
        if sys.platform == "win32":
            import msvcrt
            while True:
                try:
                    fh.seek(0)
                    msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                    got = True
                    break
                except OSError:
                    if time.monotonic() > deadline:
                        raise TimeoutError("another PowerPoint render did not finish in time")
                    time.sleep(0.3)
        yield
    finally:
        if got and sys.platform == "win32":
            import msvcrt
            try:
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        fh.close()


def open_names(app) -> list[str]:
    """Names of the presentations open in PowerPoint (for checks and tests)."""
    try:
        return [app.Presentations(i + 1).FullName for i in range(app.Presentations.Count)]
    except Exception:
        return []


def _nothing_open(app) -> bool:
    try:
        if app.Presentations.Count:
            return False
        if app.Windows.Count:
            return False
        if bool(app.Visible):
            return False
        return True
    except Exception:
        return False          # can't tell: leave it running


@contextlib.contextmanager
def session():
    """A PowerPoint application to open our own files in, left as we found it.
    Yields (app, started_by_us)."""
    import pythoncom
    import win32com.client
    with _THREAD_LOCK, _process_lock():
        pythoncom.CoInitialize()
        was_running = powerpoint_running()
        app = None
        try:
            app = win32com.client.Dispatch("PowerPoint.Application")
            yield app, not was_running
        finally:
            if app is not None and not was_running:
                # Quit only what we started, and only if the user has not
                # opened anything in it meanwhile.
                try:
                    if _nothing_open(app):
                        app.Quit()
                except Exception:
                    pass
            app = None
            pythoncom.CoUninitialize()


@contextlib.contextmanager
def opened(app, pptx: Path):
    """Open pptx read-only without a window; close only that presentation."""
    pres = app.Presentations.Open(str(Path(pptx).resolve()), True, False, False)
    try:
        yield pres
    finally:
        try:
            pres.Close()
        except Exception:
            pass


def export_pngs(pptx: Path, out_dir: Path, width_px: int) -> int:
    """slide_01.png, slide_02.png ... in out_dir; returns the slide count."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.glob("slide_*.png"):
        p.unlink()
    height_px = int(width_px * 9 / 16)
    n = 0
    with session() as (app, _):
        with opened(app, pptx) as pres:
            for i in range(1, pres.Slides.Count + 1):
                pres.Slides(i).Export(str((out_dir / f"slide_{i:02d}.png").resolve()),
                                      "PNG", width_px, height_px)
                n = i
    return n


def export_pdfs(pptxs: list[Path]) -> None:
    """A PDF beside each PPTX (same name). A file PowerPoint refuses gets none."""
    if not pptxs:
        return
    with session() as (app, _):
        for p in pptxs:
            p = Path(p).resolve()
            try:
                with opened(app, p) as pres:
                    pres.SaveAs(str(p.with_suffix(".pdf")), PP_SAVE_AS_PDF)
            except Exception:
                pass


def export_pdf(pptx: Path, pdf: Path) -> bool:
    """One PDF at a chosen path; True when written."""
    pptx, pdf = Path(pptx).resolve(), Path(pdf).resolve()
    with session() as (app, _):
        try:
            with opened(app, pptx) as pres:
                pres.SaveAs(str(pdf), PP_SAVE_AS_PDF)
        except Exception:
            return False
    return pdf.exists()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: py -3 ppt_safe.py <deck.pptx> <out_dir>")
    n = export_pngs(Path(sys.argv[1]), Path(sys.argv[2]), 1920)
    print(f"Rendered {n} slides to {sys.argv[2]} (PowerPoint)")
