"""Agent 3 -- Slide 9 (simpler-arch test).

Layout: Compare / 50/50 / light canvas.
Brief: EXACTLY two paths (Skeleton, Playwright fallback) with parallel sub-structure
(when used / how it works / when it falls short).

Hardline rule 2 honored: 2 paths in the brief => 2 columns in the slide. No fabrication.
Adjacent to slide 8 (Process) and slide 10 (Hero) -- rule 3 satisfied.
"""
from pathlib import Path
import sys
sys.path.insert(0, r"C:\Users\m.a.peralta\.claude\skills\slide-builder")
from twins.helpers import (
    new_slide, add_text, add_rect, add_title_block, add_footer,
    BRAND_PRIMARY, BRAND_PRIMARY_MID, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    TEXT_DARK, TEXT_MID, TEXT_FAINT, CARD_BG, CARD_BORDER, WHITE,
)


def build():
    prs, slide = new_slide()

    add_title_block(
        slide,
        title="Two paths from brief to slides",
        subtitle="Skeleton path when a layout matches; Playwright fallback when it doesn't.",
    )

    # 50/50 compare zones. Body region 64..1216 = 1152px, divider in middle.
    body_x = 64
    body_w = 1280 - 128
    gutter = 32
    col_w = (body_w - gutter) // 2  # 560
    col_y = 170
    col_h = 440

    cols = [
        {
            "name": "Skeleton path",
            "tag": "Primary",
            "accent": True,
            "rows": [
                ("When used",
                 "Slide intent matches one of 7 layout families: cover, single-finding, two-panel, three-column, recommendation, process-chevron, chart-with-takeaway."),
                ("How it works",
                 "Brief tokens dropped into a pre-built skeleton; structural patches (icons, RAG, stat blocks) applied; renders straight to PPTX."),
                ("When it falls short",
                 "Custom diagrams or unusual frameworks (e.g. 2x2) outside the 7 families -- the skeleton can't bend that far."),
            ],
        },
        {
            "name": "Playwright fallback",
            "tag": "Fallback",
            "accent": False,
            "rows": [
                ("When used",
                 "No skeleton matches -- typically 2x2 frameworks, custom diagrams, or one-off compositions."),
                ("How it works",
                 "Renders HTML in headless Chromium and walks the DOM to extract shapes into PPTX primitives."),
                ("When it falls short",
                 "More flexible but less reliable for structured layouts; harder to edit downstream and slower to render."),
            ],
        },
    ]

    for i, col in enumerate(cols):
        x = body_x + i * (col_w + gutter)
        cid = f"col-{i+1}"

        # Card background
        add_rect(
            slide, f"{cid}-bg",
            x_px=x, y_px=col_y, w_px=col_w, h_px=col_h,
            fill_color=CARD_BG if col["accent"] else WHITE,
        )
        # Light border on the non-accent column for visual parity
        if not col["accent"]:
            for side_name, sx, sy, sw, sh in [
                ("top", x, col_y, col_w, 1),
                ("bottom", x, col_y + col_h - 1, col_w, 1),
                ("left", x, col_y, 1, col_h),
                ("right", x + col_w - 1, col_y, 1, col_h),
            ]:
                add_rect(slide, f"{cid}-border-{side_name}",
                         x_px=sx, y_px=sy, w_px=sw, h_px=sh,
                         fill_color=CARD_BORDER)
        # Single accent moment: top strip on the primary path
        if col["accent"]:
            add_rect(
                slide, f"{cid}-accent",
                x_px=x, y_px=col_y, w_px=col_w, h_px=4,
                fill_color=BRAND_ACCENT,
            )

        pad = 22
        inner_x = x + pad
        inner_w = col_w - 2 * pad

        # Tag (small uppercase pill text)
        add_text(
            slide, f"{cid}-tag", col["tag"],
            x_px=inner_x, y_px=col_y + 18, w_px=inner_w, h_px=18,
            font_size_px=11, color=BRAND_PRIMARY_MID, bold=True,
            uppercase=True, letter_spacing_px=1,
        )
        # Column name
        add_text(
            slide, f"{cid}-name", col["name"],
            x_px=inner_x, y_px=col_y + 42, w_px=inner_w, h_px=36,
            font_size_pt=22, color=TEXT_DARK, bold=True,
        )

        # Three rows (when used / how it works / when it falls short)
        row_top = col_y + 100
        row_gap = 12
        row_h_each = 108
        for j, (label, body) in enumerate(col["rows"]):
            ry = row_top + j * (row_h_each + row_gap)
            # Hairline above each row
            add_rect(
                slide, f"{cid}-rule-{j+1}",
                x_px=inner_x, y_px=ry - 8, w_px=inner_w, h_px=1,
                fill_color=CARD_BORDER,
            )
            add_text(
                slide, f"{cid}-label-{j+1}", label,
                x_px=inner_x, y_px=ry, w_px=inner_w, h_px=20,
                font_size_px=12, color=BRAND_PRIMARY, bold=True,
                uppercase=True, letter_spacing_px=1,
            )
            add_text(
                slide, f"{cid}-body-{j+1}", body,
                x_px=inner_x, y_px=ry + 24, w_px=inner_w, h_px=row_h_each - 26,
                font_size_px=13, color=TEXT_MID, anchor="top",
            )

    add_footer(slide, page_num=9)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "agent3-slide9.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
