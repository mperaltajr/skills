"""
Builder for pattern 202: Biography Card (Two-Person split panel).

Two persona cards side by side, divided by brand-accent vertical rule.

Source HTML: _pattern-library/202_biography-card-two-person.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Leadership <strong>Profiles</strong>",
        subtitle="Meet the team driving transformation across the engagement",
        title_h=42, subtitle_h=20, brand_rule_w=64,
    )

    body_top = 158
    body_bot = 624
    body_h = body_bot - body_top
    divider_w = 16
    panel_w = (1280 - 128 - divider_w) // 2

    panels = [
        ("SA", "Sarah Alvarez", "Managing Director, Strategy & Consulting",
         "Sarah leads large-scale transformation programs for global financial services clients, with over 18 years of experience spanning operating model redesign, digital strategy, and organizational change. She has delivered programs across North America, Europe, and Asia-Pacific, consistently accelerating time-to-value through agile delivery frameworks.",
         [("18+", "Years"), ("40+", "Programs"), ("12", "Countries")],
         ["Operating Model", "Digital Strategy", "Change Management"]),
        ("MR", "Marcus Reid", "Senior Principal, Technology & Innovation",
         "Marcus specializes in enterprise AI adoption and cloud architecture for regulated industries, bringing 14 years of hands-on delivery across banking, insurance, and public sector. He has led multi-year platform modernization programs and served as chief architect on three large-scale data platform builds for Fortune 100 clients.",
         [("14+", "Years"), ("3", "Platforms"), ("F100", "Clients")],
         ["Enterprise AI", "Cloud Architecture", "Data Platforms"]),
    ]

    # Center vertical divider
    div_x = 64 + panel_w + (divider_w - 2) // 2
    add_rect(slide, "vertical-divider", div_x, body_top, 2, body_h, BRAND_ACCENT)



    for i, (initials, name, role, bio, stats, tags) in enumerate(panels):
        n = i + 1
        px = 64 + i * (panel_w + divider_w)
        # Panel bg
        panel = add_rect(slide, f"persona-{n}-bg", px, body_top, panel_w, body_h, CARD_BG)
        panel.line.color.rgb = CARD_BORDER
        panel.line.width = 9525
        # Avatar circle (centered top)
        av_size = 90
        av_x = px + (panel_w - av_size) // 2
        av_y = body_top + 24
        add_rect(slide, f"persona-{n}-photo", av_x, av_y, av_size, av_size, BRAND_PRIMARY_MID)
        add_text(slide, f"persona-{n}-photo-initials", initials,
                 x_px=av_x, y_px=av_y, w_px=av_size, h_px=av_size,
                 font_size_px=28, color=WHITE, bold=True, align="center", anchor="middle")
        # Name
        add_text(slide, f"persona-{n}-name", name,
                 x_px=px + 16, y_px=av_y + av_size + 14, w_px=panel_w - 32, h_px=22,
                 font_size_px=18, color=BRAND_PRIMARY, bold=True, align="center")
        # Role
        add_text(slide, f"persona-{n}-role", role,
                 x_px=px + 16, y_px=av_y + av_size + 38, w_px=panel_w - 32, h_px=18,
                 font_size_px=13, color=BRAND_PRIMARY_MID, align="center")
        # Separator
        sep_w = 40
        add_rect(slide, f"persona-{n}-name-rule",
                 px + (panel_w - sep_w) // 2, av_y + av_size + 64,
                 sep_w, 2, BRAND_ACCENT)
        # Bio
        bio_y = av_y + av_size + 78
        add_text(slide, f"persona-{n}-bio", bio,
                 x_px=px + 20, y_px=bio_y, w_px=panel_w - 40, h_px=110,
                 font_size_px=10, color=TEXT_DARK)
        # Stats strip (3 numbers)
        stats_y = bio_y + 118
        stats_w = panel_w - 40
        cell_w = stats_w // 3
        for j, (num, label) in enumerate(stats):
            sx = px + 20 + j * cell_w
            add_text(slide, f"persona-{n}-stat-{j+1}-num", num,
                     x_px=sx, y_px=stats_y, w_px=cell_w, h_px=26,
                     font_size_px=20, color=BRAND_PRIMARY, bold=True, align="center")
            add_text(slide, f"persona-{n}-stat-{j+1}-label", label,
                     x_px=sx, y_px=stats_y + 28, w_px=cell_w, h_px=14,
                     font_size_px=9, color=TEXT_FAINT, bold=True, align="center", uppercase=True)
        # Expertise label
        exp_y = stats_y + 60
        add_text(slide, f"persona-{n}-expertise-label", "EXPERTISE",
                 x_px=px + 20, y_px=exp_y, w_px=panel_w - 40, h_px=14,
                 font_size_px=9, color=TEXT_MID, bold=True, uppercase=True)
        # Tags
        tag_y = exp_y + 22
        tag_x = px + 20
        for j, tag in enumerate(tags):
            tw = 130
            tx = tag_x + j * (tw + 6)
            add_text(slide, f"persona-{n}-tag-{j+1}", tag,
                     x_px=tx, y_px=tag_y, w_px=tw, h_px=20,
                     font_size_px=10, color=BRAND_PRIMARY, bold=True, align="center",
                     bg_fill=BRAND_ACCENT_SOFT, padding_px=(3, 8, 3, 8))

    add_footer(slide, page_num=202)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "202_biography-card-two-person.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
