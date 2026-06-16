# Pattern B — Rollback flag design

> Defines the per-build `--pattern` flag in `build_deck.py` and the skill-wide `enable_pattern_b` feature flag in `settings.json`. Documents the rollback procedure if Pattern B underperforms.

**Status:** locked 2026-06-16.

---

## 1. The flag

`build_deck.py` gains a `--pattern` argument:

```python
parser.add_argument(
    "--pattern",
    choices=["auto", "B", "C", "legacy"],
    default=None,
    help=(
        "Build pattern. 'auto' (default when omitted) routes per-slide via "
        "Decision-2 classifier. 'B' forces HTML→translation for every slide. "
        "'C' forces native python-pptx direct for every slide (skips HTML "
        "stage). 'legacy' uses the pre-Pattern-B pipeline verbatim (same as "
        "schema_version 2). For rollback or debugging."
    ),
)
```

When `--pattern` is omitted, build_deck.py reads `enable_pattern_b` from `settings.json`. If `enable_pattern_b: true`, default is `auto`. If `false` (or settings.json missing), default is `legacy`.

This gives THREE tiers of control:
1. **Per-build CLI override** (`--pattern`) — explicit choice, highest priority
2. **Skill-wide setting** (`enable_pattern_b` in settings.json) — default for unflagged builds
3. **Skill-shipped default** — `legacy` initially (so installing the skill doesn't break existing user builds); flips to `auto` once Pattern B is validated

## 2. Per-pattern behavior

| `--pattern` value | Routing | Worker output | Translator dispatched | Schema written |
|---|---|---|---|---|
| `auto` | Per-slide via Decision-2 classifier | mixed (`.html` for B, `.py` for C) | yes, for B slides | v3 |
| `B` | All slides → Pattern B | `.html` for every slide | yes, for all slides | v3 |
| `C` | All slides → Pattern C (no HTML stage) | `.py` for every slide | no | v3 (`pattern_per_slide` all C) |
| `legacy` | Pre-Pattern-B pipeline | `.py` for every slide | no | v2 |

`legacy` differs from `C` only in schema version. v2 schema is what existed before Pattern B; finalize_deck.py treats it identically to v3-all-C but without the new fields.

## 3. settings.json structure

`$env:USERPROFILE\.claude\skills\slide-builder\settings.json`:

```json
{
  "default_pattern": "auto",
  "enable_pattern_b": true,
  "html_render_canvas": "1280x720",
  "ssim_thresholds": {
    "critical": 0.70,
    "major": 0.85,
    "pass": 0.90
  },
  "translator_timeout_seconds": 120
}
```

`build_deck.py` reads this file at startup (if it exists). Missing file = use shipped defaults. Missing fields = use shipped defaults per-field.

Initial shipped values (post-Pattern-B-cutover):
- `default_pattern`: `"legacy"` initially. Flip to `"auto"` after Pattern B passes 5-10 real builds without quality regression.
- `enable_pattern_b`: `false` initially. Flip to `true` together with `default_pattern`.

Flipping the defaults is a one-line PR; reversing them (rollback) is also one line.

## 4. Rollback procedure

If Pattern B ships and produces worse output than expected, three rollback tiers ordered fastest → slowest:

### Tier 1 — Per-build rollback (fastest, ~2-5 min)

User on a specific deck hits poor output. Run the same build with `--pattern legacy`:

```powershell
py -3 scripts/build_deck.py `
    --brief "<brief.md>" `
    --template "<template.pptx>" `
    --out "<out_dir>" `
    --pattern legacy
```

This re-prepares the deck with the pre-Pattern-B pipeline. Workers dispatch as before. Finalize runs the legacy path. **No code changes; no skill reinstall.** The user just adds one flag.

Recovery time: ~30 seconds re-prep + worker dispatch + finalize. Total ~2-5 min for a typical deck.

### Tier 2 — Skill-wide rollback (slower, ~5-10 min)

If Pattern B is consistently underperforming for the user across multiple briefs, edit `settings.json`:

```json
{
  "default_pattern": "legacy",
  "enable_pattern_b": false
}
```

All future builds default to legacy until re-flipped. User can still opt into Pattern B per-build with `--pattern B`.

Recovery time: 1 minute (edit + save). Then any new build uses legacy automatically.

### Tier 3 — Git revert (slowest, ~15-30 min)

Code-level revert of the Pattern B commits. Reserved for data corruption or build-breaking bugs in the skill itself.

```powershell
cd "$env:USERPROFILE\.claude\skills"
git log --oneline -- slide-builder/
git revert <pattern-b-commit-sha>...HEAD
```

Followed by:

```powershell
py -3 -m pip uninstall -y scikit-image playwright
```

If `playwright install chromium` was run, ~250 MB on disk. Remove with `playwright uninstall`.

Recovery time: 15-30 minutes including dep cleanup.

## 5. Routing classifier (`auto` mode)

Lives in `build_deck.py` as `_classify_all_slides()`. Implements Decision 2 (Moderate split):

```python
def classify_slide_pattern(brief_slide: dict) -> str:
    """
    Decide Pattern B vs Pattern C for one slide.
    Default: B (higher quality). Route to C only for pure-text slides.
    """
    # Pattern C triggers when ALL of these are true:
    has_chart = bool(brief_slide.get("chart_type"))
    has_table = "table" in (brief_slide.get("evidence", "") or "").lower()
    has_icon_ref = "icon" in (brief_slide.get("evidence", "") or "").lower()
    archetype = (brief_slide.get("archetype") or "").lower()

    # Pure-text archetypes (Pattern C eligible)
    pure_text_archetypes = {"cover/title", "section divider"}
    visual_archetypes = {
        "analytical", "framework/conceptual", "synthesis/findings",
        "roadmap/implementation", "risk", "financial/business case",
    }

    if archetype in pure_text_archetypes:
        return "C"
    if archetype in visual_archetypes:
        return "B"
    if has_chart or has_table or has_icon_ref:
        return "B"
    # Default: B (when in doubt, route to higher quality path)
    return "B"

def _classify_all_slides(slides: list[dict]) -> dict[int, str]:
    return {s["slide_n"]: classify_slide_pattern(s) for s in slides}
```

Override behavior: `--pattern B` forces all slides to B regardless of classifier. `--pattern C` forces all to C. `--pattern auto` uses the classifier per-slide.

## 6. Cutover sequence

1. Pattern B refactor lands. Skill ships with `default_pattern: legacy`, `enable_pattern_b: false`. **Zero impact on existing user builds.**
2. Power users (Mario) opt in per-build: `--pattern B` or `--pattern auto`.
3. Run 5-10 real builds across different briefs. Capture SSIM regression results.
4. If quality holds: flip shipped defaults to `default_pattern: auto`, `enable_pattern_b: true`. One commit.
5. If quality regresses: investigate, fix, re-test. Repeat 3.
6. Eventually: deprecate `legacy` path. (Probably 2-3 months after Pattern B is stable.)

## 7. Compatibility matrix

| Operation | Pattern B | Pattern C | Legacy |
|---|---|---|---|
| `build_deck.py --pattern B` | ✅ | — | — |
| `build_deck.py --pattern C` | — | ✅ | — |
| `build_deck.py --pattern legacy` | — | — | ✅ |
| `build_deck.py --pattern auto` | ✅ for B-routed slides | ✅ for C-routed slides | — |
| `build_deck.py` (no flag, `enable_pattern_b: true`) | ✅ for B-routed | ✅ for C-routed | — |
| `build_deck.py` (no flag, `enable_pattern_b: false`) | — | — | ✅ |
| Reading old `_meta.json` (schema v2) | — | — | ✅ (legacy mode) |
| Reading new `_meta.json` (schema v3) | ✅ | ✅ | ❌ (hard-fail, "schema too new") |

## 8. Integration points

| File | Change |
|---|---|
| `scripts/build_deck.py` | Add `--pattern` argument. Load settings.json. Implement `_classify_all_slides`. Write schema v3 with `pattern_per_slide`. |
| (new) `settings.json` | Document default keys; shipped values; reading logic. |
| `scripts/finalize_deck.py` | Route per `_meta.json["pattern_per_slide"]` when schema v3. Use legacy path when schema v2. |
| `SKILL.md` | Document the `--pattern` flag, settings.json, rollback procedure. |
| `INSTALL.md` | Note: Pattern B is opt-in initially (`--pattern B`); will be default after validation. |

## 9. Out of scope

- Per-slide CLI override (e.g., `--pattern-slide-5 C`) — out of scope; use brief edits or post-prep manual `_meta.json` edits if needed
- A/B testing automation (run same brief through both patterns and compare) — manual today; could be automated later
- Telemetry on pattern usage — out of scope; not collecting build stats

---

**Rollback is a flag flip, not a code revert.** This is intentional: Pattern B's biggest risk is unforeseen quality regression. Per-build, per-skill, and per-deployment rollback paths all exist. The user is never stuck on a bad pipeline.
