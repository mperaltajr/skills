"""
Builder for pattern 350: Dark Solution Architecture (layered stack).

Source HTML: _pattern-library/350_dark-solution-architecture.html
Standalone — closest light reference: 71_reference-architecture-layers.

Layout: left column — title + 5-layer architecture stack (UX → API →
Services → Data → Infra) with pills per layer. Right column — design
principles card (4 items) + technology partners strip.
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


def add_oval(slide, name, x, y, size, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                 px_to_emu(x), px_to_emu(y),
                                 px_to_emu(size), px_to_emu(size))
    sh.name = name
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title
    add_text(slide, "title",
             "End-to-End <strong>Solution Architecture</strong>",
             x_px=64, y_px=20, w_px=900, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Layered platform design — cloud-native, API-first, event-driven",
             x_px=64, y_px=108, w_px=900, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    # --- Architecture stack (left) ---
    sx = 64
    sy = 160
    sw = 720
    layer_h = 80
    gap = 12
    layers = [
        ("UX", "User Interface",
         ["React / Next.js", "Design System", "Accessibility"],
         RGBColor(0x5E, 0x35, 0x88)),
        ("API", "Integration",
         ["API Gateway", "Event Bus", "Auth / OAuth"],
         RGBColor(0x4A, 0x2E, 0x70)),
        ("SERVICES", "Application",
         ["Microservices", "Workflow Engine", "AI / ML Core"],
         RGBColor(0x3C, 0x28, 0x60)),
        ("DATA", "Platform",
         ["Data Lakehouse", "Streaming", "Data Mesh"],
         RGBColor(0x32, 0x20, 0x52)),
        ("INFRA", "Cloud",
         ["Kubernetes", "IaC / Terraform", "Zero-Trust"],
         RGBColor(0x28, 0x18, 0x44)),
    ]
    for i, (lbl, name, pills, color) in enumerate(layers):
        ly = sy + i * (layer_h + gap)
        c = add_rect(slide, f"layer-{i+1}-bg", sx, ly, sw, layer_h, color)
        c.line.color.rgb = BRAND_ACCENT_SOFT
        c.line.width = 6350
        # Left accent strip
        add_rect(slide, f"layer-{i+1}-strip", sx, ly, 4, layer_h, BRAND_ACCENT)
        # Layer label (e.g., "UX")
        add_text(slide, f"layer-{i+1}-label", lbl,
                 x_px=sx + 16, y_px=ly + 12, w_px=110, h_px=24,
                 font_size_px=15, color=BRAND_ACCENT_SOFT, bold=True,
                 uppercase=True, letter_spacing_px=1.5)
        # Layer name
        add_text(slide, f"layer-{i+1}-name", name,
                 x_px=sx + 16, y_px=ly + 38, w_px=110, h_px=22,
                 font_size_px=13, color=WHITE)
        # Pills
        pill_x_start = sx + 150
        pill_y = ly + (layer_h - 28) // 2
        for k, p in enumerate(pills):
            px = pill_x_start + k * 180
            is_key = (k == 0)
            pcol = BRAND_ACCENT if is_key else BRAND_PRIMARY_MID
            tcol = WHITE if is_key else TEXT_ON_DARK_MID
            pl = add_rect(slide, f"layer-{i+1}-pill-{k+1}-bg",
                          px, pill_y, 170, 28, pcol)
            pl.line.fill.background()
            add_text(slide, f"layer-{i+1}-pill-{k+1}", p,
                     x_px=px, y_px=pill_y, w_px=170, h_px=28,
                     font_size_px=11, color=tcol, bold=is_key,
                     align="center", anchor="middle")
        # Down arrow (except after last)
        if i < len(layers) - 1:
            arrow_y = ly + layer_h + 1
            add_rect(slide, f"arrow-{i+1}", sx + sw // 2, arrow_y, 1, gap - 2,
                     TEXT_ON_DARK_FAINT)

    # --- Right column ---
    rx = 800
    ry = 160
    rw = 416
    # Principles card
    pc_h = 360
    pc = add_rect(slide, "principles-bg", rx, ry, rw, pc_h, CARD_BG_DARK)
    pc.line.color.rgb = CARD_BORDER_DARK
    pc.line.width = 9525
    add_text(slide, "principles-title", "KEY DESIGN PRINCIPLES",
             x_px=rx + 18, y_px=ry + 14, w_px=rw - 36, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1.5)
    add_rect(slide, "principles-rule", rx + 18, ry + 34, 28, 2, BRAND_ACCENT)
    principles = [
        ("01", "API-First by Default",
         "Every capability exposed via versioned, documented APIs before any UI is built."),
        ("02", "Event-Driven Decoupling",
         "Services communicate asynchronously; no direct synchronous dependencies."),
        ("03", "Zero-Trust Security",
         "Identity verified at every layer; least-privilege enforced continuously."),
        ("04", "Observability Built In",
         "Logs, metrics, and traces emitted from day one — not bolted on later."),
    ]
    p_top = ry + 46
    p_h = (pc_h - 56) // 4
    for i, (num, title, desc) in enumerate(principles):
        py = p_top + i * p_h
        add_text(slide, f"p-{i+1}-num", num,
                 x_px=rx + 18, y_px=py, w_px=34, h_px=24,
                 font_size_px=18, color=BRAND_ACCENT, bold=True)
        add_text(slide, f"p-{i+1}-title", title,
                 x_px=rx + 56, y_px=py, w_px=rw - 74, h_px=18,
                 font_size_px=12, color=WHITE, bold=True)
        add_text(slide, f"p-{i+1}-desc", desc,
                 x_px=rx + 56, y_px=py + 20, w_px=rw - 74, h_px=p_h - 24,
                 font_size_px=10, color=TEXT_ON_DARK_MID)

    # Partners strip
    pt_y = ry + pc_h + 12
    pt_h = 90
    pt = add_rect(slide, "partners-bg", rx, pt_y, rw, pt_h, CARD_BG_DARK)
    pt.line.color.rgb = CARD_BORDER_DARK
    pt.line.width = 9525
    add_text(slide, "partners-label", "TECHNOLOGY PARTNERS",
             x_px=rx + 18, y_px=pt_y + 12, w_px=rw - 36, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1.5)
    partners = [("AWS", "Amazon Web Services"), ("GCP", "Google Cloud"),
                ("AZ", "Microsoft Azure")]
    pp_x = rx + 18
    pp_y = pt_y + 38
    pp_w = (rw - 36) // 3
    for i, (init, name) in enumerate(partners):
        x = pp_x + i * pp_w
        add_oval(slide, f"partner-{i+1}-circle", x, pp_y, 36, BRAND_PRIMARY_MID)
        add_text(slide, f"partner-{i+1}-init", init,
                 x_px=x, y_px=pp_y, w_px=36, h_px=36,
                 font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
                 align="center", anchor="middle")
        add_text(slide, f"partner-{i+1}-name", name,
                 x_px=x + 42, y_px=pp_y, w_px=pp_w - 50, h_px=36,
                 font_size_px=10, color=WHITE, anchor="middle")

    # Invariant zone
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "350",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = (Path(__file__).resolve().parents[2] / "_renders" / "twins" /
           "350_dark-solution-architecture.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
