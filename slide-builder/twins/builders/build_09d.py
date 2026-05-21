"""
Builder for pattern 09d: Agenda — numbered TOC + objectives — DARK variant.

Light source: twins/builders/build_09.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title", "Agenda — eight sections, four objectives.",
        x_px=64, y_px=32, w_px=1000, h_px=68,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "Each section advances one of the objectives.",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    body_top = 220
    body_h = 420
    grid_left = 56
    toc_w = 615
    obj_w = 505
    obj_x = grid_left + toc_w + 48

    rule_x = grid_left + toc_w + 24
    add_rect(slide, "column-rule", x_px=rule_x, y_px=body_top + 4, w_px=1, h_px=body_h - 8, fill_color=CARD_BORDER_DARK)

    item_h = body_h // 8
    toc_data = [
        ("01", "The problem", "Consultants rarely lack ideas — they struggle to cut through them."),
        ("02", "Why existing tools don't fix it", "Training gap and GenAI gap share the same root cause."),
        ("03", "What Slide Lab actually is", "A thought partner, not a slide machine."),
        ("04", "The ecosystem", "Think, Argue, Build — connected, not stacked."),
        ("05", "The proof", "Cycle time and partner-edit rates against the baseline."),
        ("06", "Demo: Think & Argue", "A 30-second sequence from a real session."),
        ("07", "Demo: Build", "From governing thought to a real PPTX."),
        ("08", "Honest expectations and the ask", "What works today, what's still growing, what we want."),
    ]
    for i, (num, title, desc) in enumerate(toc_data):
        n = i + 1
        ty = body_top + i * item_h
        add_text(
            slide, f"toc-{n}-num", num,
            x_px=grid_left, y_px=ty + 6, w_px=56, h_px=36,
            font_size_px=28, color=BRAND_ACCENT_SOFT, bold=True,
        )
        add_text(
            slide, f"toc-{n}-title", title,
            x_px=grid_left + 74, y_px=ty + 6, w_px=toc_w - 74, h_px=22,
            font_size_px=15, color=WHITE, bold=True,
        )
        add_text(
            slide, f"toc-{n}-desc", desc,
            x_px=grid_left + 74, y_px=ty + 26, w_px=toc_w - 74, h_px=18,
            font_size_px=12, color=TEXT_ON_DARK_MID, italic=True,
        )
        if i < 7:
            add_rect(slide, f"toc-{n}-sep", x_px=grid_left, y_px=ty + item_h - 1,
                     w_px=toc_w - 24, h_px=1, fill_color=CARD_BORDER_DARK)

    add_text(
        slide, "objectives-label", "SESSION OBJECTIVES",
        x_px=obj_x, y_px=body_top, w_px=obj_w, h_px=16,
        font_size_px=11, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True,
    )
    add_text(
        slide, "objectives-heading", "By the end of 30 minutes, you should be able to —",
        x_px=obj_x, y_px=body_top + 22, w_px=obj_w, h_px=44,
        font_size_px=18, color=WHITE, bold=True,
    )

    obj_data = [
        "Understand why decks degrade — and why that's a structural problem, not a skill problem.",
        "See how Slide Lab fixes it differently from training or generic AI.",
        "Decide whether to sponsor a four-week pilot with one practice.",
        "Align on what good looks like for the rollout — and what would kill it.",
    ]
    obj_top = body_top + 78
    obj_row_h = 50
    for i, txt in enumerate(obj_data):
        n = i + 1
        oy = obj_top + i * obj_row_h
        marker = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            px_to_emu(obj_x), px_to_emu(oy + 6),
            px_to_emu(10), px_to_emu(10),
        )
        marker.name = f"objective-{n}-marker"
        marker.fill.solid()
        marker.fill.fore_color.rgb = BRAND_ACCENT
        marker.line.fill.background()
        add_text(
            slide, f"objective-{n}-text", txt,
            x_px=obj_x + 22, y_px=oy, w_px=obj_w - 22, h_px=44,
            font_size_px=13, color=WHITE,
        )

    note_y = obj_top + 4 * obj_row_h + 18
    add_rect(slide, "objectives-rule", x_px=obj_x, y_px=note_y, w_px=32, h_px=2, fill_color=CARD_BORDER_DARK)
    add_text(
        slide, "objectives-note",
        "Each section maps to one of the four. Stop me anywhere an objective isn't being served.",
        x_px=obj_x, y_px=note_y + 12, w_px=obj_w, h_px=44,
        font_size_px=12, color=TEXT_ON_DARK_MID, italic=True,
    )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "1",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "09d_agenda-numbered-toc.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
