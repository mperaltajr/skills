# Process Icon Vocabulary

Icons are visual shape elements used above bucket/column headers in multi-column structured layouts (phases, pillars, workstreams, capability groupings). They reinforce the concept of each bucket without using text alone.

**Icons are NOT emojis or unicode characters in text boxes.** They are CSS/SVG shapes in the Phase A HTML mockup, replaced by bundled PNG files during Phase B build.

---

## When to use process icons

- **Use:** Multi-column layouts with 2–5 structural buckets, each with a clear conceptual theme (e.g., Plan / Execute / Monitor; People / Process / Technology)
- **Use:** Slide types where each column represents a distinct workstream, phase, or pillar
- **Don't use:** Tables, lists, charts, single-column slides, data-heavy layouts
- **Don't use:** When the bucket header already has strong visual differentiation (color bands, numbering, dividers)

Icons sit **above** the bucket header text, centered horizontally within the column. They should be 36–48px in the mockup (translates to ~27–36pt in PPTX). Color-tinted at build time using the template's first accent color.

---

## Icon vocabulary — standard set

The bundled PNG library lives at `slide-builder/icons/<data-icon-value>.png`. Each icon is 128×128px, monochrome (black on transparent), tinted at build time.

| Concept | `data-icon` value | Use when | Typical bucket header |
|---------|-------------------|----------|-----------------------|
| Process / operations | `gear` | Operational workflow, process steps, methodology | "Process", "Operations", "Workflow" |
| Work in progress | `wrench` | Active work, in-flight tasks, implementation | "In Progress", "Build", "Implement" |
| People / team | `people` | Workforce, stakeholders, org, change management | "People", "Team", "Organization" |
| Data / analytics | `chart-bar` | Reporting, data strategy, analytics capability | "Data", "Analytics", "Insights" |
| Strategy / direction | `compass` | Strategic direction, north star, vision | "Strategy", "Direction", "Vision" |
| Timeline / schedule | `calendar` | Roadmap, scheduling, milestones, planning | "Timeline", "Schedule", "Plan" |
| Cost / budget | `coins` | Financial planning, budget, cost management | "Cost", "Finance", "Investment" |
| Risk / escalation | `shield-warning` | Risk management, controls, blockers | "Risk", "Controls", "Compliance" |
| Decision / approval | `diamond` | Decision points, governance, escalation | "Decide", "Approve", "Governance" |
| Insight / finding | `lightbulb` | Discoveries, key findings, recommendations | "Insights", "Findings", "Recommendations" |
| External / market | `globe` | Market context, external partners, regulatory | "Market", "External", "Regulatory" |
| Compliance / audit | `clipboard-check` | Audit, controls, governance, certification | "Audit", "Compliance", "Quality" |
| Technology / systems | `chip` | Tech stack, platforms, digital, IT | "Technology", "Systems", "Digital" |
| Communication | `speech` | Change management, communications, engagement | "Communications", "Engagement", "Change" |
| Delivery / output | `package` | Deliverables, milestones, outputs, products | "Deliverables", "Output", "Milestones" |

---

## Phase A HTML pattern

In Phase A mockups, each icon is rendered as an inline SVG inside a `div.process-icon` container. The SVG is a visual approximation only — Phase B ignores the SVG and replaces the bounding box with the bundled PNG.

```html
<!-- Process icon above a bucket header -->
<div style="display:flex; flex-direction:column; align-items:center;">
  
  <!-- Icon container — Phase B reads the bounding box and data-icon attribute -->
  <div class="process-icon" data-icon="gear"
       style="width:40px; height:40px; margin:0 auto 10px auto;">
    <!-- Inline SVG: visual approximation for HTML preview only -->
    <!-- Phase B replaces this entire div's visual with the bundled PNG -->
    <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"
         style="width:100%; height:100%;">
      <circle cx="20" cy="20" r="7" stroke="#4D148C" stroke-width="2.5"/>
      <circle cx="20" cy="20" r="13" stroke="#4D148C" stroke-width="1.5" stroke-dasharray="4 3"/>
    </svg>
  </div>

  <!-- Bucket header text -->
  <div style="font-size:14px; font-weight:700; color:#4D148C; text-align:center;">
    Process
  </div>

</div>
```

**Rules for the icon container:**
- Always `<div class="process-icon" data-icon="[name]">` — not a `<span>`
- The SVG inside is for HTML preview only — Phase B skips it entirely
- `data-icon` must match a value in the icon vocabulary table above exactly
- Width and height in the container `style` attribute determine the icon's size in PPTX
- Color in the SVG stroke should match the template's primary accent color for accurate preview

**SVG approximations by concept:**

| `data-icon` | SVG approximation (40×40 viewBox) |
|-------------|-----------------------------------|
| `gear` | Two concentric circles (r=7, r=13) with the outer one dashed |
| `wrench` | Rectangle rotated 45° with a circle at one end |
| `people` | Two overlapping circles (heads) above two arc shapes (shoulders) |
| `chart-bar` | Three vertical rectangles of increasing height |
| `compass` | Circle with four cardinal tick marks and a diamond center point |
| `calendar` | Rectangle with a grid of 3×3 dots and two tabs at top |
| `coins` | Two overlapping ellipses (stacked coins) |
| `shield-warning` | Pentagon shield outline with an exclamation mark inside |
| `diamond` | 45° rotated square (diamond shape) |
| `lightbulb` | Teardrop/bulb shape with three short lines below (base) |
| `globe` | Circle with horizontal ellipse and vertical line through center |
| `clipboard-check` | Rectangle with a clip at top and a checkmark inside |
| `chip` | Square with small rectangles on each side (IC chip pins) |
| `speech` | Rounded rectangle with a triangular notch at bottom-left |
| `package` | Cube with a fold line at the top and a horizontal stripe |

---

## Phase B rendering rule

When `build_slide.py` DOM walker encounters `div.process-icon[data-icon]`:

1. Capture the container's bounding box (position and size)
2. Skip all child SVG elements — do not attempt to render SVG paths
3. Look up `slide-builder/icons/<data-icon-value>.png`
4. If found: insert as a picture shape at the captured position and size
5. Apply accent color tint using the template's `accent1` hex from `theme.json` (multiply blend at 80% opacity via PIL; fallback: insert untinted if PIL unavailable)
6. If the named icon PNG does not exist: insert a labeled rectangle placeholder with the icon concept name and a dashed border

**Tinting logic (Python, using PIL):**
```python
from PIL import Image
import pathlib

def tint_icon(icon_path: str, hex_color: str) -> Image.Image:
    icon = Image.open(icon_path).convert("RGBA")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    tint = Image.new("RGBA", icon.size, (r, g, b, 255))
    result = Image.new("RGBA", icon.size, (255, 255, 255, 0))
    result.paste(tint, mask=icon.split()[3])
    return result
```

**Fallback (no PIL):** Insert the raw PNG without tinting. Add a post-build note: "Process icons inserted without accent tint — install `Pillow` for automatic color matching."

---

## Post-build note

Add this to the delivery message for any deck that includes process icons:

> **Process icons:** Icons are rendered from the bundled icon library and tinted to match the template's accent color. For client-ready decks, review icons to ensure they match your client's approved icon set and replace if needed. Replacement takes ~2 minutes per icon in PowerPoint (Insert → Pictures → This Device).
