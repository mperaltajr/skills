"""
Builder for pattern 287: Three-column key findings cards.

Source HTML: _pattern-library/287_three-col-key-findings.html

3 cards: finding number, headline, accent rule, bullet list, implication strip.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.dml.color import RGBColor

IMPL_BG = RGBColor(0xED, 0xE0, 0xF7)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Three critical gaps are <strong>widening the delivery risk</strong>",
        subtitle="Diagnostic summary · Phase 1 assessment · May 2026",
    )

    # 3 cards
    cards_x = 56
    cards_y = 234
    cards_w = 1280 - 112
    cards_h = 720 - cards_y - 44
    gap = 20
    card_w = (cards_w - gap * 2) // 3

    # Each bullet: (stat, text, suffix). stat may be None. If suffix is True,
    # the stat appears at end of text; otherwise stat is prefix.
    findings = [
        ("01", "Data quality issues upstream of every key report",
         [("34%", " of source records fail validation on first pass", False),
          (None, "3 of 5 upstream feeds have no lineage documentation", False),
          ("8–12 days", "Remediation SLA routinely missed by ", True),
          (None, "No automated alerting for schema drift events", False)],
         "Leadership dashboards carry unquantified error risk every reporting cycle."),
        ("02", "Ownership gaps create single points of failure",
         [("7 core processes", " have no documented owner as of Q1", False),
          (None, "2 critical system admins are the sole holders of access credentials", False),
          ("14+ weeks", "Onboarding time for replacements estimated at ", True),
          (None, "Cross-team escalation path undefined for P1 incidents", False)],
         "Any unplanned attrition in these roles carries a material continuity threat."),
        ("03", "Technology debt is accelerating faster than remediation",
         [("62%", " of the application portfolio is past end-of-support", False),
          ("2.3×", " the rate of retirement (new technical debt added)", False),
          (None, "Security patch cadence averages 47 days vs. 14-day target", False),
          (None, "Infrastructure modernisation budget reduced 18% YoY", False)],
         "Without reprioritisation, remediation cost will exceed the modernisation budget by FY28."),
    ]

    # Implication strip height
    impl_h = 64

    for ci, (num, headline, bullets, implication) in enumerate(findings):
        cx = cards_x + ci * (card_w + gap)
        # Card frame
        card = add_rect(slide, f"card-{ci+1}-bg", cx, cards_y, card_w, cards_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525

        # Inner content
        ix = cx + 20
        iy = cards_y + 16
        iw = card_w - 40

        # Big finding number
        add_text(
            slide, f"card-{ci+1}-num", num,
            x_px=ix, y_px=iy, w_px=iw, h_px=58,
            font_size_px=46, color=BRAND_ACCENT, bold=True,
        )
        # Headline
        add_text(
            slide, f"card-{ci+1}-headline", headline,
            x_px=ix, y_px=iy + 64, w_px=iw, h_px=50,
            font_size_px=15, color=BRAND_PRIMARY, bold=True,
        )
        # Card rule
        add_rect(slide, f"card-{ci+1}-rule", ix, iy + 122, iw, 3, BRAND_ACCENT)

        # Bullets
        bul_y = iy + 134
        bul_step = 36
        for bi, item in enumerate(bullets):
            by = bul_y + bi * bul_step
            # dot
            add_rect(slide, f"card-{ci+1}-bullet-{bi+1}-dot",
                     ix, by + 7, 5, 5, BRAND_ACCENT_SOFT)
            # Build text: if a stat is included, emphasize it
            stat, text, suffix = item
            if stat:
                if suffix:
                    # text + stat at end (e.g., "Remediation SLA routinely missed by 8–12 days")
                    full = f"{text}<strong>{stat}</strong>"
                else:
                    full = f"<strong>{stat}</strong>{text}"
            else:
                full = text
            add_text(
                slide, f"card-{ci+1}-bullet-{bi+1}", full,
                x_px=ix + 14, y_px=by, w_px=iw - 14, h_px=bul_step,
                font_size_px=12, color=TEXT_MID, emphasis_color=BRAND_PRIMARY_MID,
            )

        # Implication strip at bottom
        impl_y = cards_y + cards_h - impl_h
        impl_strip = add_rect(slide, f"card-{ci+1}-impl-bg", cx, impl_y, card_w, impl_h, IMPL_BG)
        add_rect(slide, f"card-{ci+1}-impl-rule", cx, impl_y, card_w, 1, CARD_BORDER)
        add_text(
            slide, f"card-{ci+1}-impl-label", "IMPLICATION",
            x_px=cx + 20, y_px=impl_y + 8, w_px=card_w - 40, h_px=12,
            font_size_px=8, color=BRAND_PRIMARY_MID, bold=True,
            uppercase=True, letter_spacing_px=1.4,
        )
        add_text(
            slide, f"card-{ci+1}-impl-text", implication,
            x_px=cx + 20, y_px=impl_y + 22, w_px=card_w - 40, h_px=impl_h - 28,
            font_size_px=11, color=BRAND_PRIMARY_MID, italic=True,
        )

    add_footer(slide, page_num=287)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "287_three-col-key-findings.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
