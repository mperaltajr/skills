#!/usr/bin/env python3
"""
render_slides.py — Render PPTX to per-slide PNGs (or a PDF) without disturbing
the user's PowerPoint.

Which program draws the slides (owner's decision, 2026-10-09):
  - Windows with PowerPoint installed: PowerPoint, the safe way (ppt_safe.py:
    our file is opened read-only without a window, only that file is closed,
    and PowerPoint is quit only if we started it and nothing else is open in
    it). LibreOffice is the backup.
  - Mac, Linux, or Windows without PowerPoint: LibreOffice headless.
  - slide-builder/settings.json "renderer" overrides it: "auto" (the rule
    above), "powerpoint" or "libreoffice". SLIDE_LAB_RENDERER overrides the
    file for one run.

When a render fails twice on one program, the other one takes over for that
render (when it is installed). The first time a command renders through
PowerPoint it prints one line telling the user PowerPoint may pause.

Test switches: SLIDE_LAB_NO_LIBREOFFICE=1 acts as if LibreOffice were not
installed; SLIDE_LAB_NO_POWERPOINT=1 acts as if PowerPoint were not.

Usage:
  py -3 render_slides.py <pptx> <out_dir>                    # the default program
  py -3 render_slides.py <pptx> <out_dir> --dpi 200
  py -3 render_slides.py <pptx> <out_dir> --engine libre     # LibreOffice first
  py -3 render_slides.py <pptx> <out_dir> --engine ppt       # PowerPoint first

Outputs: <out_dir>/slide_01.png, slide_02.png, ... (one per slide, hidden
slides included, so slide_NN is always the deck's slide NN)
"""
import argparse, json, os, pathlib, re, subprocess, sys, tempfile, shutil, threading, time
import zipfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

SETTINGS_JSON = pathlib.Path(__file__).resolve().parents[2] / "slide-builder" / "settings.json"
RENDERERS = ("auto", "powerpoint", "libreoffice")
NOTICE = ("Note: PowerPoint may pause for a few seconds while Slide Lab renders slides; "
          "editing in PowerPoint during that time slows the build.")
_NOTICE_ENV = "SLIDE_LAB_PPT_NOTICE_SHOWN"


def _off(var: str) -> bool:
    return os.environ.get(var, "").strip().lower() in ("1", "true", "yes")


def _resolve_soffice() -> str:
    """Locate the LibreOffice headless executable.

    Resolution order:
      1. SLIDE_LAB_SOFFICE env var (explicit override)
      2. shutil.which("soffice") (PATH lookup; works on macOS/Linux/most Windows)
      3. Common Windows default install location
      4. Common macOS default install location

    Raises RuntimeError if nothing resolves, or when SLIDE_LAB_NO_LIBREOFFICE=1
    (act as if it were not installed).
    """
    if _off("SLIDE_LAB_NO_LIBREOFFICE"):
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


SOFFICE = None  # resolved lazily on first LibreOffice render

# pypdfium2 is NOT thread-safe; concurrent calls produce C++ exception
# 0xe06d7363 (the Windows MSVC _CXXTHROW marker). When this module is
# imported by ThreadPoolExecutor workers, serialize the PDF→PNG section
# behind this lock. The LibreOffice subprocess section runs in parallel
# fine because each call spawns its own process.
_PDFIUM_LOCK = threading.Lock()


# ---------------------------------------------------------------------------
# Which program renders
# ---------------------------------------------------------------------------
def libreoffice_available() -> bool:
    try:
        _resolve_soffice()
        return True
    except Exception:
        return False


def powerpoint_available() -> bool:
    """True on Windows when PowerPoint can be driven (pywin32 + PowerPoint)."""
    if sys.platform != "win32" or _off("SLIDE_LAB_NO_POWERPOINT"):
        return False
    try:
        import winreg
        winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"PowerPoint.Application"))
        import win32com.client  # noqa: F401
        return True
    except Exception:
        return False


def renderer_setting() -> str:
    """auto | powerpoint | libreoffice, from SLIDE_LAB_RENDERER, else
    slide-builder/settings.json "renderer", else auto."""
    val = os.environ.get("SLIDE_LAB_RENDERER", "").strip().lower()
    if not val:
        try:
            val = str(json.loads(SETTINGS_JSON.read_text(encoding="utf-8"))
                      .get("renderer", "auto")).strip().lower()
        except Exception:
            val = "auto"
    val = {"ppt": "powerpoint", "libre": "libreoffice", "lo": "libreoffice"}.get(val, val)
    return val if val in RENDERERS else "auto"


def pick_renderer(requested: str | None = None) -> str:
    """"powerpoint" or "libreoffice": the program a render starts with.

    requested None/"auto" = the setting; the setting's auto = PowerPoint on
    Windows when it is installed, else LibreOffice. A requested program that
    is not installed gives way to the other one when that one is."""
    req = (requested or "auto").strip().lower()
    req = {"ppt": "powerpoint", "libre": "libreoffice", "lo": "libreoffice"}.get(req, req)
    if req not in RENDERERS or req == "auto":
        req = renderer_setting()
    if req == "auto":
        req = "powerpoint" if powerpoint_available() else "libreoffice"
    if req == "powerpoint" and not powerpoint_available():
        return "libreoffice"
    if req == "libreoffice" and not libreoffice_available() and powerpoint_available():
        return "powerpoint"
    return req


def _other(engine: str) -> str:
    return "libreoffice" if engine == "powerpoint" else "powerpoint"


def _available(engine: str) -> bool:
    return powerpoint_available() if engine == "powerpoint" else libreoffice_available()


def _label(engine: str) -> str:
    return "PowerPoint" if engine == "powerpoint" else "LibreOffice"


def powerpoint_notice() -> None:
    """Tell the user, once per command, that PowerPoint may pause. Child
    processes of the command inherit the flag and stay quiet."""
    if os.environ.get(_NOTICE_ENV):
        return
    os.environ[_NOTICE_ENV] = "1"
    print(NOTICE, file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
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


def _pdfium():
    try:
        import pypdfium2 as pdfium
    except ImportError:
        print("Installing pypdfium2 once …", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "pip", "install",
                               "--quiet", "pypdfium2"])
        import pypdfium2 as pdfium
    return pdfium


_HIDDEN = re.compile(rb'(<p:sld\b[^>]*?)\s+show="(?:0|false)"')


def slide_count(pptx: pathlib.Path) -> int:
    """Slides listed in the deck (from presentation.xml, no python-pptx)."""
    with zipfile.ZipFile(pptx) as z:
        xml = z.read("ppt/presentation.xml")
    return len(re.findall(rb"<p:sldId\b", xml))


def slide_width_in(pptx: pathlib.Path) -> float:
    try:
        with zipfile.ZipFile(pptx) as z:
            m = re.search(rb'<p:sldSz\b[^>]*\bcx="(\d+)"', z.read("ppt/presentation.xml"))
        return int(m.group(1)) / 914400 if m else 13.333
    except Exception:
        return 13.333


def _shown_copy(pptx: pathlib.Path, td: pathlib.Path) -> pathlib.Path:
    """pptx itself, or a copy in td with every hidden slide shown.

    A PDF leaves hidden slides out, which shifted every later page onto the
    wrong slide: slide_05.png showed slide 6. Rendering them keeps slide_NN
    the deck's slide NN (hidden slides are reported by the hygiene pass)."""
    with zipfile.ZipFile(pptx) as z:
        names = [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
        if not any(_HIDDEN.search(z.read(n)[:2000]) for n in names):
            return pptx
        dst = td / f"shown_{pptx.name}"
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as out:
            for info in z.infolist():
                data = z.read(info.filename)
                if info.filename in names:
                    data = _HIDDEN.sub(rb"\1", data, count=1)
                out.writestr(info, data)
    return dst


# ---------------------------------------------------------------------------
# LibreOffice
# ---------------------------------------------------------------------------
def _convert_to_pdf(pptx: pathlib.Path, td_p: pathlib.Path) -> pathlib.Path:
    """PPTX -> PDF in td_p with LibreOffice, retried once.

    A render fails now and then (non-zero exit or no PDF), and a second try
    usually works (2026-10-08 reports). Each try gets its own fresh LibreOffice
    profile; a file under a OneDrive folder is rendered from a local copy (the
    second try always uses one). Renders are NOT made to wait for each other:
    many run in parallel fine. When both tries fail, the error carries the
    full output of both, so the cause is not lost."""
    global SOFFICE
    if SOFFICE is None:
        SOFFICE = _resolve_soffice()
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


def _pdf_to_pngs(pdf_path: pathlib.Path, out_dir: pathlib.Path, dpi: int,
                 quiet: bool = False) -> int:
    pdfium = _pdfium()
    with _PDFIUM_LOCK:
        pdf = pdfium.PdfDocument(str(pdf_path))
        scale = dpi / 72.0
        try:
            n = len(pdf)
            for i, page in enumerate(pdf, start=1):
                pil = page.render(scale=scale).to_pil()
                out = out_dir / f"slide_{i:02d}.png"
                pil.save(out)
                if not quiet:
                    print(f"  {out.name}")
        finally:
            pdf.close()
    return n


def _libre_pngs(pptx: pathlib.Path, out_dir: pathlib.Path, dpi: int, quiet: bool = False) -> int:
    with tempfile.TemporaryDirectory() as td:
        td_p = pathlib.Path(td)
        pdf_path = _convert_to_pdf(_shown_copy(pptx, td_p), td_p)
        return _pdf_to_pngs(pdf_path, out_dir, dpi, quiet)


# ---------------------------------------------------------------------------
# PowerPoint (ppt_safe: read-only, no window, never the user's decks)
# ---------------------------------------------------------------------------
def _twice(what: str, fn):
    """fn() tried twice; RuntimeError with both errors when both fail."""
    errs = []
    for attempt in (1, 2):
        try:
            got = fn()
            if attempt == 2:
                print(f"  (PowerPoint {what} worked on the second try)", file=sys.stderr)
            return got
        except Exception as exc:  # noqa: BLE001
            try:
                from ppt_safe import _com_message
                msg = _com_message(exc)
            except Exception:
                msg = f"{type(exc).__name__}: {exc}"
            errs.append(f"try {attempt}: {msg}")
            if attempt == 1:
                time.sleep(1.0)
    raise RuntimeError(f"PowerPoint could not {what} (tried twice).\n" + "\n".join(errs))


def _ppt_pngs(pptx: pathlib.Path, out_dir: pathlib.Path, width_px: int) -> int:
    import ppt_safe
    powerpoint_notice()
    n = _twice(f"render {pptx.name}",
               lambda: ppt_safe.export_pngs(pathlib.Path(pptx), pathlib.Path(out_dir), width_px))
    if n <= 0:
        raise RuntimeError(f"PowerPoint rendered no slides of {pptx.name}")
    return n


def _ppt_pdf(pptx: pathlib.Path, td_p: pathlib.Path) -> pathlib.Path:
    import ppt_safe
    powerpoint_notice()
    src = _shown_copy(pptx, td_p)
    pdf = td_p / (pptx.stem + ".ppt.pdf")

    def go():
        if not ppt_safe.export_pdf(src, pdf):
            raise RuntimeError("PowerPoint wrote no PDF")
        return pdf
    return _twice(f"render {pptx.name}", go)


# ---------------------------------------------------------------------------
# Public: render with the default program, the other one as backup
# ---------------------------------------------------------------------------
def _with_backup(first: str, run):
    """run(engine) with `first`; when it fails (twice, inside run) and the
    other program is installed, the other one takes over. Returns
    (result, engine used)."""
    errors = []
    for eng in (first, _other(first)):
        if eng != first and not _available(eng):
            break
        if eng != first:
            print(f"  {_label(first)} could not render this twice; "
                  f"{_label(eng)} takes over for this render.", file=sys.stderr)
        try:
            return run(eng), eng
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{_label(eng)}: {exc}")
    raise RuntimeError("\n".join(errors))


def render(pptx: pathlib.Path, out_dir: pathlib.Path, dpi: int = 150,
           renderer: str | None = None, quiet: bool = False) -> str:
    """slide_NN.png per slide in out_dir with the default program (see the
    top of this file), the other one taking over if it fails twice.
    renderer: None/"auto", "powerpoint" or "libreoffice" (the one to start
    with). Returns the program that drew it."""
    pptx, out_dir = pathlib.Path(pptx).absolute(), pathlib.Path(out_dir).absolute()
    out_dir.mkdir(parents=True, exist_ok=True)

    def run(eng):
        # Wipe stale slide_*.png so old files don't linger if the deck shrank
        for p in out_dir.glob("slide_*.png"):
            p.unlink()
        if eng == "powerpoint":
            return _ppt_pngs(pptx, out_dir, int(round(dpi * slide_width_in(pptx))))
        return _libre_pngs(pptx, out_dir, dpi, quiet)

    first = pick_renderer(renderer)
    if first == "libreoffice" and not libreoffice_available() and not powerpoint_available():
        _resolve_soffice()          # raises with the install hint
    n, eng = _with_backup(first, run)
    if not quiet:
        print(f"\nRendered {n} slides to {out_dir} ({_label(eng)}, {dpi} dpi)")
    return eng


def to_pdf(pptx: pathlib.Path, workdir: pathlib.Path,
           renderer: str | None = None) -> tuple[pathlib.Path, str]:
    """A PDF of pptx (one page per slide, hidden slides included) inside
    workdir, with the default program and the other one as backup.
    Returns (pdf path, program used)."""
    pptx, workdir = pathlib.Path(pptx).absolute(), pathlib.Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    k = [0]

    def run(eng):
        k[0] += 1
        td = workdir / f"r{k[0]}_{eng}"
        td.mkdir(parents=True, exist_ok=True)
        if eng == "powerpoint":
            return _ppt_pdf(pptx, td)
        return _convert_to_pdf(_shown_copy(pptx, td), td)

    first = pick_renderer(renderer)
    if first == "libreoffice" and not libreoffice_available() and not powerpoint_available():
        _resolve_soffice()
    return _with_backup(first, run)


def render_libre(pptx: pathlib.Path, out_dir: pathlib.Path, dpi: int):
    """LibreOffice first (PowerPoint takes over when LibreOffice is missing or
    fails twice). Most callers want render(), the default program."""
    return render(pptx, out_dir, dpi, renderer="libreoffice")


def render_ppt_fallback(pptx: pathlib.Path, out_dir: pathlib.Path, width_px: int):
    """Kept for older callers: PowerPoint first."""
    return render_ppt_com(pptx, out_dir, width_px)


def render_ppt_com(pptx: pathlib.Path, out_dir: pathlib.Path, width_px: int):
    """PowerPoint first, safe while the user has PowerPoint open (ppt_safe.py:
    read-only, no window, closes only this deck, quits only a PowerPoint it
    started with nothing else open in it)."""
    dpi = max(1, int(round(width_px / slide_width_in(pathlib.Path(pptx)))))
    return render(pptx, out_dir, dpi, renderer="powerpoint")


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx", type=pathlib.Path)
    ap.add_argument("out_dir", type=pathlib.Path)
    ap.add_argument("--engine", default="auto",
        choices=["auto", "ppt", "powerpoint", "libre", "libreoffice"],
        help="auto (default: PowerPoint on Windows when installed, else LibreOffice; "
             "slide-builder/settings.json 'renderer' overrides), ppt or libre "
             "(the program to start with; the other takes over if it fails twice)")
    ap.add_argument("--dpi",   type=int, default=150,
        help="render DPI (default 150 ≈ 2000px wide; 200 ≈ 2700px)")
    ap.add_argument("--width", type=int, default=None,
        help="width in pixels (overrides --dpi)")
    args = ap.parse_args()

    pptx = args.pptx.resolve()
    if not pptx.exists():
        sys.exit(f"PPTX not found: {pptx}")
    dpi = args.dpi
    if args.width:
        dpi = max(1, int(round(args.width / slide_width_in(pptx))))
    render(pptx, args.out_dir.resolve(), dpi, renderer=args.engine)


if __name__ == "__main__":
    main()
