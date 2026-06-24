# Slide Lab

A skill that builds PowerPoint decks from a narrative brief using parallel agent fanout. Owns the build layer of Slide Lab.

## What you can do

- **Build a deck from a brief.** Hand it a markdown narrative brief (governing thought + per-slide structure) and a client PPTX template; it produces a full PPTX, a PNG-thumbnailed REVIEW.html for slide-by-slide picking, and the option scripts that built each slide.
- **Rebuild a single slide.** Re-dispatch one slide against the same brief without touching the rest of the deck.
- **Register a new client template.** A chat-driven flow (`register_template.py propose` → user picks → `commit`) extracts brand colors and fonts from any client PPTX and writes a `brand.yml` + `theme.json` sidecar pair.

## Where to start

1. **Install** — see [INSTALL.md](INSTALL.md). You need Python 3.10+, the deps in `requirements.txt`, a headless Chromium (`py -3 -m playwright install chromium`) for the HTML-first render path, and LibreOffice headless for the slide-qc review step.
2. **Quick run** — see [examples/RUN.md](examples/RUN.md). An example brief lives at `examples/quickstart-brief.md`. **You provide the template** — point the example at any client PPTX you have already registered (with a `<stem>/` sidecar subfolder next to it). If you don't have one registered, the SKILL.md § "Register a new client template" walkthrough takes ~5 minutes via the chat-driven flow.
3. **First-time orientation** — open [SKILL.md](SKILL.md). The "first time?" block at the top tells you which sections to read in which order before building anything real.

The architecture in one sentence: 9 geometric splits + 3 diagram primitives + 2 special objects + 1 HTML→image fallback = 14 patterns governed by 5 hardline rules and a self-improving anti-pattern library. The pattern is the spec — read `reference/layouts.md` for the catalog.
