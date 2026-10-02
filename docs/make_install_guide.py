"""Generate Slide-Lab-Install-Guide.docx, the short Word guide consultants forward.

Regenerate whenever the install steps change:

    py -3 docs/make_install_guide.py

The README install section is the single source of truth for commands. This
script copies the paste-in request straight out of README.md ("Step 2" code
block), so the two can never drift. Everything else in the guide is plain
prose; it deliberately contains no other command blocks.

Style rules for this document (keep them when editing):
  - plain American English, no jargon, no em-dashes (U+2014)
  - Calibri, one accent color (#0B3C49), no clip art, no emoji
  - never claim Slide Lab "updates itself" or that there are "no pop-ups"
  - no client names, no firm names
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

REPO = Path(__file__).resolve().parent.parent
README = REPO / "README.md"
OUT = REPO / "Slide-Lab-Install-Guide.docx"

AS_OF = "Accurate as of 2 October 2026"
REPO_URL = "https://github.com/mperaltajr/skills"

ACCENT = RGBColor(0x0B, 0x3C, 0x49)
ACCENT_HEX = "0B3C49"
TEXT = RGBColor(0x22, 0x22, 0x22)
MUTED = RGBColor(0x5A, 0x5A, 0x5A)
FONT = "Calibri"
MONO = "Consolas"
BODY_PT = 10.5


# ---------------------------------------------------------------- README ---

def paste_request_from_readme() -> str:
    """Return the exact paste-in request from README 'Step 2', verbatim."""
    text = README.read_text(encoding="utf-8")
    m = re.search(r"^### Step 2\..*?^```[^\n]*\n(.*?)\n```", text, re.S | re.M)
    if not m:
        sys.exit("Could not find the Step 2 paste-in request in README.md")
    req = m.group(1).strip("\n")
    if "Install Slide Lab" not in req:
        sys.exit("README Step 2 code block no longer looks like the paste-in request")
    return req


# --------------------------------------------------------------- helpers ---

def set_cell_shading(cell, hex_fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tc_pr.append(shd)


def set_cell_margins(cell, top=60, bottom=60, left=100, right=100) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for side, val in (("top", top), ("bottom", bottom), ("start", left), ("end", right)):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tc_pr.append(mar)


def set_table_borders(table, color="BFC7CA", size=4, left_accent=False) -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{side}")
        if left_accent and side == "left":
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "24")
            el.set(qn("w:color"), ACCENT_HEX)
        elif left_accent:
            el.set(qn("w:val"), "nil")
        else:
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), str(size))
            el.set(qn("w:color"), color)
        el.set(qn("w:space"), "0")
        borders.append(el)
    tbl_pr.append(borders)


def set_col_widths(table, widths_in) -> None:
    """Fixed column widths that both Word and LibreOffice respect."""
    table.autofit = False
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(int(sum(widths_in) * 1440)))
    tbl_w.set(qn("w:type"), "dxa")
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tbl_pr.append(layout)
    grid = tbl.tblGrid
    for gc, w in zip(grid.findall(qn("w:gridCol")), widths_in):
        gc.set(qn("w:w"), str(int(w * 1440)))
    for row in table.rows:
        for cell, w in zip(row.cells, widths_in):
            cell.width = Inches(w)


def keep_row_together(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    cant = OxmlElement("w:cantSplit")
    tr_pr.append(cant)


def add_hyperlink(paragraph, url: str, text: str, bold=False):
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), r_id)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    fonts = OxmlElement("w:rFonts")
    fonts.set(qn("w:ascii"), FONT)
    fonts.set(qn("w:hAnsi"), FONT)
    rpr.append(fonts)
    color = OxmlElement("w:color")
    color.set(qn("w:val"), ACCENT_HEX)
    rpr.append(color)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rpr.append(u)
    if bold:
        rpr.append(OxmlElement("w:b"))
    run.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    run.append(t)
    link.append(run)
    paragraph._p.append(link)


def add_rich(paragraph, parts, size=BODY_PT, color=TEXT):
    """parts: list of str or (text, style) where style in {'b','i','link:URL'}."""
    for part in parts:
        if isinstance(part, str):
            r = paragraph.add_run(part)
            r.font.size = Pt(size)
            r.font.color.rgb = color
            continue
        txt, style = part
        if style.startswith("link:"):
            add_hyperlink(paragraph, style[5:], txt)
            continue
        r = paragraph.add_run(txt)
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.bold = "b" in style
        r.italic = "i" in style
    return paragraph


def para(doc_or_cell, parts, size=BODY_PT, after=4, before=0, color=TEXT, align=None):
    p = doc_or_cell.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(after)
    pf.space_before = Pt(before)
    pf.line_spacing = 1.08
    if align:
        p.alignment = align
    add_rich(p, parts if isinstance(parts, list) else [parts], size=size, color=color)
    return p


def bullet(doc, parts, after=2):
    p = doc.add_paragraph(style="List Bullet")
    pf = p.paragraph_format
    pf.space_after = Pt(after)
    pf.line_spacing = 1.08
    add_rich(p, parts if isinstance(parts, list) else [parts])
    return p


def numbered(doc, parts, after=2):
    p = doc.add_paragraph(style="List Number")
    pf = p.paragraph_format
    pf.space_after = Pt(after)
    pf.line_spacing = 1.08
    add_rich(p, parts if isinstance(parts, list) else [parts])
    return p


def heading(doc, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(10)
    pf.space_after = Pt(3)
    pf.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = ACCENT
    return p


def table(doc, header, rows, widths):
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    set_table_borders(t)
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        set_cell_shading(c, ACCENT_HEX)
        set_cell_margins(c)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for ri, row in enumerate(rows, start=1):
        keep_row_together(t.rows[ri])
        for ci, val in enumerate(row):
            c = t.rows[ri].cells[ci]
            set_cell_margins(c)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            parts = val if isinstance(val, list) else [val]
            if ci == 0:
                parts = [(x, "b") if isinstance(x, str) else x for x in parts]
            add_rich(p, parts, size=10)
    set_col_widths(t, widths)
    # small gap after the table
    gap = doc.add_paragraph()
    gap.paragraph_format.space_after = Pt(0)
    gap.paragraph_format.line_spacing = Pt(6)
    return t


def paste_box(doc, text):
    t = doc.add_table(rows=1, cols=1)
    set_table_borders(t, left_accent=True)
    c = t.rows[0].cells[0]
    set_cell_shading(c, "EEF2F3")
    set_cell_margins(c, top=100, bottom=100, left=160, right=160)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.1
    r = p.add_run(text)
    r.font.name = MONO
    r._element.rPr.rFonts.set(qn("w:eastAsia"), MONO)
    r.font.size = Pt(9.5)
    r.font.color.rgb = TEXT
    set_col_widths(t, [6.5])
    gap = doc.add_paragraph()
    gap.paragraph_format.space_after = Pt(0)
    gap.paragraph_format.line_spacing = Pt(6)


def add_page_number(paragraph):
    # One run per field piece, each carrying the small footer size, so the
    # page number renders at the same size as the rest of the footer.
    for kind, val in (("begin", None), ("instr", " PAGE "), ("separate", None),
                      ("text", "1"), ("end", None)):
        run = paragraph.add_run()
        run.font.size = Pt(8.5)
        run.font.color.rgb = MUTED
        if kind == "instr":
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = val
        elif kind == "text":
            el = OxmlElement("w:t")
            el.text = val
        else:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        run._r.append(el)


# ------------------------------------------------------------------ build ---

def build() -> Path:
    request = paste_request_from_readme()

    doc = Document()
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.left_margin = sec.right_margin = Inches(1)
    sec.top_margin = Inches(0.8)
    sec.bottom_margin = Inches(0.8)

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    normal.font.size = Pt(BODY_PT)
    normal.font.color.rgb = TEXT
    for sname in ("List Bullet", "List Number"):
        st = doc.styles[sname]
        st.font.name = FONT
        st.font.size = Pt(BODY_PT)

    core = doc.core_properties
    core.title = "Slide Lab install guide"
    core.author = "Slide Lab"
    core.comments = AS_OF

    # Footer: as-of stamp + page number
    fstyle = doc.styles["Footer"]
    fstyle.font.size = Pt(8.5)
    fstyle.font.color.rgb = MUTED
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = fp.add_run(f"Slide Lab install guide  |  {AS_OF}  |  Page ")
    r.font.size = Pt(8.5)
    r.font.color.rgb = MUTED
    add_page_number(fp)

    # Title block
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("Slide Lab install guide")
    r.bold = True
    r.font.size = Pt(22)
    r.font.color.rgb = ACCENT
    para(doc, [("Set up Slide Lab on your computer and build your first deck. ", ""),
               (AS_OF + ".", "i")],
         size=10.5, color=MUTED, after=2)
    rule = doc.add_paragraph()
    rule.paragraph_format.space_after = Pt(4)
    p_pr = rule._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), ACCENT_HEX)
    bdr.append(bottom)
    p_pr.append(bdr)

    # 1. What Slide Lab is
    heading(doc, "1. What Slide Lab is")
    para(doc, ["Slide Lab is an add-on for Claude that turns your message, notes and numbers "
               "into a finished PowerPoint deck on your client's own template, with their "
               "colors, fonts and layouts. It helps you shape the storyline, shows you three "
               "designs for each slide to pick from, then builds the deck and checks every "
               "slide before you open it."])

    # 2. Before you start
    heading(doc, "2. Before you start: install three programs")
    para(doc, ["Install these yourself from your company's software portal (Software Center, "
               "Self Service or similar). If you are not on a company computer, use the "
               "official sites."], after=5)
    table(
        doc,
        ["Program", "Why Slide Lab needs it", "Where to get it"],
        [
            ["Claude (desktop app or Claude Code)", "Runs Slide Lab",
             ["However your company provides Claude; otherwise ",
              ("claude.ai/code", "link:https://claude.ai/code")]],
            ["Python 3.10 or newer", "Runs the build steps behind the scenes",
             ["Software portal, or ",
              ("python.org", "link:https://www.python.org/downloads/")]],
            ["LibreOffice", "Required. Draws slide previews during template registration, "
             "the final check page and the quality check",
             ["Software portal, or ",
              ("libreoffice.org", "link:https://www.libreoffice.org/download/"),
              ". ", ("Request it on day one:", "b"),
              " on company computers it can need approval"]],
        ],
        widths=[1.7, 2.45, 2.35],
    )
    para(doc, ["Git (a download tool Slide Lab uses) is usually already there, because Claude "
               "Code on Windows uses it. If the setup check later says it is missing, get it "
               "from the portal or ", ("git-scm.com", "link:https://git-scm.com"), "."],
         after=2)

    # 3. Let Claude do the rest
    heading(doc, "3. Let Claude do the rest")
    numbered(doc, ["Open Claude and paste this request exactly as written:"], after=4)
    paste_box(doc, request)
    numbered(doc, ["Claude asks before each download or install (your company's settings may "
                   "require that). Click ", ("Allow", "b"), " each time."])
    numbered(doc, ["At the end Claude shows a setup table listing each piece as OK or not. "
                   "Any row that is not OK says exactly what to do."])
    numbered(doc, [("Restart Claude", "b"), " (close it and open it again) so it loads Slide "
                   "Lab. Then type /slide-lab or just ask for a deck."], after=4)
    para(doc, [("Prefer to type the commands yourself? ", "b"),
               "See the Install section of README.md in the Slide Lab folder or at ",
               (REPO_URL, "link:" + REPO_URL), "."], after=2)

    # 4. How long
    heading(doc, "4. How long it takes")
    para(doc, ["About 20 to 45 minutes the first time, plus however long the software portal "
               "takes to approve and install LibreOffice."])

    # 5. Getting up and running
    heading(doc, "5. Getting up and running")
    table(
        doc,
        ["Topic", "What to know"],
        [
            ["Where to keep your work",
             ["Work in a folder on your own drive, ",
              ("C:\\Users\\<you>\\Slide Lab\\sessions\\<Client>\\", "b"),
              " (the setup creates it, with a Desktop shortcut). ",
              ("Not in OneDrive:", "b"),
              " syncing hundreds of working files slowed builds from about 4 minutes per "
              "page to 9 to 20 and made previews time out. Copy finished decks to OneDrive "
              "or SharePoint."]],
            ["Your client's template",
             ["It can live anywhere, but must be 16:9 at 13.333 x 7.5 inches (PowerPoint's "
              "standard widescreen). Register each template once, about 5 to 10 minutes: "
              "Claude asks which colors are the main, highlight and cover colors and which "
              "layouts to use, then you open one sample slide in PowerPoint and confirm it "
              "looks right. Your original file is never changed."]],
            ["Your first deck",
             ["Start with 5 to 8 slides. Bring the main message, the audience, and your "
              "numbers or notes."]],
            ["How long a deck takes",
             ["A typical 10 to 15 slide deck takes 1 to 2 hours end to end, including your "
              "review time."]],
            ["When you are done",
             ["Say ", ("\"the deck is good\"", "b"), ". Slide Lab deletes the working files "
              "it no longer needs and keeps the deck and everything needed to edit it later."]],
        ],
        widths=[1.7, 4.8],
    )

    # 6. Updates
    heading(doc, "6. Getting updates")
    para(doc, ["Slide Lab checks for updates once a day when you start using it, and asks "
               "before installing. Say yes, and restart Claude if it asks you to. To check "
               "any time, say ", ("\"update Slide Lab\"", "b"), "."])

    # 7. If something goes wrong
    heading(doc, "7. If something goes wrong")
    table(
        doc,
        ["If this happens", "Do this"],
        [
            ["Something in the setup is not working",
             ["Tell Claude ", ("\"check my Slide Lab setup\"", "b"),
              ". It runs a checker, changes nothing, and shows what to fix."]],
            ["A \"certificate\" error during setup",
             ["Try again first; it usually clears on its own. If it keeps happening, tell "
              "Claude, or see the Install section of README.md."]],
            ["Anything else, or a deck did not come out right",
             ["Type ", ("/slidelab-log", "b"), " in Claude. It writes the problem report "
              "for you and gives you a link to send it."]],
        ],
        widths=[2.2, 4.3],
    )

    # 8. Learn more
    heading(doc, "8. Where to learn more")
    para(doc, ["Open ", ("Slide-Lab-Tutorial.html", "b"), " in the Slide Lab folder for a "
               "step-by-step walkthrough with timings. The example files next to it "
               "(Slide-Lab-Example-Storyline.html, Slide-Lab-Example-Review.html and "
               "Slide-Lab-Example-Deck.pptx) show what each stage looks like."])

    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    out = build()
    print(f"Wrote {out}")
