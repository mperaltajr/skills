"""
pptx_openability.py — will PowerPoint actually open this deck?
==============================================================

Every other check in this pipeline reads the deck through python-pptx or renders
it through LibreOffice. Both are forgiving. PowerPoint is not, and it is the only
reader that matters, because it is the one the recipient uses.

An 87-slide deck was delivered twice showing "PowerPoint found a problem with
content... Repair", then "could not open the file", while python-pptx read it
happily, LibreOffice rendered every slide, and the hygiene pre-pass reported zero
violations. The defects were structural and invisible to all three.

This module checks the three structures known to produce that symptom. Each is a
hard stop, not an advisory: a deck that trips one of them cannot be opened at all,
so there is no partial delivery to weigh.

  1. Incomplete <p:style>. The element takes exactly four children, in order:
     lnRef, fillRef, effectRef, fontRef. LibreOffice draws a preset shadow from
     the theme's effectRef, which does not match the flat HTML design, and the
     obvious-looking fix is to delete the element. PowerPoint then rejects the
     file. The correct way to say "no shadow" is effectRef idx="0".

  2. Duplicate shape ids. A shape's id must be unique within its slide. The graft
     paths merge shape trees that each numbered themselves from 1; they now
     renumber on graft, but a hand-edit made after compile can reintroduce it.
     PowerPoint repairs this one sometimes and refuses it sometimes — one deck
     shipped with 58 slides carrying duplicates and opened anyway — so it is
     reported as a defect to fix, not as proof the deck is unopenable.

  3. A graphicFrame (table, chart, diagram) whose r:embed/r:id points at a
     relationship the slide part does not have. A naive deepcopy carries the id
     string without the relationship behind it.

Usable as a library (`check_openability(prs, path)`) or standalone:

    py -3 pptx_openability.py "<deck.pptx>"

Prints one line per problem and exits 1 if any were found.
"""
from __future__ import annotations

import pathlib
import sys

from pptx.oxml.ns import qn

# <p:style>'s children, in the only order the schema accepts.
_STYLE_CHILDREN = ("a:lnRef", "a:fillRef", "a:effectRef", "a:fontRef")


def _shape_label(elem) -> str:
    """A human-usable name for the shape an element belongs to."""
    node = elem
    while node is not None:
        cNvPr = node.find(".//" + qn("p:cNvPr"))
        if cNvPr is not None:
            return cNvPr.get("name") or f"id {cNvPr.get('id')}"
        node = node.getparent()
    return "an unnamed shape"


def check_style_elements(slide, slide_num: int) -> list[dict]:
    """Every <p:style> must carry all four children, in order."""
    out: list[dict] = []
    expected = [qn(t) for t in _STYLE_CHILDREN]
    for style in slide.shapes._spTree.iter(qn("p:style")):
        present = [c.tag for c in style if isinstance(c.tag, str)]
        if present == expected:
            continue
        missing = [t for t in _STYLE_CHILDREN if qn(t) not in present]
        detail = (f"missing {', '.join(m.split(':')[1] for m in missing)}"
                  if missing else "children out of order")
        out.append({
            "slide": slide_num,
            "severity": "Critical",
            "category": "openability",
            "issue": (f"{_shape_label(style)}: <p:style> is incomplete ({detail}). "
                      f"PowerPoint will refuse the file. To suppress a preset "
                      f"shadow, keep all four children and set effectRef idx=\"0\"."),
        })
    return out


def check_duplicate_shape_ids(slide, slide_num: int) -> list[dict]:
    """A shape id must be unique within its slide."""
    seen: dict[str, int] = {}
    for cNvPr in slide.shapes._spTree.iter(qn("p:cNvPr")):
        sid = cNvPr.get("id")
        if sid:
            seen[sid] = seen.get(sid, 0) + 1
    dupes = sorted(sid for sid, count in seen.items() if count > 1)
    if not dupes:
        return []
    return [{
        "slide": slide_num,
        "severity": "Critical",
        "category": "openability",
        "issue": (f"shape id(s) {', '.join(dupes[:4])} used more than once. "
                  f"The file is invalid; PowerPoint repairs it sometimes and "
                  f"refuses it sometimes. Rebuild through the pipeline rather "
                  f"than editing the compiled deck."),
    }]


def check_dangling_relationships(slide, slide_num: int) -> list[dict]:
    """Every r:id/r:embed referenced on the slide must exist in its part."""
    try:
        have = set(slide.part.rels)
    except Exception:
        return []
    out: list[dict] = []
    r_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    seen_bad: set[str] = set()
    for elem in slide.shapes._spTree.iter():
        for attr in ("id", "embed", "link", "dm", "lo", "qs", "cs"):
            rid = elem.get(r_ns + attr)
            if rid and rid not in have and rid not in seen_bad:
                seen_bad.add(rid)
                out.append({
                    "slide": slide_num,
                    "severity": "Critical",
                    "category": "openability",
                    "issue": (f"{_shape_label(elem)} references {rid}, which this "
                              f"slide does not have. A copied table, chart or "
                              f"picture lost the relationship behind it."),
                })
    return out


def check_openability(prs, pptx_path=None) -> list[dict]:
    """Run every structural check. Returns violations in the hygiene JSON shape."""
    out: list[dict] = []
    for n, slide in enumerate(prs.slides, start=1):
        out.extend(check_style_elements(slide, n))
        out.extend(check_duplicate_shape_ids(slide, n))
        out.extend(check_dangling_relationships(slide, n))
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[-3].strip(), file=sys.stderr)
        return 2
    path = pathlib.Path(sys.argv[1]).resolve()
    from pptx import Presentation
    problems = check_openability(Presentation(str(path)), path)
    if not problems:
        print(f"ok: {path.name} has no structure PowerPoint would refuse.")
        return 0
    print(f"{len(problems)} problem(s) PowerPoint would refuse in {path.name}:")
    for p in problems:
        print(f"  slide {p['slide']}: {p['issue']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
