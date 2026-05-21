"""
Builder for pattern 41: Persona card.

Single large persona card. Left zone: photo + name + role + rule + chips +
skill dots. Right zone: goals bullets + pains bullets + quote.

Pattern-local IDs: persona-chip-N, persona-skill-N-name, persona-skill-N-dots.

Source HTML: _pattern-library/41_persona-card.html
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
from pptx.dml.color import RGBColor

GOAL_ACCENT = RGBColor(0x16, 0xA3, 0x4A)
PAIN_ACCENT = RGBColor(0xDC, 0x26, 0x26)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Who Slide Lab is built for — Sarah, Senior Manager.",
        subtitle="Every design decision answers to her workflow. If it doesn't move her week, it doesn't ship.",
        title_h=64,
        subtitle_h=22,
    )

    # Persona card: top=170, left=64, right=64, bottom=110 → 1152 × 440
    pc_left = 64
    pc_top = 170
    pc_w = 1280 - 128
    pc_h = 440

    pcard = add_rect(slide, "persona-card-bg", pc_left, pc_top, pc_w, pc_h, CARD_BG)
    pcard.line.color.rgb = CARD_BORDER
    pcard.line.width = 9525

    # Left zone (~360w)
    left_w = 360
    left_pad = 24
    lx = pc_left + left_pad
    ly = pc_top + left_pad

    # Photo placeholder (116x116 circle approximation)
    photo_w = 116
    photo_x = pc_left + (left_w - photo_w) // 2
    photo = add_rect(slide, "persona-photo", photo_x, ly, photo_w, photo_w, BRAND_PRIMARY)
    photo.line.color.rgb = BRAND_ACCENT
    photo.line.width = 19050  # 2px ring
    add_text(
        slide, "persona-photo-initials", "SK",
        x_px=photo_x, y_px=ly, w_px=photo_w, h_px=photo_w,
        font_size_px=40, color=WHITE, bold=True, align="center", anchor="middle",
    )

    # Name
    name_y = ly + photo_w + 16
    add_text(
        slide, "persona-name", "Sarah Kim",
        x_px=lx, y_px=name_y, w_px=left_w - 2 * left_pad, h_px=28,
        font_size_px=22, color=BRAND_PRIMARY, bold=True,
    )
    # Role
    add_text(
        slide, "persona-role", "Senior Manager, Strategy Practice",
        x_px=lx, y_px=name_y + 30, w_px=left_w - 2 * left_pad, h_px=18,
        font_size_px=12, color=TEXT_DARK, bold=True,
    )
    # Name rule
    add_rect(slide, "persona-name-rule", lx, name_y + 54, 40, 2, BRAND_ACCENT)

    # Chips (3)
    chips_y = name_y + 64
    chips_text = ["9 yrs consulting", "NYC office", "6 active engagements"]
    chip_x = lx
    for i, t in enumerate(chips_text):
        n = i + 1
        w = 100 if i == 0 else (80 if i == 1 else 140)
        # break to next row if needed
        if chip_x + w > lx + (left_w - 2 * left_pad):
            chip_x = lx
            chips_y += 22
        chip = add_rect(slide, f"persona-chip-{n}", chip_x, chips_y, w, 18,
                        RGBColor(0xF1, 0xE8, 0xFC))
        chip.line.color.rgb = CARD_BORDER
        chip.line.width = 9525
        add_text(
            slide, f"persona-chip-{n}-text", t,
            x_px=chip_x, y_px=chips_y, w_px=w, h_px=18,
            font_size_px=10, color=BRAND_PRIMARY, bold=True, align="center", anchor="middle",
        )
        chip_x += w + 5

    # Skills meter section (bottom of left zone)
    skills_top = pc_top + pc_h - 150
    add_rect(slide, "persona-skills-rule", lx, skills_top - 6, left_w - 2 * left_pad, 1, CARD_BORDER)
    add_text(
        slide, "persona-skills-label", "WHERE SHE LEANS IN",
        x_px=lx, y_px=skills_top, w_px=left_w - 2 * left_pad, h_px=12,
        font_size_px=9, color=TEXT_FAINT, bold=True,
        letter_spacing_px=1.6, uppercase=True,
    )

    skill_names = [
        "Storyline structure",
        "Client read",
        "Slide production speed",
        "Coaching juniors at scale",
    ]
    skill_filled = [5, 4, 3, 2]  # out of 5
    for i in range(4):
        n = i + 1
        sy = skills_top + 18 + i * 20
        add_text(
            slide, f"persona-skill-{n}-name", skill_names[i],
            x_px=lx, y_px=sy, w_px=200, h_px=16,
            font_size_px=10, color=TEXT_DARK,
        )
        # Dots (5 dots, 7px square, 3px gap)
        dots_x = lx + 200
        for di in range(5):
            dot_color = BRAND_ACCENT if di < skill_filled[i] else CARD_BORDER
            add_rect(slide, f"persona-skill-{n}-dot-{di+1}", dots_x + di * 10, sy + 4, 7, 7, dot_color)
        # Combined dots shape id reference
        # (no separate add_text for persona-skill-N-dots; the 5 dots collectively map)

    # Divider between left & right zones
    div_x = pc_left + left_w
    add_rect(slide, "persona-divider", div_x, pc_top, 1, pc_h, CARD_BORDER)

    # Right zone
    rx = div_x + 28
    rw = pc_w - left_w - 56
    ry = pc_top + 24

    # Goals zone
    g_h = 130
    add_text(
        slide, "persona-zone-goals-label", "● GOALS — WHAT SHE'S PUSHING TOWARD",
        x_px=rx, y_px=ry, w_px=rw, h_px=14,
        font_size_px=10, color=GOAL_ACCENT, bold=True,
        letter_spacing_px=1.8, uppercase=True,
    )
    goals = [
        "▲  Ship partner-ready decks in under 5 days",
        "▲  Develop juniors without slowing herself down",
        "▲  Win the partner promotion within 18 months",
    ]
    for gi, g in enumerate(goals):
        add_text(
            slide, f"persona-zone-goals-body-{gi+1}", g,
            x_px=rx, y_px=ry + 22 + gi * 22, w_px=rw, h_px=20,
            font_size_px=13, color=TEXT_DARK,
        )

    # Pains zone
    py = ry + g_h
    add_text(
        slide, "persona-zone-pains-label", "● PAIN POINTS — WHAT BURNS HER WEEK",
        x_px=rx, y_px=py, w_px=rw, h_px=14,
        font_size_px=10, color=PAIN_ACCENT, bold=True,
        letter_spacing_px=1.8, uppercase=True,
    )
    pains = [
        "▼  Reviews multiply through the engagement",
        "▼  Juniors hand her decks she has to rebuild",
        "▼  No framework for the storyline coaching she does on the fly",
    ]
    for pi, p in enumerate(pains):
        add_text(
            slide, f"persona-zone-pains-body-{pi+1}", p,
            x_px=rx, y_px=py + 22 + pi * 22, w_px=rw, h_px=20,
            font_size_px=13, color=TEXT_DARK,
        )

    # Quote zone (bottom of right column)
    qy = pc_top + pc_h - 88
    qh = 68
    add_rect(slide, "persona-quote-bg", rx - 8, qy, rw + 16, qh, BRAND_PRIMARY)
    add_text(
        slide, "quote-mark", "“",
        x_px=rx, y_px=qy - 18, w_px=40, h_px=40,
        font_size_px=44, color=BRAND_ACCENT, font_name="Georgia",
    )
    add_text(
        slide, "persona-quote",
        "I spend more time on slide structure than slide content. That's backwards.",
        x_px=rx + 32, y_px=qy + 14, w_px=rw - 180, h_px=40,
        font_size_px=14, color=WHITE, italic=True,
    )
    add_text(
        slide, "persona-quote-attr", "SARAH K. · WEEK 2",
        x_px=rx + rw - 140, y_px=qy + 24, w_px=140, h_px=20,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
        letter_spacing_px=1.4, uppercase=True, align="right",
    )

    add_footer(slide, page_num=41)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "41_persona-card.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
