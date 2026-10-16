#!/usr/bin/env python3
"""record_storyline.py: record the Storyline tab of the one Slide Lab page.

The user edits the storyline wording in place, comments, and picks each
slide's visual (Suggestion or Must use) on tab 1 of `<deck> - Slide Lab.html`,
then presses Done and pastes the message. This records it (owner's decision,
2026-10-16):

  py -3 scripts/record_storyline.py --out <build> --message "<the whole message, exactly as pasted>"

  - checks the header line (`Slide Lab, <deck>, Storyline, code XXXX`): a
    message from another deck, another tab or an older page is refused;
  - applies every wording change ("was" / "now") to the brief, only inside
    that slide, and writes the storyline files again (the dot-dash .md, .html
    and Word file stay prose only); a storyline written by hand gets the same
    change; a sealed brief is sealed again (the user's own words, recorded);
  - writes each slide's `**Visual:** <name> | suggestion|must use`,
    `**Visual note:**` and `**Reuse:**` lines into the brief (the seal does not
    count them) and pins or unpins the supplied pages chosen in "Start from";
  - refuses the visuals while tables plus side-by-side boxes are more than a
    third of the slides and some of them are only suggestions (the tab opens
    again with the warning);
  - comments: the chat changes the storyline from them; prep then opens the
    tab again for a look.

When only one or two slides need a visual choice, the chat asks in one
question instead and records the answer:

  py -3 scripts/record_storyline.py --out <build> --approved-in-chat "<their words>" \
        [--visual "3=Table|must use"] [--designers-pick-all]

Then prep again (the command is printed): the designers start.
Exit: 0 recorded | 4 comments wait on the chat | 5 refused | 2 bad usage
"""
from __future__ import annotations

import argparse
import json
import re
import secrets
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _paths as _p  # noqa: E402
import _state  # noqa: E402
import _visuals as V  # noqa: E402
import slidelab_page as SP  # noqa: E402

HEADER_RE = re.compile(r"^#{2,3}\s+Slide\s+(\d+)\b.*$", re.M)
VIS_LINES_RE = re.compile(r"^\*\*(?:Visual|Visual note|Reuse):\*\*[^\n]*\n?", re.M | re.I)
ID_LINE_RE = re.compile(r"^\*\*Slide id:?\*\*[^\n]*$", re.M | re.I)
PIN_LINE_RE = re.compile(r"^\*\*(?:Pinned source page|Supplied page):?\*\*[^\n]*$", re.M | re.I)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ------------------------------------------------------------------ the brief

def brief_fp(text: str) -> str:
    import seal_brief
    return seal_brief._fingerprint_as_prep_reads(text)


def _spans(text: str) -> dict[int, tuple[int, int]]:
    """{slide n: (start, end)} of each slide block, header line included."""
    ms = list(HEADER_RE.finditer(text))
    out = {}
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        nxt = re.search(r"^#{1,2}\s+(?!#)(?!Slide\s+\d)", text[m.end():end], re.M)
        if nxt:
            end = m.end() + nxt.start()
        out[int(m.group(1))] = (m.start(), end)
    return out


def _loose(s: str) -> str:
    """A regex for s that lets runs of spaces match any whitespace."""
    return r"\s+".join(re.escape(p) for p in s.split(" "))


def apply_wording(text: str, key: str, was: str, now: str) -> tuple[str, bool]:
    """Change `was` to `now` inside the part of the brief `key` names
    ("slide 3 point 2", "title"). Only the changed words and a little context
    around them are matched, so a bullet label or bold marks in the brief
    around the sentence stay as they are. (text, applied)."""
    m = re.match(r"slide (\d+)\b", key)
    if m:
        span = _spans(text).get(int(m.group(1)))
        if not span:
            return text, False
    else:  # the deck title: everything before the first slide
        first = HEADER_RE.search(text)
        span = (0, first.start() if first else len(text))
    seg = text[span[0]:span[1]]
    was, now = " ".join(was.split()), " ".join(now.split())
    if was == now:
        return text, True
    p = 0
    while p < min(len(was), len(now)) and was[p] == now[p]:
        p += 1
    s = 0
    while s < min(len(was), len(now)) - p and was[-1 - s] == now[-1 - s]:
        s += 1
    old_mid, new_mid = was[p:len(was) - s], now[p:len(now) - s]
    for c in (10**6, 40, 24, 12, 6, 3):
        left = was[max(0, p - c):p]
        right = was[len(was) - s:len(was) - s + c]
        needle = left + old_mid + right
        full = needle == was
        if len(needle.strip()) < 6 and not full:
            continue
        rx = re.compile(_loose(needle))
        hits = list(rx.finditer(seg))
        if not hits:
            continue
        if len(hits) > 1 and not full and len(needle) < 12:
            continue
        seg = rx.sub(lambda _m: left + new_mid + right, seg)
        return text[:span[0]] + seg + text[span[1]:], True
    return text, False


def write_visual_lines(text: str, n: int, name: str, lock: str, note: str, reuse: str | None) -> str:
    span = _spans(text).get(n)
    if not span:
        return text
    seg = text[span[0]:span[1]]
    seg = VIS_LINES_RE.sub("", seg)
    lines = [f"**Visual:** {V.format_visual(name, lock)}"]
    if note:
        lines.append(f"**Visual note:** {note}")
    if reuse:
        lines.append(f"**Reuse:** {reuse}")
    anchor = None
    for rx in (PIN_LINE_RE, ID_LINE_RE):
        mm = rx.search(seg)
        if mm:
            anchor = mm.end()
            break
    if anchor is None:
        first_nl = seg.find("\n")
        anchor = first_nl if first_nl >= 0 else len(seg)
    seg = seg[:anchor] + "\n\n" + "\n".join(lines) + seg[anchor:]
    seg = re.sub(r"\n{3,}", "\n\n", seg)
    return text[:span[0]] + seg + text[span[1]:]


def _set_pin(text: str, n: int, pin: str | None) -> str:
    span = _spans(text).get(n)
    if not span:
        return text
    seg = text[span[0]:span[1]]
    if pin:
        line = f"**Pinned source page:** {pin}"
        if PIN_LINE_RE.search(seg):
            seg = PIN_LINE_RE.sub(lambda _m: line, seg, count=1)
        else:
            mm = ID_LINE_RE.search(seg)
            at = mm.end() if mm else max(seg.find("\n"), 0)
            seg = seg[:at] + "\n\n" + line + seg[at:]
    else:
        seg = re.sub(r"\n*" + PIN_LINE_RE.pattern, "", seg, count=1, flags=re.M | re.I)
    return text[:span[0]] + seg + text[span[1]:]


def _front_matter_set(text: str, key: str, value: str) -> str:
    sys.path.insert(0, str(HERE.parents[1] / "storyline-helper" / "scripts"))
    import emit_dot_dash as ed
    new = ed.set_front_matter_value(text, key, value)
    return new if new is not None else text


def _seal_state(text: str) -> tuple[bool, bool]:
    """(sealed, seal valid) for the brief text."""
    import build_deck
    import seal_brief
    fm, body = build_deck.extract_front_matter(text.lstrip("﻿"))
    sha = (fm.get("storyline_gate_sha") or "").strip()
    if not sha:
        return False, False
    return True, sha in (seal_brief.brief_fingerprint(fm, body),
                         seal_brief.brief_fingerprint(fm, body, legacy=True))


# ------------------------------------------------------------------ the message

def parse_message(msg: str) -> dict:
    """{"edits": [(key, was, now)], "comments": {n: text},
        "visuals": {n: {name, lock, start, note}}, "pick_all": bool}."""
    lines = [ln.rstrip() for ln in (msg or "").replace("\r\n", "\n").split("\n")]
    out = {"edits": [], "comments": {}, "visuals": {}, "pick_all": False, "bad": []}
    sec = None
    key = was = None
    for raw in lines:
        s = raw.strip()
        if not s:
            continue
        low = s.lower()
        if low.startswith("wording:"):
            sec = "wording"
            continue
        if low.startswith("comments:"):
            sec = "comments"
            continue
        if low.startswith("visuals:"):
            sec = "visuals"
            out["pick_all"] = "designers pick every" in low
            continue
        if low.startswith(("folder:", "slide lab,", "(claude:")):
            continue
        if sec == "wording":
            m = re.fullmatch(r"(title|slide \d+ [a-z]+(?: \d+)?):", s, re.I)
            if m:
                key, was = m.group(1).lower(), None
                continue
            if low.startswith("was:") and key:
                was = s[4:].strip()
                continue
            if low.startswith("now:") and key and was is not None:
                out["edits"].append((key, was, s[4:].strip()))
                key = was = None
                continue
            out["bad"].append(s)
        elif sec == "comments":
            m = re.fullmatch(r"slide (\d+):\s*(.+)", s, re.I)
            if m:
                out["comments"][int(m.group(1))] = m.group(2).strip()
            elif out["comments"]:
                k = list(out["comments"])[-1]
                out["comments"][k] += " " + s
        elif sec == "visuals":
            m = re.fullmatch(r"slide (\d+):\s*(.+?)\s*\((suggestion|must use)\)(.*)", s, re.I)
            if not m:
                out["bad"].append(s)
                continue
            rest = m.group(4)
            start = note = ""
            nm = re.search(r";\s*note:\s*(.*)$", rest)
            if nm:
                note, rest = nm.group(1).strip(), rest[:nm.start()]
            sm = re.search(r";\s*start from:\s*(.*)$", rest)
            if sm:
                start = sm.group(1).strip()
            out["visuals"][int(m.group(1))] = {"name": m.group(2).strip(),
                                              "lock": m.group(3).lower(),
                                              "start": start, "note": note}
    return out


# ------------------------------------------------------------------ storyline files

def rewrite_storyline_files(brief: Path, edits_applied: list) -> list[str]:
    """The dot-dash .md / .html / Word file written again from the brief (prose
    only: no visuals, comments or highlights), and a storyline written by hand
    changed the same way. Returns lines to print."""
    sys.path.insert(0, str(HERE.parents[1] / "storyline-helper" / "scripts"))
    import emit_dot_dash as ed
    import build_deck
    said = []
    text = brief.read_text(encoding="utf-8")
    data = ed.parse_brief_for_dot_dash(text)
    md = ed._output_path(brief)
    htm, docx = md.with_suffix(".html"), md.with_suffix(".docx")
    md.write_text(ed.render_dot_dash_md(data), encoding="utf-8")
    htm.write_text(ed.render_dot_dash_html(data, standalone=True), encoding="utf-8")
    try:
        ed.render_dot_dash_docx(data, docx)
        said.append(f"  storyline written again: {docx}, {md.name}, {htm.name}")
    except ImportError:
        said.append(f"  storyline written again: {md}, {htm.name} (no Word file: python-docx missing)")
    fm, _ = build_deck.extract_front_matter(text)
    st = (fm.get("approved_storyline") or "").strip().strip('"')
    if st and Path(st).is_file() and Path(st).resolve() not in (htm.resolve(), md.resolve()) \
            and edits_applied:
        import replace_phrase as rp
        p = Path(st)
        if p.suffix.lower() in (".md", ".html", ".htm", ".txt"):
            body = p.read_text(encoding="utf-8")
            n = 0
            for _k, was, now in edits_applied:
                rx = re.compile(_loose(" ".join(was.split())))
                body, k = rp._replace_text(body, rx, " ".join(now.split()),
                                           p.suffix.lower() in (".html", ".htm"))
                n += k
            p.write_text(body, encoding="utf-8")
            said.append(f"  the approved storyline {p.name}: {n} change(s) made")
        else:
            said.append(f"  the approved storyline {p.name} is a {p.suffix} file: make the same "
                        "changes there with replace_phrase.py --out <build> --find ... --replace ... --apply")
    return said


# ------------------------------------------------------------------ the stage

def _brief(out: Path) -> Path | None:
    return SP.brief_path(out)


def open_stage(out: Path, brief: Path, reason: str = "") -> Path:
    """Open (or open again) the Storyline tab for the brief as it is now."""
    st = _state.read_state(out)
    sp = st.get("storyline_page") or {}
    text = brief.read_text(encoding="utf-8")
    fp = brief_fp(text)
    rnd = int(sp.get("round") or 0)
    same = sp.get("status") == "waiting" and sp.get("brief_fp") == fp and sp.get("token")
    if not same or reason:
        # a new look: a new code, so a message from the earlier page is refused
        rnd += 1
        sp["token"] = secrets.token_hex(6)
    # else: prep ran again on the same page; the message the user may already
    # have copied stays valid.
    sp.update({"status": "waiting", "round": rnd, "brief_fp": fp, "opened_at": _now()})
    if reason:
        sp["reason"] = reason
    st["storyline_page"] = sp
    _state._write(out, st)
    return SP.write(out, "storyline")


def needing(brief: Path) -> list[dict]:
    _h, slides = SP.storyline_slides(brief)
    return [s for s in slides if s["needs"]]


def prep_gate(out: Path, brief: Path, template, full_build: bool) -> tuple[str, list[str]]:
    """What prep does about the Storyline tab: ("proceed" | "wait", lines).

    "wait": the tab is open (or the chat still owes the user's comments);
    prep writes no prompts and dispatches nothing. "proceed": the designers
    may start."""
    import os
    st = _state.read_state(out)
    # the page is written before the manifest exists on a first prep
    st.setdefault("one_page", {})["brief"] = str(Path(brief).resolve())
    _state._write(out, st)
    sp = st.get("storyline_page") or {}
    on = os.environ.get("SLIDE_LAB_STORYLINE_TAB", "").strip()
    if not full_build or on == "0":
        return "proceed", []
    text = brief.read_text(encoding="utf-8")
    fp = brief_fp(text)
    status = sp.get("status")
    scripts = HERE
    if status == "done" or status in ("chat", "skipped"):
        return "proceed", []
    if status == "comments" and sp.get("recorded_fp") == fp:
        return "wait", [
            "STOPPED: the user's comments on the Storyline tab are not applied yet:",
            *[f"  slide {n}: {c}" for n, c in sorted((sp.get("comments") or {}).items(),
                                                     key=lambda kv: int(kv[0]))],
            "Change the storyline from them (storyline-helper: read the rulings file first, "
            "record each comment with add_ruling.py, re-seal the brief), then prep again: the "
            "Storyline tab opens again for the user to look.",
            f"Next: py -3 \"{scripts / 'build_deck.py'}\" --brief \"{brief}\" --template \"{template}\" --out \"{out}\""]
    need = needing(brief)
    if len(need) < V.PAGE_MIN_SLIDES:
        sp.update({"status": "chat", "recorded_at": _now(), "recorded_fp": fp,
                   "needing": len(need)})
        st["storyline_page"] = sp
        _state._write(out, st)
        SP.write(out, "designs")
        if not need:
            return "proceed", []
        names = ", ".join(f"slide {s['n']} ({s['v']})" for s in need)
        return "proceed", [
            f"Only {len(need)} slide(s) need a visual choice ({names}), so there is no "
            "Storyline tab to fill in. Before sending the workers, ask the user ONE question: "
            "\"Slide Lab proposes " + names + ". Keep that, pick another, or let the designers "
            "choose?\" Record the answer with record_storyline.py --out <build> "
            "--approved-in-chat \"<their words>\" --visual \"N=<visual>|must use\" and prep "
            "again; if they leave it to the designers, carry on."]
    path = open_stage(out, brief)
    return "wait", [
        f"STOP: the Storyline tab is open for the user: {path}",
        f"  {len(need)} slide(s) need a visual choice. The user edits the wording, comments "
        "and picks each slide's visual there, then presses Done and pastes the message.",
        "  Do NOT send any worker yet: prep wrote no slide prompts. Tell the user the page is "
        "open (tab 1, Storyline) and wait for their message.",
        f"Next: py -3 \"{scripts / 'record_storyline.py'}\" --out \"{out}\" --message \"<the whole message, exactly as pasted>\""]


def _prep_cmd(out: Path, brief: Path) -> str:
    meta = SP._meta(out)
    tpl = meta.get("template") or "<template.pptx>"
    return (f"py -3 \"{HERE / 'build_deck.py'}\" --brief \"{brief}\" --template \"{tpl}\" "
            f"--out \"{out}\"")


def record(out: Path, parsed: dict, source: str, words: str = "") -> int:
    brief = _brief(out)
    if not brief:
        print("REFUSED: this build has no brief recorded (run prep first).")
        return 5
    raw = brief.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n")
    sealed, valid = _seal_state(text)
    _h, slides = SP.storyline_slides(brief)
    by_n = {s["n"]: s for s in slides}
    need = [s for s in slides if s["needs"]]

    # 1. wording
    applied, missed = [], []
    for key, was, now in parsed["edits"]:
        text, ok = apply_wording(text, key, was, now)
        (applied if ok else missed).append((key, was, now))

    # 2. visuals
    vis_rec: dict[str, dict] = {}
    bad = []
    ropts = SP.reuse_options(slides, SP._page_map(brief))
    for n, v in sorted(parsed["visuals"].items()):
        if n not in by_n:
            bad.append(f"slide {n} is not in the brief")
            continue
        name = V.ANY if parsed.get("pick_all") else V.canonical(v["name"])
        if not name:
            bad.append(f"slide {n}: \"{v['name']}\" is not one of the visual names")
            continue
        lock = "suggestion" if parsed.get("pick_all") else v["lock"]
        reuse = None
        start = (v.get("start") or "").strip()
        if n in ropts:
            lab = ropts[n]["label"]
            if start.lower().startswith("new design") or not start:
                reuse = "new design" if start else None
            elif start.lower().endswith("clean it up"):
                reuse = f"{lab}, clean it up"
            else:
                reuse = f"{lab}, keep as is"
        vis_rec[str(n)] = {"name": name, "lock": lock, "note": v.get("note") or "",
                           "reuse": reuse or ""}
    if bad:
        print("REFUSED: the Visuals part of the message is not right: " + "; ".join(bad) + ".")
        print("Nothing was recorded. Have the user press Done on the Storyline tab again "
              "and paste the whole message.")
        return 5
    choices = [(s["n"], (vis_rec.get(str(s["n"])) or {"name": s["v"]})["name"],
                (vis_rec.get(str(s["n"])) or {"lock": s["lock"]})["lock"]) for s in need]
    mx = V.mix(choices)

    for n_s, rec in vis_rec.items():
        text = write_visual_lines(text, int(n_s), rec["name"], rec["lock"], rec["note"],
                                  rec["reuse"] or None)
    # Start from: keep as is pins the page; the others unpin it.
    m = SP._page_map(brief)
    by_id = {s.get("id"): s for s in (m or {}).get("slides") or []}
    pins_changed = 0
    for n_s, rec in vis_rec.items():
        n = int(n_s)
        if n not in ropts or not rec["reuse"]:
            continue
        s = by_n[n]
        prop = (by_id.get(s["id"]) or {}).get("proposal")
        if rec["reuse"].endswith("keep as is"):
            pin = (f"{prop['file']} slide {int(prop['page'])}" if prop else s.get("pinned"))
            if pin and pin != s.get("pinned"):
                text = _set_pin(text, n, pin)
                pins_changed += 1
        elif s.get("pinned"):
            text = _set_pin(text, n, None)
            pins_changed += 1

    if sealed and valid and applied:
        text = _front_matter_set(text, "storyline_gate_sha", brief_fp(text))
    brief.write_bytes(text.replace("\n", nl).encode("utf-8"))
    if m and pins_changed:
        try:
            import _rulings
            import map_source_pages as msp
            m["approved"] = {"words": "Start from, on the Slide Lab page's Storyline tab",
                             "at": _now(), "where": source}
            msp._save(_rulings.session_dir(brief=brief), m)
        except Exception:
            pass

    said = rewrite_storyline_files(brief, applied) if applied else []

    st = _state.read_state(out)
    sp = st.get("storyline_page") or {}
    sp.setdefault("history", []).append({
        "at": _now(), "source": source, "edits": [list(e) for e in applied],
        "missed": [list(e) for e in missed], "comments": parsed["comments"],
        "visuals": vis_rec, "words": words[:2000]})
    sp["visuals"] = vis_rec or sp.get("visuals") or {}
    sp["edits_applied"] = int(sp.get("edits_applied") or 0) + len(applied)
    sp["recorded_at"] = _now()
    sp["recorded_fp"] = brief_fp(text)
    sp.pop("cap", None)
    status = "done"
    if mx["refuse"]:
        status = "waiting"
        sp["cap"] = V.cap_message(mx)
    elif parsed["comments"]:
        status = "comments"
        sp["comments"] = {str(k): v for k, v in parsed["comments"].items()}
    sp["status"] = status
    st["storyline_page"] = sp
    _state._write(out, st)

    print(f"[ok] Storyline tab recorded ({source}).")
    print(f"  wording: {len(applied)} change(s) applied to {brief.name}"
          + (" (the brief is sealed again: these are the user's own words)" if sealed and valid and applied else ""))
    for ln in said:
        print(ln)
    for key, was, now in missed:
        print(f"  NOT applied ({key}): \"{was[:70]}\" was not found in the brief as written. "
              f"Make it with replace_phrase.py --out \"{out}\" --find \"<words as in the brief>\" "
              f"--replace \"<new words>\" --apply")
    if vis_rec:
        firm = [n for n, r in vis_rec.items() if r["lock"] == "must use"]
        print(f"  visuals: {len(vis_rec)} slide(s) recorded in the brief"
              + (f"; Must use on slide {', '.join(firm)}" if firm else "")
              + (f"; {pins_changed} supplied page(s) pinned or unpinned" if pins_changed else ""))
    if mx["repeats"]:
        print(f"  note: slide(s) {', '.join(map(str, mx['repeats']))} use the same kind of "
              "visual as the slide before.")
    if status == "waiting":
        path = open_stage(out, brief, reason="cap")
        print(f"STOPPED: {V.cap_message(mx)} Some of them are only suggestions.")
        print(f"  The Storyline tab is open again with the warning: {path}")
        print("  Tell the user: change some of them, or mark the ones they want as Must use, "
              "then press Done again.")
        print(f"Next: py -3 \"{HERE / 'record_storyline.py'}\" --out \"{out}\" --message \"<the new message>\"")
        return 5
    if status == "comments":
        SP.write(out, "storyline")
        print(f"  comments on {len(parsed['comments'])} slide(s): the chat changes the storyline "
              "from them (storyline-helper; read the rulings file first and record each with "
              "add_ruling.py), re-seals the brief, then preps again; the tab opens again for a look:")
        for n, c in sorted(parsed["comments"].items()):
            print(f"    slide {n}: {c}")
        print(f"Next: {_prep_cmd(out, brief)}")
        return 4
    SP.write(out, "designs")
    print("  The Storyline tab is read only now. Prep again: it writes the slide prompts with "
          "the visuals, then send the workers.")
    print(f"Next: {_prep_cmd(out, brief)}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Record the Storyline tab of the Slide Lab page.")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--message", default=None,
                    help="The whole message the Storyline tab's Done button copied.")
    ap.add_argument("--approved-in-chat", default=None, dest="chat",
                    help="The user's words in chat (one or two slides need a visual).")
    ap.add_argument("--visual", action="append", default=[],
                    help='With --approved-in-chat: "N=<visual name>|suggestion" or "|must use".')
    ap.add_argument("--designers-pick-all", action="store_true", dest="pick_all")
    a = ap.parse_args(argv)
    try:
        import _rulings
        _rulings.announce(out=a.out)
    except Exception:
        pass
    out = a.out.resolve()
    if not _p.meta_json(out).exists():
        print(f"ERROR: no build at {out} (no _meta.json). Run prep first.")
        return 2
    if bool(a.message) == bool(a.chat):
        print("ERROR: give exactly one of --message (what the page copied) or "
              "--approved-in-chat (the user's words).")
        return 2
    if a.message:
        ok, why = SP.check_header(out, a.message, "storyline")
        if not ok:
            print("REFUSED: " + why)
            return 5
        if not SP.HEADER_RE.search(a.message):
            print("REFUSED: the message has no Slide Lab header line, so it cannot be tied to "
                  "this build. Have the user press Done on the Storyline tab and paste the "
                  "whole message.")
            return 5
        st = _state.read_state(out)
        if (st.get("storyline_page") or {}).get("status") != "waiting":
            print("REFUSED: the Storyline tab of this build is not waiting for the user "
                  "(it was recorded already). Nothing was recorded.")
            return 5
        parsed = parse_message(a.message)
        if parsed["bad"]:
            print("REFUSED: these lines of the message could not be read: "
                  + " | ".join(parsed["bad"][:4]) + ". Paste the whole message exactly as copied.")
            return 5
        return record(out, parsed, f"Storyline tab, code {SP.stage_code(out, 'storyline')}",
                      a.message)
    words = a.chat.strip()
    if len(words.split()) < 2:
        print("REFUSED: give the user's own words, verbatim (at least two words).")
        return 5
    parsed = {"edits": [], "comments": {}, "visuals": {}, "pick_all": a.pick_all, "bad": []}
    if a.pick_all and not re.search(r"\b(you|designers?|any|pick|choose|decide)\b", words, re.I):
        print("REFUSED: --designers-pick-all, but the user's words do not leave it to the designers.")
        return 5
    for item in a.visual:
        mm = re.fullmatch(r"\s*(\d{1,3})\s*=\s*(.+?)\s*(?:\|\s*(suggestion|must use))?\s*", item, re.I)
        if not mm or not V.canonical(mm.group(2)):
            print(f"ERROR: --visual {item!r}: write \"N=<visual name>|must use\"; the names: "
                  + ", ".join(V.NAMES))
            return 2
        parsed["visuals"][int(mm.group(1))] = {"name": mm.group(2),
                                              "lock": (mm.group(3) or "suggestion").lower(),
                                              "start": "", "note": ""}
    if not parsed["visuals"] and not a.pick_all:
        print("ERROR: give --visual for each slide the user answered for, or --designers-pick-all.")
        return 2
    if a.pick_all:
        brief = _brief(out)
        for s in (needing(brief) if brief else []):
            parsed["visuals"][s["n"]] = {"name": V.ANY, "lock": "suggestion", "start": "", "note": ""}
    st = _state.read_state(out)
    sp = st.get("storyline_page") or {}
    if sp.get("status") == "waiting":
        print("REFUSED: the Storyline tab is open for the user; their Done message records it "
              "(--message). A chat answer is for builds with only one or two visual choices.")
        return 5
    return record(out, parsed, "chat", words)


if __name__ == "__main__":
    sys.exit(main())
