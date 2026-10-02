#!/usr/bin/env python3
"""assemble.py: build Slide-Lab-Tutorial.html from tutorial_src.html.

  1. Reads the facts block (<script id="slidelab-facts">) in tutorial_src.html.
  2. Writes each fact into every element marked data-f="<key>" (nested keys
     use dots, e.g. data-f="t.designs"), so the page reads correctly with
     scripts turned off. The data-f markers and the facts block stay in the
     output so check_tutorial.py can compare them.
  3. Embeds review.png and final.png (beside this script) as JPEG, at most
     1200 px wide, quality 82.
  4. Writes <skills folder>/Slide-Lab-Tutorial.html and runs check_tutorial.py.

Run:  py -3 docs/tutorial/assemble.py
Exit: 0 written and check passed | 1 check failed or a fact is missing
"""
from __future__ import annotations

import base64
import html
import io
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # the skills folder
SRC = HERE / "tutorial_src.html"
OUT = ROOT / "Slide-Lab-Tutorial.html"
CHECK = ROOT / "slide-builder" / "scripts" / "check_tutorial.py"
IMAGES = {"{{IMG_REVIEW}}": HERE / "review.png", "{{IMG_FINAL}}": HERE / "final.png"}

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

    OUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"Written: {OUT}")
    return subprocess.call([sys.executable, str(CHECK), "--tutorial", str(OUT)])


if __name__ == "__main__":
    sys.exit(main())
