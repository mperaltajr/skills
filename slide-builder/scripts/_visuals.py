"""_visuals.py: the plain visual names the user picks from, and their rules.

Owner's decisions (2026-10-14 to 2026-10-16, visual verdict + scenario
verdict): each slide's visual is chosen on the Storyline tab of the one Slide
Lab page, from these plain names with a small sketch each (never "cards" or
"text only"). A slide is open by default ("Suggestion"); "Must use" makes it
firm. One copy of the names, the sketches and the checks, shared by the page
(slidelab_page.py), the record step (record_storyline.py), prep
(build_deck.py) and the check after design (check_visual_type.py).

Brief lines (written by record_storyline.py; the seal does not count them):
  **Visual:** <name> | suggestion        (or | must use)
  **Visual note:** <the user's note on the visual>
  **Visual shows:** <one line: what the visual shows> (proposed by the chat)
  **Reuse:** <file> page <N>, keep as is | clean it up   (or: new design)
"""
from __future__ import annotations

import re

# name -> (sketch svg inner markup, family, HTML signal it needs or None,
#          data-visual-form values that count as the same kind)
# The sketches are the approved example's, unchanged.
VISUALS: dict[str, tuple[str, str, str | None, tuple[str, ...]]] = {
    "Bar chart over time": (
        '<rect x="10" y="30" width="10" height="16"/><rect x="26" y="24" width="10" height="22"/><rect x="42" y="17" width="10" height="29"/><rect x="58" y="11" width="10" height="35"/><rect x="74" y="6" width="10" height="40"/>',
        "chart", "svg", ("chart",)),
    "Bar chart, each bar split into parts": (
        '<rect x="12" y="22" width="12" height="24"/><rect x="12" y="14" width="12" height="8" fill-opacity=".45"/><rect x="34" y="18" width="12" height="28"/><rect x="34" y="8" width="12" height="10" fill-opacity=".45"/><rect x="56" y="14" width="12" height="32"/><rect x="56" y="5" width="12" height="9" fill-opacity=".45"/>',
        "chart", "svg", ("chart",)),
    "Line chart": (
        '<polyline points="8,40 26,34 44,28 62,18 84,8" fill="none" stroke="#64748B" stroke-width="3"/>',
        "chart", "svg", ("chart",)),
    "Table": (
        '<rect x="8" y="6" width="76" height="8"/><rect x="8" y="18" width="76" height="5" fill-opacity=".35"/><rect x="8" y="27" width="76" height="5" fill-opacity=".35"/><rect x="8" y="36" width="76" height="5" fill-opacity=".35"/>',
        "table", "table", ("table",)),
    "Boxes side by side, one per point": (
        '<rect x="6" y="10" width="24" height="32" rx="2" fill-opacity=".35"/><rect x="34" y="10" width="24" height="32" rx="2" fill-opacity=".35"/><rect x="62" y="10" width="24" height="32" rx="2" fill-opacity=".35"/>',
        "boxes", None, ("cards", "comparison")),
    "Steps connected by arrows": (
        '<circle cx="14" cy="26" r="8"/><circle cx="46" cy="26" r="8"/><circle cx="78" cy="26" r="8"/><path d="M24 26h10M30 22l5 4-5 4M56 26h10M62 22l5 4-5 4" stroke="#64748B" stroke-width="2" fill="none"/>',
        "flow", None, ("flow", "timeline", "diagram")),
    "Grid comparing options against criteria": (
        '<rect x="8" y="6" width="18" height="40" fill-opacity=".35"/><circle cx="40" cy="14" r="4"/><circle cx="58" cy="14" r="4" fill-opacity=".35"/><circle cx="76" cy="14" r="4"/><circle cx="40" cy="26" r="4" fill-opacity=".35"/><circle cx="58" cy="26" r="4"/><circle cx="76" cy="26" r="4"/><circle cx="40" cy="38" r="4"/><circle cx="58" cy="38" r="4"/><circle cx="76" cy="38" r="4" fill-opacity=".35"/>',
        "matrix", None, ("matrix",)),
    "Two to four large figures": (
        '<text x="6" y="28" font-size="17" font-weight="700" fill="#64748B">$3.8B</text><text x="56" y="28" font-size="17" font-weight="700" fill="#64748B">80K</text><rect x="6" y="36" width="38" height="4" fill-opacity=".35"/><rect x="56" y="36" width="30" height="4" fill-opacity=".35"/>',
        "figures", None, ("hero-number",)),
    "Short points with icons or numbers": (
        '<circle cx="12" cy="12" r="5"/><rect x="22" y="9" width="60" height="5" fill-opacity=".35"/><circle cx="12" cy="26" r="5"/><rect x="22" y="23" width="52" height="5" fill-opacity=".35"/><circle cx="12" cy="40" r="5"/><rect x="22" y="37" width="56" height="5" fill-opacity=".35"/>',
        "points", None, ("text", "quote")),
    "Photo with text": (
        '<rect x="6" y="6" width="44" height="40" fill-opacity=".35"/><rect x="56" y="12" width="30" height="5"/><rect x="56" y="22" width="26" height="4" fill-opacity=".35"/><rect x="56" y="30" width="28" height="4" fill-opacity=".35"/>',
        "photo", "img", ("image",)),
    "Map by region": (
        '<path d="M8 20c8-10 20-10 26-4s14-6 22-2 12 10 26 6v18H8z" fill-opacity=".35"/><circle cx="24" cy="26" r="4"/><circle cx="58" cy="22" r="4"/>',
        "map", None, ("map",)),
    "Designer's choice": (
        '<text x="18" y="33" font-size="22" fill="#64748B">?</text><text x="46" y="33" font-size="22" fill="#64748B">?</text>',
        "any", None, ()),
}
NAMES = list(VISUALS)
ANY = "Designer's choice"
# Tables and side-by-side boxes: the two that made decks look alike.
HEAVY = ("Table", "Boxes side by side, one per point")
LOCKS = ("suggestion", "must use")
# The mix box shows from this many slides with a visual; below it one table
# already sets off the "more than a third" warning.
MIX_MIN_SLIDES = 6
# The Storyline tab is shown when this many slides need a visual choice;
# fewer get one chat question instead.
PAGE_MIN_SLIDES = 3

_ALIASES = {
    "bar chart": "Bar chart over time", "bar": "Bar chart over time",
    "column chart": "Bar chart over time", "stacked bar": "Bar chart, each bar split into parts",
    "stacked bar chart": "Bar chart, each bar split into parts", "stacked": "Bar chart, each bar split into parts",
    "line": "Line chart", "line chart": "Line chart", "table": "Table",
    "boxes": "Boxes side by side, one per point", "cards": "Boxes side by side, one per point",
    "flow": "Steps connected by arrows", "flow diagram": "Steps connected by arrows",
    "process": "Steps connected by arrows", "steps": "Steps connected by arrows",
    "matrix": "Grid comparing options against criteria", "harvey ball matrix": "Grid comparing options against criteria",
    "big numbers": "Two to four large figures", "hero-number": "Two to four large figures",
    "large figures": "Two to four large figures", "icons": "Short points with icons or numbers",
    "photo": "Photo with text", "bios": "Photo with text", "image": "Photo with text",
    "map": "Map by region", "designer's choice": ANY, "designers choice": ANY,
    "you pick": ANY, "any": ANY, "open": ANY,
}


def canonical(name: str) -> str | None:
    """The plain visual name for what was typed, or None when unknown."""
    t = " ".join((name or "").replace("’", "'").split()).strip().rstrip(".")
    if not t:
        return None
    for n in NAMES:
        if n.lower() == t.lower():
            return n
    return _ALIASES.get(t.lower())


def sketch_svg(name: str, cls: str = "sk") -> str:
    inner = VISUALS.get(name, VISUALS[ANY])[0]
    return f'<svg class="{cls}" viewBox="0 0 92 52" fill="#64748B">{inner}</svg>'


def family(name: str) -> str:
    return VISUALS.get(name, VISUALS[ANY])[1]


def needed_signal(name: str) -> str | None:
    return VISUALS.get(name, VISUALS[ANY])[2]


def forms_for(name: str) -> tuple[str, ...]:
    return VISUALS.get(name, VISUALS[ANY])[3]


# --------------------------------------------------------------- brief lines

VISUAL_LINE_RE = re.compile(r"^\*\*Visual:\*\*[ \t]*(.*)$", re.M | re.I)
NOTE_LINE_RE = re.compile(r"^\*\*Visual note:\*\*[ \t]*(.*)$", re.M | re.I)
SHOWS_LINE_RE = re.compile(r"^\*\*Visual shows:\*\*[ \t]*(.*)$", re.M | re.I)
REUSE_LINE_RE = re.compile(r"^\*\*Reuse:\*\*[ \t]*(.*)$", re.M | re.I)


def parse_visual(value: str) -> dict | None:
    """{"name", "lock"} from a `**Visual:**` value ("Table | must use"); None
    when empty. An unknown name is kept with "unknown": True."""
    v = (value or "").strip()
    if not v:
        return None
    name, _, lock = v.partition("|")
    lock = " ".join(lock.lower().split()) or "suggestion"
    if lock in ("firm", "must", "locked", "required"):
        lock = "must use"
    if lock in ("open", "proposed", "suggested"):
        lock = "suggestion"
    canon = canonical(name)
    out = {"name": canon or name.strip(), "lock": lock if lock in LOCKS else "suggestion"}
    if not canon or lock not in LOCKS:
        out["unknown"] = True
    return out


def format_visual(name: str, lock: str) -> str:
    return f"{name} | {lock}"


def problems(visual_value: str) -> list[str]:
    """What is wrong with a `**Visual:**` value (for brief_check)."""
    v = (visual_value or "").strip()
    if not v:
        return []
    name, _, lock = v.partition("|")
    out = []
    if not canonical(name):
        out.append(f'"{name.strip()}" is not one of the visual names ({", ".join(NAMES)})')
    lk = " ".join(lock.lower().split())
    if lk and lk not in LOCKS + ("firm", "open"):
        out.append(f'"{lock.strip()}" after the bar must be "suggestion" or "must use"')
    return out


# Chart type in the brief -> the visual proposed when the chat wrote none.
_CHART_TO_VISUAL = (
    (("stacked",), "Bar chart, each bar split into parts"),
    (("line", "area"), "Line chart"),
    (("bar", "column", "waterfall"), "Bar chart over time"),
    (("table",), "Table"),
    (("map",), "Map by region"),
)


def infer(chart_type: str, mandatory_shape: str = "") -> str:
    """A proposal from the brief when no `**Visual:**` line exists."""
    ct = (chart_type or "").lower().strip()
    if ct and ct not in ("none", "n/a"):
        for keys, name in _CHART_TO_VISUAL:
            if any(k in ct for k in keys):
                return name
    ms = canonical(mandatory_shape or "")
    return ms or ANY


def needs_choice(archetype: str, no_narrative: bool = False) -> bool:
    """A slide gets a visual box unless it is a cover, divider, contents page
    or closing card (those are designed once and filled by script)."""
    if no_narrative:
        return False
    a = (archetype or "").lower()
    return not any(k in a for k in ("cover", "title page", "divider", "transition",
                                    "agenda", "contents", "closing", "thank"))


def mix(choices: list[tuple[int, str, str]]) -> dict:
    """The deck-wide mix: choices are (slide n, name, lock) in order, for the
    slides that have a visual box. Returns counts, the heavy share, the
    neighbors that repeat, and whether the cap is passed by suggestions."""
    counts: dict[str, int] = {}
    heavy = heavy_open = 0
    repeats = []
    for i, (n, name, lock) in enumerate(choices):
        counts[name] = counts.get(name, 0) + 1
        if name in HEAVY:
            heavy += 1
            if lock != "must use":
                heavy_open += 1
        if i and name != ANY and choices[i - 1][1] == name:
            repeats.append(n)
    total = len(choices)
    over = total >= MIX_MIN_SLIDES and heavy * 3 > total
    # The cap refuses only while some of the heavy ones are suggestions: the
    # user marking them Must use is their call, and it stands.
    refuse = over and heavy_open > 0
    return {"counts": counts, "heavy": heavy, "heavy_open": heavy_open, "total": total,
            "over": over, "refuse": refuse, "repeats": repeats}


def cap_message(m: dict) -> str:
    return (f"Tables and side-by-side boxes are {m['heavy']} of {m['total']} slides, more than "
            "a third, so the deck will start to look the same.")
