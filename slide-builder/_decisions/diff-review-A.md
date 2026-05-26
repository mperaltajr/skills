# Diff Review A — code correctness

Reviewer: A (blind to B, C)
Scope: 4 proposed fixes to v2 path drift (`themed/` segment removal) + prompt.md insertion.

---

## Verdict per fix

| # | Fix | Verdict |
|---|-----|---------|
| 1 | `build_review.py:297` swap to `src_dir` | **CLEAN** |
| 2 | `compile_picks.py:210` drop `"themed" /` | **CLEAN** |
| 3 | `compile_picks.py` docstring drift (lines 8/17/26/28) | **CLEAN — pure docs** |
| 4 | `prompt.md` § 5 brand-token bullet | OUT OF SCOPE for this reviewer (code-correctness only) |

**Single recommendation: APPLY AS-IS.**

---

## A1 — Fix 1 (build_review.py:297)

**Does removing `"themed"` point to where finalize_deck.py writes?** Yes. `finalize_deck.py` lines 416–417 define:

```
themed_pptx_path = slide_dir / f"option_{letter}.pptx"     # slide_dir == <out>/slide_NN
themed_png_path  = slide_dir / f"option_{letter}.png"
```

and line 962 writes `option_{letter}.qc.json` to `themed_pptx_path.parent` — i.e. `<out>/slide_NN/`. There is no `<out>/themed/slide_NN/` directory ever created. The current `build_review.py:297` points at a phantom path; the fix corrects it.

**Does any downstream code in `scan_slide` depend on `themed_dir` being a SEPARATE dir from `src_dir`?** No. Lines 315, 316, 320 use `themed_dir` for `option_X.png`, `option_X.pptx`, and `option_X.qc.json` respectively. Line 317 also computes `src_pptx = src_dir / f"option_{letter}.pptx"`. After the fix, `themed_pptx` and `src_pptx` will be the **same Path value** pointing at the same file. The dict assembled on lines 336–350 carries both (`themed_pptx`/`themed_exists` and `src_pptx`/`src_exists`) — they will just agree. Nothing reads the two as a delta (no diff, no exclusivity check). Idempotent and safe.

**Variable-naming conflicts / shadowing?** None. `themed_dir` is a local in `scan_slide` only; nothing global. The dict keys `themed_pptx`/`themed_exists` are semantic names consumed downstream (e.g. `build_html()` line 1103) and remain accurate even though physically the file now lives in `slide_NN/` — the THEMED PPTX *is* the one at that path.

---

## A2 — Fix 2 (compile_picks.py:210)

**Same as A1?** Yes. `src = out_dir / "themed" / key / f"option_{letter}.pptx"` becomes `src = out_dir / key / f"option_{letter}.pptx"`, matching what `finalize_deck.py` actually wrote.

**Does the loop logic assume the file is in a `themed/` subdir?** No. The only uses of `src` are:

- line 211: `src.exists()` — a boolean check, no parent inspection
- line 214: `src.name` — basename only, not parent
- line 218: `copy_picked_slide_into(dst_prs, src)` — opens via `Presentation(str(src))`, no parent walk

`copy_picked_slide_into()` (lines 106–122) does not touch the parent path either. Clean swap.

---

## A3 — Fix 3 (docstring drift)

Lines 8, 17, 26, 28 of `compile_picks.py` are inside the **module-level triple-quoted docstring**. They are not:

- argparse help strings (those are on lines 161–164, and reference no paths)
- `--help` output (driven by `description=` on line 160, which says `"Compile picked themed slides into a final deck (v2)."` — no path drift)
- f-strings, format templates, or any code

So yes — pure documentation. No code change beyond the docstring edits.

Note: `finalize_deck.py` line 769 has the matching correct path: `**Themed PPTX**: <out>/slide_NN/option_X.pptx`. That one is already right. Consistency across the two files after the fix is good.

---

## A4 — Other `"themed"` PATH-CONSTRUCTION lines the audit missed?

**No.** I grepped both files for `themed`. All other hits are:

- **Variable names**: `themed_dir`, `themed_pptx`, `themed_exists`, `themed_size`, `themed_paths`, `themed_pptx_path`, `themed_png_path`, `themed_statuses`, `themed_ok`. These are semantic — they describe the *role* of the file (the client-branded output) regardless of where it lives. Keep them.
- **String literals in docstrings/comments/print statements**: e.g. `compile_picks.py:1` "combine user-picked themed slides", `:203` `print("\n[2] Copy picked themed slides")`, `:945` JS toast `"No themed PPTX for this option."`. None are path-constructive.
- **HTML/JS labels**: `build_review.py:1244` `missing themed PPTX:` — display copy, not a path.

The only two physical path-construction sites with the literal `"themed"` segment in either file are exactly `build_review.py:297` and `compile_picks.py:210`. Audit caught both.

---

## A5 — Will fixes break v1 / shared infra?

No. The 4 proposed edits touch only:

- `slide-builder-simple/scripts/build_review.py`
- `slide-builder-simple/scripts/compile_picks.py`
- `slide-builder-simple/prompt.md`

V1 lives at `slide-builder/scripts/...` and is untouched. Shared infra used by v2 (`twins/composer`, `twins/client_theme`, `twins/helpers`, `slide-qc/scripts/render_slides`) is also untouched. The `sys.path` insertion on lines 49–50 of `compile_picks.py` and 73–74 of `finalize_deck.py` continues to work the same way.

V1 own `compile_picks.py` uses `<out>/themed/slide_NN/` and a different finalize step that actually writes there — that asymmetry is fine because the two skills are now decoupled.

---

## Other bugs found while reviewing

1. **`build_review.py:1234–1236` — dead counters.** `total_opts`, `missing_png`, `missing_themed` are computed but only printed once at the bottom (line 1244). Not a bug, just noise. After the fix, `missing_themed` will count the same files as `missing_png` (both come from the same dir now). Worth a note but not a blocker.

2. **`finalize_deck.py:406–409` — Mermaid PNG path is consistent.** `discover_options()` sets `mermaid_png_path = slide_dir / f"option_{letter}-mermaid.png"`, which lives in `<out>/slide_NN/`. The finalize docstring (line 43) and RESULT template (line 771) agree. No drift here — flagging only because it is adjacent to the cluster and worth a glance during the same review pass.

3. **`compile_picks.py:189` — `final_path` permission risk.** If `--final` points outside `out_dir`, `final_path.parent.mkdir(parents=True, exist_ok=True)` could silently create directories anywhere. Pre-existing behavior, not introduced by these fixes, but worth noting.

4. **`build_review.py` `themed_exists` and `src_exists` collapse to the same boolean after the fix.** Lines 341 and 343 currently expose both `themed_exists` and `src_exists` to the template. Cosmetic redundancy, not a bug. If you ever want to distinguish "raw built" from "themed", `src_exists` should instead point at `src_dir / "_raw" / f"option_{letter}.pptx"` per `finalize_deck.py` actual layout (line 415). Out of scope for this fix.

---

## Recommendation

**Apply all 4 diffs as-is.** They are minimal, correct, and reverse a documented path-drift bug. No modifications needed. No follow-up code changes required beyond the 4 lines + docstring cluster.

If the team has bandwidth, consider a small follow-up to (a) drop the now-redundant `src_pptx`/`src_exists` fields from `build_review.scan_slide` return dict, and (b) repoint `src_exists` at `_raw/option_X.pptx` if anyone cares about the raw-vs-themed distinction. Neither is required for the current fix to be correct.
