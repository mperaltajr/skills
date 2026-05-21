"""
Builder for pattern 298: Leadership team profiles (4-card grid with avatars).

Source HTML: _pattern-library/298_leadership-team-profiles.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.enum.shapes import MSO_SHAPE
from twins.helpers import px_to_emu


def _add_avatar_circle(slide, name, x, y, size, initials):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        px_to_emu(x), px_to_emu(y),
        px_to_emu(size), px_to_emu(size),
    )
    shape.name = f"{name}-circle"
    shape.fill.solid()
    shape.fill.fore_color.rgb = BRAND_PRIMARY_MID
    shape.line.fill.background()
    add_text(
        slide, f"{name}-initials", initials,
        x_px=x, y_px=y, w_px=size, h_px=size,
        font_size_px=24, color=WHITE, bold=True,
        align="center", anchor="middle",
    )


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Meet the <strong>Leadership Team</strong>",
        subtitle="Senior leaders driving transformation across the programme",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    cards = [
        ("SR", "Sarah Reynolds", "Chief Transformation Officer",
         ["Owns end-to-end delivery roadmap and executive alignment",
          "Chairs weekly steering committee and risk reviews"],
         "MBA Harvard · 18yr exp"),
        ("MK", "Marcus Klein", "Programme Director, Technology",
         ["Leads platform architecture and vendor governance",
          "Manages cross-stream dependency resolution"],
         "MSc MIT · 14yr exp"),
        ("LP", "Lena Park", "Head of Change & Adoption",
         ["Designs change impact assessments and comms strategy",
          "Drives stakeholder engagement and training rollout"],
         "MA Org Psychology · 11yr exp"),
        ("JO", "James Okafor", "Finance & Benefits Lead",
         ["Tracks business case and benefits realisation reporting",
          "Manages programme budget and cost governance"],
         "CFA · MBA Wharton · 15yr exp"),
    ]

    grid_top = 184
    grid_left = 48
    gap = 18
    card_w = (1280 - 96 - 3 * gap) // 4  # 277
    card_h = 460

    for i, (initials, name, role, bullets, tag) in enumerate(cards):
        n = i + 1
        cx = grid_left + i * (card_w + gap)
        cy = grid_top
        card = add_rect(slide, f"profile-{n}-card", cx, cy, card_w, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525

        # Avatar centered horizontally
        av_size = 76
        av_x = cx + (card_w - av_size) // 2
        av_y = cy + 24
        _add_avatar_circle(slide, f"profile-{n}-avatar", av_x, av_y, av_size, initials)

        # Name
        add_text(
            slide, f"profile-{n}-name", name,
            x_px=cx + 20, y_px=av_y + av_size + 14, w_px=card_w - 40, h_px=22,
            font_size_px=15, color=BRAND_PRIMARY, bold=True,
        )
        # Role
        add_text(
            slide, f"profile-{n}-role", role,
            x_px=cx + 20, y_px=av_y + av_size + 38, w_px=card_w - 40, h_px=36,
            font_size_px=12, color=TEXT_MID, italic=True,
        )
        # Divider
        add_rect(slide, f"profile-{n}-divider", cx + 20, av_y + av_size + 80, card_w - 40, 1, CARD_BORDER)
        # Responsibilities
        bullets_y = av_y + av_size + 92
        for bi, b in enumerate(bullets):
            bn = bi + 1
            # bullet dot
            add_rect(slide, f"profile-{n}-bullet-{bn}-dot",
                     cx + 22, bullets_y + bi * 56 + 6, 3, 3, BRAND_ACCENT)
            add_text(
                slide, f"profile-{n}-bullet-{bn}", b,
                x_px=cx + 32, y_px=bullets_y + bi * 56,
                w_px=card_w - 52, h_px=52,
                font_size_px=11, color=TEXT_MID,
            )
        # Background tag chip
        tag_y = cy + card_h - 30
        tag_h = 18
        tag_text_w = min(card_w - 40, len(tag) * 6 + 16)
        tag_x = cx + 20
        chip = add_rect(slide, f"profile-{n}-tag", tag_x, tag_y, tag_text_w, tag_h, CARD_BORDER)
        chip.line.fill.background()
        add_text(
            slide, f"profile-{n}-tag-text", tag,
            x_px=tag_x, y_px=tag_y, w_px=tag_text_w, h_px=tag_h,
            font_size_px=9, color=TEXT_MID, align="center", anchor="middle",
            padding_px=(0, 8, 0, 8),
        )

    add_footer(slide, page_num=298)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "298_leadership-team-profiles.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
