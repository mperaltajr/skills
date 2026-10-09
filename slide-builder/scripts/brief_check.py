#!/usr/bin/env python3
"""brief_check.py — the mechanical half of the storyline gate.

Measures what a person should not have to: whether each title and takeaway
fits its line on the registered template (with the template's own font and box
width), and whether the words follow the house content rules (no buzzwords,
facts carry the takeaway, thresholds have numbers, no "not X, it's Y"
reframes outside the one slide that names the audience's belief).

  py -3 scripts/brief_check.py --brief <brief.md>          print the issues table

seal_brief.py runs the same check and refuses to seal while issues remain,
unless the user's reasons are recorded with --accepted. Exit 0 clean, 3 issues.
Rows marked "recommendation" (a two-line title; a two-line title with a takeaway under it; a
takeaway that repeats the title, title_load.py) are shown but never stop a
seal: the owner's rule of 2026-10-08 is a recommendation, not a hard stop.

Why: on the 2026-10-02 showcase build, 5 of 10 titles wrapped with one word on
line 2 and 4 takeaways wrapped, although every one passed the old "under 12
words / 130 characters" rules; those were all six quality-check findings. And
only 2 of 10 takeaways carried a number.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
BANNED_MD = HERE.parent / "reference" / "banned-words.md"

THRESHOLD_WORDS = ("target", "threshold", "significant", "substantial",
                   "meaningful", "material")


def _load_words():
    text = BANNED_MD.read_text(encoding="utf-8")

    def block(name):
        m = re.search(rf"<!-- {name}:start -->(.*?)<!-- {name}:end -->", text, re.S)
        return [ln.strip() for ln in (m.group(1) if m else "").splitlines() if ln.strip()]
    banned = block("banned")
    judge = [re.sub(r"\s*\(.*\)$", "", j) for j in block("judge")]
    return banned, judge


def _word_re(term: str) -> re.Pattern:
    if term.endswith("*"):
        return re.compile(r"\b" + re.escape(term[:-1]) + r"\w*", re.I)
    return re.compile(r"\b" + re.escape(term) + r"\b", re.I)


def _template_metrics(template: str | None, layout: str | None):
    """(ttf, title_pt, title_w, sub_pt, sub_w) for the brief's template, or None."""
    if not template:
        return None
    try:
        import _paths as _p
        import yaml
        from _chrome_schema import (load_chrome_yml, canonical_subtitle_box,
                                    CANONICAL_SUBTITLE_FONT_PT, _find_brand_ttf)
        tpl = Path(template)
        chrome = load_chrome_yml(_p.chrome_yml(tpl))
        brand = yaml.safe_load(_p.brand_yml(tpl).read_text(encoding="utf-8")) or {}
        lc = chrome.layouts.get(layout or "") or next(
            (l for l in chrome.layouts.values() if l.layout_class == "body-canonical"), None)
        from _chrome_schema import (template_title_is_bold, title_measure_ttf,
                                    pick_family_faces)
        sidecar = Path(_p.template_sidecar_dir(tpl))

        def _rel(v):
            # brand.yml records bundled fonts by file name, relative to itself
            if not v:
                return None
            q = Path(str(v))
            return str(q if q.is_absolute() else sidecar / q)
        regular = (getattr(lc, "title_font_ttf_path", None) or _rel(brand.get("title_font_ttf_path"))
                   or pick_family_faces(brand.get("font_heading") or "").get("regular")
                   or _find_brand_ttf(brand.get("font_heading")))
        build_copy = sidecar / "build-template.pptx"
        bold = template_title_is_bold(build_copy if build_copy.exists() else tpl)
        ttf = title_measure_ttf(regular, _rel(brand.get("title_font_bold_ttf_path")),
                                title_bold=bold,
                                heading_face=brand.get("theme_heading_face") or "")
        title_w = (getattr(lc, "title_box_width_px", None) or 1190) - 19
        title_pt = getattr(lc, "title_font_pt", None) or 28
        sb = getattr(lc, "subtitle", None)
        if sb is not None and getattr(sb, "w_px", None):
            sub_w = sb.w_px - 19
        elif getattr(lc, "title_box_width_px", None):
            # The free-floating takeaway spans the title's width (helpers).
            sub_w = lc.title_box_width_px - 19
        else:
            sub_w = canonical_subtitle_box().w_px - 19
        sub_pt = getattr(sb, "font_pt", None) or CANONICAL_SUBTITLE_FONT_PT
        body_ttf = (_rel(brand.get("body_font_ttf_path"))
                    or pick_family_faces(brand.get("font_body") or "").get("regular")
                    or _find_brand_ttf(brand.get("font_body")) or regular)
        return ttf, title_pt, title_w, sub_pt, sub_w, body_ttf
    except Exception:
        return None


def _lines(text, ttf, pt, width):
    from _chrome_schema import count_wrapped_lines
    try:
        return count_wrapped_lines(text, ttf, pt, width)
    except Exception:
        return None


def check(brief_path: Path) -> list[dict]:
    import build_deck as bd
    brief = bd.parse_brief(brief_path, bypass_gate=True)
    fm = brief.get("front_matter") or {}
    metrics = _template_metrics(fm.get("client_template"), fm.get("default_layout"))
    banned, judge = _load_words()
    banned_res = [(w, _word_re(w)) for w in banned + ["McKinsey", "BCG", "Bain", "MBB"]]
    judge_res = [(w, _word_re(w)) for w in judge]
    issues: list[dict] = []

    def add(n, field, problem, text, level="issue"):
        issues.append({"slide": n, "field": field, "problem": problem, "text": text,
                       "level": level})

    import title_load

    for s in brief["slides"]:
        n = s.get("slide_n")
        cover = "cover" in (s.get("archetype") or "").lower()
        title = (s.get("title") or "").strip()
        take = (s.get("so_what") or "").strip()
        evidence = s.get("evidence_content") or ""
        if metrics and not cover:
            ttf, tpt, tw, spt, sw, bttf = metrics
            tl = _lines(title, ttf, tpt, tw)
            if tl and tl > 2:
                add(n, "title", f"wraps to {tl} lines on this template (2 is the most)", title)
            elif tl == 2:
                # A two-line title is allowed (owner, 2026-10-08): a recommendation only.
                add(n, "title", "recommendation: wraps to 2 lines on this template; one line reads "
                                "better, and a lone word on line 2 looks like a mistake", title,
                    level="recommendation")
            sl = _lines(take, bttf, spt, sw)
            if sl and sl > 1:
                add(n, "takeaway", f"wraps to {sl} lines under the title", take)
            # The owner's rule (2026-10-08): a two-line title is allowed, but a
            # two-line title with a takeaway under it is heavy (and the
            # template's bottom band, when filled, makes three). A subtitle is
            # recommended only under a one-line title. Not a hard stop.
            if tl and tl >= 2 and take:
                add(n, "takeaway", "recommendation: the title wraps to 2 lines and has a takeaway "
                                   "under it; use a one-line title, or drop the takeaway",
                    take, level="recommendation")
        if not cover and title and take and title_load.repeats_title(title, take):
            share = title_load.repeat_share(title, take)
            add(n, "takeaway", f"recommendation: repeats the title ({share:.0%} of its content "
                               "words are in the title); state the number or consequence the "
                               "title does not", take, level="recommendation")
        for field, text in (("title", title), ("takeaway", take), ("bullets", evidence)):
            for w, rx in banned_res:
                if rx.search(text):
                    add(n, field, f'buzzword "{w}": replace it with the number or fact it stands for',
                        rx.search(text).group(0))
            for w, rx in judge_res:
                m = rx.search(text)
                if m and not re.search(r"\d", text[m.end():m.end() + 40]):
                    add(n, field, f'"{w}" with no number next to it: say how much, or cut it',
                        m.group(0))
        if not cover and take and not re.search(r"\d", take):
            add(n, "takeaway", "no number: state what the page's facts mean, with one of its numbers "
                               "(or give the reason there is none)", take)
        if not cover and re.search(r"\bnot\b[^.;:]{0,60}[;,]\s*(it'?s|it is|but|instead)\b|\binstead of\b",
                                   take, re.I):
            add(n, "takeaway", '"not X, it\'s Y" reframe: keep it for the one slide that names the '
                               "audience's belief, and state the fact instead elsewhere", take)
        for w in THRESHOLD_WORDS:
            for m in re.finditer(rf"\b{w}\b", evidence + " " + take, re.I):
                window = (evidence + " " + take)[max(0, m.start() - 40):m.end() + 40]
                if not re.search(r"\d|to be set|tbd", window, re.I):
                    add(n, "bullets", f'"{w}" with no number: give the number or write "(to be set)"',
                        window.strip()[:80])
                    break
    return issues


def table(issues: list[dict]) -> str:
    if not issues:
        return "No issues: every title and takeaway fits its line and the wording follows the rules."
    out = ["| Slide | Where | Problem | Text |", "|---|---|---|---|"]
    for i in issues:
        txt = i["text"].replace("|", "/").replace("\n", " ")
        out.append(f"| {i['slide']} | {i['field']} | {i['problem']} | {txt[:90]} |")
    return "\n".join(out)


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Check a brief's lengths and wording.")
    ap.add_argument("--brief", required=True, type=Path)
    a = ap.parse_args(argv)
    issues = check(a.brief)
    print(table(issues))
    return 3 if blocking(issues) else 0


def blocking(issues: list[dict]) -> list[dict]:
    """The issues that stop a seal; recommendation rows are shown, never block."""
    return [i for i in issues if i.get("level") != "recommendation"]


if __name__ == "__main__":
    sys.exit(main())
