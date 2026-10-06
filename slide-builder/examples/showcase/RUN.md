# Regenerating the Slide Lab showcase examples

The three files people share to show what Slide Lab does
(`Slide-Lab-Example-Review.html`, `Slide-Lab-Example-Storyline.html`,
`Slide-Lab-Example-Deck.pptx`) come from **one real Slide Lab run**, never from
hand edits. Regenerate them whenever the review page, the final-check page or
the storyline page changes in a way users can see. A refresh takes about an
hour, most of it the person picking on the review page.

Everything is fictional: the Meridian brand, the template and every number.
Never use a client template or client content here.

## What is in this folder

| File | What it is |
|---|---|
| `make_meridian_template.py` | Builds the fictional Meridian template (16:9, 13.333 x 7.5 in, navy and amber, Arial) |
| `meridian-data.md` | The invented data sheet. Every number in the deck comes from it, so they tie out |
| `meridian-brief.md` | The storyline brief that passed the storyline gate (paths blanked, seal removed) |
| `make_showcase.py` | Turns a finished run into the three shareable files, with images embedded and local paths removed |

## The sequence

1. **Template.** `py -3 make_meridian_template.py "C:\Users\<you>\Slide Lab\templates\Meridian"`,
   then register it in chat: main color dark navy `0B3C49` (slot dk2), highlight
   amber `F2A541` (accent1), cover background navy, content layout
   "Title and Content", cover layout "Cover". Open the sample slide in
   PowerPoint and confirm.
2. **Session folder** on the local drive:
   `C:\Users\<you>\Slide Lab\sessions\Slide Lab Examples\<date> Meridian Southeast Asia\`.
   Copy `meridian-brief.md` to `_session\narrative-brief-southeast-asia-entry.md`,
   fill in `client_template` and `session_folder`, run storyline-helper's gate on
   it, and seal it (`seal_brief.py`). Then `emit_dot_dash.py` writes the storyline page.
3. **Build** the normal way (3 options per slide), log times in
   `_session\timing.log`, and have a person pick on REVIEW.html. Do not
   cherry-pick or redraw options.
4. **Final check, compile, slide-qc.** Fix Criticals and Majors through the
   pipeline (`apply_qc_fix.py` after a QC fix). `check_done.py` must pass.
   **Do not run the "deck is good" cleanup on this folder**: the export needs
   every option.
5. **Update `HOW_MADE` in `make_showcase.py`** with this run's measured times
   and every hand edit, then run
   `py -3 make_showcase.py --session "<session folder>" --dest "<where the shared files live>"`.
   It refuses if a local path is left in the shared files.
6. **Release scrub.** Open the review page and the deck. Check: every source line
   reads "Illustrative data, not real"; no real publisher is named; no retired
   buttons ("NONE", "+1 / +2 / +3"); the current buttons ("Replace these",
   "Leave out", the feedback chips) are present; the deck's File > Info shows
   "Slide Lab example", not a person's name.

## The 2026-10-05 run, measured

Rebuilt for the 12 pt type scale. The brief's titles and takeaways were rewritten
at the storyline check (facts with numbers, one line each). The owner asked Claude
to make the picks, which the build records as an override.

| Step | Time |
|---|---|
| Storyline check and seal | 5 min (rewrites approved in one reply) |
| Prep | 1 s |
| 10 slides x 3 designs, in parallel | 8.5 min (fastest slide 3.1, slowest 8.3) |
| Finalize + review page | 20 s |
| Picks to editable PowerPoint | about 4 min (script, plus the drawing agent on 3 slides) |
| Final-check page | 2 s |
| Compile | 38 s |
| Quality check (read all 10 slides, plus a PowerPoint render) | 0 Critical, 0 Major, 3 Advisory |

## The 2026-10-02 run, measured

| Step | Time |
|---|---|
| Storyline (from the finished data sheet) | 2 min |
| Prep | 18 s |
| 10 slides x 3 designs, in parallel | 12.6 min (fastest slide 5.9, slowest 12.8) |
| Previews + review page | 3.7 min (re-drew misnamed previews; fixed since) |
| Picks to editable PowerPoint (script, no agent) | 25 s |
| Finalize + final-check page | 1 min |
| Compile | 10 s |
| Quality check (read all 10 slides) | about 8 min |
| QC fix: redesign slide 5, compile, re-check | about 4 min |

Found and fixed during that run (all in Slide Lab, for every user): the brief
reader swallowed the slide divider; covers were numbered; designers typed the
"[add source here]" placeholder; previews were saved under the finished-slide
name; template text drawn twice; the sample registration slide kept an empty
body box; the review page showed a stale "brief_qc.json not found" box; QC fixes
sent the user back through both review pages.
