"""
generate_review.py — Build a review UI from rendered PNG options.

Usage:
    python generate_review.py <session_folder> [--output review.html] [--title "Session title"]

Session folder structure (auto-detected):
    session_folder/
        slide_01_A.png
        slide_01_B.png
        slide_02_A.png
        ...

Naming convention: slide_NN_[A-Z].png  (NN = zero-padded slide number)

Output:
    review.html in session_folder (or --output path)

User flow:
    1. Open review.html in browser
    2. For each slide: pick an option, approve as-is, or request new options
    3. Add zone-level feedback and/or exact replacement text per zone
    4. Add deck-level notes at the top if needed
    5. Click Save — browser downloads review-selections.md
    6. Pass that file to Claude: "read review-selections.md and apply the feedback"

Selections are auto-saved to localStorage — closing the tab does not lose your work.
"""

import sys
import os
import re
import argparse
import base64
from pathlib import Path
from collections import defaultdict


# ---------------------------------------------------------------------------
# PNG grouping
# ---------------------------------------------------------------------------

def collect_slide_options(folder: Path) -> list:
    pattern = re.compile(r"^slide_(\d+)_([A-Z])\.png$", re.IGNORECASE)
    groups = defaultdict(dict)

    for f in sorted(folder.iterdir()):
        m = pattern.match(f.name)
        if m:
            num = int(m.group(1))
            opt = m.group(2).upper()
            groups[num][opt] = f

    slides = []
    for num in sorted(groups.keys()):
        opts = groups[num]
        slide_entry = {
            "num": num,
            "label": f"Slide {num}",
            "options": [{"id": k, "path": opts[k]} for k in sorted(opts.keys())],
        }
        slides.append(slide_entry)

    return slides


def png_to_data_uri(path: Path) -> str:
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{data}"


# ---------------------------------------------------------------------------
# Zone definitions
# ---------------------------------------------------------------------------

ZONE_NAMES = [
    "Title / Governing thought",
    "Sub-headline",
    "Body / Content",
    "Chart",
    "Conclusion / Takeaway",
    "Overall design",
    "Other",
]

ZONE_PLACEHOLDERS = [
    "e.g. Too long — shorten to one clause. Or: rephrase to lead with the so-what",
    "e.g. Too wordy — cut to one sentence. Or: should explain WHY not WHAT",
    "e.g. Bullet 2 needs a number — add '$1.2M saved'. Or: swap rows 2 and 3",
    "e.g. Switch to bar chart. Or: add axis labels. Or: highlight Q3 bar in accent color",
    "e.g. Wording too vague — make it a specific decision. Or: move to right panel",
    "e.g. Too crowded — reduce to 3 rows. Or: try a dark background. Or: column widths uneven",
    "e.g. Add source citation. Or: this slide should come after slide 3",
]



# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f0f2f5;
    color: #1a1a1a;
    padding: 32px 24px 120px;
    max-width: 1400px; margin: 0 auto;
  }}

  h1 {{ font-size: 22px; font-weight: 700; margin-bottom: 6px; }}
  .subtitle {{ font-size: 13px; color: #666; margin-bottom: 24px; }}

  /* ── Deck-level notes ── */
  .deck-notes-panel {{
    background: #fff;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 28px;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
    border-left: 4px solid #4f83b7;
  }}
  .deck-notes-label {{
    font-size: 13px; font-weight: 700; color: #1a1a2e;
    margin-bottom: 8px; display: block;
  }}
  .deck-notes-sub {{
    font-size: 12px; color: #888; margin-bottom: 10px;
  }}
  .deck-notes-field {{
    width: 100%; min-height: 60px;
    border: 1px solid #ddd; border-radius: 6px;
    padding: 8px 10px; font-size: 13px; color: #333;
    resize: vertical; font-family: inherit;
    transition: border-color .15s;
  }}
  .deck-notes-field:focus {{ outline: none; border-color: #4f83b7; }}

  /* ── Slide section ── */
  .slide-section {{
    background: #fff;
    border-radius: 10px;
    padding: 24px 28px 28px;
    margin-bottom: 28px;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
    transition: box-shadow .15s;
  }}
  .slide-section.approved {{ border-left: 4px solid #00703c; }}
  .slide-section.rejected {{ border-left: 4px solid #c0392b; }}
  .slide-section.picked   {{ border-left: 4px solid #1a1a2e; }}

  .slide-header {{
    font-size: 15px; font-weight: 600; margin-bottom: 16px;
    padding-bottom: 10px; border-bottom: 1px solid #e8e8e8;
    display: flex; align-items: center; gap: 10px;
  }}
  .slide-num {{
    background: #1a1a2e; color: #fff;
    font-size: 11px; font-weight: 700;
    padding: 3px 8px; border-radius: 4px;
  }}
  .slide-status-badge {{
    display: none; margin-left: auto;
    font-size: 11px; font-weight: 700;
    padding: 3px 10px; border-radius: 12px;
  }}
  .slide-section.approved .slide-status-badge {{
    display: inline-block; background: #e8f5e9; color: #00703c;
  }}
  .slide-section.rejected .slide-status-badge {{
    display: inline-block; background: #fdecea; color: #c0392b;
  }}
  .slide-section.picked .slide-status-badge {{
    display: inline-block; background: #e8eaf6; color: #1a1a2e;
  }}

  /* ── Option cards ── */
  .options-row {{
    display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px;
    align-items: flex-start;
  }}
  .option-card {{
    flex: 1; min-width: 220px;
    border: 2px solid #e0e0e0;
    border-radius: 8px; overflow: hidden;
    cursor: pointer; transition: border-color .15s, box-shadow .15s;
    position: relative;
  }}
  .option-card:hover {{ border-color: #4f83b7; box-shadow: 0 2px 8px rgba(79,131,183,.2); }}
  .option-card.selected {{ border-color: #1a1a2e; box-shadow: 0 2px 10px rgba(26,26,46,.25); }}
  .option-header {{
    display: flex; align-items: center; gap: 8px;
    padding: 7px 12px;
    background: #f7f7f7; border-bottom: 1px solid #e0e0e0;
  }}
  .option-card.selected .option-header {{ background: #1a1a2e; color: #fff; }}
  .option-radio {{ accent-color: #1a1a2e; }}
  .option-label {{ font-size: 13px; font-weight: 600; }}
  .option-img {{ display: block; width: 100%; background: #f0f0f0; }}
  .selected-badge {{
    display: none; position: absolute; top: 6px; right: 6px;
    background: #1a1a2e; color: #fff;
    font-size: 10px; font-weight: 700;
    padding: 2px 7px; border-radius: 10px;
  }}
  .option-card.selected .selected-badge {{ display: block; }}

  /* ── Special action cards (Approve / Generate more) ── */
  .action-cards {{
    display: flex; flex-direction: column; gap: 8px;
    min-width: 160px; flex-shrink: 0;
  }}
  .action-card {{
    border: 2px solid #e0e0e0;
    border-radius: 8px; padding: 12px 14px;
    cursor: pointer; transition: border-color .15s, background .15s;
    display: flex; align-items: center; gap: 10px;
  }}
  .action-card:hover {{ border-color: #999; }}
  .action-card.approve-card {{ }}
  .action-card.approve-card.selected {{ border-color: #00703c; background: #f0faf4; }}
  .action-card.reject-card {{ }}
  .action-card.reject-card.selected {{ border-color: #c0392b; background: #fdf5f5; }}
  .action-card input[type="radio"] {{ accent-color: inherit; flex-shrink: 0; }}
  .action-card-text {{ font-size: 12px; font-weight: 600; line-height: 1.4; }}
  .action-card-sub {{ font-size: 11px; color: #888; font-weight: 400; }}

  /* ── Generate-more direction ── */
  .generate-more-panel {{
    display: none;
    background: #fdf5f5; border: 1px solid #f5c6cb;
    border-radius: 8px; padding: 14px 16px; margin-bottom: 16px;
  }}
  .generate-more-panel.visible {{ display: block; }}
  .generate-more-label {{
    font-size: 12px; font-weight: 700; color: #c0392b; margin-bottom: 6px; display: block;
  }}
  .generate-more-field {{
    width: 100%; min-height: 56px;
    border: 1px solid #f5c6cb; border-radius: 6px;
    padding: 8px 10px; font-size: 13px;
    resize: vertical; font-family: inherit;
    background: #fff;
  }}
  .generate-more-field:focus {{ outline: none; border-color: #c0392b; }}

  /* ── Approve confirmation ── */
  .approved-panel {{
    display: none;
    background: #f0faf4; border: 1px solid #a8d5b5;
    border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;
    font-size: 13px; color: #00703c; font-weight: 600;
  }}
  .approved-panel.visible {{ display: block; }}

  /* ── Zone feedback ── */
  .zones-panel {{ display: none; }}
  .zones-panel.visible {{ display: block; }}
  .zones-heading {{
    font-size: 11px; font-weight: 700; color: #1a1a2e;
    text-transform: uppercase; letter-spacing: 0.6px;
    margin-bottom: 12px; display: block;
  }}
  .zone-row {{
    display: grid;
    grid-template-columns: 140px 1fr;
    gap: 8px;
    margin-bottom: 10px;
    align-items: start;
  }}
  .zone-name {{
    font-size: 12px; font-weight: 600; color: #555;
    padding-top: 8px;
  }}
  .zone-feedback {{
    border: 1px solid #ddd; border-radius: 6px;
    padding: 7px 9px; font-size: 12px; color: #333;
    resize: vertical; min-height: 34px;
    font-family: inherit; transition: border-color .15s;
  }}
  .zone-feedback:focus {{ outline: none; border-color: #4f83b7; }}

  /* ── Bottom panel ── */
  .summary-panel {{
    position: sticky; bottom: 0;
    background: #fff;
    border-top: 2px solid #1a1a2e;
    padding: 12px 24px;
    box-shadow: 0 -2px 12px rgba(0,0,0,.1);
    display: flex; align-items: center; gap: 16px;
  }}
  .summary-status {{ flex: 1; font-size: 13px; color: #555; }}
  .summary-status strong {{ color: #1a1a2e; }}
  .save-btn {{
    background: #1a1a2e; color: #fff; border: none;
    padding: 9px 22px; border-radius: 6px;
    font-size: 13px; font-weight: 600; cursor: pointer;
    transition: background .15s; white-space: nowrap;
  }}
  .save-btn:hover {{ background: #2c2c54; }}
  .save-btn.saved {{ background: #00703c; }}
  .restore-hint {{
    font-size: 11px; color: #4f83b7; cursor: pointer;
    text-decoration: underline; white-space: nowrap;
  }}
</style>
</head>
<body>

<h1>{title}</h1>
<p class="subtitle">Pick one option per slide — or approve as-is, or request new options. Zone feedback and exact replacement text are optional. Saves to localStorage automatically.</p>

<!-- Deck-level notes -->
<div class="deck-notes-panel">
  <span class="deck-notes-label">Deck-level notes</span>
  <p class="deck-notes-sub">Feedback that applies across multiple slides — narrative arc, slide order, overall tone, consistency issues.</p>
  <textarea class="deck-notes-field" id="deck_notes"
    placeholder="e.g. Slides 3–5 need to tell a connected story — currently they feel like three separate memos. Or: the narrative flips from problem to solution too abruptly between slides 4 and 5."></textarea>
</div>

{slide_sections}

<div class="summary-panel">
  <div class="summary-status" id="summary-status">Make your selections above.</div>
  <span class="restore-hint" onclick="clearStorage()" id="clear-btn" style="display:none">Clear saved state</span>
  <button class="save-btn" onclick="saveSelections()">Save review-selections.md</button>
</div>

<script>
const SLIDES = {slides_json};
const ZONES  = {zones_json};
const STORAGE_KEY = "slide_review_{storage_key}";

// ── LocalStorage persistence ──────────────────────────────────────────────

function getState() {{
  const state = {{}};
  // Deck notes
  state.deck_notes = document.getElementById("deck_notes").value;
  // Per-slide
  state.slides = {{}};
  SLIDES.forEach(s => {{
    const checked = document.querySelector(`input[name="slide_${{s.num}}"]:checked`);
    state.slides[s.num] = {{
      pick: checked ? checked.value : null,
      direction: (document.getElementById(`direction_${{s.num}}`) || {{}}).value || "",
      zones: {{}}
    }};
    ZONES.forEach((_, i) => {{
      state.slides[s.num].zones[i] = {{
        feedback: (document.getElementById(`zf_${{s.num}}_${{i}}`) || {{}}).value || "",
      }};
    }});
  }});
  return state;
}}

function applyState(state) {{
  if (!state) return;
  if (state.deck_notes) document.getElementById("deck_notes").value = state.deck_notes;
  if (!state.slides) return;
  SLIDES.forEach(s => {{
    const sd = state.slides[s.num];
    if (!sd) return;
    if (sd.pick) selectOption(s.num, sd.pick, false);
    const dirEl = document.getElementById(`direction_${{s.num}}`);
    if (dirEl && sd.direction) dirEl.value = sd.direction;
    ZONES.forEach((_, i) => {{
      const z = sd.zones && sd.zones[i];
      if (!z) return;
      const fe = document.getElementById(`zf_${{s.num}}_${{i}}`);
      if (fe && z.feedback) fe.value = z.feedback;
    }});
  }});
}}

function saveToStorage() {{
  try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(getState())); }} catch(e) {{}}
}}

function loadFromStorage() {{
  try {{
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {{
      applyState(JSON.parse(raw));
      document.getElementById("clear-btn").style.display = "inline";
    }}
  }} catch(e) {{}}
}}

function clearStorage() {{
  if (!confirm("Clear all saved selections and start over?")) return;
  localStorage.removeItem(STORAGE_KEY);
  location.reload();
}}

// ── UI interactions ───────────────────────────────────────────────────────

function selectOption(slideNum, optId, persist=true) {{
  // Update radio
  const radio = document.querySelector(`input[name="slide_${{slideNum}}"][value="${{optId}}"]`);
  if (radio) radio.checked = true;

  // Update image option cards
  document.querySelectorAll(`.option-card[data-slide="${{slideNum}}"]`).forEach(card => {{
    card.classList.toggle("selected", card.dataset.opt === optId);
  }});

  // Update action cards
  document.querySelectorAll(`.action-card[data-slide="${{slideNum}}"]`).forEach(card => {{
    card.classList.toggle("selected", card.dataset.opt === optId);
  }});

  // Show/hide panels
  const section     = document.getElementById(`section_${{slideNum}}`);
  const zonesPanel  = document.getElementById(`zones_${{slideNum}}`);
  const approvePanel = document.getElementById(`approved_${{slideNum}}`);
  const rejectPanel  = document.getElementById(`reject_${{slideNum}}`);

  section.classList.remove("approved", "rejected", "picked");
  zonesPanel.classList.remove("visible");
  approvePanel.classList.remove("visible");
  rejectPanel.classList.remove("visible");

  const badge = section.querySelector(".slide-status-badge");

  if (optId === "APPROVE") {{
    section.classList.add("approved");
    approvePanel.classList.add("visible");
    badge.textContent = "✓ Approved";
  }} else if (optId === "MORE") {{
    section.classList.add("rejected");
    rejectPanel.classList.add("visible");
    badge.textContent = "↺ Generate more";
  }} else {{
    section.classList.add("picked");
    zonesPanel.classList.add("visible");
    badge.textContent = "Option " + optId;
  }}

  updateStatus();
  if (persist) saveToStorage();
}}

function updateStatus() {{
  const total  = SLIDES.length;
  const done   = SLIDES.filter(s =>
    document.querySelector(`input[name="slide_${{s.num}}"]:checked`)
  ).length;
  document.getElementById("summary-status").innerHTML =
    `<strong>${{done}} / ${{total}}</strong> slides reviewed`;
  document.getElementById("clear-btn").style.display = "inline";
}}

// ── Build markdown output ─────────────────────────────────────────────────

function buildMarkdown() {{
  const lines = ["# Review Selections", ""];

  const deckNotes = document.getElementById("deck_notes").value.trim();
  if (deckNotes) {{
    lines.push("## Deck-level notes");
    lines.push(deckNotes);
    lines.push("");
    lines.push("---");
    lines.push("");
  }}

  SLIDES.forEach(s => {{
    lines.push(`## ${{s.label}}`);
    const radio = document.querySelector(`input[name="slide_${{s.num}}"]:checked`);

    if (!radio) {{
      lines.push("**Status:** (not reviewed)");
    }} else if (radio.value === "APPROVE") {{
      lines.push("**Status:** Approved as-is — no changes needed");
    }} else if (radio.value === "MORE") {{
      lines.push("**Status:** None of these — generate new options");
      const dir = (document.getElementById(`direction_${{s.num}}`) || {{}}).value || "";
      if (dir.trim()) lines.push(`**Direction:** ${{dir.trim()}}`);
    }} else {{
      lines.push(`**Chosen option:** ${{radio.value}}`);

      const zoneLines = [];
      ZONES.forEach((zone, i) => {{
        const fb = (document.getElementById(`zf_${{s.num}}_${{i}}`) || {{}}).value.trim();
        if (fb) zoneLines.push(`- **${{zone}}:** ${{fb}}`);
      }});

      if (zoneLines.length > 0) {{
        lines.push("");
        lines.push("**Zone feedback:**");
        zoneLines.forEach(l => lines.push(l));
      }}
    }}

    lines.push("");
  }});

  return lines.join("\\n");
}}

function saveSelections() {{
  const text = buildMarkdown();
  const blob = new Blob([text], {{ type: "text/markdown" }});
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href = url; a.download = "review-selections.md";
  document.body.appendChild(a); a.click();
  document.body.removeChild(a); URL.revokeObjectURL(url);

  const btn = document.querySelector(".save-btn");
  btn.textContent = "Saved!"; btn.classList.add("saved");
  setTimeout(() => {{ btn.textContent = "Save review-selections.md"; btn.classList.remove("saved"); }}, 2000);
}}

// ── Wire up auto-save on every input ─────────────────────────────────────
document.addEventListener("input", () => {{ saveToStorage(); updateStatus(); }});

// ── Load saved state on open ──────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {{
  loadFromStorage();
  updateStatus();
}});
</script>
</body>
</html>
"""


SLIDE_SECTION_TEMPLATE = """\
<div class="slide-section" id="section_{slide_num}">
  <div class="slide-header">
    <span class="slide-num">{slide_num_padded}</span>
    {slide_label}
    <span class="slide-status-badge"></span>
  </div>

  <!-- Options + action cards -->
  <div class="options-row">
    {option_cards}
    <div class="action-cards">
      <div class="action-card approve-card" data-slide="{slide_num}" data-opt="APPROVE"
           onclick="selectOption({slide_num}, 'APPROVE')">
        <input type="radio" name="slide_{slide_num}" value="APPROVE">
        <div class="action-card-text">
          ✓ Approve as-is
          <div class="action-card-sub">No changes needed</div>
        </div>
      </div>
      <div class="action-card reject-card" data-slide="{slide_num}" data-opt="MORE"
           onclick="selectOption({slide_num}, 'MORE')">
        <input type="radio" name="slide_{slide_num}" value="MORE">
        <div class="action-card-text">
          ↺ None of these
          <div class="action-card-sub">Generate new options</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Approved confirmation -->
  <div class="approved-panel" id="approved_{slide_num}">
    ✓ Slide approved — Claude will keep this slide unchanged.
  </div>

  <!-- Generate more direction -->
  <div class="generate-more-panel" id="reject_{slide_num}">
    <label class="generate-more-label" for="direction_{slide_num}">Direction for new options (required)</label>
    <textarea class="generate-more-field" id="direction_{slide_num}"
      placeholder="e.g. Try a single-column layout with a hero stat on the left and bullets on the right. Or: go darker — navy background, white text. Or: this should be a process chevron not a comparison table."
      oninput="saveToStorage()"></textarea>
  </div>

  <!-- Zone feedback (visible when an option is picked) -->
  <div class="zones-panel" id="zones_{slide_num}">
    <span class="zones-heading">Zone feedback — leave blank if no changes needed</span>
    {zone_rows}
  </div>
</div>
"""

OPTION_CARD_TEMPLATE = """\
<div class="option-card" data-slide="{slide_num}" data-opt="{opt_id}"
     onclick="selectOption({slide_num}, '{opt_id}')">
  <div class="option-header">
    <input class="option-radio" type="radio" name="slide_{slide_num}" value="{opt_id}">
    <span class="option-label">Option {opt_id}</span>
  </div>
  <img class="option-img" src="{img_src}" alt="Option {opt_id}">
  <span class="selected-badge">&#10003; Selected</span>
</div>
"""

ZONE_ROW_TEMPLATE = """\
    <div class="zone-row">
      <span class="zone-name">{zone_name}</span>
      <textarea class="zone-feedback" id="zf_{slide_num}_{zone_idx}"
        placeholder="{feedback_placeholder}"></textarea>
    </div>"""


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def generate_html(slides: list, title: str, embed_images: bool = True) -> str:
    import hashlib
    storage_key = hashlib.md5(title.encode()).hexdigest()[:8]

    slide_sections_html = []
    slides_json_parts = []

    for slide in slides:
        option_cards_html = []
        for opt in slide["options"]:
            img_src = png_to_data_uri(opt["path"]) if embed_images else opt["path"].name
            card = OPTION_CARD_TEMPLATE.format(
                slide_num=slide["num"],
                opt_id=opt["id"],
                img_src=img_src,
            )
            option_cards_html.append(card)

        zone_rows_html = []
        for i, zone_name in enumerate(ZONE_NAMES):
            row = ZONE_ROW_TEMPLATE.format(
                zone_name=zone_name,
                slide_num=slide["num"],
                zone_idx=i,
                feedback_placeholder=ZONE_PLACEHOLDERS[i],
            )
            zone_rows_html.append(row)

        section = SLIDE_SECTION_TEMPLATE.format(
            slide_num=slide["num"],
            slide_num_padded=f"{slide['num']:02d}",
            slide_label=slide["label"],
            option_cards="\n    ".join(option_cards_html),
            zone_rows="\n".join(zone_rows_html),
        )
        slide_sections_html.append(section)
        slides_json_parts.append(f'{{"num": {slide["num"]}, "label": "{slide["label"]}"}}'  )

    import json
    slides_json = "[" + ", ".join(slides_json_parts) + "]"
    zones_json  = json.dumps(ZONE_NAMES)

    return HTML_TEMPLATE.format(
        title=title,
        slide_sections="\n".join(slide_sections_html),
        slides_json=slides_json,
        zones_json=zones_json,
        storage_key=storage_key,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate slide review UI from PNG options")
    parser.add_argument("folder", help="Session folder containing slide_NN_[ABC].png files")
    parser.add_argument("--output", default=None)
    parser.add_argument("--title", default="Slide Review")
    parser.add_argument("--no-embed", action="store_true")
    args = parser.parse_args()

    folder = Path(args.folder).resolve()
    if not folder.is_dir():
        print(f"ERROR: {folder} is not a directory.")
        sys.exit(1)

    slides = collect_slide_options(folder)
    if not slides:
        print(f"ERROR: No slide_NN_[ABC].png files found in {folder}")
        sys.exit(1)

    print(f"Found {len(slides)} slide(s):")
    for s in slides:
        opts = ", ".join(o["id"] for o in s["options"])
        print(f"  Slide {s['num']:02d}: options [{opts}]")

    html = generate_html(slides, title=args.title, embed_images=not args.no_embed)

    out_path = Path(args.output) if args.output else folder / "review.html"
    out_path.write_text(html, encoding="utf-8")

    print(f"\nReview UI saved: {out_path}")
    print(f"Open in browser — selections auto-save to localStorage.")
    print(f"Click 'Save review-selections.md' when done.")


if __name__ == "__main__":
    main()
