"""
Dark variant of pattern 46: Two-tier phase + detail.

Source HTML: _pattern-library/46_two-tier-phase-detail-dark.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

TINT_ACCENT = RGBColor(0x4A, 0x29, 0x6D)
TINT_MID = RGBColor(0x42, 0x24, 0x66)
TINT_PRIMARY = RGBColor(0x37, 0x1A, 0x55)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "eyebrow", "How the skill works",
        x_px=48, y_px=50, w_px=900, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
        letter_spacing_px=2, uppercase=True,
    )
    add_text(
        slide, "title",
        "Two skills, one workflow: the thinking is locked before a single slide is designed.",
        x_px=48, y_px=66, w_px=1100, h_px=58,
        font_size_px=22, color=WHITE, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Three sequential phases — structure, design, deliver. MDs read the chevrons; analysts read the detail underneath.",
        x_px=48, y_px=128, w_px=1100, h_px=32,
        font_size_px=12, color=TEXT_ON_DARK_MID,
    )
    add_rect(slide, "brand-rule", x_px=48, y_px=170, w_px=56, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    c_top = 198
    c_left = 48
    c_w = 1280 - 96

    tier1_h = 64
    chev_w = c_w // 3
    chev_colors = [BRAND_ACCENT_SOFT, BRAND_PRIMARY_MID, BRAND_ACCENT]
    chev_eyebrows = ["slide-helper", "slide-builder", "slide-builder"]
    chev_names = ["STRUCTURE", "DESIGN", "DELIVER"]

    for i in range(3):
        n = i + 1
        cx = c_left + i * chev_w
        add_rect(slide, f"step-{n}-header", cx, c_top, chev_w, tier1_h, chev_colors[i])
        add_rect(slide, f"step-{n}-num-bg", cx + 16, c_top + 14, 34, 34, BRAND_PRIMARY)
        add_text(
            slide, f"step-{n}-num", str(n),
            x_px=cx + 16, y_px=c_top + 14, w_px=34, h_px=34,
            font_size_px=14, color=WHITE, bold=True, align="center", anchor="middle",
        )
        # text color: dark on accent-soft (light), white on others
        head_text_color = BRAND_PRIMARY if i == 0 else WHITE
        eyebrow_color = BRAND_PRIMARY if i == 0 else RGBColor(0xE0, 0xE0, 0xE0)
        add_text(
            slide, f"step-{n}-eyebrow", chev_eyebrows[i],
            x_px=cx + 60, y_px=c_top + 12, w_px=chev_w - 80, h_px=14,
            font_size_px=9, color=eyebrow_color, bold=True,
            letter_spacing_px=1.4, uppercase=True,
        )
        add_text(
            slide, f"step-{n}-name", chev_names[i],
            x_px=cx + 60, y_px=c_top + 28, w_px=chev_w - 80, h_px=24,
            font_size_px=18, color=head_text_color, bold=True,
            letter_spacing_px=0.4,
        )

    tier2_top = c_top + tier1_h + 12
    tier2_h = 720 - 76 - tier2_top
    panel_w = (c_w - 24) // 3

    activities = [
        ([
            ("1", "Template intake — drop your client .pptx; fonts, colors, layouts read automatically."),
            ("2", "Opening question — what are you trying to communicate? starts the structured conversation."),
            ("3", "Audience + assumed knowledge — who sees it and what they already know going in."),
            ("4", "Infer + confirm — page type, mode and governing thought reflected back, then confirmed."),
            ("5", "Deepen structure — 2-4 supporting buckets, evidence and risks locked in."),
        ], "→ Structured brief produced (complete handoff document)"),
        ([
            ("6", "Reads brief + design rules — applies MBB slide conventions and page-type rules."),
            ("7", "Generates 3-4 visual mockup variations — each a structurally distinct layout bet."),
            ("8", "You select + refine — react, combine options or request changes; nothing locks until approved."),
        ], "→ Approved mockup produced (visual structure + content confirmed)"),
        ([
            ("9", "Builds slide in PPTX XML — uses your exact client template: fonts, colors, placeholder positions."),
            ("10", "QA'd as PDF before delivery — checked for overlaps, font errors, leftover placeholder text."),
            ("11", "Delivered to your folder — clickable file link, opens in PowerPoint, ready to present."),
        ], "→ Finished .pptx on your client template"),
    ]

    panel_colors = [BRAND_ACCENT_SOFT, BRAND_PRIMARY_MID, BRAND_ACCENT]
    panel_tints = [TINT_ACCENT, TINT_MID, TINT_PRIMARY]

    for i, (acts, output) in enumerate(activities):
        n = i + 1
        px = c_left + i * (panel_w + 12)
        panel_color = panel_colors[i]
        panel = add_rect(slide, f"step-{n}-panel", px, tier2_top, panel_w, tier2_h, CARD_BG_DARK)
        panel.line.color.rgb = CARD_BORDER_DARK
        panel.line.width = 9525
        add_rect(slide, f"step-{n}-panel-accent", px, tier2_top, panel_w, 3, panel_color)

        add_text(
            slide, f"step-{n}-activities-label", "WHAT HAPPENS IN THIS PHASE",
            x_px=px + 16, y_px=tier2_top + 14, w_px=panel_w - 32, h_px=14,
            font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True,
            letter_spacing_px=1.4, uppercase=True,
        )
        add_rect(slide, f"step-{n}-eyebrow-rule", px + 16, tier2_top + 32, panel_w - 32, 1, CARD_BORDER_DARK)

        acts_top = tier2_top + 44
        acts_area_h = tier2_h - 44 - 56
        act_row_h = acts_area_h // len(acts)

        for ai, (num, text) in enumerate(acts):
            an = ai + 1
            ay = acts_top + ai * act_row_h
            add_rect(slide, f"step-{n}-activity-{an}-num", px + 14, ay + 4, 22, 22, panel_color)
            num_text_color = BRAND_PRIMARY if i == 0 else WHITE
            add_text(
                slide, f"step-{n}-activity-{an}-num-text", num,
                x_px=px + 14, y_px=ay + 4, w_px=22, h_px=22,
                font_size_px=10, color=num_text_color, bold=True, align="center", anchor="middle",
            )
            add_text(
                slide, f"step-{n}-activity-{an}-text", text,
                x_px=px + 44, y_px=ay, w_px=panel_w - 60, h_px=act_row_h,
                font_size_px=11, color=WHITE,
            )

        out_y = tier2_top + tier2_h - 44
        add_rect(slide, f"step-{n}-output-bg", px + 8, out_y, panel_w - 16, 36, panel_tints[i])
        add_rect(slide, f"step-{n}-output-accent", px + 8, out_y, 3, 36, panel_color)
        add_text(
            slide, f"step-{n}-output", output,
            x_px=px + 18, y_px=out_y + 8, w_px=panel_w - 32, h_px=22,
            font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True,
        )

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(
        slide, "source", "Source: [add source here or delete]",
        x_px=58, y_px=688, w_px=1100, h_px=16,
        font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True,
    )
    add_text(
        slide, "page-number", "46",
        x_px=1170, y_px=688, w_px=52, h_px=16,
        font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right",
    )
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "46d_two-tier-phase-detail.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
