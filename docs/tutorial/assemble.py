#!/usr/bin/env python3
"""assemble.py: build Slide-Lab-Tutorial.html from tutorial_src.html.

  1. Reads the facts block (<script id="slidelab-facts">) in tutorial_src.html.
  2. Writes each fact into every element marked data-f="<key>" (nested keys
     use dots, e.g. data-f="t.designs"), so the page reads correctly with
     scripts turned off. The data-f markers and the facts block stay in the
     output so check_tutorial.py can compare them.
  3. Embeds review.png and final.png (beside this script) as JPEG, at most
     1200 px wide, quality 82.
  4. Embeds the four files the guide links to (install guide, example
     storyline, review page and deck, from the skills folder), so the guide
     still works when it is emailed on its own. Each link gets data-att; the
     page script opens or downloads the embedded copy.
  5. Writes <skills folder>/Slide-Lab-Tutorial.html and runs check_tutorial.py.

The tutorial is public, so it is built from the published
slide-builder/settings.json only: this computer's settings.local.json (say,
three designs per slide) is ignored (SLIDE_LAB_SETTINGS_LOCAL=none, also for
the check it runs). Never edit the built file by hand: change
tutorial_src.html and run this. slide-builder/tests/run_tutorial_build_smoke.py
fails when this script's output differs from the committed
Slide-Lab-Tutorial.html.

Run:  py -3 docs/tutorial/assemble.py [--out <path>]
      (--out writes the page somewhere else, for the test)
Exit: 0 written and check passed | 1 check failed or a fact is missing
"""
from __future__ import annotations

import argparse
import base64
import html
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

# Published settings only, for this script and the check it starts.
os.environ["SLIDE_LAB_SETTINGS_LOCAL"] = "none"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # the skills folder
SRC = HERE / "tutorial_src.html"
OUT = ROOT / "Slide-Lab-Tutorial.html"
CHECK = ROOT / "slide-builder" / "scripts" / "check_tutorial.py"
IMAGES = {"{{IMG_REVIEW}}": HERE / "review.png", "{{IMG_FINAL}}": HERE / "final.png"}
ATTACH = {
    "Slide-Lab-Install-Guide.docx":
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "Slide-Lab-Example-Storyline.html": "text/html",
    "Slide-Lab-Example-Review.html": "text/html",
    "Slide-Lab-Example-Deck.pptx":
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}

FACTS_RE = re.compile(r'<script[^>]*id="slidelab-facts"[^>]*>(.*?)</script>', re.S)
# an element carrying data-f, with no child elements (facts are plain text)
FACT_EL_RE = re.compile(r'(<(\w+)\b[^>]*\sdata-f="([^"]+)"[^>]*>)([^<]*)(</\2>)')


def _get(facts: dict, path: str):
    cur = facts
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def _jpeg_b64(png: Path) -> str:
    im = Image.open(png).convert("RGB")
    if im.width > 1200:
        im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=OUT)
    out = ap.parse_args().out
    page = SRC.read_text(encoding="utf-8")
    facts = json.loads(FACTS_RE.search(page).group(1))

    missing: list[str] = []

    def fill(m: re.Match) -> str:
        value = _get(facts, m.group(3))
        if value is None:
            missing.append(m.group(3))
            return m.group(0)
        return m.group(1) + html.escape(str(value), quote=False) + m.group(5)

    page = FACT_EL_RE.sub(fill, page)
    if missing:
        print("Facts missing from the facts block: " + ", ".join(sorted(set(missing))))
        return 1
    leftover = re.findall(r'data-f="([^"]+)"[^>]*></', page)
    if leftover:
        print("Elements left empty (they contain markup?): " + ", ".join(sorted(set(leftover))))
        return 1

    for marker, png in IMAGES.items():
        page = page.replace(marker, _jpeg_b64(png))
    if "{{" in page:
        print("An image placeholder was not replaced")
        return 1

    blocks = []
    for i, (name, mime) in enumerate(ATTACH.items()):
        f = ROOT / name
        link = f'<a href="{name}"'
        if link not in page:
            continue
        if not f.exists():
            print(f"Linked file missing: {f}")
            return 1
        page = page.replace(link, f'{link} data-att="{i}"')
        # A data: URI, so check_tutorial.py skips it like the pictures.
        data = base64.b64encode(f.read_bytes()).decode("ascii")
        blocks.append(f'<script type="text/plain" id="att-{i}" data-name="{name}" '
                      f'data-type="{mime}">data:{mime};base64,{data}</script>')
    page = page.replace("</body>", "\n".join(blocks) + "\n</body>", 1)

    out.write_text(page, encoding="utf-8", newline="\n")
    print(f"Written: {out}")
    return subprocess.call([sys.executable, str(CHECK), "--tutorial", str(out)])


if __name__ == "__main__":
    sys.exit(main())
