"""
Builder for pattern 332: 7-bucket hero-plus-six.

Asymmetric layout — one large hero card on the left with deep description and
metric, plus a 3×2 grid of 6 compact cards on the right.

Source HTML: _pattern-library/332_7bucket-hero-plus-six.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)


def _small_card(slide, n, x, y, w, h, *, num, title, bullets):
    card = add_rect(slide, f"bucket-{n}-card", x, y, w, h, CARD_BG)
    card.line.color.rgb = CARD_BORDER
    card.line.width = 9525
    # Top accent
    add_rect(slide, f"bucket-{n}-top", x, y, w, 2, BRAND_ACCENT)
    # Number
    add_text(slide, f"bucket-{n}-num", num,
             x_px=x + 12, y_px=y + 10, w_px=40, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, letter_spacing_px=1.2)
    # Title
    add_text(slide, f"bucket-{n}-title", title,
             x_px=x + 12, y_px=y + 28, w_px=w - 24, h_px=22,
             font_size_px=11, color=BRAND_PRIMARY, bold=True)
    # Bullets
    by_text = y + 54
    for bi, b in enumerate(bullets):
        bn = bi + 1
        add_text(slide, f"bucket-{n}-bullet-{bn}", "– " + b,
                 x_px=x + 12, y_px=by_text + bi * 22, w_px=w - 24, h_px=22,
                 font_size_px=10, color=TEXT_MID)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Strategic priorities require <strong>one clear focal point</strong>",
        subtitle="How the seven value buckets map to delivery outcomes and measurable client impact",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top

    # Hero card (left, ~38% width)
    hero_w = 440
    hero_h = body_h
    hx = body_left
    hy = body_top
    hero = add_rect(slide, "hero-card", hx, hy, hero_w, hero_h, WHITE)
    hero.line.color.rgb = BRAND_ACCENT
    hero.line.width = 19050
    # Hero accent stripe at top
    add_rect(slide, "hero-top", hx, hy, hero_w, 4, BRAND_ACCENT)
    # Label "Primary driver"
    add_text(slide, "hero-label", "PRIMARY DRIVER · 01",
             x_px=hx + 24, y_px=hy + 20, w_px=hero_w - 48, h_px=18,
             font_size_px=10, color=BRAND_ACCENT, bold=True, letter_spacing_px=1.6)
    # Hero title
    add_text(slide, "hero-title", "Accelerate Core Platform Modernisation",
             x_px=hx + 24, y_px=hy + 46, w_px=hero_w - 48, h_px=66,
             font_size_px=22, color=BRAND_PRIMARY, bold=True)
    # Hero rule
    add_rect(slide, "hero-rule", hx + 24, hy + 124, 48, 3, BRAND_ACCENT)
    # Hero description
    add_text(slide, "hero-desc",
             "Migrate legacy transaction systems to a cloud-native architecture, "
             "reducing operational latency by consolidating data pipelines and "
             "eliminating redundant middleware across all business units.",
             x_px=hx + 24, y_px=hy + 144, w_px=hero_w - 48, h_px=170,
             font_size_px=13, color=TEXT_MID)
    # Hero metric label
    add_text(slide, "hero-metric-label", "PROJECTED EFFICIENCY GAIN",
             x_px=hx + 24, y_px=hy + hero_h - 96, w_px=hero_w - 48, h_px=14,
             font_size_px=10, color=TEXT_FAINT, bold=True, letter_spacing_px=1.4)
    # Hero metric value
    add_text(slide, "hero-metric", "↑ 43%",
             x_px=hx + 24, y_px=hy + hero_h - 76, w_px=hero_w - 48, h_px=56,
             font_size_px=42, color=BRAND_ACCENT, bold=True)

    # Right grid: 3 cols × 2 rows = 6 small cards
    right_x = hx + hero_w + 16
    right_w = body_w - hero_w - 16
    cols = 3
    rows = 2
    gap_x = 12
    gap_y = 12
    sw = (right_w - (cols - 1) * gap_x) // cols
    sh = (body_h - (rows - 1) * gap_y) // rows

    cards = [
        ("02", "Data Governance & Quality",
         ["Establish single source of truth across domains",
          "Automate data lineage and classification tagging"]),
        ("03", "Workforce Enablement",
         ["Deploy role-based learning paths at scale",
          "Reduce onboarding time by 30% via tooling"]),
        ("04", "Cybersecurity Posture",
         ["Zero-trust architecture across all endpoints",
          "Continuous threat monitoring and response"]),
        ("05", "Customer Experience",
         ["Unify digital channels into one journey layer",
          "Real-time personalisation at touchpoints"]),
        ("06", "Sustainability Metrics",
         ["Carbon reporting integrated in financial close",
          "Scope 3 supplier data ingestion pipeline"]),
        ("07", "Innovation Velocity",
         ["Accelerate idea-to-pilot cycle to under 6 weeks",
          "Dedicated sandbox with production data proxies"]),
    ]
    for i, (num, title, bullets) in enumerate(cards):
        n = i + 2  # buckets are 02..07
        col = i % cols
        row = i // cols
        cx = right_x + col * (sw + gap_x)
        cy = body_top + row * (sh + gap_y)
        _small_card(slide, n, cx, cy, sw, sh, num=num, title=title, bullets=bullets)

    add_footer(slide, page_num=332)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "332_7bucket-hero-plus-six.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
