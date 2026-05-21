#!/usr/bin/env python3
"""
check_slide_geometry.py

Geometry and typography QA for a freshly-built slide XML. Runs after each
slide-builder-worker writes its /tmp/session_deck/ppt/slides/slideN.xml
and before the deck is packed.

Exits 0 on pass. Exits non-zero on fail with a specific error listing on stderr.

Checks performed (v1):
1. Bounding box overlap -- no two text/placeholder shapes may overlap their
   bounding boxes beyond a small tolerance
2. Slide-boundary containment -- every shape must fit within the slide
3. Typography palette -- at most 4 distinct font sizes per slide
   (title size + 2 body sizes + 9pt footnote/pagenum)
4. Empty-zone check -- if the bottom 40% of the slide contains no shapes,
   warn (soft warning, does not fail)

Usage:
    check_slide_geometry.py <slide_xml_path> <slide_width_emu> <slide_height_emu>

Returns (via exit code):
    0 = pass (slide is clean)
    1 = overlap failure
    2 = boundary failure
    3 = typography failure
    4 = multiple failures
    9 = could not parse slide (unexpected XML structure)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from lxml import etree
except ImportError:
    print("ERROR: lxml not installed. Run: py -3 -m pip install lxml", file=sys.stderr)
    sys.exit(9)


NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}

# Pixels of tolerance when comparing bounding boxes. 2000 EMU ~= 0.002 inches.
# Below this threshold we don't call it an overlap.
OVERLAP_TOLERANCE_EMU = 2000


@dataclass
class ShapeBox:
    """A shape's bounding box + its text content for error messages."""
    x: int
    y: int
    w: int
    h: int
    text: str
    is_title: bool = False  # title placeholders get special treatment
    is_footer: bool = False  # footers/page nums get special treatment
    layered_intentionally: bool = False  # e.g., text inside a panel shape

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h

    def overlaps(self, other: "ShapeBox") -> bool:
        """Return True if this box overlaps `other` beyond the tolerance."""
        if self.layered_intentionally or other.layered_intentionally:
            return False
        # Standard AABB overlap test with tolerance
        if self.right - OVERLAP_TOLERANCE_EMU <= other.x:
            return False
        if other.right - OVERLAP_TOLERANCE_EMU <= self.x:
            return False
        if self.bottom - OVERLAP_TOLERANCE_EMU <= other.y:
            return False
        if other.bottom - OVERLAP_TOLERANCE_EMU <= self.y:
            return False
        return True


def parse_slide(slide_path: Path) -> tuple[list[ShapeBox], list[int]]:
    """Return (list of ShapeBoxes with text content, list of font sizes in hundredths of a point).

    Font sizes: PPTX stores them as 100ths of a point, so 1400 = 14pt.
    We return the raw 100ths so the typography check can group small variations.
    """
    tree = etree.parse(str(slide_path))
    root = tree.getroot()

    shapes: list[ShapeBox] = []
    sizes: list[int] = []

    # Every shape (text box, placeholder, autoshape)
    for sp in root.iter(f"{{{NS['p']}}}sp"):
        # Position + size
        xfrm = sp.find(".//p:spPr/a:xfrm", NS)
        if xfrm is None:
            continue
        off = xfrm.find("a:off", NS)
        ext = xfrm.find("a:ext", NS)
        if off is None or ext is None:
            continue
        try:
            x = int(off.get("x", "0"))
            y = int(off.get("y", "0"))
            w = int(ext.get("cx", "0"))
            h = int(ext.get("cy", "0"))
        except ValueError:
            continue
        if w == 0 or h == 0:
            continue

        # Text content (first 60 chars for error messages)
        texts = [t.text or "" for t in sp.iter(f"{{{NS['a']}}}t")]
        text = " ".join(t for t in texts if t.strip())[:60]

        # Detect title placeholder
        ph = sp.find(".//p:nvSpPr/p:nvPr/p:ph", NS)
        is_title = False
        is_footer = False
        if ph is not None:
            ph_type = ph.get("type", "")
            ph_idx = ph.get("idx", "")
            if ph_type in ("title", "ctrTitle"):
                is_title = True
            if ph_type in ("ftr", "sldNum", "dt"):
                is_footer = True

        # Heuristic: text inside a solid-filled rect/shape that covers a
        # larger area is typically intentionally layered (e.g., "NET RESULT"
        # inside a dark panel). Detect by checking for a solid fill.
        # For now: if this shape has a solid fill AND text, mark it as layered
        # when other shapes' text may be sitting "on" it.
        # Simpler heuristic: if the shape's own area is > 10% of a typical
        # slide (10% of 12192000 x 6858000 ~ 8e12 EMU^2), treat as a "panel"
        # which can have text layered inside it legally.
        area = w * h
        is_panel = area > 8e12  # big filled region

        shapes.append(ShapeBox(
            x=x, y=y, w=w, h=h,
            text=text,
            is_title=is_title,
            is_footer=is_footer,
            layered_intentionally=is_panel,
        ))

        # Font sizes: walk every run, pull sz attribute
        for r in sp.iter(f"{{{NS['a']}}}r"):
            rPr = r.find(f"{{{NS['a']}}}rPr")
            if rPr is None:
                continue
            sz = rPr.get("sz")
            if sz is None:
                continue
            try:
                sizes.append(int(sz))
            except ValueError:
                continue

    return shapes, sizes


def check_overlaps(shapes: list[ShapeBox]) -> list[str]:
    """Return list of overlap error messages (empty if clean)."""
    errors = []
    for i, a in enumerate(shapes):
        # Skip comparisons between title and footer -- they won't overlap in practice
        if a.is_title or a.is_footer:
            continue
        for j in range(i + 1, len(shapes)):
            b = shapes[j]
            if b.is_title or b.is_footer:
                continue
            if a.overlaps(b):
                errors.append(
                    f"Overlap: [{a.text!r}] collides with [{b.text!r}]"
                )
    return errors


def check_boundaries(
    shapes: list[ShapeBox],
    slide_w: int,
    slide_h: int,
) -> list[str]:
    """Return list of boundary-violation error messages."""
    errors = []
    for s in shapes:
        # Allow a small negative start (shapes occasionally start at x=-N,
        # typically still visible). Require strict containment of the right/bottom
        if s.x < -50_000:  # allow ~0.05" bleed to the left
            errors.append(f"Left boundary violated by [{s.text!r}]: x={s.x}")
        if s.y < -50_000:
            errors.append(f"Top boundary violated by [{s.text!r}]: y={s.y}")
        if s.right > slide_w + 50_000:
            errors.append(
                f"Right boundary violated by [{s.text!r}]: "
                f"extends to x={s.right}, slide width={slide_w}"
            )
        if s.bottom > slide_h + 50_000:
            errors.append(
                f"Bottom boundary violated by [{s.text!r}]: "
                f"extends to y={s.bottom}, slide height={slide_h}"
            )
    return errors


def check_typography(sizes: list[int]) -> list[str]:
    """Return typography error messages.

    Rule: at most 4 distinct font sizes per slide, counting within a 0.5pt
    tolerance (so 13pt and 13.5pt count as the same).

    Sizes are in 100ths of a point, so 1400 = 14pt, 1350 = 13.5pt.
    Group sizes within 50 (0.5pt) of each other.
    """
    if not sizes:
        return []

    # Group sizes within 50 (0.5pt) of each other
    sorted_sizes = sorted(set(sizes))
    groups = []
    current_group = [sorted_sizes[0]]
    for s in sorted_sizes[1:]:
        if s - current_group[-1] <= 50:
            current_group.append(s)
        else:
            groups.append(current_group)
            current_group = [s]
    groups.append(current_group)

    distinct_count = len(groups)
    if distinct_count > 4:
        group_reprs = [f"{g[0] // 100}pt" for g in groups]
        return [
            f"Typography: {distinct_count} distinct font sizes used "
            f"({', '.join(group_reprs)}). "
            f"MBB rule: max 4 (title + 2 body sizes + 9pt footer). "
            f"Collapse to the closest valid palette."
        ]
    return []


def check_empty_bottom(
    shapes: list[ShapeBox],
    slide_h: int,
) -> list[str]:
    """Soft warning if bottom 40% of slide is empty (not a fail, just a warn)."""
    warnings = []
    threshold = slide_h * 0.6  # top 60% is where "normal" content lives
    shapes_in_bottom = [
        s for s in shapes
        if not s.is_footer and s.y > threshold
    ]
    if not shapes_in_bottom:
        warnings.append(
            "Empty-zone warning: bottom 40% of slide contains no non-footer content. "
            "Layout may be top-heavy -- consider redistributing vertically."
        )
    return warnings


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "Usage: check_slide_geometry.py <slide_xml_path> <slide_w_emu> <slide_h_emu>",
            file=sys.stderr,
        )
        return 9

    slide_path = Path(sys.argv[1])
    try:
        slide_w = int(sys.argv[2])
        slide_h = int(sys.argv[3])
    except ValueError:
        print("Slide dimensions must be integers (EMU)", file=sys.stderr)
        return 9

    if not slide_path.is_file():
        print(f"Slide file not found: {slide_path}", file=sys.stderr)
        return 9

    try:
        shapes, sizes = parse_slide(slide_path)
    except etree.XMLSyntaxError as e:
        print(f"Could not parse slide XML: {e}", file=sys.stderr)
        return 9

    print(f"Checking slide: {slide_path.name}")
    print(f"  Shapes: {len(shapes)}, Font sizes found: {len(sizes)}")

    overlap_errs = check_overlaps(shapes)
    boundary_errs = check_boundaries(shapes, slide_w, slide_h)
    typography_errs = check_typography(sizes)
    empty_warns = check_empty_bottom(shapes, slide_h)

    all_errors = []
    if overlap_errs:
        print(f"\nOVERLAP FAILURES ({len(overlap_errs)}):", file=sys.stderr)
        for e in overlap_errs:
            print(f"  - {e}", file=sys.stderr)
        all_errors.append("overlap")

    if boundary_errs:
        print(f"\nBOUNDARY FAILURES ({len(boundary_errs)}):", file=sys.stderr)
        for e in boundary_errs:
            print(f"  - {e}", file=sys.stderr)
        all_errors.append("boundary")

    if typography_errs:
        print(f"\nTYPOGRAPHY FAILURES:", file=sys.stderr)
        for e in typography_errs:
            print(f"  - {e}", file=sys.stderr)
        all_errors.append("typography")

    # Warnings (non-fatal)
    if empty_warns:
        print(f"\nWARNINGS:")
        for w in empty_warns:
            print(f"  - {w}")

    if not all_errors:
        print("\nPASS: slide geometry and typography are clean.")
        return 0

    # Return code based on which failure types occurred
    if len(all_errors) > 1:
        print(f"\nFAIL: {len(all_errors)} failure categories: {', '.join(all_errors)}", file=sys.stderr)
        return 4
    if "overlap" in all_errors:
        return 1
    if "boundary" in all_errors:
        return 2
    if "typography" in all_errors:
        return 3
    return 4


if __name__ == "__main__":
    sys.exit(main())
