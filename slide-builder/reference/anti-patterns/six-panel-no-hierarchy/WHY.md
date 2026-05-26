# six-panel-no-hierarchy — WHY NOT

**Family:** Insight / Finding (attempted) — really a Value-Case Summary
**Verdict:** dont

## What the slide is trying to do

A single-slide "value case" for one lever in a transformation deck. The author
needs to cover, on one page:

1. Current state benchmarks (with comparison vs. peers)
2. Proposed value levers (broken out by sub-lever)
3. Quantified business impact (annual P&L + 5-year cumulative)
4. Current challenges (bullet list)
5. Key assumptions (bullet list)
6. Client support required (bullet list)

The author solves "six things on one slide" by laying out a 3-column top half
plus a 3-column bottom half — six independent content panels — and shrinking
every supporting text element to ~10pt so it fits.

## What's wrong

**Body-font floor violated.** Body text below the title is uniformly ~10pt
(13px). The body-font floor for a 1280x720 slide that will be projected in a
meeting room is 14px (~10.5pt PPTX). At 10pt, supporting text is unreadable
from more than a few feet away and even at full-screen on a laptop, dense
panels of 10pt text become an undifferentiated gray block.

**No hierarchy.** Inside each panel:
- Panel header ("Current State Benchmarks") = 10pt
- Sub-section label ("Cost per Invoice (loaded)") = 10pt
- Benchmark org name ("[Org]") = 10pt
- Benchmark value ("~$3.50") = 10pt
- Inline supporting note = 10pt

When everything is the same size, nothing is the headline. The eye has no
anchor point to fix on. The author DID size up two business-impact callouts
to ~22pt, but they are quarantined in column three; the rest of the slide
gives the reader no way to distinguish "headline number" from "footnote
qualifier."

**One slide, one idea — violated.** Six independent content blocks is a
short section, not a slide. Trying to compress a section onto one page is
what forced the 10pt default. The right move is to split: a benchmarks slide,
a levers slide, an impact slide, and an appendix slide for
challenges/assumptions/support.

**Header competition.** Six panel headers (top three + bottom three) all
compete with the slide title for first fixation. The reader has seven
"section start" elements on one slide.

## Why this is a teaching anti-exemplar

When an agent is handed a brief with too many content blocks for one slide,
the temptation is to keep adding panels and shrink the type to make it fit.
This exemplar shows what that produces: a wall of uniform 10pt text where
even the headline numbers fail to carry hierarchy. Agents should learn:

1. If the body floor (14px / 10.5pt) cannot accommodate the content count,
   the content count is wrong, not the body size.
2. Hierarchy comes from size variation. Same-size panels with same-size
   bullets contain no hierarchy regardless of how cleverly they are laid out.
3. "Six panels" is the smell. Three panels is plausible. Six is a section.

## What to do instead

**Option A — split the slide.** Promote the six panels to a 3-4 slide
mini-section:
- Slide 1: Headline + business impact (the two jumbo numbers, full canvas)
- Slide 2: Current state benchmarks (three benchmarks, each readable at 14px)
- Slide 3: Value levers (the five workstreams as a Comparison page)
- Appendix: Assumptions + support required (or fold into speaker notes)

**Option B — pick one of the six panels as load-bearing and demote the rest.**
Make the business-impact callout the slide's primary content, with one
supporting benchmark and one value-lever summary. Move challenges,
assumptions, and support required to appendix slides.

Either way: the slide must have a clear primary element at >=24pt, secondary
content at >=14pt, and supporting metadata at >=11pt. Uniform 10pt is never
the answer.
