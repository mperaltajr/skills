"""
Builder for pattern 211: Structured text 3 columns (Strengths / Gaps / Opportunities).

Source HTML: _pattern-library/211_structured-text-3col.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_ACCENT, TEXT_DARK, TEXT_MID,
    CARD_BG, CARD_BORDER, WHITE,
)


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Key Findings: <strong>Structured Assessment</strong> Across Three Dimensions",
        subtitle="Diagnostic summary — current-state review · May 2026",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # 3 columns: top:160, left:48, right:48, w=1184, h=496
    cols_top = 160
    col_left = 48
    col_w = 1184 // 3  # ~394 each
    col_h = 496
    col_bgs = [WHITE, CARD_BG, WHITE]
    headings = ["Strengths", "Gaps", "Opportunities"]
    bullets_list = [
        ["Mature operating model with clearly defined ownership across delivery functions",
         "Strong executive sponsorship sustaining multi-year programme momentum",
         "Established data governance framework aligned to regulatory standards",
         "High workforce capability scores in core engineering disciplines",
         "Proven vendor partnerships reducing time-to-deploy on critical platforms"],
        ["Fragmented tooling landscape creating integration overhead and duplicate effort",
         "Insufficient change management capacity relative to transformation scope",
         "Reporting cadence misaligned with decision-making cycles at programme level",
         "Limited cross-functional collaboration between architecture and operations",
         "Underdeveloped succession planning for critical technical roles"],
        ["Consolidate tooling onto unified platform to unlock c.30% efficiency headroom",
         "Accelerate AI-assisted workflows across three high-volume process clusters",
         "Leverage existing data assets for predictive demand planning at scale",
         "Formalise centres of excellence to codify and replicate best practices",
         "Pursue strategic partnership to close skills gap in cloud-native engineering"],
    ]
    metric_values = ["87%", "14", "£4.2M"]
    metric_labels = [
        "Stakeholder alignment score\nacross delivery units",
        "Priority capability gaps\nidentified for remediation",
        "Estimated annual value\nfrom top 3 opportunities",
    ]

    for i in range(3):
        n = i + 1
        cx = col_left + i * col_w
        # Column background
        add_rect(slide, f"pillar-{n}-bg", cx, cols_top, col_w, col_h, col_bgs[i])
        # Vertical divider (between cols)
        if i > 0:
            add_rect(slide, f"col-divider-{i}", cx, cols_top + 8, 1, col_h - 16, CARD_BORDER)
        # Header
        add_text(slide, f"pillar-{n}-name", headings[i],
                 x_px=cx + 20, y_px=cols_top + 18, w_px=col_w - 40, h_px=18,
                 font_size_px=12, color=BRAND_PRIMARY, bold=True, uppercase=True)
        # Header underline
        add_rect(slide, f"pillar-{n}-rule", cx + 20, cols_top + 42, col_w - 40, 1, BRAND_ACCENT)

        # Bullets
        bullets_text = "\n".join(f"• {b}" for b in bullets_list[i])
        add_text(slide, f"pillar-{n}-body", bullets_text,
                 x_px=cx + 20, y_px=cols_top + 56, w_px=col_w - 40, h_px=320,
                 font_size_px=11, color=TEXT_DARK)

        # Metric callout at bottom
        m_y = cols_top + col_h - 90
        add_rect(slide, f"metric-{n}-rule", cx + 20, m_y, col_w - 40, 1, CARD_BORDER)
        add_text(slide, f"metric-{n}-value", metric_values[i],
                 x_px=cx + 20, y_px=m_y + 12, w_px=col_w - 40, h_px=30,
                 font_size_px=24, color=BRAND_PRIMARY, bold=True)
        add_text(slide, f"metric-{n}-label", metric_labels[i],
                 x_px=cx + 20, y_px=m_y + 46, w_px=col_w - 40, h_px=32,
                 font_size_px=10, color=TEXT_MID)

    add_footer(slide, page_num=211)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "211_structured-text-3col.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
