# Slide Lab — Alpha Runbook

**Audience:** consultants on the alpha. Goal: produce a real client deck from a brief in <30 min without DM'ing the developer.

---

## Prerequisites (one-time)

1. **Clone the repo** and ensure your Claude Code instance is launched from `C:\Users\<you>\.claude\skills\` (or your equivalent).
2. **Confirm the `slide-builder` skill loads.** Run `/skill slide-builder` in Claude Code and confirm the skill responds.
3. **Have a client template handy.** A `.pptx` file (1280×720 widescreen) that defines your client's brand colors, fonts, and any required chrome. Save it under `_templates/<client>.pptx`.

---

## The 5-step flow

### Step 1 — Write a narrative brief

Run `/skill storyline-helper`. Answer the coaching questions:
- Objective (1 sentence — what does this deck DO?)
- Strategic framework (so-what)
- Narrative framework (per-slide so-whats)
- Deck type (recommendation / status / strategy / proposal / etc.)
- Client template path

storyline-helper produces a YAML brief at `<project>/<brief-name>.yaml`. **The brief MUST include `client_template:` in its front-matter** — if missing, the next step will error.

### Step 2 — Build the deck

Run `/skill slide-builder` with the brief path. The skill:
1. Validates the brief structure and the `client_template` path
2. Runs `_inspect_template.py` to capture template colors/fonts/layouts
3. Proposes 3 themed option slides per narrative slide (via `propose_options`)
4. Generates a review HTML showing all options

**Output:** `<project>/<deck-name>-review.html` opens in your browser. Each slide has 3 candidate panels with PNG previews.

### Step 3 — Pick options in the browser

For each slide on the review page:
- Click APPROVE on your preferred option (highlights it)
- Or click TWEAK and type feedback (free text)
- Or click NONE if all 3 are bad

When done, click "Copy YAML" at the bottom of the page. Paste back into Claude.

### Step 4 — Compose the final deck

Paste the YAML to Claude. The slide-builder skill:
1. Parses your picks
2. Hydrates any `feedback.*` overrides into the chosen pattern
3. Calls `compose_picked_deck()` to assemble the final PPTX using your client template

**Output:** `<project>/<deck-name>-final.pptx`. Open it in PowerPoint.

### Step 5 — Iterate (optional)

If the deck needs work:
- Edit the brief and re-run from Step 2 (full rebuild)
- Or edit the PPTX directly in PowerPoint and save
- Or paste new feedback into the review page and re-compose

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Client template not found" error | Check `client_template:` in your brief YAML. Path must be absolute and the file must exist. |
| Review page shows blank/missing PNGs | Re-run rendering: `python -m twins.themed_thumbnails`. Common cause: LibreOffice headless crashed mid-batch. |
| All 3 options for a slide look the same | Catalog `editorial_emphasis` and `intent_tags` may be too narrow on your brief's slide. Add more tags or broaden the intent. |
| Final PPTX is missing shapes | Builder selectors return shape names that don't match the composer's lookup. Check `compose_picked_deck()` log output for unmatched shape IDs. |
| Slide opens in PowerPoint but text is overflowing boxes | Hand-edit in PowerPoint. The builder uses fixed coordinates; placeholder text may differ in length from your real copy. |
| Build fails with `ModuleNotFoundError: render_slides` | Add `C:\Users\<you>\.claude\skills\slide-qc\scripts` to PYTHONPATH or run from inside the slide-builder dir. |

---

## What's NOT supported in alpha

- **Non-standard slide sizes.** Everything assumes 1280×720. 4:3 or vertical slides need a different builder set.
- **Multi-deck merge.** You can only build one deck at a time. To stitch decks, do it manually in PowerPoint.
- **Edit-mode after composition.** You can't edit a brief mid-flow and rebuild incrementally. Each build is fresh.
- **Charts driven by real data.** Charts use illustrative dummy data baked into the builder. Replace in PowerPoint after composition.

---

## Quick reference — file locations

| File | Purpose |
|---|---|
| `_templates/<client>.pptx` | Your client templates (master slides, brand fonts/colors) |
| `<project>/<brief>.yaml` | Narrative brief produced by storyline-helper |
| `<project>/<deck>-review.html` | Browser review page with 3 options per slide |
| `<project>/<deck>-final.pptx` | Final composed deck — open in PowerPoint |
| `slide-builder/twins/pattern_catalog.yaml` | Pattern catalog (selector reads this) |
| `slide-builder/twins/builders/build_NN.py` | One builder per pattern (300+ patterns) |
| `slide-builder/_renders/twins/NN_*.pptx` | Per-pattern reference PPTX (used by composer) |

---

## When to escalate

DM the developer if:
- Multiple builds fail with the same Python error
- The selector consistently picks bad patterns even with rich briefs
- The composer drops more than ~2 shapes per slide
- A client template doesn't translate (colors map wrong, fonts off)

For "this slide could look better" feedback, file a TWEAK during review — don't DM. The deferred backlog will handle it.

---

End of runbook.
