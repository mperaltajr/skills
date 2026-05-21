"""
Builder for pattern 347: Dark Market Landscape.

Source HTML: _pattern-library/347_dark-market-landscape.html
Standalone — closest dark sibling: 271_competitive-landscape-dark.

Layout: 3-column body — Market Size card (left, with TAM stat, CAGR badge,
drivers); Competitive Landscape card (middle, 5 competitors with logo +
pills + revenue, Our Position highlighted); Opportunity card (right, 3 opps
with growth indicator).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect, px_to_emu,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)
ACCENT_GREEN = RGBColor(0x22, 0xC5, 0x5E)

PILL_BLUE = RGBColor(0x25, 0x63, 0xEB)
PILL_GREEN = RGBColor(0x22, 0xC5, 0x5E)
PILL_PURPLE = RGBColor(0x7C, 0x3A, 0xED)
PILL_ORANGE = RGBColor(0xEA, 0x43, 0x35)
PILL_PINK = RGBColor(0xEC, 0x48, 0x99)


def add_oval(slide, name, x, y, size, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                 px_to_emu(x), px_to_emu(y),
                                 px_to_emu(size), px_to_emu(size))
    sh.name = name
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def pill(slide, name, x, y, w, h, label, color):
    p = add_rect(slide, name + "-bg", x, y, w, h, CARD_BG_DARK)
    p.line.color.rgb = color
    p.line.width = 6350
    add_text(slide, name, label,
             x_px=x, y_px=y, w_px=w, h_px=h,
             font_size_px=8, color=color, bold=True,
             align="center", anchor="middle")


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title
    add_text(slide, "title",
             "Enterprise AI Platform Market: <strong>Competitive Landscape</strong> & White Space",
             x_px=64, y_px=20, w_px=1152, h_px=80,
             font_size_px=28, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Market dynamics, player positioning, and underserved opportunity segments — FY2026",
             x_px=64, y_px=108, w_px=1100, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    body_y = 160
    body_h = 500
    gap = 14
    col_w = (1152 - 2 * gap) // 3

    # --- Market size card (left) ---
    lx = 64
    c = add_rect(slide, "market-bg", lx, body_y, col_w, body_h, CARD_BG_DARK)
    c.line.color.rgb = CARD_BORDER_DARK
    c.line.width = 9525
    add_text(slide, "market-label", "MARKET SIZE",
             x_px=lx + 18, y_px=body_y + 16, w_px=col_w - 36, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1.5)
    add_text(slide, "market-stat", "$184B",
             x_px=lx + 18, y_px=body_y + 40, w_px=col_w - 36, h_px=56,
             font_size_px=44, color=WHITE, bold=True)
    add_text(slide, "market-stat-label", "Total Addressable Market, 2025E",
             x_px=lx + 18, y_px=body_y + 96, w_px=col_w - 36, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_MID)
    # CAGR badge
    cagr_y = body_y + 124
    bg2 = add_rect(slide, "cagr-bg", lx + 18, cagr_y, 80, 24, CARD_BG_DARK)
    bg2.line.color.rgb = ACCENT_GREEN
    bg2.line.width = 9525
    add_text(slide, "cagr-badge", "▲ 34%",
             x_px=lx + 18, y_px=cagr_y, w_px=80, h_px=24,
             font_size_px=12, color=ACCENT_GREEN, bold=True,
             align="center", anchor="middle")
    add_text(slide, "cagr-label", "5-yr CAGR (2025–2030)",
             x_px=lx + 106, y_px=cagr_y, w_px=col_w - 130, h_px=24,
             font_size_px=11, color=TEXT_ON_DARK_MID, anchor="middle")
    # drivers
    add_text(slide, "drivers-heading", "KEY MARKET DRIVERS",
             x_px=lx + 18, y_px=body_y + 168, w_px=col_w - 36, h_px=14,
             font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1.5)
    drivers = [
        "Generative AI adoption accelerating across regulated industries, compressing legacy vendor cycles",
        "Enterprise governance mandates driving demand for auditable, explainable AI platforms",
        "Hyperscaler commoditisation pushing differentiation toward vertical-specific orchestration layers",
    ]
    for i, d in enumerate(drivers):
        dy = body_y + 190 + i * 100
        add_rect(slide, f"drv-{i+1}-dot", lx + 18, dy + 6, 6, 6, BRAND_ACCENT)
        add_text(slide, f"drv-{i+1}-text", d,
                 x_px=lx + 30, y_px=dy, w_px=col_w - 48, h_px=90,
                 font_size_px=11, color=WHITE)

    # --- Competitive landscape (middle) ---
    mx = lx + col_w + gap
    c = add_rect(slide, "comp-bg", mx, body_y, col_w, body_h, CARD_BG_DARK)
    c.line.color.rgb = CARD_BORDER_DARK
    c.line.width = 9525
    add_text(slide, "comp-label", "COMPETITIVE LANDSCAPE",
             x_px=mx + 18, y_px=body_y + 16, w_px=col_w - 36, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1.5)
    competitors = [
        ("M", PILL_BLUE, "Microsoft Azure AI",
         [("Cloud Infra", PILL_BLUE), ("Enterprise Suite", PILL_GREEN)],
         "≈$62B revenue", False),
        ("G", RGBColor(0xEA, 0x43, 0x35), "Google Vertex AI",
         [("Cloud Infra", PILL_BLUE), ("MLOps", PILL_PURPLE)],
         "≈$38B revenue", False),
        ("A", RGBColor(0xFF, 0x99, 0x00), "AWS SageMaker",
         [("Cloud Infra", PILL_ORANGE), ("Data Platform", PILL_GREEN)],
         "≈$29B revenue", False),
        ("AC", BRAND_ACCENT, "Accenture AI Platform",
         [("Vertical AI", BRAND_ACCENT), ("Managed Services", BRAND_ACCENT)],
         "≈$9B revenue", True),
        ("S", PILL_PURPLE, "Salesforce Einstein",
         [("CRM AI", PILL_PURPLE), ("Automation", PILL_PINK)],
         "≈$11B revenue", False),
    ]
    comp_top = body_y + 40
    row_h = (body_h - 56) // 5
    for i, (init, col, name, pills, rev, is_us) in enumerate(competitors):
        ry = comp_top + i * row_h
        if is_us:
            hl = add_rect(slide, f"comp-{i+1}-hl", mx + 6, ry, col_w - 12, row_h - 4,
                          BRAND_PRIMARY_MID)
            hl.line.color.rgb = BRAND_ACCENT
            hl.line.width = 9525
        add_oval(slide, f"comp-{i+1}-logo", mx + 18, ry + 8, 30, col)
        add_text(slide, f"comp-{i+1}-init", init,
                 x_px=mx + 18, y_px=ry + 8, w_px=30, h_px=30,
                 font_size_px=11, color=WHITE, bold=True,
                 align="center", anchor="middle")
        add_text(slide, f"comp-{i+1}-name", name,
                 x_px=mx + 56, y_px=ry + 4, w_px=col_w - 80, h_px=18,
                 font_size_px=12, color=WHITE, bold=True)
        # pills
        for k, (lbl, pcol) in enumerate(pills):
            pill(slide, f"comp-{i+1}-pill-{k+1}",
                 mx + 56 + k * 95, ry + 24, 90, 16, lbl, pcol)
        # revenue
        add_text(slide, f"comp-{i+1}-rev", rev,
                 x_px=mx + 56, y_px=ry + 42, w_px=col_w - 80, h_px=14,
                 font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
        if is_us:
            add_text(slide, f"comp-{i+1}-us-label", "OUR POSITION",
                     x_px=mx + col_w - 110, y_px=ry + 6, w_px=92, h_px=14,
                     font_size_px=8, color=BRAND_ACCENT_SOFT, bold=True,
                     align="right", letter_spacing_px=1.2)

    # --- Opportunity (right) ---
    rx = mx + col_w + gap
    c = add_rect(slide, "opp-bg", rx, body_y, col_w, body_h, CARD_BG_DARK)
    c.line.color.rgb = CARD_BORDER_DARK
    c.line.width = 9525
    add_text(slide, "opp-label", "OPPORTUNITY",
             x_px=rx + 18, y_px=body_y + 16, w_px=col_w - 36, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1.5)
    opps = [
        ("Regulated Industry Verticals", "▲ 51%",
         "BFSI, healthcare, and public sector remain underserved by hyperscalers; compliance-first AI platforms command 2–3× pricing premium."),
        ("Sovereign & On-Premise AI", "▲ 44%",
         "Data residency mandates in EU, APAC, and Middle East creating demand for air-gapped deployments no hyperscaler currently addresses at scale."),
        ("AI Governance & Audit Layer", "▲ 67%",
         "Regulatory pressure (EU AI Act, SEC guidance) driving greenfield spend on explainability tooling; no dominant vendor has emerged in this segment."),
    ]
    opp_top = body_y + 40
    opp_h = (body_h - 56) // 3
    for i, (title, growth, body) in enumerate(opps):
        oy = opp_top + i * opp_h
        add_text(slide, f"opp-{i+1}-title", title,
                 x_px=rx + 18, y_px=oy, w_px=col_w - 100, h_px=20,
                 font_size_px=12, color=WHITE, bold=True)
        add_text(slide, f"opp-{i+1}-growth", growth,
                 x_px=rx + col_w - 90, y_px=oy, w_px=72, h_px=20,
                 font_size_px=13, color=ACCENT_GREEN, bold=True, align="right")
        add_text(slide, f"opp-{i+1}-body", body,
                 x_px=rx + 18, y_px=oy + 22, w_px=col_w - 36, h_px=opp_h - 28,
                 font_size_px=10, color=TEXT_ON_DARK_MID)

    # Invariant zone
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "347",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = (Path(__file__).resolve().parents[2] / "_renders" / "twins" /
           "347_dark-market-landscape.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
