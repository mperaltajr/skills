"""
Builder for pattern 11: Long-form structured text (SCQA-style sections).

Source HTML: _pattern-library/11_long-form-structured-text.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BORDER, TEXT_DARK,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Three structural failures, one root cause.",
        subtitle="How consulting decks get worse over the engagement, not better.",
        title_y=44,
        title_h=68,
        subtitle_h=22,
        brand_rule_w=56,
    )

    # Table grid: 56px numeral | 200px stage | rest body | column gap 28
    body_top = 220
    grid_left = 64
    num_w = 56
    stage_w = 200
    gap_w = 28
    body_w = 1280 - 128 - num_w - stage_w - 2 * gap_w  # = body col

    # Header row: 1.5px brand-primary bottom border
    header_y = body_top
    add_text(
        slide, "table-head-1", "#",
        x_px=grid_left, y_px=header_y, w_px=num_w, h_px=18,
        font_size_px=11, color=BRAND_PRIMARY_MID, bold=True, uppercase=True,
    )
    add_text(
        slide, "table-head-2", "STAGE",
        x_px=grid_left + num_w + gap_w, y_px=header_y, w_px=stage_w, h_px=18,
        font_size_px=11, color=BRAND_PRIMARY_MID, bold=True, uppercase=True,
    )
    add_text(
        slide, "table-head-3", "WHAT'S HAPPENING",
        x_px=grid_left + num_w + gap_w + stage_w + gap_w, y_px=header_y, w_px=body_w, h_px=18,
        font_size_px=11, color=BRAND_PRIMARY_MID, bold=True, uppercase=True,
    )
    # 1.5px brand-primary line
    add_rect(slide, "table-header-rule",
             x_px=grid_left, y_px=header_y + 24, w_px=1280 - 128, h_px=2, fill_color=BRAND_PRIMARY)

    # Rows
    rows = [
        ("01", "Situation",
         "Most consulting work starts strong — clear brief, fresh thinking, a partner who's bought in. The first week's deck reflects that clarity: a tight thesis, a single governing thought, and just enough evidence to carry it. Everyone leaves the kickoff aligned."),
        ("02", "Complication",
         "By week three, every stakeholder has touched a slide. The deck has tripled in length, lost its through-line, and added a new section called \"Appendix C: Detailed analysis.\" What started as an argument has become an archive."),
        ("03", "Question",
         "Why do decks degrade as the team learns more, instead of getting sharper? Every additional insight should make the thesis cleaner — yet the opposite happens, on every engagement, regardless of seniority or sector."),
        ("04", "Answer",
         "Because adding is faster than choosing. Every workstream contributes findings; nobody is paid to delete them. Reviewers ask \"what about X?\" and X gets added; nobody asks \"what should we cut?\" The deck becomes sediment, not synthesis."),
    ]
    rows_top = header_y + 36
    row_h = 88
    for i, (num, name, body) in enumerate(rows):
        n = i + 1
        ry = rows_top + i * row_h
        # Number
        add_text(
            slide, f"section-{n}-num", num,
            x_px=grid_left, y_px=ry + 4, w_px=num_w, h_px=28,
            font_size_px=22, color=BRAND_ACCENT, bold=True,
        )
        # Stage name
        add_text(
            slide, f"section-{n}-name", name.upper(),
            x_px=grid_left + num_w + gap_w, y_px=ry + 8, w_px=stage_w, h_px=24,
            font_size_px=14, color=BRAND_PRIMARY, bold=True, uppercase=True,
        )
        # Body
        add_text(
            slide, f"section-{n}-body", body,
            x_px=grid_left + num_w + gap_w + stage_w + gap_w, y_px=ry + 4,
            w_px=body_w, h_px=row_h - 12,
            font_size_px=12, color=TEXT_DARK,
        )
        # Separator (except last)
        if i < len(rows) - 1:
            add_rect(slide, f"section-{n}-sep",
                     x_px=grid_left, y_px=ry + row_h - 1, w_px=1280 - 128, h_px=1,
                     fill_color=CARD_BORDER)

    add_convergence(
        slide,
        "Slide Lab's job isn't to add ideas. It's to make subtraction faster than addition.",
    )

    add_footer(slide, page_num=11)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "11_long-form-structured-text.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
