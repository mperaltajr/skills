# Pattern Library MASTER STATUS — 2026-05-19

Consolidated user review across all parts. Latest authoritative status of the pattern library.

## Grand totals (after re-fix review; excluding 327-351 and 199d-251d which weren't received)

| Part | Range | Reviewed | Approved | Tweak | Rejected | Pending |
|---|---|---|---|---|---|---|
| 1 | 001-100 | 100 | 67 | 24 | 6 | 3 |
| 2 | 101-251 | 151 | 81 | 44 | 24 | 2 |
| 3 | 252-326 (partial) | 75 | 49 | 14 | 10 | 2 |
| 4 | 01d-198d | 127 | 92 | 17 | 18 | 0 |
| Re-fix delta | 28 re-validated | — | +11 | -18 | +6 | +1 |
| **Total** | | **453** | **300** | **81** | **64** | **8** |

### Re-fix review summary (28 patterns the fix agents touched)

| New status | Count | Patterns |
|---|---|---|
| APPROVED (fix landed) | 11 | 35, 40, 44, 45, 63, 82, 86, 88, 168, 169, 198 |
| STILL TWEAK (fix incomplete) | 10 | 14, 19, 69, 87, 149, 157, 166, 188, 202, 231 |
| REJECTED (fix made worse or pattern not salvageable) | 6 | 20, 80, 90, 150, 191, 194 |
| PENDING | 1 | 182 |

Full re-fix details at `_status-2026-05-19-refix-raw.md`.

## What's missing from the review

- **Part 3 batch 4: patterns 327-351** (25 patterns from the v4 light batch — `327-`...`351-` HTML files exist but no decisions captured yet)
- **Part 4 batches 7+: dark variants 199d-251d** (if these dark variants were generated). The user's last part 4 batch covered 177d-198d. Either dark variants stop at ~198 or there are more not yet reviewed.

## Themes that drive the cleanup work

### 1. Legend-below-subheadline cluster (NOW 22 patterns)

Single recipe — legend right-aligned, just below subheadline + brand-rule, body content pushed down so nothing overlaps.

**Light patterns (parts 1-3):** 44, 63, 73, 86, 87, 90, 93, 102, 106, 109, 140, 141, 156, 191, 200, 206, 242, 246, 281, 297

**Dark patterns (part 4):** 44d, 63d, 86d, 87d

**Already fixed in this session** (5/22 with existing builders): 44, 63, 86, 87, 90, 191 — see commits below

### 2. Whitespace / fill-template cluster (~30 patterns)

Pattern is template-ready, default content too sparse, leaves bottom whitespace. Recipe: add more placeholder content, rebalance, OR add takeaway/bottom strip.

**Light:** 40, 88, 138, 149, 152, 159, 166, 168, 169, 180, 182, 187, 188, 194, 198, 199, 202, 215, 224, 228, 248, 267, 277, 278, 279, 308, 324, 325

**Dark:** 88d, 27d, 41d, 45d, 46d, 48d, 49d, 54d, 85d

**Already fixed (11/30+):** 40, 88, 149, 166, 168, 169, 182, 188, 194, 198, 202

### 3. Add takeaway / bottom strip (subset)

180, 182 (fixed), 228, 229

### 4. Individual fixes (per-pattern unique feedback)

See raw status files for specifics. ~30 patterns each with a unique TWEAK note.

**Already fixed:** 14, 19, 20, 35, 45, 69, 80, 82, 150, 157, 231

## Builders that need to be CREATED (newly approved or revived from rejected, no builder yet)

Light: 8 (revived), 55 (approved was rejected), 78 (approved was tweak), 79 (revived from rejected), 105-130 already built ✓, others mostly built ✓. Remaining: most newly-approved chart/diagram patterns 252-326 don't have builders.

**Dark variants: 0 builders exist.** All 92 newly-approved dark patterns need builders authored. Use the corresponding light pattern's builder as a template, swap background to dark, swap text colors to light, keep structure.

## Builders that need to be DELETED (newly rejected)

Light parts 1-3 newly rejected: 56, 83, 84, 99 (part 1), 103, 104, 107, 108, 110, 114, 115, 117, 119, 120, 121, 122, 123, 128, 129, 155, 164, 184, 216, 220, 236, 238, 240, 241 (part 2), 265, 273, 282, 284, 286, 302, 303, 304, 305, 306 (part 3 so far).

Dark variants 13d, 14d, 15d, 20d, 21d, 32d, 33d, 53d, 82d, 83d, 90d, 94d, 95d, 99d, 166d, 169d, 170d, 182d, 53d → no builders to delete (none built yet).

## Builders FIXED in this session (28)

Committed via fix agents 2026-05-19:

> 14, 19, 20, 35, 40, 44, 45, 63, 69, 80, 82, 86, 87, 88, 90, 149, 150, 157, 166, 168, 169, 182, 188, 191, 194, 198, 202, 231

These were re-rendered to PNG and placed in `_pattern-library/REVIEW-FIXES.html` for user re-validation.

## Recommended cleanup sequence

1. **Wait** for the missing part 3 batch 4 (327-351) for complete coverage.
2. **User validates REVIEW-FIXES.html** — approves/still-tweaks the 28 already-fixed builders.
3. **Delete builders** for newly-rejected patterns (~30 builders to delete from `twins/builders/`).
4. **Build NEW builders** for the dark variants (92 approved) and the newly-approved patterns 252-326 (49 approved). This is the biggest chunk — ~140 new builders.
5. **Apply remaining TWEAK fixes** that didn't get applied because the builder didn't exist (39 from first wave + more from parts 3+4).
6. **Update catalog** — add entries for approved dark variants and newly-approved light patterns; remove rejected entries; mark pending.
7. **Add `good_for` / `bad_for` metadata** (open item #11) — now that the pattern set is stable.
8. **Align selector vocab** to storyline-helper glossary (open item #1).
