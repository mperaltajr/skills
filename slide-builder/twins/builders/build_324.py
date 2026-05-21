"""
Builder for pattern 324: 5-bucket horizontal strip (with fade in step opacity).

Same horizontal-strip treatment as 321, but with 5 buckets and a sequential
step number that fades from 100% to 60%.

Source HTML: _pattern-library/324_5bucket-horizontal-strip.html
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
from pptx.dml.color import RGBColor


def _fade(opacity):
    # Approximate fade by lightening BRAND_ACCENT_SOFT toward white
    r = int(0xC7 + (0xFF - 0xC7) * (1 - opacity))
    g = int(0x80 + (0xFF - 0x80) * (1 - opacity))
    b = int(0xFF + (0xFF - 0xFF) * (1 - opacity))
    return RGBColor(min(r, 255), min(g, 255), min(b, 255))


def _bucket_card(slide, n, x, y, w, h, *, step_num, step_opacity, title, bullets,
                 metric, metric_label):
    card = add_rect(slide, f"bucket-{n}-card", x, y, w, h, CARD_BG)
    card.line.color.rgb = CARD_BORDER
    card.line.width = 9525
    # Step number (large, with opacity)
    add_text(
        slide, f"bucket-{n}-step", step_num,
        x_px=x + 14, y_px=y + 14, w_px=80, h_px=50,
        font_size_px=44, color=_fade(step_opacity), bold=True,
    )
    # Title
    add_text(
        slide, f"bucket-{n}-title", title,
        x_px=x + 14, y_px=y + 72, w_px=w - 28, h_px=40,
        font_size_px=13, color=BRAND_PRIMARY, bold=True,
    )
    # Rule
    add_rect(slide, f"bucket-{n}-rule", x + 14, y + 116, w - 28, 2, BRAND_ACCENT)
    # Bullets
    bullets_y = y + 130
    for bi, b in enumerate(bullets):
        bn = bi + 1
        by = bullets_y + bi * 40
        add_text(
            slide, f"bucket-{n}-bullet-{bn}-dot", "·",
            x_px=x + 14, y_px=by - 4, w_px=10, h_px=20,
            font_size_px=14, color=BRAND_ACCENT_SOFT, bold=True,
        )
        add_text(
            slide, f"bucket-{n}-bullet-{bn}-text", b,
            x_px=x + 26, y_px=by, w_px=w - 40, h_px=38,
            font_size_px=10, color=TEXT_MID,
        )
    # Metric (separated by top rule)
    metric_y = y + h - 60
    add_rect(slide, f"bucket-{n}-metric-rule", x + 14, metric_y, w - 28, 1, CARD_BORDER)
    add_text(
        slide, f"bucket-{n}-metric", metric,
        x_px=x + 14, y_px=metric_y + 8, w_px=w - 28, h_px=24,
        font_size_px=18, color=BRAND_ACCENT, bold=True,
    )
    add_text(
        slide, f"bucket-{n}-metric-label", metric_label.upper(),
        x_px=x + 14, y_px=metric_y + 34, w_px=w - 28, h_px=14,
        font_size_px=9, color=TEXT_FAINT, letter_spacing_px=1.0,
    )


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Five dimensions that <strong>define delivery excellence</strong>",
        subtitle="A sequential framework for building high-performance program operations",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    body_top = 200
    body_left = 48
    body_w = 1184
    body_h = 720 - 32 - 14 - body_top
    gap = 10
    card_w = (body_w - 4 * gap) // 5

    buckets = [
        ("01", 1.00, "Mobilise & Align",
         ["Establish governance charter and RACI",
          "Confirm programme scope and boundaries",
          "Onboard key stakeholders and sponsors"],
         "Week 1–2", "Target window"),
        ("02", 0.90, "Plan & Sequence",
         ["Decompose milestones into workstreams",
          "Identify critical path and float buffers",
          "Lock resource assignments per sprint"],
         "94%", "Plan accuracy target"),
        ("03", 0.80, "Execute & Track",
         ["Run bi-weekly delivery checkpoints",
          "Surface blockers within 24-hour SLA",
          "Maintain live RAG status dashboard"],
         "≤48 hrs", "Issue resolution SLA"),
        ("04", 0.70, "Measure & Learn",
         ["Capture velocity and cycle time data",
          "Run retrospectives every two sprints",
          "Integrate learnings into next iteration"],
         "+18%", "Velocity improvement"),
        ("05", 0.60, "Scale & Sustain",
         ["Embed operating model in BAU teams",
          "Transition tooling ownership to client",
          "Define success criteria for steady state"],
         "Q3 2026", "Steady-state target"),
    ]
    for i, (num, op, title, bullets, metric, mlabel) in enumerate(buckets):
        n = i + 1
        cx = body_left + i * (card_w + gap)
        _bucket_card(
            slide, n, cx, body_top, card_w, body_h,
            step_num=num, step_opacity=op, title=title, bullets=bullets,
            metric=metric, metric_label=mlabel,
        )

    add_footer(slide, page_num=324)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "324_5bucket-horizontal-strip.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
