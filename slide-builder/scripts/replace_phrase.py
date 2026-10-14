#!/usr/bin/env python3
"""replace_phrase.py: change one phrase everywhere in a deck, in one command.

A wording change ("buyers" to "customers") used to take a dozen hand-run turns
over the storyline, the brief, its Word and web copies and every slide option,
and a few copies were always missed (18 turns on one deck). This lists every
place the phrase appears first, then changes them all at once (Q2 decision,
2026-10-14):

  py -3 scripts/replace_phrase.py --out <deck folder> --find "buyers" --replace "customers"
        (a dry run: lists every hit, changes nothing)
  py -3 scripts/replace_phrase.py --out <deck folder> --find "buyers" --replace "customers" --apply

Where it looks: the brief, the approved storyline the brief points at, the
dot-dash storyline files (.md, .html, .docx) and every slide's designs
(option_X.html, option_X.py). Converted scripts (option_X_native.py) are never
edited: a changed design is converted again by the pipeline. In HTML only the
text is changed, never tags or class names. Whole words only, unless
--anywhere; case counts, unless --ignore-case. Use it only for wording the
user gave word for word; it prints the steps that follow (re-seal, re-render,
record the edit).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _rulings  # noqa: E402

TAG_SPLIT = re.compile(r"(<[^>]*>)")


def _pattern(find: str, anywhere: bool, ignore_case: bool) -> re.Pattern:
    p = re.escape(find)
    if not anywhere:
        if find[:1].isalnum():
            p = r"(?<![A-Za-z0-9])" + p
        if find[-1:].isalnum():
            p = p + r"(?![A-Za-z0-9])"
    return re.compile(p, re.I if ignore_case else 0)


def targets(out: Path) -> list[tuple[str, Path]]:
    """(kind, file) for every file the phrase is looked for in."""
    sd = _rulings.session_dir(out=out)
    found: list[tuple[str, Path]] = []
    brief = _rulings.find_brief(sd, out)
    if brief:
        found.append(("brief", brief))
        try:
            import build_deck
            fm, _b = build_deck.extract_front_matter(brief.read_text(encoding="utf-8"))
            st = (fm.get("approved_storyline") or "").strip().strip('"')
            if st and Path(st).is_file():
                found.append(("storyline", Path(st)))
        except Exception:
            pass
    root = sd.parent
    for pat in ("dot-dash-*.md", "dot-dash-*.html", "dot-dash-*.docx",
                "*Storyline*.md", "*Storyline*.html", "*Storyline*.docx"):
        for f in sorted(root.glob(pat)):
            found.append(("storyline", f))
    for sdir in sorted(Path(out).glob("slide_[0-9][0-9]")):
        for f in sorted(sdir.glob("option_[A-F].html")) + sorted(sdir.glob("option_[A-F].py")):
            found.append(("design", f))
    seen, uniq = set(), []
    for k, f in found:
        r = f.resolve()
        if r not in seen:
            seen.add(r)
            uniq.append((k, f))
    return uniq


def _text_hits(text: str, rx: re.Pattern, html_mode: bool) -> list[tuple[int, str]]:
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        parts = TAG_SPLIT.split(line) if html_mode else [line]
        for j, part in enumerate(parts):
            if html_mode and j % 2 == 1:
                continue
            for m in rx.finditer(part):
                a, b = max(0, m.start() - 40), min(len(part), m.end() + 40)
                hits.append((i, part[a:b].strip()))
    return hits


def _replace_text(text: str, rx: re.Pattern, new: str, html_mode: bool) -> tuple[str, int]:
    if not html_mode:
        return rx.subn(lambda _m: new, text)
    parts = TAG_SPLIT.split(text)
    n = 0
    in_style = False
    for j in range(len(parts)):
        if j % 2 == 1:
            tag = parts[j].lower()
            if tag.startswith("<style") or tag.startswith("<script"):
                in_style = True
            elif tag.startswith("</style") or tag.startswith("</script"):
                in_style = False
            continue
        if in_style:
            continue
        parts[j], k = rx.subn(lambda _m: new, parts[j])
        n += k
    return "".join(parts), n


def _docx_paragraphs(doc):
    for p in doc.paragraphs:
        yield p
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p


def _docx_replace_para(p, rx: re.Pattern, new: str) -> int:
    """Replace in one Word paragraph, keeping the formatting of the run where
    each match starts (a match may run across several runs)."""
    n, start = 0, 0
    while True:
        runs = list(p.runs)
        full = "".join(r.text for r in runs)
        m = rx.search(full, start)
        if not m:
            return n
        start = m.start() + len(new)
        pos, spans = 0, []
        for r in runs:
            spans.append((pos, pos + len(r.text)))
            pos += len(r.text)
        first = next(i for i, (a, b) in enumerate(spans) if a <= m.start() < b)
        last = next(i for i, (a, b) in enumerate(spans) if a < m.end() <= b)
        a0 = spans[first][0]
        tail_start = m.end() - spans[last][0]
        tail = runs[last].text[tail_start:]
        runs[first].text = runs[first].text[:m.start() - a0] + new + (tail if first == last else "")
        if first != last:
            for i in range(first + 1, last):
                runs[i].text = ""
            runs[last].text = tail
        n += 1


def scan_docx(path: Path, rx: re.Pattern, new: str | None):
    from docx import Document
    doc = Document(str(path))
    hits, n = [], 0
    for i, p in enumerate(_docx_paragraphs(doc), 1):
        t = p.text
        for m in rx.finditer(t):
            a, b = max(0, m.start() - 40), min(len(t), m.end() + 40)
            hits.append((i, t[a:b].strip()))
        if new is not None and rx.search(t):
            n += _docx_replace_para(p, rx, new)
    if new is not None and n:
        doc.save(str(path))
    return hits, n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Change one phrase everywhere in a deck.")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--find", required=True)
    ap.add_argument("--replace", required=True)
    ap.add_argument("--apply", action="store_true", help="Change the files (default: list only).")
    ap.add_argument("--anywhere", action="store_true", help="Match inside words too.")
    ap.add_argument("--ignore-case", action="store_true", dest="ignore_case")
    a = ap.parse_args(argv)
    _rulings.announce(out=a.out)
    if not a.find.strip():
        print("ERROR: --find is empty.")
        return 2
    rx = _pattern(a.find, a.anywhere, a.ignore_case)
    total, changed = 0, []
    by_kind: dict[str, int] = {}
    for kind, f in targets(a.out):
        suf = f.suffix.lower()
        try:
            if suf == ".docx":
                hits, n = scan_docx(f, rx, a.replace if a.apply else None)
            else:
                raw = f.read_bytes().decode("utf-8", errors="replace")
                html_mode = suf in (".html", ".htm")
                hits = _text_hits(raw, rx, html_mode)
                n = 0
                if a.apply and hits:
                    new, n = _replace_text(raw, rx, a.replace, html_mode)
                    f.write_bytes(new.encode("utf-8"))
        except Exception as exc:
            print(f"  WARN: {f}: not read ({type(exc).__name__}: {exc})")
            continue
        if not hits:
            continue
        total += len(hits)
        by_kind[kind] = by_kind.get(kind, 0) + len(hits)
        print(f"{kind}: {f} ({len(hits)})")
        for ln, ctx in hits[:12]:
            print(f"    {ln}: ...{ctx}...")
        if len(hits) > 12:
            print(f"    ... {len(hits) - 12} more")
        if a.apply:
            changed.append((kind, f))
    if not total:
        print(f"\"{a.find}\" is in none of the deck's files.")
        return 0
    summary = ", ".join(f"{v} in the {k}" for k, v in sorted(by_kind.items()))
    if not a.apply:
        print(f"\nDRY RUN: {total} place(s) ({summary}). Nothing changed. Show the user this list; "
              "to change them all:")
        print(f"  py -3 scripts/replace_phrase.py --out \"{a.out}\" --find \"{a.find}\" "
              f"--replace \"{a.replace}\" --apply")
        return 0
    print(f"\n[ok] \"{a.find}\" -> \"{a.replace}\" in {len(changed)} file(s) ({summary}).")
    kinds = {k for k, _f in changed}
    print("Next:")
    if "brief" in kinds:
        print("  - The brief changed: run storyline-helper's quality gate on the change and "
              "seal it again (seal_brief.py), then emit_dot_dash.py so the storyline files match.")
    designs = sorted({f.parent.name for k, f in changed if k == "design"})
    if designs:
        nums = ",".join(str(int(d.split("_")[1])) for d in designs)
        print(f"  - Designs changed on slide(s) {nums}: render each changed sketch again "
              "(render_html.py). For picked slides, record it as your edit with the user's "
              f"wording: py -3 scripts/record_picks.py --out \"{a.out}\" --edits-done "
              f"--edited-by-parent \"N: '{a.find}' -> '{a.replace}' (the user's words)\" "
              "(one per slide); the pipeline converts them again.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
