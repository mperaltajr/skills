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

"All options in one deck" sends `PICKS ALL CHECK ...` instead. That deck
converts every option, not only the picks, so it costs several times the
tokens; the page warns before sending it.

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
# ("3-" = left out) or "Picks: all options (check ...)". Same check code.
PLAIN_RE = re.compile(r"Picks:\s*(.+?)\s*\(check\s+([0-9a-fA-F]{8})\)", re.I)


def _from_plain(text: str):
    """(canonical body, check) from the plain line, or None."""
    m = PLAIN_RE.search(text or "")
    if not m:
        return None
    raw, check = m.group(1).strip(), m.group(2)
    if raw.lower().startswith("all"):
        return "ALL", check
    pairs = []
    for tok in raw.replace(",", " ").split():
        mm = re.fullmatch(r"(\d{1,3})([A-Fa-f]|-)", tok)
        if not mm:
            return ("BAD:" + tok), check
        pairs.append((int(mm.group(1)), mm.group(2).upper()))
    body = ";".join(f"slide_{n:02d}={L}" for n, L in sorted(pairs))
    return body, check


def _letters_on_disk(slide_dir: Path) -> list[str]:
    """Option letters that exist for a slide, from any of its option files."""
    found = set()
    for p in slide_dir.glob("option_*"):
        m = re.match(r"option_([A-F])(?:[._])", p.name)
        if m and p.is_file():
            found.add(m.group(1))
    return sorted(found)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Record the user's approved picks.")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--approved", required=True,
                    help='The "PICKS ... CHECK ..." line from REVIEW.html.')
    args = ap.parse_args(argv)
    out = args.out
    if not out.exists():
        print(f"ERROR: out dir not found: {out}")
        return 2

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
    if _state.approval_check(review["token"], body) != check:
        print("REFUSED: the picks do not match their check code. They were changed "
              "after the user clicked Build, or copied from a different review page. "
              "Ask the user to click Build my deck again on the current REVIEW.html.")
        return 5

    meta = json.loads(_p.meta_json(out).read_text(encoding="utf-8"))
    slide_ns = sorted(s["n"] for s in meta.get("slides", []) if isinstance(s.get("n"), int))
    if meta.get("adopted_source"):
        # An adopted external deck: only the slides being rebuilt need a pick.
        slide_ns = [n for n in slide_ns if _letters_on_disk(_p.slide_dir(out, n))]

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
        picks = {}
        for pair in body.split(";"):
            k, _, v = pair.partition("=")
            # "-" means the user chose Leave out for this slide.
            if not re.fullmatch(r"slide_\d{2}", k) or not re.fullmatch(r"[A-F]|-", v):
                print(f"REFUSED: malformed pick {pair!r}.")
                return 5
            picks[k] = v
        missing = [n for n in slide_ns if _p.slide_key(n) not in picks]
        if missing:
            print(f"REFUSED: {len(missing)} slide(s) have no pick: "
                  f"{', '.join(str(n) for n in missing)}. Every slide needs a pick "
                  "(or 'Replace these', which rebuilds it before anything compiles).")
            return 5
        for k, v in picks.items():
            if v != "-" and v not in _letters_on_disk(out / k):
                print(f"REFUSED: {k} has no option {v}.")
                return 5
        if all(v == "-" for v in picks.values()):
            print("REFUSED: every slide is marked Leave out; there is nothing to build.")
            return 5
        all_options = False

    (out / "picks.json").write_text(json.dumps(picks, indent=2), encoding="utf-8")
    _state.record_picks(out, picks, all_options=all_options)

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
    print(f"[ok] recorded {'ALL options' if all_options else 'picks'}: "
          f"{n_opts} option(s) across {len(picks) - n_out} slide(s)"
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
    print(f"  {step + 1}. py -3 scripts/build_review.py --out \"{out}\" --final")
    print("     Show the user FINAL-CHECK.html and wait for its Build command.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
