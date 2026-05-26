# Drift-Prevention Test Infrastructure Review

**Date:** 2026-05-26
**Author:** Test-infra angle (one of three committee voices)
**Scope:** v0.1 - what automated checks would catch the class of "fix landed at file level but not at content level" drift that the last two cleanup cycles missed.

---

## Verdict up front

The current `_contract.py` is good at **schema** and **import-time** drift but blind to **content-level** drift. Two cycles of cleanup passed contract, passed `install OK`, and still shipped a v1-era worker file because `Test-Path` answers "does the file exist?" not "does the file say what v0.1 needs it to say?". The fix is **not** more CI infrastructure - Mario is one person, GitHub Actions hasnt been wired, and elaborate harnesses rot. The fix is three small, targeted checks added to the existing `_contract.py` plus one pre-commit hook driven by it.

The bug pattern is consistent across all six caught drifts:

| Drift | Existence check passed | What content check would catch |
|---|---|---|
| Worker file v1-era content | `Test-Path` was True | grep for v0.1 sentinel (`option_A.py`) |
| `build_slide.py` ref in `icons/README.md:28` | n/a - no check existed | grep for deleted-script names across docs |
| CHANGELOG lists QUICKSTART.md | n/a - no check existed | grep CHANGELOG for files that dont exist on disk |
| `clean.py` `Optional[str]` no import | `import clean` succeeded (PEP 563 hid it) | `typing.get_type_hints(clean._is_forbidden_path)` would raise NameError |
| `compile_picks.py` uncaught save | imports clean, contract green | only an actual save into a locked file would catch this - end-to-end smoke needed |
| Memory file orphans / broken `[[link]]` | none - those are docs | grep `[[\w+]]` against memory dir listing |

Every drift is **a grep + a list-comprehension away** from being caught. None requires a CI runner, a test framework, or a build matrix. They all belong as new `check_*` functions inside the existing `_contract.py`.

---

## Question-by-question

### 1. Content validation - how to verify an install step installed the *right* content

**The bug.** INSTALL.md Step 6 used to be just `Test-Path` on the installed worker file. That passes for any file at that path, including a v1-era one with 4 options A/B/C/D and `/tmp/` paths. Mario already fixed INSTALL.md (lines 102-109 now grep for `option_A\.py`) - thats the right pattern.

**The principle:** every install step that copies content should grep the installed file for a **sentinel string unique to the current version**. Existence + content fingerprint, never just existence.

**Concrete check to add.** A new contract check that walks every "copy" step in INSTALL.md and verifies the source file in the repo contains the same sentinel the install step grep-asserts. This catches the inverse drift: if Mario edits the source worker file and removes the `option_A.py` reference (e.g., refactors to a different naming scheme), INSTALL.mds grep would silently pass on stale installed copies forever. Today the install-step grep is unenforced - nothing in the repo says "the source file MUST contain this string."

```python
# scripts/_contract.py - new check
INSTALL_SENTINELS = [
    # (relative path in skill, sentinel that v0.1 installs require)
    ("agents/slide-builder-worker.md", "option_A.py"),
]

def check_install_sentinels() -> list[str]:
    """Every file shipped via INSTALL.md must contain its sentinel.

    INSTALL.md Step 6s verification greps the *installed* file for
    option_A.py to prove the v0.1 worker was installed (not a stale
    v1 copy). This check enforces the reverse: the *source* file in
    the repo must also contain that sentinel, so the install-step
    grep cant silently pass on a stale source.
    """
    errors: list[str] = []
    skill_root = HERE.parent
    for relpath, sentinel in INSTALL_SENTINELS:
        f = skill_root / relpath
        if not f.exists():
            errors.append(f"install sentinel: {relpath} missing from source tree")
            continue
        if sentinel not in f.read_text(encoding="utf-8", errors="replace"):
            errors.append(f"install sentinel: {relpath} no longer contains {sentinel!r} - "
                          f"INSTALL.md Step 6 grep would silently pass on stale installs")
    if not errors:
        _ok(f"install sentinels: {len(INSTALL_SENTINELS)} file(s) carry their v0.1 sentinel")
    return errors
```

Thats 15 lines. One new tuple per future install step. This is the single highest-signal addition Mario can make.

### 2. Cross-reference integrity - broken `file:path` references in markdown

**The bug.** `slide-builder\icons\README.md:28` still says `build_slide.py calls icon_helper.insert_icon():`. `build_slide.py` was deleted in Phase 8. The reference is dead.

**The check.** Walk every `.md` file under the skill, regex-extract every token shaped like `<word>.py`, `<word>/<word>.py`, or backticked filename, and assert each named file exists somewhere in the skill tree. False positives are real (the doc may mention a deleted file *as* deleted) but easy to suppress with a small allowlist of "historical references" tags. The signal-to-noise after one tuning pass is excellent.

```python
# scripts/_contract.py - new check
import re

def check_doc_file_refs() -> list[str]:
    """Every <word>.py / <word>.md reference in skill docs must resolve.

    Catches: build_slide.py refs in icons/README.md after the script
    was deleted; QUICKSTART.md refs in CHANGELOG after the file was
    deleted in T1.1; memory-file [[link]] crossrefs to renamed files.
    """
    errors: list[str] = []
    skill_root = HERE.parent
    # Files Mario maintains as part of v0.1. Excludes _decisions/ which is
    # forensic history and intentionally references deleted things.
    doc_globs = ["*.md", "examples/*.md", "icons/*.md", "reference/**/*.md",
                 "agents/*.md"]
    ref_re = re.compile(r"`?([A-Za-z_][\w\-]*\.(py|md))`?")
    # Allowlist: references that are *intentional* mentions of deleted things,
    # tagged with HTML comment <!-- ref-ok: deleted --> on the same line.
    ALLOW_TAG = "<!-- ref-ok"

    for pat in doc_globs:
        for doc in skill_root.glob(pat):
            text = doc.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(text.splitlines(), 1):
                if ALLOW_TAG in line:
                    continue
                for m in ref_re.finditer(line):
                    name = m.group(1)
                    # cheap existence check across whole skill tree
                    hits = list(skill_root.rglob(name))
                    if not hits:
                        errors.append(f"doc xref: {doc.relative_to(skill_root)}:{i} "
                                      f"references {name!r} but no such file exists")
    if not errors:
        _ok("doc xrefs: every <name>.py/.md reference in v0.1 docs resolves")
    return errors
```

This is the second-highest-signal check. Run it once today and Mario would have caught both the `build_slide.py` and `QUICKSTART.md` drifts.

### 3. End-to-end smoke - does the pipeline actually work?

**The honest answer:** a real end-to-end run is expensive (LibreOffice render, mmdc, agent dispatch) and wont run in pre-commit. But a **Stage-1-only** smoke is cheap and would catch the `compile_picks.py` save-on-locked-file class.

Mario already has `smoke_test.py` at the skills root (9.5 KB, dated 2026-05-21). If that already exercises `build_deck.py --brief examples/quickstart-brief.md --template <ref template> --out _smoke_out/`, the gap is wiring it to run from `_contract.py` (or a single `make smoke` target). If its stale, heres the minimum to add inline:

```python
# scripts/_contract.py - new check (slow; opt-in via env var)
import os, subprocess, tempfile

def check_stage1_smoke() -> list[str]:
    """Run build_deck.py against the bundled quickstart brief.

    Catches: argparse regressions, _meta.json validation breaks,
    template registration drift, and brand.yml-load failures. Does
    NOT catch finalize/compile bugs - those need a worker dispatch
    and are out of scope for unit-level smoke.

    Opt-in: only runs when CONTRACT_SMOKE=1 is set, because it needs
    a registered template path. Mario sets this in his local shell.
    """
    if os.environ.get("CONTRACT_SMOKE") != "1":
        _ok("stage1 smoke: skipped (set CONTRACT_SMOKE=1 to run)")
        return []
    template = os.environ.get("CONTRACT_SMOKE_TEMPLATE")
    if not template or not Path(template).exists():
        return [f"stage1 smoke: CONTRACT_SMOKE_TEMPLATE not set or missing: {template!r}"]
    skill_root = HERE.parent
    brief = skill_root / "examples" / "quickstart-brief.md"
    with tempfile.TemporaryDirectory(prefix="slidelab_smoke_") as tmp:
        try:
            r = subprocess.run(
                [sys.executable, str(HERE / "build_deck.py"),
                 "--brief", str(brief),
                 "--template", template,
                 "--out", tmp],
                capture_output=True, text=True, timeout=120,
            )
        except subprocess.TimeoutExpired:
            return ["stage1 smoke: build_deck.py timed out after 120s"]
        if r.returncode != 0:
            return [f"stage1 smoke: build_deck.py exit={r.returncode}"]
        # Existence + content fingerprint, not just existence
        meta = Path(tmp) / "_meta.json"
        if not meta.exists():
            return ["stage1 smoke: _meta.json was not written"]
        if "schema_version" not in meta.read_text(encoding="utf-8"):
            return ["stage1 smoke: _meta.json missing schema_version key"]
    _ok("stage1 smoke: build_deck.py ran clean, _meta.json well-formed")
    return []
```

**What this misses:** finalize_deck + compile_picks. Those require a worker dispatch (an agent producing `option_A.py` for each slide) which cant be faked cheaply. The right pattern there is **stub option scripts checked into `examples/`** - a 4-slide brief with hand-written, deterministic option_A.py through option_C.py committed alongside it. Then finalize + compile can be smoked deterministically. Thats a separate, larger piece of work. Defer.

### 4. CHANGELOG hygiene - enforce "if file X was deleted, CHANGELOG doesnt list it"

**This falls out of check 2 for free.** CHANGELOG.md is one of the markdown files swept by `check_doc_file_refs`. The "Added" section in CHANGELOG mentions QUICKSTART.md; the check would have flagged it.

The one nuance: CHANGELOG legitimately mentions deleted things in its **"Removed"** section. Suppress with the `<!-- ref-ok -->` allowlist tag on those lines, or scope the regex to only check the "Added" / "Changed" sections of CHANGELOG specifically. Id start with the allowlist - simpler, more general.

### 5. Type-hint validation - catching `clean.py`s `Optional[str]` missing-import

**The bug.** `clean.py:36` has `from __future__ import annotations`. That defers all annotation evaluation to runtime via PEP 563, so `Optional[str]` at line 149 is treated as a string literal at import time. The reference is **never evaluated** unless something explicitly resolves type hints (e.g., `typing.get_type_hints`, pydantic, dataclasses with `slots`, FastAPI introspection). Standard import succeeds; the bug is invisible to `check_pipeline_imports`.

**The check.** Force evaluation of every function/methods type hints. One pass over every pipeline module:

```python
# scripts/_contract.py - new check
import typing, inspect, importlib

def check_type_hints_resolve() -> list[str]:
    """Force-evaluate every annotation in pipeline modules.

    With from __future__ import annotations, type hints are stored
    as strings and never resolved at import. A missing from typing
    import Optional survives check_pipeline_imports. This check
    calls typing.get_type_hints() on every callable in every module
    to surface NameError now instead of at first introspection.

    Audit finding T1-R: clean.py:149 used Optional[str] without
    importing Optional; masked by PEP 563.
    """
    targets = [
        "_paths", "_meta_schema", "_log",
        "build_deck", "finalize_deck", "compile_picks",
        "build_review", "build_gate_preview",
        "register_template", "clean", "diagnostic",
        "icon_helper", "render_mermaid",
    ]
    errors: list[str] = []
    checked = 0
    for name in targets:
        try:
            mod = importlib.import_module(name)
        except Exception:
            continue  # already reported by check_pipeline_imports
        for attr_name, attr in inspect.getmembers(mod):
            if not (inspect.isfunction(attr) or inspect.isclass(attr)):
                continue
            if getattr(attr, "__module__", None) != name:
                continue  # dont recheck re-exports
            try:
                typing.get_type_hints(attr)
                checked += 1
            except NameError as e:
                errors.append(f"unresolved type hint in {name}.{attr_name}: {e}")
            except Exception:
                pass
    if not errors:
        _ok(f"type hints: {checked} callables resolve cleanly under get_type_hints")
    return errors
```

That single check would have caught `clean.py:149` immediately. The category - `from __future__ import annotations` + missing-import - is a recurring foot-gun in modern Python and worth a one-time investment.

### 6. Pre-commit hooks - minimum set for a solo developer

Mario is one person. He wont maintain `.pre-commit-config.yaml` with five repos pinned by SHA. Keep it stupid:

**Option A - single hook, single command.** Add `.git/hooks/pre-commit` (no framework) that runs:

```bash
#!/usr/bin/env bash
set -e
py -3 slide-builder/scripts/_contract.py
```

Thats it. Every check above lives inside `_contract.py`. Pre-commit runs `_contract.py`. Fail = no commit.

To make this survive `git clone` (the `.git/hooks/` dir isnt versioned), add a one-time install command to INSTALL.md as Step 7:

```powershell
# Step 7 - pre-commit drift guard
$hook = ".git/hooks/pre-commit"
Set-Content -Path $hook -Value @"
#!/usr/bin/env bash
py -3 slide-builder/scripts/_contract.py
"@ -Encoding ascii
```

**Option B - `pre-commit` framework.** Overkill for one developer. Skip.

**What should the pre-commit catch and what should it skip?** Pre-commit must be < 3 seconds or it gets disabled. Default `_contract.py` runs the four existing checks + the three new fast checks (install sentinels, doc xrefs, type hints). The stage-1 smoke check is **opt-in** via `CONTRACT_SMOKE=1`; pre-commit doesnt set that. Mario runs it manually before a release tag.

---

## What Im *not* recommending

- **GitHub Actions.** Adds CI latency, a YAML file Mario doesnt care about, and pull-request-shaped friction Mario doesnt have. The git root has a `.github/workflows/` dir but the previous smoke workflow was removed (`eac11c9 Remove smoke-test workflow`). Dont reintroduce one yet. Local pre-commit + manual `CONTRACT_SMOKE=1` runs cover 95% of value.
- **pytest.** `_contract.py` is already a pytest substitute. Adding pytest adds a dependency, a discovery convention, and a runner. Not worth it for ~10 checks all callable from one entry point.
- **mypy/ruff.** Real value, but a tuning rabbit hole. Defer until v0.2.
- **Memory-file lint.** Mentioned in the prompt - worth doing but lives outside the skill (memory files are in `C:\Users\m.a.peralta\.claude\projects\C--Users-m-a-peralta--claude-skills\memory\`, not in the skills repo). Different harness, different scope. Defer.

---

## Concrete deliverables

If Mario implements only three of these, do them in this order:

1. **`check_install_sentinels`** in `_contract.py` - 15 lines, catches the worker-file class. Cost: 10 minutes.
2. **`check_doc_file_refs`** in `_contract.py` - 25 lines, catches `build_slide.py` + `QUICKSTART.md` classes + future link rot. Cost: 30 minutes including allowlist tuning.
3. **`check_type_hints_resolve`** in `_contract.py` - 30 lines, catches `clean.py`-class missing-import bugs. Cost: 20 minutes.

Then the pre-commit hook from section 6 (Option A). Cost: 5 minutes.

Total cost: about 70 minutes of work. Total drift prevented: every bug the last 24 hours surfaced except `compile_picks.py` save-on-locked-file (already fixed in T1-R2; needs end-to-end to regression-guard).

---

## The honest meta-point

The current `_contract.py` does what it advertises: schema sanity, import smoke, manifest coverage. Thats three of the six bugs covered. The other three are **doc-side drifts** and **content-vs-existence confusion** - and the contract test was never designed to see them. The bug isnt "the test infrastructure is weak"; its "were treating docs and install steps as exempt from the same kind of mechanical verification we apply to the Python pipeline." The three checks above close that gap without adding a framework, a CI runner, or a new dependency.
