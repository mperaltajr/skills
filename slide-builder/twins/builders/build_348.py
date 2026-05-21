"""
Builder for pattern 348: Dark Key Messages by Audience.

Source HTML: _pattern-library/348_dark-key-messages-audience.html
Standalone — closest light reference: 194d_key-messages-per-audience.

Layout: 4 audience columns (Board · C-Suite · Operations · Front-Line),
each with header (audience + descriptor), 3 message cards with bold intros,
and a channel chip at the bottom.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title
    add_text(slide, "title",
             "Key messages <strong>tailored by audience</strong>",
             x_px=64, y_px=20, w_px=1152, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Stakeholder communication framework — transformation programme",
             x_px=64, y_px=108, w_px=1100, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    # 4-column grid
    body_y = 160
    body_h = 500
    gap = 12
    col_w = (1152 - 3 * gap) // 4

    cols = [
        ("Board", "Non-executive directors & trustees", "Board Pack", [
            ("Strategic value unlocked", " — the programme delivers £42M in run-rate savings by FY27, ahead of peer benchmarks."),
            ("Risk exposure reduced", " — legacy tech debt eliminated across four critical systems, cutting regulatory exposure."),
            ("Governance milestones", " on track — Stage Gate 2 passed with zero red risks; next review 14 Jun."),
        ]),
        ("C-Suite", "CEO, CFO, COO & function leads", "SteerCo Deck", [
            ("Delivery confidence high", " — RAG status green across all workstreams; budget consumed at 94% planned rate."),
            ("Capability investment", " accelerating — 340 staff upskilled in Q1; talent gap closes by Q3 2026."),
            ("Decision needed by 30 May", " on vendor contract extension — options paper circulated for approval."),
        ]),
        ("Operations", "Managers & team leads", "Town Hall", [
            ("New platform live", " in Regions 1–3 from 2 Jun — runbooks and support contacts issued to all leads."),
            ("Process changes mapped", " — six workflows updated; change impact matrix available on SharePoint."),
            ("Escalation path clear", " — issues raised via ServiceNow queue, SLA 4 hrs for Sev-1 during cutover."),
        ]),
        ("Front-Line", "Individual contributors & agents", "Email / Teams", [
            ("Your role is changing", " — new tools replace two manual steps; training sessions run Tue & Thu this week."),
            ("Support is available", " — floor walkers on site 6–10 Jun; Teams channel #transformation-help open 24/7."),
            ("Feedback matters", " — pulse survey open until 20 Jun; results shared back within two weeks."),
        ]),
    ]

    for i, (aud, desc, chip, messages) in enumerate(cols):
        x = 64 + i * (col_w + gap)
        # Header card
        add_text(slide, f"col-{i+1}-aud", aud,
                 x_px=x + 4, y_px=body_y, w_px=col_w - 8, h_px=24,
                 font_size_px=16, color=WHITE, bold=True)
        add_text(slide, f"col-{i+1}-desc", desc,
                 x_px=x + 4, y_px=body_y + 24, w_px=col_w - 8, h_px=16,
                 font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
        # Accent under header
        add_rect(slide, f"col-{i+1}-rule", x + 4, body_y + 44, 32, 2, BRAND_ACCENT_SOFT)
        # Message cards
        cards_top = body_y + 56
        card_h = 116
        gap_card = 8
        for j, (intro, rest) in enumerate(messages):
            cy = cards_top + j * (card_h + gap_card)
            c = add_rect(slide, f"col-{i+1}-msg-{j+1}-bg", x, cy, col_w, card_h, CARD_BG_DARK)
            c.line.color.rgb = CARD_BORDER_DARK
            c.line.width = 9525
            add_rect(slide, f"col-{i+1}-msg-{j+1}-strip", x, cy, 3, card_h, BRAND_ACCENT)
            add_text(slide, f"col-{i+1}-msg-{j+1}-text", f"<strong>{intro}</strong>{rest}",
                     x_px=x + 14, y_px=cy + 8, w_px=col_w - 22, h_px=card_h - 16,
                     font_size_px=11, color=TEXT_ON_DARK_MID,
                     emphasis_color=WHITE)
        # Channel chip at bottom
        chip_y = cards_top + 3 * (card_h + gap_card) + 4
        chip_w = 132
        cp = add_rect(slide, f"col-{i+1}-chip-bg", x, chip_y, chip_w, 24,
                      CARD_BG_DARK)
        cp.line.color.rgb = BRAND_ACCENT_SOFT
        cp.line.width = 6350
        add_text(slide, f"col-{i+1}-chip", chip,
                 x_px=x, y_px=chip_y, w_px=chip_w, h_px=24,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
                 align="center", anchor="middle", uppercase=True,
                 letter_spacing_px=1.2)

    # Invariant zone
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "348",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = (Path(__file__).resolve().parents[2] / "_renders" / "twins" /
           "348_dark-key-messages-audience.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
