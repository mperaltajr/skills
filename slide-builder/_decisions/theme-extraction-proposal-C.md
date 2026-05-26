# Theme extraction — Reviewer C proposal (workflow / hybrid)

**Position in one line:** The other two reviewers will spend the next quarter chasing an extraction algorithm that does not exist. Stop. Make the human confirm the theme once per template, save it as a flat file, and have every build read that file. The slot-mapping bug becomes irrelevant the moment a human has eyeballed the swatches.

---

## Why this is the right frame

Both XML-direct and image-analysis are *more* technology applied to a problem that is fundamentally ambiguous. Look at what the v1 loader and v2 `validate_theme()` are doing: heuristics on top of heuristics. `is_branded()` checks saturation. `_pick_brand_colors()` walks an ordered slot list. `validate_theme()` then re-checks the result and *halts the build* if a hue range does not match. That last check is the tell. The system already knows it cannot trust its own extraction — it built a guardrail that says "if FedEx primary is not purple, give up."

The honest read: there is no algorithm that reliably tells you "this hex is the brand primary" from a PPTX alone. A black square in `dk2` could be the brand. A vivid magenta in `accent3` could be the brand. The PowerPoint theme schema does not encode "which slot is the marketing hero color." That information lives in a brand guidelines PDF or in a human head. Trying to recover it from XML or pixels is reading tea leaves.

The right design treats theme determination as a **content authoring step**, not a runtime computation. The user (or a brand-savvy operator) confirms it once, in a 30-second prompt, and the system never guesses again.

Note: v1 `SKILL.md` already describes a `setup_template.py` that generates `template.json` once per template. That step exists today but it is silent auto-extraction — there is no human confirmation, no swatch preview, no smoke build. This proposal upgrades that existing step from "silent dump" to "ratified canonical file" and makes the build refuse to run without it for client-facing decks.

---

## Proposal — workflow-driven theme extraction

### Mechanism

A new explicit phase: **template registration**. Until a template is registered, *no client-facing build can run against it*. Registration is a one-time, one-template operation that produces a canonical theme file. Builds against a registered template are pure file reads.

The `register_template` command does this:

1. **Open the PPTX.** Pull what *can* be auto-extracted unambiguously: theme XML colors (all 10 slots), theme XML fonts (major/minor), layout names, slide master dimensions, logo image asset paths.
2. **Render a swatch sheet to PNG.** A single 1280x720 image showing every theme color slot labeled, both fonts in 24pt sample text, and any logo images found. Saved to `<template_dir>/_registration/preview.png` so it appears in the user preview panel.
3. **Show the user the candidate canonical theme** as YAML in chat, plus the preview PNG path on its own line for copy/click.
4. **Prompt for confirmation, slot by slot, in one structured block.** Not free-form. The user replies with edits inline.
5. **Write `<template_stem>.theme.yaml` next to the template** with the confirmed values, a SHA-256 of the source PPTX, and `registered_by` / `registered_at` stamps.
6. **Run a one-slide smoke build** using the registered theme and show the resulting PNG. If it looks wrong, the user re-runs registration and overrides. If it looks right, registration is complete.

After registration, every subsequent build for that template reads `*.theme.yaml` and that is it. No XML walk. No `is_branded()`. No `validate_theme()`. No `KNOWN_CLIENT_HUE_RANGES` table that has to be maintained per-client. The build `client_theme` loader becomes a 20-line YAML reader.

### Who decides

The **human** decides. The algorithm proposes; the human ratifies. The algorithm job is to make the human job 30 seconds instead of 30 minutes.

### When

At template registration — once. Re-confirmed only when the template file SHA changes (i.e., the client shipped a new version). Builds never re-derive.

### The exact UX

User invokes the skill with a template that has no `.theme.yaml`:

```
> /slide-builder-simple build --template ./FedEx/_templates/Template2.pptx ...
```

Skill detects unregistered template and refuses to build:

```
This template has not been registered.

  Template:   C:\...\FedEx\_templates\Template2.pptx
  Theme file: C:\...\FedEx\_templates\Template2.theme.yaml  (not found)

Run registration first:
  /slide-builder-simple register-template C:\...\FedEx\_templates\Template2.pptx

(or pass --skip-registration to use the unconfirmed auto-extracted theme,
 which is not recommended for client-facing decks.)
```

User runs registration. Skill auto-extracts, renders the swatch PNG, and prints:

```
Auto-extracted theme from Template2.pptx. Please confirm.

Preview rendered: C:\...\FedEx\_templates\_registration\Template2.preview.png

Candidate theme (edit any line, or reply "confirm" to accept all):

  brand_primary:        #4D148C    <- from dk2; my best guess at primary
  brand_accent:         #FF6600    <- from lt2; my best guess at accent
  text_dark:            #1A1A1A    <- from dk1
  text_light:           #FFFFFF    <- from lt1
  neutral_light:        #F2F2F2    <- from accent6
  neutral_border:       #E3E3E3    <- derived (mix of dk1 + lt1 at 88%)
  font_heading:         FedEx Sans Bold     <- from majorFont
  font_body:            FedEx Sans Regular  <- from minorFont
  cover_layout_index:   [master=6, layout=2]   <- best guess; layout name "Cover"
  default_layout_index: [master=0, layout=0]   <- blank white

Reply with edits (any subset), or "confirm" to accept all values as shown.
Example: "brand_primary: #5A0099; font_body: Helvetica Neue"
```

User responds:

```
confirm
```

Or:

```
brand_primary: #5A0099
font_body: Helvetica Neue Regular
```

Skill writes the YAML, runs a smoke build, shows the resulting PNG, and asks one final question:

```
Smoke build complete.

  Preview:  C:\...\FedEx\_templates\_registration\Template2.smoke.png

Does this look on-brand? (yes / no — if no, run register-template again)
```

On `yes`, registration is sealed. The skill prints the path to the saved theme file and the registration is durable across all future sessions and all future users of that template file.

---

## Canonical theme file schema

`<template_stem>.theme.yaml`, written next to the PPTX:

```yaml
# Slide Lab canonical brand theme for this template.
# Confirmed by a human at registration. Builds against this template MUST
# read this file rather than re-deriving from the PPTX XML.
#
# To re-register: run "register-template" against this PPTX.

schema_version: 1
template_path: "FedEx/_templates/Template2.pptx"   # relative to project root
template_sha256: "9f1b...c4a2"                     # SHA-256 of the PPTX bytes at registration time
registered_at: "2026-05-25T10:32:00-04:00"
registered_by: "m.a.peralta@accenture.com"

# Brand colors — what the build agents actually consume.
# These override anything that could be inferred from the PPTX theme XML.
colors:
  brand_primary:    "#4D148C"
  brand_accent:     "#FF6600"
  brand_primary_mid: "#7500C0"   # derived; user may override
  brand_accent_soft: "#FFD9B3"   # derived; user may override
  text_dark:        "#1A1A1A"
  text_mid:         "#595959"    # derived from text_dark + text_light
  text_faint:       "#888888"    # derived
  card_bg:          "#F8F4FC"    # derived neutral; NOT accent6
  card_border:      "#E3E3E3"    # derived neutral; NOT accent5
  neutral_light:    "#F2F2F2"
  neutral_border:   "#E3E3E3"

# Fonts — full family names, no weight/style suffix. The applier handles bold/italic.
fonts:
  heading: "FedEx Sans"
  body:    "FedEx Sans"
  # Optional fallback stacks used by Mermaid + HTML preview only.
  heading_fallback: "Helvetica, Arial, sans-serif"
  body_fallback:    "Helvetica, Arial, sans-serif"

# Layout indices the user wants the build agents to default to.
# This is information no extractor can produce — the user picks them at
# registration by looking at layout previews in PowerPoint.
layouts:
  default_content: { master: 0, layout: 0, name: "Blank White" }
  cover:           { master: 6, layout: 2, name: "Cover" }
  section_divider: { master: 6, layout: 5, name: "Section Divider" }

# Brand chrome assets the build agents may embed (logos, footer marks).
# Paths are relative to the template directory.
assets:
  logo_primary:   "_brand/fedex-logo-purple.png"
  logo_reversed:  "_brand/fedex-logo-white.png"
  cover_keyline:  null

# Off-palette aliases — agents observed using these colors should be remapped.
# Same idea as v1 OFF_PALETTE_* tuples but per-template-customizable.
off_palette_remap:
  "#333333": "text_dark"
  "#1E293B": "text_dark"
  "#475569": "text_mid"

# Free-form notes the human wanted to record for future operators.
notes: |
  FedEx brand center says NEVER use orange and purple adjacent without a
  white gap. The build agents should treat lt2 (orange) as accent ONLY,
  never as a primary fill. Confirmed with FedEx Brand 2026-05-12.
```

Everything an agent needs to render a branded slide lives here. Nothing about this file requires the PPTX to be re-opened at build time except for grafting onto the master layout.

### Where it lives

**Adjacent to the template.** `Template2.pptx` -> `Template2.theme.yaml` in the same directory. This makes registration travel with the template when it is copied, shared, or version-controlled. A global `~/.slide-lab/themes/` registry is the wrong location — themes are per-template, not per-user, and a fresh checkout of a project should already have its themes registered.

A `client_template:` field in the brief front-matter points at the PPTX; the loader derives the theme path by suffix swap. The brief itself does *not* duplicate the theme — that would let theme and template drift.

### Brief-level override

A brief can still override individual fields when the user wants a one-off:

```yaml
---
client_template: ./FedEx/_templates/Template2.pptx
theme_overrides:
  brand_accent: "#003366"   # this deck only — use navy for accent, not orange
---
```

Override fields shallow-merge onto the canonical theme at load time. Anything not overridden inherits from the registered theme. This is the escape hatch for "we are presenting to FedEx Logistics, who uses a navy variant" without re-registering the template.

---

## Implementation sketch

### Workflow diagram

```
NEW TEMPLATE                         REGISTERED TEMPLATE
-------------                        -------------------
build invoked                        build invoked
        |                                    |
        v                                    v
  .theme.yaml exists?  NO              .theme.yaml exists?  YES
        |                                    |
        v                                    v
  REFUSE to build.                     load_theme(yaml_path)
  Tell user to run                            |
  register-template.                          v
                                       SHA matches PPTX?  NO -> warn,
                                              |           |    prompt
                                       YES    |           v    re-register
                                              v         proceed with
                                       proceed to      stale theme
                                       prep + fanout   (user opted in)

  register-template workflow:
  auto-extract -> render swatch PNG -> user confirms / edits
  -> smoke build -> final yes/no -> write .theme.yaml
```

### Python pseudocode for the registration command

```python
# scripts/register_template.py
import hashlib
import sys
from pathlib import Path

import yaml
from pptx import Presentation

from twins.client_theme import load_client_theme  # reuse v1 extractor for the proposal step
from twins.swatch import render_swatch_png         # new — renders 1280x720 preview
from twins.smoke_build import build_smoke_slide    # new — one-slide proof build


def register_template(template_path: Path) -> int:
    if not template_path.exists():
        sys.stderr.write(f"Template not found: {template_path}\n")
        return 1

    theme_path = template_path.with_suffix(".theme.yaml")
    if theme_path.exists():
        sys.stderr.write(
            f"Theme file already exists: {theme_path}\n"
            f"Delete it first or use --force to re-register.\n"
        )
        return 2

    # 1. Auto-extract the proposal
    sha256 = hashlib.sha256(template_path.read_bytes()).hexdigest()
    auto = load_client_theme(str(template_path))
    proposal = build_proposal_dict(auto, template_path, sha256)

    # 2. Render swatch preview
    reg_dir = template_path.parent / "_registration"
    reg_dir.mkdir(exist_ok=True)
    preview_png = reg_dir / f"{template_path.stem}.preview.png"
    render_swatch_png(proposal, out_path=preview_png)

    # 3. Print proposal to chat (Claude sees this and relays to user)
    print(format_proposal_for_user(proposal, preview_png))

    # 4. Wait for user reply (handled by the calling agent, not this script).
    #    The script is invoked twice: once to propose, once with --confirm
    #    and an edits YAML to seal.
    return 0


def seal_registration(template_path: Path, edits_yaml: str) -> int:
    """Called after user confirms / edits. edits_yaml is the user response,
    parsed as YAML (may be the literal string 'confirm' or a partial dict).
    """
    theme_path = template_path.with_suffix(".theme.yaml")
    proposal = load_pending_proposal(template_path)   # from _registration/

    if edits_yaml.strip().lower() == "confirm":
        final = proposal
    else:
        edits = yaml.safe_load(edits_yaml)
        final = shallow_merge(proposal, edits)

    # Smoke build
    smoke_png = run_smoke_build(template_path, final)
    print(f"Smoke build preview:\n  {smoke_png}\nLook on-brand? (yes/no)")

    # On 'yes', write theme_path. On 'no', prompt re-registration.
    # ...
    return 0
```

The agent driving this owns the user interaction; the script is two pure functions (`propose` and `seal`) that talk to disk.

---

## Trade-offs vs alternatives

### vs XML-direct extraction (Reviewer A, presumably)

XML-direct will be precise about *what is in the file*. It cannot be precise about *what the user meant the brand to be*. Whoever proposes XML-direct is solving a different problem — they are solving "extract the theme1 element correctly" when the actual problem is "which slot is the marketing-approved primary." A perfect XML reader gives you the same `dk2: #4D148C` that v1 already gives you. If `dk2` is the wrong slot to read (as is true for any client whose brand color sits in `accent3`), better XML parsing changes nothing.

Workflow-driven catches this because the human looks at the swatch sheet and says "no, the primary is the magenta one labeled accent3, not the black one labeled dk2." No algorithm can make that call.

### vs image-analysis (Reviewer B, presumably)

Image analysis sounds smart and will work on the demo. It will fail on:
- Templates where the cover slide hero color is a gradient, not the brand primary.
- Templates whose first slide is intentionally muted (a quote, a divider) — pixel analysis finds gray.
- Templates whose brand primary appears in 0.5% of pixels (a thin keyline) but is load-bearing for the deck.
- Logos in placeholders with bg fills that overwhelm the actual brand hex.

You will then write heuristics on top of the pixel sampler to fix these cases. Those heuristics will themselves be wrong on the next template. This is where v1 lives today and why `validate_theme()` is checking hue ranges per-client.

Workflow-driven side-steps the whole loop. The human ratifies the answer; no heuristic is needed.

### What workflow-driven catches that pure-automatic misses

1. **Non-convention slot placement** (primary in accent3).
2. **Slot ambiguity** (template with dk2=black, lt2=white, brand in accent1 — the algorithm cannot know).
3. **Sub-brands** (FedEx vs FedEx Logistics vs FedEx Express — same template, different accents per deck).
4. **Layout intent** (which layout *is* the cover slide — no algorithm tells you which layout the user prefers as default content).
5. **Logo asset selection** (purple-on-white vs white-on-purple — depends on deck mood).
6. **Off-palette remap rules** (a brand-savvy operator knows "if anyone uses #1E293B, treat it as text_dark, not as a separate color").

Pure automatic catches none of these reliably.

---

## Failure modes

**1. User confirms the wrong thing without looking.** Real risk. Mitigations:
- The swatch PNG is mandatory — the proposal is not shown as a wall of YAML alone. The user *sees* the colors before confirming.
- The smoke build is the second checkpoint. If the user rubber-stamped the YAML but the smoke build looks wrong, they catch it there.
- Two confirmations is a feature, not friction. 30 seconds total.

**2. User skips registration via `--skip-registration`.** This is the documented escape hatch. The build proceeds with the auto-extracted theme and emits a banner in `REVIEW.html`: "UNREGISTERED TEMPLATE — theme not human-confirmed." The user sees the banner on every review and knows they are flying with what v1 has today. Acceptable for internal throwaway decks; not acceptable for client-facing work. This is a policy enforced by the user, not the system.

**3. Multiple users on the same template in different registration states.** This is what the SHA-256 stamp is for. If the `.theme.yaml` exists but its `template_sha256` does not match the current PPTX bytes, the loader emits:

```
WARNING: theme file is stale.
  Theme registered against SHA: 9f1b...c4a2
  Current template SHA:         a7d2...44e1
  The template has been updated since registration.

Options:
  1. Re-run register-template (recommended if template changed materially)
  2. Pass --accept-stale-theme to proceed (the theme may be wrong)
```

The theme file lives in the project git tree alongside the template. When the client ships a new template version, the SHA mismatch surfaces immediately and forces a re-registration. Two users editing the same project pull each other theme files via git like any other artifact.

**4. Template version changes that *do not* affect the theme.** A new master layout does not change brand_primary. The SHA still changes. The user re-registers, glances at the proposal, says "confirm" — 30 seconds. This is acceptable cost for the safety it buys.

**5. Theme file is hand-edited and corrupted.** YAML loader fails loudly with the line number. The build refuses to start. Better than today silent slot-mapping mistakes.

**6. The brief points at a template that has been moved.** Same problem v1 has today — orthogonal to this proposal. The path-resolution code is unchanged.

**7. Registration becomes the new ceremony users learn to skip.** Real long-term risk. Counter: registration is a one-time, 30-second action per template, and the system *refuses to build* without it for client decks. Skipping requires `--skip-registration` which is a visible audit trail. The friction is calibrated to be lower than the cost of shipping wrong colors and re-doing a deck.

---

## Migration plan

### Phase 0 — Day 1

Ship `register_template` as a new script in `slide-builder-simple/scripts/`. Behavior is opt-in: if `<template>.theme.yaml` exists, the build reads it; if not, the build falls back to today `load_client_theme()` path and emits a "consider registering this template" notice. No existing decks break.

### Phase 1 — Week 1

Run registration for the templates we know are in active use: FedEx, Accenture, NFL (the three clients flagged in v1 `client_theme.py`). Commit the resulting `.theme.yaml` files alongside each template in the project repos. Now the three known-bad cases all have human-confirmed themes; the v1 slot bug is moot for those clients.

### Phase 2 — Week 2

Flip the default. For `slide-builder-simple` (v2), `build_deck.py` refuses to run against an unregistered template unless `--skip-registration` is passed. v1 (`slide-builder`) keeps the old auto-extraction default until the v1 team is ready to flip — there is no forced lockstep migration.

### Phase 3 — Week 3+

Once both v1 and v2 default to registered-only, remove the slot heuristics from `client_theme.py` entirely. `load_client_theme()` becomes a YAML reader. The `is_branded()` / `_pick_brand_colors()` / `_resolve_brand()` / `KNOWN_CLIENT_HUE_RANGES` / `validate_theme()` code paths are deleted. That is ~400 lines of heuristic code retired in favor of a 30-line YAML loader plus a registration script.

### Templates already auto-handled by v1

Do not grandfather them in silently. The auto-extracted colors *may be wrong* (that is the entire premise). Force a 30-second re-registration per template. Print a one-line summary of what auto-extraction picked and let the user say "confirm" if they want to ratify the current behavior. For FedEx that confirmation is trivial because v1 happens to get FedEx right. For any client where v1 was silently wrong, the swatch PNG surfaces the bug.

### Transition window

During the window where some templates are registered and some are not, the loader decision tree is:

```
1. <template>.theme.yaml exists?
   YES -> read it; ignore PPTX theme XML for color/font decisions.
   NO  -> fall back to today auto-extraction; emit warning in dispatch_plan.md.
```

The two states coexist cleanly. The warning makes the gap visible without blocking work.

---

## Bottom line

Auto-extraction is the wrong frame. There is no algorithm that knows which slot is the marketing-approved primary because that information does not exist in the PPTX. Registration is a 30-second human step that produces a durable, version-controlled, override-able theme file. Builds become deterministic YAML reads. The other reviewers will propose better algorithms; this proposal eliminates the need for the algorithm. Pick this one.
