"""
Builder for pattern 243: Assumption & Dependency Log (two grouped tables + summary).

Source HTML: _pattern-library/243_assumption-dependency-log.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, TEXT_DARK, TEXT_MID, TEXT_FAINT,
    CARD_BG, CARD_BORDER, WHITE,
)
from pptx.dml.color import RGBColor

CONFIRMED_BG = RGBColor(0xDC, 0xFC, 0xE7)
CONFIRMED_TXT = RGBColor(0x15, 0x80, 0x3D)
ATRISK_BG = RGBColor(0xFE, 0xF3, 0xC7)
ATRISK_TXT = RGBColor(0xB4, 0x53, 0x09)
UNVAL_BG = RGBColor(0xF1, 0xF5, 0xF9)
UNVAL_TXT = RGBColor(0x64, 0x74, 0x8B)
CONF_HIGH = RGBColor(0x22, 0xC5, 0x5B)
CONF_MED = RGBColor(0xF5, 0x9E, 0x0B)
CONF_LOW = RGBColor(0x94, 0xA3, 0xB8)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Assumption &amp; <strong>Dependency</strong> Log",
        subtitle="Tracks project assumptions and external dependencies — confidence, owners, and status",
        title_x=32, title_y=42, title_w=1216, title_h=42,
        subtitle_h=20, brand_rule_w=64,
    )

    # Tables: top:140, left:32, right:32, w=1216
    tbl_left = 32
    tbl_w = 1216
    col_w = [40, 480, 110, 130, 130, 130]
    col_w[1] = tbl_w - (40 + 110 + 130 + 130 + 130) - 12
    col_x = [tbl_left]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)

    def draw_table(top, section_name, section_color, rows, section_n, has_conf_dots):
        # Section header bar
        sh_h = 22
        add_rect(slide, f"section-{section_n}-header-bg", tbl_left, top, tbl_w, sh_h, section_color)
        add_text(slide, f"section-{section_n}-header", section_name,
                 x_px=tbl_left + 12, y_px=top + 4, w_px=400, h_px=16,
                 font_size_px=11, color=WHITE, bold=True, uppercase=True)
        # Column headers
        hdr_y = top + sh_h
        hdr_h = 22
        add_rect(slide, f"section-{section_n}-hdr-bg", tbl_left, hdr_y, tbl_w, hdr_h, CARD_BG)
        headers = ["#", "Statement", "Category", "Confidence", "Owner", "Status"]
        for i, h in enumerate(headers):
            add_text(slide, f"section-{section_n}-col-{i+1}-header", h,
                     x_px=col_x[i] + 8, y_px=hdr_y + 4, w_px=col_w[i] - 16, h_px=14,
                     font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True)
        # Data rows
        row_h = 30
        y = hdr_y + hdr_h
        for i, (num, stmt, cat, conf_or_dash, owner, status_kind) in enumerate(rows):
            row_bg = RGBColor(0xFD, 0xFB, 0xFF) if (i % 2 == 1) else WHITE
            add_rect(slide, f"row-{num.lower()}-bg", tbl_left, y, tbl_w, row_h, row_bg)
            # Num
            add_text(slide, f"row-{num.lower()}-num", num,
                     x_px=col_x[0], y_px=y + 8, w_px=col_w[0], h_px=16,
                     font_size_px=10, color=TEXT_FAINT, bold=True, align="center")
            # Statement
            add_text(slide, f"row-{num.lower()}-statement", stmt,
                     x_px=col_x[1] + 8, y_px=y + 6, w_px=col_w[1] - 16, h_px=row_h - 8,
                     font_size_px=11, color=TEXT_DARK)
            # Category badge
            add_text(slide, f"row-{num.lower()}-category", cat,
                     x_px=col_x[2] + 8, y_px=y + 8, w_px=col_w[2] - 16, h_px=16,
                     font_size_px=9, color=BRAND_PRIMARY_MID, bold=True,
                     bg_fill=CARD_BG, padding_px=(2, 4, 2, 4))
            # Confidence
            if has_conf_dots and conf_or_dash != "—":
                conf_text, dot_color, filled_count = conf_or_dash
                # 3 dots
                for d in range(3):
                    dot_x = col_x[3] + 8 + d * 10
                    dot_y = y + 12
                    c = dot_color if d < filled_count else CARD_BORDER
                    add_rect(slide, f"row-{num.lower()}-dot-{d+1}", dot_x, dot_y, 7, 7, c)
                add_text(slide, f"row-{num.lower()}-confidence", conf_text,
                         x_px=col_x[3] + 42, y_px=y + 8, w_px=col_w[3] - 50, h_px=16,
                         font_size_px=10, color=TEXT_MID)
            else:
                add_text(slide, f"row-{num.lower()}-confidence", "—",
                         x_px=col_x[3] + 8, y_px=y + 8, w_px=col_w[3] - 16, h_px=16,
                         font_size_px=10, color=TEXT_FAINT)
            # Owner
            add_text(slide, f"row-{num.lower()}-owner", owner,
                     x_px=col_x[4] + 8, y_px=y + 8, w_px=col_w[4] - 16, h_px=16,
                     font_size_px=11, color=TEXT_DARK)
            # Status pill
            if status_kind == "Confirmed":
                pbg, ptxt = CONFIRMED_BG, CONFIRMED_TXT
            elif status_kind == "At Risk":
                pbg, ptxt = ATRISK_BG, ATRISK_TXT
            else:
                pbg, ptxt = UNVAL_BG, UNVAL_TXT
            add_text(slide, f"row-{num.lower()}-status-pill", status_kind,
                     x_px=col_x[5] + 8, y_px=y + 8, w_px=col_w[5] - 16, h_px=16,
                     font_size_px=9, color=ptxt, bold=True, align="center", uppercase=True,
                     bg_fill=pbg, padding_px=(2, 6, 2, 6))
            # Row divider
            add_rect(slide, f"row-{num.lower()}-divider", tbl_left, y + row_h - 1, tbl_w, 1, CARD_BORDER)
            y += row_h
        return y

    assumptions = [
        ("A1", "Budget approval will be secured by end of Q2", "Financial",
         ("High", CONF_HIGH, 3), "CFO Office", "Confirmed"),
        ("A2", "Legacy system can export in required format", "Technical",
         ("Medium", CONF_MED, 2), "IT Arch", "At Risk"),
        ("A3", "Regulatory sign-off timeline is 6 weeks", "Compliance",
         ("Low", CONF_LOW, 1), "Legal", "Unvalidated"),
        ("A4", "Key personnel remain available for full project", "Resource",
         ("High", CONF_HIGH, 3), "PMO", "Confirmed"),
    ]
    dependencies = [
        ("D1", "ERP upgrade project completes before Phase 2", "IT", "—", "IT PMO", "At Risk"),
        ("D2", "Vendor API access granted", "External", "—", "Procurement", "Confirmed"),
        ("D3", "Board approval of business case", "Strategic", "—", "Exec Sponsor", "Unvalidated"),
    ]

    y_end = draw_table(140, "Assumptions", BRAND_PRIMARY, assumptions, 1, has_conf_dots=True)
    y_end = draw_table(y_end + 12, "Dependencies", BRAND_PRIMARY_MID, dependencies, 2, has_conf_dots=False)

    # Summary row
    summary_y = y_end + 12
    add_rect(slide, "summary-bg", tbl_left, summary_y, tbl_w, 32, CARD_BG)
    add_text(slide, "summary-label", "SUMMARY",
             x_px=tbl_left + 14, y_px=summary_y + 8, w_px=80, h_px=16,
             font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True)
    counts = [
        ("3", "Confirmed", CONFIRMED_TXT),
        ("2", "At Risk", ATRISK_TXT),
        ("2", "Unvalidated", TEXT_FAINT),
    ]
    cx = tbl_left + 110
    for i, (count, label, color) in enumerate(counts):
        n = i + 1
        if i > 0:
            add_rect(slide, f"summary-divider-{i}", cx - 12, summary_y + 8, 1, 16, CARD_BORDER)
        add_text(slide, f"summary-{n}-count", count,
                 x_px=cx, y_px=summary_y + 4, w_px=40, h_px=22,
                 font_size_px=18, color=color, bold=True)
        add_text(slide, f"summary-{n}-label", label,
                 x_px=cx + 28, y_px=summary_y + 10, w_px=120, h_px=16,
                 font_size_px=10, color=TEXT_MID)
        cx += 160

    add_footer(slide, page_num=243)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "243_assumption-dependency-log.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
