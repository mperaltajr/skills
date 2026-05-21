# Blueprint schema

A blueprint is a JSON file describing one slide's layout. The executor (`scripts/build_slide.py`) reads a blueprint + a content JSON and produces a slide.

The blueprint declares *zones* (where things go); the content declares *slots* (what fills them). They're joined by slot names: every zone in the blueprint that needs content references a `slot` name; the content JSON has a top-level key matching that name.

## Top-level fields

```json
{
  "id": "<unique_id>",
  "layout_pattern": "<chassis layout name from glossary.md>",
  "page_types": ["<page type from page-types.md>", ...],
  "title": { ... },
  "sub_headline": { ... },             // optional
  "description_strip": { ... },         // optional
  "body": { ... },                      // required
  "comments_panel": { ... },            // optional, alt to takeaway_panel
  "takeaway_panel": { ... },            // optional, alt to comments_panel
  "bottom_takeaway": { ... },           // optional
  "invariant": true                     // default: true
}
```

## Zone shapes

### `title`
```json
{"x": 58, "y": 37, "w": 1164, "h": 76, "slot": "action_title"}
```

### `sub_headline`
```json
{"x": 58, "y": 120, "w": 1164, "h": 18, "slot": "sub_headline"}
```

### `description_strip` (chart slides — sits between title and body)
```json
{
  "description": {"x": 58, "y": 183, "w": 752, "h": 44, "slot": "chart_description"},
  "data_label":  {"x": 58, "y": 244, "w": 200, "h": 19, "slot": "data_label"}
}
```

### `body` — required, kind determines shape
**Chart body:**
```json
{
  "x": 58, "y": 283, "w": 752, "h": 349,
  "kind": "chart",
  "chart_type": "column_clustered",
  "data_slot": "chart_data"
}
```
Supported `chart_type`: `column_clustered`, `column_stacked`, `column_stacked_100`, `bar_clustered`, `bar_stacked`, `line`, `line_markers`, `scatter`.

**Bullets body:**
```json
{
  "x": 58, "y": 151, "w": 1164, "h": 481,
  "kind": "bullets",
  "slot": "body_bullets",
  "font_size": 12
}
```

**Multi-bucket body:**
```json
{
  "x": 58, "y": 151, "w": 1164, "h": 481,
  "kind": "multi_bucket",
  "buckets_slot": "buckets"
}
```
Content for `buckets_slot` is an array of `{"header": "...", "bullets": [...], "footer": "..."}`. Header and footer are optional; bullets is the body content.

**Comparison-table body:**
```json
{
  "x": 58, "y": 151, "w": 1164, "h": 481,
  "kind": "comparison_table",
  "has_row_labels": true,
  "table_slot": "table"
}
```
Content for `table_slot` is `{"columns": [...], "rows": [[...], [...], ...]}`. First row is auto-styled as headers. If `has_row_labels` is true, the first column is bold per row.

### `comments_panel` (right-side, vertical dashed divider)
```json
{
  "x": 831, "y": 183, "w": 390, "h": 480,
  "header_slot": "panel_header",
  "bullets_slot": "panel_bullets"
}
```

### `takeaway_panel` (right-side, may include hero stat)
```json
{
  "x": 848, "y": 151, "w": 374, "h": 481,
  "header_slot": "panel_header",
  "hero_stat_slot": "hero_stat",
  "bullets_slot": "panel_bullets"
}
```
`hero_stat_slot` is optional. If present and content provides a value, it renders as 36pt bold center-aligned above the bullets.

### `bottom_takeaway` (full-width strip below body)
```json
{"x": 58, "y": 596, "w": 1164, "h": 36, "slot": "bottom_takeaway"}
```

### `invariant`
Boolean. Defaults to true. When true, the executor adds:
- Footnote (slot: `footnote`)
- Source (slot: `source`)
- Page number (slot: `page_number`, defaults to "#")
- Draft watermark (always "DRAFT" in red)

## Content schema

For every blueprint zone with a `slot`, the content JSON has a top-level key with that name.

```json
{
  "action_title": "string",
  "sub_headline": "string",
  "chart_description": "string",
  "data_label": "string",
  "chart_data": {"categories": [...], "series": {...}},
  "panel_header": "string",
  "panel_bullets": ["string", "string", ...],
  "buckets": [{"header": "...", "bullets": [...], "footer": "..."}, ...],
  "table": {"columns": [...], "rows": [[...], ...]},
  "footnote": "string",
  "source": "string"
}
```

## Authoring rules

- Coordinates are pixels at 1280×720.
- Reference `glossary.md` for canonical zone coordinates. Don't invent positions.
- `page_types` should match strings in `page-types.md`.
- `id` should be unique. Convention: `<deck>__slide_<N>` for template-derived blueprints, `<descriptive_name>` for ad-hoc.
- Content slot names should be descriptive (`chart_data` not `cd`).
- Don't put colors or fonts in the blueprint. Theme inheritance from the client template handles those.

## Example

See `blueprints/02_bar_charts__slide_2.json` for a complete chart-with-comments-panel example, and `blueprints/01_executive_summary__slide_8.json` for multi-bucket.
