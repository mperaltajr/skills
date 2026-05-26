# v1 Gate Violation - Reviewer C (Risk Angle)

## Summary (3 sentences)

Ratifying FedEx is defensible only because the smoke PNG happens to surface every variable that could have gone wrong on this template, but that is luck, not process, and the gate-bypass precedent it sets will silently break on ACN (two-purples disambiguation invisible in PNG) and NFL (strip_master_backgrounds is a binary flag whose miswiring may not show in a single-slide smoke). The two-stage approach as proposed is necessary but not sufficient: it catches Phase-1 inversion and gross hex swaps, but it misses near-neighbor hex picks, font fallback, and any setting whose visual footprint is smaller than the smoke render's pixel budget. My verdict is OTHER: ratify the FedEx artifact, treat the bypass as a defect, and before ACN harden the picker UX (inline hex + swatch + role label on one row, force typed-hex confirmation for any pair within the same color-family label) and make the smoke render multi-surface (title slide + content slide + chart-with-accent + a stripped-master diagnostic slide).

---

### Verdict: OTHER (ratify FedEx output, fix the gate before ACN/NFL, sharpen the picker UX)

Outright ratification rewards the shortcut and guarantees it recurs on the next two templates where the stakes are higher. Outright redo punishes a correct-by-luck outcome and burns trust without fixing the structural defect. Split the decision: keep the FedEx artifact, log the violation, and refuse to run ACN until the gate + picker are upgraded.

---

### Risk matrix

| Option | Likelihood of silent wrong-output | Cost if wrong | Cost if right |
|---|---|---|---|
| A. Ratify FedEx, same flow for ACN/NFL | High for ACN (two purples), Medium for NFL (strip flag), Low for FedEx (already shipped) | Wrong brand.yml lands; every downstream deck inherits wrong accent / wrong stripped background. Caught only when a partner sees a built deck. Rework cost: every deck built in the interim. | Save ~5 min per template |
| B. Delete + redo FedEx with two-stage gate | Low, but redo introduces fresh inputs (timestamp drift, re-prompted Mario picks possibly inconsistent with first run, register_template.py may have changed since) | Mario re-enters 6 inputs, possibly differently. Small risk of worse outcome than current artifact. ~10-15 min. | Restores discipline, but the precedent message is "we always redo on bypass" - fine, but expensive |
| C. Ratify FedEx + harden gate + sharpen picker before ACN | Low for FedEx (already verified), Low for ACN/NFL if picker UX is fixed | Engineering time to upgrade picker (~30-60 min). No deck-level risk. | Process improves; FedEx ships; ACN/NFL protected |

C dominates on expected cost. The only argument for B is symbolic ("we don't ratify bypasses") and that argument is weaker than "we don't ship a known-broken gate to two more templates."

---

### What ratifying FedEx could have hidden (even with a correct-looking PNG)

1. Font fallback. If FedEx's stated font was not installed on the render host, PIL/LibreOffice substitutes silently. The smoke PNG looks fine because the substitute is metrically close, but every built deck on a different machine renders differently. The smoke PNG cannot detect this unless it explicitly logs the resolved font family.
2. Near-neighbor hex swap. If Phase 3 offered two oranges in a different brand, and the picker recorded the wrong one, small deltaE means the PNG looks identical. Not a FedEx risk today (only one orange) but the mechanism that allowed it to ship is the same one ACN will trip on.
3. Wrong slot mapping. brand.yml has accent_primary, accent_secondary, text_heading. If two roles got swapped but the smoke slide only exercises one role, the swap is invisible until a chart legend renders.
4. strip_master_backgrounds default. FedEx may not have a master background to strip, so the flag is a no-op here. Whether it was set Y or N did not matter. That tells us nothing about whether the flag wiring works on NFL.

These are not hypotheticals; they are the exact failure classes the gate was designed to catch and which the bypass deferred to "we will see it in a real deck."

---

### Two-stage approach - what it catches, what it misses

Catches:
- Phase-1 inversion (dark template flagged as light, or vice versa): yes, smoke PNG shows this clearly
- Gross hex error (large deltaE): yes
- Layout slot misassignment when the slot is exercised on the smoke slide: yes

Misses:
- Near-neighbor hex picks within the same color-family label (ACN's two purples: #A100FF vs #460073 are far apart visually, but the picker LABEL - both literally "Purple" - is the failure mode, not the visual delta)
- Font resolution / fallback silently swapping families
- Roles not exercised by the smoke slide (footer color, hyperlink color, table-header fill, chart series 2+)
- strip_master_backgrounds when the template has no master background to strip (FedEx) - flag is untested
- Any setting whose visual signature is smaller than the smoke PNG's resampling artifacts

A two-stage gate that shows ONE smoke slide is a single-surface verifier on a multi-variable artifact. That is a coverage gap, not a process gap.

---

### ACN two-purples specifically

The picker showing both options labeled "Purple" with hex codes next to swatches is not enough for a tired Mario at 5pm Friday. Failure modes:

- Off-by-one: picker lists Purple-A100FF as option 3, Purple-460073 as option 4. Mario types "3" intending the dark one. Smoke PNG renders A100FF (bright magenta-purple), Mario sees "yeah, purple, ship it" because the bright/dark distinction blurs on a single accent shape against a white background.
- The swatch in a terminal/TUI is often a 1-character colored block; A100FF vs 460073 are both unambiguously "purple-ish" at that size, especially on a non-color-calibrated monitor.
- Even with hex codes shown, the picker is asking Mario to pattern-match a hex string he does not remember - he picks the label, not the hex.

Sharper mechanism needed for ACN:
1. When two candidates have the same role label AND the same human-readable color family, force a disambiguation prompt: "Two purples detected. Type the LAST FOUR HEX CHARS of the one you want: 00FF or 0073." That converts a pattern-match task into a copy task.
2. Render the smoke PNG with the accent applied to a filled rectangle + text on accent + chart bar so the visual delta between A100FF and 460073 is unmissable across multiple surfaces.
3. Always show role + family + full hex on one line in the confirmation echo: `accent_primary: Purple (#A100FF) - bright magenta-purple. Confirm Y/N.`

Without these, the two-stage gate will catch nothing on ACN that it did not catch on FedEx by luck.

---

### NFL strip_master_backgrounds

A single-slide smoke PNG rendered from a layout that does not inherit the stadium-photo master will look identical whether the flag is Y or N. The smoke must include a layout that DOES inherit the master, otherwise the flag is untested. Add a "diagnostic content slide" to the smoke render - a layout known to inherit master fills - so stadium photos either appear (flag wrong) or do not (flag right). Without this, NFL ratification will look clean and ship broken.

---

### Biggest concern

The bypass succeeded. That is the worst outcome, because it teaches v1 (and us) that the gate is theater. The next time it happens it will be on ACN, where the failure is invisible in the PNG, and Mario will sign off on the wrong purple. brand.yml will land. Every deck built against it for the next week will ship with the wrong accent. The discovery moment will be a partner review, not a smoke test. Fix the gate before ACN, or accept that brand.yml is an untrusted artifact for the rest of the engagement.
