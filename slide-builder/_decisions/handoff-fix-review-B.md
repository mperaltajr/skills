# Reviewer B — build→finalize Mermaid theme handoff bug

## Verdict

**FIX NOW.** Option A. ~30 min. Anything else fails the production-grade bar Mario explicitly set.

Three-sentence summary: Option B ("ship as-is, document for v0.1") is the same deferral pattern Mario already rejected — it's "lazy" disguised as "knowingly accept" because the defense ("output looks right for FedEx") is coincidence, not engineering, and is structurally identical to the false-positive class that produced the prior smoke correction logged minutes ago in this same file. The bug is v2's own code from this session, not an inherited v1 defect, which removes the only legitimate "out of scope" argument. Fix in `build_deck.py` (write `_meta.json` with `mermaid_theme` + `client_slug`) and `finalize_deck.py` (fail loud when the per-client theme file referenced in `_meta.json` is missing, instead of silently falling back to `mermaid-brand.json`).

---

## Production-grade bar reasoning

Mario's bar names three legitimate paths: (1) fix, (2) knowingly accept with a defensible rationale, (3) shut down. Option B is being pitched as path (2). It isn't path (2). Here's why.

A "knowingly accept" rationale has to defend the **failure surface**, not the **happy-path output**. The failure surface here is: any non-FedEx client run through this pipeline produces a Mermaid PNG with wrong brand colors, and the build prints `mermaid theme : ...mermaid-brand.json` — which a reviewer scanning the console can easily misread as "the theme system ran." There is no exception, no warning, no log line saying "I could not find your per-client theme, falling back." It silently substitutes a different artifact.

The phrase "Mermaid colors are FedEx-shaped by coincidence so output is visually correct for THIS client" is the exact shape of the prior false positive. The smoke-test doc, in the Item 1 trigger-brief section, says verbatim:

> "v2's mermaid theme path has never actually been exercised against real client data. Every FedEx-purple PNG rendered to date used the hardcoded fallback defaults that happened to match FedEx, not extracted-from-template values."

That was logged as a **correction** — the prior reporting was retracted because reasoning from "the output looks right" while the substrate was coincidence-not-engineering was identified as a class of mistake to stop making. Option B asks us to do exactly that thing again, on the next code layer, in the same session. The same human, in the same file, retracting a finding and then proposing to commit the same finding's shape one layer up — that is a failure of discipline, not a defensible acceptance.

A real "knowingly accept" rationale would sound like: *"This handoff is brittle, the failure mode is silent-wrong-output for non-FedEx clients, we are committing to FedEx-only scope until v0.1, and the build emits a loud unconditional warning on every run that the mermaid theme path is unvalidated."* That rationale requires (a) scoping the skill explicitly to FedEx in SKILL.md, and (b) a loud runtime warning. Neither is in the Option B proposal. So Option B as written is not "knowingly accept" — it's "ship and hope the next reviewer doesn't notice."

---

## Is this the same false-positive class as before?

Yes. Structurally identical. Three layers, same disease:

| Layer | Symptom | Mechanism |
|---|---|---|
| Prior (logged today) | `generate_mermaid_theme()` looked correct for FedEx | Hardcoded defaults happened to match FedEx; `_lookup()` silently returned None |
| Now (this bug) | `_resolve_mermaid_theme()` looks correct for FedEx | `_meta.json` missing → silent fall-through to `mermaid-brand.json`; default happens to match FedEx |
| Cleanup 5 fix to `_hex()` | Same class, caught in `build_deck.py` | Loud raise on missing hex — the model for what this bug needs |

The Cleanup 5 fix is the precedent that settles this. The team already decided, this session, that the right response to "silent fall-through that happens to look right for FedEx" is **raise loudly**. Doing that in one location and refusing to do it in the analogous location is the kind of selective discipline that erodes trust in everything else. Either silent fall-through is acceptable or it isn't. The team picked "isn't" earlier in this session.

---

## Does "v2's own bug in same session" change the calculus?

Yes — it makes Option B worse, not the same.

When a team defers a v1 inherited bug, there's a legitimate "scope of this session" defense: *we didn't touch that code, fixing it requires context we don't have, the bug-fix surface area is uncontained.* None of that applies here. The code was written in this session by the same team. The fix surface area is two functions in two files. Both are open in the working tree. The context is fully loaded.

Deferring v2's own from-this-session bug to v0.1 is the explicit failure mode the production-grade bar names: deferring something that could be fixed in the same session because fixing it now feels like extra work. There is no "we'll get to it" defense when "now" is the cheapest moment it will ever be.

---

## "ACN smoke would surface it later" — feature or bug?

Bug. The ACN smoke would surface it as **a second instance of the same false-positive class we just retracted**. That is not "the smoke working correctly" — that is "we knew the bug existed, we shipped anyway, the smoke we ran to catch it caught it (as expected), and now we have to do the fix work plus re-run the smoke plus update the doc with a third retraction." Net cost is higher, not lower. The only thing deferring buys is the appearance of forward progress on Item 1 today.

And the deeper cost: the ACN smoke is supposed to be testing **a different question** (does v2 handle a non-FedEx brand correctly end-to-end). If the answer is "no because we deferred a known bug," the ACN smoke produces zero signal on its actual question — it just re-validates the known defect. The smoke becomes theatre.

---

## Cost of not fixing now vs. later

| Dimension | Fix now (Option A) | Defer to v0.1 (Option B) |
|---|---|---|
| Engineering time | ~30 min | ~30 min + context reload + re-running smokes + doc retraction = ~70+ min |
| Trust cost | Zero | Third entry in the false-positive ledger; partner-facing claim of "production-grade bar" weakens |
| Risk of silent-wrong shipped output | Eliminated | Survives until ACN smoke; non-zero risk a real client run sneaks through before then |
| Diff size | Two files, ~15 lines total | Same two files, plus retraction-doc edits |

There is no quadrant where Option B wins. The "saves time now" claim is wrong on arithmetic alone.

---

## Recommendation

Fix in this session. Two-part shape (Reviewer A picks the exact technical detail; this reviewer takes no position on the line shapes):

1. `build_deck.py` — after generating the per-client theme, write `<out>/_meta.json` containing `{"client_slug": "...", "mermaid_theme": "<absolute path to mermaid-<client_slug>.json>"}`.
2. `finalize_deck.py::_resolve_mermaid_theme()` — if `_meta.json` references a `mermaid_theme` path and that path does not exist, **raise**, don't fall through. The default `mermaid-brand.json` becomes a true generic-template path used only when `_meta.json` itself is absent (legacy / direct-invocation case), and even that case should print a clear warning that no per-client theme was generated.

The Cleanup 5 `_hex()` fix is the template. Match its loudness.
