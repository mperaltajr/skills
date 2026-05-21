"""
Builder for pattern 343: Dark Stakeholder Power/Interest map.

Source HTML: _pattern-library/343_dark-stakeholder-map.html
Standalone — light counterpart 21_stakeholder-map exists but uses different
quadrant styling. python-pptx approximation: ovals positioned in 2x2 grid with
4 tinted quadrant backgrounds. Sentiment color via bubble fill.

Layout: 2x2 quadrant (Power vs Interest) on left, stakeholder register list
on right.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from twins.helpers import (
    new_slide, add_text, add_rect,
    BRAND_PRIMARY, BRAND_ACCENT, BRAND_ACCENT_SOFT,
    WHITE,
)
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from twins.helpers import px_to_emu

TEXT_ON_DARK_MID = RGBColor(0xC7, 0xB8, 0xDD)
TEXT_ON_DARK_FAINT = RGBColor(0x9C, 0x88, 0xB8)
CARD_BG_DARK = RGBColor(0x3C, 0x1F, 0x5C)
CARD_BORDER_DARK = RGBColor(0x55, 0x36, 0x77)

SUPP = RGBColor(0x22, 0xC5, 0x5E)
NEUT = RGBColor(0xF5, 0x9E, 0x0B)
RESIS = RGBColor(0xEF, 0x44, 0x44)

QUAD_TL = RGBColor(0x4E, 0x1F, 0x70)   # manage closely (brand-tinted)
QUAD_TR = RGBColor(0x1F, 0x32, 0x5A)   # keep satisfied (blue-tinted)
QUAD_BL = RGBColor(0x33, 0x33, 0x44)   # monitor
QUAD_BR = RGBColor(0x4A, 0x40, 0x1E)   # keep informed (amber-tinted)


def add_oval(slide, name, x, y, size, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                 px_to_emu(x), px_to_emu(y),
                                 px_to_emu(size), px_to_emu(size))
    sh.name = name
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def build():
    prs, slide = new_slide()
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BRAND_PRIMARY

    # Title
    add_text(slide, "title",
             "Stakeholder <strong>Power / Interest Map</strong>",
             x_px=64, y_px=20, w_px=1152, h_px=80,
             font_size_px=32, color=WHITE, bold=True,
             emphasis_color=BRAND_ACCENT_SOFT, anchor="bottom")
    add_text(slide, "subtitle",
             "Engagement strategy by quadrant · Color = sentiment (green supportive · amber neutral · red resistant)",
             x_px=64, y_px=108, w_px=1100, h_px=22,
             font_size_px=14, color=TEXT_ON_DARK_MID, italic=True)
    add_rect(slide, "brand-rule", 64, 132, 64, 3, BRAND_ACCENT_SOFT)

    # Legend
    leg_y = 232
    leg_items = [("Supportive", SUPP), ("Neutral", NEUT), ("Resistant", RESIS)]
    lx = 1240 - (3 * 110)
    for i, (lbl, col) in enumerate(leg_items):
        add_oval(slide, f"leg-{i+1}-dot", lx + i * 110, leg_y + 4, 10, col)
        add_text(slide, f"leg-{i+1}", lbl,
                 x_px=lx + i * 110 + 14, y_px=leg_y, w_px=90, h_px=18,
                 font_size_px=11, color=TEXT_ON_DARK_MID, anchor="middle")

    # --- Matrix (left) ---
    mx, my, mw, mh = 64, 260, 700, 380
    # Axis bounds (inset)
    pad = 36
    plot_x = mx + pad
    plot_y = my + 10
    plot_w = mw - pad - 10
    plot_h = mh - pad - 20
    half_w = plot_w // 2
    half_h = plot_h // 2

    # Quadrant backgrounds
    add_rect(slide, "quad-tl", plot_x, plot_y, half_w, half_h, QUAD_TL)
    add_rect(slide, "quad-tr", plot_x + half_w, plot_y, half_w, half_h, QUAD_TR)
    add_rect(slide, "quad-bl", plot_x, plot_y + half_h, half_w, half_h, QUAD_BL)
    add_rect(slide, "quad-br", plot_x + half_w, plot_y + half_h, half_w, half_h, QUAD_BR)

    # Axes
    add_rect(slide, "axis-y", plot_x, plot_y, 1, plot_h, TEXT_ON_DARK_FAINT)
    add_rect(slide, "axis-x", plot_x, plot_y + plot_h, plot_w, 1, TEXT_ON_DARK_FAINT)
    # Quadrant dividers (light)
    add_rect(slide, "div-v", plot_x + half_w, plot_y, 1, plot_h, RGBColor(0x55, 0x36, 0x77))
    add_rect(slide, "div-h", plot_x, plot_y + half_h, plot_w, 1, RGBColor(0x55, 0x36, 0x77))

    # Quadrant labels
    add_text(slide, "quad-tl-label", "Manage Closely",
             x_px=plot_x, y_px=plot_y + 6, w_px=half_w, h_px=18,
             font_size_px=12, color=BRAND_ACCENT_SOFT, bold=True, align="center")
    add_text(slide, "quad-tr-label", "Keep Satisfied",
             x_px=plot_x + half_w, y_px=plot_y + 6, w_px=half_w, h_px=18,
             font_size_px=12, color=TEXT_ON_DARK_MID, bold=True, align="center")
    add_text(slide, "quad-bl-label", "Monitor",
             x_px=plot_x, y_px=plot_y + half_h + 6, w_px=half_w, h_px=18,
             font_size_px=12, color=TEXT_ON_DARK_FAINT, bold=True, align="center")
    add_text(slide, "quad-br-label", "Keep Informed",
             x_px=plot_x + half_w, y_px=plot_y + half_h + 6, w_px=half_w, h_px=18,
             font_size_px=12, color=TEXT_ON_DARK_MID, bold=True, align="center")

    # Axis titles
    add_text(slide, "axis-x-label", "INTEREST →",
             x_px=plot_x, y_px=plot_y + plot_h + 6, w_px=plot_w, h_px=14,
             font_size_px=10, color=TEXT_ON_DARK_MID, bold=True, align="center",
             letter_spacing_px=1.5)
    add_text(slide, "axis-y-label", "↑ POWER",
             x_px=mx, y_px=plot_y, w_px=pad - 4, h_px=plot_h,
             font_size_px=10, color=TEXT_ON_DARK_MID, bold=True, align="center",
             anchor="middle", letter_spacing_px=1.5)

    # Stakeholder bubbles (initials, sentiment)
    # Quadrant cells (4 sub-quadrants); place stakeholders
    bubbles = [
        ("SK", SUPP, plot_x + half_w * 0.50, plot_y + half_h * 0.30, "Sarah K."),
        ("DL", NEUT, plot_x + half_w * 0.78, plot_y + half_h * 0.55, "David L."),
        ("PM", RESIS, plot_x + half_w * 0.42, plot_y + half_h * 0.75, "Priya M."),
        ("JR", SUPP, plot_x + half_w + half_w * 0.28, plot_y + half_h * 0.20, "James R."),
        ("NT", NEUT, plot_x + half_w + half_w * 0.65, plot_y + half_h * 0.55, "Nina T."),
        ("OF", NEUT, plot_x + half_w * 0.22, plot_y + half_h + half_h * 0.40, "Omar F."),
        ("LW", SUPP, plot_x + half_w * 0.58, plot_y + half_h + half_h * 0.75, "Lisa W."),
        ("TB", RESIS, plot_x + half_w + half_w * 0.30, plot_y + half_h + half_h * 0.55, "Tom B."),
        ("AC", SUPP, plot_x + half_w + half_w * 0.62, plot_y + half_h + half_h * 0.80, "Ana C."),
        ("BH", NEUT, plot_x + half_w + half_w * 0.85, plot_y + half_h + half_h * 0.25, "Ben H."),
    ]
    bub_size = 30
    for i, (init, col, cx, cy, name) in enumerate(bubbles):
        add_oval(slide, f"bubble-{i+1}", int(cx - bub_size / 2),
                 int(cy - bub_size / 2), bub_size, col)
        add_text(slide, f"bubble-{i+1}-init", init,
                 x_px=int(cx - bub_size / 2), y_px=int(cy - bub_size / 2),
                 w_px=bub_size, h_px=bub_size,
                 font_size_px=10, color=WHITE, bold=True,
                 align="center", anchor="middle")

    # --- Stakeholder register (right) ---
    rx, ry, rw = 784, 260, 432
    add_text(slide, "register-label", "STAKEHOLDER REGISTER",
             x_px=rx, y_px=ry, w_px=rw, h_px=14,
             font_size_px=10, color=BRAND_ACCENT_SOFT, bold=True,
             uppercase=True, letter_spacing_px=1.5)
    register = [
        ("Sarah K.", "Chief Financial Officer", SUPP, "Manage Closely"),
        ("David L.", "Chief Technology Officer", NEUT, "Manage Closely"),
        ("Priya M.", "Chief Operating Officer", RESIS, "Manage Closely"),
        ("James R.", "Chief Executive Officer", SUPP, "Keep Satisfied"),
        ("Nina T.", "Board Member", NEUT, "Keep Satisfied"),
        ("Omar F.", "VP Operations", NEUT, "Monitor"),
        ("Lisa W.", "HR Director", SUPP, "Monitor"),
        ("Tom B.", "IT Manager", RESIS, "Keep Informed"),
        ("Ana C.", "Communications Lead", SUPP, "Keep Informed"),
        ("Ben H.", "Finance Analyst", NEUT, "Keep Informed"),
    ]
    row_top = ry + 22
    row_h = 36
    for i, (name, role, sent, chip) in enumerate(register):
        rowy = row_top + i * row_h
        # sentiment dot
        add_oval(slide, f"reg-{i+1}-dot", rx, rowy + 8, 10, sent)
        add_text(slide, f"reg-{i+1}-name", name,
                 x_px=rx + 16, y_px=rowy, w_px=160, h_px=16,
                 font_size_px=11, color=WHITE, bold=True)
        add_text(slide, f"reg-{i+1}-role", role,
                 x_px=rx + 16, y_px=rowy + 16, w_px=200, h_px=14,
                 font_size_px=9, color=TEXT_ON_DARK_FAINT)
        # chip
        pill_w = 110
        pill = add_rect(slide, f"reg-{i+1}-chip-bg",
                        rx + rw - pill_w, rowy + 6, pill_w, 18, CARD_BG_DARK)
        pill.line.color.rgb = CARD_BORDER_DARK
        pill.line.width = 6350
        add_text(slide, f"reg-{i+1}-chip", chip,
                 x_px=rx + rw - pill_w, y_px=rowy + 6, w_px=pill_w, h_px=18,
                 font_size_px=9, color=BRAND_ACCENT_SOFT, bold=True,
                 align="center", anchor="middle", uppercase=True)

    # Invariant zone
    add_text(slide, "footnote-1", "1. [add footnote here or delete]",
             x_px=58, y_px=672, w_px=1164, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT)
    add_text(slide, "source", "Source: [add source here or delete]",
             x_px=58, y_px=688, w_px=1100, h_px=16,
             font_size_px=10, color=TEXT_ON_DARK_FAINT, italic=True)
    add_text(slide, "page-number", "343",
             x_px=1170, y_px=688, w_px=52, h_px=16,
             font_size_px=11, color=TEXT_ON_DARK_FAINT, align="right")
    return prs


if __name__ == "__main__":
    out = (Path(__file__).resolve().parents[2] / "_renders" / "twins" /
           "343_dark-stakeholder-map.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    prs = build()
    prs.save(str(out))
    print(f"Wrote: {out}")
