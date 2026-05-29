---
client_template: C:/Users/m.a.peralta/OneDrive - Accenture/Library/FedEx/OTC/OTC Opportunity.pptx
deck_type: v0.3 smoke (body-canonical inheritance + dark overlay)
default_layout: Use as default slide template
---

## Deck-level design notes

Smoke build that exercises v0.3 body-canonical layout inheritance + the dark
body overlay path. Slide 1 uses the OTC body layout untouched; slide 2 uses
a body layout whose chrome.yml carries body_overlay_hex (light layout + dark
overlay = light_on_dark text). Slide 3 also uses a body-canonical layout to
keep this smoke focused on the body-inheritance path; the bespoke cover/
divider path is covered by the synthetic fixture in tests/.

## Slide 1 - OTC body light - inherited title placeholder
**Layout:** Use as default slide template
**Archetype:** Synthesis / Findings
**Governing thought:** v0.3 keeps the OTC body layout chrome.
**So-what:** Title lands in the inherited title placeholder; layout chrome inherits.
**Evidence:** Rendered slide carries Rectangle 4/5/6 (OTC chrome) plus a populated title placeholder.

## Slide 2 - OTC body dark via overlay
**Layout:** Layout 01
**Archetype:** Synthesis / Findings
**Governing thought:** body_overlay_hex paints a dark rectangle over the layout body zone.
**So-what:** light_on_dark text on dark background; OTC chrome still visible behind overlay.
**Evidence:** Slide has a body-overlay rectangle as the first slide-level shape.

## Slide 3 - OTC body light - second slide
**Layout:** Use as default slide template_subtitle
**Archetype:** Synthesis / Findings
**Governing thought:** Second body slide to verify consistency.
**So-what:** Same inherited chrome path as slide 1; no regression across slides.
**Evidence:** N/A.
