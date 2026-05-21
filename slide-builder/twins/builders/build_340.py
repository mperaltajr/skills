"""
Builder for pattern 340: Dark Executive Briefing.

Source HTML: _pattern-library/340_dark-executive-briefing.html
Standalone — no light counterpart (new dark executive editorial style).

Layout: memo-header block on top, then title block, then 2-col body
(left: numbered Key Points · right: For Decision + Action Required cards).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
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

    # --- Canonical chrome ---
    add_text(slide, "title",
             "Strategic Rebalancing: <strong>Accelerating High-Margin Growth</strong>",
             x_px=64, y_px=20, w_px=1152, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Quarterly performance divergence requires immediate portfolio decisions across three business units",
             x_px=64, y_px=108, w_px=1100, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    # --- Memo header strip ---
    memo_y = 148
    memo_h = 60
    memo_bg = add_rect(slide, "memo-bg", 64, memo_y, 1152, memo_h, CARD_BG_DARK)
    memo_bg.line.color.rgb = CARD_BORDER_DARK
    memo_bg.line.width = 9525
    add_text(slide, "memo-type-label", "EXECUTIVE BRIEFING",
             x_px=80, y_px=memo_y + 8, w_px=200, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
             letter_spacing_px=1.5)
    # Meta grid: 2 rows × 2 cols of label/value
    meta_top = memo_y + 28
    meta_pairs = [
        ("TO:", "Global Leadership Committee", 80, meta_top),
        ("RE:", "Q2 Portfolio Rebalancing Initiative", 80, meta_top + 18),
        ("FROM:", "Chief Strategy Office", 640, meta_top),
        ("DATE:", "19 May 2026", 640, meta_top + 18),
    ]
    for i, (lbl, val, x, y) in enumerate(meta_pairs):
        add_text(slide, f"meta-label-{i+1}", lbl,
                 x_px=x, y_px=y, w_px=50, h_px=14,
                 font_size_px=11, color=TEXT_ON_DARK_FAINT, bold=False)
        add_text(slide, f"meta-value-{i+1}", val,
                 x_px=x + 56, y_px=y, w_px=420, h_px=14,
                 font_size_px=11, color=WHITE, bold=True)

    # --- Body: 2 cols ---
    body_top = 222
    body_bot = 660
    left_x = 64
    left_w = 700
    right_x = 784
    right_w = 432

    # LEFT — Key points
    add_text(slide, "kp-section-label", "KEY POINTS",
             x_px=left_x, y_px=body_top, w_px=left_w, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1.5)

    kp_data = [
        ("Revenue concentration risk has crossed threshold",
         "Top two clients now represent 41% of gross revenue, exceeding the 35% policy ceiling. Diversification action is required within 90 days."),
        ("Cloud & AI segment outperforms by 18 pts",
         "Margin in the Cloud & AI practice reached 34% vs. 16% portfolio average. Reallocation of BD resources can compound this advantage in H2."),
        ("Legacy managed services unit is diluting EBITDA",
         "Three legacy contracts running at negative margin due to scope creep. Renegotiation or structured exit paths are modeled in the appendix."),
        ("Talent pipeline aligned to wrong growth vector",
         "Current hiring plan adds 120 FTEs in declining-demand roles. Workforce plan revision can redirect $4.2M annually toward high-demand specialisms."),
    ]
    kp_top = body_top + 24
    kp_h = (body_bot - kp_top) // 4
    for i, (title, body) in enumerate(kp_data):
        n = i + 1
        ky = kp_top + i * kp_h
        # numbered circle
        add_rect(slide, f"kp-{n}-num-bg", left_x, ky + 4, 22, 22, BRAND_ACCENT)
        add_text(slide, f"kp-{n}-num", str(n),
                 x_px=left_x, y_px=ky + 4, w_px=22, h_px=22,
                 font_size_px=12, color=WHITE, bold=True, align="center",
                 anchor="middle")
        add_text(slide, f"kp-{n}-title", title,
                 x_px=left_x + 34, y_px=ky + 2, w_px=left_w - 40, h_px=18,
                 font_size_px=13, color=WHITE, bold=True)
        add_text(slide, f"kp-{n}-text", body,
                 x_px=left_x + 34, y_px=ky + 22, w_px=left_w - 40, h_px=kp_h - 26,
                 font_size_px=11, color=TEXT_ON_DARK_MID)

    # RIGHT — Decision + Action cards (split vertically)
    right_split_y = body_top + (body_bot - body_top) // 2 - 4

    def side_card(x, y, w, h, label, items, card_n):
        c = add_rect(slide, f"side-card-{card_n}", x, y, w, h, CARD_BG_DARK)
        c.line.color.rgb = CARD_BORDER_DARK
        c.line.width = 9525
        add_text(slide, f"side-card-{card_n}-label", label,
                 x_px=x + 16, y_px=y + 10, w_px=w - 32, h_px=14,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
                 uppercase=True, letter_spacing_px=1.5)
        add_rect(slide, f"side-card-{card_n}-rule", x + 16, y + 28, w - 32, 1,
                 CARD_BORDER_DARK)
        return items

    # For Decision card
    side_card(right_x, body_top, right_w, right_split_y - body_top - 8,
              "FOR DECISION", None, 1)
    decisions = [
        "Approve portfolio rebalancing framework and 90-day execution mandate",
        "Authorize BD resource shift: 60% allocation to Cloud & AI through Q3",
        "Ratify revised hiring plan — freeze legacy roles, open 40 AI/data positions",
    ]
    dec_top = body_top + 38
    dec_h = ((right_split_y - body_top - 8) - 46) // 3
    for i, txt in enumerate(decisions):
        dy = dec_top + i * dec_h
        # checkbox
        cb = add_rect(slide, f"decision-{i+1}-cb", right_x + 16, dy + 3, 12, 12,
                      CARD_BG_DARK)
        cb.line.color.rgb = TEXT_ON_DARK_FAINT
        cb.line.width = 12700
        add_text(slide, f"decision-{i+1}-text", txt,
                 x_px=right_x + 36, y_px=dy, w_px=right_w - 50, h_px=dec_h - 6,
                 font_size_px=11, color=WHITE)

    # Action Required card
    act_y = right_split_y
    act_h = body_bot - right_split_y
    side_card(right_x, act_y, right_w, act_h, "ACTION REQUIRED", None, 2)
    actions = [
        ("CSO", "Finalize rebalancing playbook and distribute to BU leads", "30 May"),
        ("CFO", "Model exit scenarios for three legacy contracts", "6 Jun"),
        ("CPO", "Submit revised workforce plan with cost delta analysis", "13 Jun"),
    ]
    act_top = act_y + 38
    a_h = (act_h - 46) // 3
    for i, (owner, txt, due) in enumerate(actions):
        ay = act_top + i * a_h
        # owner circle
        add_rect(slide, f"action-{i+1}-owner-bg", right_x + 16, ay + 2, 22, 22,
                 BRAND_PRIMARY_MID)
        add_text(slide, f"action-{i+1}-owner", owner,
                 x_px=right_x + 16, y_px=ay + 2, w_px=22, h_px=22,
                 font_size_px=8, color=WHITE, bold=True, align="center",
                 anchor="middle")
        add_text(slide, f"action-{i+1}-text", txt,
                 x_px=right_x + 46, y_px=ay + 2, w_px=right_w - 130, h_px=22,
                 font_size_px=11, color=TEXT_ON_DARK_MID, anchor="middle")
        # deadline pill
        pill_w = 60
        pill = add_rect(slide, f"action-{i+1}-due-bg",
                        right_x + right_w - pill_w - 16, ay + 4, pill_w, 18,
                        RGBColor(0x4A, 0x1E, 0x6E))
        pill.line.color.rgb = BRAND_ACCENT
        pill.line.width = 9525
        add_text(slide, f"action-{i+1}-due", due,
                 x_px=right_x + right_w - pill_w - 16, y_px=ay + 4,
                 w_px=pill_w, h_px=18,
                 font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True,
                 align="center", anchor="middle")

    # Invariant zone
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "340",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = (Path(__file__).resolve().parents[2] / "_renders" / "twins" /
           "340_dark-executive-briefing.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
