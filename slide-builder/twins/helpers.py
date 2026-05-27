"""
Shared helpers for hand-built PPTX twins.

Every pattern's twin builder imports these. Universal-invariant shapes (chrome,
title block, footer, convergence) get drawn here so each pattern builder only
has to add its body-specific shapes.

All position/size parameters are in CSS pixels (1280x720 canvas). Conversion to
EMU happens inside this module.
"""
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# --- Brand palette (Accenture Graphik template — ACN Graphik Template.md) ---
# lt2  = #460073  Deep Purple     — dark backgrounds, primary dark fills
BRAND_PRIMARY     = RGBColor(0x46, 0x00, 0x73)
# accent1 = #7500C0  Medium Purple — mid-weight fills, sidebar panels
BRAND_PRIMARY_MID = RGBColor(0x75, 0x00, 0xC0)
# dk2  = #A100FF  Electric Purple — accent moments (one per slide)
BRAND_ACCENT      = RGBColor(0xA1, 0x00, 0xFF)
# accent2 = #C2A3FF  Light Purple  — soft accents, borders
BRAND_ACCENT_SOFT = RGBColor(0xC2, 0xA3, 0xFF)
# dk1  = #000000  Black            — primary body text
TEXT_DARK         = RGBColor(0x00, 0x00, 0x00)
# mid-gray for secondary labels and captions
TEXT_MID          = RGBColor(0x59, 0x59, 0x59)
# light-gray for tertiary labels, rules, footnotes
TEXT_FAINT        = RGBColor(0x88, 0x88, 0x88)
SLIDE_BG          = RGBColor(0xFF, 0xFF, 0xFF)
# accent3 = #E6DCFF  Very Light Purple — card / tile fills
CARD_BG           = RGBColor(0xE6, 0xDC, 0xFF)
# accent2 = #C2A3FF  Light Purple — card borders
CARD_BORDER       = RGBColor(0xC2, 0xA3, 0xFF)
DRAFT_BG          = RGBColor(0xFF, 0xD6, 0x00)
DRAFT_TEXT        = RGBColor(0xB7, 0x1C, 0x1C)
WHITE             = RGBColor(0xFF, 0xFF, 0xFF)
# Additional Accenture Graphik accent colors (available but not required on every slide)
ACCENT_PINK       = RGBColor(0xFF, 0x50, 0xA0)   # accent4 #FF50A0
ACCENT_BLUE       = RGBColor(0x22, 0x4B, 0xFF)   # accent5 #224BFF
ACCENT_TEAL       = RGBColor(0x05, 0xF2, 0xDB)   # accent6 #05F2DB

# --- Canvas constants ---
SLIDE_W_PX = 1280
SLIDE_H_PX = 720
SLIDE_W_EMU = Emu(SLIDE_W_PX * 9525)
SLIDE_H_EMU = Emu(SLIDE_H_PX * 9525)

# CSS px → EMU (96dpi assumed for screen pixels; PowerPoint uses 914400 EMU/in)
def px_to_emu(px):
    return Emu(int(px * 9525))

# CSS px → PowerPoint pt (1px @ 96dpi = 0.75pt @ 72dpi)
def px_to_pt(px):
    return Pt(px * 0.75)


def new_slide(prs=None):
    """Create a fresh 1280x720 slide on a blank layout. Returns (prs, slide)."""
    if prs is None:
        prs = Presentation()
        prs.slide_width = SLIDE_W_EMU
        prs.slide_height = SLIDE_H_EMU
    blank_layout = next(
        (l for l in prs.slide_layouts if l.name.strip().lower() == "blank"),
        prs.slide_layouts[6]
    )
    slide = prs.slides.add_slide(blank_layout)
    # Set white background
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = SLIDE_BG
    return prs, slide


import re

_INLINE_TAG_RE = re.compile(r"<(strong|em|b|i)>(.*?)</\1>", re.IGNORECASE | re.DOTALL)


def _split_runs(text, *, base_bold=False, base_italic=False,
                base_color=None, emphasis_color=None):
    """Parse `<strong>X</strong>` / `<em>X</em>` (and `<b>` / `<i>`) tags into a
    list of (segment, bold, italic, color) tuples. Other inline content gets
    base styling. Returns [] if input is empty/None.

    `emphasis_color` (optional) tints strong/b segments — e.g., brand-primary
    highlights on a title.
    """
    if not text:
        return []
    runs = []
    pos = 0
    for m in _INLINE_TAG_RE.finditer(text):
        if m.start() > pos:
            runs.append((text[pos:m.start()], base_bold, base_italic, base_color))
        tag = m.group(1).lower()
        seg = m.group(2)
        is_strong = tag in ("strong", "b")
        is_em = tag in ("em", "i")
        runs.append((
            seg,
            base_bold or is_strong,
            base_italic or is_em,
            emphasis_color if (is_strong and emphasis_color) else base_color,
        ))
        pos = m.end()
    if pos < len(text):
        runs.append((text[pos:], base_bold, base_italic, base_color))
    return runs


def add_text(slide, shape_id, text, x_px, y_px, w_px, h_px, *,
             font_size_px=14, font_size_pt=None, color=TEXT_DARK, bold=False, italic=False,
             font_name="Inter", align="left", anchor="top",
             letter_spacing_px=0, uppercase=False, bg_fill=None,
             padding_px=(0, 0, 0, 0), emphasis_color=None):
    """
    Add a text shape with given content. `shape_id` becomes the shape name
    (used by the deck composer to find shapes for text/color substitution).

    If `text` contains `<strong>...</strong>` or `<em>...</em>` tags, the
    text is split into multiple runs. Strong runs get `bold=True` and (if
    provided) `emphasis_color` (typically brand-primary). Em runs get italic.
    Other tags pass through unchanged.
    """
    tb = slide.shapes.add_textbox(
        px_to_emu(x_px), px_to_emu(y_px),
        px_to_emu(w_px), px_to_emu(h_px),
    )
    tb.name = shape_id
    if bg_fill is not None:
        tb.fill.solid()
        tb.fill.fore_color.rgb = bg_fill
        tb.line.fill.background()
    else:
        # Default: no fill, no line
        tb.fill.background()
        tb.line.fill.background()

    tf = tb.text_frame
    tf.word_wrap = True
    pt, pr, pb, pl = padding_px
    tf.margin_top = px_to_emu(pt)
    tf.margin_right = px_to_emu(pr)
    tf.margin_bottom = px_to_emu(pb)
    tf.margin_left = px_to_emu(pl)
    tf.vertical_anchor = {
        "top": MSO_ANCHOR.TOP,
        "middle": MSO_ANCHOR.MIDDLE,
        "bottom": MSO_ANCHOR.BOTTOM,
    }.get(anchor, MSO_ANCHOR.TOP)

    p = tf.paragraphs[0]
    p.alignment = {
        "left": PP_ALIGN.LEFT,
        "center": PP_ALIGN.CENTER,
        "right": PP_ALIGN.RIGHT,
    }.get(align, PP_ALIGN.LEFT)

    runs = _split_runs(
        text,
        base_bold=bold,
        base_italic=italic,
        base_color=color,
        emphasis_color=emphasis_color,
    )
    if not runs:
        runs = [(text or "", bold, italic, color)]

    for seg, seg_bold, seg_italic, seg_color in runs:
        run = p.add_run()
        run.text = seg.upper() if uppercase else seg
        f = run.font
        f.name = font_name
        f.size = Pt(font_size_pt) if font_size_pt is not None else px_to_pt(font_size_px)
        f.bold = seg_bold
        f.italic = seg_italic
        if seg_color is not None:
            f.color.rgb = seg_color

    return tb


def add_icon(slide, shape_id, x_px, y_px, size_px, glyph, *,
             color=None, font_name="Segoe UI Symbol"):
    """Add a glyph-based icon (Unicode character rendered in a sized text box).

    Examples of usable glyphs (Inter/Segoe-friendly):
      ☰  trigram (menu/lines)        →  arrow-right
      ✦  starburst                    ⊕  circled-plus
      ⊞  squared-plus                 ◇  diamond
      ▲  triangle                     ●  circle
      ✓  check                        ★  star
      ⓘ  info                         ⚙  gear (may not render in all fonts)
      ⚒  hammer-pick

    The icon is centered inside its bounding box. Use Inter or system fallback
    for most glyphs; Segoe UI Symbol gives the broadest coverage on Windows.
    """
    if color is None:
        color = BRAND_ACCENT
    tb = slide.shapes.add_textbox(
        px_to_emu(x_px), px_to_emu(y_px),
        px_to_emu(size_px), px_to_emu(size_px),
    )
    tb.name = shape_id
    tb.fill.background()
    tb.line.fill.background()
    tf = tb.text_frame
    tf.word_wrap = False
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.margin_left = 0
    tf.margin_right = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = glyph
    f = run.font
    f.name = font_name
    f.size = px_to_pt(int(size_px * 0.85))
    f.color.rgb = color
    return tb


def add_icon_from_library(slide, shape_id, x_px, y_px, size_px, name, *,
                          color=None):
    """Insert a real vector icon from the Slide Lab icon library.

    PREFER THIS over `add_icon(...glyph=...)` whenever the slide calls for an icon
    (process / data / people / risk / decision / etc.). The library ships 1,143
    pre-extracted icons. Generic Unicode glyphs (☰ ✦ →) are a last resort only.

    The 15 standard icons (use these first; full catalog in icons/icon-index.json):
      gear            — process / operations / workflow
      wrench          — work in progress / tools
      people          — team / workforce / org
      chart-bar       — data / analytics / reporting
      compass         — strategy / direction / vision
      calendar        — timeline / schedule
      coins           — cost / budget / value
      shield-warning  — risk / controls / escalation
      diamond         — decision / approval / governance
      lightbulb       — insight / finding / idea
      globe           — external / market / scale
      clipboard-check — compliance / audit / sign-off
      chip            — technology / systems / AI
      speech          — communication / engagement / change
      package         — delivery / output / shipping

    The icon is tinted with `color` (defaults to BRAND_ACCENT). After the theme
    graft pipeline runs, BRAND_ACCENT gets remapped to the client's accent — so
    icons inherit client brand automatically.

    Example:
        add_icon_from_library(slide, "think-icon",
                              x_px=200, y_px=300, size_px=64,
                              name="lightbulb")

    Falls back to a labeled dashed-border placeholder if the named icon's XML
    doesn't exist in slide-builder/icons/ — the build never errors. v0.1
    ships pre-extracted icons; there is no live extraction step.
    """
    import sys
    from pathlib import Path as _Path
    _SCRIPTS = _Path(__file__).resolve().parent.parent / "scripts"
    if str(_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS))
    from icon_helper import insert_icon

    if color is None:
        color = BRAND_ACCENT
    # RGBColor -> hex string for icon_helper
    if hasattr(color, "_RGBColor__valstr"):
        hex_color = "#" + color._RGBColor__valstr.upper()
    else:
        try:
            hex_color = "#{:02X}{:02X}{:02X}".format(*color)
        except Exception:
            hex_color = "#A100FF"
    insert_icon(
        icon_name=name,
        target_slide=slide,
        left_emu=int(px_to_emu(x_px)),
        top_emu=int(px_to_emu(y_px)),
        width_emu=int(px_to_emu(size_px)),
        height_emu=int(px_to_emu(size_px)),
        accent_color=hex_color,
    )
    # The icon is appended directly to spTree as the latest shape; expose it via
    # the standard shapes collection for downstream naming (set on the last shape).
    if len(slide.shapes) > 0:
        try:
            slide.shapes[-1].name = shape_id
        except Exception:
            pass
    return None  # icon_helper returns bool; the wrapper returns None to keep API simple


def add_circle(slide, shape_id, x_px, y_px, diameter_px, fill_color, *,
               no_line=True):
    """Add a filled circle (oval with equal width/height). The standard
    container for an icon when the brief calls for an "icon chip" treatment.

    Circles read as editorial; squares read as web-app tiles. Use circles.

    Example:
        cx, cy, d = 240, 280, 80
        add_circle(slide, "think-bg", cx - d//2, cy - d//2, d, BRAND_PRIMARY)
        add_icon_from_library(slide, "think-icon",
                              cx - 24, cy - 24, 48,
                              name="lightbulb", color=WHITE)
    """
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        px_to_emu(x_px), px_to_emu(y_px),
        px_to_emu(diameter_px), px_to_emu(diameter_px),
    )
    shape.name = shape_id
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if no_line:
        shape.line.fill.background()
    return shape


def add_rect(slide, shape_id, x_px, y_px, w_px, h_px, fill_color, *, no_line=True):
    """Add a filled rectangle. Used for rules, accent strips, color bars."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        px_to_emu(x_px), px_to_emu(y_px),
        px_to_emu(w_px), px_to_emu(h_px),
    )
    shape.name = shape_id
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if no_line:
        shape.line.fill.background()
    return shape


# ============================================================================
# Universal invariants — chrome + title block + footer + convergence
# ============================================================================

def add_chrome(slide):
    """No-op. The top chrome zone is reserved invariant space — only sources/
    footnotes/page numbers belong on the slide, all in the bottom footer.
    Kept as a function so existing builders don't need to be edited.
    """
    pass


# ---------------------------------------------------------------------------
# Cross-skill placeholder contract (F1-B, 2026-05-26)
# ---------------------------------------------------------------------------
# These two strings are INTENTIONAL presenter prompts that render in the
# footer when add_footer() is called with footnote=None or source=None.
# slide-qc imports them by name to allowlist the convention so its hygiene
# pre-pass and vision pass don't flag them as Critical lorem-ipsum residue.
#
# DO NOT change the wording without coordinating with slide-qc — the
# contract is identity-matched, not regex-guessed.
INTENTIONAL_FOOTNOTE_PLACEHOLDER = "[add footnote here or delete]"
INTENTIONAL_SOURCE_PLACEHOLDER = "[add source here or delete]"


def add_footer(slide, page_num, source=None, footnote=None):
    """ALWAYS a footnote line + source line + page number (exact skeleton positions).

    Invariant zone rule: ONLY sources, footnotes, and the page number may appear
    in the bottom invariant zone. No 'Slide Lab · YEAR · N' branding, no
    'CONFIDENTIAL' tag, no copyright. NO footer-rule divider line either —
    the user flagged that as visual noise.

    BOTH source and footnote lines are ALWAYS drawn — pass real text for each,
    or omit for placeholders. The user is expected to fill or delete in
    PowerPoint; the builder never guesses whether the slide needs them.

    Placeholder text comes from INTENTIONAL_FOOTNOTE_PLACEHOLDER and
    INTENTIONAL_SOURCE_PLACEHOLDER module constants — these are the
    cross-skill contract slide-qc imports to allowlist the convention.

    Positions match the skeleton:
      footnote     x=58   y=672  w=1164  h=16  (faint)
      source       x=58   y=688  w=1100  h=16  (italic faint)
      page number  x=1170 y=688  w=52    h=16  (right-aligned)
    """
    footnote_text = footnote if footnote else INTENTIONAL_FOOTNOTE_PLACEHOLDER
    add_text(
        slide, "footnote-1", f"1. {footnote_text}",
        x_px=58, y_px=672, w_px=1164, h_px=16,
        font_size_px=10, color=TEXT_FAINT,
    )
    source_text = source if source else INTENTIONAL_SOURCE_PLACEHOLDER
    add_text(
        slide, "source", f"Source: {source_text}",
        x_px=58, y_px=688, w_px=1100, h_px=16,
        font_size_px=10, color=TEXT_FAINT, italic=True,
    )
    add_text(
        slide, "page-number", f"{page_num}",
        x_px=1170, y_px=688, w_px=52, h_px=16,
        font_size_px=11, color=TEXT_FAINT, align="right",
    )


def add_title_block(slide, title, subtitle, *,
                    title_x=64, title_y=20, title_w=1000, title_h=80,
                    subtitle_h=26):
    """Standard title (28pt PPTX, BOTTOM-anchored) + subtitle (16pt PPTX italic).

    Title text is bottom-anchored within its 80px box, so the BOTTOM of the title
    is at a fixed y position (title_y + title_h = y=100) regardless of whether
    the title wraps to 1 or 2 lines. 2-line titles grow UPWARD from that bottom
    line; they never displace the subtitle. Top of the 2-line title can extend
    up to y=28 (still within the safe top zone).

    Title supports inline `<strong>X</strong>` for brand-primary emphasis
    (matches every approved pattern's HTML convention).

    NOTE: this helper no longer auto-draws a brand-accent rule beneath the
    subtitle. Helper-default accent decoration on every slide competed with
    deliberate accent placement by agents, violating the "one accent moment
    per slide" rule. Place accent on whatever element load-bears the takeaway:
    a highlight bar on a chart, a callout on a card, a `BRAND_ACCENT` fill on
    a recommendation band, etc. Cover and hero-statement slides build their
    own title treatment via direct `add_text` calls (see cover exemplars).
    """
    add_text(
        slide, "title", title,
        x_px=title_x, y_px=title_y, w_px=title_w, h_px=title_h,
        font_size_pt=28, color=TEXT_DARK, bold=True,
        emphasis_color=BRAND_PRIMARY,
        anchor="bottom",
    )
    sub_y = title_y + title_h + 8
    add_text(
        slide, "subtitle", subtitle,
        x_px=title_x, y_px=sub_y, w_px=title_w - 120, h_px=subtitle_h,
        font_size_pt=16, color=TEXT_DARK, italic=True,
    )


def add_source(slide, source_text):
    """Source citation in the bottom invariant zone, exact skeleton position
    (x=58, y=688). Italic, faint text. Builders call this when their content
    requires citing — it is NOT auto-emitted by add_footer.
    """
    add_text(
        slide, "source", f"Source: {source_text}",
        x_px=58, y_px=688, w_px=1100, h_px=16,
        font_size_px=10, color=TEXT_FAINT, italic=True,
    )


def add_footnote(slide, n, text):
    """Footnote (numbered) in the bottom invariant zone, just above source.
    Skeleton position (x=58, y=672). Builders call this when their content
    references footnotes — it is NOT auto-emitted by add_footer.
    """
    add_text(
        slide, f"footnote-{n}", f"{n}. {text}",
        x_px=58, y_px=672, w_px=1164, h_px=16,
        font_size_px=10, color=TEXT_FAINT,
    )


def add_convergence(slide, text, *, bottom_px=78, height_px=42):
    """Brand-primary band at bottom of body. White italic text."""
    y = 720 - bottom_px - height_px
    add_rect(
        slide, "convergence-bg",
        x_px=64, y_px=y, w_px=1280 - 128, h_px=height_px,
        fill_color=BRAND_PRIMARY,
    )
    add_text(
        slide, "convergence", text,
        x_px=64, y_px=y, w_px=1280 - 128, h_px=height_px,
        font_size_px=14, color=WHITE, italic=True, bold=False,
        anchor="middle", padding_px=(0, 22, 0, 22),
    )


def add_table(slide, shape_id, x_px, y_px, w_px, h_px, *,
              headers, rows,
              banded=True,
              header_fill=BRAND_PRIMARY,
              header_text=WHITE,
              body_text=TEXT_DARK,
              font_size_px=14,
              font_name="Inter"):
    """Add a native PowerPoint table with mandatory column headers.

    `headers` is REQUIRED — no default. Tables without column labels are
    unreadable; the API enforces what the design rule expects. Pass a list
    of header strings; the column count is derived from that list.

    `rows` is a list of row lists; each row MUST have the same length as
    `headers`. Cells contain plain text only.

    For cell-treatment patterns (harvey balls, RYG pills, arrows, mini-bars,
    sparklines), overlay shapes on top of the table after calling this helper.
    A future version may support cell-type dicts directly — see roadmap.

    Returns the python-pptx `GraphicFrame` containing the table.
    """
    n_cols = len(headers)
    if n_cols == 0:
        raise ValueError("add_table requires at least one header column")
    n_rows = len(rows) + 1  # +1 for the header row

    for i, row in enumerate(rows):
        if len(row) != n_cols:
            raise ValueError(
                f"row {i} has {len(row)} cells, expected {n_cols} to match headers"
            )

    # 14px body-floor enforcement (per final-findings empirical validation —
    # 3 of 20 agents cheated below 14px to fit dense tables; raising here
    # catches the violation at build time regardless of which agent slipped).
    if font_size_px < 14:
        raise ValueError(
            f"add_table font_size_px={font_size_px} is below the 14px body floor. "
            f"If the table doesn't fit at 14px, the content is too dense — shrink "
            f"the dataset, split across two slides, or restructure to a different "
            f"family. Do not cheat the body floor."
        )

    frame = slide.shapes.add_table(
        n_rows, n_cols,
        px_to_emu(x_px), px_to_emu(y_px),
        px_to_emu(w_px), px_to_emu(h_px),
    )
    frame.name = shape_id
    table = frame.table

    def _style_cell(cell, *, text, font_color, bold=False, fill=None):
        if fill is not None:
            cell.fill.solid()
            cell.fill.fore_color.rgb = fill
        cell.text = str(text)
        for paragraph in cell.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.name = font_name
                run.font.size = px_to_pt(font_size_px)
                run.font.bold = bold
                run.font.color.rgb = font_color

    # Header row
    for c, header in enumerate(headers):
        _style_cell(table.cell(0, c),
                    text=header, font_color=header_text,
                    bold=True, fill=header_fill)

    # Body rows
    for r, row_data in enumerate(rows, start=1):
        for c, val in enumerate(row_data):
            band_fill = CARD_BG if (banded and r % 2 == 0) else WHITE
            _style_cell(table.cell(r, c),
                        text=val, font_color=body_text,
                        bold=False, fill=band_fill)

    return frame
