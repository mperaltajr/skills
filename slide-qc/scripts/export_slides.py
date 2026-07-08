#!/usr/bin/env python3
"""Export PPTX slides to PNG using PowerPoint COM (Windows + Office required).

Usage:
    py -3 export_slides.py <path/to/deck.pptx> [--out <output_dir>] [--width 1280]

Output:
    slide_01.png, slide_02.png, ... in <output_dir> (default: <pptx_dir>/_qc/)
    Prints one line per slide on success. Exits 1 on failure.
"""

import sys
import pathlib
import argparse
import subprocess
import time


def _wait_for_powerpoint_exit(timeout_s: int = 15) -> None:
    """Poll until POWERPNT.EXE is no longer in the process list.

    app.Quit() is asynchronous — it signals PowerPoint to quit but returns
    before the process actually exits. If the next export_slides.py run starts
    while POWERPNT.EXE is still alive mid-shutdown, COM throws
    CO_E_SERVER_EXEC_FAILURE (-2146959355). Polling here ensures the process
    is fully gone before this script returns control to the caller.

    Does NOT kill PowerPoint — only waits. User's open files are not touched.
    """
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq POWERPNT.EXE', '/NH'],
            capture_output=True, text=True
        )
        if 'POWERPNT.EXE' not in result.stdout:
            return
        time.sleep(0.5)
    # Timed out — process didn't exit cleanly. Not fatal for this run,
    # but the next run may still fail. Log a warning.
    print("WARNING: POWERPNT.EXE still running after quit — next export may fail.", file=sys.stderr)


def export_via_powerpoint(pptx_path: pathlib.Path, out_dir: pathlib.Path, width: int = 1920):
    try:
        import win32com.client
    except ImportError:
        print("ERROR: pywin32 not installed.", file=sys.stderr)
        print("  Run: pip install pywin32", file=sys.stderr)
        sys.exit(1)

    height = int(width * 9 / 16)
    out_dir.mkdir(parents=True, exist_ok=True)

    app = None
    prs = None
    try:
        app = win32com.client.DispatchEx("PowerPoint.Application")
        app.Visible = True
        prs = app.Presentations.Open(
            str(pptx_path.resolve()),
            ReadOnly=True,
            Untitled=False,
            WithWindow=False,
        )
        count = prs.Slides.Count
        for i in range(1, count + 1):
            out_path = out_dir / f"slide_{i:02d}.png"
            prs.Slides(i).Export(str(out_path.resolve()), "PNG", width, height)
            print(f"  slide {i:02d}/{count}: {out_path}")
        print(f"OK {count} slides -> {out_dir}")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        if prs is not None:
            try:
                prs.Close()
            except Exception:
                pass
        if app is not None:
            try:
                app.Quit()
            except Exception:
                pass
        # Wait for the process to fully exit before returning.
        # This prevents CO_E_SERVER_EXEC_FAILURE on the next export run.
        _wait_for_powerpoint_exit()


def main():
    parser = argparse.ArgumentParser(description="Export PPTX slides to PNG via PowerPoint COM")
    parser.add_argument("pptx", help="Path to the .pptx file")
    parser.add_argument("--out", default=None, help="Output directory (default: <pptx_dir>/_qc/)")
    # Default 1920 (1.5× 1280) so small text — chart annotations, footnotes,
    # numerals — is legible at thumbnail zoom. At 1280 a 9pt footnote was ~6px
    # tall and Claude could not reliably read it; that gap was the review failure
    # mode documented in slide-qc/SKILL.md. Do not lower.
    parser.add_argument("--width", type=int, default=1920, help="Export width in pixels (default: 1920)")
    args = parser.parse_args()

    pptx_path = pathlib.Path(args.pptx).resolve()
    if not pptx_path.exists():
        print(f"ERROR: file not found: {pptx_path}", file=sys.stderr)
        sys.exit(1)
    if pptx_path.suffix.lower() != ".pptx":
        print(f"ERROR: expected a .pptx file, got: {pptx_path.suffix}", file=sys.stderr)
        sys.exit(1)

    out_dir = pathlib.Path(args.out).resolve() if args.out else pptx_path.parent / "_qc"
    export_via_powerpoint(pptx_path, out_dir, args.width)


if __name__ == "__main__":
    main()
