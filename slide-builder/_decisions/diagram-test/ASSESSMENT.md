# Diagram Feasibility Test — Assessment

Generated 2026-05-25. Four standalone python-pptx diagrams built using `twins/helpers.py` for chrome + raw `shape.add_shape`/`shape.add_connector` for the diagram bodies. Rendered to PNG via LibreOffice headless.

Files in this folder:
- `diagram1-orgchart.py` / `.pptx` / `.png`
- `diagram2-swimlane.py` / `.pptx` / `.png`
- `diagram3-hubspoke.py` / `.pptx` / `.png`
- `diagram4-decisiontree.py` / `.pptx` / `.png`

---

## Diagram 1 — Org chart (3-level hierarchy)

1. **Did it render?** Yes.
2. **Legible / partner-ready?** Mostly. Boxes align on a 3-column grid; connectors are real `add_connector` straight lines (horizontal bus + vertical stubs) so the tree topology reads instantly.
3. **What broke or looks amateur:**
   - Role descriptions inside L1 / L2 nodes use `BRAND_ACCENT_SOFT` (light purple) on `BRAND_PRIMARY` / `BRAND_PRIMARY_MID` fill — contrast is low; secondary line looks washed out.
   - Multi-line role text is `align="center"` but visually looks left-shifted because the text box has padding artifacts.
   - Minor: vertical stubs at the L3 bus crossing show a faint visual collision where the L2 vertical stub and the L3 bus terminate at the same x, but a partner wouldn't notice unless zooming.
4. **Verdict: SHIPPABLE** — with a contrast tweak on the role description color, this goes in front of a client tomorrow.

## Diagram 2 — Swimlane (3 lanes × 4 steps, L→R with hand-offs)

1. **Did it render?** Yes.
2. **Legible / partner-ready?** Yes. The L-shape connectors between lane hand-offs (Sales→Ops, Ops→Finance) read as intentional process hand-offs. Arrow heads are clean PowerPoint `RIGHT_ARROW` shapes, not glyphs. Critical-path step (Collect & post cash) lights up in accent purple.
3. **What broke or looks amateur:**
   - The two L-shape down-then-right hand-offs between lanes are visually fine but could read as "process moves down, then right" rather than a hand-off; an arrow head on the vertical segment would help.
   - Lane label boxes (Sales, Operations, Finance) use brand-primary, mid, and accent-soft — three different colors makes lanes look hierarchical when they are siblings. Should be one tone or a graduated tint.
   - White space inside the lanes is large — could be tightened with smaller lane height or fewer columns.
4. **Verdict: SHIPPABLE** — minor cosmetic improvements only.

## Diagram 3 — Hub-and-spoke (Porter 5 Forces variant)

1. **Did it render?** Yes.
2. **Legible / partner-ready?** Borderline. The compass layout is perfectly symmetric, arrows point into the hub with proper triangle heads (added via raw OOXML `<a:tailEnd>`).
3. **What broke or looks amateur:**
   - **Text inside circles wraps badly.** "Low capex barriers / attract / regional Asian producers" wraps because the textbox is rectangular and bumps against the curved edge — line breaks fall in awkward places. This is the standard problem with text-in-circles in PPT.
   - Hub subtitle "Specialty / Chemicals" displays on two lines and looks crammed under "Our Firm". A single-line subtitle would be cleaner.
   - The light purple satellite borders (CARD_BORDER) are barely visible at projection contrast.
4. **Verdict: NEEDS-HEAVY-EDIT** — the text-in-circle problem is a recurring failure mode. Solution would be to use circles only for the visual node and place labels in rectangular text boxes BELOW or BESIDE the circle, not inside. That's a structural redesign, not a tweak.

## Diagram 4 — Decision tree (root → 2 branches → 4 leaves)

1. **Did it render?** Yes.
2. **Legible / partner-ready?** Yes. Tree topology is unambiguous; diagonal connector lines from parent to child read as a tree (not as a grid). Edge labels "Yes" / "No" sit legibly between root and branch boxes. Accent on "Pilot region *" cleanly marks the recommendation.
3. **What broke or looks amateur:**
   - The "Yes" and "No" edge labels sit BESIDE the diagonal lines, not on them — fine but a designer would label the lines directly.
   - The footnote "* Recommended path" at the bottom is positioned awkwardly above the standard footer zone. Could be inline with the leaf box instead.
   - Diagonal connector angles are slightly inconsistent (Yes side has wider spread than No side) because parent-to-leaf x-distances differ.
4. **Verdict: SHIPPABLE** — the diagonal connector approach worked surprisingly well. A partner could present this as-is.

---

## Overall Recommendation

**(b) Keep the three that worked, drop the one that broke.**

- **Keep as ontology primitives:** org-chart, swimlane, decision-tree. All three rendered cleanly in <80 lines of python-pptx using `add_shape` + `add_connector`. Connector routing via `slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT)` plus arrow-head OOXML poke is reliable. The hierarchical bus + stub pattern works for both org chart (orthogonal) and decision tree (diagonal). Swimlane works by drawing lane rects then placing step rects inside.
- **Drop or replace:** hub-and-spoke with text-inside-circles. The text-wrap problem inside a circle is intrinsic — python-pptx can't shape-fit text. The fix would be to put labels OUTSIDE the satellite shapes, which changes the visual language and makes the hub-spoke look less like a network diagram. If this primitive ships, it must enforce labels-outside-circles in the helper signature.
- **Underlying observation:** Mario's prior intuition that "diagrams come out crooked" was correct for diagrams that depend on text inside curved containers or on auto-routed connectors. Orthogonal layouts with explicit (x, y) connector endpoints render reliably. SmartArt-style auto-routing is what historically broke; explicit connectors don't.

Final ontology proposal: ship org-chart, swimlane, decision-tree as ontology primitives. For hub-spoke and other curved-container diagrams, keep the HTML→PNG screenshot fallback path.
