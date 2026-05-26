# Slide Lab

A skill that builds PowerPoint decks from a narrative brief using parallel agent fanout. Owns the build layer of Slide Lab.

## What you can do

- **Build a deck from a brief.** Hand it a markdown narrative brief (governing thought + per-slide structure) and a client PPTX template; it produces a full PPTX, a PNG-thumbnailed REVIEW.html for slide-by-slide picking, and the option scripts that built each slide.
- **Rebuild a single slide.** Re-dispatch one slide against the same brief without touching the rest of the deck.
- **Register a new client template.** A chat-driven flow (`register_template.py propose` → user picks → `commit`) extracts brand colors and fonts from any client PPTX and writes a `brand.yml` + `theme.json` sidecar pair.

## Where to start

1. **Install** — see [INSTALL.md](INSTALL.md). Pinned versions matter: `mmdc 11.4.0`, LibreOffice headless, Python 3.10+, plus the deps in `requirements.txt`.
2. **Quick run** — see [QUICKSTART.md](QUICKSTART.md). An example brief lives at `examples/quickstart-brief.md`. **You provide the template** — point the quickstart at any client PPTX you have already registered (with `<stem>.brand.yml` + `<stem>.theme.json` sidecars next to it). If you don't have one registered, the README walkthrough at SKILL.md § "Register a new client template" takes ~5 minutes via the chat-driven flow.
3. **First-time orientation** — open [SKILL.md](SKILL.md). The "first time?" block at the top tells you which sections to read in which order before building anything real.

The architecture in one sentence: 9 geometric splits + 3 diagram primitives + 2 special objects + 1 Mermaid fallback = 14 patterns governed by 5 hardline rules and a self-improving anti-pattern library. The pattern is the spec — read `reference/layouts.md` for the catalog.
