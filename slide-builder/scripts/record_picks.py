#!/usr/bin/env python3
"""record_picks.py — record the user's picks exactly as they made them.

REVIEW.html's "Build my deck" button copies a command that runs this script
with a line like:

    PICKS slide_01=A;slide_02=C CHECK 1a2b3c4d

CHECK is computed in the page from the review token and those exact picks. This
script recomputes it and refuses on any difference, so a pick list that was
mistyped, hand-edited, or made up never gets recorded. Picks used to be
transcribed into picks.json by hand, and one build recorded slide 2 as B when
the user had picked A.

It also refuses unless every slide has a pick: a partial list used to compile
into a shorter deck with nothing saying so.

A slide may keep several options ("Picks: 1BC 2A", canonical
"slide_01=BC;slide_02=A"): the user wants B and C of slide 1, not A. That is
recorded as their choice and compiled as a labeled all-options deck of exactly
those options; nothing is moved aside and no override is logged. The page's
"All options in one deck" mode writes this line from a keep / leave-out switch
on every option. `PICKS ALL CHECK ...` (every option on disk) is still accepted.

Chat approval (owner's decision D2, 2026-10-06): when REVIEW.html was built and
opened for the current designs (build_review.py --open) and the user types
their picks in chat ("build B and C", "use 1A 2C"), record them with

  py -3 scripts/record_picks.py --out <out_dir> --approved-in-chat "<the user's words>" --picks "1BC"

The words are recorded verbatim, bound to the review token and the option files
the opened page showed. Refused when the page was not opened, is from before a
rebuild, or a slide's options changed since; and when a picked letter does not
appear in the user's words (the picks must be theirs, not inferred).

Comments before conversion (owner's decision, 2026-10-09). The page's message
carries a "Feedback:" block (quick-feedback chips and typed notes per slide).
Pass the WHOLE message to --approved so it is read; in chat, pass each comment
the user typed as --comment "N: <their words>". A picked slide with comments is
recorded as "edit first" and is NOT converted: one worker edits the picked
design in place (same layout, same letter, the comments applied), its sketch is
re-rendered, and then

  py -3 scripts/record_picks.py --out <out_dir> --edits-done

checks every such slide's design changed, marks its comments applied, and
converts the edited picks together in one call. A comment that asks for a
different design ("try a chart instead", the "Wrong layout / structure" chip)
is a Replace request instead: the slide's pick is not kept, the comment goes
to slide_NN/_prior_feedback.md, and a redesign round is recorded (ask the user
one or three new designs, three preselected). Every comment is recorded in the
build record and listed at delivery by check_done.py; none is dropped.

Run (the page gives you this exact command):
  py -3 scripts/record_picks.py --out <out_dir> --approved "<the whole message: Picks line + Feedback>"
  (the older "PICKS slide_01=B;... CHECK ..." form is still accepted)
Exit: 0 recorded | 5 refused | 2 bad usage
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _paths as _p  # noqa: E402
import _state  # noqa: E402

LINE_RE = re.compile(r"PICKS\s+(\S+)\s+CHECK\s+([0-9a-fA-F]{8})")
# The plain line the review page copies now: "Picks: 1B 2C 3- 4A (check 1a2b3c4d)"
# ("3-" = left out, "1BC" = keep options B and C of slide 1) or
# "Picks: all options (check ...)". Same check code.
PLAIN_RE = re.compile(r"Picks:\s*(.+?)\s*\(check\s+([0-9a-fA-F]{8})\)", re.I)


# The page's chip that asks for another structure, and words that ask for a
# different design rather than an edit of this one. Those comments are a
# Replace request (owner's decision, 2026-10-08), not an edit in place.
REDESIGN_CHIP = "Wrong layout / structure"
REDESIGN_RE = re.compile(
    r"\b(?:"
    r"try (?:a|an|another|some)\b[^.;]*\binstead"
    r"|(?:a|an|as an?) [\w-]+(?: [\w-]+)? instead\b"
    r"|instead of (?:this|the|a) (?:layout|design|structure|format)"
    r"|(?:different|another|new|other) (?:design|layout|structure|approach|format|option)s?"
    r"|re-?design|start (?:over|again)|from scratch"
    r"|wrong (?:layout|structure|design)"
    r"|(?:make|turn) (?:it|this) (?:in)?to (?:a|an) (?:chart|table|diagram|timeline|graph)"
    r")", re.I)


def parse_feedback(text: str) -> dict:
    """{slide_NN: {field: value}} from the page's "Feedback:" block:

        Feedback:
          slide_02:
            quick: Too dense, simplify; Fix a number / wording
            headline: shorter title

    Indentation may be lost in a paste; a line that is only "slide_NN:" starts
    a slide, "field: value" lines belong to the last slide."""
    out: dict[str, dict] = {}
    lines = (text or "").splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip().lower() == "feedback:")
    except StopIteration:
        return out
    cur = None
    for ln in lines[start + 1:]:
        s = ln.strip()
        if not s:
            continue
        m = re.fullmatch(r"(slide_\d{2,3}):", s)
        if m:
            cur = _p.slide_key(int(m.group(1).split("_")[1]))
            out.setdefault(cur, {})
            continue
        m = re.fullmatch(r"([a-z_]+):\s*(.*)", s)
        if m and cur and m.group(2).strip():
            out[cur][m.group(1)] = m.group(2).strip()
            continue
        if re.match(r"(Picks|Keep|Folder|Build|Deck|Final check):", s, re.I):
            break
        if cur and out[cur]:                  # a wrapped note: keep it with the last field
            k = list(out[cur])[-1]
            out[cur][k] += " " + s
    return {k: v for k, v in out.items() if v}


def comment_text(fields: dict) -> str:
    """One line for the record: "quick: ...; headline: ..."."""
    return " | ".join(f"{k}: {v}" for k, v in fields.items())


def asks_for_redesign(fields: dict) -> bool:
    chips = [c.strip() for c in (fields.get("quick") or "").split(";")]
    if any(c.startswith(REDESIGN_CHIP) for c in chips):
        return True
    typed = " ".join(v for k, v in fields.items() if k != "quick")
    return bool(REDESIGN_RE.search(typed))


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def chat_comments(words: str, comment_args: list) -> tuple[dict, str]:
    """{slide_NN: {"note": text}} from --comment "N: text", each of which must
    be the user's own words (it must appear in what they typed)."""
    out: dict[str, dict] = parse_feedback(words)
    for raw in comment_args or []:
        m = re.fullmatch(r"\s*(\d{1,3})\s*:\s*(.+)", raw or "", re.S)
        if not m:
            return {}, (f'--comment looks like "3: make the title shorter", not {raw!r}.')
        text = m.group(2).strip()
        if _norm(text) not in _norm(words):
            return {}, (f"--comment {raw!r} is not in the user's words. Pass what they "
                        "typed for that slide, verbatim; if it is unclear, ask.")
        sid = _p.slide_key(int(m.group(1)))
        fields = out.setdefault(sid, {})
        fields["note"] = (fields["note"] + "; " + text) if fields.get("note") else text
    return out, ""


def _plain_body(raw: str) -> str:
    """Canonical body from the plain pick list ("1B 2C 3-", "1BC 2A", "all").
    Returns "ALL", the canonical body, or "BAD:<token>"."""
    raw = (raw or "").strip()
    if raw.lower().startswith("all"):
        return "ALL"
    pairs = []
    for tok in raw.replace(",", " ").split():
        mm = re.fullmatch(r"(\d{1,3})([A-Fa-f]+|-)", tok)
        if not mm:
            return "BAD:" + tok
        v = mm.group(2).upper()
        pairs.append((int(mm.group(1)), v if v == "-" else "".join(sorted(set(v)))))
    if not pairs:
        return "BAD:" + raw
    return ";".join(f"slide_{n:02d}={L}" for n, L in sorted(pairs))


def _from_plain(text: str):
    """(canonical body, check) from the plain line, or None."""
    m = PLAIN_RE.search(text or "")
    if not m:
        return None
    return _plain_body(m.group(1)), m.group(2)


def _letters_on_disk(slide_dir: Path) -> list[str]:
    """Option letters that exist for a slide, from any of its option files."""
    found = set()
    for p in slide_dir.glob("option_*"):
        m = re.match(r"option_([A-F])(?:[._])", p.name)
        if m and p.is_file():
            found.add(m.group(1))
    return sorted(found)


def _letters_in_words(words: str) -> set[str]:
    """Option letters the user's words name: "B and C", "1BC 2A", "option b".
    Deliberately loose (an article "a" counts as A): it only catches picks the
    user never mentioned, not every possible misreading."""
    found: set[str] = set()
    for m in re.finditer(r"(?<![A-Za-z])\d*([A-Fa-f]+)(?![A-Za-z])", words or ""):
        found.update(m.group(1).upper())
    return found


def _chat_body(words: str, picks_arg: str) -> tuple[str, str]:
    """(canonical body, refusal) for a chat approval."""
    if not (words or "").strip():
        return "", "--approved-in-chat needs the user's own words, verbatim."
    if not (picks_arg or "").strip():
        return "", ('--approved-in-chat needs --picks, the user\'s picks as a pick list, '
                    'e.g. --picks "1BC" or --picks "1A 2C 3-".')
    body = _plain_body(picks_arg)
    if body.startswith("BAD:"):
        return "", (f"malformed pick {body[4:]!r}. --picks looks like \"1A 2C\", "
                    "\"1BC 2A\" (several options kept) or \"3-\" (left out).")
    if body == "ALL":
        if not re.search(r"\b(all|every|each)\b", words, re.I):
            return "", ("--picks says all options, but the user's words do not say "
                        "all. Record only what they asked for.")
        return body, ""
    named = _letters_in_words(words)
    picked = {L for pair in body.split(";") for L in pair.partition("=")[2] if L != "-"}
    unnamed = sorted(picked - named)
    if unnamed:
        return "", (f"--picks names option(s) {', '.join(unnamed)}, which the user's words "
                    "do not mention. Record the user's own choice; if it is unclear, ask.")
    return body, ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Record the user's approved picks.")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--approved", default=None,
                    help='The "Picks: ... (check ...)" line from REVIEW.html.')
    ap.add_argument("--approved-in-chat", default=None, dest="approved_in_chat",
                    help="The user's own words typed in chat, verbatim, with REVIEW.html "
                         "open for the current designs (build_review.py --open). Needs --picks.")
    ap.add_argument("--picks", default=None,
                    help='With --approved-in-chat: the user\'s picks, e.g. "1A 2C", "1BC" '
                         '(keep B and C of slide 1) or "3-" (leave slide 3 out).')
    ap.add_argument("--comment", action="append", default=[],
                    help='With --approved-in-chat: a comment the user typed for one slide, '
                         '"N: <their words>" (repeat per slide). It must appear in their words.')
    ap.add_argument("--edits-done", action="store_true", dest="edits_done",
                    help="The picked slides with comments were edited in place: check, mark "
                         "the comments applied, convert them together.")
    args = ap.parse_args(argv)
    out = args.out
    if not out.exists():
        print(f"ERROR: out dir not found: {out}")
        return 2
    if args.edits_done:
        if args.approved or args.approved_in_chat:
            print("ERROR: --edits-done takes only --out.")
            return 2
        return edits_done(out)
    if args.comment and not args.approved_in_chat:
        print("ERROR: --comment goes with --approved-in-chat; the page's message carries "
              "its comments in its Feedback block.")
        return 2
    if bool(args.approved) == bool(args.approved_in_chat):
        print("ERROR: give exactly one of --approved (the line the page copied) or "
              "--approved-in-chat (the user's words) with --picks.")
        return 2
    if args.picks and not args.approved_in_chat:
        print("ERROR: --picks goes with --approved-in-chat; the page's line carries its own picks.")
        return 2

    state = _state.read_state(out)
    review = state.get("review") or {}
    if not review.get("token"):
        print("REFUSED: no review recorded for this build. Run build_review.py and "
              "have the user pick in REVIEW.html.")
        return 5
    if state.get("content_hash") and review.get("content_hash") != state.get("content_hash"):
        print("REFUSED: the review page is from before the latest rebuild. Run "
              "build_review.py again and have the user pick on the current page.")
        return 5

    meta = json.loads(_p.meta_json(out).read_text(encoding="utf-8"))
    slide_ns = sorted(s["n"] for s in meta.get("slides", []) if isinstance(s.get("n"), int))
    if meta.get("adopted_source"):
        # An adopted external deck: only the slides being rebuilt need a pick.
        slide_ns = [n for n in slide_ns if _letters_on_disk(_p.slide_dir(out, n))]

    chat_bound = None
    if args.approved_in_chat:
        words = args.approved_in_chat.strip()
        body, why = _chat_body(words, args.picks)
        if why:
            print("REFUSED: " + why)
            return 5
        stamps_now = {_p.slide_key(n): _state.option_files_stamp(_p.slide_dir(out, n))
                      for n in slide_ns}
        ok, why = _state.check_page_opened(state, "review", stamps_now)
        if not ok:
            print("REFUSED: " + why + " (Or have them click Build my deck and paste its "
                  "line, which runs this with --approved.)")
            return 5
        chat_bound = {"page": "REVIEW.html", "review_token": review["token"],
                      "stamps": stamps_now, "picks": body}
    else:
        m = LINE_RE.search(args.approved or "")
        plain = None if m else _from_plain(args.approved)
        if not m and not plain:
            print("REFUSED: that is not an approval line from REVIEW.html. It looks "
                  'like "Picks: 1A 2C 3B (check 1a2b3c4d)".')
            return 5
        if m:
            body, check = m.group(1), m.group(2).lower()
        else:
            body, check = plain[0], plain[1].lower()
            if body.startswith("BAD:"):
                print(f"REFUSED: malformed pick {body[4:]!r}.")
                return 5
        if _state.approval_check(review["token"], body) != check:
            print("REFUSED: the picks do not match their check code. They were changed "
                  "after the user clicked Build, or copied from a different review page. "
                  "Ask the user to click Build my deck again on the current REVIEW.html.")
            return 5

    if body == "ALL":
        picks = {}
        for n in slide_ns:
            letters = _letters_on_disk(_p.slide_dir(out, n))
            if not letters:
                print(f"REFUSED: slide {n} has no options to include.")
                return 5
            picks[_p.slide_key(n)] = letters
        if all(len(v) <= 1 for v in picks.values()):
            print("REFUSED: every slide has one option, so an all-options deck is just "
                  "the final deck. Pick in REVIEW.html instead.")
            return 5
        all_options = True
    else:
        raw: dict[str, str] = {}
        for pair in body.split(";"):
            k, _, v = pair.partition("=")
            # "-" means the user chose Leave out for this slide; several letters
            # mean they kept several options of it.
            if not re.fullmatch(r"slide_\d{2}", k) or not re.fullmatch(r"[A-F]+|-", v):
                print(f"REFUSED: malformed pick {pair!r}.")
                return 5
            if v != "-" and len(set(v)) != len(v):
                print(f"REFUSED: malformed pick {pair!r} (a letter twice).")
                return 5
            raw[k] = v
        missing = [n for n in slide_ns if _p.slide_key(n) not in raw]
        if missing:
            print(f"REFUSED: {len(missing)} slide(s) have no pick: "
                  f"{', '.join(str(n) for n in missing)}. Every slide needs a pick "
                  "(or 'Replace these', which rebuilds it before anything compiles).")
            return 5
        for k, v in raw.items():
            if v == "-":
                continue
            on_disk = _letters_on_disk(out / k)
            for L in v:
                if L not in on_disk:
                    print(f"REFUSED: {k} has no option {L}.")
                    return 5
        if all(v == "-" for v in raw.values()):
            print("REFUSED: every slide is marked Leave out; there is nothing to build.")
            return 5
        # Several options kept on any slide: a labeled deck of exactly the kept
        # options (compile --all-variations --badge), every slide as a list.
        all_options = any(len(v) > 1 for v in raw.values() if v != "-")
        if all_options:
            picks = {k: (v if v == "-" else sorted(v)) for k, v in raw.items()}
        else:
            picks = dict(raw)

    # The user's comments, per slide (the page's Feedback block, or what they
    # typed in chat). Read before anything is converted.
    if chat_bound:
        fb, why = chat_comments(args.approved_in_chat, args.comment)
        if why:
            print("REFUSED: " + why)
            return 5
    else:
        fb = parse_feedback(args.approved or "")
    unknown = sorted(k for k in fb if k not in picks)
    if unknown:
        print(f"REFUSED: comments for {', '.join(unknown)}, which is not a slide of this "
              "review. Check the Feedback block came from this page.")
        return 5
    entries, edit_sids, redesign_sids = [], [], []
    for sid in sorted(fb):
        v = picks[sid]
        letters = "".join(v) if isinstance(v, list) else v
        kind = ("left_out" if v == "-" else
                "redesign" if asks_for_redesign(fb[sid]) else "edit")
        entries.append({"slide": sid, "letters": "" if v == "-" else letters,
                        "text": comment_text(fb[sid]), "kind": kind,
                        "letters_on_disk": "".join(_letters_on_disk(out / sid)),
                        "via": "chat" if chat_bound else "page"})
        (edit_sids if kind == "edit" else redesign_sids if kind == "redesign" else []).append(sid)

    # Comments from an earlier round that asked for a redesign are applied once
    # the slide has new designs (the user is now picking among them).
    st0 = _state.read_state(out)
    for c in _state.pending_comments(st0, "redesign"):
        if c["slide"] not in redesign_sids and \
                _state.option_files_stamp(out / c["slide"]) != c.get("stamp"):
            _state.mark_comments_applied(out, c["slide"], "redesigned: new designs made "
                                         "from the comment and picked by the user", "redesign")

    (out / "picks.json").write_text(json.dumps(picks, indent=2), encoding="utf-8")
    _state.record_picks(out, picks, all_options=all_options,
                        via="chat" if chat_bound else "page")
    if chat_bound:
        _state.record_chat_approval(out, "picks", args.approved_in_chat.strip(), chat_bound)
    _state.reset_auto_qc_rounds(out)
    stored = _state.record_comments(out, entries) if entries else []
    by_sid = {}
    for c in stored:
        by_sid.setdefault(c["slide"], []).append(c)
    for sid in edit_sids:
        _write_edit_request(out, sid, picks[sid], by_sid.get(sid, []))
    if redesign_sids:
        for sid in redesign_sids:
            _write_redesign_feedback(out, sid, by_sid.get(sid, []))
        _state.forget_picks(out, redesign_sids)
        state = _state.read_state(out)
        state["redesign_round"] = {
            "slides": sorted(int(s.split("_")[1]) for s in redesign_sids),
            "kept": {k: v for k, v in picks.items() if k not in redesign_sids},
            "from_comments": True}
        _state._write(out, state)
    else:
        state = _state.read_state(out)
        if state.pop("redesign_round", None) is not None:
            _state._write(out, state)   # a full pick list ends any earlier round

    # What happens next. Only picked sketch designs are translated, and not
    # yet on a slide whose comments come first.
    held = set(edit_sids) | set(redesign_sids)
    to_translate = []
    for k, v in picks.items():
        if k in held:
            continue
        for L in (v if isinstance(v, list) else [v]):
            if L == "-":
                continue
            sd = out / k
            if (sd / f"option_{L}.html").exists() and not (sd / f"option_{L}_native.py").exists():
                to_translate.append(f"{k}/option_{L}.html")
    n_opts = sum(len(v) if isinstance(v, list) else (0 if v == "-" else 1)
                 for v in picks.values())
    n_out = sum(1 for v in picks.values() if v == "-")
    n_multi = sum(1 for v in picks.values() if isinstance(v, list) and len(v) > 1)
    what = ("ALL options" if body == "ALL"
            else f"picks ({n_multi} slide(s) keep several options; a labeled deck)"
            if all_options else "picks")
    print(f"[ok] recorded {what}"
          + (" from the user's words in chat" if chat_bound else "")
          + f": {n_opts} option(s) across {len(picks) - n_out} slide(s)"
          + (f"; {n_out} slide(s) left out by the user." if n_out else "."))
    for c in stored:
        label = {"edit": "EDIT FIRST (not converted yet)",
                 "redesign": "asks for a different design: a Replace request",
                 "left_out": "on a slide left out; nothing to apply"}[c["kind"]]
        print(f"  comment on {c['slide']}: {label}: {c['text'][:160]}")
    print("\nNext:")
    step = _convert_and_list(out, to_translate)
    if redesign_sids or edit_sids:
        _print_comment_steps(out, meta, edit_sids, redesign_sids, step)
        return 0
    _print_finish_steps(out, meta, picks, step)
    return 0


def _write_edit_request(out: Path, sid: str, pick, comments: list) -> Path:
    """slide_NN/_edit_request.md: what the worker applies to the picked design."""
    letters = pick if isinstance(pick, list) else [pick]
    sd = out / sid
    files = []
    for L in letters:
        for name in (f"option_{L}.html", f"option_{L}.py"):
            if (sd / name).exists():
                files.append(sd / name)
    lines = [f"# Edit request: {sid}, option(s) {', '.join(letters)} (EDIT IN PLACE)", "",
             "The user picked this design and commented on it. Edit the picked file(s) "
             "IN PLACE: keep the same layout and structure, apply every comment below, "
             "keep the option letter, do not write other options. Then re-render the "
             "sketch (scripts/render_html.py) for a sketch design.", "",
             "Files to edit:"] + [f"    {f}" for f in files] + ["", "Comments (the user's):"]
    lines += [f"- {c['text']}" for c in comments]
    p = sd / "_edit_request.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def _write_redesign_feedback(out: Path, sid: str, comments: list) -> Path:
    """The comment goes to _prior_feedback.md, which the redesign's worker reads."""
    p = out / sid / "_prior_feedback.md"
    prev = p.read_text(encoding="utf-8") if p.exists() else ""
    add = "\n".join(f"- {c['text']}" for c in comments)
    if add and add not in prev:
        p.write_text((prev.rstrip() + "\n\n" if prev.strip() else "")
                     + "## The user's comment on the review page (asks for a new design)\n"
                     + add + "\n", encoding="utf-8")
    return p


def _print_comment_steps(out: Path, meta: dict, edit_sids, redesign_sids, step: int) -> None:
    tpl = meta.get("template") or "<template>"
    if edit_sids:
        print(f"  {step}. Edit first: dispatch one slide-builder-worker per slide in EDIT MODE "
              "(at most 20 at a time), each on its _edit_request.md (edit the PICKED design "
              "in place, same layout, apply the comments, letter unchanged), then render "
              "each edited sketch:")
        for sid in edit_sids:
            print(f"       {out / sid / '_edit_request.md'}")
        print(f"  {step + 1}. py -3 scripts/record_picks.py --out \"{out}\" --edits-done")
        print("     (it checks each design changed, marks the comments applied and converts "
              "the edited picks together)")
        step += 2
    if redesign_sids:
        nums = ",".join(str(int(s.split("_")[1])) for s in redesign_sids)
        print(f"  {step}. Slide(s) {nums}: the comment asks for a different design, so it is "
              "a Replace request; that pick is not kept. ASK THE USER: \"One new design or "
              "three?\" with THREE preselected (owner's decision, 2026-10-08). The comment is "
              "in slide_NN/_prior_feedback.md; the redesign round is recorded.")
        print(f"     For each: py -3 scripts/build_deck.py --slide N --out \"{out}\" "
              f"--template \"{tpl}\" --options 3 (or 1), its worker, the sketch render.")
        print(f"     Three: py -3 scripts/build_review.py --out \"{out}\" --open (the other "
              "picks are preselected); one: py -3 scripts/redesign_round.py finish "
              f"--out \"{out}\"" + (" after --edits-done." if edit_sids else "."))
    else:
        print(f"  {step}. Then finalize_deck.py and build_review.py --final --open "
              "(--edits-done prints them).")


def _print_finish_steps(out: Path, meta: dict, picks: dict, step: int) -> None:
    tpl = meta.get("template") or "<template>"
    if meta.get("adopted_source"):
        # An adopted deck: finalize only the slides being rebuilt. A full
        # finalize exits 11 there, because the other slides have no options.
        for k in sorted(k for k, v in picks.items() if v != "-"):
            print(f"  {step}. py -3 scripts/finalize_deck.py --out \"{out}\" "
                  f"--template \"{tpl}\" --slide {int(k.split('_')[1])}")
    else:
        print(f"  {step}. py -3 scripts/finalize_deck.py --out \"{out}\" --template \"{tpl}\"")
    print(f"  {step + 1}. py -3 scripts/build_review.py --out \"{out}\" --final --open")
    print("     Tell the user FINAL-CHECK.html is open and wait for its Build it message "
          "(or for them to say \"build it\" in chat).")


def edits_done(out: Path) -> int:
    """The edit-first slides were edited in place: verify, record, convert."""
    state = _state.read_state(out)
    pend = _state.pending_comments(state, "edit")
    if not pend:
        print("Nothing to do: no picked slide is waiting on an edit from the user's comments.")
        return 0
    try:
        picks = json.loads((out / "picks.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        print("REFUSED: no picks.json; record the picks first.")
        return 5
    sids = sorted({c["slide"] for c in pend})
    for sid in sids:
        cs = [c for c in pend if c["slide"] == sid]
        now = _state.option_files_stamp(out / sid)
        if all(now == c.get("stamp") for c in cs):
            print(f"REFUSED: {sid}'s design has not changed since the comments were recorded, "
                  "so they are not applied yet. Dispatch the worker on "
                  f"{out / sid / '_edit_request.md'} first.")
            return 5
        letters_now = "".join(_letters_on_disk(out / sid))
        if any(c.get("letters_on_disk") and c["letters_on_disk"] != letters_now for c in cs):
            print(f"REFUSED: {sid}'s options changed ({cs[0]['letters_on_disk']} -> "
                  f"{letters_now}). An edit in place keeps the picked option and its letter; "
                  "new designs are a Replace round.")
            return 5
    for sid in sids:
        v = picks.get(sid)
        letters = ", ".join(v) if isinstance(v, list) else str(v)
        _state.mark_comments_applied(out, sid, f"edited in place (option {letters} kept, "
                                     "same layout, the comments applied)", "edit")
        _state.mark_edited_in_place(out, sid)
        # The review record's stamps move on too: the user's pick stands.
        st = _state.read_state(out)
        opened = ((st.get("review") or {}).get("opened") or {})
        if sid in (opened.get("stamps") or {}):
            opened["stamps"][sid] = _state.option_files_stamp(out / sid)
            _state._write(out, st)
        rq = out / sid / "_edit_request.md"
        if rq.exists():
            rq.replace(rq.with_name("_edit_request.applied.md"))
    print(f"[ok] comments applied on {len(sids)} slide(s): {', '.join(sids)}; picks kept.")
    # Convert every pick whose design has not been converted from its current
    # version, in one call (one browser, one self-check pass).
    import translate_html
    to_translate = []
    for k, v in picks.items():
        for L in (v if isinstance(v, list) else [v]):
            html = out / k / f"option_{L}.html"
            if L != "-" and html.exists() and translate_html.needs_conversion(html, out / k, L):
                to_translate.append(f"{k}/option_{L}.html")
    meta = json.loads(_p.meta_json(out).read_text(encoding="utf-8"))
    print("\nNext:")
    step = _convert_and_list(out, to_translate)
    rr = _state.read_state(out).get("redesign_round") or {}
    if rr.get("slides"):
        print(f"  {step}. A redesign is still recorded for slide(s) "
              f"{', '.join(map(str, rr['slides']))}: finish it as record_picks printed "
              "(redesign_round.py finish, or build_review.py --open for three designs).")
        return 0
    _print_finish_steps(out, meta, picks, step)
    return 0


def _convert_and_list(out: Path, to_translate: list) -> int:
    """Convert (script mode) or list (agent mode) these picked sketches, all in
    one call. Returns the next step number."""
    step = 1
    if to_translate and _p.translator_mode() == "script":
        # Translate the picked sketches right here: a script, seconds each, no
        # agents. Only elements it can't draw go to the agent (fallback mode).
        import translate_html
        jobs = []
        for t in to_translate:
            slide_key, html_name = t.split("/")
            n = int(slide_key.split("_")[1])
            letter = html_name.split("_")[1].split(".")[0]
            jobs.append(translate_html.job_for(out, n, letter))
        reports = translate_html.translate_many(jobs)
        pending = [r for r in reports if r["needs_agent"]]
        print(f"  translated {len(reports)} picked sketch design(s) with translate_html.py"
              + (f"; {len(pending)} still need the agent for some elements" if pending else ""))
        if pending:
            print(f"  {step}. Dispatch slide-builder-translator in FALLBACK MODE on each of "
                  f"these (it draws only the listed elements; at most 20 at a time):")
            for r in pending:
                html = Path(r["html"])
                print(f"       {html.with_name(html.stem + '_native.py')}  "
                      f"({len(r['fallback'])} element(s): "
                      + "; ".join(f["reason"] for f in r["fallback"][:3]) + ")")
            step += 1
    elif to_translate:
        print(f"  {step}. Dispatch slide-builder-translator on each of these "
              f"({len(to_translate)}; at most 20 at a time):")
        for t in to_translate:
            print(f"       {out / t}")
        step += 1
    return step


if __name__ == "__main__":
    sys.exit(main())
