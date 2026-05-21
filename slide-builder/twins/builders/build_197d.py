"""
Builder for pattern 197d: Solution Overview — DARK variant.

Light source: twins/builders/build_197.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT, WHITE,
)
from pptx.dml.color import RGBColor

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

X_BG = RGBColor(0x4A, 0x14, 0x22)
X_TXT = RGBColor(0xFB, 0x72, 0x85)
CHECK_BG = RGBColor(0x0F, 0x3F, 0x2A)
CHECK_TXT = RGBColor(0x4A, 0xDE, 0x80)


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    add_text(
        slide, "title",
        "Our <strong>Solution</strong> — At a Glance",
        x_px=64, y_px=20, w_px=1000, h_px=80,
        font_size_px=32, color=WHITE, bold=True,
        emphasis_color=BRAND_ACCENT_SOFT,
        anchor="bottom",
    )
    add_text(
        slide, "subtitle",
        "What we solve, how we solve it, and the outcomes you can expect",
        x_px=64, y_px=108, w_px=880, h_px=22,
        font_size_px=14, color=TEXT_ON_DARK_MID, italic=True,
    )
    add_rect(slide, "brand-rule", x_px=64, y_px=132, w_px=64, h_px=3, fill_color=BRAND_ACCENT_SOFT)

    body_top = 220
    body_bot = 600
    body_h = body_bot - body_top
    grid_w = 1280 - 128
    col1_w = int(grid_w * 0.28)
    col2_w = int(grid_w * 0.44)
    col3_w = grid_w - col1_w - col2_w - 32
    cx1 = 64
    cx2 = cx1 + col1_w + 16
    cx3 = cx2 + col2_w + 16

    add_text(slide, "col-1-header", "THE CHALLENGE",
             x_px=cx1, y_px=body_top, w_px=col1_w, h_px=18,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True)
    add_rect(slide, "col-1-rule", cx1, body_top + 20, col1_w, 1, CARD_BORDER_DARK)
    challenges = [
        ("Fragmented Processes", "Siloed teams operate on disconnected workflows, creating costly hand-off delays and version errors."),
        ("Limited Visibility", "Leadership lacks real-time data to make confident decisions, relying on lagging weekly reports."),
        ("Slow Time-to-Market", "Manual approvals and legacy tooling extend delivery cycles well beyond competitive benchmarks."),
    ]
    cy = body_top + 36
    for i, (head, body) in enumerate(challenges):
        add_text(slide, f"challenge-{i+1}-marker", "✗",
                 x_px=cx1, y_px=cy, w_px=18, h_px=18,
                 font_size_px=10, color=X_TXT, bold=True, align="center", anchor="middle",
                 bg_fill=X_BG, padding_px=(0, 0, 0, 0))
        add_text(slide, f"challenge-{i+1}-heading", head,
                 x_px=cx1 + 26, y_px=cy, w_px=col1_w - 26, h_px=16,
                 font_size_px=11, color=WHITE, bold=True)
        add_text(slide, f"challenge-{i+1}-body", body,
                 x_px=cx1 + 26, y_px=cy + 18, w_px=col1_w - 26, h_px=68,
                 font_size_px=11, color=TEXT_ON_DARK_MID)
        cy += 110

    sol_bg = add_rect(slide, "col-2-bg", cx2, body_top, col2_w, body_h, CARD_BG_DARK)
    sol_bg.line.color.rgb = CARD_BORDER_DARK
    sol_bg.line.width = 9525
    add_rect(slide, "col-2-left-border", cx2, body_top, 2, body_h, BRAND_ACCENT_SOFT)
    add_rect(slide, "col-2-right-border", cx2 + col2_w - 2, body_top, 2, body_h, BRAND_ACCENT_SOFT)
    add_text(slide, "col-2-header", "OUR SOLUTION",
             x_px=cx2 + 16, y_px=body_top + 16, w_px=col2_w - 32, h_px=18,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True)
    add_rect(slide, "col-2-rule", cx2 + 16, body_top + 36, col2_w - 32, 1, BRAND_ACCENT_SOFT)
    add_text(slide, "solution-name", "Accenture Intelligent Operations Platform",
             x_px=cx2 + 16, y_px=body_top + 50, w_px=col2_w - 32, h_px=22,
             font_size_px=14, color=WHITE, bold=True)
    add_text(slide, "solution-desc",
             "A cloud-native, AI-augmented platform that unifies your end-to-end operating model — connecting people, processes, and data in a single pane of glass. Embedded intelligence surfaces exceptions before they escalate, and modular architecture means you go live in weeks, not years.",
             x_px=cx2 + 16, y_px=body_top + 76, w_px=col2_w - 32, h_px=110,
             font_size_px=11, color=TEXT_ON_DARK_MID)
    add_text(slide, "capabilities-label", "CORE CAPABILITIES",
             x_px=cx2 + 16, y_px=body_top + 196, w_px=col2_w - 32, h_px=14,
             font_size_px=9, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True)
    capabilities = [
        "Unified Data & Process Orchestration",
        "AI-Powered Decision Intelligence",
        "Modular, Cloud-Ready Architecture",
    ]
    chip_y = body_top + 216
    for i, cap in enumerate(capabilities):
        cy2 = chip_y + i * 38
        add_rect(slide, f"capability-{i+1}-bg", cx2 + 16, cy2, col2_w - 32, 28, BRAND_ACCENT)
        add_rect(slide, f"capability-{i+1}-icon-bg", cx2 + 22, cy2 + 6, 16, 16, WHITE)
        add_text(slide, f"capability-{i+1}", cap,
                 x_px=cx2 + 46, y_px=cy2 + 6, w_px=col2_w - 64, h_px=18,
                 font_size_px=11, color=WHITE, bold=True)

    add_text(slide, "col-3-header", "KEY BENEFITS",
             x_px=cx3, y_px=body_top, w_px=col3_w, h_px=18,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, bold=True, uppercase=True)
    add_rect(slide, "col-3-rule", cx3, body_top + 20, col3_w, 1, CARD_BORDER_DARK)
    benefits = [
        ("Operational Cost Reduction", "Automated workflows eliminate manual overhead and rework across finance and supply chain.", "−30% cost"),
        ("Faster Delivery Cycles", "Parallel processing and intelligent routing cut end-to-end cycle times dramatically.", "+2× speed"),
        ("Improved Decision Quality", "Real-time dashboards and AI alerts keep leadership ahead of issues, not behind them.", "+45% accuracy"),
    ]
    cy = body_top + 36
    for i, (head, body, metric) in enumerate(benefits):
        add_text(slide, f"benefit-{i+1}-marker", "✓",
                 x_px=cx3, y_px=cy, w_px=18, h_px=18,
                 font_size_px=10, color=CHECK_TXT, bold=True, align="center", anchor="middle",
                 bg_fill=CHECK_BG, padding_px=(0, 0, 0, 0))
        add_text(slide, f"benefit-{i+1}-heading", head,
                 x_px=cx3 + 26, y_px=cy, w_px=col3_w - 26, h_px=16,
                 font_size_px=11, color=WHITE, bold=True)
        add_text(slide, f"benefit-{i+1}-body", body,
                 x_px=cx3 + 26, y_px=cy + 18, w_px=col3_w - 26, h_px=50,
                 font_size_px=11, color=TEXT_ON_DARK_MID)
        add_text(slide, f"benefit-{i+1}-metric", metric,
                 x_px=cx3 + 26, y_px=cy + 72, w_px=110, h_px=18,
                 font_size_px=10, color=WHITE, bold=True, align="center",
                 bg_fill=BRAND_ACCENT, padding_px=(2, 8, 2, 8))
        cy += 110

    conv_y = 620
    add_rect(slide, "convergence-bg", 64, conv_y, 1280 - 128, 28, BRAND_ACCENT)
    add_text(slide, "convergence",
             "Proven across 40+ deployments — ready to activate in 8 weeks.",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=28,
             font_size_px=11, color=WHITE, bold=True, align="center", anchor="middle")

    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "197",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "197d_solution-overview-dark.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
