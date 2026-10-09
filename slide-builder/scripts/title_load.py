#!/usr/bin/env python3
"""title_load.py — does a slide say the same thing three times at the top?

The owner's rule (2026-10-08): a two-line title is allowed, but a two-line
title PLUS a subtitle (the takeaway under the title) PLUS a filled bottom
takeaway band is too much. A subtitle is recommended only when the title is
one line (a recommendation, not a hard stop). Each line must add something the
others do not say.

Why: on the Flux investor deck, 18 of 33 slides had a two-line title (98 to
117 characters), a takeaway under it and the template's bottom takeaway band,
all saying roughly the same thing (the band reused up to 73% of the title's
content words).

Used by:
  - brief_check.py (storyline gate): recommendation rows, never a hard stop
  - slide-qc's check_pptx_hygiene.py (finished deck): a subtitle or band that
    repeats the title is a content Major (a wording choice for the user, never
    fixed automatically); a two-line title with a subtitle and a filled band is
    an Advisory recommendation.

  py -3 scripts/title_load.py <deck.pptx>     print what each slide carries
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# Share of the band's (or subtitle's) content words already in the title at or
# above which it "repeats the title".
REPEAT_THRESHOLD = 0.5
# A line with fewer content words than this is not judged.
MIN_WORDS = 3

STOPWORDS = frozenset("""
a an the and or but nor so yet of in on at to for from by with without into onto
over under than then that this these those it its is are was were be been being
has have had do does did can could will would shall should may might must as if
about after before between through during per via up down out off our we us you
your their they them he she his her who whom which what when where why how all
any each every more most less least very just also only not no both either
neither such own same other another one's there here while because until
""".split())

_TOKEN = re.compile(r"[a-z0-9]+(?:[.,][0-9]+)*", re.I)


def _stem(w: str) -> str:
    if w.isdigit() or any(c.isdigit() for c in w):
        return w
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def content_words(text: str) -> set[str]:
    """Lower-cased content words (stopwords removed, light stemming); numbers
    count as content words."""
    out = set()
    for m in _TOKEN.finditer((text or "").lower()):
        w = m.group(0).strip(".,")
        if not w or w in STOPWORDS or (len(w) < 2 and not w.isdigit()):
            continue
        out.add(_stem(w))
    return out


def repeat_share(title: str, other: str) -> float:
    """Share of `other`'s content words that the title already says (0 to 1).
    1.0 = every content word of the line is in the title: it adds nothing."""
    t, o = content_words(title), content_words(other)
    if len(o) < MIN_WORDS or not t:
        return 0.0                  # too short to judge ("Takeaway 1.")
    return len(t & o) / len(o)


def repeats_title(title: str, other: str) -> bool:
    return repeat_share(title, other) >= REPEAT_THRESHOLD


# ---------------------------------------------------------------------------
# Finished-deck side: find the title, the subtitle and the bottom band
# ---------------------------------------------------------------------------
EMU_PER_IN = 914400
BAND_NAME = re.compile(r"takeaway|so[-_ ]?what|bottom[-_ ]?line|key[-_ ]?message|kicker|conclusion",
                       re.I)
NOT_BAND_TEXT = re.compile(r"^\s*(sources?|notes?|footnotes?)\b|^\s*\d+\s*$|^\s*\(?\d\)|^\s*[*†‡]",
                           re.I)
NOT_BAND_NAME = re.compile(r"foot|source|note|legend|label|axis|page", re.I)


def _ph_type(sh):
    try:
        return sh.placeholder_format.type if sh.is_placeholder else None
    except Exception:
        return None


def _text(sh) -> str:
    try:
        return sh.text_frame.text.strip() if sh.has_text_frame else ""
    except Exception:
        return ""


def _title_shape(slide):
    from pptx.enum.shapes import PP_PLACEHOLDER
    for sh in slide.shapes:
        if _ph_type(sh) in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE) and _text(sh):
            return sh
    return None


def _theme_major_font(slide) -> str | None:
    try:
        master = slide.slide_layout.slide_master
        for rel in master.part.rels.values():
            if rel.reltype.endswith("/theme"):
                xml = rel.target_part.blob.decode("utf-8", "replace")
                m = re.search(r"<a:majorFont>\s*<a:latin typeface=\"([^\"]+)\"", xml)
                return m.group(1) if m else None
    except Exception:
        return None
    return None


def _title_size_and_font(slide, title) -> tuple[float, str | None, bool]:
    """(size in pt, font family or None, bold) the title draws in: its own
    runs first, then the layout's title, then the master's title style."""
    from pptx.oxml.ns import qn
    size = None
    font = None
    bold = False
    for p in title.text_frame.paragraphs:
        for r in p.runs:
            if r.font.size and not size:
                size = r.font.size.pt
            if r.font.name and not font:
                font = r.font.name
            if r.font.bold:
                bold = True
    els = []
    try:
        for sh in slide.slide_layout.placeholders:
            if sh.placeholder_format.type == title.placeholder_format.type:
                els.append(sh._element)
                break
    except Exception:
        pass
    try:
        ts = slide.slide_layout.slide_master._element.find(qn("p:txStyles"))
        if ts is not None:
            els.append(ts.find(qn("p:titleStyle")))
    except Exception:
        pass
    for el in [e for e in els if e is not None]:
        for d in el.iter(qn("a:defRPr")):
            if not size and d.get("sz"):
                size = int(d.get("sz")) / 100
            if d.get("b") == "1":
                bold = True
            lat = d.find(qn("a:latin"))
            if not font and lat is not None and not lat.get("typeface", "").startswith("+"):
                font = lat.get("typeface")
        for r in el.iter(qn("a:rPr")):
            if not size and r.get("sz"):
                size = int(r.get("sz")) / 100
    return float(size or 28), (font or _theme_major_font(slide)), bold


def title_lines(slide, title=None) -> int:
    """How many lines the title draws on: measured with the title's font when
    it is installed, else estimated from its size and box width."""
    title = title or _title_shape(slide)
    if title is None:
        return 0
    text = _text(title)
    hard = text.count("\n") + text.count("\v") + 1
    size, family, bold = _title_size_and_font(slide, title)
    width_px = max(1, int((title.width or 0) / 9525) - 19)
    lines = None
    try:
        from _chrome_schema import count_wrapped_lines, pick_family_faces, _find_brand_ttf
        faces = pick_family_faces(family or "") if family else {}
        ttf = (faces.get("bold") if bold else None) or faces.get("regular") or _find_brand_ttf(family)
        if ttf:
            lines = sum(count_wrapped_lines(part, ttf, size, width_px) or 1
                        for part in re.split(r"[\n\v]", text))
    except Exception:
        lines = None
    if lines is None:
        # about half an em per character, the usual width of a proportional face
        per_line = max(1, int(width_px * 0.75 / (size * 0.5)))
        lines = sum(max(1, -(-len(part) // per_line)) for part in re.split(r"[\n\v]", text))
    return max(lines, hard)


def slide_lines(slide, slide_w: int, slide_h: int) -> dict:
    """{"title", "title_lines", "subtitle", "band"} for one slide. The subtitle
    is the text right under the title (the takeaway Slide Lab places there);
    the band is a takeaway / so-what strip low on the slide (by its name, or a
    wide text line in the bottom third that is not the source or a note)."""
    title = _title_shape(slide)
    res = {"title": _text(title) if title is not None else "", "title_lines": 0,
           "subtitle": "", "band": ""}
    if title is None:
        return res
    res["title_lines"] = title_lines(slide, title)
    t_bottom = title.top + title.height
    from pptx.enum.shapes import PP_PLACEHOLDER
    skip = (PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.SLIDE_NUMBER, PP_PLACEHOLDER.DATE)
    sub_best = None
    band = []
    for sh in slide.shapes:
        if sh is title or _ph_type(sh) in skip:
            continue
        txt = _text(sh)
        if not txt or sh.top is None or sh.width is None:
            continue
        name = sh.name or ""
        # subtitle: starts within a third of an inch above / half an inch below
        # the title's bottom, and is wide
        if (abs(sh.top - t_bottom) <= 0.5 * EMU_PER_IN and sh.width >= 0.5 * title.width
                and sh.top < slide_h * 0.35 and not BAND_NAME.search(name)):
            if sub_best is None or abs(sh.top - t_bottom) < abs(sub_best.top - t_bottom):
                sub_best = sh
            continue
        low = sh.top >= slide_h * 0.62
        if BAND_NAME.search(name) and low:
            band.append(txt)
        elif (low and sh.width >= 0.75 * slide_w and not NOT_BAND_TEXT.search(txt)
              and not NOT_BAND_NAME.search(name)
              and not sh.is_placeholder and len(content_words(txt)) >= 4):
            band.append(txt)
    if sub_best is not None:
        res["subtitle"] = _text(sub_best)
    res["band"] = " ".join(band).strip()
    return res


def deck_findings(prs) -> list[dict]:
    """Findings in check_pptx_hygiene's shape for a finished deck."""
    out = []
    W, H = prs.slide_width, prs.slide_height
    for i, slide in enumerate(prs.slides, start=1):
        try:
            r = slide_lines(slide, W, H)
        except Exception:
            continue
        if not r["title"]:
            continue
        for where, txt in (("takeaway under the title", r["subtitle"]),
                           ("bottom takeaway band", r["band"])):
            if txt:
                share = repeat_share(r["title"], txt)
                if share >= REPEAT_THRESHOLD:
                    out.append({
                        "slide": i, "severity": "Major", "category": "repeats-title",
                        "content": True, "auto_fix": False,
                        "issue": (f"Slide {i}: the {where} repeats the title ({share:.0%} of its "
                                  f"content words are in the title): \"{txt[:90]}\". Each line "
                                  f"must add something: state the number or consequence the "
                                  f"title does not, or leave it out. A wording choice for the "
                                  f"user; not fixed automatically."),
                    })
        if r["title_lines"] >= 2 and r["subtitle"] and r["band"]:
            out.append({
                "slide": i, "severity": "Advisory", "category": "title-load",
                "content": True, "auto_fix": False,
                "issue": (f"Slide {i}: a {r['title_lines']}-line title, a takeaway under it and a "
                          f"filled bottom band. Recommended: a one-line title, or drop the "
                          f"takeaway under the title (a subtitle suits a one-line title)."),
            })
    return out


def main(argv=None) -> int:
    from pptx import Presentation
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    prs = Presentation(args[0])
    W, H = prs.slide_width, prs.slide_height
    for i, slide in enumerate(prs.slides, start=1):
        r = slide_lines(slide, W, H)
        print(f"slide {i}: title {r['title_lines']} line(s), {len(r['title'])} chars | "
              f"subtitle {'yes' if r['subtitle'] else 'no'} "
              f"(repeat {repeat_share(r['title'], r['subtitle']):.2f}) | band "
              f"{'yes' if r['band'] else 'no'} (repeat {repeat_share(r['title'], r['band']):.2f})")
    for f in deck_findings(prs):
        print(f"  {f['severity']}: {f['issue']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
