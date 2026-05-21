# Direct python-pptx Patterns — Clone-and-Replace Pipeline

Use this reference when the user wants an **exact design match** to existing slides in a deck — same tables, same layout, same color scheme — and the HTML mockup pipeline is explicitly bypassed. All patterns here were validated in real client sessions and address failure modes that are silent (no error, wrong output).

---

## When to use this pipeline

Use direct python-pptx (not HTML mockups) when:
- The user says "match this existing slide exactly"
- The slide is a table, grid, or structured layout that already exists in the deck
- The user is updating content in 5+ slides with a shared design
- Rebuilding slides inside a large deck (100+ slides) where insertion order matters

Do NOT use this pipeline for net-new creative slides — use the HTML mockup path instead.

---

## Pattern 1 — Clone-and-delete workflow (required order of operations)

The correct sequence for replacing N slides in an existing deck:

```
1. Clone the N source slides → append clones at the END of the presentation
2. Update content on the clones (see Pattern 2)
3. Delete the original N slides in REVERSE index order
4. Save
```

**Why reverse-order deletion:** Deleting a slide shifts all subsequent slide indices down by 1. Deleting from the end first preserves the indices of earlier slides. Forward-order deletion causes wrong slides to be removed.

```python
# Clone slides
from pptx import Presentation
from pptx.util import Inches
import copy

prs = Presentation("deck.pptx")
source_indices = [3, 4, 5, 6, 7, 8]  # 0-based

# Step 1: clone and append
clones = []
for idx in source_indices:
    src_slide = prs.slides[idx]
    blank_layout = prs.slide_layouts[6]  # blank
    new_slide = prs.slides.add_slide(blank_layout)
    new_slide.shapes._spTree[:] = []  # clear blank layout shapes
    # Deep-copy the entire shape tree from the source
    for elem in src_slide.shapes._spTree:
        new_slide.shapes._spTree.append(copy.deepcopy(elem))
    clones.append(new_slide)

# Step 2: update content (see Pattern 2)
for i, slide in enumerate(clones):
    update_slide(slide, data[i])

# Step 3: delete originals in reverse order
xml_slides = prs.slides._sldIdLst
for idx in reversed(source_indices):
    rId = prs.slides._sldIdLst[idx].get("r:id")
    prs.part.drop_rel(rId)
    del xml_slides[idx]

prs.save("deck-updated.pptx")
```

---

## Pattern 2 — Clear-and-recreate text (never modify lxml in-place)

**The critical rule:** Never modify `<a:t>` text elements in-place on cloned slides. When the same source slide is cloned multiple times, the `<a:r>` run elements may share XML node references. In-place writes silently fail or corrupt other clones — no error is raised.

**Always use clear-and-recreate:**

```python
import copy
from lxml import etree

NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

def _get_format_templates(txBody):
    """Extract pPr and rPr from the first paragraph as deep-copied templates."""
    paras = txBody.findall(f"{{{NS}}}p")
    if not paras:
        return None, None
    pPr = paras[0].find(f"{{{NS}}}pPr")
    runs = paras[0].findall(f"{{{NS}}}r")
    rPr = runs[0].find(f"{{{NS}}}rPr") if runs else None
    return (
        copy.deepcopy(pPr) if pPr is not None else None,
        copy.deepcopy(rPr) if rPr is not None else None,
    )

def _write_para(txBody, text, pPr=None, rPr=None):
    """Append one paragraph with one run to txBody."""
    new_p = etree.SubElement(txBody, f"{{{NS}}}p")
    if pPr is not None:
        new_p.insert(0, copy.deepcopy(pPr))
    new_r = etree.SubElement(new_p, f"{{{NS}}}r")
    if rPr is not None:
        new_r.insert(0, copy.deepcopy(rPr))
    etree.SubElement(new_r, f"{{{NS}}}t").text = text

def set_single_text(shape, text):
    """Replace all text in a shape with a single paragraph."""
    if not shape.has_text_frame:
        return
    txBody = shape.text_frame._txBody
    pPr, rPr = _get_format_templates(txBody)
    for p in list(txBody.findall(f"{{{NS}}}p")):
        txBody.remove(p)
    _write_para(txBody, text, pPr, rPr)

def set_bullet_text(shape, lines):
    """Replace all text in a shape with multiple bullet paragraphs."""
    if not shape.has_text_frame:
        return
    txBody = shape.text_frame._txBody
    pPr, rPr = _get_format_templates(txBody)
    for p in list(txBody.findall(f"{{{NS}}}p")):
        txBody.remove(p)
    for line in lines:
        _write_para(txBody, line, pPr, rPr)
```

**Why this works:** `_get_format_templates` extracts `pPr` and `rPr` as deep copies before the existing paragraphs are removed. Each new paragraph and run gets its own deep copy of those templates, so there are no shared references.

**Side benefit:** This correctly handles titles with mixed-color runs (e.g., `"Initiative 1 : Payables Optimization"` stored as run[0]=dark gray + run[1]=purple). The clear-and-recreate approach uses `rPr` from run[0] only and rebuilds as a single run — avoiding the silent failure of the in-place approach which could only update the first run.

---

## Pattern 3 — Find shapes by position (not by name)

Shape names are not stable across cloned slides. The reliable method is matching by position in inches with a tolerance.

```python
from pptx.util import Emu

def find_shape_by_position(slide, x_in, y_in, tolerance=0.35):
    """
    Find a shape by its top-left position in inches.
    tolerance: allowed delta in inches (default 0.35")
    """
    assert isinstance(slide, __import__('pptx').slide.Slide), \
        f"Expected Slide, got {type(slide)}"
    for shape in slide.shapes:
        shape_x = shape.left / 914400   # EMU → inches
        shape_y = shape.top  / 914400
        if abs(shape_x - x_in) <= tolerance and abs(shape_y - y_in) <= tolerance:
            return shape
    return None

def find_oval_badge(slide, x_in, y_in, tolerance=0.35):
    """Find an oval/circle shape by position — used for numbered badges."""
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    shape = find_shape_by_position(slide, x_in, y_in, tolerance)
    if shape and shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
        return shape
    return None

def find_title_placeholder(slide):
    """Find the title placeholder by placeholder type, not by name."""
    from pptx.util import PP_PLACEHOLDER
    for ph in slide.placeholders:
        if ph.placeholder_format.type in (
            PP_PLACEHOLDER.TITLE,
            PP_PLACEHOLDER.CENTER_TITLE,
        ):
            return ph
    return None
```

**How to find the right coordinates:** Run `check_slide_geometry.py` (in `scripts/`) on the source deck. It prints each shape's position in inches — copy those values into `find_shape_by_position` calls.

**EMU conversion reference:**
- 1 inch = 914,400 EMU
- `shape.left / 914400` → x position in inches
- `shape.top  / 914400` → y position in inches
- `shape.width / 914400` → width in inches

---

## Pattern 4 — Type guard on find functions

python-pptx's duck-typed API makes `ShapeCollection` vs `Slide` mismatches invisible at runtime — the function iterates incorrectly, returns `None` silently, and all content updates are skipped. Add a guard to every find function:

```python
from pptx.slide import Slide

def find_shape_by_position(slide, x_in, y_in, tolerance=0.35):
    assert isinstance(slide, Slide), \
        f"find_shape_by_position expects a Slide, got {type(slide).__name__}. " \
        f"Did you pass slide.shapes instead of slide?"
    ...
```

**Common mistake:** Assigning `shapes = new_slide.shapes` at the top of a loop, then passing `shapes` to find helpers after refactoring those helpers to accept `slide`. The `isinstance` guard turns this into an immediate readable error instead of a silent wrong-output.

---

## Pattern 5 — Multi-run title detection (inspection)

Branded templates often store title text as multiple runs with different colors (e.g., label in dark gray, keyword in brand purple). If your inspection script shows a title placeholder with `>1 run`, note it before writing any text-update code.

```python
def inspect_title_runs(slide):
    """Print run count and color for the title placeholder."""
    for shape in slide.placeholders:
        if shape.placeholder_format.idx == 0:  # title
            tf = shape.text_frame
            for p_idx, para in enumerate(tf.paragraphs):
                runs = para.runs
                print(f"Para {p_idx}: {len(runs)} run(s)")
                for r_idx, run in enumerate(runs):
                    color = run.font.color.rgb if run.font.color and run.font.color.type else "inherited"
                    print(f"  Run {r_idx}: '{run.text}' | color={color}")
```

If a title has 2+ runs with distinct colors, the clear-and-recreate pattern (Pattern 2) handles it correctly — it uses `rPr` from run[0] and collapses to a single run. The in-place approach will silently fail on the second run.

---

## Summary — rules at a glance

| Rule | Why |
|---|---|
| Clone → append → update → delete (reverse order) | Forward deletion shifts indices and removes wrong slides |
| Never modify lxml elements in-place on clones | Shared XML references cause silent failures on multi-clone sessions |
| Always extract `pPr`/`rPr` as `copy.deepcopy` before clearing | Preserves paragraph + run formatting without shared references |
| Find shapes by position (inches + tolerance), not by name | Shape names are not stable across clones |
| Type-guard find functions with `isinstance(slide, Slide)` | ShapeCollection passed as Slide fails silently — guard makes it immediate |
| Run `inspect_title_runs` before writing any title update code | Branded titles often have 2+ runs with distinct colors |
