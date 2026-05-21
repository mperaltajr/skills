"""
Builder for pattern 163: Architecture stack (cloud) — IaaS/PaaS/SaaS/Users + annotations.

Source HTML: _pattern-library/163_architecture-stack-cloud.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

IAAS_BG = RGBColor(0x3A, 0x12, 0x60)
PAAS_BG = RGBColor(0x6B, 0x38, 0x99)
SAAS_BG = CARD_BG
USERS_BG = WHITE
CHIP_LIGHT_PURPLE = RGBColor(0xED, 0xE0, 0xFB)
CHIP_DARK = RGBColor(0xC0, 0x80, 0xFF)
ANNOT_BG = {
    "users": RGBColor(0xFA, 0xFA, 0xFA),
    "saas":  RGBColor(0xF7, 0xEC, 0xFA),
    "paas":  RGBColor(0xEC, 0xE0, 0xF4),
    "iaas":  RGBColor(0xF3, 0xE7, 0xFC),
}


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Title (28px brand-primary, "Layer by Layer" brand-accent)
    add_text(slide, "title", "Cloud Architecture Stack — <strong>Layer by Layer</strong>",
             x_px=48, y_px=58, w_px=1100, h_px=36,
             font_size_px=26, color=BRAND_PRIMARY, bold=True,
             emphasis_color=BRAND_ACCENT)
    add_text(slide, "subtitle",
             "Mapping IaaS, PaaS, and SaaS services to business consumption patterns",
             x_px=48, y_px=96, w_px=900, h_px=18,
             font_size_px=12, color=TEXT_MID, italic=True)
    add_rect(slide, "brand-rule", 48, 122, 64, 3, BRAND_ACCENT)

    # Content area: top:138 left:48 right:48 bottom:64
    ca_x = 48
    ca_y = 138
    ca_w = 1280 - 96
    ca_h = 720 - 64 - ca_y

    # Arrow column (28 wide)
    arrow_x = ca_x
    arrow_w = 28
    add_rect(slide, "arrow-shaft", arrow_x + 12, ca_y + 20, 3, ca_h - 40,
             BRAND_PRIMARY_MID)
    add_text(slide, "arrow-head", "▲",
             x_px=arrow_x, y_px=ca_y + 4, w_px=arrow_w, h_px=16,
             font_size_px=14, color=BRAND_ACCENT, align="center")
    add_text(slide, "arrow-label", "ABSTRACTION",
             x_px=arrow_x, y_px=ca_y + ca_h // 2 - 8, w_px=arrow_w, h_px=16,
             font_size_px=7, color=BRAND_PRIMARY_MID, bold=True, align="center", uppercase=True)

    # Layers (right of arrow, before annotations)
    annot_w = 220
    layers_x = arrow_x + arrow_w + 12
    layers_w = ca_w - arrow_w - 12 - annot_w - 14
    layer_h = (ca_h - 18) // 4  # 4 layers stacked
    layer_gap = 6
    layer_top_h = layer_h - layer_gap

    layers = [
        ("users", "Users", USERS_BG, BRAND_PRIMARY, BRAND_PRIMARY,
         ["Web Browser", "Mobile App", "API Client", "Partner Portal"]),
        ("saas", "SaaS", SAAS_BG, BRAND_PRIMARY, BRAND_PRIMARY,
         ["Microsoft 365", "Salesforce", "ServiceNow", "Workday", "Power BI"]),
        ("paas", "PaaS", PAAS_BG, WHITE, WHITE,
         ["Azure App Service", "Cloud Run", "AWS Lambda", "Azure SQL", "API Mgmt"]),
        ("iaas", "IaaS", IAAS_BG, WHITE, WHITE,
         ["VMs / Compute", "Virtual Network", "Blob Storage", "Load Balancer", "DNS / CDN"]),
    ]
    for i, (key, label, bg, label_color, chip_text_color, chips) in enumerate(layers):
        ly = ca_y + i * layer_h
        layer = add_rect(slide, f"layer-{key}-bg", layers_x, ly, layers_w, layer_top_h, bg)
        layer.line.color.rgb = CARD_BORDER if bg in (USERS_BG, SAAS_BG) else bg
        layer.line.width = 9525
        # Label
        add_text(slide, f"layer-{key}-label", label,
                 x_px=layers_x + 14, y_px=ly, w_px=80, h_px=layer_top_h,
                 font_size_px=11, color=label_color, bold=True, anchor="middle", uppercase=True)
        # Chips
        chips_text = "  •  ".join(chips)
        add_text(slide, f"layer-{key}-chips", chips_text,
                 x_px=layers_x + 100, y_px=ly, w_px=layers_w - 110, h_px=layer_top_h,
                 font_size_px=10, color=chip_text_color, anchor="middle")

    # Annotation column (right)
    annot_x = layers_x + layers_w + 14
    for i, (key, _label, _bg, _lc, _ctc, _chips) in enumerate(layers):
        ay = ca_y + i * layer_h
        annot = add_rect(slide, f"annot-{key}-bg", annot_x, ay, annot_w, layer_top_h, ANNOT_BG[key])
        annot.line.fill.background()
        # Left accent
        accent_color = {
            "users": CARD_BORDER, "saas": BRAND_ACCENT_SOFT,
            "paas": BRAND_PRIMARY_MID, "iaas": BRAND_ACCENT,
        }[key]
        add_rect(slide, f"annot-{key}-accent", annot_x, ay, 3, layer_top_h, accent_color)
        # Title
        titles = {"users": "Presentation", "saas": "Software as a Service",
                  "paas": "Platform as a Service", "iaas": "Infrastructure as a Service"}
        add_text(slide, f"annot-{key}-label", titles[key],
                 x_px=annot_x + 14, y_px=ay + 6, w_px=annot_w - 28, h_px=14,
                 font_size_px=9, color=accent_color, bold=True, uppercase=True)
        # Body
        bodies = {
            "users": "End-user touchpoints consuming services via browser, mobile, or third-party integrations.",
            "saas":  "Fully managed applications. No infra ownership; consumed via subscription and configured, not coded.",
            "paas":  "Managed runtimes, databases, and middleware. Teams deploy code; cloud owns OS patching and scaling.",
            "iaas":  "Raw compute, storage, and networking. Maximum control; team is responsible for OS, patching, and HA.",
        }
        add_text(slide, f"annot-{key}-body", bodies[key],
                 x_px=annot_x + 14, y_px=ay + 22, w_px=annot_w - 28, h_px=layer_top_h - 26,
                 font_size_px=9, color=TEXT_MID)

    add_footer(slide, page_num=163)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "163_architecture-stack-cloud.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
