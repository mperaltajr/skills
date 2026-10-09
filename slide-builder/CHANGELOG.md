# Changelog — Slide Lab

All notable changes to this skill. Versioning follows [Semantic Versioning](https://semver.org/) loosely: major bumps signal architectural changes, minor bumps signal feature additions, patch bumps signal fixes.

## 2026-10-09: comments before conversion, picks kept, PowerPoint by default

### Review page and comments

- **Comments on a pick are applied before it is converted** (owner's
  decision). The review page's "Build my deck" message carries a `Feedback:`
  block (quick-feedback chips and typed notes per slide), but
  `record_picks.py` converted every pick at once and nothing read the block,
  so comments were missed or applied by hand after conversion (the slide was
  converted twice and agent-drawn parts redone). Now `record_picks.py` parses
  the block (pass the whole message to `--approved`; in chat, each comment as
  `--comment "N: <the user's words>"`, which must appear in their words). A
  picked slide with comments is recorded as **edit first** and is not
  converted; the other picks are. It writes `slide_NN/_edit_request.md`, and
  one `slide-builder-worker` per such slide, in its new **EDIT MODE**, edits
  the picked design in place (same layout, the comments applied, option letter
  unchanged) and re-renders the sketch. `record_picks.py --edits-done` then
  refuses a slide whose design did not change or whose option letters changed,
  marks the comments applied, keeps the picks, and converts the edited picks
  together in one call.
- **A comment asking for a different design is a Replace request** (the
  "Wrong layout / structure" chip, "try a chart instead", "a different
  layout"). `record_picks.py` drops that pick, writes the comment to
  `slide_NN/_prior_feedback.md` and records the redesign round; Claude asks
  the user for one or three new designs, three preselected (owner's decision,
  2026-10-08). `redesign_round.py finish` refuses while a slide still waits on
  an edit, converts every pick that needs it, finalizes the whole deck for a
  round started from comments, and marks the comment applied.
- **No comment is dropped.** Every comment is kept in the build record with
  how it was applied (edited in place, redesigned, or not needed on a slide
  the user left out). FINAL-CHECK.html refuses while one is pending;
  `check_done.py` refuses a deck with one never applied and lists them all at
  delivery.
- **The review page keeps picks between rounds.** The per-slide stamp hashed
  every `option_*` `.py`/`.html`, including the `option_X_native.py` the
  conversion writes, so every converted pick looked changed on the next page
  and was dropped, while its comments stayed. The stamp now covers only the
  designer's files (`option_X.html`, `option_X.py`). Comments are stored per
  slide with the stamp, like picks: a slide edited in place or redesigned
  starts with no comments, comments on untouched slides stay. Recorded picks
  (kept in the build record across prep) are written into the next
  REVIEW.html, so they are preselected in any browser, with a small "Kept from
  last round" mark ("edited from your comments" on a slide edited in place,
  which keeps its letter); a redesigned slide starts empty. A pick still never
  lands on a slide whose designs changed under it, except that edit in place.
- Tests: `tests/run_comments_before_conversion_smoke.py` (picks with and
  without feedback, only the unflagged slides convert first, all convert after
  the edit, the redesign and left-out cases, the delivery list),
  `tests/run_picks_kept_smoke.py` (the stamp, and two review rounds driven in
  a real page through `scripts/_browser.py`, in the same and a fresh browser).

### Automatic QC fixes

- **Layout and format findings are fixed without asking** (owner's decision).
  After slide-qc, every Critical and every Major in the layout/format group
  (text under the size floor or more than 3 body sizes, overflow or clipping,
  overlap, an arrow into a box, a panel vanishing on the background, chrome
  drift or a misplaced takeaway / footnote / source line, template sample
  text, a missing footer or page number, an axis without a unit, color palette
  drift) is fixed automatically, at most two rounds. Content Majors (a number
  or label not in the brief, buzzwords or hedging, a headline that is not a
  fact or is a topic label, bullets not parallel, a missing source where one
  was expected, anything that rewrites words or numbers) still go to the user
  in one table with proposed fixes and one reply. Then ONE message: what was
  fixed per slide (before/after pictures), the content table, what is open.
- `scripts/qc_fix_policy.py` is the one place that classes a finding (category
  key -> automatic or ask; `--list`, `classify`); slide-qc's report tags each
  finding with its key. Unrecognized Majors are asked.
- `apply_qc_fix.py --snapshot` keeps a slide's current design (and the deck)
  before the rebuild; `--auto "<findings>"` records the fix as an automatic
  fix with its finding text (not as a user approval), refuses a content
  finding, a slide with no snapshot and a third round, compiles, and prints
  before/after picture paths; `--undo N --approved "<the user's words>"`
  restores slide N's earlier design and compiles again. `check_done.py` lists
  every automatic fix at delivery as "fixed automatically", with any undo.
- Test: `tests/run_auto_qc_fix_smoke.py` (a fictional deck with one Critical,
  two layout Majors and one content Major: three fixed and recorded without
  approval, the content one refused for asking, no third round, undo restores
  the slide).

### Rendering through PowerPoint

- **PowerPoint is the default renderer on Windows** (owner's decision). When
  PowerPoint is installed, every render goes through it: the converter's
  self-check, finalize (and so the final check page), compile, slide-qc,
  the template setup's preview, layout thumbnails and sample slide, and the
  style-reference pictures. LibreOffice is only a backup there; a Mac stays on
  LibreOffice. All PowerPoint use goes through `slide-qc/scripts/ppt_safe.py`
  (read-only, no window, closes only its own file, quits only a PowerPoint it
  started with nothing else open in it). New setting
  `settings.json::renderer` = `auto` (PowerPoint on Windows when installed,
  else LibreOffice) | `powerpoint` | `libreoffice`; `SLIDE_LAB_RENDERER`
  overrides it for one run. `render_slides.render()` / `to_pdf()` are the one
  entry point; `render_slides.py --engine` now defaults to `auto`.
- **One deck per round.** The converter's self-check
  (`translate_alarm.render_full`, so `translate_html.self_check` and its
  re-renders after a step-down) and finalize's renders put every slide of the
  round into ONE temporary deck, render it once and hand each page back to
  its slide (`scripts/one_deck.py`). Re-renders after a fix render only the
  changed slides, also as one deck. Slides merge only with decks built on the
  same template (masters, layouts, theme, table styles, slide size, default
  text); hidden slides are shown in the render deck and the page count is
  checked before any page is handed back. When the merged deck fails (one bad
  slide makes PowerPoint refuse the whole file), it is halved until the bad
  slide stands alone, so only that slide is reported as failed, with its own
  reason (`SELF_CHECK_SKIPPED` now says why; finalize marks only that option).
- **A render that fails twice is handed to the other program.** LibreOffice
  failing twice -> PowerPoint takes over for that render; PowerPoint failing
  twice -> LibreOffice, when installed. Both failing -> one error with both
  reasons.
- **Hidden slides no longer shift the pictures.** A PDF leaves hidden slides
  out, so `slide_05.png` showed slide 6; renders now include them, so
  `slide_NN` is always slide NN (the hygiene pass still reports them).
- **PowerPoint's own opens-cleanly check before a deck is done.**
  `compile_picks.py` (and `--splice-into`) opens the saved deck in
  PowerPoint, read-only and without a window, before it replaces the previous
  deck: a file PowerPoint refuses or asks to repair (with alerts off, the
  repair question comes back as an error), or opens with a different slide
  count, is refused (exit 6, kept as `.REJECTED.pptx`), so it is never
  recorded as compiled and `check_done.py` never calls it done. COMPILED.md
  gains "Opens in PowerPoint". On a computer without PowerPoint it says the
  check did not run. (Measured: PowerPoint refuses an incomplete `<p:style>`;
  it opens a deck with duplicate shape ids, which the offline check still
  refuses.) `ppt_safe.check_opens` runs the open on its own thread with a
  timeout, so a stuck PowerPoint cannot hang compile.
- **The user is told before PowerPoint renders.** Before a step that renders
  through PowerPoint (stages 6, 8, 9, 11 and template registration; slide-qc),
  Claude says in one line that PowerPoint may pause for a few seconds and that
  editing in PowerPoint meanwhile slows the build. The scripts print the same
  line once per command (child processes stay quiet).
- **Setup.** `doctor.py`: PowerPoint is the renderer row on Windows (tested
  with a real render); LibreOffice is optional there (backup) and required on
  a Mac. README's install section and the install guide (still 2 pages) say
  LibreOffice is needed on a Mac and optional on Windows.
- **PowerPoint export height follows the deck's slide size** (it assumed
  16:9).
- Test switches: `SLIDE_LAB_NO_POWERPOINT=1` (act as if PowerPoint were not
  installed, e.g. a Mac) beside `SLIDE_LAB_NO_LIBREOFFICE=1`.
- New smokes: `run_one_deck_render_smoke.py` (page-to-slide mapping on both
  renderers, one render per template, a failing slide reported alone, real
  PowerPoint refusing one slide), `run_renderer_default_smoke.py` (the
  default and overrides, PowerPoint with LibreOffice present and missing, the
  twice-failed hand-over both ways, the notice once),
  `run_powerpoint_opens_smoke.py` (the opens-cleanly check),
  `run_powerpoint_e2e_smoke.py` (a fictional build end to end on PowerPoint
  only; `--time N` times an N-slide build on both renderers). Each records the
  user's open presentations before and after and requires them unchanged.
- **Measured.** A 20-slide fictional build end to end: PowerPoint 53.8 s
  (finalize's render 5.3 s, compile 6.5 s, slide-qc render 2.9 s) vs
  LibreOffice 82.5 s (18.1 s, 15.9 s, 15.2 s). Go/no-go replay of the
  converter on 101 past options, self-check on LibreOffice vs PowerPoint:
  open failures 0 / 0, lost text 0 / 0, same lines 99.71% / 99.85%, needs the
  agent 17.8% / 35.6% (bar: at most 15%, missed on both). Through PowerPoint
  the self-check fires mostly on `position` (64 elements vs 2): large
  numerals and hero text sit about 5 px lower in PowerPoint than the
  converter places them for, plus gradient and chart-bar colors. These are
  real differences in what PowerPoint shows, but the limits were set on
  LibreOffice; recalibrating them (or the converter's text placement) for
  PowerPoint is an open decision. (Resolved the same day: see "The sketch
  converter places text for PowerPoint" below; the self-check now runs on
  the default renderer.)

### The sketch converter places text for PowerPoint (owner's decision)

- **What was wrong, measured** (fictional test slides: 9 fonts, 9 to 72 pt,
  line spacing 0.69 to 2.3 x the size, both programs, read from the glyph
  origins in each program's PDF and checked against the pixels):
  - **Most of the "5 px lower" was the check, not the slide.** The
    self-check found each letter from the letter box in the PDF. LibreOffice
    writes the font's Windows metrics there (as Chrome uses), PowerPoint its
    typographic ones (Arial: 0.73 em above the baseline, not 0.91), so in a
    PowerPoint PDF the box's middle sat 0.09 em lower with the letters in the
    same place: 6 px on a 72 px numeral. In pixels, large numerals with tight
    spacing were within 1 to 3 px.
  - **Real differences in where PowerPoint sets text.** PowerPoint rounds
    exact line spacing to whole points (the pitch too: 13.65 pt is set at
    14). With spacing L above its "single" line (L > floor(1.2 x size) pt)
    the first baseline is 0.75 L below the box top, for every font; at or
    below it, max(0.75 L, L - D), D = 1.2 x size x descent / (ascent +
    descent). LibreOffice puts it at L - 0.2 x size for every font and does
    not round. The converter had been placing text by LibreOffice's rule, so
    in PowerPoint text with loose spacing sat high: 16 px too high for 96 px
    type at line-height 1.5, 3 to 5 px for body text.
  - **`line-height: normal` was taken as 1.15 em for every font**; Chrome
    uses the font's own (Segoe UI 1.33, Calibri 1.22).
- **What changed** (`scripts/translate_html.py`): line spacing is written in
  whole points, so both programs set the same pitch; every text box's top is
  set from PowerPoint's rule (`ppt_first_baseline`, `place_first_line`) and
  Chrome's first baseline (the first line's box top plus the font's ascent
  share); a one-line text box gets spacing 0.8 x its size, the one spacing
  at which PowerPoint and LibreOffice put the baseline in the same place
  (checked: no letter is cut off); `normal` uses the font's own line height
  (`vertical_metrics`); SVG text uses the same placement. On a LibreOffice
  render, text on several lines sits lower than in PowerPoint by
  LibreOffice's own rule (0.25 L - 0.2 x size: about 3 px for 16 px body
  text at 1.5, more for large loose headings); each text op records it
  (`_dy_lo`) and the self-check expects it there.
- **Gradients** (`twins/html_emit.py`): PowerPoint blends gradient stops in
  linear light, Chrome and LibreOffice in sRGB, so a white-to-navy gradient
  was up to ~50 RGB levels off in the middle (mean 31 per pixel). The
  converter now adds in-between stops computed the browser's way (at most 10
  stops, PowerPoint's own limit): mean error per pixel on 8 test gradients
  0.3 to 2.6 in PowerPoint (was 0.6 to 31), LibreOffice unchanged (0.2 to
  0.8). A gradient with transparent stops was also faded twice (its middle
  stop's transparency applied to every stop, so a 90% to 10% navy fade came
  out nearly white in both programs); fixed.
- **The self-check** (`scripts/translate_alarm.py`): text is located by its
  baseline and size from the PDF (the same in both programs) with Chrome's
  letter box built around it; the program that drew each page is read from
  the PDF (the other one takes over when the first fails twice). On a
  PowerPoint render, the pixel rows a filled shape's fractional edge only
  partly covers are left out of its color and ink checks: PowerPoint draws
  every straight edge on a whole pixel and rounds where it likes (a 7.1 px
  bar drew 8 px tall), which moved a thin chart bar's average color by up to
  29 levels with the bar drawn right. Shapes with an outline and table cells
  keep those rows. The limits are unchanged. (Rounding the shapes' edges to
  whole pixels instead was tried and dropped: it made LibreOffice worse on
  half-pixel edges.)
- **The self-check renders with the default renderer** (PowerPoint on
  Windows); `run_translate_smoke.py` and `run_native_tables_lists_smoke.py`
  no longer pin it to LibreOffice. `run_translate_smoke.py` gains a
  placement check on every program installed (6 texts in 5 fonts within
  1.5 px of where expected, the transparent gradient's alpha).
- **The go/no-go replay scores every option.** Work folders were named after
  the folder given plus `slide_NN/option_X`, so given a client folder every
  session's `slide_01/option_A` shared one folder and only 101 of 263
  options were scored. They are now named after the option's whole path
  (session folder included). `translate_gonogo.py --engine` defaults to the
  default renderer; `translate_alarm_seeded.py` gains `--engine`.
- **Measured, 263 past options** (`translate_replay.py` +
  `translate_gonogo.py`; bars: 0 open failures, no lost text, at least 98%
  same lines, at most 15% need the agent):

  | | LibreOffice before | LibreOffice after | PowerPoint before | PowerPoint after |
  |---|---|---|---|---|
  | needs the agent | 35 (13.31%) | 36 (13.69%) | 82 (31.18%) | 33 (12.55%) |
  | elements flagged | 159 | 161 | 298 | 151 |
  | of which position | 10 | 10 | 112 | 11 |
  | of which color | 124 | 126 | 154 | 120 |
  | open failures | 0 | 0 | 0 | 0 |
  | same lines | 99.67% | 99.67% | 99.70% | 99.70% |
  | options with lost text | 1 | 1 | 1 | 1 |

  The one option with lost text is unchanged (87 characters in an element
  left to the agent, known since 2026-10-08). Planted defects
  (`translate_alarm_seeded.py`, 526 planted, 467 visible): caught 96.8% on
  PowerPoint and 97.2% on LibreOffice leaving out bold flipped (bar 95%),
  with the limits unchanged.
- **Open:** LibreOffice pictures (the Mac renderer and the backup) now show
  text on several lines a little lower than the sketch (about 3 px for body
  text, up to 16 px for 96 px type at line-height 1.5), because the text is
  placed for PowerPoint; one-line text is unchanged. PowerPoint for Mac was
  not measured.

## 2026-10-08: native tables and PowerPoint-only rendering

### Native tables and one-box lists (sketch path)

- **An HTML table becomes a real PowerPoint table.** The converter
  (`scripts/translate_html.py`) used to turn a `<table>` into a rectangle and
  a text box per cell. Now a `<table>` (or a `<div>` grid marked
  `data-native="table"`) becomes ONE native table (`twins/html_emit.py`,
  plan op `"table"`): column widths and row heights as designed, merged
  cells (`colspan`/`rowspan`), every cell's fill (a highlighted row
  included), every border per edge (CSS's collapsed-border rules: widest
  wins, cell over row over group over table), cell margins that put each
  letter where the sketch had it, and styled runs (size, bold, color,
  alignment). The table carries no theme banding ("No Style, No Grid"). A
  pill or badge inside a cell stays its own shape on top of the table. A
  table that can't be matched (rounded corners, spaced-apart cells, pieces
  of text side by side in a cell) stays separate shapes as before, with a
  `TABLE_KEPT_AS_SHAPES` warning naming why.
- **A bullet list becomes one text box with real bullets.** A `<ul>`/`<ol>`
  (or a column marked `data-native="list"`) becomes ONE text box: one
  paragraph per item, real bullets or numbers (`buChar` / `buAutoNum`) in
  the marker's color and size, nested items as paragraph levels, the hanging
  indent and the space between items from the CSS, bold lead-ins kept.
  Custom markers (a small square or dot drawn with `li::before`, a glyph,
  "1.") become the bullet character in their color; markers that can't be
  (an icon, a boxed number) are drawn as shapes beside the one text box.
- **Checked like everything else, never at the cost of text.** The
  self-check (`translate_alarm.py`) judges a native table cell by cell (each
  cell's text and area) and a list by its text and each bullet's spot. One
  that renders differently from the sketch steps down and that slide is
  rendered again: table -> separate shapes (`TABLE_NOT_NATIVE`); list ->
  one box with marker shapes (`LIST_MARKERS_AS_SHAPES`) -> one box per item
  (`LIST_NOT_SINGLE_BOX`). Every version holds all the text. The report's
  counts gain `native_tables` and `single_box_lists`.
- **Type-scale check reads table text** (`type_scale.py`); it used to skip
  graphic frames.
- Designer and translator guidance: `prompt.md` and
  `reference/sketch-html-spec.md` § 6b ("draw tables as an HTML table,
  header row in `<thead>`"; "write lists as `<ul>`/`<ol>`"), and the
  translator agent's instructions (draw native tables and one-box lists in
  full translations; draw only the listed element in fallback mode).
- Test: `tests/run_native_tables_lists_smoke.py` (a fictional table slide:
  header row, 6 rows, a highlighted row, a merged cell, right-aligned
  numbers; a fictional 5-item list with a nested item and bold lead-ins plus
  a square-marker list). One native table, one text box per list, opens
  cleanly, every character kept, renders at least as close to the sketch as
  the old shapes in LibreOffice (mean pixel difference table 2.55 vs 3.33,
  lists 11.08 vs 12.02 of 255) and in PowerPoint (5.10 vs 6.41, 13.71 vs
  14.57), planted defects step down with warnings, no text lost.
- Go/no-go replay (263 past translated options, `tests/translate_replay.py`
  + `tests/translate_gonogo.py`, which now runs the converter's own
  self-check including the step-downs and counts table cells as text):
  open failures 0 -> 0; options with lost text 1 -> 1 (the same 87
  characters in an element left to the agent, unchanged); options needing
  the agent 14.07% -> 13.31%; same lines 99.67% -> 99.67%; mid-word breaks
  1 -> 1. 6 options now carry a native table and 7 options carry 19
  one-box lists; 1 table and 1 list stepped down by the self-check.
- Known and unchanged: a list that steps all the way down still draws a
  "• " in front of each item box, which shifts its text right; the
  self-check hands those items to the agent, as before.

### Rendering without LibreOffice (Windows, PowerPoint)

- **One safe way to drive PowerPoint** (`slide-qc/scripts/ppt_safe.py`),
  used by every PowerPoint render: attach (start it if needed), open OUR
  file read-only without a window, export, close only that file, and quit
  PowerPoint only if it was not running before AND nothing is open in it
  afterwards. This fixes the race where the user opened PowerPoint while a
  render ran and Slide Lab then quit it. Renders are serial (one lock shared
  by every Slide Lab process) and never touch, save or close the user's
  presentations.
- **The converter's self-check works without LibreOffice.**
  `translate_alarm.render_full` now picks LibreOffice, else PowerPoint
  (`engine="auto"`); it used to call `soffice` directly, so the check was
  skipped. `selfcheck_render.py` (the translator agent's check render) no
  longer refuses without LibreOffice.
- **slide-qc's PowerPoint pass works while PowerPoint is open.**
  `render_slides.py --engine ppt` and `export_slides.py` used to refuse (or
  start their own PowerPoint and quit it); both now use the safe path.
  `slide-qc/SKILL.md` updated (it said to ask the user to close PowerPoint).
- **`SLIDE_LAB_NO_LIBREOFFICE=1`** makes Slide Lab act as if LibreOffice
  were not installed (tests, or a broken LibreOffice).
- **Finalize: a sparse slide drawn by PowerPoint is not a failed render.**
  PowerPoint compresses a mostly empty slide under the 12 KB "blank render"
  floor, which blocked every slide of a fictional build; a small picture
  that shows content now passes (`finalize_deck.py`).
- **doctor.py** lists LibreOffice as optional on Windows when PowerPoint can
  be driven, with a note that renders then run one at a time and are slower.
  README install table and the install guide say the same (guide still 2
  pages).
- Tests: `tests/run_powerpoint_only_smoke.py` (the quit rule with a stand-in
  PowerPoint, including the user opening a deck mid-render; then, with
  LibreOffice turned off and the user's PowerPoint open: slide-qc render,
  `--engine ppt`, `export_slides.py`, the converter's self-check and
  `selfcheck_render.py`, recording the open presentations before and after:
  unchanged, PowerPoint still running). `run_pipeline_e2e_smoke.py` (finalize,
  picks, converter, compile) and `run_registration_selftest_smoke.py` pass
  with `SLIDE_LAB_NO_LIBREOFFICE=1`, the user's 4 open presentations unchanged.
- Timing per slide on this computer (4-slide fictional deck, one process
  per render, PowerPoint already running): PowerPoint 0.27 s, LibreOffice
  0.96 s. PowerPoint is faster per file when it is already open, but renders
  never run in parallel; LibreOffice's parallel renders are faster for a
  whole build. A cold PowerPoint start adds several seconds.

## 2026-10-08: session-report fixes, batch 3

### Brief, icons and variety

- **Deck-wide rules reach every designer, under any common heading.** Prep
  read only "## Deck-level design notes", so a brief whose rules sat under
  "## Section content rules (binding on every page)" sent every designer
  "(no deck-level design notes)". `build_deck.py` now also reads "Deck rules",
  "Deck-wide content rules", "Design rules", any heading with "design notes"
  or "(binding on every page)", and joins every such section. **Any other
  `##` section and any bold slide field prep does not read is now a
  `WARNING (brief):` line** in prep's output (repeated in its summary),
  naming it, instead of being dropped silently. Test:
  `tests/run_brief_fields_smoke.py`.
- **Per-page Source line and Section tag reach the designer.** New brief
  fields `**Source:**` and `**Section tag:**` (documented in
  storyline-helper's brief format) go into `_prompt.md` § 1 (next to the
  footer rule: the source goes word for word in the footer / Source slot),
  `_context.md`, and `_meta.json` (`source`, `section_tag`) so the finishing
  step can fill the template's Source slot. The tag is text only for now (a
  fixed-style drawn slot is planned). The review card flags a sketch whose
  brief gives a source but which has no footer element
  (`SOURCE_LINE_MISSING`). Same test.
- **Library icons end to end.** `scripts/icon_svg.py --build` converts every
  icon's DrawingML into a small SVG once (`icons/svg/`, 1,138 files, about
  2 MB; two icons have no drawable picture). `render_html.py` draws
  `<i data-icon-name>` and `<img src="icons/x.svg">` from them in the
  element's color (or `data-icon-color`), so the review page no longer shows
  blank gaps. `translate_html.py` turns each icon into an `icon` step and
  `twins/html_emit.py` inserts the real vector icon (`icon_helper.insert_icon`)
  at the same box (aspect kept) and color; it used to drop `<i>` icons
  without a word. An unknown name gets a labeled placeholder on the sketch and
  the slide, an `ICON_UNKNOWN` warning on the render, the translation report
  and the review card, never a silent gap. `insert_icon` now gives inserted
  shapes fresh ids (the library XML carried its source deck's ids) and names
  the group `icon-<name>`. Test: `tests/run_icons_smoke.py`.
- **A checked icon list.** About half of the library's names do not match
  their pictures. `icons/checked-icons.json` lists 48 names whose pictures
  were rendered and checked by eye, each with what it `shows`; designers use
  only those (an unchecked library name still draws, with an advisory). The
  worker prompt's "icon built from shapes, no image files" rule now points at
  the library; `icons/README.md` and the design guide no longer describe
  `compass` as a lighthouse or use the nonexistent `check-circle`.
- **Sameness warning on the review page.** Each sketch declares its visual
  form (`data-visual-form` on `.slide-canvas`: cards, table, chart, flow,
  ...). REVIEW.html shows the form count across the deck and a "Many pages
  look alike" warning when one form is on at least half the pages or on three
  neighbors in a row; untagged sketches are listed as unknown. The old check
  read only `option_X.py` headers, so it never ran on sketch decks. The stale
  "you see the patterns picked for the previous two slides" text is gone from
  the worker prompt and agent. Test: `tests/run_visual_form_smoke.py`.
- **`translate_html.py --emit <dir>` creates the folder** instead of crashing
  on a manual run. Covered in `tests/run_icons_smoke.py`.
- **Designer and translator instructions follow the fonts and chrome
  changes below.** Worker (`agents/slide-builder-worker.md`, `prompt.md`): no
  `@font-face`, footnotes as `footnote-1`, `footnote-2` ..., the source in the
  footer field, room left above the source line. Translator: the takeaway,
  footnotes and source are named `subtitle`, `footnote-N`, `source` for
  `twins/chrome_rules.py`; box growth happens after the self-check, into empty
  space only. A design that painted its own picture of a library icon
  (background image) now shows the library icon instead, so sketch and slide
  agree. Installed agent copies updated (md5 checked).

### Fonts, converter and chrome

- **The brand font's files are chosen from the fonts' own data.** Registration
  used to guess the font file from the family's name; one family ships its
  narrow ("condensed") face as the bare `<Family>.ttf`, so that face was
  bundled and every sketch and title-fit check was drawn about a quarter
  narrower than the finished slide. `register_template.py` now reads each
  installed font's name table (`_chrome_schema.pick_family_faces`: family,
  style, weight, width), picks the heading family's regular face (upright,
  normal width, weight nearest 400) and its bold face, plus the body family's
  regular face, bundles them into the sidecar and records them in `brand.yml`
  (`title_font_ttf_path`, new `title_font_bold_ttf_path`,
  `body_font_ttf_path`). It prints the face chosen and warns when only a
  narrow or wide version is installed. `brand.yml` also records the theme's
  own face names (`theme_heading_face`, `theme_body_face`), and registration
  warns when heading and body are one family with a bold heading face.
  `bold_ttf_for` finds the bold face by name table (the bundled one first).
  Title-fit measurement (brief check, finalize, the sample slide) uses the
  bold face when the title style is bold or the theme's heading face is bold;
  the brief check also resolves the bundled file names it used to pass as
  bare names. Templates registered earlier keep their bundled file until they
  are registered again. Test: `tests/run_font_pick_smoke.py`.
- **A design cannot swap an installed font for a file.** A designer pointed
  the installed brand family at a copied file holding its narrow face, so the
  review picture and the conversion were narrower than the finished slide.
  The rendering browser (`scripts/_browser.py`, used by the review render and
  the converter) now removes any `@font-face` rule that points an installed
  font at a file, inline or in a linked stylesheet, before anything is drawn
  or measured, prints a warning, and the conversion records
  `FONT_FACE_REMOVED`. The sketch spec bans `@font-face` outright. The
  `RENDER_FONT_RATIO` warning no longer blames the check's renderer or says
  "not a defect": with the font installed it says the design was drawn in a
  different version of the font and the finished text runs N% wider (a design
  issue to check for overflow); with the font missing it says the check used
  a stand-in and text size was not judged. Test:
  `tests/run_font_face_rule_smoke.py`.
- **Box growth only into empty space, after the self-check** (owner's
  decision). To keep text off a filled box's edge the converter grew every
  such box a few px without looking below it, and before the self-check:
  thin stacked boxes grew into each other and nearly every one went to the
  agent (21 elements on one slide). `_apply_clearance` now runs after the
  self-check (like the takeaway snap), grows a box only into free space,
  keeps 2 px (`CLEARANCE_GAP_PX`) to the next shape, line, text or
  agent-drawn element, and leaves a box with no room at its design size
  (`boxes_kept_no_room` in the report). Test: `tests/run_box_growth_smoke.py`
  (a made-up stack of thin solid and dashed boxes: 0 elements to the agent,
  no overlaps, a box with room still grows).
- **Body text stays regular when heading and body are one family.** With the
  theme's heading face being that family's bold face, both names read as the
  same family, and the theme pass bound every body run to the heading font,
  so body text came out bold on every slide. Text in a name that is both the
  heading and the body font now binds to the body font (`client_theme.py`
  `_replace_font`). Test: `tests/run_body_font_binding_smoke.py`.
- **The template's sample text never ships.** A layout footer cloned with its
  bracketed sample line (`<Customize with ...>`) appeared on every slide when
  the design gave no footer text. Finalize (and the registration sample
  slide) now clears whole sample lines (angle-bracket lines, "Click to add" /
  "Click to edit") from inherited placeholders, keeping real text
  (`twins/composer.py` `clear_template_sample_text`), and
  `slide-qc/scripts/check_pptx_hygiene.py` flags any such line left on a
  slide as Critical (`template-sample-text`). Test:
  `tests/run_sample_text_smoke.py`.
- **Pictures and charts survive finalize and assembly.** Both copy steps
  copied shapes without their files: finalize re-attached top-level pictures
  only (losing crops), compile nothing, so a page with a photo, a grouped
  photo, a logo or a native chart failed the integrity check and compile
  refused the whole deck with a misleading message. Both now use
  `twins/composer.py` `copy_shape_with_parts`, which carries every related
  part (images, charts with their workbooks and styles, media, external
  links) under fresh ids, copies a part used twice once, and drops links to
  other slides cleanly. Test: `tests/run_picture_graft_smoke.py` (through
  prep, finalize, final check and compile).
- **The takeaway, footnotes and source line sit in one place on every slide**
  (owner's rule). New `twins/chrome_rules.py` `normalize_chrome`, run per
  slide at finalize on every path and on the registration sample slide: the
  takeaway goes directly under the title (in the template's takeaway slot,
  else 8 px below the title box) at the title's text left edge, in the
  template's own Subtitle-slot size (`template_takeaway_pt`) else 16 pt, not
  bold, in the template's main text color, the same on every slide; the
  source line goes to the template's source position (registered Source
  slot, else its footer slot, else the standard source line) at the title's
  text left edge in 9 pt, also where the template's footer box is centered;
  footnotes stack upward directly above it, same edge, 9 pt. Roles come from
  the template's fields and from shape names (`subtitle*`, `takeaway*`,
  `source*`, `footnote*`); covers and section dividers keep their own lines.
  slide-qc's visual pass flags a slide where one differs. Test:
  `tests/run_chrome_rules_smoke.py` (a made-up deck with footnotes mid-page
  and sources at different x and sizes comes out identical on every slide,
  and the sample slide matches). Updated to the new rule:
  `tests/run_source_line_fallback_smoke.py` (the drawn source line now starts
  at the title's text edge) and `tests/run_registration_selftest_smoke.py`
  (the takeaway spans the title's text width, not its box width).
- **A failed LibreOffice render is retried once, and its error is kept.**
  `slide-qc/scripts/render_slides.py` retries a render that exits non-zero
  or writes no PDF once, with a fresh profile and from a local copy (always
  from a local copy for a deck in a OneDrive folder); renders still run in
  parallel. When both tries fail the error carries the full output of both.
  The converter's self-check render retries the slides that wrote no PDF.
  finalize prints the whole error instead of its first 50 characters. Test:
  `tests/run_render_retry_smoke.py`.

## 2026-10-06: session-report fixes, batch 2

### Approvals and picks

- **Picks and "build it" typed in chat count, with the page open** (owner's
  decisions D1 and D2). `record_picks.py --approved-in-chat "<the user's
  words>" --picks "1A 2C"` records picks typed in chat, and
  `compile_picks.py --approved-in-chat "<words>"` takes the place of
  `--final-token`. Each is accepted only when its page (REVIEW.html,
  FINAL-CHECK.html) was opened with `build_review.py --open` for the current
  files: `build_review.py` now records the opening, bound to the page's token
  and to each slide's option-file stamp (review) or the finished files'
  digests (final check). Refused before the page was opened, after a rebuild
  or finalize, when a file changed since, and when a picked letter is not in
  the user's words. The words are recorded verbatim with what they were bound
  to, and `check_done.py` lists them at delivery under `chat approvals`, not
  as gates passed over (a QC fix approved in chat is listed there too). The
  pasted lines work as before. Test: `tests/run_chat_approval_smoke.py`.
- **Keep some options of a slide.** A pick may name several letters,
  `Picks: 1BC 2A (check ...)` (canonical `slide_01=BC;slide_02=A`), recorded as
  the user's choice and compiled as a labeled all-options deck of exactly the
  kept options. Before, "B and C, not A" meant moving A's files aside and
  finalizing with `--allow-missing`, which logged an override on every run.
  REVIEW.html's "All options in one deck" now shows a **Kept in the
  all-options deck** switch on every option (first click), and its message
  uses the multi-letter form with the check code. An identical override is
  now logged once, with a count. Test: `tests/run_keep_options_smoke.py`
  (the page switch is driven through Playwright).
- **QC fixes on slides with several kept options.** `apply_qc_fix.py --slides
  1B` rebuilds only the named option(s) of a slide that keeps several (B
  converted again, C left byte-identical and still in the deck), keeps the
  slide's list and the all-options flag, and compiles the labeled deck. A
  plain slide number on such a slide, or a letter the user did not keep, is
  refused. It still needs a first compile. The dead "all-options" guard is
  gone. Test: case 7 in `tests/run_qc_fix_smoke.py`.
- **Finalize names pending work and says plainly when it refused.** Options
  converted before any pick and waiting on the translator agent are no longer
  counted as "nobody has picked yet" (which ended in "nothing to do", exit 0):
  finalize exits 11 and names them ("slide 1 option B, slide 1 option C") with
  the next step on the normal output. Sketches simply waiting for the user's
  picks get a next-step line instead of "nothing to do". Every refusal or
  stop ends with one `REFUSED (exit N)` line on the normal output, saying
  whether anything was rebuilt. Test: `tests/run_finalize_pending_smoke.py`.

### Templates and designs
- A template's named Source slot that starts indented is moved to the title's
  left edge (right edge, font and size kept), so the source line lines up with
  the footnote (owner's decision, 2026-10-07). Standard footer slots are left
  as the template places them.

- **Template setup learns text slots named Subtitle and Source.** Many
  templates make the takeaway line and the source line ordinary text (BODY)
  placeholders and say what they are only in the name. `register_template.py`
  now records a BODY placeholder named `Subtitle` / `Subheading` / `Takeaway`
  that starts just under the title (within 80 px of its bottom) as the
  takeaway slot (`subtitle_placeholder_idx`), and one named `Source` /
  `Sources` / `Footnote` in the bottom 40% of the page as the new
  `source_placeholder_idx`. PowerPoint's own SUBTITLE / FOOTER types still
  win; a "Takeaway" box at the foot of the page is not taken for the line
  under the title. The body starts 12 px below a takeaway slot and ends above
  a source slot. The composer fills the source slot by its idx
  (`_populate_layout_placeholders(..., footer_idx=)`), and the registration
  self-test writes both lines into the slots and fails if either misses. Older
  chrome.yml files load unchanged (new fields default to empty) and behave as
  before until the template is registered again.
- **PDF pages are read for their figures.** When the pinned source page is a
  PDF with a text layer, `source_ledger.py build` lists each line that
  carries a figure as a row to resolve (`bind_from_brief` / `keep_source` /
  `replace_with`), and compile waits for them, as for a PowerPoint page (owner
  decision). Pictures on the page go to the vision pass. A scanned PDF page or
  a picture is still "checked by eye only".
- **Sketches are drawn on the template's real background.** Registration
  records each layout's own background (its own `<p:bg>`, else the master's;
  `background_hex`, `background_kind`) and the left and right edges of its
  text area (`body_left_px`, `body_right_px`); `brand.css`'s canvas is the
  default content layout's background instead of a fixed white. Each
  designer's `_context.md` carries `--slide-canvas-bg`, `--body-left` and
  `--body-right` for its slide's layout, read from the template itself when
  the registration predates these fields (scripts/_template_bg.py), so no
  re-registration is needed. `translate_html.py` leaves a canvas of that color
  to the template instead of painting a full-slide rectangle over the
  master's artwork (its self-check gives the check slide the same color, so
  it still compares like with like), and warns `PALE_FILL_ON_BACKGROUND` when
  a large panel is within a few shades of what is behind it, or was designed
  visible on white in exactly the template's color (a fill in exactly the
  color the designer saw behind it is deliberate and not flagged). A loose HTML
  file with no template (the replay harness) converts exactly as before.
- **Arrowheads that run into boxes are flagged.** New `scripts/arrow_ends.py`:
  every arrowhead must stop at least 6 px clear of any box (a panel behind the
  whole arrow does not count). `translate_html.py` checks the design's SVG
  arrows (arrow markers, curved ones included) against its boxes, and the
  translator agent's self-check checks the connectors and freeforms it drew;
  hits are `MAJOR_ARROW_END_AT_BOX` warnings in the translation report, which
  the review page shows. prompt.md and the worker / translator instructions
  now say: arrows end 8 px short of the box edge, and boxes on a cycle diagram
  are at least 60 px apart.
- **Each option's self-check has its own picture.** New
  `scripts/selfcheck_render.py` renders one option's drawn slide into a
  folder of its own (one per option, in the slide folder's render scratch
  area; LibreOffice only, never PowerPoint) and writes
  `option_X_native.png`, then runs the arrow check. The
  translator agent uses it instead of rendering into the slide folder and
  renaming `slide_01.png`, which let options B and C of one slide be checked
  against one shared picture.
- Fixed: `tests/run_source_line_fallback_smoke.py` read the fixture's
  chrome.yml from an old flat path that only exists on machines that
  registered the fixture long ago; it failed on a fresh clone.
- Tests: run_named_slots_smoke, run_pdf_ledger_rows_smoke,
  run_template_background_smoke, run_arrow_ends_smoke,
  run_selfcheck_folder_smoke.
- **The build fills the Source slot too.** finalize's body-canonical
  finishing step now passes the layout's `source_placeholder_idx` to the
  composer, so a sketch's source line lands in the template's own Source slot
  (matched by idx first, a FOOTER placeholder second) instead of the fallback
  text box with a "no footer slot" warning. Test: case 6 in
  `tests/run_named_slots_smoke.py`.

## 2026-10-06: session-report fixes, batch 1

From a session report, checked by three validators and an adjudicator. These
are the six fixes for silent damage and dead ends.

- **Option labels pass the text-size check.** The 9 pt "Option B" label
  `compile_picks.py --badge` stamps on an all-options deck (shape
  `chrome-option-badge`) is Slide Lab's own review labeling; `type_scale.py`
  now skips it (not under the floor, not a 4th size), so a labeled
  all-options deck no longer fails slide-qc on its own label. Exact names
  only: a designer's shape named `chrome-anything` is still checked.
- **Bold is kept.** `translate_html.py` writes weight 600 and up as the base
  font with bold on (it used to name the heavy face, e.g. Arial Black, with
  bold off), and draws 600+ at 700 before measuring, so the self-check
  compares against the face that ships. The theme font swap
  (`twins/client_theme.py`) also turns bold on when it replaces a heavy face
  name (Black, ExtraBold, Bold, Semibold, Heavy); Medium and Light stay
  regular. Before, weight 800 and Semibold text shipped regular, in
  PowerPoint too.
- **The takeaway lines up with the title.** On a layout with no subtitle slot
  the takeaway is still drawn as a shape named `subtitle` (the documented
  rule), but its left edge and width now match the title's text (title box
  plus its inner margin); its height position stays the design's. It used to
  keep the sketch's guessed x and sat indented.
- **QC fixes and redesigns no longer loop.** `apply_qc_fix.py` and
  `redesign_round.py finish` convert a sketch only when its design changed
  since the last conversion (the translation report now records the design's
  fingerprint). A slide the translator agent finished is kept as is. Before,
  every run converted it again, erased the agent's drawing and exited 3 for
  ever.
- **A PDF or picture can be the pinned source page.** `source_ledger.py build
  --deck page.pdf` (or .png, .jpg) writes an honest ledger: no rows, the whole
  page recorded as checked by eye only, so compile proceeds and slide-qc's
  vision pass covers it. `check_done.py` says so at delivery. Before, `build`
  crashed and a pinned PDF could never compile. Other file types are refused
  with "save it as a PDF".
- **Source lines are no longer dropped silently.** When a slide has a source
  line and its layout has no footer slot (the template's source slot is an
  ordinary text box, or there is none), finalize draws it as a text box at
  the template's source position and prints a WARN line.
- Tests: run_type_scale_smoke [7]-[8], run_translate_smoke (weights),
  run_title_subtitle_loud_fail_smoke P6, run_qc_fix_smoke [5]-[6],
  run_redesign_round_smoke [6], run_source_ledger_smoke [7]-[8], and the new
  run_source_line_fallback_smoke.

## 2026-10-06: guide in pages, storyline and slide-rules reference

- Slide-Lab-Tutorial.html is now 25 pages in 6 tabs (Start here, Your first
  deck with one page per step, Storylines, Slide rules, Reference, Help), still
  one emailed file. "Show the whole guide on one page" keeps Ctrl+F and
  printing; every old link still works; without scripts all pages show.
- New Storylines pages (how Claude coaches, deck types and structures, page
  order and page types, headlines and takeaways, what the storyline check
  flags, the Meridian worked example) and Slide rules pages (each rule with
  why, do and don't, and where Slide Lab checks it), sourced from the skills.
- check_tutorial.py also compares the guide's type-scale numbers with
  type_scale.py and its buzzword examples with banned-words.md.
- Meridian slide 8 reworded to what the data supports ("We expect partners to
  lower Indonesia's entry cost; no data yet") and that slide rebuilt.
- Agents never close or kill the user's browser or PowerPoint.

## 2026-10-05: type scale (12 pt body default, 10.5 pt floor)

- Body text is 12 pt by default (12, 14, 16), at most 3 sizes per slide. When
  the content cannot be cut it may drop to 11 or 10.5 pt (an Advisory note),
  never lower (Major). Sources, footnotes and chart text may be smaller, never
  under 9 pt.
  Title, takeaway, template footer and one hero figure are not counted.
- One check, `scripts/type_scale.py`, used by finalize, FINAL-CHECK.html (a
  "Text size" box) and slide-qc (Major: fix it or give a reason). It replaces
  the old 10.5 pt / 8 pt floor in finalize.
- Designer instructions and the sketch spec carry the new scale and ask for
  `chart-`, `source-` and `footnote-` shape names; text that does not fit is
  cut or split, never shrunk. New smoke `tests/run_type_scale_smoke.py`.
- The Meridian example (deck, review page, storyline, tutorial screenshots and
  timings) was rebuilt under the scale, with fact-based titles and takeaways.
- Review pages no longer show the designer's working note ("Worker used your
  reference slide. Body zone ..."); the warning when a designer skipped the
  template's sample slide is in plain words.

## 2026-10-05: full audit (less friction, fact-based content)

From a three-auditor review of download, install, operation and output.

### Content
- Takeaways must state a fact with its number; slogans and "not X, it's Y"
  lines are allowed only on the slide whose job is to break a belief.
  `reference/banned-words.md` is the one list of buzzwords; slide-qc treats
  them as Major.
- `scripts/brief_check.py` measures each title and takeaway in the
  template's own font and box (bold included) and reports what will not fit
  one line; `seal_brief.py` refuses until each row is fixed or accepted with
  a reason.
- `scripts/source_check.py`: FINAL-CHECK.html lists numbers and labels on
  the slides that are not in the brief, and figures written in two units.
- Designers now see the whole deck (main message, audience, every title),
  number only real sequences, and run on Opus.
- Fixed: a brief with "deck notes (optional)" lost its deck notes.

### Fewer stops
- The storyline ends with one message (setup, problems with rewrites,
  "build / save only / changes") and one reply. The template is asked once.
- Review pages open by themselves and copy plain messages
  ("Picks: 1B 2C (check ...)"); `record_picks.py` reads them.
- A redesign with one design (a Replace round or "rebuild slide N") skips the
  second picking page: `scripts/redesign_round.py` (`--keep-previous` for a
  rebuild) goes straight to FINAL-CHECK.html.
- Approved QC fixes compile straight through (`scripts/apply_qc_fix.py`).
- The front door offers 5 plain choices instead of 8.
- GATE3-PREVIEW.html is no longer written.

### Output
- The deck is also saved under its topic ("Southeast Asia Entry.pptx");
  earlier decks move to `_session/old-decks/`.
- Storyline files use plain labels ("Main message", "What the audience
  believes now").

### Tutorial
- Redesigned from tables into 8 numbered steps (your turn vs Claude working
  shown on each step), with reference and help after the steps.
- Works as one emailed file: the install guide, example storyline, review
  page and deck are built in (`docs/tutorial/assemble.py`).
- Review pages keep choices in memory when the browser refuses to save them,
  instead of the buttons failing.

### Install and security
- `doctor.py fix` grants only Slide Lab's own commands and folders, not
  blanket shell access. LibreOffice can be replaced by PowerPoint on Windows.
- One install path in the README; registration asks for a client deck to
  copy the look from every time.
- Published history cleaned of client names, internal notes and the licensed
  reference pack (commit IDs changed). `update.py` spots a replaced history
  and offers a one-time `git reset --keep`; the README covers older installs.
- Bug reports go privately to the maintainer, never to GitHub issues.
  Decision notes and licensed reference packs are no longer published.

## 2026-10-02: install, updates, chat registration

### Fixed
- `requirements.txt` was missing `pydantic`, `playwright` (commented out) and
  `python-docx`, so a by-the-book install crashed on the first registration or
  build. Added them plus `defusedxml`; verified in a clean virtual environment.
- Registration: `commit-cli` now takes `--cover-layout NAME` (written to
  theme.json as `cover_layout`, which SKILL.md asked for but nothing stored)
  and `--reference-slide N`. New smoke `tests/run_commit_cli_smoke.py`.
- `tests/run_sketch_smoke.py` runs with the current Python (was `py -3`
  only, so it failed on Mac).

### Added
- `scripts/_browser.py`: design sketches render with Playwright's Chromium,
  falling back to Microsoft Edge, then Google Chrome, when the Chromium
  download is blocked (it times out on the Accenture network). Edge gave
  identical translator go/no-go results on all 207 replayed options.
- `scripts/doctor.py`: setup check (Python, packages, browser, LibreOffice
  converting a test slide, agent files, settings, local work folder) with a
  plain table; `fix` copies agents, merges permissions into settings.json
  (backup kept) and creates `~/Slide Lab/sessions` + a Desktop shortcut. It
  never installs software.
- `scripts/update.py`: once-a-day update check run by the slide-lab front
  door, which asks before pulling; `after-pull` re-copies agents and says when
  a restart is needed. Replaces the start-up git-pull hook, which
  company-managed Claude Code ignores (`allowManagedHooksOnly`).

### Changed
- Template registration is chat-first: Claude asks for the main, highlight and
  cover colors separately with no pre-picked answer (the automatic guess was
  wrong on 5 of 5 templates), plus the content and cover layouts.
  `register.html` is still written but no longer offered.
- README install rewritten: three programs by hand, one paste-in request to
  Claude, `doctor.py` instead of hand-edited settings, LibreOffice listed as
  required, a "Your first deck" section with timings and the local work
  folder. storyline-helper defaults new session folders to the local drive.

## [Unreleased] — production naming + pipeline completion

### Changed — build paths renamed to production names
- The two build paths are now named for what they do: **sketch** (HTML-first:
  worker writes HTML → translator converts to native python-pptx) and
  **direct** (python-pptx direct, no HTML stage). These replace the internal
  refactor codenames "Pattern B" / "Pattern C" across `settings.json`
  (`default_pattern` values; `enable_pattern_b` → `enable_sketch`),
  `build_deck.py` (`--pattern sketch|direct|auto|legacy`, the classifier, the
  per-slide `pattern` token), `_meta.json` (`pattern` / `pattern_default` /
  `pattern_per_slide` values), `finalize_deck.py` (classifier status
  `pattern_b_translated` → `sketch_translated`; `_check_r4_rules_for_pattern_b`
  → `_check_r4_rules_for_sketch`), `build_review.py` (`render_pattern_b_qc_section`
  → `render_sketch_qc_section`; `.pattern-b-*` REVIEW.html CSS → `.sketch-*`),
  the worker + translator agent prompts (`PATTERN: sketch|direct`), and the
  smoke test (renamed `run_pattern_b_smoke.py` → `run_sketch_smoke.py`).
- **Clean break**: a `_meta.json` written before this rename carries stale
  `"B"`/`"C"` values. These are session-scratch (regenerated every build); the
  validator + a finalize-time guard treat stale values as legacy and ask the
  operator to re-run, rather than mis-routing.
- The `option_A/B/C` per-slide variant filenames are unrelated and unchanged.

### Other completions this cycle
- RFP → slide-builder handoff wired (`mode: rfp` gate bypass + conformant
  proposal-brief format).
- `deck_meta.governing_thought` / `audience` now populate from the brief's
  body headings (were shipping empty).
- Chart data + per-slide steering fields (visual rhythm, mandatory shape,
  forbidden patterns, accent placement) parsed and threaded to the worker prompt.
- storyline-helper: `evidence_type` / `source` micro-fields implemented +
  open-gaps punch list emitted in the dot-dash.
- Mermaid fully retired; client-specific brand guard removed; scar tissue
  (milestone tags, version markers, dated parentheticals) stripped across all skills.

## [Prior] — Pattern B refactor (M1 – M7, 2026-06-16 → 2026-06-17)

### Added — Pattern B HTML-first build path (M1 – M5)
- **M1** (`3fed1ee`): `--pattern {auto,B,C,legacy}` CLI flag on `build_deck.py`; per-slide classifier `_classify_slide_pattern`; `_meta.json` schema-v3 extension with optional Pattern B fields (`pattern_default`, `pattern_per_slide`, `html_render_canvas`, `translator_dispatched`, `translation_reports`, per-slide `pattern` / `artifacts`); shipped `settings.json` with `default_pattern: legacy` + `enable_pattern_b: false` master switch.
- **M2** (`def2a07`): SSIM regression-test harness (`tests/capture_baseline.py` + `tests/regression_check.py`); `scikit-image>=0.21,<1.0` dep.
- **M3** (`eae0a05`): `scripts/render_html.py` Playwright wrapper (headless Chromium → 1280×720 PNG); public color helpers in `twins/client_theme.py` (`hex_to_rgbcolor`, `css_color_to_rgbcolor`, `resolve_css_var`, `wcag_contrast`, public `mix_hex`); `EMU_PER_PX_AT_1280` + `emu_to_px` / `px_to_emu` / `_emu_to_px_dict` in `scripts/_chrome_schema.py`; `write_brand_css()` in `register_template.py` (emits `brand.css` sidecar at registration); WCAG AA contrast warning at register time; `playwright>=1.40,<2.0` dep + INSTALL.md Step 1.5.
- **M4** (`d7e8326`): NEW `agents/slide-builder-translator.md` (~350 lines, per Spec 4); Pattern B branch added to `agents/slide-builder-worker.md`; INSTALL.md Step 7 for translator agent install + verify.
- **M5** (`72aa7d0`): `build_deck.py` emits `PATTERN: B|C` into per-slide `_prompt.md` via `_classify_all_slides()` + `build_placeholders()`; `finalize_deck.py` discovers `option_X_native.py` (translator output), classifies it as `pattern_b_translated`, parses `__template_fields__` header for placeholder population, threads through `_apply_body_canonical_finishing()` with new `template_fields_override` kwarg.
- **M6** (`392ea2d`): R4.1 – R4.8 QC rules in `finalize_deck.py::_check_r4_rules_for_pattern_b()` (3 Critical / 4 Major / 1 Advisory per Spec 6); REVIEW.html surfaces per-zone SSIM + R4 severity chips via `build_review.py::render_pattern_b_qc_section()`; new `slide-qc/VISION_QC_PROTOCOL.md` documents R1 – R8 with severity table.

### Removed — M7 Mermaid retirement (2026-06-17, Decision 6 locked)
- `scripts/render_mermaid.py` — Mermaid CLI wrapper deleted. Pattern B HTML→PNG replaces it for curved-container diagrams.
- `reference/fallback.md` + `reference/fallback-examples/` directory — Mermaid contract docs + worked `.mmd` examples deleted.
- `scripts/finalize_deck.py` functions: `_resolve_mermaid_theme()`, `_render_mermaid_png()`, `_assemble_fallback_pptx()`. `FALLBACK_MERMAID_TOKEN` constant + the `fallback_mermaid` branch of `_classify_option()` + the build_pptx fallback branch removed. `--theme` CLI argument removed. `mermaid_theme` argument removed from `build_pptx()`, `write_result()`, `write_meta_json()` writes, and the dispatch_plan output. `OptionStatus.mmd_path` / `OptionStatus.mermaid_png_path` fields removed.
- `scripts/build_deck.py` functions: `_compute_theme_variables()`, `generate_mermaid_theme()`. The inline brand-theme sanity check that followed Mermaid theme generation was retired with it (brand-color validation now lives at `register_template.py` Phase 3 + M3 WCAG warning).
- `_meta_schema.py::MetaJson.mermaid_theme` made OPTIONAL (default `""`) so existing v3 metas with the field still validate; new writes omit it. No schema version bump.
- `INSTALL.md` Step 2 (Mermaid CLI install + verify). Consolidated verify block (line ~165) no longer checks `mmdc`.
- `agents/slide-builder-worker.md` fallback-trigger Step 7: replaced with Pattern C `SKELETON_REJECTED` route or Pattern B native HTML+SVG authoring.
- `prompt.md`: `{{FALLBACK_MD_PATH}}` and `{{FALLBACK_EXAMPLES_DIR}}` placeholder rows removed; Step 4 "fallback trigger" rewritten for the Pattern B / C split; output contract no longer mentions `# FALLBACK_MERMAID:` token.
- `SKILL.md`: Fallback-path description rewritten — Pattern B is the supersession; Mermaid CLI removed from the INSTALL.md summary.

Stale builds that carry `# FALLBACK_MERMAID:` line-1 markers will now fall through to the `native` classifier and crash at execution. The operator re-builds; no production decks contained Mermaid artifacts at retirement time.

### Resolved — Slide 16 strikethrough (2026-06-17)
A client deck's slide 16 strikethrough defect (forensic entry in private `SLIDE_LAB_FEEDBACK_LOG.md` 2026-06-16) is closed as `resolved-by-pattern-b-superseding`. M4 demonstrated Pattern B rebuilds slide 16 cleanly. The actual root cause was confirmed in PowerPoint: overlapping textbox content from undersized description boxes — a geometry-cascade in the python-pptx layer, not a font-decoration bug. No inline patch to `option_A_native.py` is required because Pattern B replaces the rendering path wholesale.

### Deferred (M7 scope, not flipped)
Production defaults remain `enable_pattern_b: false` + `default_pattern: legacy`. Flipping the master switch requires a separate gating task — Mario validates Pattern B end-to-end on a real (non-test) deck before cutover. See plan at `C:\Users\m.a.peralta\.claude\plans\stop-telling-me-to-indexed-puzzle.md`.

---

## [Unreleased — pre-Pattern B] — v0.1 hardening + taxonomy consolidation (2026-05-26 post-tag)

### Changed — Deck-type taxonomy: 17 → 7 + 1 edge (2026-05-26)

Three-agent committee analysis (Reduction maximalist / Preservation realist / Mechanism check) found the canonical deck-type list in `storyline-helper/SKILL.md` had drifted to 17 types with only 6 unique gate-check mechanisms — half the labels were redundant. Worse, the Mode Check and Step 0.7 Decision-2 tables disagreed on which 16/17 were canonical (e.g., "Facilitation Deck" was in Decision-2 but not in Mode Check). Off-canon types silently bypassed the Step 7 Part 5 deck-type-specific gate check.

The taxonomy now consolidates to 7 + 1 edge:

1. **Recommendation / POV** — absorbs Executive Briefing, Strategic Plan, Investor Pitch, Partnership Proposal.
2. **Business Case** — kept distinct so a future CFO-grade gate (NPV / options compare / sensitivity) has a hook. Currently shares Recommendation's gate; v0.2 sharpens.
3. **Diagnosis** — absorbs Problem Diagnosis + Feasibility Study (verdict = cause-claim).
4. **Operating Review** — absorbs QBR, Status, Board Update, Market & Competitive Analysis (all G3+G4 variance-and-implication).
5. **Capability Pitch** — kept distinct (G5 differentiation; buyer chooses *who*, not *what*).
6. **Workshop Readout** — kept distinct (past-tense decision record).
7. **Workshop Design** — kept distinct per Agent C's pitfall: the label encodes a *routing decision* (gate bypass), not just a gate variant. Folding it into anything else would break the Step 0.7 overlay branch.

**+1 edge — Training / Enablement.** Demoted from primary type to documented sub-route. Edge cases use it; standard consulting work picks one of the 7.

**Files modified:**
- `storyline-helper/SKILL.md` § Mode Check (line ~110) — examples + list now reflect 7+1.
- `storyline-helper/SKILL.md` § Step 0.7 Decision 2 (line ~259) — 17-row table → 7-row table.
- `storyline-helper/SKILL.md` § Step 7 Part 5 (line ~505) — 9-row gate-check table → 7-row.
- `storyline-helper/SKILL.md` § Part 7 + Part 8 — updated absorbed-type references.
- `storyline-helper/SKILL.md` § Brief format spec (line ~778, 785) — "16 types" → "7 canonical + Training edge."
- `storyline-helper/_decisions/v0.2-improvements-queue.md` — Business Case gate sharpening + Workshop Design gate-bypass decision still parked.

Existing briefs with old type names (e.g., `deck_type: Executive Briefing`) continue to work — `slide-builder` treats `deck_type` as free-text metadata, no code key on the string.

---

## [Unreleased] — v0.1 hardening pass (2026-05-26 post-tag)

Behavioral guardrails + Tier 1 install/safety blockers + Tier 2 production-readiness fixes from the v0.1 audit handover (`_decisions/v0.1-audit-handover-2026-05-26.md`) and the follow-up 4-agent regression audit.

### Added

- **`slide-builder/agents/slide-builder-worker.md`** as source-of-truth for the per-slide Stage-2 worker (was orphaned at `~/.claude/agents/slide-builder-simple-worker.md`). INSTALL.md Step 6 documents the copy step.
- **INSTALL Step 6 content-aware verification** — `Select-String -Pattern "option_A.py"` proves the installed worker is the v0.1 contract, not a stale v1 copy.
- **`_contract.py` import-smoke check** — fourth check imports all 14 pipeline modules to surface module-load-time errors at contract test time.
- **`compile_picks.py` timestamped backup** of `final_deck.pptx` on overwrite.
- **`compile_picks.py` save-time error handling** — `PermissionError` / `OSError` surfaces an actionable message ("close PowerPoint") and exits with code 3 instead of a raw traceback.
- **`finalize_deck.stash_raw` loud failure** — Windows file-lock failures during the rename now surface via `st.error` instead of silent return.
- **`clean.py` safety guards** — refuses drive roots, user home, paths under the skill itself, and `--deep` without explicit `--yes-i-really-want-to-wipe-prompts`. Exit codes 3 / 4 / 5.
- **Storyline-helper hard rules** — per-slide handshake required (Step 5); review must be acknowledged before brief saves (Step 9); never ask the user to classify the deck (Mode Check).
- **Slide-builder hard rule** — no auto-accept on template registration; user must respond to `register.html`.

### Changed

- **SKILL.md** — v1/v2 history deferred to a bottom appendix; main flow no longer points new users at `DECISIONS.md` (503 lines) before doing work. Duplicate "Input contract" section deleted. Adjacency attribution fixed (gate-preview + review, not finalize). Mode Check opener hardened against menu-style questions.
- **`prompt.md`, `DECISIONS.md`** — Hardline #3 adjacency attribution corrected at all callers.
- **`prompt.md`, `SKILL.md`, `DECISIONS.md`** — Hardline #4 (brief fidelity) reframed as prompt-time-only with v0.2 enforcement target.
- **`TROUBLESHOOTING.md`** — exit-code tables re-derived from actual `sys.exit()` calls in every script.
- **`twins/composer.py`** — stripped 654 lines of dead v1 chassis-vocabulary code; kept only `_find_blank_layout`, `_strip_layout_placeholders`, `_clear_existing_slides` used by finalize/compile.
- **`convergence-hold-declaration-2026-05-26.md`** — banner enumerates what's now Path D-obsoleted in the body.
- **Cross-skill v1-script references** — `slide-qc/SKILL.md`, `rfp-helper/SKILL.md`, `slide-builder/icons/README.md`, `scripts/icon_helper.py`, `twins/helpers.py` repointed off deleted `build_slide.py` / `extract_icons.py` / `phase-a-rules.md` / `visual-treatment-library.md`.
- **Three anti-pattern WHY.md cross-references** repointed at `reference/anti-patterns.md` / `reference/layouts.md`.

### Removed

- **`QUICKSTART.md`** — content folded into `examples/RUN.md`; was a first-day onboarding speed bump.
- **Stale v1 worker** at `~/.claude/agents/slide-builder-simple-worker.md` (replaced by `slide-builder-worker.md`).

### Added — Phase 10 drift-prevention forcing function (2026-05-26)

- **`scripts/_contract.py` gained three new checks** (now 7 total): `check_install_sentinels` (source/installed content fingerprint match — first sentinel: worker agent must contain `option_A.pptx` output-contract string), `check_doc_file_refs` (every backtick-wrapped markdown ref must resolve; allowlists for runtime artifacts, deleted-by-design, user-memory cross-context, and user-context dir prefixes), `check_type_hints_resolve` (forces `typing.get_type_hints()` past PEP 563 deferral).
- Two new behavioral memories in `~/.claude/projects/.../memory/`: `feedback_existence_vs_content.md` ("done" means user-facing behavior works end-to-end), `feedback_cleanup_chat_cannot_self_declare.md` (cleanup chat marks `claimed-complete-by-cleanup`, only fresh audit chat marks `audit-confirmed`).

### Changed — Phase 10

- **Worker save contract fixed.** Worker agent rewrite (source + installed at `~/.claude/agents/slide-builder-worker.md`) corrected from "saves to `sys.argv[1]`" to the prompt.md-canonical `prs.save(str(Path(__file__).resolve().parent / "option_A.pptx"))`. md5 match verified between source and installed copies. INSTALL Step 6 sentinel grep enforces this going forward.
- **Phantom archive path refs rewritten.** `SKILL.md`, `CHANGELOG.md`, `reference/anti-patterns.md`, `twins/composer.py` no longer claim `slide-builder_archived_2026-05-26/` lives on disk (it doesn't). Refs rewritten as "archived and removed from disk."
- **`project_slide_lab_architecture.md` v1-perspective error fixed.** The "skill is being archived" instruction (written when v1 was active) no longer tells future Claude not to import from the live v0.1 skill.
- **`convergence-hold-declaration-2026-05-26.md`** banner expanded to declare the doc fully superseded; body intentionally retained as forensic audit trail.
- **Three stale anti-pattern WHY.md cross-refs** dropped (`do/single-finding/`, `do/chart-bottom-takeaway/`, etc.) — v1's `do/` corpus never ported to v0.1; refs were dangling.

### Removed — Phase 10

- **Three stale v1 agents** from `~/.claude/agents/`: `slide-builder.md`, `slide-designer.md`, `deck-builder.md`. Only `slide-builder-worker.md` remains.
- **`slide-builder/icons/_audit/`** (254 KB) + **`slide-builder/icons/_backup/`** (736 KB) hangover dirs.
- **`~/.claude/skills/smoke_test.py`** orphan (imported deleted v1 modules; crashed at step 1).

---

## [v0.1] — 2026-05-26

First release after the Path D consolidation (v1 retired, v2 wins). See `_decisions/cleanup-plan-master-2026-05-26.md` for the full 8-phase cleanup log.

### Added

- **Geometric-pattern build pipeline** — 9 splits + 3 diagram primitives + 2 special objects + 1 Mermaid fallback (14 patterns) governed by 5 hardline rules. The pattern is the spec.
- **Chat-driven `register_template.py`** — three subcommands (`propose` / `commit` / `interactive`). Replaces the PowerShell TTY-gated flow for coworker setup. Safety property preserved via explicit `picks.json`.
- **Pydantic-validated `_meta.json`** at schema version 2 — adds `brand_primary` + `brand_accent` fields driven from `brand.yml` so no one client's defaults leak into other decks.
- **`_paths.py` registry** — single source of truth for ~35 pipeline artifact filenames across 5 scripts. Filename helpers + uppercase constants for both absolute-path and slide-relative call sites.
- **`_contract.py` module-load contract test** — verifies paths registry, meta-JSON schema round-trip, and handoff coverage at the manifest level. Required to pass before any release tag.
- **`_log.py` build.log tee** — every pipeline-script run appends timestamped stdout + stderr to `<out>/build.log`.
- **`clean.py`** — removes ephemeral artifacts from a build dir while preserving `picks.json`, agent build scripts, and prompts. `--deep` for full reset.
- **`diagnostic.py`** — bundles `_meta.json` + all `_prompt.md` + `*.qc.json` + `build.log` into a zip for bug reports.
- **Onboarding docs** — `README.md`, `INSTALL.md`, `examples/quickstart-brief.md`, `examples/RUN.md`, `TROUBLESHOOTING.md`.
- **9 Tier-1 anti-exemplars** ported from v1 corpus into `reference/anti-patterns/<slug>/` with PNG + WHY.md.
- **Brand-display polish in `REVIEW.html`** — `acme` → `ACME`, etc., via per-brand override table.

### Changed

- **Default skill** — `slide-builder` is now the default Slide Lab build layer (was: opt-in alongside the legacy chassis-vocabulary skill). The legacy chassis-vocabulary skill was archived and removed from disk during Path D consolidation.
- **Shared infrastructure re-homed in-tree** — all infra previously imported from the legacy chassis-vocabulary skill (`twins/{client_theme,composer,helpers}.py`, `scripts/icon_helper.py`, `patches/patches.py`, `icons/*.xml`) was re-homed into this skill in Phase 2. No more cross-skill imports.
- **SKILL.md routing** — single-default-skill model. Drops A/B testing section, "Exclusive to v1" section rewritten as "v1 retirement," adds "first time?" + brief-format-spec sections.
- **Rotation seed documentation in `layouts.md:5`** — now correctly documents `pattern_pick_seed = md5(content_hash + slide_n)` and `variant_seed_{A,B,C} = md5(content_hash + slide_n + option_letter)` per `build_deck.py:404-427`. Previous text was a v1-era fiction.
- **`reference/fallback.md` brand mapping section** — rewritten for the `brand.yml`-canonical world; the slot-position mapping table is replaced with the canonical `brand.yml` field mapping from `build_deck.py::_compute_theme_variables`.
- **`page_type` lookup in build_review.py** — now reads only from `_meta.json` (canonical). The dead `**Page type (heuristic):**` regex against `_prompt.md` is removed.
- **PNG-too-small QC floor** — lowered from 50KB to 12KB so sparse/cover slides don't false-positive.
- **`render_mermaid.py --theme`** — now required (no client-shaped default).

### Removed

- **`theme/mermaid-brand.json`** (dead fallback file — Stage-1 requires per-client brand.yml).
- **`scripts/_verify_critical_fixes.py`** (one-off scaffold).
- **12 already-decisioned v1 `dont/` slugs** (`b-bridge`, `b-framing`, etc.).
- **40 legacy process-artifact files** at the archived skill's `exemplars/` root (`_fix_report_*`, `_qc_report_*`, `_reverify_report_*`, `_phase3_*`).
- **NFL scope** — explicitly out of scope for v0.1.

### Notes

- Phase 7 (bloat archive) reclaimed approximately 1.26 GB across OneDrive, Documents, and Downloads — see `_decisions/cleanup-plan-master-2026-05-26.md` Phase 7 status log for the file-by-file accounting.
- Phase 8 archived the legacy chassis-vocabulary skill (since removed from disk) and consolidated the surviving skill at `slide-builder/`. All internal references, the storyline-helper handoff, and memory files were updated in the same pass.
