# Dispatch plan — slide-builder prep

- Brief:           C:\Users\m.a.peralta\.claude\skills\.claude\worktrees\agent-abaae9e70ed8f6544\slide-builder\_decisions\v0.3-audit-workspace\collision\brief_2slide.md
- Client template: C:\Users\m.a.peralta\OneDrive - Accenture\Library\FedEx\OTC\OTC Opportunity.pptx
- Client slug:     otc
- Mermaid theme:   C:\Users\m.a.peralta\.claude\skills\.claude\worktrees\agent-abaae9e70ed8f6544\slide-builder\theme\mermaid-otc.json
- Slide total:     2

## Per-slide forecast (adjacency context — NOT a constraint)

| Slide | Title | Forecasted pattern |
|---|---|---|
| 1 | Light AR findings | Chart (with quadrant mode) |
| 2 | Dark funnel | Full canvas |

## Per-slide artifact locations

- Slide 1: `slide-builder\_decisions\v0.3-audit-workspace\collision\build\slide_01\_prompt.md`
- Slide 2: `slide-builder\_decisions\v0.3-audit-workspace\collision\build\slide_02\_prompt.md`

## Next step

Parent session dispatches one `slide-builder-worker` agent per slide IN PARALLEL using the rendered `_prompt.md` files above. Each agent writes `option_A.py`, `option_B.py`, `option_C.py` (plus `option_X.mmd` for Mermaid-fallback slides) into its own `slide_NN/` directory. Then run `finalize_deck.py` to graft, render, and produce REVIEW.html.