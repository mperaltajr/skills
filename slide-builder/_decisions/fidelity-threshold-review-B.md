# Reviewer B — Script Adaptation Architecture (Shim / Patch / Fork)

Reviewer: B (blind to A, C)
Scope: Architectural shape for getting Hardline #4 (brief fidelity) measured in v2,
given that `slide-builder/tests/gate4/check_brief_fidelity.py` lives in v1 territory.

---

## Verdict: **Fork** (option 3). Not shim, not patch.

The shim option (1) is the cheap path. It is also the same move that produced the
`themed/` bug and the `sys.argv[1]` bug already documented in this skill's
audit history. Picking it again would be the third time we ratify the same anti-pattern.

The patch option (2) is worse. It puts v2-specific control flow inside v1's QC
script while v1 is mid-flight on its own theme-loader rewrite. Cross-skill
coupling at exactly the wrong moment.

The fork option (3) costs ~1.5–2 hours and creates a second copy of a ~180-line
script. That's real maintenance debt. Under the production-grade bar, it is
still the right call — for reasons that are mostly NOT about this script.

---

## Why shim is wrong (and why it's tempting)

Shimming means: v2 writes a synthetic `_meta.json` with `{"brief": "<path>"}`,
calls `check()` from v1's module, and gets a number back in 30 minutes.

Read lines 99–114 of `check_brief_fidelity.py`. The function entry point reads
`_meta.json`, expects a `brief` key with an absolute path, then walks
`out_dir/slide_*/option_*.py`. v2 writes `dispatch_plan.md` instead and stores
the brief path inside it as a Markdown bullet line. The directory layout
(`slide_NN/option_*.py`) does match — that's the temptation.

Three problems with shimming:

1. **It is the same disease the audit already named.** Reviewer A's diff-review
   (`diff-review-A.md`) and the prior cross-stream finding both traced the
   `themed/` bug to v2 having been forked from v1 file-by-file with no shared
   `paths.py` and no shared contract on where artifacts live. A shim doesn't
   fix that — it adds a second cross-skill contract (`_meta.json` shape) that
   v2 now silently depends on. When v1's QC script evolves (which it will —
   the `FALLBACK_MERMAID` gap proves the script is still maturing), v2 breaks
   in a way that is invisible until someone runs Gate 4 and gets a misleading
   pass/fail.

2. **`_meta.json` and `dispatch_plan.md` are not just file-format variants.
   They encode different mental models.** v1's `_meta.json` was a single
   machine-readable artifact. v2's `dispatch_plan.md` is human-readable, in
   line with v2's broader bias toward Markdown over JSON for parent-agent
   handoff. Shimming a JSON file back in re-introduces the v1 convention into
   a skill that explicitly chose Markdown. Now v2 has *both* — and which one
   is canonical for "where the brief lives"? Note that `finalize_deck.py`
   already writes `_finalize_meta.json` (line 924) — adding a shimmed
   `_meta.json` produces three overlapping deck-metadata artifacts, none of
   which fully describes the build.

3. **The thresholds problem doesn't get solved.** Lines 26–34 of
   `check_brief_fidelity.py` show that v1 has *already recalibrated twice*
   (0.30/0.70 from the strawman's 0.92/0.95) against v1's own observed
   distribution. A shimming v2 inherits those v1-recalibrated numbers
   silently, with no statement of whether v2's distribution looks the same.
   Best case: the numbers happen to fit. Worst case: v2 ships a Hardline #4
   measurement that is calibrated against the wrong tool's empirical data
   and either passes-when-it-shouldn't or fails-when-it-shouldn't. Either
   way, the metric loses its meaning.

The shim's "30 minutes" framing is a sunk-cost trap. It gets a number out
fast, but the number doesn't mean what the consumer thinks it means.

---

## Why patching v1's script is worse

Adding a `FALLBACK_MERMAID` handler inside v1's `check_brief_fidelity_for_option`
puts v2 vocabulary into a v1 module. v1's Gate 4 runner imports the same module
(see `slide-builder/tests/gate4/run_gate4.py`). Now any change to that handler
must be regression-tested against v1 fixtures AND v2 fixtures simultaneously.

Worse, v1 is mid-rewrite on `twins/client_theme.py` (see lines 562–581 of
`build_deck.py`'s `validate_theme` docstring referencing the v1 loader bug
under fix). Cross-skill coupling at the QC layer during an active v1 refactor
is exactly the configuration where invisible regressions land.

Patch is the wrong move here.

---

## On forking: thresholds inherited from v1 or recalibrated for v2?

**Recalibrated independently against v2's empirical data.** Not inherited.

Here is the math from the script itself. Line 27 documents that v1's healthy
decks score 0.35–0.95 *per OPTION* with deck-avg ~0.77, and that slide 11
composite legitimately hit 0.354. Those numbers came from "the first real run"
of v1's Gate 4. v2's pattern library, prompt structure, agent dispatch, and
brand-token rules are all different from v1's — v2 explicitly uses 9 geometric
splits + 3 diagram primitives + 2 special objects, where v1 used a larger
pattern-library skeleton system. The TOKEN distributions agents produce will
be different by construction.

The honest path is:

1. Fork the script + helper modules (`_chrome.py`, `_structural.py`,
   `_tokens.py`, `_porter.py`) into `slide-builder-simple/scripts/qc/`.
2. Adapt entry point to read brief path from `dispatch_plan.md` (or, better,
   take it as an explicit CLI arg — `--brief <path> --out <dir>` — and drop
   the contract dependency entirely).
3. Handle `FALLBACK_MERMAID` files (skip-with-classification, same shape as
   `SKELETON_REJECTED`).
4. Run v2 against 3–5 real briefs, record observed per-option / per-slide /
   deck-avg distributions, set thresholds at the 5th-percentile floor (or
   wherever the structural-flag-zero band actually sits in v2's data).
5. Document the calibration in the v2 script header the way v1 did on lines
   26–34.

Inheriting v1's 0.30/0.70 without v2-side calibration would repeat the
mistake v1 already noticed and fixed — the strawman's 0.92/0.95 were
"author-estimated" and didn't survive contact with real data.

---

## "No shared paths.py" → "no shared QC scripts"? Same disease, different surface?

Partly yes, partly no. This is the question that matters most.

**Yes, in this sense:** the underlying disease is that v1 and v2 were forked
file-by-file with no formal contract about which conventions are shared. Path
construction was one surface (`themed/`); QC-input contracts (`_meta.json`)
are another; threshold semantics are a third. A shared QC library would, in
principle, prevent that drift.

**No, in this sense:** v1 and v2 are intentionally diverging on the *content*
they produce. v2's pattern set, brand-token rules, `FALLBACK_MERMAID` handling,
and dispatch-plan artifact are deliberate departures, not accidental drift.
A "shared QC script" with v1-or-v2 control flow forks inside it would carry
all the same cross-skill coupling pain as patching, just one layer up. The
right shared layer is not the QC script itself — it's the *contract* the QC
script consumes: "where is the brief? where are the option files? what does
a rejected file look like?" That contract could live in a tiny shared module
(`shared/qc_contract.py`) that both skills produce against, and each skill
runs its own QC on top of.

For v0, fork the script. For v1.x of the v2 skill, propose a shared
`qc_contract.py` as the medium-term anti-drift move. Don't conflate the two
horizons.

---

## Biggest concern

The biggest concern is **not** the script architecture. It is the threshold
calibration in isolation from v2's empirical data.

If v2 forks the script and inherits v1's 0.30/0.70 because "those numbers
worked there," Hardline #4 will become a number that is reported with
confidence but means nothing — exactly the failure mode v1 already corrected
once. The fork is only worth the 1.5–2 hours if step 4 (run v2 against 3–5
briefs and set thresholds from observed distribution) actually happens. If
the team will shortcut step 4 to save time, the fork degenerates to a worse
shim, and option C (downgrade Hardline #4 to "unmeasured in v0") is more
honest than any of the three.

In rank order: Fork-with-recalibration > Option C (downgrade, honestly
unmeasured) > Shim > Patch. Pick one of the top two. Don't ship a
fork-with-inherited-thresholds; it's the worst combination of cost and
dishonesty.

---

## Summary

- **Architecture:** Fork (option 3). Not shim, not patch.
- **Thresholds:** Recalibrate against v2's own data. Do not inherit v1's.
- **Broader pattern:** Same disease as "no shared paths.py" in spirit, but
  the right fix isn't a shared QC script — it's a shared QC *contract*
  (where artifacts live, how rejection is signaled) that both skills target
  independently.
- **If you can't commit to the recalibration step**, take option C and mark
  Hardline #4 unmeasured-in-v0. A fake measurement is worse than no
  measurement.
