# Smoke-test fixtures

This directory holds the self-bootstrapping fixture for
`tests/run_layout_inheritance_smoke.py`. **Contents are gitignored** (see
`.gitignore`) — the smoke regenerates everything on each run from source-of-
truth code, so committing the binaries would only invite stale-sha8 drift.

## How to populate

```bash
py -3 slide-builder/tests/run_layout_inheritance_smoke.py
```

That builds `layout_diverse_template.pptx` from python-pptx primitives (rename
+ dark-background XML mutation) and writes the brand.yml / chrome.yml /
theme.json sidecars next to it. Re-runs are idempotent unless `--rebuild` is
passed.

## Why a synthetic fixture

The v0.2 layout-inheritance audit (2026-05-28) could not run § 6.2 because no
template registered on the machine carried the full layout-class diversity
(cover_light + cover_dark + body_canonical_light + body_canonical_dark +
section_divider + section_divider_dark). FDX Template has 178 layouts but
none are dark-variant; the auto-registered audit template was 11
body-canonical layouts only.

The synthetic fixture closes that gap. It exists solely to exercise the
text_role color flip + bottom-anchor invariant under light/dark variants in a
reproducible, no-external-template way.

## Contract-test gating

`_contract.py::check_layout_inheritance_smoke_runs` gates on
`layout_diverse_template.pptx` existing on disk. A brand-new clone (no
fixture yet) sees:

```
ok: layout-inheritance smoke: skipped (fixture absent — run
    tests/run_layout_inheritance_smoke.py to build it)
```

Run the smoke once to bootstrap, then future contract-test runs include the
full 5-phase smoke check.
