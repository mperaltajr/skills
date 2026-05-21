"""
Builder for pattern 203: Team Bios Grid (3×2 = 6 cards).

Six persona cards in a 3-col × 2-row grid. Each card: avatar + name + role + bio + 2 tags.

Source HTML: _pattern-library/203_team-bios-grid.html
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


def build():
    prs, slide = new_slide()
    add_chrome(slide)
    add_title_block(
        slide,
        title="Meet the <strong>Core Team</strong>",
        subtitle="Six leaders driving the programme — backgrounds, roles, and areas of expertise",
        title_h=42, subtitle_h=20, brand_rule_w=64,
    )

    body_top = 168
    body_bot = 600
    body_h = body_bot - body_top
    grid_w = 1280 - 128
    gap = 12
    card_w = (grid_w - 2 * gap) // 3
    card_h = (body_h - gap) // 2

    cards = [
        ("SR", "Sarah Reynolds", "Programme Director",
         "20+ years leading large-scale digital transformations across FS and public sector. Accountable for overall delivery and stakeholder alignment.",
         ["Programme Governance", "Change Management"]),
        ("JM", "James Morales", "Technology Lead",
         "Cloud-native architect specialising in Azure and Kubernetes. Defines the technical blueprint and oversees engineering squads across two workstreams.",
         ["Cloud Architecture", "DevSecOps"]),
        ("LP", "Lena Park", "Data & AI Strategist",
         "Leads the analytics and ML platform build. Prior experience at a global consultancy driving gen-AI adoption in regulated industries.",
         ["Generative AI", "Data Governance"]),
        ("TN", "Tariq Nassar", "Change & Comms Lead",
         "Behavioural change expert with a track record in enterprise ERP rollouts. Manages communications, training design, and adoption metrics.",
         ["OCM", "Training Design"]),
        ("CW", "Claire Wong", "Commercial & Risk Manager",
         "Manages contract performance, financial controls, and risk registers. Brings 12 years in commercial management on multi-vendor engagements.",
         ["Risk & Controls", "Commercial"]),
        ("BO", "Ben O'Sullivan", "Solution Architect",
         "Owns integration design between legacy platforms and the new cloud core. Experienced in API-led connectivity and enterprise middleware patterns.",
         ["Integration", "API Design"]),
    ]

    for i, (initials, name, role, bio, tags) in enumerate(cards):
        n = i + 1
        col = i % 3
        row = i // 3
        cx = 64 + col * (card_w + gap)
        cy = body_top + row * (card_h + gap)
        # Card bg
        card = add_rect(slide, f"persona-{n}-bg", cx, cy, card_w, card_h, CARD_BG)
        card.line.color.rgb = CARD_BORDER
        card.line.width = 9525
        # Avatar
        av_size = 56
        add_rect(slide, f"persona-{n}-photo", cx + 14, cy + 14, av_size, av_size, BRAND_PRIMARY_MID)
        add_text(slide, f"persona-{n}-photo-initials", initials,
                 x_px=cx + 14, y_px=cy + 14, w_px=av_size, h_px=av_size,
                 font_size_px=16, color=WHITE, bold=True, align="center", anchor="middle")
        # Identity
        add_text(slide, f"persona-{n}-name", name,
                 x_px=cx + 80, y_px=cy + 18, w_px=card_w - 94, h_px=18,
                 font_size_px=13, color=BRAND_PRIMARY, bold=True)
        add_text(slide, f"persona-{n}-role", role,
                 x_px=cx + 80, y_px=cy + 38, w_px=card_w - 94, h_px=16,
                 font_size_px=11, color=TEXT_MID)
        # Bio
        bio_y = cy + 80
        add_text(slide, f"persona-{n}-bio", bio,
                 x_px=cx + 14, y_px=bio_y, w_px=card_w - 28, h_px=68,
                 font_size_px=10, color=TEXT_DARK)
        # Tags
        tag_y = cy + card_h - 26
        for j, tag in enumerate(tags):
            # Approximate width based on text
            tw = max(90, 7 * len(tag) + 14)
            tx = cx + 14 + j * (tw + 6)
            if tx + tw > cx + card_w - 14:
                continue
            add_text(slide, f"persona-{n}-tag-{j+1}", tag,
                     x_px=tx, y_px=tag_y, w_px=tw, h_px=16,
                     font_size_px=9, color=BRAND_PRIMARY, bold=True, align="center",
                     bg_fill=BRAND_ACCENT_SOFT, padding_px=(2, 6, 2, 6))

    add_footer(slide, page_num=203)
    return prs


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "_renders" / "twins" / "203_team-bios-grid.pptx"
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
