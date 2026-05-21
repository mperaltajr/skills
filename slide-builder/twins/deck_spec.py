"""
Deck spec loader.

A deck is described by a small YAML file:

    output: decks/my-deck.pptx
    slides:
      - pattern: 19_cover-split-panel
        overrides:
          cover-deck-title: Pilot Recap
          cover-tagline: Four weeks, six metrics.
      - pattern: 38_statement-hero-text
        overrides:
          hero-statement: Four weeks in, every metric is moving the right way.
          hero-attribution: Mario Peralta · May 2026

`compose_from_spec()` reads the file and calls compose_deck().

Color overrides use the {"text": "...", "fill": "#RRGGBB"} dict form, which
also flows through unchanged:

      - pattern: 13_2x2-framework-quadrants
        overrides:
          quadrant-tl-name:
            text: Quick wins
            fill: "#16A34A"
"""
from pathlib import Path
from typing import Optional

import yaml

from twins.composer import compose_deck


def compose_from_spec(spec_path: str, *, output_override: Optional[str] = None,
                      twins_dir: Optional[Path] = None, verbose: bool = True) -> Path:
    """Load a deck-spec YAML and build the corresponding PPTX deck.

    `output_override` lets the caller route the output somewhere else (e.g. a
    timestamped run dir) without editing the spec.
    """
    spec_path = Path(spec_path)
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec not found: {spec_path}")

    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))

    if not isinstance(spec, dict):
        raise ValueError(f"Spec must be a YAML mapping, got {type(spec)}")
    if "slides" not in spec or not isinstance(spec["slides"], list):
        raise ValueError("Spec must include a 'slides' list")

    out_path = output_override or spec.get("output")
    if not out_path:
        raise ValueError("Spec must include 'output' (or caller must pass output_override)")
    out_path = Path(out_path)
    if not out_path.is_absolute():
        # Resolve relative to the spec file's directory
        out_path = (spec_path.parent / out_path).resolve()

    # Optional client template. Path is resolved relative to the YAML's dir.
    # If provided, MUST exist — fail fast with a clear error message rather than
    # silently falling back to the default theme (alpha contract).
    client_template = spec.get("client_template")
    if client_template:
        tpl = Path(client_template)
        if not tpl.is_absolute():
            tpl = (spec_path.parent / tpl).resolve()
        if not tpl.exists():
            raise FileNotFoundError(
                f"client_template specified in {spec_path.name} but file not found: {tpl}\n"
                f"Fix: ensure the path is correct relative to the brief, or use an absolute path."
            )
        if tpl.suffix.lower() not in {".pptx", ".potx"}:
            raise ValueError(
                f"client_template must be .pptx or .potx; got {tpl.suffix}: {tpl}"
            )
        client_template = str(tpl)

    slides = []
    for i, s in enumerate(spec["slides"]):
        if not isinstance(s, dict):
            raise ValueError(f"slides[{i}] must be a mapping")
        if "pattern" not in s:
            raise ValueError(f"slides[{i}] missing 'pattern'")
        slides.append({
            "pattern": s["pattern"],
            "overrides": s.get("overrides", {}) or {},
        })

    if verbose:
        tpl_note = f" on template {Path(client_template).name}" if client_template else ""
        print(f"Composing deck from {spec_path} ({len(slides)} slides){tpl_note} -> {out_path}")

    return compose_deck(
        str(out_path),
        slides,
        twins_dir=twins_dir,
        client_template=client_template,
        verbose=verbose,
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m twins.deck_spec <spec.yaml> [output_override]")
        sys.exit(1)
    override = sys.argv[2] if len(sys.argv) >= 3 else None
    compose_from_spec(sys.argv[1], output_override=override)
