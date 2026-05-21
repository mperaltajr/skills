"""
Builder for pattern 197: Solution Overview.

3-column body: Challenge (left, 28%) / Solution (center, 44%, highlighted) /
Benefits (right, 28%). Center column is the dominant zone.
Bottom convergence bar.

Source HTML: _pattern-library/197_solution-overview.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, add_icon,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

X_BG = RGBColor(0xFE, 0xE2, 0xE2)
X_TXT = RGBColor(0xDC, 0x26, 0x26)
CHECK_BG = RGBColor(0xDC, 0xFC, 0xE7)
CHECK_TXT = RGBColor(0x16, 0xA3, 0x4A)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Our <strong>Solution</strong> — At a Glance",
        subtitle="What we solve, how we solve it, and the outcomes you can expect",
        title_h=42, subtitle_h=20, brand_rule_w=64,
    )

    # 3-col grid
    body_top = 168
    body_bot = 560
    body_h = body_bot - body_top
    grid_w = 1280 - 128
    col1_w = int(grid_w * 0.28)
    col2_w = int(grid_w * 0.44)
    col3_w = grid_w - col1_w - col2_w - 32  # 16px gap each
    cx1 = 64
    cx2 = cx1 + col1_w + 16
    cx3 = cx2 + col2_w + 16

    # Col 1: The Challenge
    add_text(slide, "col-1-header", "THE CHALLENGE",
             x_px=cx1, y_px=body_top, w_px=col1_w, h_px=18,
             font_size_px=10, color=TEXT_FAINT, bold=True, uppercase=True)
    add_rect(slide, "col-1-rule", cx1, body_top + 20, col1_w, 1, CARD_BORDER)
    challenges = [
        ("Fragmented Processes", "Siloed teams operate on disconnected workflows, creating costly hand-off delays and version errors."),
        ("Limited Visibility", "Leadership lacks real-time data to make confident decisions, relying on lagging weekly reports."),
        ("Slow Time-to-Market", "Manual approvals and legacy tooling extend delivery cycles well beyond competitive benchmarks."),
    ]
    cy = body_top + 36
    for i, (head, body) in enumerate(challenges):
        # Marker
        add_text(slide, f"challenge-{i+1}-marker", "✗",
                 x_px=cx1, y_px=cy, w_px=18, h_px=18,
                 font_size_px=10, color=X_TXT, bold=True, align="center", anchor="middle",
                 bg_fill=X_BG, padding_px=(0, 0, 0, 0))
        add_text(slide, f"challenge-{i+1}-heading", head,
                 x_px=cx1 + 26, y_px=cy, w_px=col1_w - 26, h_px=16,
                 font_size_px=11, color=BRAND_PRIMARY, bold=True)
        add_text(slide, f"challenge-{i+1}-body", body,
                 x_px=cx1 + 26, y_px=cy + 18, w_px=col1_w - 26, h_px=68,
                 font_size_px=11, color=TEXT_DARK)
        cy += 110

    # Col 2: Our Solution (center, highlighted)
    sol_bg = add_rect(slide, "col-2-bg", cx2, body_top, col2_w, body_h, CARD_BG)
    sol_bg.line.color.rgb = CARD_BORDER
    sol_bg.line.width = 9525
    add_rect(slide, "col-2-left-border", cx2, body_top, 2, body_h, BRAND_PRIMARY_MID)
    add_rect(slide, "col-2-right-border", cx2 + col2_w - 2, body_top, 2, body_h, BRAND_PRIMARY_MID)
    add_text(slide, "col-2-header", "OUR SOLUTION",
             x_px=cx2 + 16, y_px=body_top + 16, w_px=col2_w - 32, h_px=18,
             font_size_px=10, color=BRAND_PRIMARY_MID, bold=True, uppercase=True)
    add_rect(slide, "col-2-rule", cx2 + 16, body_top + 36, col2_w - 32, 1, BRAND_PRIMARY_MID)
    add_text(slide, "solution-name", "Accenture Intelligent Operations Platform",
             x_px=cx2 + 16, y_px=body_top + 50, w_px=col2_w - 32, h_px=22,
             font_size_px=14, color=BRAND_PRIMARY, bold=True)
    add_text(slide, "solution-desc",
             "A cloud-native, AI-augmented platform that unifies your end-to-end operating model — connecting people, processes, and data in a single pane of glass. Embedded intelligence surfaces exceptions before they escalate, and modular architecture means you go live in weeks, not years.",
             x_px=cx2 + 16, y_px=body_top + 76, w_px=col2_w - 32, h_px=110,
             font_size_px=11, color=TEXT_MID)
    add_text(slide, "capabilities-label", "CORE CAPABILITIES",
             x_px=cx2 + 16, y_px=body_top + 196, w_px=col2_w - 32, h_px=14,
             font_size_px=9, color=TEXT_FAINT, bold=True, uppercase=True)
    capabilities = [
        "Unified Data & Process Orchestration",
        "AI-Powered Decision Intelligence",
        "Modular, Cloud-Ready Architecture",
    ]
    chip_y = body_top + 216
    for i, cap in enumerate(capabilities):
        cy = chip_y + i * 38
        add_rect(slide, f"capability-{i+1}-bg", cx2 + 16, cy, col2_w - 32, 28, BRAND_ACCENT_SOFT)
        add_rect(slide, f"capability-{i+1}-icon-bg", cx2 + 22, cy + 6, 16, 16, BRAND_ACCENT)
        add_text(slide, f"capability-{i+1}", cap,
                 x_px=cx2 + 46, y_px=cy + 6, w_px=col2_w - 64, h_px=18,
                 font_size_px=11, color=BRAND_PRIMARY, bold=True)

    # Col 3: Key Benefits
    add_text(slide, "col-3-header", "KEY BENEFITS",
             x_px=cx3, y_px=body_top, w_px=col3_w, h_px=18,
             font_size_px=10, color=TEXT_FAINT, bold=True, uppercase=True)
    add_rect(slide, "col-3-rule", cx3, body_top + 20, col3_w, 1, CARD_BORDER)
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
                 font_size_px=11, color=BRAND_PRIMARY, bold=True)
        add_text(slide, f"benefit-{i+1}-body", body,
                 x_px=cx3 + 26, y_px=cy + 18, w_px=col3_w - 26, h_px=50,
                 font_size_px=11, color=TEXT_DARK)
        add_text(slide, f"benefit-{i+1}-metric", metric,
                 x_px=cx3 + 26, y_px=cy + 72, w_px=110, h_px=18,
                 font_size_px=10, color=WHITE, bold=True, align="center",
                 bg_fill=BRAND_PRIMARY, padding_px=(2, 8, 2, 8))
        cy += 110

    # Convergence bar
    conv_y = 580
    add_rect(slide, "convergence-bg", 64, conv_y, 1280 - 128, 28, BRAND_PRIMARY)
    add_text(slide, "convergence",
             "Proven across 40+ deployments — ready to activate in 8 weeks.",
             x_px=64, y_px=conv_y, w_px=1280 - 128, h_px=28,
             font_size_px=11, color=WHITE, bold=True, align="center", anchor="middle")

    add_footer(slide, page_num=197)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "197_solution-overview.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
