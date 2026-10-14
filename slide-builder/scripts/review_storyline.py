#!/usr/bin/env python3
"""review_storyline.py: the storyline panel at the top of REVIEW.html.

Owner's decision (2026-10-13): the panel shows the storyline the user
approved, as written, not a rebuild from the brief. The brief's bullets are
the designers' instructions ("Supporting points:", "SECTION LIST, show all six
sections..."), and the old panel printed them, plus a "Slide N —" prefix and
every headline twice, so the owner read "Claude speak" where his prose
storyline should have been.

Where the file comes from: prep records it (build_deck.py, _meta.json
["storyline"]: path, size, last-changed time, fingerprint) from the brief's
front matter line `approved_storyline: <path>` (emit_dot_dash.py writes it;
whoever writes a prose storyline by hand sets it) or build_deck.py
--storyline. Nothing is searched for by name or date: one session held 15
files that looked like the storyline.

How it is shown: inline (it prints and Ctrl+F finds it), with the file's own
styles dropped and only a short list of plain tags kept (headings,
paragraphs, lists, bold and italic, tables), with no scripts and no on*
handlers; REVIEW's own CSS styles it under .sl-embed. A .md file is turned
into the same simple HTML. A Word file is not converted: the panel links to it.

One-line warnings: the file is missing; it changed after prep; the brief was
changed after it; a storyline headline is worded differently on a slide (by
text, not slide number: close matches show both wordings), or is on no slide.
Slides with no storyline headline (cover, agenda, dividers) are never flagged.

With no recorded storyline, the panel shows the slide headlines only, one
plain line each in order, after the deck's governing thought once.

check_panel() runs after REVIEW.html is written: the panel's text must equal
the source text, with no ALL CAPS designer label, no "Supporting points:" and
no em-dash; otherwise build_review.py stops (exit 6) with what to fix.
"""
from __future__ import annotations

import difflib
import hashlib
import html
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

START = "<!--SL-STORYLINE-START-->"
END = "<!--SL-STORYLINE-END-->"

# Kept tags (only their class attribute survives). Everything else loses its
# tags but keeps its text, except DROP_WITH_TEXT, which goes entirely.
SAFE_TAGS = {"h1", "h2", "h3", "h4", "p", "ul", "ol", "li", "b", "i", "em", "strong",
             "br", "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption",
             "div", "span", "blockquote", "hr", "sup", "sub", "small", "u"}
VOID = {"br", "hr"}
DROP_WITH_TEXT = {"script", "style", "head", "title", "noscript", "template", "iframe",
                  "object", "embed", "svg", "math", "button", "form", "select", "textarea"}
BLOCK = {"h1", "h2", "h3", "h4", "p", "li", "div", "tr", "blockquote", "caption", "br",
         "table", "ul", "ol", "hr"}

DESIGNER_LABEL_RE = re.compile(r"\b[A-Z][A-Z0-9&/'’]+(?:\s+[A-Z][A-Z0-9&/'’]+)+\s*[—–:]")
SUPPORTING_RE = re.compile(r"supporting points\s*:", re.I)
EM_DASH = "—"


# ---------------------------------------------------------------- cleaning
class _Clean(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.drop = 0
        self.stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in DROP_WITH_TEXT:
            if tag not in VOID:
                self.drop += 1
            return
        if self.drop or tag not in SAFE_TAGS:
            return
        cls = next((v for k, v in attrs if k.lower() == "class" and v), "")
        cls = re.sub(r"[^\w\- ]", "", cls).strip()
        self.out.append(f'<{tag} class="{cls}">' if cls else f"<{tag}>")
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() in self.stack and tag.lower() not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in DROP_WITH_TEXT:
            self.drop = max(0, self.drop - 1)
            return
        if self.drop or tag not in SAFE_TAGS or tag in VOID:
            return
        if tag in self.stack:
            while self.stack:
                t = self.stack.pop()
                self.out.append(f"</{t}>")
                if t == tag:
                    break

    def handle_data(self, data):
        if not self.drop:
            self.out.append(html.escape(data, quote=False))

    def result(self) -> str:
        while self.stack:
            self.out.append(f"</{self.stack.pop()}>")
        return "".join(self.out)


def clean_html(source: str) -> str:
    """The file's body with only safe tags (class kept), no scripts, no styles,
    no event handlers, no links."""
    m = re.search(r"<body[^>]*>([\s\S]*)</body>", source, re.I)
    body = m.group(1) if m else source
    c = _Clean()
    c.feed(body)
    c.close()
    return c.result()


def _inline_md(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return s


def md_to_html(text: str) -> str:
    """A small markdown subset to simple HTML: headings, paragraphs, bullet and
    numbered lists (one level of nesting), bold and italic. Front matter goes."""
    text = text.replace("\r\n", "\n").lstrip("﻿")
    text = re.sub(r"\A---\n[\s\S]*?\n---\n", "", text)
    out: list[str] = []
    para: list[str] = []
    lists: list[tuple[str, int]] = []      # (tag, indent)

    def close_para():
        if para:
            out.append("<p>" + _inline_md(" ".join(para)) + "</p>")
            para.clear()

    def close_lists(to_indent: int = -1):
        while lists and lists[-1][1] > to_indent:
            out.append(f"</{lists.pop()[0]}>")

    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            close_para()
            close_lists()
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", line)
        li = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
        if h:
            close_para(); close_lists()
            lvl = min(4, len(h.group(1)))
            out.append(f"<h{lvl}>{_inline_md(h.group(2).strip())}</h{lvl}>")
        elif re.match(r"^\s*(---|\*\*\*|___)\s*$", line):
            close_para(); close_lists()
            out.append("<hr>")
        elif li:
            close_para()
            ind = len(li.group(1).replace("\t", "    "))
            tag = "ol" if li.group(2)[0].isdigit() else "ul"
            if not lists or ind > lists[-1][1]:
                out.append(f"<{tag}>")
                lists.append((tag, ind))
            else:
                close_lists(ind)
                if not lists:
                    out.append(f"<{tag}>")
                    lists.append((tag, ind))
            out.append(f"<li>{_inline_md(li.group(3).strip())}</li>")
        else:
            if lists:
                close_lists()
            para.append(line.strip())
    close_para()
    close_lists()
    return "\n".join(out)


def text_of(fragment: str) -> str:
    """Visible text of an HTML fragment, one line per block, whitespace tidied."""
    s = re.sub(r"<(script|style)[\s\S]*?</\1>", "", fragment, flags=re.I)
    s = re.sub(r"<br\s*/?>|</(p|li|div|h\d|tr|caption|blockquote|summary)>|<hr\s*/?>",
               "\n", s, flags=re.I)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    lines = [" ".join(ln.split()) for ln in s.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def _norm_words(t: str) -> str:
    return " ".join(t.split())


# ---------------------------------------------------------------- headlines
def storyline_headlines(fragment: str, is_md: bool, md_text: str = "") -> list[str]:
    """The storyline's headline lines: <p class="dot"> (hand-written house
    style), .dd-gov (emit_dot_dash.py), or in markdown a line that is bold
    and nothing else ("**3. Headline**")."""
    found: list[str] = []
    if is_md:
        for m in re.finditer(r"^\s*(?:[-*]\s+)?\*\*(.+?)\*\*\s*$", md_text, re.M):
            found.append(m.group(1))
    else:
        for m in re.finditer(r'<(\w+) class="[^"]*\b(?:dot|dd-gov)\b[^"]*">([\s\S]*?)</\1>',
                             fragment):
            found.append(text_of(m.group(2)))
    out = []
    for t in found:
        t = re.sub(r"^\s*\d+[.)]\s*", "", " ".join(t.split())).strip()
        if t and not t.lower().startswith("(cover"):
            out.append(t)
    return out


def _key(t: str) -> str:
    return " ".join(re.sub(r"[^\w%$.\s]", " ", t.lower()).split()).rstrip(".")


def drift_warnings(story_heads: list[str], cards: list[tuple[int, str]]) -> list[str]:
    """Storyline headlines against the slide cards' headlines, by text."""
    out: list[str] = []
    if not story_heads or not cards:
        return out
    for sh in story_heads:
        best_n, best_t, best_r = None, "", 0.0
        for n, t in cards:
            r = difflib.SequenceMatcher(None, _key(sh), _key(t)).ratio()
            if r > best_r:
                best_n, best_t, best_r = n, t, r
        if best_r >= 0.999:
            continue
        if best_r >= 0.6:
            out.append(f'Slide {best_n} headline differs from the storyline. Storyline: '
                       f'"{sh}". Slide: "{best_t}".')
        else:
            out.append(f'Storyline headline not on any slide: "{sh}".')
    return out


# ---------------------------------------------------------------- the panel
def _when(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def build_panel(meta: Optional[dict], storyline: dict, slides: list) -> dict:
    """{"html": the <details> panel, "expected": the text the panel must
    show, "source": what it came from, "warnings": [...]}"""
    meta = meta or {}
    rec = meta.get("storyline") or {}
    warnings: list[str] = []
    cards = [(s.get("n"), (s.get("title") or "").strip()) for s in slides if s.get("title")]
    body = ""
    label = ""
    expected = None
    source = "headlines"
    path = Path(rec["path"]) if rec.get("path") else None
    if path is not None:
        name = html.escape(path.name)
        if not path.exists():
            warnings.append(f"The approved storyline file is missing: {path}. Showing the "
                            "slide headlines instead. Fix approved_storyline in the brief and "
                            "prep again.")
        elif path.suffix.lower() in (".docx", ".doc"):
            label = f"Approved storyline: {path.name}, last changed {_when(path.stat().st_mtime)}"
            warnings.append("The approved storyline is a Word file, so it is not shown here: "
                            f'<a href="{html.escape(path.resolve().as_uri())}">open {name}</a>.')
        else:
            raw = path.read_bytes()
            text = raw.decode("utf-8", errors="replace")
            is_md = path.suffix.lower() in (".md", ".markdown", ".txt")
            frag = md_to_html(text) if is_md else clean_html(text)
            body = f'<div class="sl-embed">{frag}</div>'
            expected = text_of(frag)
            source = str(path)
            label = f"Approved storyline: {path.name}, last changed {_when(path.stat().st_mtime)}"
            if rec.get("sha256") and hashlib.sha256(raw).hexdigest() != rec["sha256"]:
                warnings.append("This storyline file changed after the slides were prepped "
                                f"(prep saw it at {_when(rec.get('mtime') or 0)}). Check the "
                                "slides still follow it.")
            bp = Path(meta.get("brief") or "")
            if meta.get("brief") and bp.exists() and bp.stat().st_mtime > path.stat().st_mtime + 1:
                warnings.append(f"The brief was changed after the storyline (brief "
                                f"{_when(bp.stat().st_mtime)}, storyline "
                                f"{_when(path.stat().st_mtime)}). Check they still agree.")
            warnings += drift_warnings(storyline_headlines(frag, is_md, text), cards)
    if expected is None:
        # Headlines only: the deck's governing thought once, then one plain
        # line per slide in order. No "Slide N", no bullets, no repeats.
        gov = (storyline.get("governing") or "").strip()
        by_n = {s["n"]: s for s in storyline.get("slides") or []}
        lines: list[str] = []
        for s in slides:
            t = ((by_n.get(s.get("n")) or {}).get("title") or s.get("title") or "").strip()
            if t and t != f"Slide {s.get('n')}" and (not lines or lines[-1] != t):
                lines.append(t)
        parts = []
        if gov:
            parts.append(f'<p class="sl-gov">{html.escape(gov)}</p>')
        parts.append('<ol class="sl-heads">' + "".join(
            f"<li>{html.escape(t)}</li>" for t in lines) + "</ol>")
        body = '<div class="sl-embed">' + "".join(parts) + "</div>"
        expected = "\n".join(([gov] if gov else []) + lines)
        label = label or "The slide headlines, in order (no approved storyline file recorded)"
    warn_html = "".join(f'<div class="sl-warn">{w if "<a " in w else html.escape(w)}</div>'
                        for w in warnings)
    panel = (f'\n<details class="storyline-section">\n<summary><span class="storyline-summary-text">'
             f'&#9654; {html.escape(label)}: click to open</span></summary>\n'
             f'<div class="storyline-body">{warn_html}{START}{body}{END}</div>\n</details>\n')
    return {"html": panel, "expected": expected, "source": source, "warnings": warnings}


def check_panel(page_html: str, expected: str) -> list[str]:
    """Problems with the panel as written into REVIEW.html (empty = fine)."""
    i, j = page_html.find(START), page_html.find(END)
    if i < 0 or j < 0:
        return ["the storyline panel is missing from REVIEW.html"]
    got = text_of(page_html[i + len(START): j])
    problems = []
    if _norm_words(got) != _norm_words(expected or ""):
        problems.append("the panel's text is not the storyline's text word for word")
    labels = DESIGNER_LABEL_RE.findall(got)
    if labels:
        problems.append(f"{len(labels)} ALL CAPS designer label(s), for example "
                        f'"{labels[0].strip()}"')
    if SUPPORTING_RE.search(got):
        problems.append('"Supporting points:" (a note for the designer)')
    if EM_DASH in got:
        problems.append(f"{got.count(EM_DASH)} em-dash(es)")
    return problems
