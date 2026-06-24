"""build_gate_preview.py — Stage 3 visual preview generator.

Produces <out>/GATE3-PREVIEW.html: a light, picking-free, QC-free, visual
verification page so the operator can eyeball rendered PNGs against
brand/pattern expectations before approving Stage 4 (build_review.py).

Spec (from operator):
  - Vertical scroll, one section per slide (10 sections for a 10-slide deck)
  - Per slide: slide number + title + 3 option tiles side-by-side
  - Each tile shows the rendered PNG (option_X.png)
  - Under each tile: pattern + variant + directive verb + classification
  - Adjacency advisory at top if any pattern appears 3+ consecutive across option_A
  - NO picking interface, NO QC banner, NO override-with-reason flow
  - Reuses the gallery styling conventions

Sources of metadata:
  - Pattern, variant, classification: parsed from option_X.py header (lines 1-2):
      Line 1 (native):   "# Slide N option X — pattern: <name>"
      Line 1 (fallback): "# FALLBACK_MERMAID: <reason>"
      Line 1 (rejected): "# SKELETON_REJECTED: <reason>"
      Line 2 (variant):  "# Variant: <description>" (or "pattern attempted" for fallback/rejected)
  - Directive verb (slide-level): parsed from <slide_dir>/_pattern_pick.md if the
    parent session wrote one after Stage 2 dispatch. Absent → "(directive not captured)".

Usage:
    py -3 build_gate_preview.py --out <output_dir>

Exit codes:
    0  Success — GATE3-PREVIEW.html written.
    1  --out missing or not a directory.
    2  No slide_NN directories found.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Optional

import _paths as _p

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


OPTIONS = ("A", "B", "C")
FALLBACK_TOKEN = "# FALLBACK_MERMAID:"
REJECTED_TOKEN = "# SKELETON_REJECTED:"

# Header line 1 patterns
_PATTERN_LINE_RE = re.compile(
    r"^#\s*Slide\s+\d+\s+option\s+[A-Z]\s+[—\-]\s+pattern(?:\s+attempted)?:\s*(.+?)\s*$",
    re.IGNORECASE,
)
_VARIANT_LINE_RE = re.compile(r"^#\s*Variant:\s*(.+?)\s*$", re.IGNORECASE)

# _pattern_pick.md parsing
_PATTERN_PICK_FIELD_RE = re.compile(
    r"^\s*(Picked|Directive verb|Variant tilt|Top signals|Seed used\?|Adjacency|Fallback\?)\s*:\s*(.+?)\s*$",
    re.IGNORECASE,
)


def extract_option_metadata(option_py: Path) -> dict:
    """Read option_X.py header. Returns:
        {
          "pattern":        <pattern name or None>,
          "variant":        <variant description or "(no variant in header)">,
          "classification": "native" | "fallback_mermaid" | "skeleton_rejected" | "unknown",
          "reason":         <reason if fallback/rejected, else "">,
        }
    """
    out = {"pattern": None, "variant": "(no variant in header)", "classification": "unknown", "reason": ""}
    if not option_py.exists():
        out["classification"] = "missing"
        out["reason"] = f"file not found: {option_py.name}"
        return out
    try:
        text = option_py.read_text(encoding="utf-8")
    except Exception as exc:
        out["classification"] = "missing"
        out["reason"] = f"{type(exc).__name__}: {exc}"
        return out
    lines = text.splitlines()[:4]
    if not lines:
        out["classification"] = "unknown"
        out["reason"] = "empty file"
        return out

    line1 = lines[0].strip()
    line2 = lines[1].strip() if len(lines) > 1 else ""

    if line1.startswith(FALLBACK_TOKEN):
        out["classification"] = "fallback_mermaid"
        out["reason"] = line1[len(FALLBACK_TOKEN):].strip()
        pat_match = _PATTERN_LINE_RE.match(line2)
        if pat_match:
            out["pattern"] = pat_match.group(1).strip()
    elif line1.startswith(REJECTED_TOKEN):
        out["classification"] = "skeleton_rejected"
        out["reason"] = line1[len(REJECTED_TOKEN):].strip()
        pat_match = _PATTERN_LINE_RE.match(line2)
        if pat_match:
            out["pattern"] = pat_match.group(1).strip()
    else:
        # Native path — line 1 has pattern
        out["classification"] = "native"
        pat_match = _PATTERN_LINE_RE.match(line1)
        if pat_match:
            out["pattern"] = pat_match.group(1).strip()
        # Variant on line 2
        var_match = _VARIANT_LINE_RE.match(line2)
        if var_match:
            out["variant"] = var_match.group(1).strip()

    return out


def read_pattern_pick_md(slide_dir: Path) -> dict:
    """Read <slide_dir>/_pattern_pick.md (written by parent post-dispatch).
    Returns dict with available fields or empty dict if file missing.
    """
    pick_file = slide_dir / _p.PATTERN_PICK_MD
    if not pick_file.exists():
        return {}
    try:
        text = pick_file.read_text(encoding="utf-8")
    except Exception:
        return {}
    out: dict = {}
    for line in text.splitlines():
        m = _PATTERN_PICK_FIELD_RE.match(line)
        if m:
            key = m.group(1).lower().replace(" ", "_").rstrip("?")
            out[key] = m.group(2).strip()
    return out


def slide_title_from_prompt(slide_dir: Path) -> str:
    """Try to extract the title from the slide's _prompt.md. Falls back to '(no title)'."""
    prompt = slide_dir / _p.PROMPT_MD
    if not prompt.exists():
        return f"(no _prompt.md for {slide_dir.name})"
    try:
        text = prompt.read_text(encoding="utf-8")
    except Exception:
        return f"(unreadable _prompt.md)"
    # Line: `# Slide N build prompt — \`<title>\``
    m = re.search(r"^#\s+Slide\s+\d+\s+build prompt\s*[—\-]\s*`(.+?)`", text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Fallback: **Slide title:** <title>
    m = re.search(r"\*\*Slide title:\*\*\s*(.+?)\s*$", text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return "(title not extracted)"


def discover_slides(out_dir: Path) -> list[dict]:
    """Walk slide_NN/ directories in numeric order. Returns:
        [{slide_n, slide_dir, title, options: [{letter, png_path, png_exists, pattern, variant, classification, reason}]}, ...]
    """
    slides: list[dict] = []
    slide_dirs = sorted(
        (d for d in out_dir.iterdir() if d.is_dir() and re.fullmatch(r"slide_\d+", d.name)),
        key=lambda d: int(d.name.split("_")[1]),
    )
    for sd in slide_dirs:
        slide_n = int(sd.name.split("_")[1])
        title = slide_title_from_prompt(sd)
        pick_meta = read_pattern_pick_md(sd)
        # Slide-level pattern (from _pattern_pick.md if present, else from option_A header)
        slide_pattern = pick_meta.get("picked")
        directive = pick_meta.get("directive_verb") or "(directive not captured)"

        options = []
        for letter in OPTIONS:
            py_path = sd / _p.option_py_name(letter)
            png_path = sd / _p.option_png_name(letter)
            meta = extract_option_metadata(py_path)
            options.append({
                "letter": letter,
                "png_path": png_path,
                "png_exists": png_path.exists(),
                "pattern": meta["pattern"],
                "variant": meta["variant"],
                "classification": meta["classification"],
                "reason": meta["reason"],
            })

        # If no slide-level pattern from _pattern_pick.md, fall back to option_A's pattern
        if not slide_pattern and options[0]["pattern"]:
            slide_pattern = options[0]["pattern"]

        slides.append({
            "slide_n": slide_n,
            "slide_dir": sd,
            "title": title,
            "pattern": slide_pattern or "(pattern not captured)",
            "directive": directive,
            "options": options,
        })
    return slides


def compute_adjacency_warnings(slides: list[dict], option_letter: str = "A") -> list[str]:
    """Detect 3+ consecutive same-pattern runs on the given option letter.

    Returns advisory strings, one per detected run.
    """
    warnings: list[str] = []
    if not slides:
        return warnings
    sequence: list[tuple[int, Optional[str]]] = []
    for s in slides:
        pat = None
        for opt in s["options"]:
            if opt["letter"] == option_letter:
                pat = opt["pattern"]
                break
        sequence.append((s["slide_n"], pat))

    i = 0
    while i < len(sequence):
        n_i, pat_i = sequence[i]
        if pat_i is None:
            i += 1
            continue
        j = i + 1
        while j < len(sequence) and sequence[j][1] == pat_i:
            j += 1
        run_len = j - i
        if run_len >= 3:
            run_slides = [sequence[k][0] for k in range(i, j)]
            warnings.append(
                f"Option {option_letter} runs the same pattern ({pat_i!r}) "
                f"across slides {', '.join(str(s) for s in run_slides)}. "
                f"Hardline #3 forbids 3+ consecutive same-split slides."
            )
            i = j
        else:
            i += 1
    return warnings


# Neutral fallback colors — used when _meta.json predates schema_version 2 or
# is missing brand_primary/brand_accent. NEVER a hardcoded brand default: a
# silent brand-colored default would render the wrong client's theme into
# previews for other clients (the false-positive class flagged in
# finalize_deck.py::_resolve_mermaid_theme).
_FALLBACK_BRAND_PRIMARY = "#333333"
_FALLBACK_BRAND_ACCENT  = "#888888"


def read_brand_colors(out_dir: Path) -> tuple[str, str]:
    """Read brand_primary + brand_accent from <out>/_meta.json.

    Falls back to neutral grays if the file is missing, malformed, or
    predates META_SCHEMA_VERSION 2.
    """
    meta_path = _p.meta_json(out_dir)
    if not meta_path.exists():
        return _FALLBACK_BRAND_PRIMARY, _FALLBACK_BRAND_ACCENT
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        from _meta_schema import validate_warn
        validate_warn(meta, source="build_gate_preview")
    except Exception:
        return _FALLBACK_BRAND_PRIMARY, _FALLBACK_BRAND_ACCENT
    primary = (meta.get("brand_primary") or "").strip() or _FALLBACK_BRAND_PRIMARY
    accent  = (meta.get("brand_accent")  or "").strip() or _FALLBACK_BRAND_ACCENT
    return primary, accent


CSS_TEMPLATE = """
:root {
  --bg: #FAFAFA;
  --panel: #FFFFFF;
  --rule: #E1E1E6;
  --brand-primary: __BRAND_PRIMARY__;
  --brand-accent: __BRAND_ACCENT__;
  --text-dark: #1A1A1A;
  --text-mid: #555;
  --advisory-bg: #FEF3C7;
  --advisory-border: #F59E0B;
  --advisory-text: #78350F;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  background: var(--bg);
  color: var(--text-dark);
  padding: 32px 48px 64px;
  line-height: 1.5;
}
header {
  max-width: 1400px;
  margin: 0 auto 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--brand-primary);
}
h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--brand-primary);
  margin-bottom: 6px;
}
.subtitle {
  font-size: 14px;
  color: var(--text-mid);
  font-style: italic;
}
.meta-line {
  font-size: 12px;
  color: var(--text-mid);
  margin-top: 6px;
  font-family: Consolas, monospace;
}
.advisory {
  max-width: 1400px;
  margin: 0 auto 20px;
  padding: 14px 18px;
  background: var(--advisory-bg);
  border-left: 4px solid var(--advisory-border);
  border-radius: 4px;
  color: var(--advisory-text);
  font-size: 13px;
}
.advisory-title {
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
  font-size: 11px;
}
.advisory ul { margin: 4px 0 0 18px; }
.advisory li { padding: 2px 0; }
.slide-section {
  max-width: 1400px;
  margin: 0 auto 36px;
  padding: 20px 24px;
  background: var(--panel);
  border: 1px solid var(--rule);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.slide-header {
  margin-bottom: 16px;
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
}
.slide-num {
  font-size: 11px;
  font-weight: 800;
  color: var(--brand-primary);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.slide-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-dark);
  flex: 1;
  min-width: 0;
}
.slide-meta {
  font-size: 11px;
  color: var(--text-mid);
  display: flex;
  gap: 16px;
  margin-top: 4px;
  width: 100%;
}
.slide-meta .label {
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 700;
  margin-right: 4px;
  font-size: 10px;
}
.options-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.option-tile {
  border: 1px solid var(--rule);
  border-radius: 6px;
  overflow: hidden;
  background: #FFF;
}
.option-tile.fallback_mermaid { border-color: #2563EB; border-width: 2px; }
.option-tile.skeleton_rejected { border-color: #DC2626; border-width: 2px; background: rgba(220,38,38,0.04); }
.option-tile.missing { border-color: #888; background: rgba(0,0,0,0.04); }
.tile-frame {
  width: 100%;
  aspect-ratio: 16/9;
  background: #FFF;
  border-bottom: 1px solid var(--rule);
  overflow: hidden;
  position: relative;
}
.tile-frame img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}
.tile-frame .missing-png {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: rgba(220,38,38,0.08);
  color: #C62828;
  font-size: 12px;
  font-weight: 600;
}
.class-badge {
  position: absolute;
  bottom: 6px;
  right: 6px;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.6px;
  line-height: 1.1;
  z-index: 2;
  box-shadow: 0 2px 5px rgba(0,0,0,0.25);
  color: #FFF;
}
.class-badge.fallback_mermaid { background: #2563EB; }
.class-badge.skeleton_rejected { background: #DC2626; }
.class-badge.missing { background: #888; }
.tile-body {
  padding: 10px 12px 12px;
}
.tile-letter {
  font-size: 12px;
  font-weight: 800;
  color: var(--brand-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}
.tile-meta {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 2px 8px;
  font-size: 11px;
  color: var(--text-mid);
}
.tile-meta .k {
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 700;
  font-size: 9px;
  padding-top: 1px;
}
.tile-meta .v { color: var(--text-dark); word-break: break-word; }
.tile-meta .v.italic { font-style: italic; color: var(--text-mid); }
.reason-line {
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px dashed var(--rule);
  font-size: 11px;
  color: #C62828;
  font-style: italic;
}
footer.note {
  max-width: 1400px;
  margin: 32px auto 0;
  padding-top: 18px;
  border-top: 1px solid var(--rule);
  font-size: 12px;
  color: var(--text-mid);
  font-style: italic;
}
"""


def render_html(out_dir: Path, slides: list[dict], adjacency: list[str]) -> str:
    primary, accent = read_brand_colors(out_dir)
    css = (
        CSS_TEMPLATE
        .replace("__BRAND_PRIMARY__", primary)
        .replace("__BRAND_ACCENT__", accent)
    )
    advisory_html = ""
    if adjacency:
        items = "".join(f"<li>{html.escape(w)}</li>" for w in adjacency)
        advisory_html = (
            '<div class="advisory">'
            '<div class="advisory-title">Adjacency advisory (option_A)</div>'
            f'<ul>{items}</ul>'
            '</div>'
        )

    sections_html: list[str] = []
    for s in slides:
        tiles_html: list[str] = []
        for opt in s["options"]:
            cls = opt["classification"]
            tile_class = f"option-tile {cls}"
            if opt["png_exists"]:
                rel_png = opt["png_path"].relative_to(out_dir).as_posix() if opt["png_path"].is_relative_to(out_dir) else opt["png_path"].as_uri()
                frame_inner = f'<img src="{html.escape(rel_png)}" alt="slide {s["slide_n"]} option {opt["letter"]}" loading="lazy">'
            else:
                frame_inner = '<div class="missing-png">no PNG (option not rendered)</div>'

            class_badge_html = ""
            if cls in ("fallback_mermaid", "skeleton_rejected", "missing"):
                label = {"fallback_mermaid": "MERMAID", "skeleton_rejected": "REJECTED", "missing": "MISSING"}[cls]
                class_badge_html = f'<div class="class-badge {cls}">{label}</div>'

            reason_html = ""
            if opt["reason"]:
                reason_html = f'<div class="reason-line">{html.escape(opt["reason"])}</div>'

            variant_html = html.escape(opt["variant"] or "(no variant in header)")
            pattern_html = html.escape(opt["pattern"] or "(no pattern in header)")

            tiles_html.append(f"""
<div class="{tile_class}">
  <div class="tile-frame">{frame_inner}{class_badge_html}</div>
  <div class="tile-body">
    <div class="tile-letter">Option {opt["letter"]}</div>
    <div class="tile-meta">
      <div class="k">Pattern</div><div class="v">{pattern_html}</div>
      <div class="k">Variant</div><div class="v italic">{variant_html}</div>
      <div class="k">Class</div><div class="v">{html.escape(cls)}</div>
    </div>
    {reason_html}
  </div>
</div>
""")

        sections_html.append(f"""
<section class="slide-section">
  <div class="slide-header">
    <div>
      <div class="slide-num">SLIDE {s["slide_n"]}</div>
      <div class="slide-title">{html.escape(s["title"])}</div>
    </div>
    <div class="slide-meta">
      <span><span class="label">Pattern</span>{html.escape(s["pattern"])}</span>
      <span><span class="label">Directive verb</span>{html.escape(s["directive"])}</span>
    </div>
  </div>
  <div class="options-grid">
    {"".join(tiles_html)}
  </div>
</section>
""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Gate 3 Preview — visual verification</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{css}</style>
</head>
<body>

<header>
  <h1>Gate 3 Preview — visual verification</h1>
  <div class="subtitle">Light preview after Stage 3 (finalize). No picking, no QC banner — just visual sanity check before Stage 4 (REVIEW.html).</div>
  <div class="meta-line">Output dir: {html.escape(str(out_dir.resolve()))} &middot; {len(slides)} slides &middot; {sum(len(s["options"]) for s in slides)} option tiles</div>
</header>

{advisory_html}

{"".join(sections_html)}

<footer class="note">Generated by scripts/build_gate_preview.py at Stage 3 finalize. After visual approval, run build_review.py for the full Gate 4 REVIEW.html with picking machinery.</footer>

</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate GATE3-PREVIEW.html for visual verification after Stage 3.")
    ap.add_argument("--out", required=True, type=Path, help="Output dir from build_deck.py / finalize_deck.py")
    args = ap.parse_args()

    from _log import attach as _log_attach
    _log_attach(args.out, "build_gate_preview.py")

    if not args.out.exists() or not args.out.is_dir():
        sys.stderr.write(f"ERROR: --out is not a directory: {args.out}\n")
        return 1

    slides = discover_slides(args.out)
    if not slides:
        sys.stderr.write(f"ERROR: no slide_NN directories in {args.out}\n")
        return 2

    adjacency = compute_adjacency_warnings(slides, option_letter="A")
    html_text = render_html(args.out, slides, adjacency)
    target = _p.gate3_preview_html(args.out)
    target.write_text(html_text, encoding="utf-8")

    print(f"GATE3-PREVIEW.html written:")
    print(f"  {target.resolve()}")
    print(f"  {len(slides)} slides, {sum(len(s['options']) for s in slides)} option tiles")
    if adjacency:
        print(f"  Adjacency advisories surfaced: {len(adjacency)}")
    missing_png_count = sum(1 for s in slides for o in s["options"] if not o["png_exists"])
    if missing_png_count:
        print(f"  Missing PNGs: {missing_png_count} (preview will show placeholder boxes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
