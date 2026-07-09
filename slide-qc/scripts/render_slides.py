#!/usr/bin/env python3
"""
render_silent.py — Render PPTX to per-slide PNGs WITHOUT touching the user's
PowerPoint instance.

Default engine = LibreOffice headless (always safe; spawns its own process,
never sees PowerPoint).  Use --engine=ppt only when pixel-perfect font
fidelity is required AND PowerPoint isn't already open with other files.

Usage:
  py -3 render_silent.py <pptx> <out_dir>
  py -3 render_silent.py <pptx> <out_dir> --dpi 200
  py -3 render_silent.py <pptx> <out_dir> --engine ppt          # uses COM (will refuse if PPT is already running)

Outputs: <out_dir>/slide_01.png, slide_02.png, …
"""
import argparse, os, pathlib, subprocess, sys, tempfile, shutil, threading, time


def _resolve_soffice() -> str:
    """Locate the LibreOffice headless executable.

    Resolution order:
      1. SLIDE_LAB_SOFFICE env var (explicit override)
      2. shutil.which("soffice") (PATH lookup; works on macOS/Linux/most Windows)
      3. Common Windows default install location
      4. Common macOS default install location

    Raises RuntimeError on the FIRST call that needs soffice if nothing resolves.
    """
    env = os.environ.get("SLIDE_LAB_SOFFICE")
    if env and pathlib.Path(env).exists():
        return env
    # `soffice` is the canonical binary on every OS; `libreoffice` is the
    # command name many Linux distros ship (a wrapper/symlink).
    on_path = (
        shutil.which("soffice") or shutil.which("soffice.exe")
        or shutil.which("libreoffice") or shutil.which("libreoffice.exe")
    )
    if on_path:
        return on_path
    candidates = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/soffice",
        "/usr/local/bin/soffice",
        "/opt/libreoffice/program/soffice",
    ]
    for c in candidates:
        if pathlib.Path(c).exists():
            return c
    raise RuntimeError(
        "LibreOffice (soffice) not found. Install LibreOffice and either:\n"
        "  - add its `program/` directory to PATH, OR\n"
        "  - set SLIDE_LAB_SOFFICE to the full soffice.exe path."
    )


SOFFICE = None  # resolved lazily on first render_libre call

# pypdfium2 is NOT thread-safe; concurrent calls produce C++ exception
# 0xe06d7363 (the Windows MSVC _CXXTHROW marker). When this module is
# imported by ThreadPoolExecutor workers, serialize the PDF→PNG section
# behind this lock. The LibreOffice subprocess section runs in parallel
# fine because each call spawns its own process.
_PDFIUM_LOCK = threading.Lock()


# ---------------------------------------------------------------------------
# LibreOffice path (silent, default)
# ---------------------------------------------------------------------------
def render_libre(pptx: pathlib.Path, out_dir: pathlib.Path, dpi: int):
    global SOFFICE
    if SOFFICE is None:
        SOFFICE = _resolve_soffice()
    out_dir.mkdir(parents=True, exist_ok=True)
    # Wipe stale slide_*.png so old files don't linger if the deck shrank
    for p in out_dir.glob("slide_*.png"):
        p.unlink()

    with tempfile.TemporaryDirectory() as td:
        td_p = pathlib.Path(td)
        # PPTX → PDF, isolated user profile so we don't fight a running LO
        user_profile = td_p / "lo_profile"
        cmd = [
            SOFFICE,
            f"-env:UserInstallation=file:///{user_profile.as_posix()}",
            "--headless", "--norestore", "--nologo", "--nodefault", "--nofirststartwizard",
            "--convert-to", "pdf", "--outdir", str(td_p), str(pptx),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            raise RuntimeError(
                f"soffice failed (rc={result.returncode})\n"
                f"stdout={result.stdout!r}\nstderr={result.stderr!r}")
        pdf_path = td_p / (pptx.stem + ".pdf")
        if not pdf_path.exists():
            raise RuntimeError(f"PDF not produced. td contents: {list(td_p.iterdir())}")

        # PDF → PNG via pypdfium2 (pure-python, no system deps).
        # pypdfium2 is NOT thread-safe — serialize via _PDFIUM_LOCK so
        # ThreadPoolExecutor callers don't crash with 0xe06d7363.
        try:
            import pypdfium2 as pdfium
        except ImportError:
            print("Installing pypdfium2 once …", file=sys.stderr)
            subprocess.check_call([sys.executable, "-m", "pip", "install",
                                   "--quiet", "pypdfium2"])
            import pypdfium2 as pdfium
        with _PDFIUM_LOCK:
            pdf = pdfium.PdfDocument(str(pdf_path))
            scale = dpi / 72.0
            try:
                n = len(pdf)
                for i, page in enumerate(pdf, start=1):
                    bitmap = page.render(scale=scale)
                    pil = bitmap.to_pil()
                    out = out_dir / f"slide_{i:02d}.png"
                    pil.save(out)
                    print(f"  {out.name}")
            finally:
                pdf.close()
    print(f"\nRendered {n} slides to {out_dir} (LibreOffice engine, {dpi} dpi)")


# ---------------------------------------------------------------------------
# PowerPoint COM path (high-fidelity, opt-in)
# ---------------------------------------------------------------------------
def _powerpoint_already_running() -> bool:
    """Return True if any POWERPNT.EXE process is currently running."""
    try:
        out = subprocess.check_output(
            ["tasklist", "/FI", "IMAGENAME eq POWERPNT.EXE", "/FO", "CSV"],
            stderr=subprocess.DEVNULL, text=True)
        return "POWERPNT.EXE" in out
    except Exception:
        # If we can't check, assume yes — fail safe.
        return True


def render_ppt_com(pptx: pathlib.Path, out_dir: pathlib.Path, width_px: int):
    """Pixel-perfect via PowerPoint COM. Refuses if PowerPoint is already running."""
    if _powerpoint_already_running():
        raise RuntimeError(
            "PowerPoint is already running — refusing to launch a COM instance "
            "because it would interfere with your open decks.\n"
            "Close PowerPoint and retry, or use the default LibreOffice engine "
            "(drop --engine ppt).")
    import win32com.client
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.glob("slide_*.png"):
        p.unlink()
    height_px = int(width_px * 9 / 16)
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    try:
        pres = powerpoint.Presentations.Open(str(pptx), WithWindow=False)
        try:
            for i, slide in enumerate(pres.Slides, start=1):
                png = out_dir / f"slide_{i:02d}.png"
                slide.Export(str(png), "PNG", width_px, height_px)
                print(f"  {png.name}")
        finally:
            pres.Close()
    finally:
        powerpoint.Quit()
    print(f"\nRendered {i} slides to {out_dir} (PowerPoint COM, {width_px}px)")


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx", type=pathlib.Path)
    ap.add_argument("out_dir", type=pathlib.Path)
    ap.add_argument("--engine", choices=["libre", "ppt"], default="libre",
        help="libre (default; silent, never touches PowerPoint) or ppt (pixel-perfect COM, refuses if PowerPoint already running)")
    ap.add_argument("--dpi",   type=int, default=150,
        help="LibreOffice render DPI (default 150 ≈ 1700px wide; 200 ≈ 2300px)")
    ap.add_argument("--width", type=int, default=1920,
        help="PowerPoint COM export width in pixels (default 1920)")
    args = ap.parse_args()

    pptx = args.pptx.resolve()
    if not pptx.exists():
        sys.exit(f"PPTX not found: {pptx}")

    if args.engine == "libre":
        render_libre(pptx, args.out_dir.resolve(), args.dpi)
    else:
        render_ppt_com(pptx, args.out_dir.resolve(), args.width)


if __name__ == "__main__":
    main()
