#!/usr/bin/env python3
"""migrate_brief_to_v3.py — upgrade a v0.1 narrative brief to v0.2 layout schema.

v0.2 build_deck.py requires every slide to resolve a chrome.yml layout, either
via per-slide `**Layout:** <name>` or via a deck-level `default_layout:` in
the front-matter. Briefs authored before P1.4 land lack both — this migrator
adds the deck-level default + a cover override on slide 1, which is enough
for finalize_deck to graft against the right layouts.

Usage:
    py -3 scripts/migrate_brief_to_v3.py <brief.md>
    py -3 scripts/migrate_brief_to_v3.py <brief.md> --default-layout body_canonical_light
    py -3 scripts/migrate_brief_to_v3.py <brief.md> --slide1-layout cover_light

The migrator is idempotent — running it twice on the same brief is a no-op.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


_FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_SLIDE_HEADER_RE = re.compile(
    r"^(?P<hdr>#{2,3}\s+Slide\s+(?P<n>\d+)\s*(?:[—\-:]\s*.+?)?)$",
    re.MULTILINE,
)
_LAYOUT_FIELD_RE = re.compile(r"\*\*Layout\s*:?\*\*", re.IGNORECASE)
_DEFAULT_LAYOUT_LINE_RE = re.compile(r"^\s*default_layout\s*:", re.MULTILINE)


def _ensure_default_layout(text: str, default_layout: str) -> str:
    """Add `default_layout: <name>` to the YAML front-matter if absent."""
    m = _FRONT_MATTER_RE.match(text)
    if not m:
        # No front-matter — create one.
        new_fm = f"default_layout: {default_layout}\n"
        return f"---\n{new_fm}---\n\n" + text
    fm_text = m.group(1)
    if _DEFAULT_LAYOUT_LINE_RE.search(fm_text):
        return text  # already set; idempotent
    new_fm = fm_text.rstrip("\n") + f"\ndefault_layout: {default_layout}\n"
    return text.replace(m.group(0), f"---\n{new_fm}---\n", 1)


def _slide_blocks(text: str) -> list[tuple[int, int, int]]:
    """Return [(slide_n, start_of_header, end_of_block), ...] for each slide."""
    matches = list(_SLIDE_HEADER_RE.finditer(text))
    out: list[tuple[int, int, int]] = []
    for i, m in enumerate(matches):
        n = int(m.group("n"))
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((n, start, end))
    return out


def _ensure_slide_layout(text: str, target_slide_n: int, layout_name: str) -> str:
    """Insert `**Layout:** <name>` into the body of the named slide block when
    the block has no Layout field yet."""
    for n, start, end in _slide_blocks(text):
        if n != target_slide_n:
            continue
        block = text[start:end]
        if _LAYOUT_FIELD_RE.search(block):
            return text  # already present; idempotent
        # Insert just after the slide header line (the first line of the block).
        header_end_in_block = block.find("\n")
        if header_end_in_block == -1:
            # No newline — append at end of block.
            insertion = f"\n**Layout:** {layout_name}\n"
            return text[:end] + insertion + text[end:]
        insert_pos = start + header_end_in_block + 1
        insertion = f"**Layout:** {layout_name}\n"
        return text[:insert_pos] + insertion + text[insert_pos:]
    return text


def migrate_brief(
    brief_path: Path, *,
    default_layout: str = "body_canonical_light",
    slide1_layout: str = "cover_light",
) -> bool:
    """Migrate the brief in-place. Returns True if file content changed."""
    original = brief_path.read_text(encoding="utf-8")
    text = _ensure_default_layout(original, default_layout)
    text = _ensure_slide_layout(text, target_slide_n=1, layout_name=slide1_layout)
    if text != original:
        brief_path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Migrate a narrative brief to v0.2 layout schema (default_layout + slide-1 cover override).",
    )
    ap.add_argument("brief", type=Path, help="Path to the narrative brief markdown")
    ap.add_argument("--default-layout", default="body_canonical_light",
                    help="Deck-level default_layout (front-matter). "
                         "Default: body_canonical_light")
    ap.add_argument("--slide1-layout", default="cover_light",
                    help="Layout for slide 1 if it has no **Layout:** field. "
                         "Default: cover_light")
    args = ap.parse_args()

    if not args.brief.exists():
        sys.stderr.write(f"ERROR: brief not found: {args.brief}\n")
        return 1
    changed = migrate_brief(
        args.brief,
        default_layout=args.default_layout,
        slide1_layout=args.slide1_layout,
    )
    if changed:
        print(f"Migrated: {args.brief}")
        print(f"  default_layout: {args.default_layout}")
        print(f"  slide 1 layout: {args.slide1_layout}")
    else:
        print(f"Already v0.2-compliant (no changes needed): {args.brief}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
