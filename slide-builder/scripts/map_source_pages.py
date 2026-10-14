#!/usr/bin/env python3
"""map_source_pages.py: map every slide to an earlier deck's page, approved once.

The biggest single cause of repeated steers on two decks (about 35 of them)
was "use the page you already have": the draft, the v2 deck, the NVIDIA deck.
The chat had the files; a listing did not help. A pinned page did: after the
one-off pin_v2.py there was one re-steer. This makes that mapping a standard
step, before the build, approved in ONE answer per deck (owner's decisions,
2026-10-14). The map is data (`_session\\page_map.json` and the brief's pin
lines); it has no page of its own: the user should not open several HTML
files. render_section() returns the "Pages you gave us" section that
REVIEW.html shows under the storyline (and a later single Slide Lab page shows
in its Storyline tab):

  1. propose   reads the brief and every earlier deck given, proposes for each
               slide id the source page it most likely is (or "new"), renders
               the pages into `_session\\page_map\\` and prints the list: every
               slide, its proposed page (and picture), the next candidates.
  2. set       the user's changes ("risks: page 44", "leaders: new").
  3. approve   with the user's words, exactly as typed (checked against the
               session transcript): writes each slide's `**Pinned source
               page:** <file> slide N` line into the brief (removes it for
               "new"). Prep then tells the designer that option A reproduces
               that page, and the copied-page check (source_ledger.py) checks
               its figures. The seal does not count these lines.

  py -3 scripts/map_source_pages.py propose --brief <brief.md> --from <deck.pptx> [--from <deck.pdf>]
  py -3 scripts/map_source_pages.py set --brief <brief.md> risks=44 leaders=new "exec-summary=<file>:3"
  py -3 scripts/map_source_pages.py approve --brief <brief.md> --approved-in-chat "<their words>"
  py -3 scripts/map_source_pages.py show --brief <brief.md>

A page number alone in `set` means the first deck given; `<file>:<page>` names
another. `--no-pictures` skips the rendering (the map then shows text only).
"""
from __future__ import annotations

import argparse
import html
import json
import math
import re
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _rulings  # noqa: E402
import slide_ids  # noqa: E402

MAP_JSON = "page_map.json"
PIC_DIR = "page_map"
PIN_LINE_RE = re.compile(r"^\*\*(?:Pinned source page|Supplied page):?\*\*.*$", re.M | re.I)
PICTURE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
MIN_SCORE = 0.12       # below this a slide is proposed as a new design (tuned on the Leo deck)
STOP = slide_ids.STOP | set("""slide page source note notes kinfield deck chart total year
years percent million billion share""".split())


# ------------------------------------------------------------------ reading

def _tokens(text: str) -> list[str]:
    t = (text or "").lower().replace("’", "'")
    words = [w for w in re.findall(r"[a-z][a-z0-9'-]+", t) if len(w) >= 3 and w not in STOP]
    nums = [re.sub(r"[,\s]", "", n) for n in re.findall(r"\$?\d[\d,.]*\s?[%xkmb]?", t)
            if len(re.sub(r"\D", "", n)) >= 2]
    return words + ["#" + n for n in nums]


def source_pages(path: Path) -> list[dict]:
    """[{page, text}] of every page of an earlier deck (pptx, pdf, picture)."""
    suf = path.suffix.lower()
    pages = []
    if suf == ".pptx":
        from pptx import Presentation
        import _extract
        for i, s in enumerate(Presentation(str(path)).slides, 1):
            try:
                surfaces, _u = _extract.walk_slide(s, i)
                text = "\n".join(x.get("text", "") for x in surfaces)
            except Exception:
                text = ""
            pages.append({"page": i, "text": text})
    elif suf == ".pdf":
        import source_ledger
        n = source_ledger._pdf_pages(path) or 0
        for i in range(1, n + 1):
            got = source_ledger._pdf_text_page(path, i)
            pages.append({"page": i, "text": "\n".join(got[0]) if got else ""})
    elif suf in PICTURE_SUFFIXES:
        pages.append({"page": 1, "text": path.stem.replace("_", " ")})
    else:
        raise SystemExit(f"ERROR: {path.name}: an earlier deck must be a PowerPoint file, a "
                         "PDF or a picture; save it as a PDF and run this again.")
    return pages


def brief_slides(brief: Path) -> list[dict]:
    import build_deck
    text = brief.read_text(encoding="utf-8")
    _fm, body = build_deck.extract_front_matter(text.replace("\r\n", "\n"))
    out = []
    for n, title, block in build_deck.split_slide_blocks(body):
        f = lambda labels: build_deck.extract_field(block, labels)  # noqa: E731
        sid = f(("slide id",)).strip("` ").lower()
        gist = " ".join([title, f(build_deck.FIELD_LABELS["governing_thought"]),
                         f(build_deck.FIELD_LABELS["so_what"]),
                         f(build_deck.FIELD_LABELS["evidence_content"])])
        out.append({"n": n, "id": sid, "title": title or f(build_deck.FIELD_LABELS["title"]),
                    "text": gist, "type": f(build_deck.FIELD_LABELS["archetype"]),
                    "pin": f(build_deck.FIELD_LABELS["pinned_source_page"])})
    return out


# ------------------------------------------------------------------ matching

def propose(slides: list[dict], decks: list[tuple[Path, list[dict]]]) -> None:
    """Fill slide['proposal'] and slide['candidates'] (TF-IDF cosine on words
    and figures; each source page proposed for at most one slide)."""
    docs = []
    for path, pages in decks:
        for pg in pages:
            docs.append({"file": str(path), "page": pg["page"],
                         "tf": Counter(_tokens(pg["text"])), "text": pg["text"]})
    n_docs = max(len(docs), 1)
    df: Counter = Counter()
    for d in docs:
        df.update(set(d["tf"]))
    idf = {w: math.log((1 + n_docs) / (1 + c)) + 1 for w, c in df.items()}

    def vec(tf):
        v = {w: (1 + math.log(c)) * idf.get(w, math.log(1 + n_docs) + 1) for w, c in tf.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {w: x / norm for w, x in v.items()}

    dvecs = [vec(d["tf"]) for d in docs]
    pairs = []
    for s in slides:
        sv = vec(Counter(_tokens(s["text"])))
        scored = []
        for i, dv in enumerate(dvecs):
            sc = sum(x * dv.get(w, 0.0) for w, x in sv.items())
            scored.append((sc, i))
        scored.sort(reverse=True)
        s["candidates"] = [{"file": docs[i]["file"], "page": docs[i]["page"],
                            "score": round(sc, 3)} for sc, i in scored[:4] if sc > 0]
        for sc, i in scored[:6]:
            pairs.append((sc, s["n"], i))
    taken_pages, taken_slides = set(), set()
    best = {}
    for sc, n, i in sorted(pairs, reverse=True):
        if sc < MIN_SCORE or n in taken_slides or i in taken_pages:
            continue
        best[n] = (sc, i)
        taken_slides.add(n)
        taken_pages.add(i)
    for s in slides:
        if s["n"] in best:
            sc, i = best[s["n"]]
            s["proposal"] = {"file": docs[i]["file"], "page": docs[i]["page"],
                             "score": round(sc, 3), "how": "proposed"}
        else:
            s["proposal"] = None


# ------------------------------------------------------------------ pictures

def render_pictures(sd: Path, decks: list[Path]) -> dict[str, str]:
    """{file: folder of slide_NN.png}. Rendered once per deck (PowerPoint on
    Windows, read-only and windowless; LibreOffice otherwise)."""
    out = {}
    for d in decks:
        folder = sd / PIC_DIR / re.sub(r"[^A-Za-z0-9_-]+", "_", d.stem)[:40]
        folder.mkdir(parents=True, exist_ok=True)
        suf = d.suffix.lower()
        try:
            if suf in PICTURE_SUFFIXES:
                shutil.copy2(d, folder / f"slide_01{suf}")
            elif suf == ".pdf":
                sys.path.insert(0, str(HERE.parents[1] / "slide-qc" / "scripts"))
                import render_slides
                render_slides._pdf_to_pngs(d, folder, 50, quiet=True)
            else:
                sys.path.insert(0, str(HERE.parents[1] / "slide-qc" / "scripts"))
                import render_slides
                render_slides.render(d, folder, dpi=50, quiet=True)
            out[str(d)] = str(folder)
        except Exception as exc:
            print(f"  WARN: could not draw the pages of {d.name} ({type(exc).__name__}: {exc}); "
                  "the map shows its text only.")
    return out


def _pic(folder: str | None, page: int) -> str:
    if not folder:
        return ""
    for ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"):
        p = Path(folder) / f"slide_{page:02d}{ext}"
        if p.exists():
            return p.as_uri()
    return ""


# ------------------------------------------------------------------ the section

def load_map(sd: Path) -> dict | None:
    """The deck's page map (data), or None when there is none."""
    try:
        return json.loads((Path(sd) / MAP_JSON).read_text(encoding="utf-8"))
    except Exception:
        return None


def render_section(sd: Path, m: dict | None = None) -> str:
    """The "Pages you gave us" section, for another page to embed (owner's
    direction, 2026-10-14: no page of its own; REVIEW.html shows it under the
    storyline, and a later single Slide Lab page shows it in its Storyline
    tab). One row per supplied page: its picture, and the slide it goes to or
    "not used". Empty string when the deck has no page map."""
    m = m if m is not None else load_map(sd)
    if not m:
        return ""
    pics = m.get("pictures") or {}
    texts = m.get("page_text") or {}
    to_slide = {}
    for s in m.get("slides") or []:
        pr = s.get("proposal")
        if pr:
            to_slide[(pr["file"], int(pr["page"]))] = s
    rows = []
    for d in m.get("decks") or []:
        n_pages = sum(1 for k in texts if k.startswith(d + "#")) or \
            max([pg for (f, pg) in to_slide if f == d] or [0])
        for pg in range(1, n_pages + 1):
            s = to_slide.get((d, pg))
            uri = _pic(pics.get(d), pg)
            thumb = (f'<img src="{uri}" style="width:160px;border:1px solid #d0d5dd;">' if uri else
                     '<span style="color:#667085;font-size:11px;">'
                     + html.escape((texts.get(f"{d}#{pg}") or "")[:120]) + "</span>")
            where = (f"<b>Slide {s['n']} ({html.escape(s['id'] or '')})</b>: option A copies this page"
                     + (" (your choice)" if (s.get("proposal") or {}).get("how") == "set" else "")
                     if s else '<span style="color:#667085;">not used</span>')
            style = "" if s else ' style="opacity:0.6;"'
            rows.append(f"<tr{style}><td style='padding:4px 8px;vertical-align:top;'>"
                        f"{html.escape(Path(d).name)} p{pg}</td><td style='padding:4px 8px;'>{thumb}</td>"
                        f"<td style='padding:4px 8px;vertical-align:top;'>{where}</td></tr>")
    new = [s for s in m.get("slides") or [] if not s.get("proposal")]
    new_line = ("<p>New designs (no earlier page): "
                + ", ".join(f"Slide {s['n']} ({html.escape(s['id'] or '')})" for s in new) + "</p>"
                if new else "")
    ap = m.get("approved")
    state = (f"<p style='color:#067647;'>Approved {html.escape(ap['at'][:16].replace('T', ' '))}: "
             f"&ldquo;{html.escape(ap['words'])}&rdquo;</p>" if ap else
             "<p style='color:#b42318;'><b>Not approved yet.</b> Tell the chat "
             "&ldquo;approved&rdquo;, or what to change (for example &ldquo;risks: page 44, "
             "leaders: new&rdquo;). Nothing is pinned until you approve.</p>")
    used = len(to_slide)
    return (f'<details class="page-map-section" style="margin:8px 0;"{"" if ap else " open"}>'
            f"<summary><b>Pages you gave us</b>: {used} used, as option A of the slide named "
            "</summary>"
            f"{state}{new_line}"
            "<table style='border-collapse:collapse;font-size:13px;'>"
            "<tr><th style='text-align:left;padding:4px 8px;'>Page</th><th></th>"
            "<th style='text-align:left;padding:4px 8px;'>Goes to</th></tr>"
            + "".join(rows) + "</table></details>")


def print_map(m: dict) -> None:
    """The map as plain lines, for the chat to show the user."""
    pics = m.get("pictures") or {}
    for s in m["slides"]:
        p = s.get("proposal")
        if p:
            pic = _pic(pics.get(p["file"]), p["page"])
            pic = f"  picture: {Path(pic.replace('file:///', '')).as_posix()}" if pic else ""
            others = ", ".join(f"p{c['page']}" for c in (s.get("candidates") or [])
                               if (c["file"], c["page"]) != (p["file"], p["page"]))
            print(f"  {slide_ids.label(s['n'], s['id'])}: {Path(p['file']).name} page {p['page']} "
                  f"(match {p['score']:.2f}{', set by the user' if p.get('how') == 'set' else ''})"
                  + (f"; next candidates {others}" if others else "") + pic)
        else:
            print(f"  {slide_ids.label(s['n'], s['id'])}: new design")


# ------------------------------------------------------------------ commands

def _load(sd: Path) -> dict:
    p = sd / MAP_JSON
    if not p.exists():
        raise SystemExit(f"ERROR: no page map yet ({p}). Run propose first.")
    return json.loads(p.read_text(encoding="utf-8"))


def _save(sd: Path, m: dict) -> None:
    (sd / MAP_JSON).write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_propose(a) -> int:
    brief = a.brief.resolve()
    sd = _rulings.session_dir(brief=brief)
    sd.mkdir(parents=True, exist_ok=True)
    added, ids, problems = slide_ids.assign(brief)
    if problems:
        print("ERROR: fix the slide ids first: " + "; ".join(problems))
        return 3
    if added:
        print(f"  {len(added)} slide id(s) added to the brief first (slide_ids.py).")
    decks = [Path(d).resolve() for d in a.decks]
    missing = [str(d) for d in decks if not d.is_file()]
    if missing:
        print("ERROR: not found: " + "; ".join(missing))
        return 2
    read = [(d, source_pages(d)) for d in decks]
    slides = brief_slides(brief)
    propose(slides, read)
    page_text = {f"{d}#{pg['page']}": pg["text"][:600] for d, pages in read for pg in pages}
    m = {"schema": 1, "brief": str(brief), "decks": [str(d) for d in decks],
         "at": datetime.now().isoformat(timespec="seconds"),
         "slides": [{k: s.get(k) for k in ("n", "id", "title", "proposal", "candidates")}
                    for s in slides],
         "page_text": page_text, "approved": None}
    if not a.no_pictures:
        print("PowerPoint may pause for a few seconds while Slide Lab renders slides; "
              "editing in PowerPoint during that time slows the build.")
        m["pictures"] = render_pictures(sd, decks)
    _save(sd, m)
    n_copy = sum(1 for s in m["slides"] if s["proposal"])
    print(f"[ok] page map proposed: {n_copy} of {len(slides)} slide(s) copy an earlier page, "
          f"{len(slides) - n_copy} are new designs.")
    print_map(m)
    print("Next: show the user this whole list in ONE message (with the pictures of the "
          "proposed pages) and WAIT for their answer. No separate page opens: REVIEW.html "
          "shows the map later under the storyline (\"Pages you gave us\").")
    print("Their changes: py -3 scripts/map_source_pages.py set --brief \"%s\" <id>=<page> "
          "<id>=new ..." % brief)
    print("Their approval: py -3 scripts/map_source_pages.py approve --brief \"%s\" "
          "--approved-in-chat \"<their words, exactly>\"" % brief)
    return 0


def cmd_set(a) -> int:
    brief = a.brief.resolve()
    sd = _rulings.session_dir(brief=brief)
    m = _load(sd)
    by_id = {s["id"]: s for s in m["slides"]}
    for item in a.changes:
        sid, _, val = item.partition("=")
        sid, val = sid.strip().lower(), val.strip()
        if sid not in by_id:
            print(f"ERROR: no slide id {sid!r}; the ids: {', '.join(by_id)}")
            return 3
        if val.lower() in ("new", "none", "-"):
            by_id[sid]["proposal"] = None
            continue
        f, _, pg = val.rpartition(":")
        if not f:
            f = m["decks"][0]
        else:
            hits = [d for d in m["decks"] if Path(d).name.lower() == Path(f).name.lower()
                    or str(Path(f).resolve()) == d]
            if not hits:
                print(f"ERROR: {f} is not one of the earlier decks of this map: "
                      + ", ".join(Path(d).name for d in m["decks"]))
                return 3
            f = hits[0]
        if not pg.strip().isdigit():
            print(f"ERROR: {item!r}: write <id>=<page>, <id>=<file>:<page> or <id>=new")
            return 2
        by_id[sid]["proposal"] = {"file": f, "page": int(pg), "score": 1.0, "how": "set"}
    m["approved"] = None
    _save(sd, m)
    print("[ok] map changed; show the user the whole list again and wait for their approval:")
    print_map(m)
    return 0


def _write_pins(brief: Path, m: dict) -> tuple[int, int]:
    raw = brief.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n")
    want = {s["id"]: s.get("proposal") for s in m["slides"] if s["id"]}
    pinned = removed = 0
    bl = sorted(slide_ids.blocks(text), key=lambda b: b["header_end"], reverse=True)
    for b in bl:
        if b["id"] not in want:
            continue
        seg = text[b["header_end"]:b["end"]]
        p = want[b["id"]]
        if p:
            line = f"**Pinned source page:** {p['file']} slide {p['page']}"
            if PIN_LINE_RE.search(seg):
                seg = PIN_LINE_RE.sub(lambda _m: line, seg, count=1)
            else:
                idm = slide_ids.ID_LINE_RE.search(seg)
                at = idm.end() if idm else 0
                seg = seg[:at] + f"\n\n{line}" + seg[at:]
            pinned += 1
        elif PIN_LINE_RE.search(seg):
            seg = re.sub(r"\n*" + PIN_LINE_RE.pattern, "", seg, count=1, flags=re.M | re.I)
            removed += 1
        text = text[:b["header_end"]] + seg + text[b["end"]:]
    brief.write_bytes(text.replace("\n", nl).encode("utf-8"))
    return pinned, removed


def cmd_approve(a) -> int:
    brief = a.brief.resolve()
    sd = _rulings.session_dir(brief=brief)
    m = _load(sd)
    ok, why, where = _rulings.check_users_words(a.approved_in_chat, a.transcript)
    if not ok:
        print(f"REFUSED: {why}")
        print("Nothing was pinned. The user approves the page map in their own words.")
        return 4
    pinned, removed = _write_pins(brief, m)
    m["approved"] = {"words": a.approved_in_chat.strip(),
                     "at": datetime.now().isoformat(timespec="seconds"),
                     "where": f"{Path(where[0]).name}:{where[1]}"}
    _save(sd, m)
    print(f"[ok] page map approved: {pinned} slide(s) pinned to an earlier page"
          + (f", {removed} pin(s) removed (new designs)" if removed else "") + ".")
    print("     The brief's seal does not count these lines, so it stays sealed. Prep tells "
          "each pinned slide's designer that option A reproduces its page; the copied "
          "figures are checked before anything compiles.")
    print("Next: build (build_deck.py); for a deck already built, prep each changed slide "
          "again (build_deck.py --slide N).")
    return 0


def cmd_show(a) -> int:
    sd = _rulings.session_dir(brief=a.brief.resolve())
    m = _load(sd)
    print_map(m)
    print("approved" if m.get("approved") else "NOT approved yet", "|", sd / MAP_JSON)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Map every slide to an earlier deck's page.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("propose")
    p.add_argument("--brief", required=True, type=Path)
    p.add_argument("--from", dest="decks", action="append", required=True)
    p.add_argument("--no-pictures", action="store_true", dest="no_pictures")
    p = sub.add_parser("set")
    p.add_argument("--brief", required=True, type=Path)
    p.add_argument("changes", nargs="+")
    p = sub.add_parser("approve")
    p.add_argument("--brief", required=True, type=Path)
    p.add_argument("--approved-in-chat", dest="approved_in_chat", required=True)
    p.add_argument("--transcript", default=None, help=argparse.SUPPRESS)
    p = sub.add_parser("show")
    p.add_argument("--brief", required=True, type=Path)
    a = ap.parse_args(argv)
    _rulings.announce(brief=a.brief)
    return {"propose": cmd_propose, "set": cmd_set, "approve": cmd_approve,
            "show": cmd_show}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
