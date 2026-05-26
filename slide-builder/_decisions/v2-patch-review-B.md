# v2 Patch Review B — Stage-1 sanity check in build_deck.py

Reviewer B (blind to A and C). File reviewed:
`C:\Users\m.a.peralta\.claude\skills\slide-builder-simple\scripts\build_deck.py`

### Verdict: APPLY WITH CHANGES

The patch is structurally correct, fail-fast, and clearly written. The fail-path messages are usable. Two real defects keep it from "as-is": (1) the sanity check runs AFTER the output directory is created, leaving empty `<out>/` dirs on every failed prep run, and (2) the bare `except Exception` branch in `stage1_sanity_check()` will catch `SystemExit` and report it as "probably BrandSidecarStale or malformed brand.yml", which is misleading. Both are five-line fixes.

---

### Per-question answer

**B1. Call-site placement.** `stage1_sanity_check(args.template)` is invoked at **line 1036**, inside `main()`, AFTER `--template` existence check (1017), prompt-template existence (1020), and output-dir creation (1026) — but BEFORE `parse_brief()` (1041), the forecast loop (1047), the seed loop (1050), `load_brand_sidecar` for theme generation (1056), and the per-slide render loop (1097). So yes, it is BEFORE brief parsing and BEFORE any per-slide prep / agent dispatch. The Step 4 requirement is satisfied. Comment block at 1031–1035 explicitly cites Reviewer A's "proactive sanity check, not reactive fail-at-finalize" pattern.

**B2. Windows mmdc fallback.** `_check_mmdc_installed()` (lines 920–945) does it correctly:

1. `shutil.which("mmdc")` first (line 922).
2. If unresolved AND `os.name == "nt"`, falls back to two candidate paths (lines 925–928):
   - `%APPDATA%\npm\mmdc.cmd`
   - `%USERPROFILE%\AppData\Roaming\npm\mmdc.cmd`

These cover the two npm-global install locations on Windows (the second is the canonical resolution of the first when `APPDATA` is unset/empty — defensive). It uses `.cmd` rather than the bare executable, which is correct for npm shims on Windows. Minor gap: no nvm-for-Windows path (e.g., `%APPDATA%\nvm\<ver>\mmdc.cmd`), but that is a low-probability case for Mario's box and acceptable for v0.1.

**B3. Error handling for failed `--version`.** Lines 934–944 handle three modes:

- `FileNotFoundError` or `subprocess.TimeoutExpired` — caught at 938, returns `(False, "mmdc invocation failed: <type>: <msg>")`.
- Non-zero exit code — returns `(False, "mmdc --version returned exit <rc>: <stderr[:200]>")`.
- Zero exit but empty stdout — returns `(False, "mmdc --version returned empty stdout")`.

Timeout is 10 s, which is generous. The handling is graceful; the only thing missed is the broader `OSError` parent of `FileNotFoundError`. On Windows, `subprocess.run` of a `.cmd` file with malformed PATHEXT can raise `PermissionError` (an `OSError`). Worth widening the `except` tuple to `(OSError, subprocess.TimeoutExpired)` to be safe.

**B4. `load_brand_sidecar` vs `load_client_theme`.** The patch uses `load_brand_sidecar` (imported at line 91, called at line 956). Step 4's spec said "`load_client_theme()` warm-up" but the choice of `load_brand_sidecar` is **correct and intentional** for v2 — `load_client_theme` returns a `ClientTheme` dataclass that ALSO parses `theme1.xml` (palette accent slots) for text-color derivation, which v2 does not need at sanity-check time. `load_brand_sidecar` is the narrower, cheaper check: it raises `BrandSidecarMissing` (exactly the failure mode Step 4 calls out) and `BrandSidecarStale` (SHA mismatch — also valuable to catch at prep time). Inspected `client_theme.py:145–215` to confirm: it reads brand.yml + theme.json, verifies SHA, returns the dict v2 uses anyway at line 1056. No side effects on disk, no logging, no global state mutation. Choice is correct.

**B5. Error message clarity.**

- Brand-sidecar-missing (lines 958–967): tells Mario the EXACT command — `py -3 slide-builder/scripts/register_template.py "<path>"`. Quotes the template path so spaces are handled. Warns against `--auto-accept-phase1`. The underlying `BrandSidecarMissing` message (from `client_theme.py:163–173`) ALSO prints which sidecar files are missing, so Mario sees `MISSING: ...brand.yml` AND the v2 wrapper telling him to register. Good.
- mmdc-missing (lines 980–987): tells Mario the EXACT install command — `npm install -g @mermaid-js/mermaid-cli@11.4.0` — and a verify line. Pinned version matches the rest of the skill's contract.
- Distinguishable: brand-sidecar message starts "Client template not registered"; mmdc starts "Mermaid CLI (mmdc) not installed or not runnable". No risk of confusion.
- **No stale `THEME_MAPPING` / `template.json` references in the sanity-check messages.** The retired framing is gone from both error paths. (It still appears in legacy comment blocks around `validate_theme` at lines 583–588, but that is outside Step 4 scope.)

Both messages are usable by Mario without external context.

**B6. Exit code 7 on failure.** Verified end-to-end:

- `stage1_sanity_check()` returns `7` on both fail branches (lines 968, 975, 988).
- Call site at line 1037 — `if sanity_rc != 0: return sanity_rc` — propagates the value.
- `main()` returns into `sys.exit(main())` at line 1152.

The process really does exit 7. The docstring at line 42 documents this. Good.

**B7. Order: output dir vs. sanity check.** The output dir is created at line 1026 — BEFORE the sanity check at 1036. **This is the wrong order.** If sanity fails (brand sidecar missing OR mmdc missing), the patch leaves behind an empty (or pre-existing) `<out>/` directory but exits 7 with nothing written into it. Every retry attempt will silently re-create / touch the dir. The correct order is: validate template exists → validate prompt template exists → **sanity check** → create output dir → parse brief. That way a fail-fast run leaves no breadcrumbs on disk. Five-line move.

**B8. Race conditions / side effects.** I read `load_brand_sidecar` (client_theme.py:145–215). It reads two files (`<stem>.brand.yml`, `<stem>.theme.json`), parses them, runs `_sha256_of_file(template_path)`, and returns a dict. No file writes. No global state. No logger configured. No env-var mutation. The function is pure read. Safe to invoke twice (the call at line 956 sanity-checks; the call at line 1056 actually consumes the result — two reads, no caching, but disk-cheap). `_check_mmdc_installed()` runs a `subprocess` and reads env vars (`APPDATA`, `USERPROFILE`) — no side effects beyond the subprocess. Clean.

Additional side-effect note: lines 991–992 print `[stage-1 sanity] ...` audit lines to stdout on success. Good — gives Mario positive confirmation that sanity passed, with the version string. Worth keeping.

---

### Biggest concern

The output-dir-before-sanity-check ordering (B7). On a fresh laptop where mmdc is not installed, Mario runs `build_deck.py`, sees the exit-7 message telling him to `npm install -g ...`, runs that, retries. Meanwhile every fail-fast attempt has been creating (or touching, via `exist_ok=True`) the output directory. It is not destructive, but it violates the "no breadcrumbs on failed prep" expectation that fail-fast implies. The fix: move `args.out.mkdir(...)` from lines 1025–1029 to AFTER the sanity-check block at line 1038. This also implicitly fixes a second-order issue — if the sanity check ever grows to need a writable scratch dir, it will not conflict with the not-yet-validated output dir.

Secondary concern: the bare `except Exception` at line 969. `KeyboardInterrupt` is `BaseException` so it is safe from that, but it DOES catch `SystemExit` and `MemoryError`. The user-facing message ("Probably BrandSidecarStale — SHA mismatch — or malformed brand.yml") is misleading for anything other than those two. Narrow to `except (BrandSidecarStale, ValueError, OSError) as exc:` — `BrandSidecarStale` will need to be imported alongside `BrandSidecarMissing` at line 91.

Neither is a blocker. Apply with changes.
