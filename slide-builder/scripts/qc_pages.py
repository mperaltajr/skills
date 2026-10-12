#!/usr/bin/env python3
"""qc_pages.py — which pages the quality check must read, and proof it read them.

The owner's definition of done (approved 2026-10-09, Kinfield v3.1 session
report, item 8): a deck is done when EVERY page's reviewed image is the image
of that page in the current render of this exact deck, a deck-wide look was
recorded for this exact deck, and no Critical or Major finding is open.

Before this, the vision record was one whole-deck digest plus a typed count
of pages. Any recompile broke the digest, so every fix meant re-reading all
71 pages; and the count was whatever the session typed. One session recorded
71 pages reviewed after opening about 9 page images.

So the script, not the agent, decides what to read and checks it was read:

  plan    compares each page's image (render_manifest.json, written by the
          render compile or render_slides.py made of THIS deck) with the image
          that page had when it was last reviewed. Pages whose image changed are
          the ones to read; the rest carry their review (and their open
          findings) forward. Every page is read when there is no earlier
          page-by-page review, the page count changed, the renderer or dpi
          changed, or the template (slide master or theme) changed.
          It writes, into <build>/_qc/to_read/:
            page_NN.png   each page to read, with a band under it holding a
                          one-time check code for that page
            sheet_NN.png  thumbnail sheets of the whole deck (12 pages each),
                          for the cross-page checks, each with its own code
            pair_NN.png   each changed page beside an unchanged page of the
                          same layout (same-type comparison), with a code
          and <build>/_qc/page_notes.json, to fill in.

  record  (record_vision_qc.py) refuses unless every page in the round has a
          note with its page code AND a short quote of that page's own visible
          text that the script finds in the slide's text (pages with no text
          get a short description instead), the claimed pages cover every
          page that changed, every sheet and pair code is given, and any
          --slides-reviewed count is no larger than the pages the notes prove.
          It also runs the whole-file hygiene and type-scale check itself.
          Each Critical or Major from that check BLOCKS done (owner's decision
          2026-10-09) until it is gone on a later round or, for a Major, the
          user keeps it: record_vision_qc.py --keep-file-check KEY
          --user-words "<the user's exact words>". A Critical cannot be kept.
          Advisory never blocks.

WHAT THE PROOF CAN AND CANNOT SHOW (honestly):
  - A page code exists only in the pixels of that page's to_read image; it is
    in no text file (the build record keeps only a slow salted hash of it).
    So a correct code shows that image was opened (or decoded by a program).
    Codes are new every round, so a code from an earlier round does not work.
  - The quote shows the note was written about that page, not another one.
  - Neither shows the page was inspected zone by zone, or carefully. A
    session that opens each image and copies the code without looking at the
    slide passes. A session that deliberately writes a program to read the
    codes out of the images, or calls this module's internals to get them,
    defeats it; the transcript would show that, and it is deliberate cheating,
    not a corner cut by accident.
  - Quotes can be copied from the deck's text without looking at the image;
    the code is what ties the note to the image.
  - Pages whose text is all in pictures cannot be quote-checked; their
    description is not verified (only the code is), and the record says how
    many such pages there were.

Run:
  py -3 scripts/qc_pages.py plan --out <build dir> [--deck <deck>] [--also 5,7]
  py -3 scripts/qc_pages.py status --out <build dir> [--deck <deck>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "slide-qc" / "scripts"))
import _state  # noqa: E402
import render_manifest as RM  # noqa: E402

READ_DIR = "to_read"
NOTES = "page_notes.json"
PLAN = "qc_plan.json"
ALPHABET = "ACDEFHJKLMNPQRTUVWXY3479"     # no 0/O, 1/I, 2/Z, 5/S, 6/G, 8/B
CODE_LEN = 6
KDF_ROUNDS = 20000
SHEET_COLS, SHEET_ROWS, THUMB_W = 4, 3, 480
SEVERITIES = ("Critical", "Major", "Advisory")
MIN_QUOTE_CHARS = 12
MIN_QUOTE_WORDS = 3
MIN_SEEN_WORDS = 4


class PlanError(RuntimeError):
    pass


def qc_dir(out) -> Path:
    """The build's one QC folder (compile renders into it; slide-qc reuses it)."""
    return Path(out) / "_qc"


# ---------------------------------------------------------------- codes
def _new_code() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LEN))


def _norm_code(code) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(code or "").upper())


def _code_hash(code: str, label: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", f"{label}:{_norm_code(code)}".encode(),
                               bytes.fromhex(salt), KDF_ROUNDS).hex()


# ---------------------------------------------------------------- text
_QUOTE_MAP = {"‘": "'", "’": "'", "“": '"', "”": '"',
              "–": "-", "—": "-", "−": "-", " ": " ",
              "…": "...", "­": "", "​": ""}


def norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s or ""))
    for k, v in _QUOTE_MAP.items():
        s = s.replace(k, v)
    return re.sub(r"\s+", " ", s).strip().casefold()


def _shape_texts(shapes, out: list) -> None:
    for sh in shapes:
        try:
            if sh.shape_type == 6 or hasattr(sh, "shapes") and sh.__class__.__name__ == "GroupShape":
                _shape_texts(sh.shapes, out)
                continue
        except Exception:
            pass
        try:
            if getattr(sh, "has_text_frame", False) and sh.has_text_frame:
                out.append(sh.text_frame.text)
        except Exception:
            pass
        try:
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    for cell in row.cells:
                        out.append(cell.text)
        except Exception:
            pass
        try:
            if getattr(sh, "has_chart", False) and sh.has_chart:
                ch = sh.chart
                if ch.has_title and ch.chart_title.has_text_frame:
                    out.append(ch.chart_title.text_frame.text)
                for plot in ch.plots:
                    out.extend(str(c) for c in plot.categories)
                    out.extend(str(s.name) for s in plot.series)
        except Exception:
            pass


def page_texts(deck) -> list[str]:
    """Each page's own text (shapes, tables, chart titles and labels), joined."""
    from pptx import Presentation
    texts = []
    for slide in Presentation(str(deck)).slides:
        parts: list[str] = []
        _shape_texts(slide.shapes, parts)
        texts.append("\n".join(p for p in parts if p))
    return texts


def quote_on_page(quote: str, page_text: str) -> bool:
    q, t = norm_text(quote), norm_text(page_text)
    if not q:
        return False
    if q in t:
        return True
    # Lines wrap and shapes join differently from the picture: compare with
    # every space removed too.
    return q.replace(" ", "") in t.replace(" ", "")


def _words(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9%$]+", s or ""))


# ---------------------------------------------------------------- what changed
def assess(state: dict, man: dict) -> dict:
    """{"full": bool, "reasons": [...], "changed": [pages], "carried": [pages]}."""
    pages = [int(p["page"]) for p in man.get("pages") or []]
    prior = state.get("vision_pages") or {}
    reasons = []
    if not prior.get("pages"):
        reasons.append("no earlier page-by-page review of this build")
    else:
        if int(prior.get("slides") or 0) != int(man.get("slides") or 0):
            reasons.append(f"the page count changed ({prior.get('slides')} -> "
                           f"{man.get('slides')})")
        if prior.get("renderer") != man.get("renderer"):
            reasons.append(f"the renderer changed ({prior.get('renderer')} -> "
                           f"{man.get('renderer')})")
        if int(prior.get("dpi") or 0) != int(man.get("dpi") or 0):
            reasons.append(f"the dpi changed ({prior.get('dpi')} -> {man.get('dpi')})")
        if prior.get("template_fp") != man.get("template_fp"):
            reasons.append("the template (slide master or theme) changed")
    if reasons:
        return {"full": True, "reasons": reasons, "changed": pages, "carried": []}
    by = prior.get("pages") or {}
    changed = [int(p["page"]) for p in man["pages"]
               if (by.get(str(p["page"])) or {}).get("hash") != p["hash"]]
    return {"full": False, "reasons": [], "changed": changed,
            "carried": [p for p in pages if p not in changed]}


def _deck_and_manifest(out, deck=None) -> tuple[Path, dict]:
    out = Path(out)
    deck = Path(deck) if deck else _state.compiled_deck(out)
    if not deck.exists():
        raise PlanError(f"no deck at {deck}")
    man = RM.read(qc_dir(out))
    if not man:
        raise PlanError(f"no render manifest in {qc_dir(out)}. Render the deck there "
                        f"first: render_slides.py \"{deck}\" \"{qc_dir(out)}\"")
    if man.get("deck_digest") != RM.file_md5(deck):
        raise PlanError(f"the images in {qc_dir(out)} are of different deck bytes than "
                        f"{deck.name}. Render it again: render_slides.py \"{deck}\" "
                        f"\"{qc_dir(out)}\"")
    missing = [p["image"] for p in man["pages"] if not (qc_dir(out) / p["image"]).exists()]
    bad = RM.verify_images(man, qc_dir(out))
    if missing or bad:
        raise PlanError(f"page images in {qc_dir(out)} are missing or were changed after "
                        f"the render ({', '.join((missing + bad)[:5])}). Render again: "
                        f"render_slides.py --fresh \"{deck}\" \"{qc_dir(out)}\"")
    return deck, man


# ---------------------------------------------------------------- pictures
def _font(size: int):
    from PIL import ImageFont
    for name in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def _with_band(img, text: str):
    """img with a band under it carrying text (the page itself is untouched)."""
    from PIL import Image, ImageDraw
    h = max(48, img.width // 32)
    out = Image.new("RGB", (img.width, img.height + h), (255, 244, 179))
    out.paste(img.convert("RGB"), (0, 0))
    d = ImageDraw.Draw(out)
    d.line([(0, img.height), (img.width, img.height)], fill=(120, 120, 120), width=2)
    d.text((16, img.height + h // 2), text, fill=(20, 20, 20), font=_font(int(h * 0.55)),
           anchor="lm")
    return out


def _thumb(img, w: int):
    from PIL import Image
    r = w / img.width
    return img.convert("RGB").resize((w, max(1, int(img.height * r))), Image.LANCZOS)


def _sheet(pngs: list[tuple[int, Path]], changed: set, label_font) -> "object":
    from PIL import Image, ImageDraw
    thumbs = []
    for n, p in pngs:
        with Image.open(p) as im:
            thumbs.append((n, _thumb(im, THUMB_W)))
    th = max(t.height for _, t in thumbs)
    lab = 34
    W = SHEET_COLS * (THUMB_W + 16) + 16
    rows = (len(thumbs) + SHEET_COLS - 1) // SHEET_COLS
    H = rows * (th + lab + 16) + 16
    sheet = Image.new("RGB", (W, H), (235, 235, 235))
    d = ImageDraw.Draw(sheet)
    for i, (n, t) in enumerate(thumbs):
        x = 16 + (i % SHEET_COLS) * (THUMB_W + 16)
        y = 16 + (i // SHEET_COLS) * (th + lab + 16)
        d.text((x, y + 2), f"page {n}" + ("  (changed)" if n in changed else ""),
               fill=(160, 0, 0) if n in changed else (30, 30, 30), font=label_font)
        sheet.paste(t, (x, y + lab))
        d.rectangle([x - 1, y + lab - 1, x + t.width, y + lab + t.height],
                    outline=(120, 120, 120))
    return sheet


def _pair(a: Path, na: int, b: Path, nb: int, note: str, label_font):
    from PIL import Image, ImageDraw
    with Image.open(a) as ia, Image.open(b) as ib:
        ta, tb = _thumb(ia, 960), _thumb(ib, 960)
    lab = 40
    W = ta.width + tb.width + 48
    H = max(ta.height, tb.height) + lab + 32
    im = Image.new("RGB", (W, H), (235, 235, 235))
    d = ImageDraw.Draw(im)
    d.text((16, 8), f"page {na} (changed)", fill=(160, 0, 0), font=label_font)
    d.text((32 + ta.width, 8), f"page {nb} ({note})", fill=(30, 30, 30), font=label_font)
    im.paste(ta, (16, lab))
    im.paste(tb, (32 + ta.width, lab))
    return im


def _partner(n: int, carried: list[int], layouts: dict) -> tuple[int | None, bool]:
    """The nearest unchanged page with the same layout (else the nearest one)."""
    if not carried:
        return None, False
    same = [p for p in carried if layouts.get(p) and layouts.get(p) == layouts.get(n)]
    pool = same or carried
    return min(pool, key=lambda p: (abs(p - n), p)), bool(same)


# ---------------------------------------------------------------- plan
def make_plan(out, deck=None, also=None, _return_codes: bool = False) -> dict:
    """Work out this round's pages, write the pictures with their codes and
    the notes file, and record the codes' hashes. See the module docstring."""
    from PIL import Image
    out = Path(out)
    deck, man = _deck_and_manifest(out, deck)
    state = _state.read_state(out)
    a = assess(state, man)
    n_pages = int(man["slides"])
    extra = sorted({int(x) for x in (also or []) if 1 <= int(x) <= n_pages} - set(a["changed"]))
    read_pages = sorted(set(a["changed"]) | set(extra))
    carried = [p for p in a["carried"] if p not in read_pages]
    qc = qc_dir(out)
    rd = qc / READ_DIR
    shutil.rmtree(rd, ignore_errors=True)
    rd.mkdir(parents=True, exist_ok=True)
    salt = secrets.token_hex(16)
    codes: dict[str, str] = {}
    img = {int(p["page"]): qc / p["image"] for p in man["pages"]}
    layouts = {int(p["page"]): p.get("layout", "") for p in man["pages"]}

    for n in read_pages:
        code = codes[f"page:{n}"] = _new_code()
        with Image.open(img[n]) as im:
            _with_band(im, f"Check code for page {n}: {code}   (write it in "
                           f"page_notes.json)").save(rd / f"page_{n:02d}.png")
    lf = _font(24)
    per = SHEET_COLS * SHEET_ROWS
    sheets = []
    order = sorted(img)
    for i in range(0, len(order), per):
        name = f"sheet_{i // per + 1:02d}.png"
        code = codes[f"look:{name}"] = _new_code()
        chunk = [(n, img[n]) for n in order[i:i + per]]
        sh = _sheet(chunk, set(read_pages), lf)
        _with_band(sh, f"Check code for {name}: {code}   (pages {chunk[0][0]}-"
                       f"{chunk[-1][0]})").save(rd / name)
        sheets.append({"file": name, "pages": [c[0] for c in chunk]})
    pairs = []
    for n in read_pages:
        q, same = _partner(n, carried, layouts)
        if q is None:
            continue
        name = f"pair_{n:02d}.png"
        code = codes[f"look:{name}"] = _new_code()
        note = (f"unchanged, same layout '{layouts.get(n)}'" if same
                else "unchanged; no unchanged page has the same layout")
        _with_band(_pair(img[n], n, img[q], q, note, lf),
                   f"Check code for {name}: {code}").save(rd / name)
        pairs.append({"file": name, "changed": n, "partner": q, "same_layout": same})

    plan = {"deck": str(deck.resolve()), "deck_digest": man["deck_digest"],
            "manifest_at": man.get("at"), "renderer": man.get("renderer"),
            "dpi": man.get("dpi"), "full": a["full"], "reasons": a["reasons"],
            "changed": a["changed"], "also": extra, "read_pages": read_pages,
            "carried": carried, "slides": n_pages,
            "sheets": sheets, "pairs": pairs, "at": datetime.now().isoformat(timespec="seconds")}
    (qc / PLAN).write_text(json.dumps(plan, indent=2), encoding="utf-8")
    notes = {"deck": plan["deck"], "deck_digest": plan["deck_digest"],
             "how": ("For each page: open _qc/to_read/page_NN.png, read every zone, "
                     "write the check code under the page, a short quote (3+ words) "
                     "of that page's own text as it appears, and every finding still "
                     "open: {severity: Critical|Major|Advisory, category, issue}; a "
                     "Major the user chose to keep also gets user_reason (their words). "
                     "A page whose text is "
                     "all in pictures: describe what you see in 'seen' instead of a "
                     "quote. Then open every sheet and pair under deck_look, write "
                     "their codes, and the cross-page findings with their pages."),
             "pages": [{"page": n, "code": "", "quote": "", "seen": "", "findings": []}
                       for n in read_pages],
             "deck_look": {"codes": {**{s["file"]: "" for s in sheets},
                                     **{p["file"]: "" for p in pairs}},
                           "findings": []}}
    (qc / NOTES).write_text(json.dumps(notes, indent=2), encoding="utf-8")
    st = _state.read_state(out)
    st["vision_plan"] = {k: plan[k] for k in ("deck_digest", "manifest_at", "full",
                                              "reasons", "read_pages", "carried",
                                              "slides", "at")}
    st["vision_plan"].update({"salt": salt, "kdf_rounds": KDF_ROUNDS,
                              "codes": {k: _code_hash(v, k, salt) for k, v in codes.items()},
                              "sheets": [s["file"] for s in sheets],
                              "pairs": [p["file"] for p in pairs]})
    _state._write(out, st)
    if _return_codes:
        return {**plan, "_codes": codes}
    return plan


# ---------------------------------------------------------------- verify + record
def _check_findings(items, where: str, n_pages: int, need_pages: bool, problems: list) -> list:
    good = []
    if not isinstance(items, list):
        problems.append(f"{where}: findings must be a list")
        return good
    for f in items:
        if not isinstance(f, dict):
            problems.append(f"{where}: a finding is not an object")
            continue
        sev = str(f.get("severity", "")).strip().capitalize()
        if sev not in SEVERITIES:
            problems.append(f"{where}: severity must be Critical, Major or Advisory, "
                            f"not {f.get('severity')!r}")
            continue
        issue = str(f.get("issue", "")).strip()
        if not issue:
            problems.append(f"{where}: a {sev} finding has no issue text")
            continue
        rec = {"severity": sev, "category": str(f.get("category", "")).strip(),
               "issue": issue}
        kept = str(f.get("user_reason", "") or "").strip()
        if kept:
            if sev == "Critical":
                problems.append(f"{where}: a Critical cannot be kept with a reason; it "
                                f"must be fixed (\"{issue[:40]}\")")
                continue
            rec["user_reason"] = kept[:300]      # a Major the user chose to keep
        if need_pages:
            pages = f.get("pages") or ([f["page"]] if f.get("page") else [])
            try:
                pages = sorted({int(p) for p in pages})
            except Exception:
                pages = []
            if not pages or any(p < 1 or p > n_pages for p in pages):
                problems.append(f"{where}: the {sev} finding \"{issue[:40]}\" needs the "
                                f"page(s) it is on (1-{n_pages})")
                continue
            rec["pages"] = pages
        good.append(rec)
    return good


def verify_notes(out, deck, notes: dict, slides_reviewed: int | None = None) -> tuple[list, dict]:
    """(problems, result). result holds the verified pages and findings."""
    out = Path(out)
    problems: list[str] = []
    deck, man = _deck_and_manifest(out, deck)
    state = _state.read_state(out)
    plan = state.get("vision_plan") or {}
    if not plan:
        return ([f"no plan for this round. Run qc_pages.py plan --out \"{out}\" first; "
                 "it says which pages to read and makes their pictures."], {})
    if plan.get("deck_digest") != man["deck_digest"] or plan.get("manifest_at") != man.get("at"):
        return (["the plan was made for a different render or deck (it was recompiled "
                 "or rendered again since). Run qc_pages.py plan again and read the new "
                 "pictures."], {})
    salt = plan["salt"]
    hashes = plan.get("codes") or {}
    n_pages = int(man["slides"])
    texts = page_texts(deck)
    verified: dict[int, dict] = {}
    no_text = []
    for e in notes.get("pages") or []:
        try:
            n = int(e.get("page"))
        except Exception:
            problems.append(f"a page note has no page number: {str(e)[:60]}")
            continue
        label = f"page:{n}"
        code = str(e.get("code") or "").strip()
        if label not in hashes:
            problems.append(f"page {n} was not in this round's pages to read (no picture "
                            f"was made for it). To re-read an unchanged page, run plan "
                            f"with --also {n}.")
            continue
        if not code:
            continue        # left blank: not read (coverage below says so)
        if _code_hash(code, label, salt) != hashes[label]:
            problems.append(f"page {n}: the check code is wrong. Open "
                            f"_qc/{READ_DIR}/page_{n:02d}.png and copy the code under the page.")
            continue
        text = texts[n - 1] if n - 1 < len(texts) else ""
        quote = str(e.get("quote") or "").strip()
        seen = str(e.get("seen") or "").strip()
        if _words(text) >= MIN_QUOTE_WORDS:
            if (len(norm_text(quote).replace(" ", "")) < MIN_QUOTE_CHARS
                    or _words(quote) < MIN_QUOTE_WORDS):
                problems.append(f"page {n}: give a quote of at least {MIN_QUOTE_WORDS} words "
                                f"of this page's own text (title or body), as you read it.")
                continue
            if not quote_on_page(quote, text):
                problems.append(f"page {n}: the quote \"{quote[:60]}\" is not text on page "
                                f"{n}. Quote the page you opened (its own title or body, not "
                                "the footer).")
                continue
        else:
            if _words(seen) < MIN_SEEN_WORDS and not quote:
                problems.append(f"page {n} has no text the script can read (pictures): "
                                f"describe what you see in 'seen' ({MIN_SEEN_WORDS}+ words).")
                continue
            no_text.append(n)
        found = _check_findings(e.get("findings") or [], f"page {n}", n_pages, False, problems)
        verified[n] = {"quote": quote[:200], "seen": seen[:300], "findings": found}

    need = set(plan.get("read_pages") or [])
    missing = sorted(need - set(verified))
    if missing:
        problems.append(
            f"{len(missing)} page(s) of this round have no verified note: "
            f"{', '.join(map(str, missing[:20]))}{' ...' if len(missing) > 20 else ''}. "
            + ("Every page must be read this round ("
               + "; ".join(plan.get("reasons") or []) + ")."
               if plan.get("full") else
               "Their images changed since they were last reviewed, so they must be "
               "read again."))
    if slides_reviewed is not None and int(slides_reviewed) > len(verified):
        problems.append(f"--slides-reviewed {slides_reviewed} claims more pages than the "
                        f"notes prove ({len(verified)}). Record only the pages you opened.")
    look = notes.get("deck_look") or {}
    lcodes = look.get("codes") or {}
    for f in list(plan.get("sheets") or []) + list(plan.get("pairs") or []):
        c = str(lcodes.get(f) or "").strip()
        if not c or _code_hash(c, f"look:{f}", salt) != hashes.get(f"look:{f}"):
            problems.append(f"deck-wide look: the check code for {f} is "
                            f"{'missing' if not c else 'wrong'}. Open _qc/{READ_DIR}/{f}.")
    look_findings = _check_findings(look.get("findings") or [], "deck-wide look",
                                    n_pages, True, problems)
    return problems, {"deck": deck, "man": man, "plan": plan, "verified": verified,
                      "look_findings": look_findings, "no_text": no_text}


def file_check_key(v: dict) -> str:
    """A short name for one whole-file finding that stays the same from round
    to round while the finding does: category, slide (or 'deck') and a hash
    of the issue text. A changed issue is a new finding."""
    slide = v.get("slide")
    where = f"s{int(slide)}" if isinstance(slide, int) or str(slide or "").isdigit() else "deck"
    h = hashlib.sha1(str(v.get("issue", "")).encode("utf-8")).hexdigest()[:6]
    cat = re.sub(r"[^a-z0-9-]+", "-", str(v.get("category") or "check").lower()).strip("-")
    return f"{cat or 'check'}:{where}:{h}"


def run_hygiene(deck) -> dict:
    """The whole-file hygiene and type-scale pass (slide-qc's
    check_pptx_hygiene.py, which runs type_scale.py), run by the script.
    Every Critical and Major is kept in the record (they block done); the
    Advisory list is cut at 60."""
    try:
        import check_pptx_hygiene as H
        res = H.run_all_checks(Path(deck))
        v = [{**x, "key": file_check_key(x)} for x in (res.get("violations") or [])]
        cnt = {s: sum(1 for x in v if x.get("severity") == s) for s in SEVERITIES}
        blocking = [x for x in v if x.get("severity") in ("Critical", "Major")]
        advisory = [x for x in v if x.get("severity") not in ("Critical", "Major")]
        return {"ran": True, "criticals": cnt["Critical"], "majors": cnt["Major"],
                "advisories": cnt["Advisory"],
                "violations": blocking + advisory[:max(0, 60 - len(blocking))]}
    except Exception as exc:
        return {"ran": False, "error": f"{type(exc).__name__}: {exc}"}


def file_check_findings(state: dict) -> list[dict]:
    """The Critical and Major findings of the whole-file checks of the last
    recorded round, each with its key and, when the user kept it, their
    words ("kept_words"). A finding gone from the last round is fixed."""
    hyg = (state.get("vision_deck_look") or {}).get("hygiene") or {}
    kept = state.get("file_checks_kept") or {}
    out = []
    for v in hyg.get("violations") or []:
        if v.get("severity") not in ("Critical", "Major"):
            continue
        key = v.get("key") or file_check_key(v)
        rec = {**v, "key": key}
        k = kept.get(key)
        if k and v.get("severity") == "Major":
            rec["kept_words"] = k.get("words", "")
            rec["kept_at"] = k.get("at", "")
        out.append(rec)
    return out


def open_file_checks(state: dict) -> list[dict]:
    """The whole-file Critical and Major findings still blocking done."""
    return [f for f in file_check_findings(state) if not f.get("kept_words")]


def keep_file_check(out, key: str, words: str) -> dict:
    """Record that the user keeps one whole-file Major, with their exact
    words. Refuses a Critical, an unknown key and empty words."""
    out = Path(out)
    st = _state.read_state(out)
    words = str(words or "").strip()
    if not words:
        raise PlanError("give the user's exact words with --user-words (why they keep it)")
    match = [f for f in file_check_findings(st) if f["key"] == key]
    if not match:
        keys = [f["key"] for f in file_check_findings(st)]
        raise PlanError(f"no Critical or Major from the last round's whole-file checks has "
                        f"the key {key!r}. Open ones: {', '.join(keys) or 'none'}")
    f = match[0]
    if f.get("severity") == "Critical":
        raise PlanError(f"{key} is a Critical; a Critical cannot be kept, it must be fixed "
                        f"(\"{str(f.get('issue', ''))[:80]}\")")
    rec = {"words": words[:500], "at": datetime.now().isoformat(timespec="seconds"),
           "severity": f.get("severity"), "category": f.get("category", ""),
           "slide": f.get("slide"), "issue": str(f.get("issue", ""))[:300]}
    st.setdefault("file_checks_kept", {})[key] = rec
    _state._write(out, st)
    return rec


def open_counts(state: dict) -> dict:
    """Open findings over every page's record plus the deck-wide look."""
    cnt = {s: 0 for s in SEVERITIES}
    for f in all_findings(state):
        if f.get("user_reason"):
            continue                  # a Major the user kept, with their reason
        cnt[f.get("severity", "Advisory")] = cnt.get(f.get("severity", "Advisory"), 0) + 1
    return cnt


def all_findings(state: dict) -> list[dict]:
    """Every recorded finding, each with its page(s)."""
    out = []
    for k, rec in ((state.get("vision_pages") or {}).get("pages") or {}).items():
        out += [{**f, "pages": [int(k)]} for f in rec.get("findings") or []]
    out += list((state.get("vision_deck_look") or {}).get("findings") or [])
    return out


def record(out, deck, result: dict, hygiene: dict) -> dict:
    """Write the round: per-page records (re-read pages replaced, the rest
    carried with their open findings), the deck-wide look, and the summary."""
    out = Path(out)
    man, plan, verified = result["man"], result["plan"], result["verified"]
    st = _state.read_state(out)
    now = datetime.now().isoformat(timespec="seconds")
    prior = {} if plan.get("full") else dict((st.get("vision_pages") or {}).get("pages") or {})
    hashes = {int(p["page"]): p["hash"] for p in man["pages"]}
    rnd = int((st.get("vision_pages") or {}).get("round") or 0) + 1 if not plan.get("full") else 1
    pages = {}
    for n in range(1, int(man["slides"]) + 1):
        if n in verified:
            v = verified[n]
            pages[str(n)] = {"page": n, "hash": hashes[n], "renderer": man["renderer"],
                             "dpi": man["dpi"], "reviewed_at": now, "round": rnd,
                             "quote": v["quote"], "seen": v["seen"],
                             "findings": v["findings"]}
        elif str(n) in prior:
            pages[str(n)] = prior[str(n)]
    st["vision_pages"] = {"slides": int(man["slides"]), "renderer": man["renderer"],
                          "dpi": man["dpi"], "template_fp": man.get("template_fp"),
                          "deck_digest": man["deck_digest"], "round": rnd, "at": now,
                          "pages": pages}
    st["vision_deck_look"] = {"deck_digest": man["deck_digest"], "at": now,
                              "sheets": plan.get("sheets") or [],
                              "pairs": plan.get("pairs") or [],
                              "findings": result["look_findings"], "hygiene": hygiene}
    cnt = open_counts(st)
    st["vision_qc"] = {"deck": str(Path(deck).resolve()), "digest": man["deck_digest"],
                       "slides_reviewed": len(verified), "pages_total": int(man["slides"]),
                       "carried": len([p for p in pages if int(p) not in verified]),
                       "full_read": bool(plan.get("full")),
                       "no_text_pages": result.get("no_text") or [],
                       "criticals": cnt["Critical"], "majors": cnt["Major"],
                       "advisories": cnt["Advisory"],
                       "findings": sum(cnt.values()), "at": now}
    st.pop("vision_plan", None)          # codes are one-time
    _state._write(out, st)
    return st["vision_qc"]


def unreviewed_pages(state: dict, man: dict) -> list[int]:
    """Pages whose reviewed image is not the current render's image."""
    vp = state.get("vision_pages") or {}
    if (vp.get("renderer") != man.get("renderer")
            or int(vp.get("dpi") or 0) != int(man.get("dpi") or 0)
            or int(vp.get("slides") or 0) != int(man.get("slides") or 0)
            or vp.get("template_fp") != man.get("template_fp")):
        # The same cases in which plan makes every page be read again.
        return [int(p["page"]) for p in man.get("pages") or []]
    by = vp.get("pages") or {}
    return [int(p["page"]) for p in man.get("pages") or []
            if (by.get(str(p["page"])) or {}).get("hash") != p["hash"]]


# ---------------------------------------------------------------- CLI
def _parse_pages(s: str | None) -> list[int]:
    out = []
    for part in (s or "").replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Plan a quality-check round.")
    ap.add_argument("cmd", choices=("plan", "status"))
    ap.add_argument("--out", required=True, type=Path, help="Build folder (_state.json).")
    ap.add_argument("--deck", default=None, help="Default: the deck the last compile wrote.")
    ap.add_argument("--also", default="", help="Unchanged pages to read again too, e.g. 5,7 "
                                               "(to correct a finding carried on them).")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "status":
            deck, man = _deck_and_manifest(args.out, args.deck)
            a = assess(_state.read_state(args.out), man)
            print(json.dumps({k: a[k] for k in ("full", "reasons", "changed")}, indent=2))
            return 0
        plan = make_plan(args.out, args.deck, _parse_pages(args.also))
    except PlanError as exc:
        print(f"ERROR: {exc}")
        return 2
    qc = qc_dir(args.out)
    n = len(plan["read_pages"])
    if plan["full"]:
        print(f"Read EVERY page this round ({n}): " + "; ".join(plan["reasons"]) + ".")
    else:
        print(f"Read {n} page(s) this round: {', '.join(map(str, plan['read_pages'])) or 'none'}"
              f" (their images changed since they were reviewed"
              f"{'; plus the ones asked for with --also' if plan['also'] else ''}). "
              f"{len(plan['carried'])} unchanged page(s) keep their review and their "
              "open findings.")
    print(f"  pages to read : {qc / READ_DIR}\\page_NN.png (one per page above)")
    print(f"  deck-wide look: {len(plan['sheets'])} thumbnail sheet(s) and "
          f"{len(plan['pairs'])} changed-beside-unchanged pair(s) in {qc / READ_DIR}")
    print(f"  fill in       : {qc / NOTES}")
    print("Each picture carries a check code in the band under it; the record needs "
          "every code, plus a short quote of each page's own text.")
    print(f"Then: record_vision_qc.py --out \"{args.out}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
