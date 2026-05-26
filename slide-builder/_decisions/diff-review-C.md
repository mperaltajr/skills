# Reviewer C — prompt.md insertion (brand-token mandate) efficacy review

Reviewing the proposed 78-word bullet for § 5 "Variant picking rules" intended to prevent the slide-1 "zero brand color" defect from recurring.

---

## C1. Does the insertion actually prevent the failure mode?

**Mostly yes, with one real loophole.**

The defect agent wrote a "light canvas, no counter-line, standard typography" variant and reasoned itself into TEXT_DARK / TEXT_MID / TEXT_FAINT only. Reading the proposed constraint, that specific path is now closed: "A variant where every element renders only in TEXT_DARK / TEXT_MID / TEXT_FAINT is a brand-fidelity failure." That sentence is the load-bearing one. It names the exact token combo the failing agent used. An agent re-running the same brief and reading this would catch the violation in self-review.

The list of load-bearing elements ("hero text, accent rule, divider, anchor, or fill") covers every plausible cover-slide surface. Hero text (the product name) tinted BRAND_PRIMARY would have fixed slide-1 option A in one line of code. So would a counter-line accent rule, or BRAND_PRIMARY_MID on the tagline. The constraint gives the agent enough surface area; this is not a case where the rule forbids the failure but offers no compliant alternative.

**The loophole.** "On a load-bearing element" is squishy. An agent could put `BRAND_ACCENT_SOFT` on the meta italic "[Date]" line — technically a brand token visibly applied — and call it done. The `[Date]` placeholder is *not* load-bearing in the editorial sense, but the constraint does not say "load-bearing in the hierarchy of the slide"; it says "load-bearing element" and then enumerates options including "divider" and "anchor" which an agent could stretch. A more honest phrasing would tie the requirement to the slide's editorial focus: hero text, primary accent, or background fill. Underlines and placeholder meta should not qualify.

The "barely-visible underline" loophole is real but probably caught at the vision-QC pass downstream. Not blocking for v0, but worth a sharper word.

---

## C2. Conflict with "safe default" elsewhere in prompt.md?

**No direct conflict, and the insertion correctly redefines the term.**

§ 5 line 184 already says: *"One option SHOULD push the pattern further than the safe-default version (e.g., dark canvas instead of light, hero metric instead of bullets, oversized typography instead of standard)."*

That existing language frames "safe default" as a typographic/compositional choice (light vs. dark canvas, hero vs. bullets). The proposed insertion's phrasing — *"A 'safe default' is quieter typography or composition — not the absence of brand identity"* — is consistent with line 184's framing, not in tension with it. It tightens an implied definition rather than overriding it.

**Is the bug actually missing-instruction vs. agent-interpretation?** Mostly missing-instruction. § 5 does not contain the word "brand" or any reference to BRAND_PRIMARY/ACCENT tokens. The anti-patterns library (Aesthetics #1, #4, #5, #7) talks about *over*-using accent and contrast failures *on* dark fill — not about the absence of brand color on light canvas. There is no existing "DON'T render a brand-less slide" anti-pattern. The agent inferred that "safe default" = "neutral" because nothing told it otherwise. The insertion fills a genuine gap.

The constraint does not appear in layouts.md's Full canvas variant list either (line 70: *"light vs. dark canvas · counter-line yes/no · supporting tagline yes/no · type alignment"*) — so "light canvas + no counter-line + no other accent" is, today, a literally-legal variant combination. The insertion changes that.

---

## C3. Word count

**Exactly 78 words.** Verified by tokenize-and-count. The v2 cite is accurate. No restructuring rationale survives.

---

## C4. New failure modes?

**Two real concerns; one mitigatable, one a non-issue.**

**Concern (a) — over-decoration of editorially-sparse slides.** An editorial pull-quote, a single-statement claim, a "70%" hero finding — these slides are *meant* to be quiet. The constraint says "at least one brand token visibly," which is satisfiable with a single colored hero word or a 2px accent rule. That's fine. Where it gets risky is the closing sentence — *"Default to `BRAND_PRIMARY` for the most important element if no variant choice forces it"* — an agent could read this as "tint the hero word BRAND_PRIMARY" and turn what should be a stark gray-on-white pull quote into a purple-on-white slogan. The intent (a quiet brand-anchored slide) survives, but the editorial restraint of the original concept does not.

**Concern (b) — convergence across the three variants.** This is the more dangerous reading of the closing sentence. If three parallel agents each read "default to BRAND_PRIMARY for the most important element," all three options on slide 1 could land on "purple product name, otherwise gray." Now you have brand fidelity but three near-clones — which violates § 5's *"genuinely different, not three near-clones"* rule. The seeds were supposed to prevent convergence on variant choice; this default-rule re-introduces convergence on the *brand application*.

**Non-concern — dark-canvas / Full-fill variants.** When the variant is "dark canvas (BRAND_PRIMARY fill)," the requirement is satisfied automatically. The dark canvas IS the brand token. No additional accent forced; no conflict with anti-pattern #1 (accent overuse).

---

## C5. Is the closing default sentence load-bearing?

**It is load-bearing in the wrong direction. Drop it.**

The first four sentences of the insertion do the work: they define the constraint, name the failure mode (TEXT_DARK/TEXT_MID/TEXT_FAINT-only), and name the compliant surfaces (hero text, accent rule, divider, anchor, fill). An agent reading those four sentences has enough.

Sentence five — *"Default to `BRAND_PRIMARY` for the most important element if no variant choice forces it"* — invites the convergence bug from C4(b) and the over-decoration risk from C4(a). It also undercuts § 5's "three structurally distinct options" rule by giving all three agents the same default. If the four-sentence constraint is enough to catch the failure, the fifth sentence is net-negative.

---

## Suggested wording

Drop the closing sentence. Tighten the "load-bearing element" phrasing to exclude placeholder/meta surfaces. Add an explicit anti-convergence instruction.

> - **All three variants MUST use at least one brand token visibly on the slide's editorial focus.** A "safe default" is quieter typography or composition — not the absence of brand identity. Every option must include `BRAND_PRIMARY`, `BRAND_ACCENT`, `BRAND_PRIMARY_MID`, or `BRAND_ACCENT_SOFT` on the hero text, primary accent rule, anchor fill, or background — not on placeholder/meta lines like `[Date]` or footer chrome. A variant where every editorially-load-bearing element renders only in TEXT_DARK / TEXT_MID / TEXT_FAINT is a brand-fidelity failure. The three options must apply the brand token differently (different surface, different element) so they remain structurally distinct.

This is ~93 words (8% longer than the original 78), closes the placeholder loophole, and replaces the convergence-causing default with an explicit anti-convergence instruction.

---

## Verdict

**Insert with modifications.** The core constraint (sentences 1–4) is structurally correct and fills a real instructional gap. The closing default sentence (sentence 5) should be removed or replaced — as written, it introduces a new convergence failure mode that is at least as visible as the brand-less failure it is meant to fix. The "load-bearing element" phrasing should also be tightened to exclude placeholder/meta surfaces so an agent cannot satisfy the constraint with a tinted `[Date]` line.

If accepting modifications is out of scope and the choice is binary insert / do-not-insert as-written, lean toward inserting as-written — sentence 5's convergence risk is real but recoverable (user picks at REVIEW.html; non-determinism between agents further reduces it), and the four good sentences materially close the actual defect.
