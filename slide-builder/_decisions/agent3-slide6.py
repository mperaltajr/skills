"""Agent 3 -- Slide 6 (simpler-arch test).

Layout: Compare / stacked-rows / light canvas.
Brief: Two stacked horizontal rows -- Storyline Helper on top, Slide Builder below.
Adjacent to slide 5 (Hero) -- rule 3 satisfied.
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
        title="Two layers, one workflow",
        subtitle="Storyline Helper coaches the narrative; Slide Builder produces the slides.",
    )

    body_x = 64
    body_w = 1280 - 128  # 1152
    row_h = 200
    gap = 24
    top_y = 170
    bottom_y = top_y + row_h + gap  # 394

    rows = [
        {
            "tag": "Layer 01",
            "name": "Storyline Helper",
            "tagline": "Narrative coaching",
            "bullets": [
                "Turns raw objectives into a structured narrative brief",
                "Governing-thought gate -- no brief until every slide has an assertive one-sentence claim",
                "Captures deck-level design notes alongside",
            ],
            "accent": True,
            "y": top_y,
        },
        {
            "tag": "Layer 02",
            "name": "Slide Builder",
            "tagline": "Brief to PPTX",
            "bullets": [
                "Matches each slide to a pre-built skeleton",
                "Fills tokens, applies structural patches (bullets, icons, stat blocks, RAG)",
                "Renders PPTX and PNG via LibreOffice",
            ],
            "accent": False,
            "y": bottom_y,
        },
    ]

    for i, row in enumerate(rows):
        y = row["y"]
        rid = f"row-{i+1}"

        # Tinted card background (compare panel)
        add_rect(
            slide, f"{rid}-bg",
            x_px=body_x, y_px=y, w_px=body_w, h_px=row_h,
            fill_color=CARD_BG,
        )

        # Single accent: vertical strip on the upstream layer (Storyline)
        if row["accent"]:
            add_rect(
                slide, f"{rid}-accent",
                x_px=body_x, y_px=y, w_px=6, h_px=row_h,
                fill_color=BRAND_ACCENT,
            )

        # Left column (tag + name + tagline) ~ 320px
        pad_x = 24
        col_left_x = body_x + pad_x
        col_left_w = 300
        # Tag (small uppercase)
        add_text(
            slide, f"{rid}-tag", row["tag"],
            x_px=col_left_x, y_px=y + 22, w_px=col_left_w, h_px=20,
            font_size_px=11, color=BRAND_PRIMARY_MID, bold=True,
            uppercase=True, letter_spacing_px=1,
        )
        # Name (big)
        add_text(
            slide, f"{rid}-name", row["name"],
            x_px=col_left_x, y_px=y + 48, w_px=col_left_w, h_px=44,
            font_size_pt=24, color=TEXT_DARK, bold=True,
        )
        # Tagline (italic)
        add_text(
            slide, f"{rid}-tagline", row["tagline"],
            x_px=col_left_x, y_px=y + 102, w_px=col_left_w, h_px=24,
            font_size_px=14, color=TEXT_MID, italic=True,
        )

        # Right column: 3 bullets
        col_right_x = col_left_x + col_left_w + 32
        col_right_w = body_w - (col_right_x - body_x) - pad_x
        bullet_y = y + 28
        for j, bullet in enumerate(row["bullets"]):
            # Dot
            add_text(
                slide, f"{rid}-dot-{j+1}", "•",
                x_px=col_right_x, y_px=bullet_y, w_px=14, h_px=22,
                font_size_px=18, color=BRAND_PRIMARY_MID, bold=True,
            )
            # Text
            add_text(
                slide, f"{rid}-bullet-{j+1}", bullet,
                x_px=col_right_x + 20, y_px=bullet_y, w_px=col_right_w - 24, h_px=46,
                font_size_px=14, color=TEXT_DARK, anchor="top",
            )
            bullet_y += 52

    add_footer(slide, page_num=6)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "agent3-slide6.pptx"
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
