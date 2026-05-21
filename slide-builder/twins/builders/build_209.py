"""
Builder for pattern 209: Banded rows key findings table.

Source HTML: _pattern-library/209_banded-rows-findings.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT,
    CARD_BG, CARD_BORDER, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Key findings reveal <strong>critical gaps</strong> in operational maturity",
        subtitle="Four priority findings across process, technology, talent, and governance dimensions",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # Table: top:140, left:48, right:48 (w=1184), bottom 66 → height ~514
    tbl_left = 48
    tbl_top = 140
    tbl_w = 1184
    col_w = [140, 784, 260]
    col_x = [tbl_left, tbl_left + col_w[0], tbl_left + col_w[0] + col_w[1]]

    # Headers
    header_h = 30
    add_text(slide, "table-col-1-header", "Finding",
             x_px=col_x[0], y_px=tbl_top, w_px=col_w[0], h_px=header_h - 8,
             font_size_px=12, color=BRAND_PRIMARY, bold=True, align="center")
    add_text(slide, "table-col-2-header", "Description",
             x_px=col_x[1] + 14, y_px=tbl_top, w_px=col_w[1] - 28, h_px=header_h - 8,
             font_size_px=12, color=BRAND_PRIMARY, bold=True)
    add_text(slide, "table-col-3-header", "Evidence",
             x_px=col_x[2] + 14, y_px=tbl_top, w_px=col_w[2] - 28, h_px=header_h - 8,
             font_size_px=12, color=BRAND_PRIMARY, bold=True)
    # Header underline
    add_rect(slide, "table-head-rule", tbl_left, tbl_top + header_h, tbl_w, 2, BRAND_PRIMARY)

    # Rows
    rows = [
        ("F1\nProcess\nFragmentation",
         "• Core order-to-cash workflows span 7 disconnected systems with no single source of truth\n"
         "• Manual re-keying at 4 handoff points introduces error rates exceeding tolerance\n"
         "• Process owners lack visibility into end-to-end cycle time, preventing improvement",
         "38%", "of transactions require manual rework before close; avg. 2.4 hrs per incident",
         "Source: Process mining analysis, Apr 2026"),
        ("F2\nTechnology\nDebt",
         "• Legacy ERP modules running on end-of-life versions unsupported since Q3 2024\n"
         "• API layer lacks idempotency guarantees, causing duplicate postings during peak load\n"
         "• No automated regression suite; releases require 6-week manual UAT cycles",
         "$4.2M", "estimated annual cost of unplanned downtime and emergency patching",
         "Source: IT cost model, FY2025 actuals"),
        ("F3\nTalent\nReadiness",
         "• Only 12% of ops staff hold current certification in target-state tooling\n"
         "• Knowledge concentrated in 3 SMEs with no documented succession or cross-training\n"
         "• Attrition risk rated HIGH for 2 of 3 SMEs based on tenure and benchmarks",
         "~9 mo", "to full proficiency for a new hire under current onboarding programme",
         "Source: HR skills assessment, Mar 2026"),
        ("F4\nGovernance\nGaps",
         "• No formal change-advisory board; 60% of production changes deployed without peer review\n"
         "• SLA targets defined but not instrumented — breaches detected only via client complaint\n"
         "• Ownership matrix last updated 18 months ago; 5 critical controls show 'TBD' owner",
         "3 of 5", "audit findings from FY2025 remain open past remediation deadline",
         "Source: Internal audit report, Jan 2026"),
    ]
    row_h = 110
    body_top = tbl_top + header_h + 4
    for i, (finding, desc, stat, label, source) in enumerate(rows):
        n = i + 1
        ry = body_top + i * row_h
        row_bg = CARD_BG if (i % 2 == 1) else WHITE
        # Row background spanning desc and evidence columns
        add_rect(slide, f"table-row-{n}-bg", col_x[1], ry, col_w[1] + col_w[2], row_h, row_bg)
        # Finding cell — brand-primary always
        add_rect(slide, f"table-row-{n}-cell-1-bg", col_x[0], ry, col_w[0], row_h, BRAND_PRIMARY)
        add_text(slide, f"table-row-{n}-cell-1", finding,
                 x_px=col_x[0] + 6, y_px=ry, w_px=col_w[0] - 12, h_px=row_h,
                 font_size_px=11, color=WHITE, bold=True, align="center", anchor="middle")
        # Description
        add_text(slide, f"table-row-{n}-cell-2", desc,
                 x_px=col_x[1] + 16, y_px=ry + 8, w_px=col_w[1] - 32, h_px=row_h - 16,
                 font_size_px=11, color=TEXT_DARK)
        # Evidence: stat + label + source
        add_text(slide, f"table-row-{n}-stat", stat,
                 x_px=col_x[2] + 14, y_px=ry + 10, w_px=col_w[2] - 28, h_px=28,
                 font_size_px=22, color=BRAND_ACCENT, bold=True)
        add_text(slide, f"table-row-{n}-stat-label", label,
                 x_px=col_x[2] + 14, y_px=ry + 42, w_px=col_w[2] - 28, h_px=40,
                 font_size_px=10, color=TEXT_MID)
        add_text(slide, f"table-row-{n}-source", source,
                 x_px=col_x[2] + 14, y_px=ry + row_h - 18, w_px=col_w[2] - 28, h_px=14,
                 font_size_px=9, color=TEXT_FAINT)
        # Row divider
        add_rect(slide, f"table-row-{n}-divider",
                 col_x[1], ry + row_h - 1, col_w[1] + col_w[2], 1, CARD_BORDER)
        # Left border between evidence and desc
        add_rect(slide, f"table-row-{n}-vsep",
                 col_x[2], ry, 1, row_h, CARD_BORDER)

    add_footer(slide, page_num=209)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "209_banded-rows-findings.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
