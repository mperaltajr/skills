#!/usr/bin/env python3
"""check_done.py — is this deck actually deliverable?

"Done" was an orchestrator claim. It has been claimed over a deck with open
defects, over a file that would not open, over a deck that was edited after QC,
over a deck compiled from an older brief, and over a folder with no deck in it.
An audit on 2026-09-30 got DELIVERABLE out of this script for a text file
containing the words "not a pptx".

So this checks one unbroken chain of recorded facts, each tied to the last:

  1. a compile SUCCEEDED and recorded what it produced (path, bytes, the content
     it was built from, slide count)
  2. the deck being checked IS that file, byte for byte
  3. it was built from the CURRENT brief (nothing re-prepped since)
  4. it opens, and has no structure PowerPoint refuses
  5. every option in it was finalized with no blocking findings
  6. every page's REVIEWED image is that page's image in the current render
     of this exact deck (render_manifest.json in <out>/_qc, bound to the
     deck's bytes; reviews of unchanged pages carry forward), each review
     recorded with proof the page's picture was opened (qc_pages.py), and a
     deck-wide look was recorded for this exact deck (owner's definition of
     done, 2026-10-09)
  7. no Critical or Major finding is open on any page, including findings
     carried on unchanged pages (only Advisory may remain, or a Major the
     user kept with their reason)
  7a. no Critical or Major from the whole-file hygiene and type-scale checks
      of the last round is open (owner's decision 2026-10-09: they block, as
      page findings do); a Major the user kept, with their exact words
      recorded (record_vision_qc.py --keep-file-check), does not block and is
      listed at delivery. A Critical cannot be kept. Advisory never blocks.
  7b. the agent files the build's steps ran with are all one version, or
      all on main (a file installed after the last agent step only warns,
      2026-10-14)
  8. every figure on a replicated supplied page was reconciled
  9. every comment the user made on a pick was applied (none pending)

On delivery it also lists the user's comments with how each was applied, and
every QC finding fixed automatically (apply_qc_fix.py --auto), with any undo,
and every edit the main session made itself ("edited by parent").

It is deliberately dumb: it verifies recorded facts, it does not re-run QC.
On a deliverable deck it also lists every gate passed over (overrides) and,
separately, every step the user approved by typing in chat (picks, the final
check, a QC fix), with their words: those are approvals, not overrides.

Run:  py -3 scripts/check_done.py --out <out_dir> [--deck <path>]
Exit: 0 deliverable | 1 not deliverable | 2 bad usage
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "slide-qc" / "scripts"))
import _state  # noqa: E402
import _install  # noqa: E402
import qc_pages  # noqa: E402
import render_manifest as RM  # noqa: E402


def _same_file(a, b) -> bool:
    try:
        return Path(a).resolve() == Path(b).resolve()
    except Exception:
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Verify a deck is actually deliverable.")
    ap.add_argument("--out", required=True, type=Path, help="Build output dir.")
    ap.add_argument("--deck", default=None,
                    help="The file you intend to send. Default: the file the last "
                         "successful compile recorded. A different path is accepted "
                         "only if it is byte-identical to that file.")
    args = ap.parse_args(argv)

    if not args.out.exists():
        print(f"ERROR: out dir not found: {args.out}")
        return 2

    state = _state.read_state(args.out)
    problems: list[str] = []

    def _refuse() -> int:
        print("NOT DELIVERABLE:")
        for p in problems:
            print(f"  - {p}")
        print("\nDo not tell the user the deck is finished until this passes.")
        return 1

    # 1. A successful compile, with a record of what it produced.
    comp = (state.get("stages") or {}).get("compile") or {}
    if not state:
        problems.append("no _state.json — this build has no recorded history at all")
        return _refuse()
    if not comp:
        problems.append("no successful compile recorded — the deck was never built "
                        "through compile_picks.py, or every compile failed")
        return _refuse()
    if not comp.get("output") or not comp.get("digest"):
        problems.append("the compile record predates output tracking; re-run "
                        "compile_picks.py so there is a record of what it produced")
        return _refuse()

    # 2. The deck being checked is that file.
    recorded = Path(comp["output"])
    deck = Path(args.deck) if args.deck else recorded
    if not deck.exists():
        problems.append(f"no deck at {deck} — nothing to deliver")
        return _refuse()
    digest = _state.file_digest(deck)
    if digest != comp["digest"]:
        if _same_file(deck, recorded):
            problems.append(
                "the deck has changed since it was compiled. Edits made to a "
                "compiled deck are how defects shipped before; rebuild through "
                "the pipeline and recompile.")
        else:
            problems.append(
                f"{deck} is not the deck the last compile produced ({recorded}). "
                "Check the file you are actually sending.")

    # 3. Built from the current brief, and nothing rebuilt since.
    if comp.get("content_hash") != state.get("content_hash"):
        problems.append(
            "the brief or build inputs changed after this deck was compiled "
            "(prep ran again). This deck shows the old content; recompile.")
    # A single-slide rebuild keeps the same brief, so the content hash alone
    # missed it: the old deck stayed DELIVERABLE after slide 2 was redesigned.
    # The build's event counter says what happened after the compile.
    _crev = int(comp.get("rev") or 0)
    _prep_rev = int(((state.get("stages") or {}).get("prep") or {}).get("rev") or 0)
    _fin_rev = int((state.get("finalize") or {}).get("rev") or 0)
    if _crev and _prep_rev > _crev:
        problems.append(
            "a slide was rebuilt or inserted after this deck was compiled, so the "
            "deck does not contain it. Finish the review sequence and recompile.")
    elif _crev and _fin_rev > _crev:
        problems.append(
            "finalize ran again after this deck was compiled, so the deck may not "
            "match the current slides. Finish the review sequence and recompile.")

    # 4. Opens, and no structure PowerPoint refuses.
    n_deck = 0
    try:
        from pptx import Presentation
        prs = Presentation(str(deck))
        n_deck = len(prs.slides)
    except Exception as exc:
        problems.append(f"the deck does not open: {type(exc).__name__}: {exc}")
        prs = None
    if prs is not None:
        try:
            from pptx_openability import check_openability
            issues = check_openability(prs)
            if issues:
                problems.append(
                    f"{len(issues)} structure(s) PowerPoint would refuse, e.g. "
                    f"slide {issues[0]['slide']}: {issues[0]['issue'][:120]}")
        except Exception as exc:
            problems.append(f"could not check openability: {type(exc).__name__}: {exc}")
        if comp.get("slides") and n_deck != int(comp["slides"]):
            problems.append(f"the deck has {n_deck} slides; the compile produced "
                            f"{comp['slides']}")

    # 5. Every shipped option finalized clean (a re-finalize after compile can
    # record new blocks against options already in the deck).
    shipped = comp.get("options") or []
    if shipped:
        ok, why = _state.check_options_finalized(state, shipped)
        if not ok:
            problems.append(why)

    # 6 + 7. The owner's definition of done (2026-10-09): every page's reviewed
    # image is that page's image in the current render of THIS deck, a
    # deck-wide look was recorded for this deck, nothing open above Advisory.
    vq = state.get("vision_qc") or {}
    vp = state.get("vision_pages") or {}
    look = state.get("vision_deck_look") or {}
    qc = qc_pages.qc_dir(args.out)
    man = RM.read(qc)
    _qc_steps = (
        f" Invoke the slide-qc skill (again, if your copy of its steps is old). Its "
        f"steps: py -3 \"{HERE / 'qc_pages.py'}\" plan --out \"{Path(args.out).resolve()}\"; "
        f"open every picture in {qc / qc_pages.READ_DIR} and fill in "
        f"{qc / qc_pages.NOTES}; then py -3 \"{HERE / 'record_vision_qc.py'}\" --out "
        f"\"{Path(args.out).resolve()}\".")
    if not vq and not vp:
        problems.append(
            "no vision pass recorded: the deterministic self-check does NOT "
            "count, and neither does a look at pictures that was not recorded."
            + _qc_steps)
    elif not vp:
        problems.append(
            "the vision pass was recorded the old way (a typed page count, no proof "
            "the pages were opened)." + _qc_steps)
    elif not man or man.get("deck_digest") != digest:
        problems.append(
            f"there is no render of this exact deck in {qc} (it was edited, "
            "recompiled, or rendered elsewhere), so no page review can be matched "
            f"to it. Render it there (render_slides.py \"{deck}\" \"{qc}\") and run "
            "slide-qc on the pages that changed.")
    else:
        bad = RM.verify_images(man, qc)
        if bad:
            problems.append(
                f"{len(bad)} page image(s) in {qc} were changed after the render "
                f"({', '.join(bad[:4])}); render again with --fresh and re-run slide-qc.")
        if n_deck and int(man.get("slides") or 0) != n_deck:
            problems.append(f"the render has {man.get('slides')} page(s); the deck has "
                            f"{n_deck}. Render again and re-run slide-qc.")
        unrev = qc_pages.unreviewed_pages(state, man)
        if unrev:
            problems.append(
                f"{len(unrev)} page(s) were never reviewed as they look in this deck: "
                f"page {', '.join(map(str, unrev[:15]))}{' ...' if len(unrev) > 15 else ''}. "
                "A partial look is how defects shipped last time. Run slide-qc "
                "(qc_pages.py plan lists exactly these pages).")
        if look.get("deck_digest") != digest:
            problems.append(
                "no deck-wide look (thumbnail sheets, changed pages beside unchanged "
                "ones, whole-file hygiene and type-scale check) was recorded for this "
                "exact deck. Run slide-qc; every round records one.")
        cnt = qc_pages.open_counts(state)
        crit, maj = cnt["Critical"], cnt["Major"]
        if crit or maj:
            problems.append(
                f"the vision pass left {crit} Critical and {maj} Major finding(s) "
                "open (findings on unchanged pages carry forward and stay open). "
                "Everything above Advisory must be fixed (or corrected to 'not a "
                "defect' if the finding was wrong), then QC re-run.")
        if look.get("deck_digest") == digest:
            if not (look.get("hygiene") or {}).get("ran"):
                problems.append(
                    "the whole-file hygiene and type-scale check was not recorded for "
                    "this deck. Run slide-qc again; record_vision_qc.py runs it.")
            else:
                fopen = qc_pages.open_file_checks(state)
                if fopen:
                    crit_f = sum(1 for f in fopen if f.get("severity") == "Critical")
                    problems.append(
                        f"the whole-file checks (hygiene and type scale) of the last round "
                        f"found {crit_f} Critical and {len(fopen) - crit_f} Major still open: "
                        + "; ".join(
                            f"[{f['key']}] {'slide ' + str(f['slide']) if f.get('slide') else 'deck'}: "
                            f"{str(f.get('issue', ''))[:90]}" for f in fopen[:4])
                        + (" ..." if len(fopen) > 4 else "")
                        + ". Fix each and run the next QC round, or, for a Major the user "
                          "decides to keep, record their exact words: record_vision_qc.py "
                          "--out <build> --keep-file-check KEY --user-words \"...\" "
                          "(a Critical cannot be kept).")

    # 6b. The agent files the build's steps ran with: two versions that are both
    #     on main are accepted, with a line below. Since 2026-10-14 (owner's
    #     decision, speed verdict Q2 item 7) a file installed AFTER the last
    #     agent step is a warning, not a refusal: every agent of this build has
    #     finished, so no page was made with it.
    _agents_ok, _agents, _agents_note = _install.versions_compatible(state, include_now=False)
    if not _agents_ok:
        problems.append(_agents)
    _agents_later = _install.installed_changed_after_last_step(state)
    if _agents_later:
        print(f"WARNING: {_agents_later}.")

    # 8. Every slide that copies a supplied page is settled: its own check,
    #    made from the picked design, every figure answered (2026-10-13; this
    #    used to read one count from the last ledger run).
    sl = state.get("source_ledger") or {}
    ok_l, why_l = _state.check_ledger(state, args.out)
    if not ok_l:
        problems.append(why_l)

    # 9. Every comment the user made on a pick was applied (never dropped).
    pend = _state.pending_comments(state)
    if pend:
        problems.append(
            f"{len(pend)} comment(s) from the review page were never applied: "
            + "; ".join(f"{c['slide']} ({c['kind']}): {c['text'][:80]}" for c in pend[:4])
            + ". Edit or redesign those slides (record_picks.py --edits-done, "
              "redesign_round.py finish) and rebuild.")

    if problems:
        return _refuse()

    kind = comp.get("kind", "picks")
    label = {"picks": "final deck", "all_variations": "all-options comparison deck",
             "splice": "spliced deck"}.get(kind, kind)
    print(f"DELIVERABLE ({label}): {deck}")
    print(f"  compiled at   : {comp.get('at')}  ({n_deck} slides)")
    cnt = qc_pages.open_counts(state)
    print(f"  vision pass   : all {n_deck} page(s) reviewed as they look in this deck "
          f"({vq.get('slides_reviewed')} read in the last round, {vq.get('carried', 0)} "
          f"carried from earlier rounds); {cnt['Advisory']} Advisory open; deck-wide "
          f"look {look.get('at')}")
    if vq.get("no_text_pages"):
        print(f"                  {len(vq['no_text_pages'])} page(s) had no readable text "
              "(pictures): for those only the check code proved the page was opened.")
    kept = [f for f in qc_pages.all_findings(state) if f.get("user_reason")]
    if kept:
        print(f"  kept by user  : {len(kept)} Major finding(s) kept with the user's reason:")
        for f in kept:
            print(f"                  - page {','.join(map(str, f.get('pages') or []))}: "
                  f"{f.get('issue', '')[:90]} (\"{f['user_reason'][:90]}\")")
    for line in file_check_kept_lines(qc_pages.file_check_findings(state)):
        print(line)
    # Every gate that was deliberately passed over in this build. They were
    # recorded and then never shown to anyone; delivery is where the user sees
    # what the deck did NOT go through.
    # A QC fix approved in chat was once recorded as an override; it is an
    # approval, so it is listed with the chat approvals.
    all_ov = state.get("overrides") or []
    legacy_chat = [o for o in all_ov if o.get("override") == "qc_fix_approved_in_chat"]
    overrides = [o for o in all_ov if o not in legacy_chat]
    if overrides:
        print(f"  overrides     : {len(overrides)} gate(s) passed over in this build:")
        for o in overrides:
            times = f", {o['count']} times" if int(o.get("count") or 1) > 1 else ""
            print(f"                  - {o.get('override')}: {o.get('detail', '')} "
                  f"({o.get('at', '')}{times})")
        print("                  Tell the user about these when you deliver.")
    for line in chat_approval_lines(state.get("chat_approvals") or [], legacy_chat):
        print(line)
    for line in comment_lines(state.get("comments") or []):
        print(line)
    for line in auto_fix_lines(state.get("auto_fixes") or []):
        print(line)
    for line in parent_edit_lines(state.get("parent_edits") or []):
        print(line)
    line = supplied_page_line(sl)
    if line:
        print(line)
    if _agents_note:
        print(f"  agent files   : {_agents_note}. Mention it when you deliver.")
    if _agents_later:
        print(f"  agent files   : warning only: {_agents_later}.")
    return 0


def file_check_kept_lines(findings: list) -> list[str]:
    """Delivery lines for whole-file Majors the user kept, with their words."""
    kept = [f for f in findings if f.get("kept_words")]
    if not kept:
        return []
    out = [f"  kept file checks: {len(kept)} Major finding(s) from the whole-file checks "
           "kept with the user's words:"]
    for f in kept:
        where = f"slide {f['slide']}" if f.get("slide") else "whole deck"
        out.append(f"                  - [{f['key']}] {where}: {str(f.get('issue', ''))[:90]} "
                   f"(\"{f['kept_words'][:120]}\", {f.get('kept_at', '')})")
    out.append("                  Tell the user about these when you deliver.")
    return out


_CHAT_KIND = {"picks": "picks, with REVIEW.html open",
              "final_check": "final check, with FINAL-CHECK.html open",
              "qc_fix": "QC fix after the quality check",
              "qc_undo": "undo of an automatic QC fix"}


def chat_approval_lines(approvals: list, legacy: list | None = None) -> list[str]:
    """Delivery lines for approvals the user gave in chat instead of pasting a
    page's line. They are approvals, not gates passed over: each was accepted
    only with its page open for the current files (or, for a QC fix, after the
    first compile), and the user's own words are on record."""
    rows = [(_CHAT_KIND.get(a.get("kind"), a.get("kind", "")), a.get("words", ""),
             a.get("at", "")) for a in approvals]
    rows += [(_CHAT_KIND["qc_fix"], o.get("detail", ""), o.get("at", ""))
             for o in (legacy or [])]
    if not rows:
        return []
    out = [f"  chat approvals: {len(rows)} recorded (the user's own words in chat):"]
    out += [f"                  - {what}: \"{words}\" ({at})" for what, words, at in rows]
    out.append("                  Mention them when you deliver: these steps were "
               "approved in chat, not on the page.")
    return out


def comment_lines(comments: list) -> list[str]:
    """Delivery lines for the user's comments on their picks: each one and how
    it was applied (edited in place, redesigned, or not needed because the
    slide was left out). Comments used to be read by nobody."""
    if not comments:
        return []
    out = [f"  comments      : {len(comments)} from the review page, each applied:"]
    for c in comments:
        how = c.get("applied_how") or "NOT APPLIED"
        out.append(f"                  - {c.get('slide')}: \"{c.get('text', '')}\" -> {how}")
    out.append("                  Tell the user how their comments were applied.")
    return out


def parent_edit_lines(edits: list) -> list[str]:
    """Delivery lines for edits the main session made itself, no worker (a
    color, a font size or the user's exact words on a direct-path page;
    owner's decision 2026-10-09)."""
    if not edits:
        return []
    out = [f"  edited by parent: {len(edits)} edit(s) made by the main session, no worker:"]
    for e in edits:
        out.append(f"                  - {e.get('slides')}: {e.get('what', '')} "
                   f"({e.get('via', '')}, {e.get('at', '')})")
    out.append("                  List these when you deliver.")
    return out


def auto_fix_lines(fixes: list) -> list[str]:
    """Delivery lines for QC findings fixed automatically (no approval asked,
    owner's decision 2026-10-09), with the finding text and any undo."""
    if not fixes:
        return []
    out = [f"  fixed automatically: {len(fixes)} QC fix round(s) without asking:"]
    for f in fixes:
        undone = f.get("undone_slides") or []
        tail = (f"; undone by the user on {', '.join(undone)}" if undone else "")
        out.append(f"                  - round {f.get('round')}, slide(s) {f.get('slides')}: "
                   f"{f.get('findings', '')}{tail} ({f.get('at', '')})")
    out.append("                  List these when you deliver; \"undo slide N\" restores "
               "a slide's design from before its fix.")
    return out


def supplied_page_line(sl: dict) -> str:
    """The delivery line for a pinned supplied page: how much was taken on
    trust rather than verified. Empty when no page was pinned."""
    if not sl:
        return ""
    by = sl.get("by_slide")
    if by:
        out = [f"  copied pages  : {len(by)} slide(s) copy a supplied page:"]
        for sid, c in sorted(by.items()):
            n = int(sid.split("_")[-1])
            if c.get("visual_only"):
                out.append(f"                  - slide {n} ({c.get('source')}): a PDF page "
                           "or picture, CHECKED BY EYE ONLY (the vision pass); no figure on "
                           "it was machine-checked. Tell the user.")
            else:
                out.append(f"                  - slide {n} ({c.get('source')}): "
                           f"{c.get('kept', 0)} figure(s) from the copied page kept on the "
                           f"final check, {c.get('brief_matches', 0)} match the brief, "
                           f"{c.get('unreachable', 0)} surface(s) unreadable and covered "
                           "only by the vision pass")
        return "\n".join(out)
    if sl.get("visual_only"):
        return ("  supplied page : a PDF page or picture, CHECKED BY EYE ONLY (the "
                "vision pass); no figure on it was machine-checked against the brief. "
                "Tell the user.")
    return (f"  supplied page : {sl.get('keep_source', 0)} figure(s) kept "
            f"verbatim from the source, {sl.get('unreachable', 0)} surface(s) "
            f"unreadable and covered only by the vision pass")


if __name__ == "__main__":
    sys.exit(main())
