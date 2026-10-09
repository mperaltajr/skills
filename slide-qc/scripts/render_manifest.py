#!/usr/bin/env python3
"""render_manifest.py — what a folder of page images is a render OF.

A folder of slide_NN.png files says nothing about which deck it shows, which
program drew it or at what resolution. So every render that the quality check
relies on (compile's render, and render_slides.py run from the command line)
writes render_manifest.json beside the images:

  deck            the deck's path
  deck_digest     md5 of the deck's bytes (the render is evidence about these bytes)
  renderer        "powerpoint" or "libreoffice" (the program that actually drew it)
  dpi             the resolution
  template_fp     a fingerprint of the deck's slide masters and theme (template changes)
  slides          page count
  pages           [{page, image, hash, file_md5, layout}]: hash is md5 of the
                  decoded pixels (PNG metadata cannot change it), file_md5 the
                  file's bytes (fast reuse check), layout the page's layout name

Page images are compared by their pixel hash, exactly (no tolerance).
Measured 2026-10-09 at 150 dpi, each deck drawn twice by each program
(PowerPoint through ppt_safe, read-only, no window; LibreOffice headless):
  - a fictional 6-page deck on the default template (title, bullets, a
    native column chart, a table, a filled shape): 6 of 6 pages identical
    pixels AND identical file bytes, in both programs
  - a fictional 8-page deck on the test template (its masters and layouts),
    with pictures and page-number fields: 8 of 8 identical, both programs
  - a one-word edit in one title changed that page's image only, both decks,
    both programs
So both renderers are deterministic for these decks on this computer. A
program update or a font change can change every page's pixels; then those
pages are simply read again: the comparison errs toward re-reading, never
toward skipping a page.
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path

MANIFEST = "render_manifest.json"
SCHEMA = 1


def file_md5(path) -> str:
    h = hashlib.md5()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except Exception:
        return ""
    return h.hexdigest()


def pixel_hash(png) -> str:
    """md5 of the decoded RGB pixels plus the size."""
    from PIL import Image
    with Image.open(png) as im:
        rgb = im.convert("RGB")
        h = hashlib.md5(f"{rgb.size[0]}x{rgb.size[1]}:".encode())
        h.update(rgb.tobytes())
    return h.hexdigest()


def template_fingerprint(deck) -> str:
    """Hash of the deck's slide master(s) and theme(s), by content (part names
    are ignored, so renumbering does not count as a change). Layout parts are
    left out: compile keeps only the layouts in use, and a page whose layout
    changed shows up as a changed page image anyway."""
    try:
        with zipfile.ZipFile(deck) as z:
            parts = sorted(hashlib.md5(z.read(n)).hexdigest() for n in z.namelist()
                           if re.match(r"ppt/(slideMasters/slideMaster|theme/theme)\d+\.xml$", n))
    except Exception:
        return ""
    return hashlib.md5("|".join(parts).encode()).hexdigest()


def layout_names(deck) -> list[str]:
    """Each page's layout name ('' when unknown)."""
    try:
        from pptx import Presentation
        return [s.slide_layout.name or "" for s in Presentation(str(deck)).slides]
    except Exception:
        return []


def manifest_path(img_dir) -> Path:
    return Path(img_dir) / MANIFEST


def read(img_dir) -> dict:
    p = manifest_path(img_dir)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write(img_dir, deck, renderer: str, dpi: int, writer: str = "") -> dict:
    """Hash every slide_NN.png in img_dir and write the manifest."""
    img_dir = Path(img_dir)
    pngs = sorted(img_dir.glob("slide_*.png"),
                  key=lambda p: int(re.sub(r"\D", "", p.stem) or 0))
    layouts = layout_names(deck)
    pages = []
    for i, png in enumerate(pngs, start=1):
        pages.append({"page": i, "image": png.name, "hash": pixel_hash(png),
                      "file_md5": file_md5(png),
                      "layout": layouts[i - 1] if i - 1 < len(layouts) else ""})
    man = {"schema": SCHEMA, "deck": str(Path(deck).resolve()),
           "deck_digest": file_md5(deck), "renderer": renderer, "dpi": int(dpi),
           "template_fp": template_fingerprint(deck), "slides": len(pages),
           "pages": pages, "writer": writer,
           "at": datetime.now().isoformat(timespec="seconds")}
    manifest_path(img_dir).write_text(json.dumps(man, indent=2), encoding="utf-8")
    return man


def reusable(img_dir, deck, renderer: str, dpi: int) -> tuple[bool, str]:
    """Can the images in img_dir stand in for a fresh render of deck with
    this renderer at this dpi? Only when the manifest names these exact deck
    bytes, the same program and resolution, and every image is still the file
    the manifest hashed."""
    man = read(img_dir)
    if not man:
        return False, "no render manifest"
    if man.get("deck_digest") != file_md5(deck):
        return False, "the images are of different deck bytes"
    if man.get("renderer") != renderer:
        return False, f"drawn by {man.get('renderer')}, not {renderer}"
    if int(man.get("dpi") or 0) != int(dpi):
        return False, f"drawn at {man.get('dpi')} dpi, not {dpi}"
    for pg in man.get("pages") or []:
        f = Path(img_dir) / pg.get("image", "")
        if not f.exists() or file_md5(f) != pg.get("file_md5"):
            return False, f"{pg.get('image')} is missing or changed"
    extra = [p for p in Path(img_dir).glob("slide_*.png")
             if p.name not in {pg.get("image") for pg in man.get("pages") or []}]
    if extra or not man.get("pages"):
        return False, "the folder holds images the manifest does not list"
    return True, f"{man['slides']} page images of these exact deck bytes"


def verify_images(man: dict, img_dir) -> list[str]:
    """Pages whose image on disk no longer matches the manifest (empty when
    they all match, or when the images were cleaned away after delivery)."""
    bad = []
    for pg in man.get("pages") or []:
        f = Path(img_dir) / pg.get("image", "")
        if f.exists() and pixel_hash(f) != pg.get("hash"):
            bad.append(pg.get("image"))
    return bad
