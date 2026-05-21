"""
Builder for pattern 171d: Technical Glossary v2 — DARK variant.

Light source: twins/builders/build_171.py
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

# Dark-mode tag pill palette (saturated darker bg + light fg for visibility)
TAG_TECH_BG = RGBColor(0x45, 0x27, 0xA0); TAG_TECH_FG = RGBColor(0xE6, 0xDC, 0xFF)
TAG_BUS_BG = RGBColor(0x1B, 0x5E, 0x20); TAG_BUS_FG = RGBColor(0xD7, 0xF1, 0xDA)
TAG_REG_BG = RGBColor(0xE6, 0x51, 0x00); TAG_REG_FG = RGBColor(0xFF, 0xEC, 0xD9)
TAG_DATA_BG = RGBColor(0x0D, 0x47, 0xA1); TAG_DATA_FG = RGBColor(0xDA, 0xE9, 0xFB)

TAG_MAP = {
    "tech": (TAG_TECH_BG, TAG_TECH_FG, "Tech"),
    "business": (TAG_BUS_BG, TAG_BUS_FG, "Business"),
    "regulatory": (TAG_REG_BG, TAG_REG_FG, "Regulatory"),
    "data": (TAG_DATA_BG, TAG_DATA_FG, "Data"),
}


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title (bottom-anchored: y=20, h=80 -> bottom-y=100)
    add_text(
        slide, "title",
        "Technical <strong>Glossary</strong>",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    # Subtitle y=108, h=22
    add_text(
        slide, "subtitle",
        "Standardized definitions for project terminology — Architecture, Data, and Regulatory domains",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    # Brand-rule y=132
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    content_top = 220
    content_left = 48
    content_right = 1280 - 48
    content_w = content_right - content_left

    # Alpha sidebar
    side_w = 28
    add_rect(slide, "alpha-sidebar-rule", content_left + side_w + 4, content_top, 1,
             720 - 64 - content_top - 4, CARD_BORDER_DARK)
    active_letters = {"A", "B", "D", "F", "I", "L", "M", "P", "R", "S"}
    for idx, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        ly = content_top + idx * 15
        if ch == "A":
            add_rect(slide, f"alpha-{ch}-bg", content_left + 4, ly, 20, 14, BRAND_ACCENT_SOFT)
            add_text(slide, f"alpha-{ch}", ch,
                     content_left + 4, ly, 20, 14,
                     font_size_px=8, color=BRAND_PRIMARY, bold=True, align="center", anchor="middle")
        else:
            color = WHITE if ch in active_letters else TEXT_ON_DARK_FAINT
            add_text(slide, f"alpha-{ch}", ch,
                     content_left + 4, ly, 20, 14,
                     font_size_px=8, color=color,
                     bold=(ch in active_letters), align="center", anchor="middle")

    # Two columns
    col_start_x = content_left + side_w + 16
    col_w = (content_right - col_start_x - 20) // 2
    col_gap = 20

    left_col_x = col_start_x
    right_col_x = col_start_x + col_w + col_gap

    rows_left = [
        ("section", "A"),
        ("term", 1, "API Gateway", "Managed entry point routing client requests to back-end microservices with auth, rate limiting, and logging.", "tech"),
        ("term", 2, "Audit Trail", "Immutable, timestamped log of system events used for compliance verification and forensic investigation.", "regulatory"),
        ("term", 3, "Availability SLA", "Contractual uptime commitment (e.g., 99.9%) defining acceptable downtime windows per rolling month.", "business"),
        ("section", "B"),
        ("term", 4, "Backpressure", "Flow-control mechanism signalling upstream producers to slow emission when consumers are saturated.", "tech"),
        ("term", 5, "Bounded Context", "DDD partition within which a specific domain model applies consistently, with explicit translation at boundaries.", "tech"),
        ("section", "D"),
        ("term", 6, "Data Lineage", "End-to-end traceability of data from origin through all transformations to its current state.", "data"),
        ("term", 7, "DPIA", "Data Protection Impact Assessment — mandatory GDPR process for high-risk personal-data processing activities.", "regulatory"),
    ]
    rows_right = [
        ("section", "F"),
        ("term", 8, "Feature Flag", "Runtime toggle decoupling code deployment from feature release, enabling targeted rollouts and A/B testing.", "tech"),
        ("section", "I"),
        ("term", 9, "Idempotency Key", "Client-supplied token ensuring duplicate API calls produce identical side-effects without double-processing.", "tech"),
        ("term", 10, "Ingestion Latency", "Elapsed time from event creation to availability in the analytic store; measured at p50, p95, p99.", "data"),
        ("section", "M"),
        ("term", 11, "MTTR", "Mean Time To Recover — average duration to restore service following an incident; primary reliability KPI.", "business"),
        ("section", "R"),
        ("term", 12, "RPO", "Recovery Point Objective — maximum acceptable data-loss window, expressed in time, in a disaster scenario.", "regulatory"),
        ("section", "S"),
        ("term", 13, "Schema Registry", "Centralised catalogue enforcing schema versioning and compatibility checks across event-driven producers/consumers.", "data"),
        ("term", 14, "Service Mesh", "Infrastructure layer handling inter-service communication, mTLS, observability, and traffic management transparently.", "tech"),
    ]

    def _render_col(x, rows):
        y = content_top
        for r in rows:
            if r[0] == "section":
                letter = r[1]
                add_text(slide, f"section-{letter}-header", letter,
                         x, y, col_w, 16,
                         font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
                add_rect(slide, f"section-{letter}-rule", x, y + 16, col_w, 1, CARD_BORDER_DARK)
                y += 22
            else:
                _, n, label, defn, tag = r
                row_h = 36
                add_text(slide, f"term-{n}-label", label,
                         x, y, 100, 14,
                         font_size_px=11, color=WHITE, bold=True)
                add_text(slide, f"term-{n}-def", defn,
                         x + 104, y, col_w - 158, row_h - 4,
                         font_size_px=9, color=TEXT_ON_DARK_MID)
                bg_c, fg, txt = TAG_MAP[tag]
                pill_w = 50
                add_rect(slide, f"term-{n}-tag-bg",
                         x + col_w - pill_w, y, pill_w, 14, bg_c)
                add_text(slide, f"term-{n}-tag", txt,
                         x + col_w - pill_w, y, pill_w, 14,
                         font_size_px=8, color=fg, bold=True, align="center", anchor="middle")
                add_rect(slide, f"term-{n}-rule", x, y + row_h, col_w, 1, CARD_BORDER_DARK)
                y += row_h + 2

    _render_col(left_col_x, rows_left)
    _render_col(right_col_x, rows_right)

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "171",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "171d_glossary-v2-technical-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
