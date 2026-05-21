"""
Builder for pattern 179: Anchored Quote + Chart pairing.

Source HTML: _pattern-library/179_anchored-quote-chart-pairing.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT,
)
from pptx.dml.color import RGBColor

TRACK_BG = RGBColor(0xED, 0xE8, 0xF4)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Employee trust is the <strong>new performance currency</strong>",
        subtitle="Survey data shows alignment between leadership sentiment and workforce confidence scores",
        title_h=42,
        subtitle_h=20,
        brand_rule_w=64,
    )

    # Body: 40/60 split
    body_top = 156
    body_bottom = 720 - 72
    body_left = 48
    body_w = 1280 - 96
    gap = 28
    quote_w = int((body_w - gap) * 0.40)
    chart_w = body_w - gap - quote_w

    # ----- Quote panel
    qx = body_left
    qy = body_top
    qh = body_bottom - body_top
    quote = add_rect(slide, "quote-card", qx, qy, quote_w, qh, CARD_BG)
    quote.line.fill.background()
    add_rect(slide, "quote-accent", qx, qy, 4, qh, BRAND_ACCENT)

    add_text(slide, "quote-mark", "“",
             x_px=qx + 24, y_px=qy + 12, w_px=60, h_px=60,
             font_size_px=56, color=BRAND_ACCENT, bold=True, font_name="Georgia")
    add_text(slide, "quote-text",
             "When people trust that their leaders are being honest with them, performance outcomes follow naturally. Culture isn't a soft metric — it's the leading indicator every board should be watching.",
             x_px=qx + 24, y_px=qy + 78, w_px=quote_w - 48, h_px=qh - 160,
             font_size_px=15, color=BRAND_PRIMARY_MID, italic=True)
    add_text(slide, "quote-attribution-name", "Sarah Okonkwo",
             x_px=qx + 24, y_px=qy + qh - 48, w_px=quote_w - 48, h_px=16,
             font_size_px=12, color=TEXT_MID, bold=True)
    add_text(slide, "quote-attribution-role", "Chief People Officer, Global Enterprise Survey 2026",
             x_px=qx + 24, y_px=qy + qh - 30, w_px=quote_w - 48, h_px=14,
             font_size_px=11, color=TEXT_MID, italic=True)

    # ----- Chart panel
    cx = body_left + quote_w + gap
    cy = body_top
    add_text(slide, "chart-title",
             "% Employees who strongly agree — Workforce Confidence Survey 2026 (n = 4,200)",
             x_px=cx, y_px=cy, w_px=chart_w, h_px=18,
             font_size_px=11, color=TEXT_DARK, bold=True)

    # 5 bars
    bars = [
        ("Leadership communicates openly", 78, True),
        ("I trust my direct manager", 71, False),
        ("Company vision is clear to me", 64, False),
        ("Feedback leads to real change", 52, False),
        ("Senior leadership walks the talk", 44, False),
    ]
    chart_top = cy + 32
    chart_bot = body_bottom - 24
    chart_h = chart_bot - chart_top
    label_w = 180
    track_x = cx + label_w
    track_w_total = chart_w - label_w - 50  # leave room for value label
    bar_h = 22
    row_h = chart_h // len(bars)

    for i, (label, pct, highlight) in enumerate(bars):
        n = i + 1
        row_y = chart_top + i * row_h + (row_h - bar_h) // 2
        # Label
        add_text(slide, f"bar-{n}-label", label,
                 x_px=cx, y_px=row_y, w_px=label_w - 8, h_px=bar_h,
                 font_size_px=11, color=TEXT_MID, anchor="middle", align="right")
        # Track
        add_rect(slide, f"bar-{n}-track", track_x, row_y, track_w_total, bar_h, TRACK_BG)
        # Fill
        fill_w = int(track_w_total * pct / 100)
        fill_color = BRAND_ACCENT if highlight else BRAND_PRIMARY_MID
        add_rect(slide, f"bar-{n}-bar", track_x, row_y, fill_w, bar_h, fill_color)
        # Value
        add_text(slide, f"bar-{n}-val", f"{pct}%",
                 x_px=track_x + fill_w + 6, y_px=row_y, w_px=44, h_px=bar_h,
                 font_size_px=11, color=TEXT_DARK, bold=True, anchor="middle")

    # X-axis labels at bottom
    axis_y = chart_bot
    ticks = [(0, "0%"), (25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")]
    for pct, label in ticks:
        x = track_x + int(track_w_total * pct / 100)
        add_text(slide, f"x-tick-{pct}", label,
                 x_px=x - 20, y_px=axis_y + 2, w_px=40, h_px=14,
                 font_size_px=9, color=TEXT_FAINT, align="center")

    add_footer(slide, page_num=179)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "179_anchored-quote-chart-pairing.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
