"""
Builder for pattern 72: OKR cascade (objective → 3 KRs → 9 initiatives).

SVG-driven cascade connectors (picture-asset per SHAPE-ROLES): chart-canvas
placeholder for connector lines. Objective, KR cards, and initiative cards
are rendered natively since text is addressable.

Source HTML: _pattern-library/72_okr-cascade.html
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    add_chrome, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    CARD_BG, CARD_BORDER, TEXT_DARK, TEXT_MID, WHITE,
)
from pptx.dml.color import RGBColor

CHART_PLACEHOLDER = RGBColor(0xFB, 0xF8, 0xFE)


def build():
    prs, slide = new_slide()
    add_chrome(slide)

    # Optional pattern-tag (kept as plain text for ID)
    add_text(
        slide, "title",
        "Q3 OKRs — one objective, three key results, nine initiatives.",
        x_px=64, y_px=50, w_px=1100, h_px=40,
        font_size_px=27, color=TEXT_DARK, bold=True,
    )
    add_text(
        slide, "subtitle",
        "Each level commits the level below: the objective sets ambition, KRs make it measurable, "
        "initiatives make it doable this quarter.",
        x_px=64, y_px=98, w_px=1100, h_px=22,
        font_size_px=14, color=TEXT_MID, italic=True,
    )
    add_rect(slide, "brand-rule", 64, 142, 56, 3, BRAND_ACCENT)

    # Cascade body
    c_top = 174
    c_left = 64
    c_right = 1280 - 64
    c_bottom = 720 - 60 - 32  # convergence and footer below
    c_w = c_right - c_left
    c_h = c_bottom - c_top

    # Chart-canvas placeholder for connectors
    add_rect(slide, "chart-canvas", c_left, c_top, c_w, c_h, CHART_PLACEHOLDER)

    # Objective (top centered, 720x78)
    obj_w = 720
    obj_h = 78
    obj_x = c_left + (c_w - obj_w) // 2
    obj_y = c_top
    add_rect(slide, "objective", obj_x, obj_y, obj_w, obj_h, BRAND_PRIMARY)
    add_text(
        slide, "objective-tag", "OBJECTIVE",
        x_px=obj_x + 24, y_px=obj_y + 12, w_px=obj_w - 48, h_px=14,
        font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
    )
    add_text(
        slide, "objective-label",
        "Make Slide Lab the default deck-building method across three practices.",
        x_px=obj_x + 24, y_px=obj_y + 30, w_px=obj_w - 48, h_px=42,
        font_size_px=16, color=WHITE, bold=True,
    )

    # 3 KR columns
    kr_top = c_top + 134
    kr_h = 72
    kr_gap = 24
    kr_w = (c_w - 2 * kr_gap) // 3

    kr_data = [
        ("Key Result 1", "Roll out to 3 practice areas by Q3 end",
         [("1.1", "Coach 6 senior managers through full deck cycle"),
          ("1.2", "Brand-theme each practice (colors, type, marks)"),
          ("1.3", "Weekly pilot review with practice leads")]),
        ("Key Result 2", "80%+ partner-ready sign-off rate",
         [("2.1", "Ship QC framework v2 with deterministic checks"),
          ("2.2", "Grow pattern library to 100+ vetted patterns"),
          ("2.3", "Close the coach feedback loop after every deck")]),
        ("Key Result 3", "−50% deck cycle time vs Q2 baseline",
         [("3.1", "Optimize the storyline session to under 30 min"),
          ("3.2", "Build the HTML-to-PPTX translator end-to-end"),
          ("3.3", "Enable one-click template hot-swap per practice")]),
    ]

    for ci, (kr_tag, kr_label, inits) in enumerate(kr_data):
        n = ci + 1
        cx = c_left + ci * (kr_w + kr_gap)

        # KR card
        add_rect(slide, f"kr-{n}", cx, kr_top, kr_w, kr_h, BRAND_PRIMARY_MID)
        add_text(
            slide, f"kr-{n}-tag", kr_tag.upper(),
            x_px=cx + 16, y_px=kr_top + 10, w_px=kr_w - 32, h_px=14,
            font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True, uppercase=True,
        )
        add_text(
            slide, f"kr-{n}-label", kr_label,
            x_px=cx + 16, y_px=kr_top + 28, w_px=kr_w - 32, h_px=38,
            font_size_px=13, color=WHITE, bold=True,
        )

        # Initiatives stack (margin-top 38px)
        init_top = kr_top + kr_h + 38
        init_h = 38
        init_gap = 8

        for ii, (num, text) in enumerate(inits):
            in_ = ii + 1
            iy = init_top + ii * (init_h + init_gap)
            card = add_rect(slide, f"kr-{n}-init-{in_}", cx, iy, kr_w, init_h, CARD_BG)
            card.line.color.rgb = CARD_BORDER
            card.line.width = 9525
            add_text(
                slide, f"kr-{n}-init-{in_}-num", num,
                x_px=cx + 10, y_px=iy + 11, w_px=24, h_px=16,
                font_size_px=9, color=BRAND_PRIMARY_MID, bold=True,
            )
            add_text(
                slide, f"kr-{n}-init-{in_}-text", text,
                x_px=cx + 38, y_px=iy + 8, w_px=kr_w - 48, h_px=init_h - 16,
                font_size_px=11, color=TEXT_DARK,
            )

    # Convergence
    cv_y = 720 - 32 - 50
    cv_h = 44
    add_rect(slide, "convergence-bg", c_left, cv_y, c_w, cv_h, BRAND_PRIMARY)
    add_text(
        slide, "convergence",
        "Nine initiatives, three measurable outcomes, one ambition — if an initiative does not "
        "ladder up, it does not ship this quarter.",
        x_px=c_left + 22, y_px=cv_y, w_px=c_w - 44, h_px=cv_h,
        font_size_px=13, color=WHITE, italic=True, anchor="middle",
    )

    add_footer(slide, page_num=72)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "72_okr-cascade.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
