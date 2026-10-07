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

Run (the page gives you this exact command):
  py -3 scripts/record_picks.py --out <out_dir> --approved "Picks: 1B 2C ... (check 1a2b3c4d)"
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
    args = ap.parse_args(argv)
    out = args.out
    if not out.exists():
        print(f"ERROR: out dir not found: {out}")
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

    (out / "picks.json").write_text(json.dumps(picks, indent=2), encoding="utf-8")
    _state.record_picks(out, picks, all_options=all_options,
                        via="chat" if chat_bound else "page")
    if chat_bound:
        _state.record_chat_approval(out, "picks", args.approved_in_chat.strip(), chat_bound)

    # What happens next. Only picked sketch designs are translated.
    to_translate = []
    for k, v in picks.items():
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
    print("\nNext:")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
