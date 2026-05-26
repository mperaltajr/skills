# A/B Timing Review — Reviewer C (Strategic / Opportunity-Cost)

**Blind to:** Reviewers A and B.
**Angle:** What does each path *signal* about the project, and what hidden options is the coordinator's framing concealing?

---

## Verdict: PATH D — Ship v2 as the default for the next real deck. Don't A/B at all yet.

Not Path B. Not Path A. Not Path C. The A/B framing is the problem. Below is why.

---

## Reasoning (strategic angle)

### The A/B framing is performance theater dressed as rigor

The DECISIONS.md is unambiguous: v2 was built *because* v1 hit 23% curator acceptance after layering skeleton pre-assignment, SKELETON_REJECTED rules, rotation, Layer 5 collision, deadlock audit, and a 489-slug backfill on top of a wrong primitive. Three reviewers in round 1 flagged the lever-stack pattern; the empirical data validated them. v2 was conceived as a *replacement primitive*, not a sibling product.

Then somewhere between architecture-lock and now, the framing softened into "parallel skill, A/B test, may the best architecture win." That softening is the strategic mistake. v1 didn't *fail* a clean test against v2 — v1 failed against the *brief itself* (23% acceptance, fabrication bugs, twin bugs). v2 already cleared 5/5 SHIPPABLE on the same diagnostic slides that broke v1. The A/B is not "which architecture wins" — it's "let's re-prove what we already know, but politely, so nobody loses face."

That's the signal problem. Each path broadcasts:

- **Path A (A/B now, bug-tainted):** "We ship fast and iterate, even on dirty data." Fine signal for an internal velocity culture; terrible signal when the dirty input *is* the v1 loader bug v2 was partly built to escape. You'd be measuring the wrong thing on purpose.
- **Path B (wait 2 days, A/B clean):** "We wait for clean data before we measure." Sounds responsible. Actually signals: *we don't yet have the conviction to commit, so we're going to schedule a 2-day data-collection ritual to give us permission to do what we already plan to do.* This is the worst signal. It tells anyone watching that the team can't make a directional call without a 2-day external dependency unblocking it.
- **Path C (now + later, two data points):** "We measure everything." Signals careful but also signals indecision — and burns Mario's time twice on the same brief.
- **Path D (ship v2, let v1 die back):** "We made a call." Signals conviction. The risk is being wrong; the upside is recovering the 2 days and the parallel-maintenance tax v1 will keep extracting forever.
- **Path E (kill v2, all-in on v1):** Would signal "we admit the side-bet didn't pan out." Defensible 4 weeks ago. Not defensible after 12 agents x 4 test rounds x 17 PNGs validated v2 on the exact slides v1 fails.

The coordinator picked Path B because it's the safest *meeting* outcome. It's not the safest *project* outcome.

### Why we're A/B'ing at all (the real reason)

The decision to A/B implies v1 might win. Read DECISIONS.md section "Testing protocol" line 246: "Both perform similarly -> keep both, route by user preference." That outcome — *keep both* — is the tell. The framework has been written to make "keep both" a legitimate result. But "keep both" means Mario maintains two parallel skills indefinitely, and every future improvement gets debated twice. The A/B isn't measuring; it's *deferring the consolidation decision*.

What would actually push toward v1 winning? Honestly: nothing the slidelab-intro brief can show. The brief was designed around v1's documented failure modes (twin bug, fabrication bug, 60% convergence). v2 was architected against those failure modes. Running this brief through both is like asking a fish and a bird to compete at swimming. v1 has a structural disadvantage on the only brief currently queued. **Using slidelab-intro for the first A/B is performance theater.** If the project genuinely wanted to give v1 a fair shot, it would pick a brief v2 was *not* built around — a dense KPI scorecard, a quadrant matrix, a workflow-swimlane-heavy deck — where v1's 19-chassis vocabulary might shine.

### What Mario actually needs

Re-read the question: Mario is running both chats, dispatching reviewers, and asking *when* to A/B. He's not asking "is v2 ready" (artifact 6 verified end-to-end). He's not asking "is v1 better" (he wrote DECISIONS.md and authored both architectures). What he's asking, underneath, is: **"give me permission to commit to v2, or give me the one thing that would change my mind."**

The A/B doesn't produce that. The A/B produces a comparison report on a stacked-deck brief that v2 will probably win, and then *another* maintenance burden for both skills until the next A/B. What produces conviction is shipping v2 against a real client deck (FedEx OTC Reboot work is sitting right there per memory) and seeing if it holds up where it matters.

### The sunk-cost asymmetry cuts both ways

v1 has had vastly more investment — 19-chassis vocabulary, adjacency graph, Layer 5, 489 slugs, the whole hardening plan. That's sunk cost arguing *for* v1. But it's also the cost that produced 23% acceptance. The sunk cost isn't an asset; it's the receipt for the failed approach. Conversely, v2 has the "exciting new thing" halo, which biases the A/B in v2's favor. The honest read: both biases exist, they roughly cancel, and the real signal is the empirical data already in hand (5/5 SHIPPABLE on diagnostic slides). That data was generated *before* anyone was emotionally committed to v2 as a product. Trust it.

### The v1 theme rewrite is a separate decision and shouldn't gate this one

Path B's whole premise is "wait for v1's brand.yml rewrite so the A/B is clean." But DECISIONS.md section "Open — cross-skill dependency" line 276 explicitly states v2's current build is shippable for A/B in the interim because `validate_theme()` already halts on the failure mode the rewrite addresses. The loader bug taints v1's output, not v2's. Waiting 2 days doesn't help v2 — it only helps v1 look less broken. That's not data hygiene; that's handicap-balancing for a competition that shouldn't be happening.

---

## What the A/B is REALLY testing

Cut through the framing. The actual question being asked isn't "which architecture produces better slides." It's: **"can we justify deprecating v1 without anyone having to formally admit the chassis-vocabulary path was wrong?"**

The A/B is a face-saving mechanism. It lets the project arrive at "v2 wins, deprecate v1" through the appearance of empirical neutrality, when in fact the empirical neutrality was already established by the 12-agent / 4-round test that locked v2's architecture in the first place. We are about to spend 2 days waiting plus 1 day running an A/B to re-discover what 17 PNGs already showed.

The *useful* test is not v1-vs-v2 on slidelab-intro. The useful test is: **does v2 hold up on a brief it was NOT architected against?** That's a forward-looking question. A/B'ing on slidelab-intro is a backward-looking ritual.

---

## Biggest concern

Path B locks in **2 days of motion that produces no new information**. During those 2 days: v1 burns 2 dev-days on a theme rewrite that v2 will inherit transitively anyway (per the cross-skill dependency note). Mario doesn't ship a deck. No real client work moves. At the end of Day 2, the project is exactly where it is today plus a clean loader, and now everyone is committed to a ceremonial A/B that will tell them what they already know.

Worse: Path B's "wait for clean data" framing makes it *harder* to skip the A/B once Day 2 arrives. Sunk-cost dynamics will kick in — "we waited 2 days for this, we have to run it." The decision gets harder, not easier.

The strategic move is the opposite. **Ship v2 against the next real deck Mario actually needs to build** (FedEx OTC work per memory, or whichever client is on deck). Make v1 the explicit fallback for failure modes v2 doesn't yet cover (the deferred-to-v0.1 Mermaid types: fishbone, concentric rings — keep v1 alive *only* for those, with a sunset date). Skip the A/B entirely. The slidelab-intro brief becomes a regression fixture, not a competition arena.

If after the first real-client deck v2 visibly underperforms v1, *then* run the A/B. Conviction first, ceremony only if the conviction was wrong. The opposite ordering — ceremony to manufacture conviction — is what produced v1's lever-stack in the first place. Don't repeat the pattern at the meta-level.
