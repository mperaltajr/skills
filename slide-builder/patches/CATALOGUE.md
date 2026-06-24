# Patch Catalogue — Slide Lab

Patches are named python-pptx operations applied after token fill.
The skill calls them by name. Each patch has a defined trigger condition.

---

## get_named_layout(prs, layout_name)
Select a template's named slide layout (case-insensitive exact then substring match, blank fallback).
- **Trigger:** brief targets a specific template layout, e.g. a cover/title slide or a dark section divider
- **layout_name:** `"Cover"` matches "Cover: gradient"; `"dark"` matches first layout containing "dark"
- **Used via:** `skeleton_on_template(..., layout_name="Cover")` or `skeleton_from_pptx(..., layout_name=...)`

## add_comparison_table(slide, left_heading, right_heading, rows, x_in=0.607, y_in=1.5, w_in=12.12, ...)
Add a native 3-column PPTX comparison table (Criterion | Option A | Option B).
- **Trigger:** two-panel brief has variable row count OR the data is structured criteria vs. two options
- **rows:** `[("Criterion label", "Left value", "Right value"), ...]` — any number of rows
- **Replaces:** the 32-token text-box grid in the two-panel skeleton for dynamic comparisons
- **Returns:** the table shape
- **Example:** `add_comparison_table(slide, "Build Internal", "Guidewire", [("Cost", "$14M", "$13M"), ...])`

## find_shape_by_token(slide, token_name)
Locate a shape by its `{{TOKEN}}` content. Use before fill to get a shape reference.
- **Returns:** shape object or None

## find_shape_by_name(slide, shape_name)
Locate a shape by its exact PPTX shape name.
- **Returns:** shape object or None

## fill_tokens(slide, token_map)
Replace `{{KEY}}` → value across all shapes. Main fill operation.
- **token_map:** `{"ACTION_TITLE": "My title", "BULLET_1": "First point", ...}`
- **Returns:** list of token names successfully replaced

---

## convert_to_bullets(shape, items, bullet_char="•")
Replace shape text with a bulleted list.
- **Trigger:** brief has 3+ discrete items instead of continuous prose
- **items:** `["First point", "Second point", "Third point"]`
- **Preserves:** font size and color of the original shape's first run

## reposition_zone(shape, x_in, y_in)
Move shape to (x_in, y_in) in inches. Width/height unchanged.
- **Trigger:** reading path check (Rule 4A) fails for default skeleton position
- **Example:** move RAG legend from mid-slide to top-right corner

## resize_zone(shape, width_in=None, height_in=None)
Resize shape. Pass only the dimension(s) to change.
- **Trigger:** content is longer or shorter than skeleton default
- **Example:** 6-bullet list needs taller body zone than default 4-bullet height

## add_hero_stat(slide, stat_value, stat_label, x_in, y_in, w_in, h_in, color, stat_pt=60, label_pt=14)
Add a large stat number with a smaller label below it.
- **Trigger:** brief has a key quantitative finding to lead with
- **Example:** "14%" at 60pt bold, "cost increase YoY" at 14pt below
- **Returns:** stat shape

## set_shape_fill(shape, hex_color)
Set shape fill to a hex color.
- **Trigger:** template accent color needs to be applied to a structural zone
- **hex_color:** `"#A100FF"` (with or without #)

## set_rag_status(shape, status)
Set shape fill to the RAG color for the given status.
- **Trigger:** status field in brief maps to a RAG indicator shape
- **status:** `"green"` / `"g"` / `"amber"` / `"yellow"` / `"a"` / `"red"` / `"r"`

## add_table_row(table_shape, row_data)
Append a row to a native PowerPoint table. Clones formatting from last row.
- **Trigger:** table has variable row count depending on brief data
- **row_data:** `["Action item text", "Owner name", "2026-06-01"]`

## generate_chart(..., bg="dark")
Generate a chart PNG with transparent background and light-colored text for dark-zone slides.
- **Trigger:** brief targets a chart-with-takeaway slide where the CWT body zone has a dark fill
- **bg="dark":** saves RGBA PNG (transparent=True), white/light labels, luminance-boosted accent palette
- **bg="light" (default):** white background, dark labels — unchanged from earlier behaviour
- **Zone fill:** after `skeleton_from_pptx`, find the body rectangle by position (`abs(shape_top - 1.57) < 0.1`) and call `set_shape_fill(shape, "1A1A2E")` before inserting the chart PNG
- **Note:** CWT zone shapes are positional — use position lookup, not `find_shape_by_token`

## insert_icon(slide, icon_name, x_in, y_in, size_in, accent_hex="#000000")
Insert a pre-extracted icon at the given position, color-swapped to accent_hex.
- **Trigger:** brief mentions a concept that maps to an icon in the vocabulary
- **icon_name:** must match a filename (without extension) under `icons/`; `Get-ChildItem icons/*.xml | Select-Object Name` enumerates the available glyphs
- **Returns:** True on success, False if placeholder inserted (icon not found)
- **Fallback:** inserts a labeled dashed-border placeholder — never crashes
