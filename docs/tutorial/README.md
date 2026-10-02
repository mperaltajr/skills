# Slide Lab tutorial source
`tutorial_src.html` is the source of `Slide-Lab-Tutorial.html` (skills folder root); `review.png` and `final.png` are its two screenshots. Never edit the built file by hand.
To change a timing, count or button label, edit the facts block at the top of `tutorial_src.html`; to change text, edit the HTML.
Rebuild: `py -3 docs\tutorial\assemble.py`. It writes each fact into the page text (so it reads correctly with scripts off), embeds the screenshots and runs the check.
`py -3 slide-builder\scripts\check_tutorial.py` must pass before the tutorial is shared or committed.
