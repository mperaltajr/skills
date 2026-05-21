"""
Builder for pattern 172: Acronym Key — 2-column alphabetized acronym table.

Source HTML: _pattern-library/172_acronym-key.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID,
)
from pptx.dml.color import RGBColor

TAG_BUS_BG = RGBColor(0xED, 0xE9, 0xFE); TAG_BUS_FG = RGBColor(0x5B, 0x21, 0xB6)
TAG_TECH_BG = RGBColor(0xE0, 0xF2, 0xFE); TAG_TECH_FG = RGBColor(0x03, 0x69, 0xA1)
TAG_REG_BG = RGBColor(0xFE, 0xF3, 0xC7); TAG_REG_FG = RGBColor(0x92, 0x40, 0x0E)

TAGS = {
    "business": (TAG_BUS_BG, TAG_BUS_FG, "Business"),
    "tech": (TAG_TECH_BG, TAG_TECH_FG, "Tech"),
    "regulatory": (TAG_REG_BG, TAG_REG_FG, "Regulatory"),
}


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Glossary of <strong>Key Acronyms</strong>",
        subtitle="Reference card — alphabetized by acronym across Business, Technology, and Regulatory domains",
        title_h=42,
        subtitle_h=20,
        brand_rule_w=64,
    )

    content_left = 48
    content_top = 148
    content_w = 1280 - 96
    col_gap = 24
    col_w = (content_w - col_gap) // 2

    # Column headers
    def _col_header(x, prefix):
        add_text(slide, f"{prefix}-acronym-header", "ACRONYM",
                 x + 8, content_top, 80, 14,
                 font_size_px=9, color=TEXT_MID, bold=True, uppercase=True)
        add_text(slide, f"{prefix}-fullform-header", "FULL FORM",
                 x + 8 + 88, content_top, col_w - 8 - 88 - 90, 14,
                 font_size_px=9, color=TEXT_MID, bold=True, uppercase=True)
        add_text(slide, f"{prefix}-category-header", "CATEGORY",
                 x + col_w - 90, content_top, 80, 14,
                 font_size_px=9, color=TEXT_MID, bold=True, align="center", uppercase=True)
        add_rect(slide, f"{prefix}-header-rule", x, content_top + 16, col_w, 1, CARD_BORDER)

    left_x = content_left
    right_x = content_left + col_w + col_gap
    _col_header(left_x, "left-col")
    _col_header(right_x, "right-col")

    left_rows = [
        ("group", 1, "A"),
        ("row", 1, "AGI", "Artificial General Intelligence", "tech", False),
        ("row", 2, "API", "Application Programming Interface", "tech", True),
        ("row", 3, "AUM", "Assets Under Management", "business", False),
        ("group", 2, "B"),
        ("row", 4, "BI", "Business Intelligence", "business", True),
        ("row", 5, "BPO", "Business Process Outsourcing", "business", False),
        ("group", 3, "C"),
        ("row", 6, "CAGR", "Compound Annual Growth Rate", "business", True),
        ("row", 7, "CRM", "Customer Relationship Management", "tech", False),
        ("row", 8, "CSAT", "Customer Satisfaction Score", "business", True),
        ("group", 4, "D"),
        ("row", 9, "DLP", "Data Loss Prevention", "regulatory", False),
        ("row", 10, "DW", "Data Warehouse", "tech", True),
        ("group", 5, "E"),
        ("row", 11, "ERP", "Enterprise Resource Planning", "tech", False),
        ("row", 12, "ESG", "Environmental, Social & Governance", "regulatory", True),
        ("group", 6, "G"),
        ("row", 13, "GDPR", "General Data Protection Regulation", "regulatory", False),
    ]
    right_rows = [
        ("group", 7, "I"),
        ("row", 14, "IAM", "Identity & Access Management", "tech", False),
        ("row", 15, "IP", "Intellectual Property", "regulatory", True),
        ("row", 16, "IRR", "Internal Rate of Return", "business", False),
        ("group", 8, "K"),
        ("row", 17, "KPI", "Key Performance Indicator", "business", True),
        ("group", 9, "L"),
        ("row", 18, "LLM", "Large Language Model", "tech", False),
        ("row", 19, "LOE", "Level of Effort", "business", True),
        ("group", 10, "M"),
        ("row", 20, "MLOps", "Machine Learning Operations", "tech", False),
        ("row", 21, "MoM", "Month-over-Month", "business", True),
        ("group", 11, "N"),
        ("row", 22, "NPS", "Net Promoter Score", "business", False),
        ("row", 23, "NPV", "Net Present Value", "business", True),
        ("group", 12, "R"),
        ("row", 24, "RACI", "Responsible, Accountable, Consulted, Informed", "business", False),
        ("row", 25, "ROI", "Return on Investment", "business", True),
        ("group", 13, "S"),
        ("row", 26, "SLA", "Service Level Agreement", "regulatory", False),
        ("row", 27, "SOC 2", "System & Org. Controls 2", "regulatory", True),
    ]

    def _render_col(x, rows):
        y = content_top + 22
        for r in rows:
            if r[0] == "group":
                _, gid, letter = r
                add_text(slide, f"group-{gid}-header", letter,
                         x + 8, y, 60, 14,
                         font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, uppercase=True)
                y += 16
            else:
                _, aid, key, full, tag, alt = r
                row_h = 19
                if alt:
                    add_rect(slide, f"acronym-{aid}-row-bg", x, y, col_w, row_h, CARD_BG)
                add_text(slide, f"acronym-{aid}-key", key,
                         x + 8, y, 80, row_h,
                         font_size_px=11, color=BRAND_PRIMARY, bold=True, anchor="middle")
                add_text(slide, f"acronym-{aid}-full", full,
                         x + 8 + 88, y, col_w - 8 - 88 - 92, row_h,
                         font_size_px=11, color=TEXT_DARK, anchor="middle")
                # tag pill
                bg, fg, label = TAGS[tag]
                pill_w = 76
                add_rect(slide, f"acronym-{aid}-tag-bg",
                         x + col_w - pill_w - 6, y + 2, pill_w, row_h - 4, bg)
                add_text(slide, f"acronym-{aid}-tag", label,
                         x + col_w - pill_w - 6, y + 2, pill_w, row_h - 4,
                         font_size_px=8, color=fg, bold=True, align="center", anchor="middle")
                y += row_h

    _render_col(left_x, left_rows)
    _render_col(right_x, right_rows)

    add_footer(slide, page_num=172)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "172_acronym-key.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
