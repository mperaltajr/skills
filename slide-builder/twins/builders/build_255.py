"""
Builder for pattern 255: Risk-adjusted recommendation.

Source HTML: _pattern-library/255_risk-adjusted-recommendation.html

Layout: title block + top section (recommendation box ~65% wide + risk panel ~35%) +
bottom section with 3 evidence cards.
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
        title="Proceed now — the <strong>cost of delay exceeds the risk</strong> of acting.",
        subtitle="Risk-adjusted analysis across three independent evidence streams. Mitigation actions are confirmed and owner-assigned before launch.",
    )

    # Body area
    body_top = 230
    body_bottom = 635
    left_x = 48
    right_x = 1280 - 48
    body_w = right_x - left_x

    # Top section split (65 / 35) with gap
    top_h = 250
    gap = 16
    rec_w = int((body_w - gap) * 0.65)
    risk_w = body_w - gap - rec_w

    # --- Recommendation box (left) ---
    rec_x = left_x
    rec_y = body_top
    rec = add_rect(slide, "recommendation-box", rec_x, rec_y, rec_w, top_h, CARD_BG)
    rec.line.color.rgb = CARD_BORDER
    rec.line.width = 9525
    # Left brand accent stripe
    add_rect(slide, "rec-accent", rec_x, rec_y, 4, top_h, BRAND_ACCENT)

    add_text(
        slide, "we-recommend-label", "WE RECOMMEND",
        x_px=rec_x + 20, y_px=rec_y + 14, w_px=rec_w - 40, h_px=14,
        font_size_px=10, color=BRAND_ACCENT, bold=True,
        letter_spacing_px=1.6, uppercase=True,
    )
    add_text(
        slide, "recommendation-statement",
        "Launch the cost-reduction program in Q3 2026 with a phased diagnostic-first approach, gated at 6 weeks.",
        x_px=rec_x + 20, y_px=rec_y + 34, w_px=rec_w - 40, h_px=64,
        font_size_px=18, color=BRAND_PRIMARY, bold=True,
    )
    add_text(
        slide, "recommendation-rationale",
        "The diagnostic phase de-risks the full commitment: it surfaces detailed savings by sub-category, confirms ownership and governance, and delivers a 6-week payback on its own spend. Delaying to Q4 surrenders >$3.5M in identified run-rate savings and compresses the implementation window. Comparable programs across the portfolio consistently cleared their savings targets — the evidence base is strong enough to act.",
        x_px=rec_x + 20, y_px=rec_y + 108, w_px=rec_w - 40, h_px=top_h - 120,
        font_size_px=11, color=TEXT_DARK,
    )

    # --- Risk panel (right) ---
    risk_x = rec_x + rec_w + gap
    risk_y = body_top
    risk = add_rect(slide, "risk-panel", risk_x, risk_y, risk_w, top_h, BRAND_PRIMARY)

    add_text(
        slide, "risk-panel-header", "KEY RISKS & MITIGATIONS",
        x_px=risk_x + 16, y_px=risk_y + 12, w_px=risk_w - 32, h_px=18,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
        letter_spacing_px=1.4, uppercase=True,
    )

    risks = [
        ("Change-readiness gap",
         "Executive sponsor confirmed; change-management workstream scoped in Week 1 with dedicated lead."),
        ("Savings realisation slippage",
         "Gate review at Week 6 hard-stops full rollout if diagnostic yields fall below 70% of model."),
        ("Resource contention",
         "Diagnostic team ring-fenced; no competing priorities until gate. Backfill approved by PMO."),
    ]
    risk_top = risk_y + 38
    risk_inner_h = top_h - 50
    item_h = risk_inner_h // 3
    for i, (name, mit) in enumerate(risks):
        n = i + 1
        iy = risk_top + i * item_h
        add_text(
            slide, f"risk-{n}-name", name,
            x_px=risk_x + 16, y_px=iy + 4, w_px=risk_w - 32, h_px=18,
            font_size_px=11, color=WHITE, bold=True,
        )
        add_text(
            slide, f"risk-{n}-mit", mit,
            x_px=risk_x + 16, y_px=iy + 24, w_px=risk_w - 32, h_px=item_h - 28,
            font_size_px=9, color=BRAND_ACCENT_SOFT,
        )

    # --- Bottom: evidence cards ---
    ev_top = body_top + top_h + 18
    ev_bottom = body_bottom
    ev_h = ev_bottom - ev_top
    add_text(
        slide, "evidence-label", "SUPPORTING EVIDENCE",
        x_px=left_x, y_px=ev_top, w_px=400, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY, bold=True,
        letter_spacing_px=1.6, uppercase=True,
    )
    cards_top = ev_top + 22
    cards_h = ev_h - 22
    card_gap = 12
    card_w = (body_w - 2 * card_gap) // 3
    evidence = [
        ("$14M identified savings", " across seven sub-categories in the opportunity model, validated against FY25 actuals by internal finance."),
        ("92% of comparable programs", " delivered at or above their savings target when launched within the Q3 window in prior engagements."),
        ("6-week payback", " on diagnostic investment based on conservative 40% realisation rate; full-program IRR exceeds 8× over 24 months."),
    ]
    for i, (head, tail) in enumerate(evidence):
        n = i + 1
        cx = left_x + i * (card_w + card_gap)
        card = add_rect(slide, f"evidence-card-{n}", cx, cards_top, card_w, cards_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        add_rect(slide, f"evidence-card-{n}-accent", cx, cards_top, 3, cards_h, BRAND_ACCENT)
        add_text(
            slide, f"evidence-card-{n}-text",
            f"<strong>{head}</strong>{tail}",
            x_px=cx + 14, y_px=cards_top + 10, w_px=card_w - 28, h_px=cards_h - 20,
            font_size_px=11, color=TEXT_DARK, emphasis_color=BRAND_PRIMARY,
        )

    add_footer(slide, page_num=255)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "255_risk-adjusted-recommendation.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
