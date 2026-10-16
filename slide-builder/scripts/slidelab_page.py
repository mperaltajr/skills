#!/usr/bin/env python3
"""slidelab_page.py: ONE Slide Lab page per deck, for the whole build.

Owner's decision (2026-10-14 to 2026-10-16): the user never opens several
HTML files. Each build has one file, `<deck topic> - Slide Lab.html`, in the
build folder, rewritten in place at each stage, with three tabs:

  1 Storyline      the approved storyline, editable in place (changed lines
                   turn yellow), "+ Comment on this slide", a gray visual box
                   per slide (Suggestion / Must use), the mix box (6+ slides),
                   and "Pages you gave us" when pages were supplied.
  2 Slide designs  today's design review (REVIEW.html's content).
  3 Final check    today's final check (FINAL-CHECK.html's content).

A tab not reached yet is gray with a note; a finished tab is read only; only
the current stage's Done button works. Every Done copies ONE message whose
first line is

    Slide Lab, <deck>, <tab>, code <XXXX>

The code is tied to this build and this stage (and the stage's own token), so
a message pasted into the wrong deck, or from an older page, is refused by
the script that records it (record_storyline.py, record_picks.py).

REVIEW.html and FINAL-CHECK.html are still written for one release (scripts
and in-flight builds read them), with a redirect: opened on their own they
jump to this file's tab.

  py -3 scripts/slidelab_page.py show --out <build>     (print the path and the stage)
  py -3 scripts/slidelab_page.py write --out <build>    (write it again for the stage recorded)
"""
from __future__ import annotations

import argparse
import html
import json
import re
import secrets
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _paths as _p  # noqa: E402
import _state  # noqa: E402
import _visuals as V  # noqa: E402

STAGES = ("storyline", "designs", "final")
TAB = {"storyline": "Storyline", "designs": "Slide designs", "final": "Final check"}
TAB_TO_STAGE = {v.lower(): k for k, v in TAB.items()}
HEADER_RE = re.compile(
    r"^\s*Slide Lab,\s*(.+?),\s*(Storyline|Slide designs|Final check),\s*code\s+([0-9A-Za-z]{4})\s*$",
    re.M)
REDIRECT_START = "<!--slidelab-redirect-->"
REDIRECT_END = "<!--/slidelab-redirect-->"
ANCHOR = {"storyline": "storyline", "designs": "designs", "final": "final"}


# ----------------------------------------------------------------- names

def _emit():
    sh = HERE.parents[1] / "storyline-helper" / "scripts"
    if str(sh) not in sys.path:
        sys.path.insert(0, str(sh))
    import emit_dot_dash  # noqa: E402
    return emit_dot_dash


def _meta(out_dir: Path) -> dict:
    try:
        return json.loads(_p.meta_json(out_dir).read_text(encoding="utf-8"))
    except Exception:
        return {}


def brief_path(out_dir: Path, meta: dict | None = None) -> Path | None:
    meta = meta if meta is not None else _meta(out_dir)
    b = (meta or {}).get("brief") or (
        (_state.read_state(out_dir).get("one_page") or {}).get("brief") or "")
    return Path(b) if b and Path(b).exists() else None


def deck_name(out_dir: Path, meta: dict | None = None) -> str:
    """The deck's topic from the brief's title line, else the folder name."""
    b = brief_path(out_dir, meta)
    if b:
        try:
            m = re.search(r"^#\s+(?:Narrative brief:\s*)?(.+?)\s*$",
                          b.read_text(encoding="utf-8"), re.M)
            if m:
                return " ".join(m.group(1).split())
        except OSError:
            pass
    return Path(out_dir).resolve().name


def _safe(name: str) -> str:
    t = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", name)
    t = " ".join(t.split()).strip(" .")
    return (t[:80].rstrip(" .") or "Deck")


def _one(state: dict) -> dict:
    return state.setdefault("one_page", {})


def page_path(out_dir: Path) -> Path:
    """`<build>/<deck topic> - Slide Lab.html`. The name is fixed the first
    time (a later title change does not make a second file)."""
    out_dir = Path(out_dir)
    st = _state.read_state(out_dir)
    name = (st.get("one_page") or {}).get("file")
    if name:
        return out_dir / name
    return out_dir / f"{_safe(deck_name(out_dir))} - Slide Lab.html"


def _ensure_ids(out_dir: Path) -> dict:
    st = _state.read_state(out_dir)
    one = _one(st)
    changed = False
    if not one.get("build_id"):
        one["build_id"] = secrets.token_hex(4)
        changed = True
    if not one.get("file"):
        one["file"] = page_path(out_dir).name
        changed = True
    if changed:
        _state._write(out_dir, st)
    return st


# ----------------------------------------------------------------- codes

def stage_token(state: dict, stage: str) -> str:
    if stage == "storyline":
        return (state.get("storyline_page") or {}).get("token", "")
    if stage == "designs":
        return (state.get("review") or {}).get("token", "")
    return (state.get("final_check") or {}).get("token", "")


def stage_code(out_dir: Path, stage: str, token: str | None = None, state: dict | None = None) -> str:
    st = state if state is not None else _state.read_state(out_dir)
    tok = token if token is not None else stage_token(st, stage)
    canon = st.get("canonical_out") or str(Path(out_dir).resolve())
    bid = (st.get("one_page") or {}).get("build_id", "")
    return _state.fnv1a32(f"{canon.lower()}|{bid}|{stage}|{tok}")[:4].upper()


def header(out_dir: Path, stage: str, token: str | None = None) -> str:
    st = _ensure_ids(out_dir)
    return f"Slide Lab, {deck_name(out_dir)}, {TAB[stage]}, code {stage_code(out_dir, stage, token, st)}"


def check_header(out_dir: Path, text: str, stage: str) -> tuple[bool, str]:
    """(ok, message) for a pasted message. No header line: accepted (a page
    made before the one Slide Lab page), with a note. A header for another
    tab, another deck or an older page: refused."""
    m = HEADER_RE.search(text or "")
    if not m:
        return True, "no Slide Lab header line (a page from before the one Slide Lab page)"
    deck, tab, code = m.group(1).strip(), m.group(2), m.group(3).upper()
    want_stage = TAB_TO_STAGE[tab.lower()]
    here = deck_name(out_dir)
    fname = page_path(out_dir).name
    if want_stage != stage:
        return False, (f"this message comes from the {tab} tab, but this step records the "
                       f"{TAB[stage]} tab. Use the command for the {tab} tab, or have the user "
                       f"press Done on the {TAB[stage]} tab of {fname}.")
    now = stage_code(out_dir, stage)
    if code != now:
        if deck.lower() != here.lower():
            return False, (f'this message is from the deck "{deck}", not "{here}" (this build: '
                           f"{Path(out_dir).resolve()}). Nothing was recorded. Use the build "
                           "folder of that deck, or have the user press Done in this deck's "
                           f"page ({fname}).")
        return False, (f"the code {code} is not this build's current {tab} code. The message "
                       "is from an older page or a copy of this deck in another folder. "
                       f"Nothing was recorded. Have the user open {fname} again, press Done "
                       f"on the {tab} tab and paste the new message.")
    return True, "ok"


# ----------------------------------------------------------------- storyline data

_FIELD_RE = r"^\*\*{label}:\*\*[ \t]*(.*)$"


def _field(block: str, label: str) -> str:
    m = re.search(_FIELD_RE.format(label=re.escape(label)), block, re.M | re.I)
    return m.group(1).strip() if m else ""


def _key(t) -> str:
    """Text compared without case, spaces or end punctuation (a headline and
    the same claim with a period are one line, shown once)."""
    return " ".join((t or "").lower().split()).strip(" .;:")


def storyline_slides(brief: Path) -> tuple[dict, list[dict]]:
    """(deck header, slides) for the Storyline tab, from the brief."""
    ed = _emit()
    text = brief.read_text(encoding="utf-8")
    data = ed.parse_brief_for_dot_dash(text)
    blocks = ed._split_slides(text)
    out = []
    for s, block in zip(data["slides"], blocks):
        m = re.match(r"^#+\s*Slide\s+(\d+)\s*[—–:-]?\s*(.*)$", block.splitlines()[0])
        n = int(m.group(1)) if m else len(out) + 1
        headline = (m.group(2).strip() if m else "") or s.get("governing") or ""
        vis = V.parse_visual(_field(block, "Visual"))
        chart = _field(block, "Chart type")
        mand = _field(block, "Mandatory shape")
        needs = V.needs_choice(s.get("archetype") or "", s.get("no_narrative"))
        proposed = vis["name"] if vis and not vis.get("unknown") else V.infer(chart, mand)
        shows = _field(block, "Visual shows") or (
            (s.get("exhibit") or "").replace("Exhibit: ", "", 1) if s.get("exhibit") else "")
        out.append({
            "n": n,
            "id": _field(block, "Slide id").strip("` "),
            "sec": " ".join(_field(block, "Section tag").split()),
            "h": headline,
            "claim": s.get("governing") if _key(s.get("governing")) not in ("", _key(headline)) else "",
            "b": [ed.bullet_text(b) for b in s.get("bullets") or []] if not s.get("no_narrative") else [],
            "take": s.get("so_what") or "",
            "needs": needs,
            "v": proposed if proposed in V.VISUALS else V.ANY,
            "from_brief": bool(vis and not vis.get("unknown")),
            "lock": (vis or {}).get("lock", "suggestion"),
            "note": _field(block, "Visual note"),
            "shows": shows or ("Left to the designer" if proposed == V.ANY else ""),
            "reuse": _field(block, "Reuse"),
            "pinned": _field(block, "Pinned source page") or _field(block, "Supplied page"),
        })
    return data["header"], out


def _page_map(brief: Path) -> dict | None:
    try:
        import _rulings
        import map_source_pages as msp
        return msp.load_map(_rulings.session_dir(brief=brief))
    except Exception:
        return None


def _pic_uri(m: dict, deck: str, page: int) -> str:
    try:
        import map_source_pages as msp
        return msp._pic((m.get("pictures") or {}).get(deck), page)
    except Exception:
        return ""


def reuse_options(slides: list[dict], m: dict | None) -> dict:
    """{n: {"label": "<file> page N", "thumb": uri, "default": choice}} for the
    slides with a supplied page (the page map's proposal, or a pinned line)."""
    out: dict[int, dict] = {}
    by_id = {s.get("id"): s for s in (m or {}).get("slides") or []}
    for s in slides:
        prop = (by_id.get(s["id"]) or {}).get("proposal") if s["id"] else None
        label, thumb = "", ""
        if prop:
            label = f"{Path(prop['file']).name} page {int(prop['page'])}"
            thumb = _pic_uri(m, prop["file"], int(prop["page"]))
        elif s.get("pinned"):
            pm = re.match(r"(.+?)\s+slide\s+(\d+)\s*$", s["pinned"], re.I)
            label = (f"{Path(pm.group(1)).name} page {pm.group(2)}" if pm
                     else Path(s["pinned"]).name)
        if not label:
            continue
        cur = (s.get("reuse") or "").lower()
        default = ("new" if "new design" in cur else "clean" if "clean" in cur else "keep")
        out[s["n"]] = {"label": label, "thumb": thumb, "default": default}
    return out


def given_rows(slides: list[dict], m: dict | None) -> list[dict]:
    """Every supplied page and the slide it goes to, or not used."""
    if not m:
        return []
    by_page = {}
    for s in m.get("slides") or []:
        pr = s.get("proposal")
        if pr:
            by_page[(pr["file"], int(pr["page"]))] = s
    texts = m.get("page_text") or {}
    rows = []
    for d in m.get("decks") or []:
        n_pages = sum(1 for k in texts if k.startswith(d + "#")) or max(
            [pg for (f, pg) in by_page if f == d] or [0])
        for pg in range(1, n_pages + 1):
            s = by_page.get((d, pg))
            rows.append({"page": pg, "from": Path(d).name, "thumb": _pic_uri(m, d, pg),
                         "slide": s["n"] if s else None})
    return rows


# ----------------------------------------------------------------- the page

CSS = """
:root { --bg:#FFFFFF; --panel:#FFFFFF; --panel-2:#F4F5F7; --text:#17202E; --text-dim:#475569; --accent:#A100FF; --accent-soft:#7A0FB8; --border:#E2E8F0; --warn:#B45309; --warn-bg:#FFF7ED; --ok:#15803D; --edit-bg:#FEFCE8; --edit-line:#CA8A04; }
html, body { margin:0; height:100%; }
body { background:var(--bg); font-family:'Inter', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; color:var(--text); font-size:14px; line-height:1.5; display:flex; flex-direction:column; }
.topbar { flex:0 0 auto; z-index:10; background:var(--panel); border-bottom:2px solid var(--border); padding:10px 28px 0; }
.toprow { display:flex; align-items:center; gap:20px; }
.t { font-size:18px; font-weight:700; }
.stage { margin-left:auto; font-size:12.5px; color:var(--text-dim); }
.tabs { display:flex; gap:4px; margin-top:10px; }
.tab { padding:8px 16px; border:1px solid var(--border); border-bottom:0; border-radius:6px 6px 0 0; background:var(--panel-2); color:var(--text-dim); cursor:pointer; font-weight:600; font-size:13px; }
.tab.on { background:#fff; color:var(--text); border-color:var(--accent); border-bottom:2px solid #fff; margin-bottom:-2px; }
.tab.later { color:#94A3B8; background:#F8FAFC; }
.tab small { font-weight:400; margin-left:6px; }
.tab .st { font-weight:400; font-size:11px; margin-left:6px; }
.pane { display:none; flex:1 1 auto; min-height:0; }
.pane.on { display:block; }
.pane:focus, .pane:focus-visible { outline:none; }
.pane.scroll { overflow:auto; }
.pane.frame.on { display:flex; flex-direction:column; }
.pane iframe { flex:1 1 auto; width:100%; border:0; min-height:0; }
.wrap { max-width:1060px; margin:0 auto; padding:18px 28px 70px; }
.box { background:var(--panel); border:1px solid var(--border); border-radius:6px; padding:12px 16px; margin-bottom:14px; }
.box ol { margin:6px 0 0 18px; padding:0; } .box li { margin:3px 0; }
.note { border-color:#FED7AA; background:var(--warn-bg); }
.done-note { border-color:#BBF7D0; background:#F0FDF4; }
.later-note { color:var(--text-dim); background:var(--panel-2); }
.mixrow { display:flex; gap:22px; flex-wrap:wrap; margin-top:6px; } .mixrow span b { font-size:16px; margin-right:4px; }
.mixmsg { margin-top:6px; } .mixmsg.ok { color:var(--ok); } .mixmsg.bad { color:var(--warn); font-weight:700; }
table.given { border-collapse:collapse; width:100%; margin-top:8px; font-size:13px; }
table.given th { text-align:left; background:var(--panel-2); color:var(--text-dim); font-weight:600; padding:6px 8px; border-bottom:1px solid var(--border); }
table.given td { padding:6px 8px; border-top:1px solid var(--border); }
.thumb { width:96px; height:54px; border:1px solid var(--border); background:#fff; display:inline-flex; align-items:center; justify-content:center; color:var(--text-dim); font-size:10.5px; vertical-align:middle; margin-right:8px; object-fit:cover; }
.doc { border:1px solid var(--border); border-radius:6px; padding:8px 28px 18px; }
.doc h1 { font-size:22px; margin:14px 0 4px; }
.doc h2 { font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:var(--accent-soft); margin:26px 0 4px; }
.slide { padding:10px 0 4px; border-top:1px solid var(--border); margin-top:10px; }
.slide h3 { font-size:16px; margin:6px 0 6px; }
.slide .num { color:var(--text-dim); margin-right:4px; }
.slide ul { margin:0 0 6px 20px; padding:0; } .slide li { margin:3px 0; }
.slide .claim { margin:0 0 6px; }
.take { margin:4px 0 6px; } .take b { color:var(--text-dim); font-weight:600; }
[contenteditable] { outline:none; border-radius:3px; padding:1px 3px; margin:-1px -3px; }
[contenteditable]:hover { background:var(--panel-2); }
[contenteditable]:focus { background:#fff; box-shadow:0 0 0 2px #E9D5FF; }
.edited { background:var(--edit-bg) !important; box-shadow:inset 3px 0 0 var(--edit-line); }
.cbtn { font-size:12px; color:var(--accent-soft); cursor:pointer; background:none; border:0; padding:0; font-weight:600; }
.comment { display:none; margin:6px 0; } .comment.open { display:block; }
.comment textarea { width:100%; height:44px; }
.pick { background:var(--panel-2); border:1px solid var(--border); border-radius:6px; padding:10px 12px; margin:10px 0 4px; display:grid; grid-template-columns: 1.3fr 1fr; gap:10px 18px; }
.lbl { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--text-dim); margin-bottom:3px; }
select, textarea { font:inherit; font-size:13px; width:100%; box-sizing:border-box; border:1px solid #CBD5E1; border-radius:4px; padding:4px; background:#fff; color:var(--text); }
.pick textarea { height:44px; resize:vertical; }
.vrow { display:flex; gap:10px; align-items:flex-start; }
.sk { flex:0 0 92px; width:92px; height:52px; background:#fff; border:1px solid var(--border); border-radius:4px; }
.shows { font-size:12.5px; color:var(--text-dim); margin-top:4px; }
.lock label { margin-right:14px; font-size:13px; cursor:pointer; }
.flagtxt { color:var(--warn); font-size:12px; font-weight:700; margin-top:4px; }
.slide.flag .pick { background:var(--warn-bg); border-color:#FED7AA; }
.newdesign { font-size:13px; color:var(--text-dim); }
.btns { display:flex; gap:10px; margin-top:10px; flex-wrap:wrap; }
button { font:inherit; font-weight:600; background:var(--accent); color:#fff; border:0; border-radius:4px; padding:8px 16px; cursor:pointer; }
button.alt { background:#fff; color:var(--accent-soft); border:1px solid var(--accent); }
button:disabled { background:#CBD5E1; color:#fff; border-color:#CBD5E1; cursor:not-allowed; }
#out { display:none; width:100%; height:180px; font-family:Consolas, monospace; font-size:12px; margin-top:10px; }
#outhint { display:none; font-size:12.5px; color:var(--text-dim); margin-top:6px; }
.ro [contenteditable] { pointer-events:none; }
"""

_RO_INJECT = """<style>.slidelab-ro-banner{position:sticky;top:0;z-index:99999;background:#F0FDF4;border-bottom:1px solid #BBF7D0;color:#166534;font:600 13px 'Segoe UI',Arial,sans-serif;padding:8px 24px}
body.slidelab-ro button,body.slidelab-ro textarea,body.slidelab-ro input,body.slidelab-ro select,body.slidelab-ro .option{pointer-events:none !important;opacity:.6}</style>
<div class="slidelab-ro-banner">__MSG__</div>
<script>document.body.classList.add("slidelab-ro");document.querySelectorAll("button,textarea,input,select").forEach(function(e){e.disabled=true;});</script>"""


def _strip_redirect(page: str) -> str:
    return re.sub(re.escape(REDIRECT_START) + r".*?" + re.escape(REDIRECT_END), "", page, flags=re.S)


def redirect_block(out_dir: Path, stage: str) -> str:
    """The lines REVIEW.html / FINAL-CHECK.html carry: opened on their own,
    they jump to the one Slide Lab page's tab."""
    target = quote(page_path(out_dir).name) + "#" + ANCHOR[stage]
    # An automated browser (the test suites drive REVIEW.html itself, and
    # navigator.webdriver is true there) stays on the page.
    return (f'{REDIRECT_START}<script>if (window.self === window.top && !navigator.webdriver '
            f'&& location.search.indexOf("stay") < 0) '
            f'location.replace({json.dumps(target)});</script>{REDIRECT_END}')


def add_redirect(page: str, out_dir: Path, stage: str) -> str:
    page = _strip_redirect(page)
    block = redirect_block(out_dir, stage)
    i = page.lower().find("<head>")
    if i < 0:
        return block + page
    i += len("<head>")
    return page[:i] + block + page[i:]


def _embedded(path: Path, read_only_msg: str | None) -> str:
    try:
        page = _strip_redirect(path.read_text(encoding="utf-8"))
    except OSError:
        return ""
    if read_only_msg:
        inj = _RO_INJECT.replace("__MSG__", html.escape(read_only_msg))
        m = re.search(r"<body[^>]*>", page, re.I)
        if m:
            # the banner goes first; the disabling script must run after the
            # page's own content exists, so it goes at the end.
            css_banner, script = inj.rsplit("<script>", 1)
            page = (page[:m.end()] + css_banner + page[m.end():])
            j = page.lower().rfind("</body>")
            script = "<script>" + script
            page = page[:j] + script + page[j:] if j >= 0 else page + script
    return (f'<iframe class="part" title="{html.escape(path.stem)}" allow="clipboard-write" '
            f'srcdoc="{html.escape(page, quote=True)}"></iframe>')


def _storyline_tab(out_dir: Path, stage: str, st: dict) -> str:
    meta = _meta(out_dir)
    b = brief_path(out_dir, meta)
    sp = st.get("storyline_page") or {}
    if not b:
        return '<div class="wrap"><div class="box later-note">No brief recorded for this build yet.</div></div>'
    head, slides = storyline_slides(b)
    pm = _page_map(b)
    ropts = reuse_options(slides, pm)
    rows = given_rows(slides, pm) if ropts or pm else []
    n_need = sum(1 for s in slides if s["needs"])
    current = stage == "storyline" and sp.get("status") in ("waiting", None)
    page_on = n_need >= V.PAGE_MIN_SLIDES
    status = sp.get("status") or ""
    notes = []
    if current:
        notes.append('<div class="box"><b>What to do on this tab</b><ol>'
                     "<li><b>Edit the wording right in the text.</b> Click any headline, point or "
                     "takeaway and type. Changed lines turn yellow so you can see what you touched.</li>"
                     "<li><b>Comment</b> on a slide when you'd rather say what you want than rewrite it "
                     "(\"merge this with slide 5\").</li>"
                     + ("<li><b>Visual:</b> in the gray box under each slide. Slide Lab proposes one; the "
                        "small sketch shows what it means. <i>Suggestion</i> lets the designer do better "
                        "if they say why; <i>Must use</i> means it has to come back that way.</li>"
                        if page_on else "")
                     + "<li>Press <b>Done</b> and paste the message into the chat. Slide Lab updates the "
                       "storyline and the Word version, records the visuals, and then the designers start "
                       "(tab 2).</li></ol>The Word version you share with others has only your prose: the "
                       "gray boxes, comments and highlights are left out.</div>")
        if sp.get("round", 1) > 1:
            notes.append('<div class="box note">The storyline was changed from your comments. '
                         "Look at it again and press Done.</div>")
        if sp.get("cap"):
            notes.append(f'<div class="box note"><b>{html.escape(sp["cap"])}</b> Change some of '
                         "them, or mark the ones you want as Must use, then press Done again.</div>")
    else:
        when = (sp.get("recorded_at") or "")[:16].replace("T", " ")
        if status == "done":
            msg = f"Done{(' ' + when) if when else ''}: your storyline changes and visuals are recorded."
            if sp.get("edits_applied"):
                msg += f" {sp['edits_applied']} wording change(s) applied."
            notes.append(f'<div class="box done-note">{html.escape(msg)} This tab is read only now.</div>')
        elif status == "comments":
            notes.append('<div class="box note">Your comments are with the chat: it changes the '
                         "storyline, and this tab opens again for a look.</div>")
        elif status == "chat":
            notes.append('<div class="box done-note">Only '
                         f"{n_need} slide(s) needed a visual choice, so Slide Lab asked in chat instead "
                         "of on this tab. Read only.</div>")
        elif status == "skipped":
            notes.append('<div class="box done-note">The storyline was settled before this build '
                         "(no Storyline tab for this kind of build). Read only.</div>")
        else:
            notes.append('<div class="box done-note">The storyline as approved. Read only.</div>')
    if rows:
        trs = "".join(
            "<tr><td>" + (f'<img class="thumb" src="{html.escape(r["thumb"])}" alt="">' if r["thumb"]
                          else '<span class="thumb">picture</span>')
            + f"Page {r['page']}</td><td>{html.escape(r['from'])}</td><td>"
            + (f"Slide {r['slide']}" if r["slide"] else "Not used (tell us if it should be)")
            + "</td></tr>" for r in rows)
        notes.append('<div class="box given-box"><b>Pages you gave us</b> (every page you supplied, '
                     "and which slide it goes to, so nothing is dropped unseen)<table class=\"given\">"
                     "<tr><th>Your page</th><th>From</th><th>Used for</th></tr>" + trs + "</table></div>")
    mix_on = page_on and n_need >= V.MIX_MIN_SLIDES
    if mix_on:
        notes.append('<div class="box"><b>Mix of visuals across the deck</b>'
                     + (' (updates as you change the choices)' if current else '')
                     + '<div class="mixrow" id="mix"></div><div id="mixmsg" class="mixmsg">'
                     "</div></div>")
    data = {
        "slides": slides, "reuse": {str(k): v for k, v in ropts.items()},
        "visuals": {k: V.VISUALS[k][0] for k in V.NAMES}, "heavy": list(V.HEAVY),
        "any": V.ANY, "mixOn": mix_on, "pageOn": page_on, "current": current,
        "header": header(out_dir, "storyline") if current else "",
        "folder": str(Path(out_dir).resolve()), "title": head.get("topic") or deck_name(out_dir),
        "recorded": sp.get("visuals") or {},
    }
    done_box = ""
    if current:
        done_box = ('<div class="box" style="margin-top:16px"><div class="btns">'
                    '<button id="done">Done: copy my changes</button>'
                    + ('<button class="alt" id="all">Let the designers pick all the visuals</button>'
                       if page_on else "")
                    + '</div><div id="outhint">If nothing was copied, click in the box, press Ctrl+A '
                      'then Ctrl+C, and paste it into the chat.</div><textarea id="out" readonly></textarea></div>')
    return (f'<div class="wrap{"" if current else " ro"}">' + "".join(notes)
            + '<div class="doc" id="doc"></div>' + done_box + "</div>"
            + f"<script>var D = {json.dumps(data, ensure_ascii=False)};</script>")


TAB1_JS = r"""
(function(){
var VS = D.visuals, doc = document.getElementById("doc");
function esc(t){ return String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;"); }
function sketch(v){ return '<svg class="sk" viewBox="0 0 92 52" fill="#64748B">' + (VS[v] || VS[D.any]) + '</svg>'; }
function ed(tag, cls, key, txt){ return "<" + tag + (cls ? ' class="' + cls + '"' : "") + (D.current ? ' contenteditable="true"' : "") + ' data-k="' + esc(key) + '">' + esc(txt) + "</" + tag + ">"; }
var h0 = '<h1 ' + (D.current ? 'contenteditable="true" ' : '') + 'data-k="title">' + esc(D.title) + '</h1>';
doc.insertAdjacentHTML("beforeend", h0);
var lastSec = "";
D.slides.forEach(function(s, i){
  var n = s.n, h = "";
  var rec = D.recorded[String(n)] || null;
  var v = rec ? rec.name : s.v, lock = rec ? rec.lock : s.lock, note = rec ? (rec.note || "") : s.note;
  if (s.sec && s.sec !== lastSec) { h += "<h2>" + esc(s.sec) + "</h2>"; lastSec = s.sec; }
  h += '<div class="slide" data-n="' + n + '"' + (s.needs && D.pageOn ? ' data-box="1"' : '') + '>' +
       '<h3><span class="num">' + n + '.</span>' + ed("span", "", "slide " + n + " headline", s.h) + "</h3>";
  if (s.claim) h += ed("p", "claim", "slide " + n + " claim", s.claim);
  if (s.b.length) h += "<ul>" + s.b.map(function(x, j){ return ed("li", "", "slide " + n + " point " + (j + 1), x); }).join("") + "</ul>";
  if (s.take) h += '<div class="take"><b>Takeaway:</b> ' + ed("span", "", "slide " + n + " takeaway", s.take) + "</div>";
  if (D.current) h += '<button class="cbtn">+ Comment on this slide</button><div class="comment"><textarea class="ctext" placeholder="Say what you want changed, in your own words"></textarea></div>';
  if (s.needs && D.pageOn) {
    var opts = Object.keys(VS).map(function(k){ return "<option" + (k === v ? " selected" : "") + ">" + esc(k) + "</option>"; }).join("");
    var r = D.reuse[String(n)], start = "";
    if (r) {
      var cur = rec && rec.reuse ? (rec.reuse.indexOf("new design") === 0 ? "new" : rec.reuse.indexOf("clean") >= 0 ? "clean" : "keep") : r.default;
      start = '<div style="margin-top:8px"><div class="lbl">Start from</div><div class="vrow">' +
        (r.thumb ? '<img class="thumb" src="' + esc(r.thumb) + '" alt="">' : '<span class="thumb">picture</span>') +
        '<select class="ssel"' + (D.current ? '' : ' disabled') + '>' +
        '<option value="keep"' + (cur === "keep" ? " selected" : "") + '>' + esc(r.label) + ', keep as is</option>' +
        '<option value="clean"' + (cur === "clean" ? " selected" : "") + '>' + esc(r.label) + ', clean it up</option>' +
        '<option value="new"' + (cur === "new" ? " selected" : "") + '>New design</option></select></div></div>';
    } else if (Object.keys(D.reuse).length) {
      start = '<div style="margin-top:8px"><div class="lbl">Start from</div><div class="newdesign">New design</div></div>';
    }
    var dis = D.current ? "" : " disabled";
    h += '<div class="pick"><div><div class="lbl">Visual</div><div class="vrow"><span class="skw">' + sketch(v) +
         '</span><div style="flex:1"><select class="vsel"' + dis + '>' + opts + '</select><div class="shows">' + esc(s.shows || "") + "</div></div></div>" + start + "</div>" +
         '<div><div class="lbl">Lock it?</div><div class="lock"><label><input type="radio" name="l' + i + '"' + (lock === "must use" ? "" : " checked") + dis + '> Suggestion</label><label><input type="radio" name="l' + i + '"' + (lock === "must use" ? " checked" : "") + dis + '> Must use</label></div>' +
         '<div class="lbl" style="margin-top:8px">Notes on the visual</div><textarea class="vnote" placeholder="Optional"' + dis + '>' + esc(note) + "</textarea></div></div>";
  }
  h += "</div>";
  doc.insertAdjacentHTML("beforeend", h);
});
document.querySelectorAll("[contenteditable]").forEach(function(el){ el.dataset.orig = el.textContent; });
document.addEventListener("input", function(e){
  var el = e.target; if (!el.dataset || el.dataset.orig === undefined) return;
  el.classList.toggle("edited", norm(el.textContent) !== norm(el.dataset.orig));
});
document.addEventListener("click", function(e){
  if (e.target.classList && e.target.classList.contains("cbtn")) { var c = e.target.nextElementSibling; c.classList.toggle("open"); if (c.classList.contains("open")) c.querySelector("textarea").focus(); }
});
function norm(t){ return String(t || "").replace(/\s+/g, " ").trim(); }
function boxes(){ return Array.prototype.slice.call(document.querySelectorAll(".slide[data-box]")); }
function update(){
  var counts = {}, heavy = 0, rep = 0, list = boxes();
  list.forEach(function(el, i){
    var v = el.querySelector(".vsel").value;
    el.querySelector(".skw").innerHTML = sketch(v);
    var sh = el.querySelector(".shows");  // the proposal's line fits only the proposal
    if (sh.dataset.v === undefined) { sh.dataset.v = v; sh.dataset.t = sh.textContent; }
    sh.textContent = v === sh.dataset.v ? sh.dataset.t : "";
    counts[v] = (counts[v] || 0) + 1; if (D.heavy.indexOf(v) >= 0) heavy++;
    el.classList.remove("flag"); var o = el.querySelector(".flagtxt"); if (o) o.remove();
    if (i > 0 && v !== D.any && list[i-1].querySelector(".vsel").value === v) {
      rep++; el.classList.add("flag");
      el.querySelector(".shows").insertAdjacentHTML("afterend", '<div class="flagtxt">Same kind of visual as the slide before</div>');
    }
  });
  if (!D.mixOn) return;
  document.getElementById("mix").innerHTML = Object.keys(counts).sort(function(a,b){ return counts[b]-counts[a]; }).map(function(k){ return "<span><b>" + counts[k] + "</b>" + esc(k) + "</span>"; }).join("");
  var m = document.getElementById("mixmsg");
  if (heavy * 3 > list.length) { m.className = "mixmsg bad"; m.textContent = "Tables and side-by-side boxes are " + heavy + " of " + list.length + " slides, more than a third. The deck will start to look the same."; }
  else if (rep) { m.className = "mixmsg bad"; m.textContent = rep + " slide(s) use the same kind of visual as the slide before (shaded)."; }
  else { m.className = "mixmsg ok"; m.textContent = "Good mix: no visual takes over and no two neighbors repeat."; }
}
document.addEventListener("change", update);
function collect(pickAll){
  var out = [D.header, "Folder: " + D.folder];
  var edits = Array.prototype.filter.call(document.querySelectorAll("[contenteditable]"), function(el){ return norm(el.textContent) !== norm(el.dataset.orig); });
  out.push(edits.length ? "Wording:" : "Wording: no changes");
  edits.forEach(function(el){ out.push("  " + el.dataset.k + ":\n    was: " + norm(el.dataset.orig) + "\n    now: " + norm(el.textContent)); });
  var cm = Array.prototype.filter.call(document.querySelectorAll(".slide"), function(s){ var t = s.querySelector(".ctext"); return t && t.value.trim(); });
  if (cm.length) { out.push("Comments:"); cm.forEach(function(s){ out.push("  slide " + s.dataset.n + ": " + norm(s.querySelector(".ctext").value)); }); }
  var list = boxes();
  if (list.length) {
    out.push(pickAll ? "Visuals: the designers pick every visual" : "Visuals:");
    list.forEach(function(el){
      var lock = el.querySelectorAll(".lock input")[1].checked ? "must use" : "suggestion";
      var v = el.querySelector(".vsel").value;
      if (pickAll) { v = D.any; lock = "suggestion"; }
      var ss = el.querySelector(".ssel"), note = norm(el.querySelector(".vnote").value);
      var start = ss ? "; start from: " + ss.options[ss.selectedIndex].text : (Object.keys(D.reuse).length ? "; start from: New design" : "");
      out.push("  slide " + el.dataset.n + ": " + v + " (" + lock + ")" + start + (note && !pickAll ? "; note: " + note : ""));
    });
  }
  out.push("(Claude: record it with record_storyline.py --out \"" + D.folder + "\" --message \"<this whole message>\")");
  return out.join("\n");
}
function show(t){
  var o = document.getElementById("out"); o.value = t; o.style.display = "block";
  document.getElementById("outhint").style.display = "block"; o.focus(); o.select();
  var ok = function(){ document.getElementById("outhint").textContent = "Copied. Paste it into the chat. (If it did not copy: click in the box, Ctrl+A, Ctrl+C.)"; };
  try { if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(ok, function(){ try { if (document.execCommand("copy")) ok(); } catch (e) {} }); else if (document.execCommand("copy")) ok(); } catch (e) {}
}
if (D.current) {
  document.getElementById("done").addEventListener("click", function(){ show(collect(false)); });
  var all = document.getElementById("all"); if (all) all.addEventListener("click", function(){ show(collect(true)); });
}
update();
})();
"""

PAGE_JS = r"""
(function(){
function go(id){
  document.querySelectorAll(".tab").forEach(function(t){ t.classList.toggle("on", t.dataset.p === id); });
  document.querySelectorAll(".pane").forEach(function(p){ p.classList.toggle("on", p.id === id); });
}
document.querySelectorAll(".tab").forEach(function(t){ t.addEventListener("click", function(){ go(t.dataset.p); history.replaceState(null, "", "#" + t.dataset.p); }); });
var want = (location.hash || "").replace("#", "");
if (want && document.getElementById(want)) go(want);
})();
"""


def _tab_label(stage: str, cur: str, done: bool) -> tuple[str, str]:
    order = STAGES.index
    if stage == cur:
        return "on", "now"
    if done or order(stage) < order(cur):
        return "", "done, read only"
    return "later", "not yet"


def write(out_dir: Path, stage: str | None = None) -> Path:
    """Write the one Slide Lab page for `stage` (storyline, designs, final),
    or for the stage last recorded. Returns its path. Never raises for a
    missing part: a tab without content shows a note instead."""
    out_dir = Path(out_dir)
    st = _ensure_ids(out_dir)
    one = _one(st)
    stage = stage or one.get("stage") or "designs"
    one["stage"] = stage
    one["written_at"] = datetime.now().isoformat(timespec="seconds")
    _state._write(out_dir, st)
    st = _state.read_state(out_dir)
    deck = deck_name(out_dir)
    sub = {"storyline": "edit the wording, pick the visuals",
           "designs": "pick a design per slide", "final": "the finished slides"}
    tabs, panes = [], []
    for s in STAGES:
        cls, word = _tab_label(s, stage, False)
        tabs.append(f'<div class="tab {cls}" data-p="{ANCHOR[s]}">{STAGES.index(s) + 1}. {TAB[s]}'
                    f'<small>{sub[s]}</small><span class="st">({word})</span></div>')
    # tab 1
    try:
        t1 = _storyline_tab(out_dir, stage, st)
    except Exception as exc:  # the page must still be written
        t1 = (f'<div class="wrap"><div class="box note">The storyline could not be shown '
              f"({html.escape(type(exc).__name__)}: {html.escape(str(exc))}).</div></div>")
    panes.append(f'<div class="pane scroll{" on" if stage == "storyline" else ""}" id="storyline">{t1}</div>')
    # tab 2
    review = _p.review_html(out_dir)
    if stage == "storyline":
        t2 = ('<div class="wrap"><div class="box later-note">This tab is the slide design review: '
              "pick a design per slide, Replace, +3 designs, comments. It opens once tab 1 is "
              "done and the designs are ready.</div></div>")
        panes.append(f'<div class="pane scroll" id="designs">{t2}</div>')
    elif review.exists() and one.get("designs_ready"):
        ro = None if stage == "designs" else (
            "Done: your picks are recorded. This tab is read only now; the final check is tab 3.")
        panes.append(f'<div class="pane frame{" on" if stage == "designs" else ""}" id="designs">'
                     + _embedded(review, ro) + "</div>")
    else:
        t2 = ('<div class="wrap"><div class="box later-note">The designers are working on the '
              "slides. This tab fills in when the designs are ready.</div></div>")
        panes.append(f'<div class="pane scroll{" on" if stage == "designs" else ""}" id="designs">{t2}</div>')
    # tab 3
    final = out_dir / "FINAL-CHECK.html"
    if stage == "final" and final.exists() and one.get("final_ready"):
        panes.append('<div class="pane frame on" id="final">' + _embedded(final, None) + "</div>")
    else:
        msg = ("This tab is the final check: the finished slides on your template, exactly what "
               "will be built. It opens after you pick the designs."
               if stage != "final" else
               "The picked designs are being finished on your template. This tab fills in when "
               "they are ready.")
        panes.append(f'<div class="pane scroll{" on" if stage == "final" else ""}" id="final">'
                     f'<div class="wrap"><div class="box later-note">{msg}</div></div></div>')
    page = ("<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<title>Slide Lab: {html.escape(deck)}</title>"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<style>{CSS}</style></head><body>"
            f'<div class="topbar"><div class="toprow"><div class="t">Slide Lab: {html.escape(deck)}</div>'
            f'<div class="stage">Now: tab {STAGES.index(stage) + 1}, {TAB[stage]}</div></div>'
            f'<div class="tabs">{"".join(tabs)}</div></div>'
            + "".join(panes)
            + f"<script>{TAB1_JS}{PAGE_JS}</script></body></html>")
    dest = page_path(out_dir)
    dest.write_text(page, encoding="utf-8")
    return dest


def mark_part_ready(out_dir: Path, part: str) -> None:
    """REVIEW.html (part "designs") or FINAL-CHECK.html ("final") was just
    written for the current build."""
    st = _ensure_ids(out_dir)
    _one(st)[f"{part}_ready"] = True
    if part == "designs":
        _one(st).pop("final_ready", None)
    _state._write(out_dir, st)


def forget_parts(out_dir: Path) -> None:
    """A new prep: the old designs and final check are not this build's any more."""
    st = _state.read_state(out_dir)
    one = st.get("one_page")
    if one:
        one.pop("designs_ready", None)
        one.pop("final_ready", None)
        _state._write(out_dir, st)


def open_page(path: Path) -> str:
    """Open the one page in the user's browser (same rules as build_review)."""
    import build_review
    return build_review._open_page(path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="The one Slide Lab page of a build.")
    ap.add_argument("cmd", choices=["show", "write"])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--stage", choices=STAGES, default=None)
    a = ap.parse_args(argv)
    if a.cmd == "write":
        p = write(a.out, a.stage)
        print(f"Slide Lab page: {p}")
        return 0
    st = _state.read_state(a.out)
    print(f"Slide Lab page: {page_path(a.out)}")
    print(f"  stage: {(st.get('one_page') or {}).get('stage') or '(not written yet)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
