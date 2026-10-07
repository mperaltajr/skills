#!/usr/bin/env python3
"""source_ledger.py — reconcile the figures on a SUPPLIED page before it ships.

The problem this solves. When a user hands over a page to be reproduced (a
one-pager, a mockup), replicating it faithfully also replicates its numbers. In
a real build that shipped "$300B / 6-12 months / 3x" when the brief already
carried the verified "~$450B / sold out / ~4x". So the fix for "you dropped my
page" silently becomes "you shipped my stale numbers".

Why this is a LEDGER and not a differ. A differ would compare each figure on the
page against the brief and pass or fail. It cannot: the brief has no typed
numeric field, only prose, so deciding that "6-12 months" and "sold out" denote
the same quantity is a semantic judgment the machine does not own. A differ that
reported "0 conflicts" would be asserting exactly that judgment, and the rest of
the pipeline would consume it as a recorded fact. That is false assurance, which
is a worse failure than the one we started with.

So the machine records only what it genuinely knows: *this figure-bearing slot
has not been resolved by a human*. Each slot takes exactly one of:

    bind_from_brief   the value comes from the brief, not the source page
    keep_source       the human states this source value is still correct
    replace_with      the human supplies a value

`null` is not a resolution. Unresolved slots block the compile.

Only figure-bearing slots are listed. A dense one-pager has 30-40 text surfaces;
prompting on all of them produces a bulk-accept reflex, which is how always-on
signals went blind in this pipeline before.

Run:
  py -3 scripts/source_ledger.py build  --out <out> --deck <page.pptx> --slide N
  py -3 scripts/source_ledger.py build  --out <out> --deck <page.pdf|page.png> --slide N
      (a PDF page with a text layer: each line that carries a figure is a row
       to resolve, as for a PowerPoint page; pictures on it go to the vision
       pass. A scanned PDF page or a picture has nothing to read: no rows, the
       whole page is recorded as checked by eye only, and the vision pass
       covers it)
  py -3 scripts/source_ledger.py status --out <out>
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _extract  # noqa: E402
import _paths as _p  # noqa: E402
import _state  # noqa: E402

from pptx import Presentation  # noqa: E402

LEDGER_NAME = "source_ledger.json"
RESOLUTIONS = ("bind_from_brief", "keep_source", "replace_with")
# A supplied page with no shape tree: recorded as checked by eye only.
VISUAL_SUFFIXES = frozenset({".pdf", ".png", ".jpg", ".jpeg", ".gif", ".bmp",
                             ".tif", ".tiff", ".webp"})


def ledger_path(out_dir: Path) -> Path:
    return Path(out_dir) / LEDGER_NAME


def _load(out_dir: Path) -> dict:
    p = ledger_path(out_dir)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def tally(ledger: dict) -> tuple[int, int, int]:
    """Return (unresolved, keep_source, total) over the ledger's rows."""
    rows = ledger.get("rows", []) or []
    unresolved = sum(1 for r in rows if r.get("resolution") not in RESOLUTIONS)
    # replace_with without a replacement is not resolved either.
    unresolved += sum(1 for r in rows
                      if r.get("resolution") == "replace_with"
                      and not str(r.get("replacement") or "").strip())
    keeps = sum(1 for r in rows if r.get("resolution") == "keep_source")
    return unresolved, keeps, len(rows)


def _write_brief_qc(out_dir: Path, ledger: dict) -> None:
    """Render the ledger into the brief_qc.json shape REVIEW.html already reads.

    build_review has rendered this banner for a long time with no writer (the
    path is an accepted orphan in the manifest). This is that writer.
    """
    unresolved, keeps, total = tally(ledger)
    unreachable = ledger.get("unreachable", []) or []
    blocking, warnings = [], []
    for r in ledger.get("rows", []):
        if r.get("resolution") not in RESOLUTIONS or (
                r.get("resolution") == "replace_with"
                and not str(r.get("replacement") or "").strip()):
            blocking.append(
                f"slide {r.get('slide')} {r.get('addr')}: {r.get('source_text')!r} "
                f"carried from the supplied page and not yet reconciled")
    for u in unreachable:
        warnings.append(f"{u.get('addr')}: {u.get('why')} — NOT checked; "
                        f"the vision pass is responsible for this surface")
    # Deliberately never a green "0 conflicts": silence must not read as a pass.
    if ledger.get("source_kind") == "visual":
        summary = ("Supplied page is a PDF or picture: nothing on it could be read by "
                   "machine, so it is checked by eye only (vision QC). Take every figure "
                   "from the brief or confirm it with the user.")
        _p.brief_qc_json(out_dir).write_text(
            json.dumps({"summary": summary, "blocking": blocking, "warnings": warnings},
                       indent=2), encoding="utf-8")
        return
    summary = (f"Supplied page: {total} figure-bearing slot(s), "
               f"{total - unresolved} resolved, {keeps} kept from source, "
               f"{len(unreachable)} surface(s) unreadable and referred to vision QC.")
    _p.brief_qc_json(out_dir).write_text(
        json.dumps({"summary": summary, "blocking": blocking, "warnings": warnings},
                   indent=2), encoding="utf-8")


def _pdf_pages(path: Path) -> int | None:
    """Page count of a PDF, or None when no PDF reader is installed."""
    try:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(str(path))
        try:
            return len(doc)
        finally:
            doc.close()
    except ImportError:
        pass
    except Exception:
        return None
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(path)).pages)
    except Exception:
        return None


def _pdf_text_page(path: Path, n: int) -> tuple[list[str], int] | None:
    """(text lines, number of pictures) on page n of a PDF, from its text
    layer. None when no PDF reader is installed or the page can't be read.
    A scan has no text layer: its lines come back empty."""
    try:
        import pypdfium2 as pdfium
        import pypdfium2.raw as pdfium_c
    except ImportError:
        pdfium = None
    if pdfium is not None:
        try:
            doc = pdfium.PdfDocument(str(path))
            try:
                page = doc[n - 1]
                tp = page.get_textpage()
                text = tp.get_text_range() or ""
                try:
                    pictures = sum(1 for _ in page.get_objects(
                        filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE], max_depth=3))
                except Exception:
                    pictures = 0
                return [ln.strip() for ln in text.replace("\r", "\n").split("\n")
                        if ln.strip()], pictures
            finally:
                doc.close()
        except Exception:
            pass
    try:
        from pypdf import PdfReader
        page = PdfReader(str(path)).pages[n - 1]
        text = page.extract_text() or ""
        try:
            pictures = len(page.images)
        except Exception:
            pictures = 0
        return [ln.strip() for ln in text.splitlines() if ln.strip()], pictures
    except Exception:
        return None


def _build_pdf_text(out_dir: Path, deck: Path, args, lines: list[str], pictures: int) -> int:
    """A PDF page with a text layer: its figure-bearing lines become ledger
    rows the user resolves, exactly like the slots of a PowerPoint page (owner
    decision, 2026-10-06). Option A reproduces the page's wording, so a figure
    that is only on the PDF can come through; the rows make sure each one is
    bound from the brief, confirmed, or replaced before compile. Pictures on
    the page are not machine-read: they go to the vision pass as before."""
    n = args.slide
    rows = []
    for k, line in enumerate(lines):
        if not _extract.has_figure(line):
            continue
        rows.append({
            "slide": args.target_slide or n,
            "addr": f"p{n}/line{k + 1}",
            "kind": "pdf_text",
            "shape_name": "",
            "source_text": line,
            "resolution": None,          # bind_from_brief | keep_source | replace_with
            "replacement": None,         # required when resolution == replace_with
            "note": "",
        })
    unreachable = []
    if pictures:
        unreachable.append({
            "slide": args.target_slide or n,
            "addr": f"p{n}/pictures",
            "kind": "picture",
            "why": (f"{pictures} picture(s) on PDF page {n}: any figure inside them is "
                    "not read by machine; checked by eye only (slide-qc vision pass)"),
        })
    ledger = {
        "source_page": str(deck.resolve()),
        "source_slide": n,
        "source_kind": "pdf_text",
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "_how_to": ("Rows are the figure-bearing lines of the PDF page's text. Set "
                    "`resolution` on every row to one of: bind_from_brief (take the value "
                    "from the brief), keep_source (you confirm the page's value is still "
                    "right), replace_with (+ set `replacement`). null is not a resolution "
                    "and blocks the compile."),
        "rows": rows,
        "unreachable": unreachable,
    }
    ledger_path(out_dir).write_text(json.dumps(ledger, indent=2, ensure_ascii=False),
                                    encoding="utf-8")
    _write_brief_qc(out_dir, ledger)
    unresolved, keeps, total = tally(ledger)
    _state.record_source_ledger(out_dir, unresolved, keeps, len(unreachable))
    print(f"[ok] wrote {ledger_path(out_dir)}")
    print(f"     PDF page {n} has a text layer: {total} line(s) with a figure to "
          f"reconcile, {unresolved} unresolved.")
    if pictures:
        print(f"     {pictures} picture(s) on the page are NOT read by machine; the "
              "slide-qc vision pass is responsible for them.")
    print("     compile_picks.py will refuse until every row is resolved.")
    return 0


def _build_visual(out_dir: Path, deck: Path, args) -> int:
    """A PDF page or a picture. A PDF page with a text layer is read like a
    PowerPoint page: its figure-bearing lines become rows to resolve
    (_build_pdf_text). A scan or a picture has nothing to read, so no figure
    can be machine-checked: write an honest ledger with no rows (nothing is
    claimed as bound), the whole page in `unreachable` so slide-qc's vision
    pass owns it, and the state compile needs. Delivery (check_done) says the
    page was checked by eye only. Before this, `build` crashed on any
    non-PowerPoint file and a pinned PDF could never compile (2026-10-06)."""
    n = args.slide
    is_pdf = deck.suffix.lower() == ".pdf"
    if is_pdf:
        pages = _pdf_pages(deck)
        if pages is not None and not (1 <= n <= pages):
            print(f"[error] --slide {n} out of range (the PDF has {pages} page(s))",
                  file=sys.stderr)
            return 2
        got = _pdf_text_page(deck, n)
        if got is not None and any(ch.isalnum() for ln in got[0] for ch in ln):
            return _build_pdf_text(out_dir, deck, args, got[0], got[1])
        why_pdf = ("no text layer: a scan" if got is not None
                   else "its text could not be read")
    elif n != 1:
        print(f"[error] --slide {n}: a picture has one page; use --slide 1", file=sys.stderr)
        return 2
    what = f"PDF page {n} ({why_pdf})" if is_pdf else "picture"
    unreachable = [{
        "slide": args.target_slide or n,
        "addr": f"whole page ({what})",
        "kind": "pdf" if is_pdf else "picture",
        "why": (f"{what}: its figures are not read by machine; checked by eye only "
                "(slide-qc vision pass), no figure on it was machine-checked"),
    }]
    ledger = {
        "source_page": str(deck.resolve()),
        "source_slide": n,
        "source_kind": "visual",
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "_how_to": ("A PDF or picture: nothing here was machine-read, so there are no "
                    "rows to resolve. Every figure on the slide must come from the brief "
                    "or be confirmed with the user; slide-qc's vision pass checks the "
                    "page by eye."),
        "rows": [],
        "unreachable": unreachable,
    }
    ledger_path(out_dir).write_text(json.dumps(ledger, indent=2, ensure_ascii=False),
                                    encoding="utf-8")
    _write_brief_qc(out_dir, ledger)
    _state.record_source_ledger(out_dir, 0, 0, len(unreachable), visual_only=True)
    print(f"[ok] wrote {ledger_path(out_dir)}")
    print(f"     The supplied page is a {what}: its figures are not machine-read, so "
          "none is claimed as checked.")
    print("     It is CHECKED BY EYE ONLY: the slide-qc vision pass covers it, and "
          "check_done.py says so at delivery.")
    print("     Take every figure from the brief, or confirm it with the user.")
    return 0


def cmd_build(args) -> int:
    out_dir = Path(args.out)
    deck = Path(args.deck)
    if not out_dir.exists():
        print(f"[error] out dir not found: {out_dir}", file=sys.stderr)
        return 2
    if not deck.exists():
        print(f"[error] supplied page not found: {deck}", file=sys.stderr)
        return 2

    suffix = deck.suffix.lower()
    if suffix in VISUAL_SUFFIXES:
        return _build_visual(out_dir, deck, args)
    if suffix not in (".pptx", ".pptm", ".potx"):
        print(f"[error] {deck.name}: a supplied page must be a PowerPoint file, a PDF or a "
              f"picture ({', '.join(sorted(VISUAL_SUFFIXES))}). Save it as a PDF and run "
              f"this again.", file=sys.stderr)
        return 2

    prs = Presentation(str(deck))
    slides = list(prs.slides)
    n = args.slide
    if not (1 <= n <= len(slides)):
        print(f"[error] --slide {n} out of range (deck has {len(slides)})", file=sys.stderr)
        return 2

    surfaces, unreachable = _extract.walk_slide(slides[n - 1], n)
    rows = []
    for s in surfaces:
        if not _extract.has_figure(s["text"]):
            continue          # prompt only where a figure actually lives
        rows.append({
            "slide": args.target_slide or n,
            "addr": s["addr"],
            "kind": s["kind"],
            "shape_name": s["name"],
            "source_text": s["text"],
            "resolution": None,          # bind_from_brief | keep_source | replace_with
            "replacement": None,         # required when resolution == replace_with
            "note": "",
        })

    ledger = {
        "source_page": str(deck.resolve()),
        "source_slide": n,
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "_how_to": ("Set `resolution` on every row to one of: bind_from_brief "
                    "(take the value from the brief), keep_source (you confirm the "
                    "page's value is still right), replace_with (+ set `replacement`). "
                    "null is not a resolution and blocks the compile."),
        "rows": rows,
        "unreachable": unreachable,
    }
    ledger_path(out_dir).write_text(json.dumps(ledger, indent=2, ensure_ascii=False),
                                    encoding="utf-8")
    _write_brief_qc(out_dir, ledger)
    unresolved, keeps, total = tally(ledger)
    _state.record_source_ledger(out_dir, unresolved, keeps, len(unreachable))

    print(f"[ok] wrote {ledger_path(out_dir)}")
    print(f"     {total} figure-bearing slot(s) to reconcile, {unresolved} unresolved.")
    if unreachable:
        print(f"     {len(unreachable)} surface(s) could NOT be read "
              f"(picture / SmartArt / embedded object). They are NOT checked here; "
              f"the slide-qc vision pass is responsible for them.")
    print("     compile_picks.py will refuse until every row is resolved.")
    return 0


def cmd_status(args) -> int:
    out_dir = Path(args.out)
    ledger = _load(out_dir)
    if not ledger:
        print(f"[info] no {LEDGER_NAME} in {out_dir} — no supplied page pinned.")
        return 0
    unresolved, keeps, total = tally(ledger)
    _write_brief_qc(out_dir, ledger)
    _state.record_source_ledger(out_dir, unresolved, keeps,
                                len(ledger.get("unreachable", []) or []),
                                visual_only=ledger.get("source_kind") == "visual")
    print(f"[ok] {total} slot(s): {total - unresolved} resolved, {unresolved} unresolved, "
          f"{keeps} kept from source.")
    for r in ledger.get("rows", []):
        if r.get("resolution") not in RESOLUTIONS:
            print(f"     UNRESOLVED {r['addr']}: {r['source_text']!r}")
    return 1 if unresolved else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Reconcile figures on a supplied page.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Enumerate figure-bearing slots from a supplied page.")
    b.add_argument("--out", required=True)
    b.add_argument("--deck", required=True,
                   help="The supplied page: a .pptx; a PDF (its text's figure lines "
                        "become rows; a scan is checked by eye only); or a picture "
                        "(checked by eye only).")
    b.add_argument("--slide", type=int, default=1, help="Which slide of that file.")
    b.add_argument("--target-slide", type=int, default=None,
                   help="Slide number in the deck being built (defaults to --slide).")
    b.set_defaults(func=cmd_build)
    s = sub.add_parser("status", help="Re-tally the ledger and record it.")
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_status)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
