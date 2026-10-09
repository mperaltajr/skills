#!/usr/bin/env python3
"""
render_slides.py — Render PPTX to per-slide PNGs without disturbing the user's
PowerPoint.

Default engine = LibreOffice headless (spawns its own process, never sees
PowerPoint). When LibreOffice is not installed (Windows), PowerPoint draws
the slides instead, the safe way (ppt_safe.py): our file is opened read-only
without a window, only that file is closed, and PowerPoint is quit only if
we started it and nothing else is open in it. --engine ppt uses that same
safe path on purpose (PowerPoint's own fonts and layout), also while the
user has PowerPoint open.

Set SLIDE_LAB_NO_LIBREOFFICE=1 to act as if LibreOffice were not installed
(tests, or a broken LibreOffice).

Usage:
  py -3 render_slides.py <pptx> <out_dir>
  py -3 render_slides.py <pptx> <out_dir> --dpi 200
  py -3 render_slides.py <pptx> <out_dir> --engine ppt          # PowerPoint, safe with PowerPoint open

Outputs: <out_dir>/slide_01.png, slide_02.png, …
"""
import argparse, os, pathlib, subprocess, sys, tempfile, shutil, threading, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))


def _resolve_soffice() -> str:
    """Locate the LibreOffice headless executable.

    Resolution order:
      1. SLIDE_LAB_SOFFICE env var (explicit override)
      2. shutil.which("soffice") (PATH lookup; works on macOS/Linux/most Windows)
      3. Common Windows default install location
      4. Common macOS default install location

    Raises RuntimeError on the FIRST call that needs soffice if nothing resolves,
    or when SLIDE_LAB_NO_LIBREOFFICE=1 (act as if it were not installed).
    """
    if os.environ.get("SLIDE_LAB_NO_LIBREOFFICE", "").strip() in ("1", "true", "yes"):
        raise RuntimeError("LibreOffice turned off (SLIDE_LAB_NO_LIBREOFFICE=1).")
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
def powerpoint_available() -> bool:
    """True on Windows when PowerPoint can be driven (pywin32 + PowerPoint)."""
    if sys.platform != "win32":
        return False
    try:
        import winreg
        winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"PowerPoint.Application"))
        import win32com.client  # noqa: F401
        return True
    except Exception:
        return False


def render_ppt_fallback(pptx: pathlib.Path, out_dir: pathlib.Path, width_px: int):
    """Draw slides with PowerPoint when LibreOffice is not installed.

    Safe while the user has PowerPoint open (ppt_safe.py): the deck is opened
    read-only without a window, only that deck is closed, and PowerPoint is
    quit only if it was not running before AND nothing is open in it after
    (the user may open PowerPoint while a render runs). Renders are serial.
    Same slide_NN.png names as render_libre, so every caller works unchanged.
    """
    import ppt_safe
    n = ppt_safe.export_pngs(pathlib.Path(pptx), pathlib.Path(out_dir), width_px)
    print(f"Rendered {n} slides to {out_dir} (PowerPoint, because LibreOffice is not installed)")


def _run_soffice(cmd: list) -> subprocess.CompletedProcess:
    """One LibreOffice call (a seam the render-retry test replaces)."""
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180)


def _is_synced_path(p: pathlib.Path) -> bool:
    """True for a file under a OneDrive (cloud-synced) folder: the sync client
    can hold the file while LibreOffice opens it."""
    return any("onedrive" in part.lower() for part in pathlib.Path(p).resolve().parts)


def _pdf_pages(pdf: pathlib.Path) -> int:
    try:
        import pypdfium2 as pdfium
        with _PDFIUM_LOCK:
            doc = pdfium.PdfDocument(str(pdf))
            try:
                return len(doc)
            finally:
                doc.close()
    except Exception:
        return 0


def _convert_to_pdf(pptx: pathlib.Path, td_p: pathlib.Path) -> pathlib.Path:
    """PPTX -> PDF in td_p, retried once.

    A render fails now and then (non-zero exit or no PDF), and a second try
    usually works (2026-10-08 reports). Each try gets its own fresh LibreOffice
    profile; a file under a OneDrive folder is rendered from a local copy (the
    second try always uses one). Renders are NOT made to wait for each other:
    many run in parallel fine. When both tries fail, the error carries the
    full output of both, so the cause is not lost."""
    attempts = []
    for attempt in (1, 2):
        run_dir = td_p / f"try{attempt}"
        run_dir.mkdir(parents=True, exist_ok=True)
        src = pptx
        if attempt == 2 or _is_synced_path(pptx):
            (run_dir / "in").mkdir(exist_ok=True)
            src = run_dir / "in" / pptx.name
            shutil.copyfile(pptx, src)
        user_profile = run_dir / "lo_profile"
        cmd = [
            SOFFICE,
            f"-env:UserInstallation=file:///{user_profile.as_posix()}",
            "--headless", "--norestore", "--nologo", "--nodefault", "--nofirststartwizard",
            "--convert-to", "pdf", "--outdir", str(run_dir), str(src),
        ]
        try:
            result = _run_soffice(cmd)
            rc, out, err = result.returncode, result.stdout or "", result.stderr or ""
        except subprocess.TimeoutExpired as exc:
            rc, out, err = "timeout", str(exc.stdout or ""), str(exc.stderr or "")
        pdf_path = run_dir / (src.stem + ".pdf")
        if pdf_path.exists() and (rc == 0 or _pdf_pages(pdf_path) > 0):
            if attempt == 2:
                print(f"  (LibreOffice render of {pptx.name} worked on the second try)",
                      file=sys.stderr)
            return pdf_path
        attempts.append(
            f"try {attempt}{' (from a local copy)' if src != pptx else ''}: "
            f"exit code {rc}; PDF {'written' if pdf_path.exists() else 'not written'}\n"
            f"  stdout: {out.strip() or '(empty)'}\n  stderr: {err.strip() or '(empty)'}")
        if attempt == 1:
            time.sleep(1.0)
    raise RuntimeError(
        f"LibreOffice could not render {pptx.name} (tried twice, each with a fresh "
        f"profile, the second time from a local copy).\n" + "\n".join(attempts))


def render_libre(pptx: pathlib.Path, out_dir: pathlib.Path, dpi: int):
    global SOFFICE
    if SOFFICE is None:
        try:
            SOFFICE = _resolve_soffice()
        except RuntimeError:
            if powerpoint_available():
                return render_ppt_fallback(pptx, out_dir, int(round(dpi * 13.333)))
            raise
    out_dir.mkdir(parents=True, exist_ok=True)
    # Wipe stale slide_*.png so old files don't linger if the deck shrank
    for p in out_dir.glob("slide_*.png"):
        p.unlink()

    with tempfile.TemporaryDirectory() as td:
        td_p = pathlib.Path(td)
        # PPTX → PDF, isolated user profile so we don't fight a running LO;
        # retried once on failure (see _convert_to_pdf).
        pdf_path = _convert_to_pdf(pathlib.Path(pptx), td_p)

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
    """Pixel-perfect via PowerPoint itself, safe while the user has PowerPoint
    open (ppt_safe.py: read-only, no window, closes only this deck, quits
    only a PowerPoint it started and nothing else is open in)."""
    import ppt_safe
    n = ppt_safe.export_pngs(pathlib.Path(pptx), pathlib.Path(out_dir), width_px)
    for i in range(1, n + 1):
        print(f"  slide_{i:02d}.png")
    print(f"\nRendered {n} slides to {out_dir} (PowerPoint, {width_px}px)")


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx", type=pathlib.Path)
    ap.add_argument("out_dir", type=pathlib.Path)
    ap.add_argument("--engine", choices=["libre", "ppt"], default="libre",
        help="libre (default; never touches PowerPoint; falls back to PowerPoint when LibreOffice "
             "is not installed) or ppt (PowerPoint itself, safe with PowerPoint open)")
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
