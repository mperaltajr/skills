"""
Builder for pattern 309: OKR tracking dashboard (3 objectives × 3 KRs each).

Confidence legend (green/amber/red) goes BELOW the subheadline, right-aligned.
Body content is pushed down to y=280 to clear the legend.

Source HTML: _pattern-library/309_okr-tracking-dashboard.html
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
from pptx.enum.shapes import MSO_SHAPE
from twins.helpers import px_to_emu
from pptx.dml.color import RGBColor

CONF_GREEN = RGBColor(0x22, 0xC5, 0x5E)
CONF_AMBER = RGBColor(0xF5, 0x9E, 0x0B)
CONF_RED = RGBColor(0xEF, 0x44, 0x44)


def _owner_circle(slide, name, x, y, size, initials):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, px_to_emu(x), px_to_emu(y),
        px_to_emu(size), px_to_emu(size),
    )
    shape.name = f"{name}-circle"
    shape.fill.solid()
    shape.fill.fore_color.rgb = BRAND_PRIMARY_MID
    shape.line.fill.background()
    add_text(
        slide, f"{name}-text", initials,
        x_px=x, y_px=y, w_px=size, h_px=size,
        font_size_px=8, color=WHITE, bold=True,
        align="center", anchor="middle",
    )


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    add_title_block(
        slide,
        title="Q2 OKR Progress — <strong>Tracking Dashboard</strong>",
        subtitle="Status as of May 19, 2026 · Three strategic objectives · Nine key results",
        title_x=48, title_y=44, title_w=900, title_h=44,
        subtitle_h=20, brand_rule_w=64,
    )

    # ── CONFIDENCE LEGEND (below subheadline, right-aligned) ──
    leg_h = 32
    leg_y = 232
    leg_right = 1232
    items = [("On Track", CONF_GREEN), ("At Risk", CONF_AMBER), ("Off Track", CONF_RED)]
    title_w = 100
    item_w = 96
    leg_w = title_w + len(items) * item_w + 16
    leg_x = leg_right - leg_w
    leg_bg = add_rect(slide, "legend-bg", leg_x, leg_y, leg_w, leg_h, CARD_BG)
    leg_bg.line.color.rgb = CARD_BORDER
    leg_bg.line.width = 9525
    add_text(
        slide, "legend-title", "CONFIDENCE",
        x_px=leg_x + 12, y_px=leg_y, w_px=title_w, h_px=leg_h,
        font_size_px=9, color=TEXT_MID, bold=True, letter_spacing_px=1.4,
        anchor="middle",
    )
    cur_x = leg_x + title_w + 12
    for i, (lbl, col) in enumerate(items):
        n = i + 1
        add_rect(slide, f"legend-{n}-dot", cur_x, leg_y + (leg_h - 9) // 2, 9, 9, col)
        add_text(
            slide, f"legend-{n}-label", lbl,
            x_px=cur_x + 16, y_px=leg_y, w_px=item_w - 20, h_px=leg_h,
            font_size_px=10, color=TEXT_DARK, bold=True, anchor="middle",
        )
        cur_x += item_w

    # ── OBJECTIVE CARDS (3 stacked) ──
    body_top = 280
    body_left = 48
    body_w = 1184
    # Body must end ≤ y=670 to stay clear of invariant zone (≥672).
    body_h = 670 - body_top
    obj_gap = 10
    obj_h = (body_h - 2 * obj_gap) // 3

    objectives = [
        ("O1 · Accelerate Enterprise AI Adoption Across Client Accounts", "72%",
         [("KR1 · Deploy AI pilots in 12 client accounts by Jun 30", 83, "JR", "green"),
          ("KR2 · Achieve 90% client satisfaction on AI engagements", 67, "SL", "amber"),
          ("KR3 · Certify 40 practitioners in generative AI toolchain", 65, "MP", "green")]),
        ("O2 · Scale Delivery Efficiency Through Platform Standardisation", "54%",
         [("KR1 · Migrate 80% of active projects to unified DevOps platform", 60, "AT", "amber"),
          ("KR2 · Reduce average release cycle time from 3 weeks to 1 week", 42, "DN", "red"),
          ("KR3 · Publish 5 reusable accelerator assets to internal marketplace", 60, "CH", "amber")]),
        ("O3 · Build a High-Performing, Inclusive Talent Pipeline", "38%",
         [("KR1 · Hire 20 senior engineers with cloud-native specialisation", 50, "RP", "amber"),
          ("KR2 · Achieve 40% underrepresented groups in new hires cohort", 30, "FO", "red"),
          ("KR3 · Complete structured mentoring programme for 60 analysts", 33, "LK", "amber")]),
    ]
    conf_map = {"green": CONF_GREEN, "amber": CONF_AMBER, "red": CONF_RED}

    for oi, (obj_title, obj_pct, krs) in enumerate(objectives):
        on = oi + 1
        oy = body_top + oi * (obj_h + obj_gap)
        card = add_rect(slide, f"obj-{on}-card", body_left, oy, body_w, obj_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Header bar
        hdr_h = 30
        add_text(
            slide, f"obj-{on}-title", obj_title,
            x_px=body_left + 16, y_px=oy + 6, w_px=body_w - 110, h_px=hdr_h,
            font_size_px=13, color=BRAND_PRIMARY, bold=True, anchor="middle",
        )
        add_text(
            slide, f"obj-{on}-pct", obj_pct,
            x_px=body_left + body_w - 80, y_px=oy + 6, w_px=64, h_px=hdr_h,
            font_size_px=18, color=BRAND_ACCENT, bold=True,
            align="right", anchor="middle",
        )
        # Divider
        add_rect(slide, f"obj-{on}-divider",
                 body_left + 16, oy + hdr_h + 4, body_w - 32, 1, CARD_BORDER)
        # KR rows
        kr_top = oy + hdr_h + 12
        kr_zone_h = obj_h - hdr_h - 18
        kr_row_h = kr_zone_h // 3
        for ki, (desc, pct, owner, conf) in enumerate(krs):
            kn = ki + 1
            ky = kr_top + ki * kr_row_h
            # Desc
            add_text(
                slide, f"obj-{on}-kr-{kn}-desc", desc,
                x_px=body_left + 16, y_px=ky, w_px=560, h_px=kr_row_h,
                font_size_px=11, color=TEXT_DARK, anchor="middle",
            )
            # Bar background
            bar_x = body_left + 590
            bar_w = 360
            bar_y = ky + (kr_row_h - 8) // 2
            add_rect(slide, f"obj-{on}-kr-{kn}-bar-bg",
                     bar_x, bar_y, bar_w, 8, CARD_BORDER)
            # Fill
            fill_w = int(bar_w * pct / 100)
            add_rect(slide, f"obj-{on}-kr-{kn}-bar-fill",
                     bar_x, bar_y, fill_w, 8, BRAND_ACCENT)
            # Pct
            add_text(
                slide, f"obj-{on}-kr-{kn}-pct", f"{pct}%",
                x_px=bar_x + bar_w + 8, y_px=ky, w_px=40, h_px=kr_row_h,
                font_size_px=11, color=TEXT_DARK, bold=True, anchor="middle",
            )
            # Owner circle
            ow_size = 22
            ow_x = bar_x + bar_w + 56
            ow_y = ky + (kr_row_h - ow_size) // 2
            _owner_circle(slide, f"obj-{on}-kr-{kn}-owner", ow_x, ow_y, ow_size, owner)
            # Confidence dot
            cdot_size = 10
            cdot_x = ow_x + ow_size + 14
            cdot_y = ky + (kr_row_h - cdot_size) // 2
            add_rect(slide, f"obj-{on}-kr-{kn}-conf",
                     cdot_x, cdot_y, cdot_size, cdot_size, conf_map[conf])

    add_footer(slide, page_num=309)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "309_okr-tracking-dashboard.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
