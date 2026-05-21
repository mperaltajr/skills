#!/usr/bin/env python3
"""
generate_chart.py — Generate a styled chart PNG from data for Slide Lab.

Produces a matplotlib chart styled with brand colors from theme.json.
The PNG is embedded in the slide as a DRAFT image. The consultant should
replace it with a think-cell chart before client delivery.

Usage:
  py -3 generate_chart.py --type bar --data "Category,Value\\nQ1,1200\\nQ2,1450" \\
      --theme _session/theme.json --output _session/chart-slide-1.png

  Or from a file:
  py -3 generate_chart.py --type bar --data-file _reference/data.csv \\
      --theme _session/theme.json --output _session/chart-slide-1.png \\
      --title "Revenue by Quarter" --ylabel "Revenue ($K)"

Supported chart types:
  bar            Vertical column chart (single series)
  bar-h          Horizontal bar chart (single series)
  line           Line chart (one or more series; multi-series via extra CSV columns)
  pie            Pie chart
  donut          Donut chart
  waterfall      Waterfall / bridge chart (first row = start total, last row = end total)
  clustered-bar  Grouped bar chart (multi-series via extra CSV columns)
  stacked-bar    Stacked bar chart (multi-series via extra CSV columns)
  stacked-bar-100  100% stacked bar chart

Legend placement rule (DO NOT CHANGE):
  All multi-series legends must be placed at the TOP RIGHT inside the chart area:
    ax.legend(..., loc="upper right")
  NEVER place legends below the chart or outside the axes.

Data format:
  CSV with header row. First column = categories/labels. Additional columns = series.
  Numeric values may contain commas, currency symbols ($), and parentheses for negatives.

  Example (bar):
    Quarter,Revenue
    Q1,1200
    Q2,1450
    Q3,1100
    Q4,1600

  Example (waterfall — first row = start, last row = end, middle rows = changes):
    Label,Value
    Starting savings,1000
    +Network efficiency,500
    -One-time correction,-200
    +Headcount actions,300
    FY26 total,1600

  Example (multi-series line — one series per column after column 1):
    Quarter,Actual,Target
    Q1,1200,1100
    Q2,1450,1300
    Q3,1100,1400
    Q4,1600,1500
"""

import argparse
import csv
import io
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend — no display required
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import numpy as np


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _parse_numeric(val: str) -> float:
    """Parse a numeric string. Handles commas, $, %, and (negative) notation."""
    cleaned = (
        val.strip()
        .replace(",", "")
        .replace("$", "")
        .replace("%", "")
        .replace("(", "-")
        .replace(")", "")
    )
    return float(cleaned)


def _load_csv_text(csv_text: str) -> tuple[list[str], list[list[str]]]:
    """Parse inline CSV text (use \\n literal for newlines from command line)."""
    normalized = csv_text.replace("\\n", "\n").replace("\\t", "\t")
    reader = csv.reader(io.StringIO(normalized))
    rows = [r for r in reader if any(c.strip() for c in r)]
    if not rows:
        return [], []
    return rows[0], rows[1:]


def _load_csv_file(path: str) -> tuple[list[str], list[list[str]]]:
    """Load data from a CSV or Excel file."""
    p = Path(path)
    if p.suffix.lower() in (".xlsx", ".xls", ".xlsm"):
        try:
            import openpyxl
        except ImportError:
            sys.exit("ERROR: openpyxl is required for Excel files. Run: pip install openpyxl")
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        all_rows = []
        for row in ws.iter_rows(values_only=True):
            if any(v is not None for v in row):
                all_rows.append([str(v) if v is not None else "" for v in row])
        wb.close()
        if not all_rows:
            return [], []
        return all_rows[0], all_rows[1:]
    else:
        with open(path, "r", encoding="utf-8-sig") as f:
            return _load_csv_text(f.read())


# ---------------------------------------------------------------------------
# Theme colors
# ---------------------------------------------------------------------------

def _load_theme_colors(theme_path: str | None) -> list[str]:
    """
    Load accent colors from theme.json produced by --print-theme.
    Returns hex strings in order: accent1 through accent6.
    Falls back to a clean default palette if the file is missing or unreadable.
    """
    defaults = ["#4472C4", "#ED7D31", "#A9D18E", "#FF0000", "#FFC000", "#70AD47"]
    if not theme_path or not Path(theme_path).exists():
        return defaults
    try:
        with open(theme_path, "r", encoding="utf-8") as f:
            theme = json.load(f)
        c = theme.get("colors", {})
        slots = ["accent1", "accent2", "accent3", "accent4", "accent5", "accent6"]
        colors = []
        for i, slot in enumerate(slots):
            val = c.get(slot, "").lstrip("#")
            colors.append(f"#{val}" if len(val) == 6 else defaults[i])
        return colors
    except Exception:
        return defaults


def _hex_to_rgb01(hex_color: str) -> tuple[float, float, float]:
    """Convert '#RRGGBB' to (r, g, b) with values in [0, 1]."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))


# ---------------------------------------------------------------------------
# Shared styling helpers
# ---------------------------------------------------------------------------

def _apply_axis_style(ax: plt.Axes, dark: bool = False) -> None:
    """Clean, minimal axis style — no top/right spines, light grid.

    dark=True: white/light spines and tick labels for dark-background slides.
    """
    spine_color  = "#555555" if dark else "#DDDDDD"
    tick_color   = "#DDDDDD" if dark else "#555555"
    grid_color   = "#666666" if dark else "#EEEEEE"
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(spine_color)
    ax.spines["bottom"].set_color(spine_color)
    ax.tick_params(colors=tick_color, labelsize=9)
    ax.yaxis.grid(True, color=grid_color, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def _add_draft_label(fig: plt.Figure, dark: bool = False) -> None:
    """Add a small 'DRAFT — Replace with think-cell' notice at the bottom right."""
    fig.text(
        0.99, 0.005,
        "DRAFT — Replace with think-cell before delivery",
        ha="right", va="bottom",
        fontsize=7, color="#888888" if dark else "#BBBBBB",
        fontstyle="italic",
    )


def _value_label(val: float) -> str:
    """Format a number for display on a chart: no decimals if whole, else 1 dp."""
    return f"{val:,.0f}" if val == int(val) else f"{val:,.1f}"


def _fix_label_legend_overlap(ax: plt.Axes, fig: plt.Figure) -> None:
    """
    After tight_layout, shift value labels (ax.transData texts) that overlap:
      (a) the legend bounding box, or
      (b) chart title / units texts above the axes (ax.transAxes)
    Then do a second pass to stagger any remaining label-to-label overlaps.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    # Collect obstacle bboxes: legend + transAxes title/units
    obstacles = []
    leg = ax.get_legend()
    if leg is not None:
        obstacles.append(leg.get_window_extent(renderer))
    for txt in ax.texts:
        if txt.get_transform() is ax.transAxes:
            bb = txt.get_window_extent(renderer)
            if bb.width > 0 and bb.height > 0:
                obstacles.append(bb)

    if not obstacles:
        return

    def _drop(txt, drop_px):
        x_d, y_d = txt.get_position()
        disp_x, disp_y = ax.transData.transform((x_d, y_d))
        _, y_d_new = ax.transData.inverted().transform((disp_x, disp_y - drop_px))
        txt.set_position((x_d, y_d_new))

    # Pass 1: clear obstacles
    for txt in ax.texts:
        if txt.get_transform() is not ax.transData:
            continue
        txt_bb = txt.get_window_extent(renderer)
        for obs in obstacles:
            if obs.overlaps(txt_bb):
                drop_px = txt_bb.y1 - obs.y0 + 3
                if drop_px > 0:
                    _drop(txt, drop_px)
                    fig.canvas.draw()
                    txt_bb = txt.get_window_extent(renderer)
                break

    # Pass 2: stagger label-to-label overlaps
    data_texts = [t for t in ax.texts if t.get_transform() is ax.transData]
    fig.canvas.draw()
    for i in range(len(data_texts)):
        for j in range(i + 1, len(data_texts)):
            bb_i = data_texts[i].get_window_extent(renderer)
            bb_j = data_texts[j].get_window_extent(renderer)
            if not bb_i.overlaps(bb_j):
                continue
            overlap_px = min(bb_i.y1, bb_j.y1) - max(bb_i.y0, bb_j.y0) + 2
            if overlap_px <= 0:
                continue
            # Push the lower-anchored label further down
            yi = data_texts[i].get_position()[1]
            yj = data_texts[j].get_position()[1]
            if yi <= yj:
                _drop(data_texts[i], overlap_px)
            else:
                _drop(data_texts[j], overlap_px)
            fig.canvas.draw()


# ---------------------------------------------------------------------------
# Chart renderers
# ---------------------------------------------------------------------------

def _render_bar(ax, headers, rows, colors, horizontal=False, label_color="#444444"):
    categories = [r[0] for r in rows]
    values = [_parse_numeric(r[1]) for r in rows]
    color = _hex_to_rgb01(colors[0])
    max_val = max(abs(v) for v in values) if values else 1

    if horizontal:
        bars = ax.barh(categories, values, color=color, zorder=3)
        ax.xaxis.grid(True, color="#EEEEEE", linewidth=0.8, zorder=0)
        ax.yaxis.grid(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color("#DDDDDD")
        for bar, val in zip(bars, values):
            offset = max_val * 0.01
            ax.text(
                bar.get_width() + offset, bar.get_y() + bar.get_height() / 2,
                _value_label(val), va="center", ha="left", fontsize=8, color=label_color,
            )
    else:
        bars = ax.bar(categories, values, color=color, zorder=3, width=0.6)
        ax.set_ylabel(headers[1] if len(headers) > 1 else "", fontsize=9, color="#555555")
        for bar, val in zip(bars, values):
            offset = max_val * 0.015
            ax.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height() + offset,
                _value_label(val), ha="center", va="bottom", fontsize=8, color=label_color,
            )


def _render_line(ax, headers, rows, colors, label_color="#555555"):
    x_labels = [r[0] for r in rows]
    x = range(len(x_labels))
    n_series = len(headers) - 1

    label_tops = {}  # xi -> highest y_top placed so far (approx data units)

    for i in range(n_series):
        col = i + 1
        values = [_parse_numeric(r[col]) if len(r) > col else 0 for r in rows]
        color = _hex_to_rgb01(colors[i % len(colors)])
        ax.plot(x, values, marker="o", color=color, linewidth=2.5, markersize=6,
                label=headers[col], zorder=3)
        max_val = max(abs(v) for v in values) if values else 1
        label_h = max_val * 0.05  # approx label height in data units
        for xi, val in zip(x, values):
            y_pos = val + max_val * 0.02
            prev_top = label_tops.get(xi)
            if prev_top is not None and y_pos < prev_top + label_h:
                y_pos = prev_top + max_val * 0.01  # clear previous label
            ax.text(xi, y_pos, _value_label(val),
                    ha="center", va="bottom", fontsize=7, color=label_color)
            label_tops[xi] = y_pos + label_h

    ax.set_xticks(list(x))
    ax.set_xticklabels(x_labels)
    if n_series > 1:
        ax.legend(fontsize=9, framealpha=0, loc="upper right")


def _render_pie(ax, headers, rows, colors, donut=False):
    labels = [r[0] for r in rows]
    values = [_parse_numeric(r[1]) for r in rows]
    rgb_colors = [_hex_to_rgb01(colors[i % len(colors)]) for i in range(len(values))]

    kw = {"linewidth": 2, "edgecolor": "white"}
    if donut:
        kw["width"] = 0.45

    _, texts, autotexts = ax.pie(
        values, labels=labels, colors=rgb_colors,
        autopct="%1.0f%%", startangle=90,
        wedgeprops=kw,
        pctdistance=0.72 if donut else 0.6,
    )
    for t in texts:
        t.set_fontsize(9)
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("white")
    ax.axis("equal")


def _render_waterfall(ax, headers, rows, colors, label_color="#444444"):
    """
    Waterfall / bridge chart.
    Convention: first row = starting total (absolute), last row = ending total (absolute,
    shown for reference — recalculated from cumulative sum). Middle rows = signed changes.
    """
    labels = [r[0] for r in rows]
    raw = [_parse_numeric(r[1]) for r in rows]
    n = len(labels)

    # Build bottom + height arrays
    bottoms = [0.0] * n
    heights = [0.0] * n
    running = raw[0]
    heights[0] = raw[0]  # start bar from zero

    for i in range(1, n - 1):
        change = raw[i]
        bottoms[i] = running if change >= 0 else running + change
        heights[i] = abs(change)
        running += change

    # End bar: show running total from zero
    heights[-1] = running
    bottoms[-1] = 0.0

    pos_color = _hex_to_rgb01(colors[0])
    neg_color = _hex_to_rgb01(colors[1] if len(colors) > 1 else "#C00000")
    total_color = _hex_to_rgb01("#808080")

    bar_colors = [total_color]
    for i in range(1, n - 1):
        bar_colors.append(pos_color if raw[i] >= 0 else neg_color)
    bar_colors.append(total_color)

    x = np.arange(n)
    ax.bar(x, heights, bottom=bottoms, color=bar_colors, width=0.6, zorder=3)

    # Connector lines between bars
    tops = [b + h for b, h in zip(bottoms, heights)]
    for i in range(n - 2):
        ax.plot([x[i] + 0.31, x[i + 1] - 0.31], [tops[i], tops[i]],
                color="#CCCCCC", linewidth=0.8, zorder=2)

    # Value labels
    for i in range(n):
        display = raw[i] if i in (0, n - 1) else raw[i]
        sign = "+" if raw[i] > 0 and 0 < i < n - 1 else ""
        max_top = max(tops)
        ax.text(x[i], tops[i] + max_top * 0.02,
                f"{sign}{_value_label(display)}",
                ha="center", va="bottom", fontsize=8, color=label_color)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)

    ax.legend(
        handles=[
            mpatches.Patch(color=pos_color, label="Increase"),
            mpatches.Patch(color=neg_color, label="Decrease"),
            mpatches.Patch(color=total_color, label="Total"),
        ],
        fontsize=8, framealpha=0, loc="upper right",
    )


def _render_clustered_bar(ax, headers, rows, colors):
    n_groups = len(rows)
    n_series = len(headers) - 1
    x = np.arange(n_groups)
    bar_w = min(0.8 / n_series, 0.35)

    for i in range(n_series):
        col = i + 1
        values = [_parse_numeric(r[col]) if len(r) > col else 0 for r in rows]
        color = _hex_to_rgb01(colors[i % len(colors)])
        offset = (i - (n_series - 1) / 2) * bar_w
        ax.bar(x + offset, values, bar_w * 0.9, label=headers[col], color=color, zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels([r[0] for r in rows], fontsize=9)
    if n_series > 1:
        ax.legend(fontsize=9, framealpha=0, loc="upper right")


def _render_stacked_bar(ax, headers, rows, colors, normalized=False, label_color="#555555"):
    categories = [r[0] for r in rows]
    n_series = len(headers) - 1
    x = np.arange(len(categories))

    all_series = []
    for i in range(n_series):
        col = i + 1
        all_series.append([_parse_numeric(r[col]) if len(r) > col else 0 for r in rows])

    if normalized:
        totals = [sum(s[j] for s in all_series) for j in range(len(categories))]
        all_series = [
            [v / totals[j] * 100 if totals[j] else 0 for j, v in enumerate(s)]
            for s in all_series
        ]
        ax.set_ylabel("Percentage (%)", fontsize=9, color=label_color)
        ax.yaxis.set_major_formatter(ticker.PercentFormatter())

    bottoms = np.zeros(len(categories))
    for i, series in enumerate(all_series):
        color = _hex_to_rgb01(colors[i % len(colors)])
        ax.bar(x, series, bottom=bottoms, label=headers[i + 1], color=color, width=0.6, zorder=3)
        bottoms += np.array(series)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9)
    if n_series > 1:
        ax.legend(fontsize=9, framealpha=0, loc="upper right")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

CHART_TYPES = {
    "bar", "bar-h", "horizontal-bar",
    "line",
    "pie", "donut", "doughnut",
    "waterfall",
    "clustered-bar", "grouped-bar",
    "stacked-bar", "stacked",
    "stacked-bar-100", "100-stacked",
}

PIE_TYPES = {"pie", "donut", "doughnut"}


def generate_chart(
    chart_type: str,
    data_text: str | None,
    data_file: str | None,
    theme_path: str | None,
    output_path: str,
    title: str | None,
    units: str | None,
    xlabel: str | None,
    ylabel: str | None,
    width: int,
    height: int,
    bg: str = "light",
) -> None:
    # --- Load data ---
    if data_file:
        headers, rows = _load_csv_file(data_file)
    elif data_text:
        headers, rows = _load_csv_text(data_text)
    else:
        sys.exit("ERROR: provide --data or --data-file")

    if not rows:
        sys.exit("ERROR: no data rows found in the provided input")

    dark = bg.strip().lower() == "dark"

    # --- Load colors ---
    # Dark mode uses a brighter palette so bars/lines pop on dark backgrounds.
    # The on-dark palette cycles through the same theme accent slots, but we
    # boost low-contrast swatches by falling back to a set of pre-validated
    # vibrant defaults when the theme accent is very dark.
    colors = _load_theme_colors(theme_path)
    if dark:
        _DARK_DEFAULTS = [
            "#6BA3F5", "#FFB347", "#7FDB97", "#FF6B6B", "#FFD966", "#82E0C8",
        ]
        boosted = []
        for i, c in enumerate(colors):
            h = c.lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            # luminance check — boost if too dark for a dark background
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            boosted.append(c if lum >= 0.35 else _DARK_DEFAULTS[i % len(_DARK_DEFAULTS)])
        colors = boosted

    # --- Create figure ---
    dpi = 150
    fig, ax = plt.subplots(figsize=(width / dpi, height / dpi), dpi=dpi)
    if dark:
        fig.patch.set_facecolor("none")   # transparent — lets slide bg show through
        ax.set_facecolor("none")
    else:
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

    ctype = chart_type.lower().strip()

    # Colors for text labels
    label_color = "#DDDDDD" if dark else "#444444"
    axis_label_color = "#CCCCCC" if dark else "#555555"
    title_color   = "#FFFFFF" if dark else "#222222"
    units_color   = "#CCCCCC" if dark else "#555555"

    # --- Render ---
    if ctype == "bar":
        _render_bar(ax, headers, rows, colors, horizontal=False, label_color=label_color)
    elif ctype in ("bar-h", "horizontal-bar"):
        _render_bar(ax, headers, rows, colors, horizontal=True, label_color=label_color)
    elif ctype == "line":
        _render_line(ax, headers, rows, colors, label_color=label_color)
    elif ctype == "pie":
        _render_pie(ax, headers, rows, colors, donut=False)
    elif ctype in ("donut", "doughnut"):
        _render_pie(ax, headers, rows, colors, donut=True)
    elif ctype == "waterfall":
        _render_waterfall(ax, headers, rows, colors, label_color=label_color)
    elif ctype in ("clustered-bar", "grouped-bar"):
        _render_clustered_bar(ax, headers, rows, colors)
    elif ctype in ("stacked-bar", "stacked"):
        _render_stacked_bar(ax, headers, rows, colors, normalized=False, label_color=axis_label_color)
    elif ctype in ("stacked-bar-100", "100-stacked"):
        _render_stacked_bar(ax, headers, rows, colors, normalized=True, label_color=axis_label_color)
    else:
        sys.exit(
            f"ERROR: unsupported chart type '{chart_type}'.\n"
            f"Supported: bar, bar-h, line, pie, donut, waterfall, "
            f"clustered-bar, stacked-bar, stacked-bar-100"
        )

    # --- Axis styling (not for pie/donut) ---
    if ctype not in PIE_TYPES:
        _apply_axis_style(ax, dark=dark)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=9, color=axis_label_color)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=9, color=axis_label_color)

    # Title block — bold chart title left-aligned, units in regular weight below it.
    # Convention: title aligns with the left edge of the plot area (same x as axis).
    # Do NOT use ax.set_title() — it centres the text and ignores the units line.
    top_offset = 1.13 if units else 1.07
    if title:
        ax.text(
            0.0, top_offset, title,
            transform=ax.transAxes,
            fontsize=11, fontweight="bold", color=title_color,
            va="bottom", ha="left",
        )
    if units:
        ax.text(
            0.0, top_offset - 0.07, units,
            transform=ax.transAxes,
            fontsize=9, fontweight="normal", color=units_color,
            va="bottom", ha="left",
        )

    _add_draft_label(fig, dark=dark)

    # Add headroom above the data so bars/lines never crowd the legend or title
    if ctype not in PIE_TYPES and ctype not in ("bar-h", "horizontal-bar"):
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(top=ymax + (ymax - ymin) * 0.18)

    plt.tight_layout(rect=[0, 0.03, 1, 0.88])  # Reserve space for title block and draft label
    _fix_label_legend_overlap(ax, fig)

    # --- Save ---
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    save_kwargs = dict(dpi=dpi, bbox_inches="tight")
    if dark:
        save_kwargs["transparent"] = True
    else:
        save_kwargs["facecolor"] = "white"
    fig.savefig(output_path, **save_kwargs)
    plt.close(fig)
    print(f"Chart saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a styled draft chart PNG for Slide Lab.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--type", required=True,
        help="Chart type: bar, bar-h, line, pie, donut, waterfall, clustered-bar, stacked-bar, stacked-bar-100",
    )
    parser.add_argument(
        "--data",
        help=r"Inline CSV data. Use \n for newlines. Example: 'Quarter,Revenue\nQ1,1200\nQ2,1450'",
    )
    parser.add_argument(
        "--data-file",
        help="Path to a CSV or Excel (.xlsx) file containing the chart data.",
    )
    parser.add_argument(
        "--theme",
        help="Path to _session/theme.json (from --print-theme). Used for brand colors.",
    )
    parser.add_argument("--output", required=True, help="Output PNG file path.")
    parser.add_argument("--title", help="Chart title text (bold). Example: 'CY29 Net Run-Rate Benefit'")
    parser.add_argument("--units", help="Units label shown below the title in regular weight. Example: '$M' or '# FTEs'")
    parser.add_argument("--xlabel", help="X-axis label.")
    parser.add_argument("--ylabel", help="Y-axis label.")
    parser.add_argument("--width", type=int, default=960,
                        help="Output width in pixels (default: 960).")
    parser.add_argument("--height", type=int, default=540,
                        help="Output height in pixels (default: 540).")
    parser.add_argument(
        "--bg", default="light", choices=["light", "dark"],
        help="Background mode: 'light' (default, white bg + dark text) or "
             "'dark' (transparent bg + light text for dark-accent slides).",
    )
    args = parser.parse_args()

    generate_chart(
        chart_type=args.type,
        data_text=args.data,
        data_file=args.data_file,
        theme_path=args.theme,
        output_path=args.output,
        title=args.title,
        units=args.units,
        xlabel=args.xlabel,
        ylabel=args.ylabel,
        width=args.width,
        height=args.height,
        bg=args.bg,
    )


if __name__ == "__main__":
    main()
