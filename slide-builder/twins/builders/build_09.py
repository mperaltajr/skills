"""
Builder for pattern 09: Agenda — numbered table of contents + objectives panel.

Source HTML: _pattern-library/09_agenda-numbered-toc.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT,
)
from pptx.enum.shapes import MSO_SHAPE


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Agenda — eight sections, four objectives.",
        subtitle="Each section advances one of the objectives.",
        title_h=68,
        subtitle_h=20,
        brand_rule_w=64,
    )

    # Body grid: 1.22fr toc / 1fr objectives, gap 48
    body_top = 220
    body_h = 420
    grid_left = 56
    # Total width 1280-112=1168, 1.22:1 + 48 gap
    # toc width = (1168-48)*1.22/2.22 = 615; obj width = 505
    toc_w = 615
    obj_w = 505
    obj_x = grid_left + toc_w + 48

    # Column rule between
    rule_x = grid_left + toc_w + 24
    add_rect(slide, "column-rule", x_px=rule_x, y_px=body_top + 4, w_px=1, h_px=body_h - 8, fill_color=CARD_BORDER)

    # 8 TOC items, evenly spaced
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
        # Numeral (28px brand-accent bold)
        add_text(
            slide, f"toc-{n}-num", num,
            x_px=grid_left, y_px=ty + 6, w_px=56, h_px=36,
            font_size_px=28, color=BRAND_ACCENT, bold=True,
        )
        # Title
        add_text(
            slide, f"toc-{n}-title", title,
            x_px=grid_left + 74, y_px=ty + 6, w_px=toc_w - 74, h_px=22,
            font_size_px=15, color=BRAND_PRIMARY, bold=True,
        )
        # Desc
        add_text(
            slide, f"toc-{n}-desc", desc,
            x_px=grid_left + 74, y_px=ty + 26, w_px=toc_w - 74, h_px=18,
            font_size_px=12, color=TEXT_MID, italic=True,
        )
        # Separator
        if i < 7:
            add_rect(slide, f"toc-{n}-sep", x_px=grid_left, y_px=ty + item_h - 1,
                     w_px=toc_w - 24, h_px=1, fill_color=CARD_BORDER)

    # Objectives panel
    add_text(
        slide, "objectives-label", "SESSION OBJECTIVES",
        x_px=obj_x, y_px=body_top, w_px=obj_w, h_px=16,
        font_size_px=11, color=TEXT_FAINT, bold=True, uppercase=True,
    )
    add_text(
        slide, "objectives-heading", "By the end of 30 minutes, you should be able to —",
        x_px=obj_x, y_px=body_top + 22, w_px=obj_w, h_px=44,
        font_size_px=18, color=BRAND_PRIMARY, bold=True,
    )

    # 4 objectives
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
        # Marker (10x10 brand-accent circle)
        marker = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            px_to_emu(obj_x), px_to_emu(oy + 6),
            px_to_emu(10), px_to_emu(10),
        )
        marker.name = f"objective-{n}-marker"
        marker.fill.solid()
        marker.fill.fore_color.rgb = BRAND_ACCENT
        marker.line.fill.background()
        # Text
        add_text(
            slide, f"objective-{n}-text", txt,
            x_px=obj_x + 22, y_px=oy, w_px=obj_w - 22, h_px=44,
            font_size_px=13, color=TEXT_DARK,
        )

    # Objectives rule + trailing note
    note_y = obj_top + 4 * obj_row_h + 18
    add_rect(slide, "objectives-rule", x_px=obj_x, y_px=note_y, w_px=32, h_px=2, fill_color=CARD_BORDER)
    add_text(
        slide, "objectives-note",
        "Each section maps to one of the four. Stop me anywhere an objective isn't being served.",
        x_px=obj_x, y_px=note_y + 12, w_px=obj_w, h_px=44,
        font_size_px=12, color=TEXT_MID, italic=True,
    )

    add_footer(slide, page_num=1)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "09_agenda-numbered-toc.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
