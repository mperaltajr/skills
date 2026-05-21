"""
Builder for pattern 301: Board reporting pack — KPI strip + agenda list + decisions/risks.

Source HTML: _pattern-library/301_board-reporting-pack.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer, add_title_block,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, TEXT_FAINT, WHITE,
)
from pptx.dml.color import RGBColor

RAG_GREEN = RGBColor(0x16, 0xA3, 0x4A)
RAG_AMBER = RGBColor(0xD9, 0x77, 0x06)
RAG_RED = RGBColor(0xDC, 0x26, 0x26)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Board reporting pack — <strong>summary, decisions & risks.</strong>",
        subtitle="Board Pack · Q2 2026 · Pre-read summary for non-executive directors",
        title_x=48, title_y=44, title_w=1184, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # ── KPI strip (5 tiles) ──
    kpi_y = 178
    kpi_h = 76
    kpi_x = 48
    kpi_w = 1184
    strip = add_rect(slide, "kpi-strip", kpi_x, kpi_y, kpi_w, kpi_h, CARD_BG)
    strip.line.color.rgb = CARD_BORDER
    strip.line.width = 9525

    kpis = [
        ("Revenue YTD", "$2.4B", "▲ +8%", "up"),
        ("EBITDA Margin", "22.1%", "▲ +1.4pp", "up"),
        ("Cash Position", "$640M", "▼ −4%", "down"),
        ("NPS Score", "+68", "▲ +5pts", "up"),
        ("Headcount", "12,480", "■ +0.3%", "flat"),
    ]
    tile_w = kpi_w // len(kpis)
    for i, (name, value, delta, direction) in enumerate(kpis):
        n = i + 1
        tx = kpi_x + i * tile_w
        # accent top strip
        add_rect(slide, f"kpi-{n}-accent", tx, kpi_y, tile_w, 3, BRAND_ACCENT)
        # divider line right (except last)
        if i < len(kpis) - 1:
            add_rect(slide, f"kpi-{n}-divider", tx + tile_w - 1, kpi_y + 6, 1, kpi_h - 12, CARD_BORDER)
        add_text(
            slide, f"kpi-{n}-name", name.upper(),
            x_px=tx + 14, y_px=kpi_y + 16, w_px=tile_w - 28, h_px=14,
            font_size_px=9, color=TEXT_FAINT, bold=True, letter_spacing_px=1.4,
        )
        add_text(
            slide, f"kpi-{n}-value", value,
            x_px=tx + 14, y_px=kpi_y + 34, w_px=tile_w - 28, h_px=26,
            font_size_px=20, color=BRAND_PRIMARY, bold=True,
        )
        delta_color = {"up": RAG_GREEN, "down": RAG_RED, "flat": TEXT_MID}[direction]
        add_text(
            slide, f"kpi-{n}-delta", delta,
            x_px=tx + 14, y_px=kpi_y + kpi_h - 22, w_px=tile_w - 28, h_px=16,
            font_size_px=10, color=delta_color, bold=True,
        )

    # ── Middle zone: agenda (left ~65%) + right column (35%) ──
    mid_y = 268
    mid_x = 48
    mid_w = 1184
    mid_h = 360
    gap = 18
    left_w = int(mid_w * 0.62)
    right_w = mid_w - left_w - gap
    right_x = mid_x + left_w + gap

    # Agenda zone label
    add_text(
        slide, "agenda-zone-label", "BOARD AGENDA",
        x_px=mid_x, y_px=mid_y, w_px=left_w, h_px=16,
        font_size_px=10, color=BRAND_PRIMARY, bold=True, letter_spacing_px=1.8,
    )
    add_rect(slide, "agenda-zone-rule", mid_x, mid_y + 22, left_w, 2, BRAND_PRIMARY)

    agenda = [
        ("1", "Q2 Financial Performance — revenue, margin & cash bridge", "CFO · Sarah Mitchell", "20 min"),
        ("2", "Strategic Initiatives Update — cloud transformation & M&A pipeline", "CEO · James Okafor", "25 min"),
        ("3", "Risk & Compliance Review — regulatory horizon & open actions", "CRO · Dana Voss", "15 min"),
        ("4", "People & Culture Scorecard — attrition, DEI targets & engagement", "CHRO · Priya Nair", "10 min"),
        ("5", "Decisions & Close — three board approvals required this session", "Board Chair · Helen Tran", "10 min"),
    ]
    a_y = mid_y + 32
    row_h = (mid_h - 32) // 5
    for i, (num, topic, presenter, time) in enumerate(agenda):
        n = i + 1
        ry = a_y + i * row_h
        # bottom divider
        if i < len(agenda) - 1:
            add_rect(slide, f"agenda-{n}-divider", mid_x, ry + row_h - 1, left_w, 1, CARD_BORDER)
        # number square
        add_rect(slide, f"agenda-{n}-num-bg", mid_x, ry + (row_h - 26) // 2, 26, 26, BRAND_PRIMARY)
        add_text(
            slide, f"agenda-{n}-num", num,
            x_px=mid_x, y_px=ry + (row_h - 26) // 2, w_px=26, h_px=26,
            font_size_px=12, color=WHITE, bold=True, align="center", anchor="middle",
        )
        # topic
        add_text(
            slide, f"agenda-{n}-topic", topic,
            x_px=mid_x + 40, y_px=ry + 12, w_px=left_w - 100, h_px=20,
            font_size_px=12, color=TEXT_DARK, bold=True,
        )
        # presenter
        add_text(
            slide, f"agenda-{n}-presenter", presenter,
            x_px=mid_x + 40, y_px=ry + 32, w_px=left_w - 100, h_px=16,
            font_size_px=10, color=TEXT_MID,
        )
        # time
        add_text(
            slide, f"agenda-{n}-time", time,
            x_px=mid_x + left_w - 60, y_px=ry + 16, w_px=60, h_px=18,
            font_size_px=11, color=BRAND_ACCENT, bold=True, align="right",
        )
        add_text(
            slide, f"agenda-{n}-time-label", "TIME ALLOC.",
            x_px=mid_x + left_w - 60, y_px=ry + 34, w_px=60, h_px=12,
            font_size_px=8, color=TEXT_FAINT, align="right", letter_spacing_px=0.8,
        )

    # ── Right column: Decisions Required card ──
    dec_x = right_x
    dec_y = mid_y
    dec_w = right_w
    dec_h = 160
    dec_card = add_rect(slide, "decisions-card", dec_x, dec_y, dec_w, dec_h, CARD_BG)
    dec_card.line.color.rgb = CARD_BORDER
    dec_card.line.width = 9525
    add_text(
        slide, "decisions-card-label", "DECISIONS REQUIRED",
        x_px=dec_x + 14, y_px=dec_y + 12, w_px=dec_w - 28, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY, bold=True, letter_spacing_px=1.6,
    )
    add_rect(slide, "decisions-rule", dec_x + 14, dec_y + 30, dec_w - 28, 2, BRAND_PRIMARY)

    decisions = [
        ("Approve H2 capital allocation of $180M", "CFO"),
        ("Ratify proposed acquisition of DataBridge Inc.", "CEO & Legal"),
        ("Endorse revised ESG targets for FY2027", "Board Chair"),
    ]
    d_y = dec_y + 40
    d_row_h = (dec_h - 50) // 3
    for i, (text, owner) in enumerate(decisions):
        n = i + 1
        ry = d_y + i * d_row_h
        # checkbox
        cb = add_rect(slide, f"decision-{n}-checkbox", dec_x + 14, ry + 4, 12, 12, WHITE)
        cb.line.color.rgb = BRAND_PRIMARY_MID
        cb.line.width = 19050
        add_text(
            slide, f"decision-{n}-text", text,
            x_px=dec_x + 32, y_px=ry, w_px=dec_w - 46, h_px=24,
            font_size_px=11, color=TEXT_DARK,
        )
        add_text(
            slide, f"decision-{n}-owner", f"OWNER: {owner.upper()}",
            x_px=dec_x + 32, y_px=ry + 22, w_px=dec_w - 46, h_px=14,
            font_size_px=8, color=BRAND_ACCENT, bold=True, letter_spacing_px=1.2,
        )

    # ── Right column: Key Risks ──
    rk_x = right_x
    rk_y = dec_y + dec_h + 14
    rk_w = right_w
    rk_h = mid_h - dec_h - 14
    add_text(
        slide, "risks-label", "KEY RISKS",
        x_px=rk_x, y_px=rk_y, w_px=rk_w, h_px=14,
        font_size_px=10, color=BRAND_PRIMARY, bold=True, letter_spacing_px=1.6,
    )
    add_rect(slide, "risks-rule", rk_x, rk_y + 16, rk_w, 2, BRAND_PRIMARY)
    risks = [
        ("red", "Regulatory scrutiny on AI model licensing — EU ruling expected Q3"),
        ("amber", "Talent attrition in engineering — voluntary turnover +3pp YoY"),
        ("green", "Cyber programme on track — SOC 2 Type II audit closes 15 Jun"),
    ]
    r_y = rk_y + 24
    rag_map = {"red": RAG_RED, "amber": RAG_AMBER, "green": RAG_GREEN}
    r_row_h = (rk_h - 24) // 3
    for i, (color, text) in enumerate(risks):
        n = i + 1
        ry = r_y + i * r_row_h
        if i < len(risks) - 1:
            add_rect(slide, f"risk-{n}-divider", rk_x, ry + r_row_h - 1, rk_w, 1, CARD_BORDER)
        add_rect(slide, f"risk-{n}-dot", rk_x, ry + 6, 9, 9, rag_map[color])
        add_text(
            slide, f"risk-{n}-text", text,
            x_px=rk_x + 16, y_px=ry, w_px=rk_w - 16, h_px=r_row_h - 4,
            font_size_px=11, color=TEXT_DARK,
        )

    add_footer(slide, page_num=301)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "301_board-reporting-pack.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
