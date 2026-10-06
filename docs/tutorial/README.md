# Slide Lab tutorial source
`tutorial_src.html` is the source of `Slide-Lab-Tutorial.html` (skills folder root); `review.png` and `final.png` are its two screenshots. Never edit the built file by hand.
To change a timing, count or button label, edit the facts block at the top of `tutorial_src.html`; to change text, edit the HTML.
Rebuild: `py -3 docs\tutorial\assemble.py`. It writes each fact into the page text (so it reads correctly with scripts off), embeds the screenshots and runs the check.
`py -3 slide-builder\scripts\check_tutorial.py` must pass before the tutorial is shared or committed.

The guide is one file of 25 pages. Each page is a `<section class="page">` directly inside `<main>`, with `data-tab` (its part in the top bar) and `data-title` (the window title); `tab-start` marks the first page of each part (each part starts on a new sheet when the whole guide is printed). Ids are the addresses (`#step-5`, `#r-type-scale`), so a new page or section needs a unique id and an entry in its part's group in the contents (`nav.side`). The page script shows one page at a time; with scripts off every page shows, stacked.
The `type` facts (body, floor, small, number of sizes, hero, in pt) are checked against `slide-builder\scripts\type_scale.py`, and every buzzword example on the page (`<span class="bw">`) against `slide-builder\reference\banned-words.md`.
