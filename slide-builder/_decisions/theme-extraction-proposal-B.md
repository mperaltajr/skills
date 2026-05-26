# Theme extraction — Proposal B (empirical / image-analysis)

**Reviewer:** B (blind to A and C)
**Angle:** don't trust template metadata; render a representative slide to PNG and read the actual pixels.
**Verdict up front:** this approach is a viable *secondary* signal (a sanity-check oracle) but a poor *primary* extraction mechanism. The failure modes around multi-master templates, gradient covers, and dk2/lt2-both-saturated palettes are severe enough that pixel-extraction shouldn't be the canonical loader. Section "Trade-offs" recommends pinning it as a **verification layer** atop a metadata-driven loader rather than a replacement.

---

## Proposal — image-analysis extraction

### Mechanism

1. **Render a small, deterministic set of slides** from the template using LibreOffice headless (`soffice --headless --convert-to png`). Not "the master" — the master itself often has no rendered fill, since masters in PPTX are *templates of templates*, not finished slides. Render instead:
   - Layout 0 of the first slide master (typically "Title Slide")
   - Layout 1 of the first slide master (typically the primary content layout)
   - The first 3 slides of the template's example deck, if it ships one (most client templates do — FedEx ships 48 sample slides, ACN ships 93)
2. **Cluster pixels** with k-means (k=7) on each PNG. Discard clusters with (a) area < 1% of canvas (anti-aliasing noise), (b) saturation < 0.15 AND value > 0.92 (white-ish backgrounds), (c) saturation < 0.15 AND value < 0.18 (text-black).
3. **Score remaining clusters by zone weight, not raw frequency.** Define five rectangles on each rendered PNG: title-band (top 0–18%), logo-corner (top-left 0–10% × 0–8%), accent-stripe (top-right 0–8% × 0–100%), body (18–82% vertical), footer (82–100%). Each cluster gets a weighted score = sum over zones of (zone_weight × pixels_in_zone). Logo-corner and accent-stripe carry the heaviest weights (×8 and ×5 respectively); body is ×0.5; title-band is ×3.
4. **The cluster with the highest weighted score is `brand_primary`. The next-highest cluster whose HSV-hue differs from primary by ≥ 30° (or, if no such cluster exists, the next-highest unconditional) is `brand_accent`.**
5. **Cross-reference all rendered slides.** A cluster that shows up in the top-3 weighted positions on at least 2 of N rendered slides is trusted; clusters appearing in only one slide are demoted. This rejects per-slide hero-image pollution.
6. **Fonts: do NOT extract from pixels.** OCR + font identification is unreliable across rendered weight variants. Fall through to the existing theme1.xml `<a:majorFont>` / `<a:minorFont>` parse. Fonts are the *one* attribute XML reliably exposes.

### Which slide gets rendered

Rendering the *master* directly is a trap. PPTX masters frequently contain only placeholder boxes with theme-color *references* (`<a:schemeClr val="accent1"/>`), and LibreOffice renders an empty placeholder as a faint outline at best. The template's example slides are where the brand actually lives in pixels — they hold the cover treatments, accent bars, and logos the designer placed *using* the theme.

Concretely:
- **Primary signal:** first 3 example slides of the template's sample deck.
- **Fallback signal:** Layout 0 + Layout 1 of slide master 0 (rendered through a synthetic single-slide deck constructed by python-pptx from the layout — adds 200ms but works when the template has no example slides).
- **Never use:** the raw `<sldMaster>` XML rendered standalone. It's not a slide; it's a definition.

### Disambiguating primary vs accent

Position-based, not frequency-based. The zone weights above (logo-corner ×8, accent-stripe ×5, title-band ×3) encode the rule: **the color that appears in the brand-mark position is primary; the color that appears in the accent-stripe position is accent.** Frequency alone is wrong — a full-bleed cover slide has the brand color covering 90% of the canvas, but the *logo* is in a 5% corner, and that's what defines the palette.

When position weight is ambiguous (both candidate colors appear in similar zones — common with two-color gradient covers, see Failure modes), fall through to:
1. **HSV value preference for primary** — darker of the two is usually primary (dk2 by convention).
2. **If still ambiguous, prompt the operator.** A 5-second human confirmation is cheap; a wrong-color deck is expensive.

---

## Canonical theme file schema

```json
{
  "schema_version": 1,
  "template_path": "C:/.../FedEx/_templates/Moving Forward PPT Template.pptx",
  "template_sha256": "abc123...",
  "extracted_at": "2026-05-25T14:00:00Z",
  "extraction_method": "image-analysis-v1",
  "renders": [
    {"source": "slide_1", "png": ".cache/render_001.png", "dim": [1280, 720]},
    {"source": "slide_2", "png": ".cache/render_002.png", "dim": [1280, 720]}
  ],
  "colors": {
    "brand_primary":   {"hex": "4D148C", "confidence": 0.94, "source": "logo-corner cluster, 3/3 slides"},
    "brand_accent":    {"hex": "FF6600", "confidence": 0.91, "source": "accent-stripe cluster, 2/3 slides"},
    "brand_primary_mid": {"hex": "7D22C3", "confidence": 0.62, "source": "derived (mix 30% to white)"},
    "brand_accent_soft": {"hex": "FFCCAA", "confidence": 0.55, "source": "derived"},
    "text_dark":  {"hex": "1A1A1A", "confidence": 0.99, "source": "body-zone text cluster"},
    "neutral_card_bg": {"hex": "F2F2F2", "confidence": 0.71, "source": "subgraph zone cluster"}
  },
  "fonts": {
    "major": {"name": "FedEx Sans", "source": "theme1.xml a:majorFont"},
    "minor": {"name": "FedEx Sans", "source": "theme1.xml a:minorFont"}
  },
  "warnings": [
    "slide_1 had gradient cover — primary cluster weighted accordingly"
  ],
  "needs_operator_confirmation": false
}
```

Stored at `<project_root>/_templates/<template_stem>.theme.json`. Every build agent reads this file; no agent re-reads the PPTX or recomputes colors. `template_sha256` lets `build_deck.py` detect template-changed-since-extraction and trigger a re-render.

---

## Implementation sketch

```python
# scripts/extract_theme_image.py
import hashlib, json, subprocess, sys
from collections import Counter
from pathlib import Path
from PIL import Image
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from pptx import Presentation

SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"

def render_slide_to_png(template_pptx: Path, slide_idx: int, out_png: Path) -> None:
    # Build a single-slide subset, render via soffice headless
    sub = template_pptx.with_suffix(f".slide{slide_idx}.pptx")
    _extract_single_slide(template_pptx, slide_idx, sub)
    subprocess.run(
        [SOFFICE, "--headless", "--convert-to", "png",
         "--outdir", str(out_png.parent), str(sub)],
        check=True, timeout=30,
    )

def cluster_colors(png_path: Path, k: int = 7):
    img = Image.open(png_path).convert("RGB")
    arr = np.array(img).reshape(-1, 3)
    sample = arr[np.random.choice(len(arr), 50_000, replace=False)]
    km = MiniBatchKMeans(n_clusters=k, batch_size=1024, n_init=3).fit(sample)
    labels = km.predict(arr)
    counts = Counter(labels.tolist())
    clusters = []
    for cid, n_pixels in counts.most_common():
        r, g, b = km.cluster_centers_[cid].astype(int)
        clusters.append({
            "hex": f"{r:02X}{g:02X}{b:02X}",
            "pixels": n_pixels,
            "cluster_id": cid,
        })
    return clusters, labels.reshape(img.size[1], img.size[0]), img.size

def filter_chrome(clusters):
    out = []
    for c in clusters:
        h, s, v = _hex_to_hsv(c["hex"])
        if v > 0.92 and s < 0.15: continue
        if v < 0.18 and s < 0.15: continue
        if s < 0.10:               continue
        out.append(c)
    return out

ZONE_WEIGHTS = {
    "logo_corner":   (0.00, 0.08, 0.00, 0.10, 8.0),
    "accent_stripe": (0.00, 1.00, 0.92, 1.00, 5.0),
    "title_band":    (0.00, 0.18, 0.00, 1.00, 3.0),
    "body":          (0.18, 0.82, 0.00, 1.00, 0.5),
    "footer":        (0.82, 1.00, 0.00, 1.00, 1.0),
}

def score_by_zone(labels_2d, clusters):
    H, W = labels_2d.shape
    for c in clusters:
        cid = c["cluster_id"]
        score = 0.0
        for yl, yh, xl, xh, w in ZONE_WEIGHTS.values():
            patch = labels_2d[int(yl*H):int(yh*H), int(xl*W):int(xh*W)]
            score += w * (patch == cid).sum()
        c["zone_score"] = score
    return clusters

def pick_brand_colors(all_clusters_per_slide):
    appearances, scores = Counter(), {}
    for slide_clusters in all_clusters_per_slide:
        top3 = sorted(slide_clusters, key=lambda c: -c["zone_score"])[:3]
        for c in top3:
            appearances[c["hex"]] += 1
            scores.setdefault(c["hex"], []).append(c["zone_score"])
    trusted = [h for h, n in appearances.items()
               if n >= 2 or len(all_clusters_per_slide) == 1]
    trusted.sort(key=lambda h: -sum(scores[h]))
    if not trusted:
        return None, None, "no-trusted-cluster"
    primary = trusted[0]
    accent = next((h for h in trusted[1:]
                   if _hue_distance(h, primary) >= 30), None)
    return primary, accent, "ok"
```

**Deps:** Pillow (already available — python-pptx depends on it), NumPy, scikit-learn for `MiniBatchKMeans`. Hand-rolled k-means is feasible (~50 lines) but `MiniBatchKMeans` on 50k sampled pixels with k=7 runs in ~200ms; not worth re-implementing. LibreOffice is already installed at `C:\Program Files\LibreOffice\program\soffice.exe` per env check, and Slide Lab uses it elsewhere (slide-qc uses it for screenshots), so this introduces no new external dependency.

---

## Failure modes

These are not edge cases — they are present in the two templates on disk *right now*.

**1. Multi-master templates blow up the "which slide" assumption.** FedEx ships **12 slide masters with 188 layouts total**; ACN ships 1 master with 57 layouts. Rendering "the master" is undefined when there are 12. Picking master 0's first layout is a guess — the actual cover used by the example deck might live in master 4. Mitigation: render the example deck's first 3 slides instead of the masters. But if the template ships no example slides, this signal is gone and we are stuck rendering a near-empty layout placeholder.

**2. ACN-style palettes where dk2 AND lt2 are both saturated.** The ACN template has `dk2=A100FF` (electric purple) and `lt2=460073` (deep purple) — both saturated, hue-distance < 30°, both legitimate brand colors. Cross-slide voting returns both as top clusters; the hue-distance rule fails because they are both purple; the HSV-value heuristic (darker = primary) picks lt2 as primary, *which contradicts the canonical slot mapping where dk2 is primary*. Pixel extraction here disagrees with the template's own declared intent. Either result is defensible, but they do not agree, and the user will see a mismatch between the template they opened in PowerPoint and the deck Slide Lab built.

**3. Gradient covers (ACN cover layout is literally named "Cover: gradient").** A gradient from `A100FF` to `460073` produces 50+ intermediate colors. k-means with k=7 collapses these to ~3 quantized purples that do not match either declared theme slot exactly. The output is a *close-but-wrong* hex like `7300A0` — not in the palette, not what python-pptx will write into shape fills downstream. Color remapping (the `color_map` in `client_theme.py`) is keyed on *exact hex strings*; an off-by-2 hex breaks every map lookup silently.

**4. Hero images on the cover.** Any client whose template ships with a photographic cover slide pollutes the cluster set with skin tones, sky blues, foliage greens. The cross-slide voting rule (cluster must appear in 2+ slides) mitigates this *only if there are 2+ non-hero slides among the 3 we render*. If all 3 happen to be hero-image covers (some marketing-led templates ship 3 cover variants up front), pixel extraction returns hero-image colors, not brand colors.

**5. Multi-color logos.** FedEx itself has a purple-and-orange logo. If both colors appear in the logo-corner zone with similar zone scores, the picker arbitrarily picks one as primary and the other as accent. That happens to be *correct* for FedEx, but only because the FedEx logo happens to express the brand palette. A two-color logo where neither color matches the deck actual primary (rare but real — some clients use a grey wordmark logo on top of vivid accent fills) would produce wrong primary.

**6. Accent that matches background.** If a template uses a near-white accent (e.g., FedEx `accent5=E3E3E3` / `accent6=F2F2F2` neutral greys), the saturation-filter drops them as chrome. Pixel extraction has no concept of "this near-white IS the accent slot." Theme1.xml does.

**7. LibreOffice render fidelity.** LibreOffice renders PPTX with substituted fonts when corporate fonts are not installed (FedEx Sans, Graphik). Font substitution does not change color extraction, but if the substituted font is bolder/thinner, antialiasing colors at type edges shift the cluster set marginally. Minor noise; mitigated by k-means quantization. More concerning: LibreOffice has known fidelity bugs with PPTX gradients and some shape-fill effects — what gets rendered may not match what PowerPoint shows.

---

## Trade-offs vs alternatives

| Axis | Image-analysis (this proposal) | XML-direct (likely Reviewer A or C) | Interactive setup |
|---|---|---|---|
| Slot-mapping bugs irrelevant | Yes | No — inherits whatever conventions the loader encodes | Yes (human picks) |
| Handles vivid dk2+lt2 ambiguity | **No** — pixel extraction cannot tell which purple is "primary" intent | Yes — the slot label IS the intent | Yes |
| Handles gradient covers | **Poor** — quantization drift | Yes — XML has exact hex | Yes |
| Setup cost per template | ~10s render + 1s cluster = **~11s** | ~50ms parse | ~30s human time |
| Per-build cost | Zero (cached) | Zero (cached) | Zero (cached) |
| New deps | Pillow, NumPy, sklearn, soffice | None beyond pptx + re | None |
| Robust to "template author put primary in accent1 not dk2" | Yes | Only if loader has saturation-aware fallback (v1 already has one in `_pick_brand_colors`) | Yes |
| Color hex matches what python-pptx writes downstream | **Sometimes off-by-quantization** | Always exact | Always exact |

**The trade-off table makes pixel extraction case weak as a primary mechanism.** Its single decisive advantage — being immune to slot-mapping bugs — is also achievable in XML-direct with a saturation-aware slot picker (v1 already has one). Its weaknesses (gradient drift, dk2/lt2-both-saturated, quantization off-by-hex) are inherent to the technique and not fixable.

**Where it does decisively win: as a verification layer.** Run image-analysis *and* XML-direct, then compare. If the two agree (hue distance < 15° between picked primaries), trust the XML hex. If they disagree, halt and prompt the operator. This catches:
- The v1 multi-client bug where the loader returns Accenture colors for a FedEx template (XML says purple but rendered slides are orange-and-purple → disagreement → halt).
- Mis-authored templates where the declared theme slots do not match what the designer actually used in the example slides.

That is the right home for this technique: an **oracle that catches the slot-mapping class of bugs**, not the canonical source of truth.

---

## Migration plan

**Recommended sequencing** (assuming Proposal A or C provides the canonical XML loader):

1. **Phase 0 (one-time per template, at registration):** Run `extract_theme_image.py` once when a template is added to `_templates/`. Write `<template_stem>.theme.json` next to the PPTX. The render+cluster pass costs ~11 seconds and never runs again unless the template SHA256 changes. This is **template-registration time**, not first-build time — putting it at first-build adds 11s to the first run of every project, which is user-visible latency for negligible benefit.
2. **Phase 1 (every build):** `build_deck.py` reads `<template_stem>.theme.json` and the v1 XML loader output, then runs a **disagreement check**. If hue distance between image-derived and XML-derived primary is ≥ 15°, halt with a new exit code 7 ("theme disagreement — operator must reconcile"). This replaces the current FedEx-only hue check in `validate_theme()` with a client-agnostic mechanism.
3. **Phase 2 (v1 cutover):** v1 `twins/client_theme.py::load_client_theme` adopts the same `<template_stem>.theme.json` file as a *sanity check*, not a replacement for its existing XML loader. v1 keeps slot-mapping; image-analysis catches the bugs.
4. **Phase 3 (deprecation, optional):** If after 3 months the disagreement check fires ≥ 5 times in real usage and the operator overrides correctly each time, leave both signals in place. If it never fires, drop the image-analysis layer — the XML loader is good enough on its own.

**Do not** make image-analysis the *primary* extraction. The gradient-drift and dk2/lt2-ambiguity failure modes mean it will be wrong on real templates (ACN today). XML metadata, for all its slot-mapping quirks, has the property that the hexes are *exact* and machine-readable. Pixel-extracted hexes are *approximations*.

**Specifically — does the render happen at registration or first build?** Registration. The PPTX in `_templates/` is treated as immutable once registered; re-extraction is gated on SHA256 change. This makes per-build latency zero and contains the one-time cost in the template-onboarding step. A new helper `scripts/register_template.py` does the extraction + writes the canonical theme.json; `build_deck.py` errors out with a clear "run register_template.py first" message if it cannot find the sidecar.
