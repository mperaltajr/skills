"""
Builder for pattern 163d: Architecture stack (cloud) — IaaS/PaaS/SaaS/Users — dark.

Source HTML: _pattern-library/163_architecture-stack-cloud-dark.html
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

IAAS_BG = RGBColor(0x1A, 0x05, 0x30)
PAAS_BG = RGBColor(0x4A, 0x29, 0x76)
SAAS_BG = CARD_BG_DARK
USERS_BG = RGBColor(0x35, 0x1A, 0x52)
ANNOT_BG = {
    "users": RGBColor(0x35, 0x1A, 0x52),
    "saas":  RGBColor(0x3C, 0x1F, 0x5C),
    "paas":  RGBColor(0x4A, 0x29, 0x76),
    "iaas":  RGBColor(0x2A, 0x10, 0x42),
}


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Canonical chrome
    add_text(slide, "title", "Cloud Architecture Stack — <strong>Layer by Layer</strong>",
             x_px=48, y_px=20, w_px=1184, h_px=80,
             font_size_px=26, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Mapping IaaS, PaaS, and SaaS services to business consumption patterns",
             x_px=48, y_px=108, w_px=1184, h_px=22,
             font_size_px=12, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Content area
    ca_x = 48
    ca_y = 220
    ca_w = 1280 - 96
    ca_h = 660 - ca_y

    # Arrow column
    arrow_x = ca_x
    arrow_w = 28
    add_rect(slide, "arrow-shaft", arrow_x + 12, ca_y + 20, 3, ca_h - 40,
             BRAND_ACCENT_SOFT)
    add_text(slide, "arrow-head", "▲",
             x_px=arrow_x, y_px=ca_y + 4, w_px=arrow_w, h_px=16,
             font_size_px=14, color=BRAND_ACCENT, align="center")
    add_text(slide, "arrow-label", "ABSTRACTION",
             x_px=arrow_x, y_px=ca_y + ca_h // 2 - 8, w_px=arrow_w, h_px=16,
             font_size_px=7, color=BRAND_ACCENT_SOFT, bold=True, align="center", uppercase=True)

    # Layers
    annot_w = 220
    layers_x = arrow_x + arrow_w + 12
    layers_w = ca_w - arrow_w - 12 - annot_w - 14
    layer_h = (ca_h - 18) // 4
    layer_gap = 6
    layer_top_h = layer_h - layer_gap

    layers = [
        ("users", "Users", USERS_BG, WHITE, WHITE,
         ["Web Browser", "Mobile App", "API Client", "Partner Portal"]),
        ("saas", "SaaS", SAAS_BG, BRAND_ACCENT_SOFT, WHITE,
         ["Microsoft 365", "Salesforce", "ServiceNow", "Workday", "Power BI"]),
        ("paas", "PaaS", PAAS_BG, WHITE, WHITE,
         ["Azure App Service", "Cloud Run", "AWS Lambda", "Azure SQL", "API Mgmt"]),
        ("iaas", "IaaS", IAAS_BG, WHITE, WHITE,
         ["VMs / Compute", "Virtual Network", "Blob Storage", "Load Balancer", "DNS / CDN"]),
    ]
    for i, (key, label, bg_col, label_color, chip_text_color, chips) in enumerate(layers):
        ly = ca_y + i * layer_h
        layer = add_rect(slide, f"layer-{key}-bg", layers_x, ly, layers_w, layer_top_h, bg_col)
        layer.line.color.rgb = CARD_BORDER_DARK
        layer.line.width = 9525
        add_text(slide, f"layer-{key}-label", label,
                 x_px=layers_x + 14, y_px=ly, w_px=80, h_px=layer_top_h,
                 font_size_px=11, color=label_color, bold=True, anchor="middle", uppercase=True)
        chips_text = "  •  ".join(chips)
        add_text(slide, f"layer-{key}-chips", chips_text,
                 x_px=layers_x + 100, y_px=ly, w_px=layers_w - 110, h_px=layer_top_h,
                 font_size_px=10, color=chip_text_color, anchor="middle")

    # Annotation column
    annot_x = layers_x + layers_w + 14
    for i, (key, _label, _bg, _lc, _ctc, _chips) in enumerate(layers):
        ay = ca_y + i * layer_h
        annot = add_rect(slide, f"annot-{key}-bg", annot_x, ay, annot_w, layer_top_h, ANNOT_BG[key])
        annot.line.fill.background()
        accent_color = {
            "users": TEXT_ON_DARK_FAINT, "saas": BRAND_ACCENT_SOFT,
            "paas": BRAND_ACCENT_SOFT, "iaas": BRAND_ACCENT,
        }[key]
        add_rect(slide, f"annot-{key}-accent", annot_x, ay, 3, layer_top_h, accent_color)
        titles = {"users": "Presentation", "saas": "Software as a Service",
                  "paas": "Platform as a Service", "iaas": "Infrastructure as a Service"}
        add_text(slide, f"annot-{key}-label", titles[key],
                 x_px=annot_x + 14, y_px=ay + 6, w_px=annot_w - 28, h_px=14,
                 font_size_px=9, color=accent_color, bold=True, uppercase=True)
        bodies = {
            "users": "End-user touchpoints consuming services via browser, mobile, or third-party integrations.",
            "saas":  "Fully managed applications. No infra ownership; consumed via subscription and configured, not coded.",
            "paas":  "Managed runtimes, databases, and middleware. Teams deploy code; cloud owns OS patching and scaling.",
            "iaas":  "Raw compute, storage, and networking. Maximum control; team is responsible for OS, patching, and HA.",
        }
        add_text(slide, f"annot-{key}-body", bodies[key],
                 x_px=annot_x + 14, y_px=ay + 22, w_px=annot_w - 28, h_px=layer_top_h - 26,
                 font_size_px=9, color=TEXT_ON_DARK_MID)

    # Dark source + page number
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "163",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")

    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "163d_architecture-stack-cloud.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
