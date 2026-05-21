# Security and Privacy

Slide Lab produces presentation decks from narrative briefs you write. Briefs
can contain sensitive content — internal strategy, client names, financials,
roadmap details. A few notes on keeping that out of public hands.

## Things this repo intentionally does NOT collect

- No telemetry. The skills run locally; nothing phones home.
- No analytics scripts in the rendered review HTML.
- No credentials or auth flow — slide-builder runs as your user.

## Things you should NOT commit

The `.gitignore` already filters most of these, but worth knowing:

- `_session/` folders — your working briefs and intermediate artifacts.
  These can contain governing thoughts, client names, financial figures.
- Anything under `slide-builder/clients/<client>/` — per-client template
  configurations live here. If you push them, you push the client's brand
  + any embedded copy.
- Output `.pptx`, `.docx`, `.xlsx`, `.pdf`, `.png` files — produced decks
  often contain audience-confidential material. The repo-wide `*.pptx`
  rule covers this; the curated `_renders/twins/*.pptx` allow-list is
  the only exception (those are generic pattern exemplars).

If you fork or contribute, double-check `git status` shows nothing under
`_session/` or `slide-builder/clients/` before pushing.

## Reporting a security issue

If you find a vulnerability (path traversal in a script, dependency CVE,
credential leak in shipped content, etc.), please **do not** file a public
GitHub issue. Instead email the maintainer or open a private security
advisory at https://github.com/mperaltajr/skills/security/advisories.

## Third-party dependencies

The Python deps listed in `requirements.txt` are pulled from PyPI. Pin
versions in your own deployment and run `pip list --outdated` periodically.
The repo currently uses unpinned minimum versions for portability; a
production deployment may want stricter pins.

## LibreOffice + PowerPoint

Two render paths exist:

- **LibreOffice headless** (default) — spawns a subprocess; does NOT touch
  any PowerPoint instance you have open. Safe to run during a working
  session.
- **PowerPoint COM** (opt-in via `--engine ppt`) — refuses to launch if
  `POWERPNT.EXE` is already running, to avoid interfering with open decks.

Neither path uploads files. Both produce only local `.pptx` / `.png` output.
