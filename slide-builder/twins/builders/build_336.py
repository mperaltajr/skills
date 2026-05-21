"""
Builder for pattern 336: 8-bucket 4x2 grid (4 cols × 2 rows).

Compact cards with number, title, 2 short bullets, and a colored metric on a
"label + value" line.

Source HTML: _pattern-library/336_8bucket-4x2-grid.html
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


def _bucket_card(slide, n, x, y, w, h, *, num, title, bullets, metric, metric_label):
    card = add_rect(slide, f"bucket-{n}-card", x, y, w, h, CARD_BG)
    card.line.color.rgb = CARD_BORDER
    card.line.width = 9525
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
    by_text = y + 56
    for bi, b in enumerate(bullets):
        bn = bi + 1
        add_text(slide, f"bucket-{n}-bullet-{bn}", "– " + b,
                 x_px=x + 12, y_px=by_text + bi * 22, w_px=w - 24, h_px=22,
                 font_size_px=10, color=TEXT_MID)
    # Metric line
    metric_y = y + h - 36
    add_rect(slide, f"bucket-{n}-rule", x + 12, metric_y, w - 24, 1, CARD_BORDER)
    add_text(slide, f"bucket-{n}-metric", metric,
             x_px=x + 12, y_px=metric_y + 6, w_px=70, h_px=20,
             font_size_px=14, color=BRAND_ACCENT, bold=True)
    add_text(slide, f"bucket-{n}-metric-label", metric_label,
             x_px=x + 12 + 70, y_px=metric_y + 8, w_px=w - 24 - 70, h_px=18,
             font_size_px=10, color=TEXT_MID)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Eight dimensions of <strong>strategic transformation</strong>",
        subtitle="A structured view across capability domains — each bucket maps to a discrete workstream and owner.",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap_x = 12
    gap_y = 12
    cols = 4
    rows = 2
    card_w = (body_w - (cols - 1) * gap_x) // cols
    card_h = (body_h - (rows - 1) * gap_y) // rows

    buckets = [
        ("01", "Operating Model",
         ["Redesign spans & layers for speed",
          "Shift from matrix to product pods"],
         "−22%", "decision latency"),
        ("02", "Talent & Skills",
         ["Reskill 40% of workforce by Q4",
          "AI-fluency baseline for all roles"],
         "3,400", "FTEs in scope"),
        ("03", "Data & Analytics",
         ["Unified data mesh across 6 domains",
          "Self-serve BI for senior leadership"],
         "85%", "data trust score"),
        ("04", "Technology Core",
         ["Migrate 70% workloads to cloud",
          "Decommission 14 legacy systems"],
         "$18M", "run-rate savings"),
        ("05", "Customer Experience",
         ["Omnichannel journey re-architecture",
          "Personalisation engine at scale"],
         "+14pt", "NPS improvement"),
        ("06", "Process Excellence",
         ["Automate 60% of back-office tasks",
          "Lean Six Sigma wave 2 rollout"],
         "−31%", "cycle time"),
        ("07", "Risk & Compliance",
         ["Real-time controls monitoring layer",
          "Regulatory change mgmt. playbook"],
         "0", "material findings"),
        ("08", "Innovation Pipeline",
         ["Venture studio: 12 concepts in flight",
          "IP portfolio review & spin-out options"],
         "×2.4", "R&D yield target"),
    ]
    for i, (num, title, bullets, metric, mlabel) in enumerate(buckets):
        n = i + 1
        col = i % cols
        row = i // cols
        cx = body_left + col * (card_w + gap_x)
        cy = body_top + row * (card_h + gap_y)
        _bucket_card(slide, n, cx, cy, card_w, card_h,
                     num=num, title=title, bullets=bullets,
                     metric=metric, metric_label=mlabel)

    add_footer(slide, page_num=336)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "336_8bucket-4x2-grid.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
