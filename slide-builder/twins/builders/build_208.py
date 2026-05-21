"""
Builder for pattern 208: Executive Summary (Structured 4-Zone).

2×2 grid: Context (tl) / Findings (tr) / Recommendation (bl, dominant) /
Next Steps (br). Uses canonical quadrant-{tl|tr|bl|br}-* IDs.

Source HTML: _pattern-library/208_exec-summary-structured.html
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
        title="Client Program Needs a <strong>Decisive Pivot</strong> Before Q3 Gate",
        subtitle="Executive Summary — Program Health Review · May 2026",
        title_h=42, subtitle_h=20, brand_rule_w=64,
    )

    # 2x2 grid
    body_top = 168
    body_bot = 600
    body_h = body_bot - body_top
    body_w = 1280 - 128
    cell_w = body_w // 2
    cell_h = body_h // 2

    # Cell positions
    cells = {
        "tl": (64, body_top, cell_w, cell_h),
        "tr": (64 + cell_w, body_top, cell_w, cell_h),
        "bl": (64, body_top + cell_h, cell_w, cell_h),
        "br": (64 + cell_w, body_top + cell_h, cell_w, cell_h),
    }

    # Draw cell backgrounds
    for pos, (x, y, w, h) in cells.items():
        bg_color = CARD_BG if pos == "bl" else WHITE
        cell = add_rect(slide, f"quadrant-{pos}-bg", x, y, w, h, bg_color)
        cell.line.color.rgb = CARD_BORDER
        cell.line.width = 9525

    # Left accent on bl
    add_rect(slide, "quadrant-bl-accent", cells["bl"][0], cells["bl"][1], 3, cell_h, BRAND_PRIMARY)

    # TL: Context
    x, y, w, h = cells["tl"]
    add_rect(slide, "quadrant-tl-label-accent", x + 16, y + 16, 3, 14, BRAND_ACCENT)
    add_text(slide, "quadrant-tl-label", "CONTEXT",
             x_px=x + 24, y_px=y + 14, w_px=w - 40, h_px=18,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    add_text(slide, "quadrant-tl-body",
             "The Orion transformation program entered Phase 3 four months ago with three workstreams running in parallel. Despite on-schedule delivery of two streams, the data migration workstream has accumulated a 6-week lag, putting the Q3 go-live at material risk. Steering has not yet been formally notified of scope implications.",
             x_px=x + 24, y_px=y + 40, w_px=w - 48, h_px=h - 56,
             font_size_px=12, color=TEXT_DARK)

    # TR: Findings (numbered list)
    x, y, w, h = cells["tr"]
    add_rect(slide, "quadrant-tr-label-accent", x + 16, y + 16, 3, 14, BRAND_ACCENT)
    add_text(slide, "quadrant-tr-label", "FINDINGS",
             x_px=x + 24, y_px=y + 14, w_px=w - 40, h_px=18,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    findings = [
        "Data migration lag is systemic — root cause is an under-resourced ETL team, not a tooling defect; adding sprint cycles will not close the gap without headcount.",
        "Change management readiness scores dropped from 74% to 61% in the last pulse survey, signaling user adoption risk at launch.",
        "Budget contingency is 80% consumed with two months remaining; current burn rate projects a $1.2M overrun unless scope is re-baselined.",
    ]
    fy = y + 40
    for i, f in enumerate(findings):
        n = i + 1
        add_text(slide, f"quadrant-tr-{n}-num", str(n),
                 x_px=x + 24, y_px=fy, w_px=18, h_px=18,
                 font_size_px=10, color=BRAND_PRIMARY, bold=True, align="center", anchor="middle",
                 bg_fill=BRAND_ACCENT_SOFT, padding_px=(0, 0, 0, 0))
        add_text(slide, f"quadrant-tr-{n}-body", f,
                 x_px=x + 50, y_px=fy - 2, w_px=w - 70, h_px=52,
                 font_size_px=11, color=TEXT_DARK)
        fy += 56

    # BL: Recommendation (dominant)
    x, y, w, h = cells["bl"]
    add_rect(slide, "quadrant-bl-label-accent", x + 16, y + 16, 3, 14, BRAND_PRIMARY)
    add_text(slide, "quadrant-bl-label", "RECOMMENDATION",
             x_px=x + 24, y_px=y + 14, w_px=w - 40, h_px=18,
             font_size_px=10, color=BRAND_PRIMARY, bold=True, uppercase=True)
    add_text(slide, "quadrant-bl-statement",
             "Approve a 6-week schedule extension and immediate resource augmentation for the data workstream to protect go-live quality and contain budget exposure.",
             x_px=x + 24, y_px=y + 40, w_px=w - 48, h_px=60,
             font_size_px=13, color=BRAND_PRIMARY, bold=True)
    rec_body = (
        "› Onboard 2 senior ETL engineers from the bench by end of May to restore migration velocity to target.\n"
        "› Re-baseline scope with Steering at the June 3 gate to formally absorb the extension and reset the budget ceiling."
    )
    add_text(slide, "quadrant-bl-body", rec_body,
             x_px=x + 24, y_px=y + 108, w_px=w - 48, h_px=h - 120,
             font_size_px=12, color=TEXT_DARK, emphasis_color=BRAND_ACCENT)

    # BR: Next Steps
    x, y, w, h = cells["br"]
    add_rect(slide, "quadrant-br-label-accent", x + 16, y + 16, 3, 14, BRAND_ACCENT)
    add_text(slide, "quadrant-br-label", "NEXT STEPS",
             x_px=x + 24, y_px=y + 14, w_px=w - 40, h_px=18,
             font_size_px=10, color=BRAND_ACCENT, bold=True, uppercase=True)
    actions = [
        ("Raise resource request for 2 ETL engineers through the Talent Deployment board.",
         "J. Reyes · Delivery Lead", "May 23"),
        ("Prepare revised program baseline (schedule + budget) for Steering deck.",
         "A. Müller · PMO", "May 30"),
        ("Present extension recommendation and re-baselined plan at Steering gate.",
         "C. Okafor · Sponsor", "Jun 3"),
    ]
    ay = y + 40
    for i, (text, owner, date) in enumerate(actions):
        n = i + 1
        add_text(slide, f"quadrant-br-{n}-text", text,
                 x_px=x + 24, y_px=ay, w_px=w - 48, h_px=32,
                 font_size_px=11, color=TEXT_DARK)
        # Chips row
        chip_y = ay + 32
        add_text(slide, f"quadrant-br-{n}-owner", owner,
                 x_px=x + 24, y_px=chip_y, w_px=180, h_px=16,
                 font_size_px=9, color=BRAND_PRIMARY, bold=True, align="center",
                 bg_fill=BRAND_ACCENT_SOFT, padding_px=(2, 6, 2, 6))
        add_text(slide, f"quadrant-br-{n}-date", date,
                 x_px=x + 210, y_px=chip_y, w_px=80, h_px=16,
                 font_size_px=9, color=TEXT_MID, align="center",
                 bg_fill=CARD_BG, padding_px=(2, 6, 2, 6))
        ay += 60

    add_footer(slide, page_num=208)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "208_exec-summary-structured.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
