# Reviewer B — post-Stage 4 plan review (code-level diagnosis)

Blind to A and C. Read the four scripts, the smoke-test option_A, and the smoke-test finding doc. Verdict-first below; receipts in "Code-level findings."

---

## Verdict on sequencing

**Audit-first is the right call, but not because it''s slow and careful — because the audit literally surfaces a third bug that "fix-first" would have missed.** `compile_picks.py` has the same path-contract drift as `build_review.py`. If v2 fixes only #4 and re-fires Stage 4, REVIEW.html will work, the user will pick, click "Build my deck," and Stage 5 will fail with `missing source: <out>/themed/slide_NN/option_A.pptx`. Another round-trip, more frustration.

So the sequencing debate isn''t process theater **in this case**. The coordinator is right for an empirical reason: the audit catches a real third bug. Once you find it, "fix all at once" collapses to one tiny patch, and the fix-first vs. audit-first distinction becomes moot.

What is theatrical: framing this as a deep architectural question. It is not. The fix is ~3 lines per script, all the same shape (delete one path segment). The audit takes 5 minutes. Stop treating this like an ADR.

## Verdict on defect 1 classification

**Reclassify to v0 — tighten prompt.md § 5 now.** I read § 5 closely. The relevant sentence is:

> "One option SHOULD push the pattern further than the safe-default version… The user picks among the three; offering one safer + two bolder is good."

That sentence licenses exactly the behavior that produced zero-brand-color option A. "Safe default" in current § 5 means "don''t push it" — which a literal agent reads as "no accent, no brand color, neutral typography." The smoke-test option_A.py is a near-perfect execution of that reading: no `BRAND_PRIMARY`, no `BRAND_ACCENT`, no `add_rect` with a fill, just three `add_text` calls and a footer.

The agent didn''t fail. The prompt failed. Fixing this at v0 is a one-paragraph addition (~80 words) to § 5. I drafted it inline below — the existing language is *not* structurally hostile to the fix; it''s a clean insertion. Defer-to-v0.1 is wrong here because the cost is trivial and the next smoke would reproduce the bug unchanged.

## Code-level findings

### Path mismatch: exact location + fix scope

**finalize_deck.py writes themed PPTX to** `<out>/slide_NN/option_X.pptx`. See line 416:

```python
themed_pptx_path=slide_dir / f"option_{letter}.pptx",
```

where `slide_dir = py.parent` (line 402). No `themed/` segment anywhere in finalize. Confirmed on disk: `<smoke_out>/slide_01/` contains `option_A.pptx` + `option_A.png` directly. No `<smoke_out>/themed/` directory exists.

**build_review.py reads from** `<out>/themed/slide_NN/option_X.pptx`. See lines 296–297:

```python
src_dir = out_dir / slide_id
themed_dir = out_dir / "themed" / slide_id
```

Then `themed_dir` is used at lines 315 (`png`), 316 (`themed_pptx`), 320 (`qc_path`). All three reads point at a directory that doesn''t exist. That''s why REVIEW.html shows "no thumbnail" + missing QC badges + empty themed paths.

**Fix scope: one line.** Change line 297 to `themed_dir = out_dir / slide_id` (drop the `"themed" /` segment). All downstream uses of `themed_dir` then resolve correctly. The variable name stays accurate semantically (it points to where the themed artifacts live; "themed" is now folder semantics, not a path segment). No other code touches the variable.

This is not a refactor. It''s a one-token deletion.

### compile_picks.py path bug: present? where?

**Yes. Same bug. Line 210:**

```python
src = out_dir / "themed" / key / f"option_{letter}.pptx"
```

`key` is `"slide_NN"`. Finalize writes the themed PPTX to `<out>/slide_NN/option_X.pptx`, not `<out>/themed/slide_NN/option_X.pptx`. If you fix only build_review.py and the user clicks "Build my deck," every pick will fail with `missing source: <out>/themed/slide_01/option_A.pptx` and COMPILED.md will report `Copied: 0 / N`.

**Fix scope: one line.** Drop `"themed" /` from line 210: `src = out_dir / key / f"option_{letter}.pptx"`. Done.

This is the third bug. It validates the coordinator''s "audit first" stance with hard evidence — fix-first would have shipped a working REVIEW.html and a broken Stage 5, which is worse than the current state because it''d take another smoke cycle to surface.

I did not find a fourth in the three scripts I read. The token conventions (FALLBACK_MERMAID, SKELETON_REJECTED) line up between finalize and build_review. The header regex in build_review (line 86, `_PATTERN_RE`) matches the header convention in prompt.md § 8 (em-dash + hyphen tolerated). No mismatch there.

### Prompt.md § 5 language: can the "safe default" tightening actually land cleanly?

**Yes.** § 5 has a clean insertion point right after the "One option SHOULD push the pattern further" sentence. Suggested addition:

> **"Safe default" never means "no brand color."** Every option must use at least one of `BRAND_PRIMARY`, `BRAND_PRIMARY_MID`, or `BRAND_ACCENT` as a visible element — accent rule, eyebrow, hero numeral, KPI fill, header band, divider. A "safe default" variant is safer in *layout choice* (centered vs. asymmetric, light vs. dark canvas) but still carries the brand. An all-text slide with only `TEXT_DARK` / `TEXT_MID` / `TEXT_FAINT` is a failed option, not a safe one — the client cannot tell which template it came from.

That''s 78 words. Drops in after line 184. No restructuring required. The fix is real and lands cleanly.

### v2''s reporting: one-off error or pattern?

**One-off, but symptomatic of "vibes reporting."** I read the smoke-test finding doc end to end. The error in question — slide 7''s principle names rendering coral because of `BRAND_PRIMARY_MID` color_map drift — is documented with specific mechanism (steps 1–4 in Architecture finding C). That''s not sloppy. The doc is precise about what happened and why.

But Architecture finding C''s *re-run section* says: "this run, the slide 7 agent used `TEXT_DARK` for the principle names instead — they render dark gray, as semantically expected." That''s the conflation: the run-1 coral was BRAND_PRIMARY_MID resolving through the theme; the run-2 dark gray was a *different token entirely*. They''re not the same element behaving differently — they''re different elements named "principle names" in two different builds. The doc treats them as comparable observations when they''re not.

That''s a small reporting hygiene issue, not a pattern. The rest of the doc is empirically solid (color hex codes traceable, classification counts cross-checked, seed-tiebreak math reproduced). I would not gate v2 progress on this. But the next smoke writeup should pin observations to the actual XML hex value extracted from the rendered PNG, not the agent''s free-text intent. That''s a one-line discipline change ("when reporting on color, quote the hex").

## Biggest concern

The fact that the audit found a *third* identical bug — same shape, same path segment, same script-fork drift from v1 — tells me the underlying problem is not these three scripts. It''s that v2 was forked from v1 by file copy + surgical edit, and the surgical edits diverged the *write-side path convention* in finalize_deck.py without updating the *read-side path convention* in the two downstream scripts. There''s no shared constant. No `OUT_LAYOUT.themed_pptx(slide_n, letter)` helper. Each script bakes its own assumption about where themed PPTX lives.

**This will happen again.** Any next-stage script (a slide-qc batcher, a regen dispatcher, an analytics roll-up) will be forked from v1 and will probably also assume `<out>/themed/slide_NN/`. The v0.1 fix is not "be more careful." It''s a tiny shared module — `slide-builder-simple/scripts/paths.py` — with one function per artifact type:

```python
def themed_pptx_path(out_dir, slide_n, letter): return out_dir / f"slide_{slide_n:02d}" / f"option_{letter}.pptx"
def themed_png_path(out_dir, slide_n, letter):  return out_dir / f"slide_{slide_n:02d}" / f"option_{letter}.png"
def qc_json_path(out_dir, slide_n, letter):     return out_dir / f"slide_{slide_n:02d}" / f"option_{letter}.qc.json"
```

Three lines. Imported by finalize, build_review, compile_picks. Locks the convention in one place. Future forks can''t drift.

Not blocking for the re-fire. But add it to v0.1 backlog with priority above the BRAND_PRIMARY_MID rename — this drift pattern has now bitten three scripts in one feature.
