"""
Builder for pattern 94: Change readiness assessment (ADKAR 5 stages + readiness bar).

Source HTML: _pattern-library/94_change-readiness-assessment.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block, add_convergence,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

STATUS_GREEN = RGBColor(0x16, 0xA3, 0x4A)
STATUS_GREEN_SOFT = RGBColor(0xDC, 0xFC, 0xE7)
STATUS_AMBER = RGBColor(0xF5, 0x9E, 0x0B)
STATUS_AMBER_SOFT = RGBColor(0xFE, 0xF3, 0xC7)
STATUS_RED = RGBColor(0xDC, 0x26, 0x26)
STATUS_RED_SOFT = RGBColor(0xFE, 0xE2, 0xE2)
DOT_OFF = RGBColor(0xED, 0xE2, 0xF6)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Wave 2 change readiness — awareness is there, ability isn't.",
        subtitle="ADKAR scoring across the consulting org: people know Slide Lab exists and roughly half want it, but knowledge and ability gaps will stall adoption unless coaching and reinforcement land before Wave 2 kicks off.",
        title_x=56, title_w=1168, title_h=60,
        subtitle_h=44,
        brand_rule_w=56,
    )

    # Framework label strip — pushed below the brand-rule so the 3px rule
    # doesn't strike through the eyebrow text.
    add_text(
        slide, "eyebrow",
        "ADKAR readiness model · N = 142 respondents · survey + manager interviews, Apr 2026",
        x_px=56, y_px=200, w_px=1168, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, uppercase=True,
    )

    # 5 stage cards
    stage_top = 220
    stages_left = 56
    stages_right = 1280 - 56
    stages_w = stages_right - stages_left
    gap = 14
    card_w = (stages_w - gap * 4) // 5
    card_h = 332

    stages = [
        ("A", "Awareness", "Know the change is happening and why.", 4,
         "green", "On track",
         "Most consultants know Slide Lab exists; town hall and MD email drove broad reach."),
        ("D", "Desire", "Want to participate and support the change.", 3,
         "amber", "Watch",
         "~50% actively want it; the other half see it as \"another tool\" on top of existing workflow."),
        ("K", "Knowledge", "Know how to change — the skills and steps.", 2,
         "red", "Gap",
         "Only the 14 champions know how it actually works; no enablement materials yet for the broader org."),
        ("A", "Ability", "Can demonstrate the change in real work.", 2,
         "red", "Gap",
         "Low — first attempts stall on framing and briefs; needs structured coaching, not just docs."),
        ("R", "Reinforcement", "Sustain the change — recognition, metrics, rituals.", 2,
         "red", "Gap",
         "Scoreboard exists but nobody watches it; no MD recognition tied to Slide Lab usage."),
    ]

    for i, (letter, name, definition, score, color_kind, status_label, obs) in enumerate(stages):
        n = i + 1
        cx = stages_left + i * (card_w + gap)
        card = add_rect(slide, f"stage-{n}", cx, stage_top, card_w, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Top accent strip (4px)
        add_rect(slide, f"stage-{n}-accent", cx, stage_top, card_w, 4, BRAND_ACCENT)

        # Big letter
        add_text(slide, f"stage-{n}-letter", letter,
                 x_px=cx + 14, y_px=stage_top + 16, w_px=70, h_px=60,
                 font_size_px=56, color=BRAND_ACCENT, bold=True)
        # Name
        add_text(slide, f"stage-{n}-name", name,
                 x_px=cx + 14, y_px=stage_top + 84, w_px=card_w - 28, h_px=18,
                 font_size_px=13, color=BRAND_PRIMARY, bold=True, uppercase=True)
        # Definition
        add_text(slide, f"stage-{n}-definition", definition,
                 x_px=cx + 14, y_px=stage_top + 104, w_px=card_w - 28, h_px=40,
                 font_size_px=11, color=TEXT_MID)

        # Meter label
        add_text(slide, f"stage-{n}-meter-label", "CURRENT LEVEL",
                 x_px=cx + 14, y_px=stage_top + 152, w_px=card_w - 28, h_px=14,
                 font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True)
        # 5 dots
        dot_top = stage_top + 170
        for j in range(5):
            dx = cx + 14 + j * 19
            dot_color = BRAND_ACCENT if j < score else DOT_OFF
            add_rect(slide, f"stage-{n}-meter-dot-{j+1}",
                     dx, dot_top, 14, 14, dot_color)
        # Aggregate meter id
        add_rect(slide, f"stage-{n}-meter", cx + 14, dot_top, 14*5 + 4*5, 14,
                 RGBColor(0xFF, 0xFF, 0xFF))  # transparent stand-in (won't render visibly over dots)
        # Score
        add_text(slide, f"stage-{n}-score", f"{score} / 5",
                 x_px=cx + 14, y_px=dot_top + 22, w_px=card_w - 28, h_px=16,
                 font_size_px=11, color=BRAND_PRIMARY_MID, bold=True)

        # Status row
        if color_kind == "green":
            sbg, stxt, spip = STATUS_GREEN_SOFT, STATUS_GREEN, STATUS_GREEN
        elif color_kind == "amber":
            sbg, stxt, spip = STATUS_AMBER_SOFT, RGBColor(0xB4, 0x53, 0x09), STATUS_AMBER
        else:
            sbg, stxt, spip = STATUS_RED_SOFT, STATUS_RED, STATUS_RED
        status_y = dot_top + 48
        add_rect(slide, f"stage-{n}-status",
                 cx + 14, status_y, card_w - 28, 22, sbg)
        add_rect(slide, f"stage-{n}-status-pip",
                 cx + 22, status_y + 6, 10, 10, spip)
        add_text(slide, f"stage-{n}-status-label", status_label,
                 x_px=cx + 36, y_px=status_y + 3, w_px=card_w - 50, h_px=16,
                 font_size_px=10, color=stxt, bold=True, uppercase=True)

        # Observation (bottom)
        obs_y = status_y + 36
        add_rect(slide, f"stage-{n}-obs-divider",
                 cx + 14, obs_y - 4, card_w - 28, 1, CARD_BORDER)
        add_text(slide, f"stage-{n}-observation", obs,
                 x_px=cx + 14, y_px=obs_y, w_px=card_w - 28, h_px=70,
                 font_size_px=10, color=TEXT_DARK)

    # Overall readiness strip
    rs_y = 720 - 128 - 56
    rs_h = 56
    rs = add_rect(slide, "readiness-strip", 56, rs_y, 1280 - 112, rs_h, WHITE)
    rs.line.color.rgb = CARD_BORDER
    rs.line.width = 9525

    add_text(slide, "readiness-label", "OVERALL READINESS",
             x_px=72, y_px=rs_y + 8, w_px=200, h_px=14,
             font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, uppercase=True)
    add_text(slide, "readiness-score", "65%",
             x_px=72, y_px=rs_y + 22, w_px=200, h_px=30,
             font_size_px=26, color=BRAND_PRIMARY, bold=True)

    # Readiness bar
    bar_x = 280
    bar_w = 740
    bar_y = rs_y + 22
    bar_h = 14
    add_rect(slide, "readiness-bar-track", bar_x, bar_y, bar_w, bar_h, DOT_OFF)
    add_rect(slide, "readiness-bar-fill", bar_x, bar_y, int(bar_w * 0.65), bar_h, BRAND_ACCENT)
    # Ticks under bar
    for j, lab in enumerate(["0%", "25%", "50%", "75%", "100%"]):
        tx = bar_x + int(bar_w * j / 4)
        add_text(slide, f"readiness-tick-{j+1}", lab,
                 x_px=tx - 16, y_px=bar_y + bar_h + 2, w_px=32, h_px=12,
                 font_size_px=9, color=TEXT_FAINT, bold=True, align="center")

    # Verdict (right)
    add_text(slide, "readiness-verdict", "NEEDS WORK",
             x_px=1280 - 56 - 160, y_px=rs_y + 16, w_px=140, h_px=24,
             font_size_px=12, color=STATUS_AMBER, bold=True, align="center", uppercase=True,
             bg_fill=STATUS_AMBER_SOFT, padding_px=(4, 8, 4, 8))

    add_convergence(
        slide,
        "Awareness is solved; the next 6 weeks have to move K, A, and R from red to amber — or Wave 2 launches into an org that can't actually use the tool.",
        bottom_px=60, height_px=42,
    )

    add_footer(slide, page_num=94)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "94_change-readiness-assessment.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
