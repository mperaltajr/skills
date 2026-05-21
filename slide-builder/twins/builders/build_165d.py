"""
Builder for pattern 165d: Enterprise Service Catalogue — dark.

Source HTML: _pattern-library/165_service-catalogue-dark.html
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

BADGE_ACTIVE_BG = RGBColor(0x14, 0x4E, 0x2A)
BADGE_ACTIVE_FG = RGBColor(0x86, 0xEF, 0xAC)
BADGE_REVIEW_BG = RGBColor(0x57, 0x40, 0x12)
BADGE_REVIEW_FG = RGBColor(0xFC, 0xD3, 0x4D)
BADGE_DEPR_BG = RGBColor(0x5C, 0x1F, 0x1F)
BADGE_DEPR_FG = RGBColor(0xF8, 0x71, 0x71)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Canonical chrome
    add_text(slide, "title", "Enterprise <strong>Service Catalogue</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=26, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Consolidated view of active services, ownership, and operational status across all delivery domains",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Table layout
    left = 48
    right = 1280 - 48
    table_w = right - left
    top = 220

    col1_w = int(table_w * 0.22)
    col2_w = int(table_w * 0.48)
    col3_w = table_w - col1_w - col2_w

    col1_x = left
    col2_x = col1_x + col1_w
    col3_x = col2_x + col2_w

    # Column headers
    header_h = 24
    add_text(slide, "table-col-1-header", "SERVICE NAME",
             col1_x + 12, top, col1_w - 12, header_h,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "table-col-2-header", "DESCRIPTION",
             col2_x + 12, top, col2_w - 12, header_h,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_text(slide, "table-col-3-header", "OWNER / SLA STATUS",
             col3_x + 12, top, col3_w - 12, header_h,
             font_size_px=11, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_rect(slide, "table-header-rule", left, top + header_h, table_w, 2, CARD_BORDER_DARK)

    rows = [
        ("cat", 1, "Infrastructure & Platform Services"),
        ("svc", 1, "Cloud Provisioning",
         "Automated VM and container provisioning across Azure and AWS environments",
         "R. Santos", "Active", "active", False),
        ("svc", 2, "Network Operations",
         "End-to-end network configuration, monitoring and incident management for all regions",
         "T. Okonkwo", "Active", "active", True),
        ("svc", 3, "Identity & Access Mgmt",
         "SSO, MFA, and role-based access control for enterprise applications and data assets",
         "A. Mehra", "Review", "review", False),
        ("svc", 4, "Storage & Backup",
         "Tiered object and block storage with automated daily backup and retention policies",
         "L. Ferreira", "Deprecated", "deprecated", True),
        ("cat", 2, "Application & Data Services"),
        ("svc", 5, "API Gateway",
         "Centralised API management, rate limiting, and analytics for internal and external consumers",
         "P. Nguyen", "Active", "active", False),
        ("svc", 6, "Data Warehouse",
         "Governed enterprise data lake and warehouse with self-service BI connectivity",
         "C. Balogun", "Active", "active", True),
        ("svc", 7, "CI/CD Pipeline",
         "Automated build, test, and deployment pipeline supporting microservices and monoliths",
         "S. Johansson", "Review", "review", False),
        ("svc", 8, "Observability Platform",
         "Unified logging, tracing, and alerting stack across all production workloads",
         "M. Al-Rashid", "Active", "active", True),
    ]

    y = top + header_h + 4
    cat_h = 22
    svc_h = 38

    for row in rows:
        if row[0] == "cat":
            _, n, txt = row
            add_rect(slide, f"cat-{n}-bg", left, y, table_w, cat_h, BRAND_PRIMARY_MID)
            add_text(slide, f"cat-{n}-header", txt,
                     left + 12, y, table_w - 24, cat_h,
                     font_size_px=10, color=WHITE, bold=True, uppercase=True,
                     anchor="middle")
            y += cat_h
        else:
            _, n, name, desc, owner, status_label, status_kind, tinted = row
            if tinted:
                add_rect(slide, f"svc-{n}-row-bg", left, y, table_w, svc_h, CARD_BG_DARK)
            add_text(slide, f"svc-{n}-name", name,
                     col1_x + 12, y + 4, col1_w - 24, svc_h - 8,
                     font_size_px=12, color=WHITE, bold=True, anchor="middle")
            add_text(slide, f"svc-{n}-desc", desc,
                     col2_x + 12, y + 4, col2_w - 24, svc_h - 8,
                     font_size_px=11, color=TEXT_ON_DARK_MID, anchor="middle")
            add_text(slide, f"svc-{n}-owner", owner,
                     col3_x + 12, y + 4, 80, svc_h - 8,
                     font_size_px=11, color=WHITE, anchor="middle")
            pill_x = col3_x + 12 + 90
            pill_w = 80
            pill_h = 16
            pill_y = y + (svc_h - pill_h) // 2
            if status_kind == "active":
                pbg, pfg = BADGE_ACTIVE_BG, BADGE_ACTIVE_FG
            elif status_kind == "review":
                pbg, pfg = BADGE_REVIEW_BG, BADGE_REVIEW_FG
            else:
                pbg, pfg = BADGE_DEPR_BG, BADGE_DEPR_FG
            add_rect(slide, f"svc-{n}-status-pill-bg", pill_x, pill_y, pill_w, pill_h, pbg)
            add_text(slide, f"svc-{n}-status-pill", status_label,
                     pill_x, pill_y, pill_w, pill_h,
                     font_size_px=9, color=pfg, bold=True, align="center", anchor="middle")
            add_rect(slide, f"svc-{n}-rule", left, y + svc_h - 1, table_w, 1, CARD_BORDER_DARK)
            y += svc_h

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "165",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "165d_service-catalogue.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
