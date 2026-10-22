#!/usr/bin/env python3
"""icon_names.py: the one lookup for the icons designers may use.

`icons/checked-icons.json` lists the allowed icons (238, each checked by eye
at 24 px, owner's decisions 2026-10-21). Each has a plain name that says what
the picture shows (`gavel`, `server-rack`), the library file it draws from
(`icons/<file>.xml`, preview `icons/svg/<file>.svg`), a topic, and the old
names that still work.

Every place that turns an icon name into a picture asks this module:
  icon_helper.py     direct path: inserts the vector icon on a slide
  icon_svg.py        draws icons into sketches; the review card's notes
  translate_html.py  sketch path: the icon steps of the finished slide
  build_deck.py      the icon topics each design prompt offers

The lookup:
  - a plain name opens its file;
  - an old name (the icon's file name, or a name from the 10/08 list that
    moved to a new picture) still works and prints the plain name, so old
    scripts rebuild;
  - any other name is refused: the direct path stops the build, the sketch
    path blocks the review card. About half the library's own file names do
    not match their pictures, which is why they are not accepted.

Default color: TEXT_DARK, the palette's dark text color (#000000), which the
theme step turns into the template's dark text color. The accent color only
when the user asks for it.

Run:
  py -3 scripts/icon_names.py NAME [NAME ...]   what each name opens
  py -3 scripts/icon_names.py --topics          the topics and their icons
  py -3 scripts/icon_names.py --offer "slide words"   the prompt's icon block
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ICONS = HERE.parent / "icons"
LIST_JSON = ICONS / "checked-icons.json"

# The palette's dark text color (twins/helpers.TEXT_DARK). The theme step
# changes it to the template's own dark text color, so an icon drawn in it is
# the template's text color on the finished slide.
DEFAULT_COLOR = "#000000"
MAX_PER_PAGE = 6
MIN_TOPICS, MAX_TOPICS = 2, 4
# Topics offered when a page's words match fewer than two.
FALLBACK_TOPICS = ("strategy", "data")


class UnknownIcon(ValueError):
    """An icon name that is not on the allowed list (and not an old name of
    an allowed icon)."""


_DATA: dict | None = None
_INDEX: dict[str, dict] | None = None


def data() -> dict:
    global _DATA
    if _DATA is None:
        _DATA = json.loads(LIST_JSON.read_text(encoding="utf-8"))
    return _DATA


def icons() -> list[dict]:
    return list(data().get("icons") or [])


def _index() -> dict[str, dict]:
    """{name or old name: icon}. Plain names win over old names."""
    global _INDEX
    if _INDEX is None:
        idx: dict[str, dict] = {}
        for ic in icons():
            for old in [ic["file"]] + list(ic.get("old_names") or []):
                idx.setdefault(old, ic)
        for ic in icons():
            idx[ic["name"]] = ic
        _INDEX = idx
    return _INDEX


def _clean(name) -> str:
    return str(name or "").strip()


def lookup(name) -> dict | None:
    """The allowed icon a name opens (plain name or old name), or None."""
    return _index().get(_clean(name))


def is_old_name(name) -> bool:
    ic = lookup(name)
    return bool(ic) and ic["name"] != _clean(name)


def old_name_note(name) -> str:
    ic = lookup(name)
    return (f'icon "{_clean(name)}" is an old name; it works, and its plain name is '
            f'"{ic["name"]}" ({ic["shows"]}). Use "{ic["name"]}" next time.') if ic else ""


def refusal(name) -> str:
    return (f'icon "{_clean(name)}" is not on the allowed icon list. Use a plain name from '
            f'slide-builder/icons/checked-icons.json (the topics your _prompt.md offers), or a '
            f'plain circle or square instead. To see a list: py -3 slide-builder/scripts/'
            f'icon_names.py --topics')


def resolve(name, *, quiet: bool = False) -> dict:
    """The allowed icon for `name`. An old name prints its plain name (unless
    quiet); an unknown name raises UnknownIcon with the next step."""
    ic = lookup(name)
    if ic is None:
        raise UnknownIcon(refusal(name))
    if not quiet and ic["name"] != _clean(name):
        print(f"  [icon] {old_name_note(name)}")
    return ic


def file_for(name) -> str | None:
    """The library file (stem) an allowed name or old name opens, or None."""
    ic = lookup(name)
    return ic["file"] if ic else None


def names() -> list[str]:
    return sorted(ic["name"] for ic in icons())


# ---------------------------------------------------------------------------
# Topics offered to a design prompt
# ---------------------------------------------------------------------------

def topics() -> dict[str, dict]:
    return dict(data().get("topics") or {})


def status_topic() -> str:
    return data().get("status_topic") or "status"


def by_topic(topic: str) -> list[dict]:
    return sorted((ic for ic in icons() if ic["topic"] == topic), key=lambda ic: ic["name"])


def _hits(text: str, words) -> int:
    n = 0
    for w in words:
        w = w.lower()
        if not w.strip():
            continue
        if re.match(r"^[\w\- ]+$", w):
            n += len(re.findall(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", text))
        else:
            n += text.count(w)
    return n


def pick_topics(text: str) -> list[str]:
    """2 to 4 topics for a page, ranked by how often the page's words name
    them (ties: the list's own order). The status group is added on top."""
    low = " " + (text or "").lower() + " "
    st = status_topic()
    order = [k for k in topics() if k != st]
    scored = [(_hits(low, topics()[k].get("keywords") or []), -i, k) for i, k in enumerate(order)]
    picked = [k for s, _i, k in sorted(scored, reverse=True) if s > 0][:MAX_TOPICS]
    for k in FALLBACK_TOPICS:
        if len(picked) >= MIN_TOPICS:
            break
        if k not in picked:
            picked.append(k)
    return picked


def _entry(ic: dict) -> str:
    marks = []
    if (ic.get("min_px") or 0) > 24:
        marks.append(f"{ic['min_px']} px+")
    if ic.get("note"):
        marks.append("sparingly")
    return f"`{ic['name']}`" + (f" ({', '.join(marks)})" if marks else "")


def topic_block(text: str) -> str:
    """The `{{ICON_TOPICS}}` block of a design prompt: the offered topics,
    each with its icon names, then the status group."""
    st = status_topic()
    lines = []
    for k in pick_topics(text) + [st]:
        t = topics().get(k) or {}
        label = t.get("label") or k
        if k == st:
            label += " (always offered)"
        lines.append(f"  - {label}: " + ", ".join(_entry(ic) for ic in by_topic(k)))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 0
    if argv[0] == "--topics":
        for k, t in topics().items():
            print(f"{t.get('label') or k} [{k}]: " + ", ".join(_entry(ic) for ic in by_topic(k)))
        print(f"\n{len(icons())} icons. Plain names only; '32 px+' blurs smaller than 32 px.")
        return 0
    if argv[0] == "--offer":
        print(topic_block(" ".join(argv[1:])))
        return 0
    bad = 0
    for n in argv:
        ic = lookup(n)
        if ic is None:
            print(f"REFUSED: {refusal(n)}")
            bad += 1
        elif ic["name"] != n:
            print(f"OLD NAME: {old_name_note(n)} File: icons/{ic['file']}.xml")
        else:
            print(f"ok: {n} = {ic['shows']} [{ic['topic']}], file icons/{ic['file']}.xml")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
