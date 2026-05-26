# Reviewer C — Side-effect & regression review of v2's build_deck.py patch

### Verdict: APPLY AS-IS

The patch removes the right things, preserves the public surface that downstream
callers use, and the existing regression harness should still pass cleanly. One
double-call observation and two doc/comment cleanups are noted below but none
rise to "block landing."

---

### Per-question answer

**C1 — Deletions and orphan-caller check.**
v2 deleted the entire pre-`load_brand_sidecar` theme path. Specifically:

- `THEME_MAPPING` dict — removed. No survivors in the live file.
- `_lookup()` helper — removed.
- `find_template_json()` — removed.
- Their callers inside `generate_mermaid_theme()` have been replaced by
  `_compute_theme_variables(brand)`, which reads only `brand.primary_hex`,
  `accent_hex`, `font_heading`, `font_body`.

I grepped the entire `slide-builder-simple/` tree for `THEME_MAPPING|_lookup|
find_template_json`. The only remaining hits are in `_decisions/*.md` (review
docs describing pre-patch state) and one stale comment inside build_deck.py
itself at line 584 ("When v1 ships its load_client_theme fix, re-validate the
THEME_MAPPING table…"). That comment is now obsolete — see C7.

Cross-script callers: I also grepped `build_deck\.(THEME_MAPPING|_lookup|
find_template_json|generate_mermaid_theme|validate_theme|parse_brief|
forecast_pattern|compute_seeds)` across `slide-builder-simple/`. The only
external caller of build_deck symbols is `_verify_critical_fixes.py`, which
touches `parse_brief` and `validate_theme` — both still present, same
signatures. No orphan callers.

**C2 — Updated `validate_theme()` error messages.**
Read top-to-bottom (lines 637–748). The messages are semantically clean for the
brand.yml architecture:

- All five error branches name `brand_yml` (computed at line 658) as the
  source. No survivors of "v1 loader bug under fix," "THEME_MAPPING['primaryColor']",
  or "colors.dk2" / "colors.lt2" inside `validate_theme`.
- Hardline #4 recalibration text reads correctly: "human-confirmed at
  registration" / "slot-position guessing-bug class of failures is gone by
  construction" (line 734 comment + line 743 warning). The framing is
  internally consistent.
- The "Re-register interactively (do NOT use --auto-accept-phase1)" guidance
  in the equal-primary-accent branch (line 676) correctly inherits Reviewer
  B's inversion-risk concern from the stage-1 message.
- One nit: the Check 3 hue-mismatch error message at line 727 still suggests
  "Re-register or pass --client-name" — `--client-name` only renames the slug
  for the generated theme filename; it does NOT change the colors. That hint
  may mislead an operator into thinking the override fixes the hue problem.
  Not a blocker, but worth tightening in v0.1.

**C3 — Double-call of `load_brand_sidecar`.**
Yes — called twice:

1. `stage1_sanity_check(args.template)` at line 1036 → line 956.
2. `brand = load_brand_sidecar(args.template)` at line 1056 (theme-generation
   step).

The second call is NOT cached — it re-opens brand.yml, re-opens theme.json,
re-computes the file SHA. This is wasteful but functionally safe (the file
is small and read-only at this point; SHA on a real .pptx is a few hundred
ms). No correctness bug. Cleanup candidate: have `stage1_sanity_check` return
the brand dict and pass it through, so the second call is dropped. Flagging
but not blocking.

**C4 — Regression test pass-through.**
Walking `_verify_critical_fixes.py` against the patched file:

- **Check #1 (parser):** `SLIDE_HEADER_RE` at line 113 still matches
  `^#{2,3}\s+Slide\s+(\d+)`. `DECK_NOTES_RE` at line 117 still has the H1-H3
  lookahead. Both prior fixes are intact. PASS.
- **Check #2 (deck-notes terminator):** unchanged regex. PASS.
- **Check #3 (validate_theme on Microsoft-blue):** the function still returns
  `(errors, warnings)` tuple. The unknown-client warning text (line 738–746)
  contains both `"not in KNOWN_CLIENT_HUE_RANGES"` AND `"skipped"`, satisfying
  the test's assertion at line 208. The FedEx path with `#4D148C` (hue ≈ 273)
  still falls inside the 260–310 range. PASS.
- **Signature stability:** `validate_theme(theme_variables, template_path,
  template_json_path)` — the third parameter is preserved with a
  "kept for signature compat; no longer used" comment. The test calls it as
  `template_json_path=None`. PASS.
- **Seed computation:** `compute_seeds()` untouched (line 404). PASS.

Net: regression harness should report 3/3.

**C5 — Unknown-client warning text.**
Lines 738–746. Still useful: names the client, lists currently-registered
clients, explains what was skipped (Check 3), what still ran (structural),
and how to extend (`append an entry to KNOWN_CLIENT_HUE_RANGES`). The
"register the template" suggestion is now redundant in this warning because
registration is already enforced by Stage-1 — by the time we reach the
warning, brand.yml exists. So the absence of a "register the template" call
in the warning is correct, not a strip. Useful info retained.

**C6 — Cross-stream brittleness.**
- `load_brand_sidecar` + `BrandSidecarMissing` import contract: real risk but
  low. The names are stable in `slide-builder/twins/client_theme.py` (lines
  135 and 145). If v1 renames or restructures, v2 will fail-loud at import
  time (line 91–98 try/except), not silently mis-behave. Acceptable coupling.
- Schema assumptions: `_compute_theme_variables` reads `primary_hex`,
  `accent_hex`, `font_heading`, `font_body`. It does NOT touch `cover_bg_hex`,
  `primary_slot`, `accent_slot`, `cover_bg_slot`, `strip_master_backgrounds`,
  or `_template_sha` — all of which v1 returns. So v2 ignores 6 of the 10
  returned fields. That's robust to additions (v1 can add fields freely) but
  fragile to renames of the 4 fields v2 reads. The `_normalize_hex` contract
  (uppercase, no '#', 6 chars) is honored by `_compute_theme_variables`'s
  `[0-9A-F]{6}` regex. No issue today.

**C7 — Other changes v2 made.**
- The big block comment at lines 581–589 still references "the shared v1
  client_theme loader bug (multi-client templates returning Accenture's colors
  due to naive dk2->primary / lt2->accent slot mapping)" and mentions
  "the THEME_MAPPING table in reference/fallback.md." That block is stale —
  the bug class it describes is precisely what brand.yml eliminates. Should
  be rewritten or deleted in a doc-cleanup follow-up.
- The docstring at line 41 still references "the v1 client_theme loader-bug
  note in fallback.md" as part of the exit-code-6 explanation. Mildly stale
  but not wrong.
- The fallback-defaults inside `_compute_theme_variables` (`#4D148C`,
  `#FF6600`) are FedEx colors. If brand.yml has a missing/malformed
  `primary_hex`, the generated theme will silently look FedEx-purple. The
  `slots_using_fallback` list will record it, but a brand.yml with a typo
  would still produce a theme — just one that fails `validate_theme()`'s
  hue check (for FedEx) or passes silently (for non-FedEx, since Check 3
  doesn't fire for them and Check 2 won't catch saturated purple). Edge case;
  flagging for awareness.

---

### Side-effect summary

- Deleted: `THEME_MAPPING`, `_lookup`, `find_template_json` — no external
  callers; removal is clean.
- Added: `stage1_sanity_check`, `_check_mmdc_installed`, imports of `shutil`,
  `subprocess`, `os`, plus `load_brand_sidecar`, `BrandSidecarMissing` from
  v1's twins.client_theme.
- Modified: `_compute_theme_variables`, `generate_mermaid_theme`,
  `validate_theme`, `main()`. All retain stable signatures except
  `generate_mermaid_theme(client_slug, brand)` — previously took
  `(client_slug, theme_json_path, fonts)` or similar. No external callers
  (only `main()`), so this is safe.
- `validate_theme` keeps its `template_json_path` parameter for signature
  compat with the test harness; ignored internally. Good defensive choice.
- Stale documentation: 3 comment blocks still reference the deceased
  THEME_MAPPING / loader-bug narrative. Doc-cleanup ticket, not a blocker.

### Biggest concern

The double call to `load_brand_sidecar(args.template)` — once in
`stage1_sanity_check` (line 956), again at line 1056. It is not a correctness
bug today (idempotent, no cache invalidation gap), but it does two full
SHA-256 reads of the PPTX file. For a 50–100 MB FedEx template this adds
maybe 200–500 ms per prep run. More importantly, the *philosophical* shape
is wrong: stage-1 is supposed to verify, then main is supposed to use the
verified result. Passing the loaded dict through avoids the duplicate I/O and
makes the data-flow legible. Recommend cleanup in v0.1 but not blocking.
