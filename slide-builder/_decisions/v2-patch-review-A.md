# v2 Step-3 Patch Review (Reviewer A)

Target file: C:\Users\m.a.peralta\.claude\skills\slide-builder-simple\scripts\build_deck.py
Canonical writer: C:\Users\m.a.peralta\.claude\skills\slide-builder\twins\client_theme.py

## Verdict

APPLY AS-IS. The patch faithfully implements the committee spec: brand sidecar is read directly, slot-position guessing is gone (only retirement-callouts remain in comments), font composition order is body then heading then fallback, and the (client_slug, brand) signature matches its single call site in main(). There is one minor correctness nit worth flagging (A4 -- silent FedEx-shaped fallback in _hex) and one dead comment block (A2), but neither warrants blocking; both can be cleaned up in a follow-up patch.

## Per-question answers

### A1. Brand-field reads -- correct?

Yes. _compute_theme_variables() reads each canonical brand-sidecar field:

- primary_hex   -- line 485 (_hex("primary_hex", "#4D148C"))
- accent_hex    -- line 486 (_hex("accent_hex",  "#FF6600"))
- font_heading  -- line 488
- font_body     -- line 489

One spec gap to call out honestly: the committee listed brand.cover_bg_hex as a field the patch should read, but _compute_theme_variables does not consume it. That is defensible -- Mermaid's themeVariables has no slot that corresponds to "cover background"; that hex is consumed by v1's cover-page composer, not the diagram theme. cover_bg_hex is still loaded by load_brand_sidecar (sits in the brand dict at v1 lines 203-205) and available to downstream consumers; v2's Mermaid theme just has no use for it. Correct interpretation, not an omission.

### A2. Slot-position remnants -- any?

No live references. A targeted grep for THEME_MAPPING|find_template_json|_lookup|all_colors|("colors", "dk2") against build_deck.py returns only two hits, both in comments/docstrings:

- Line 476 -- inside _compute_theme_variables docstring, explicitly says: NO walking template.json["extracted"]["all_colors"]. Intentional reminder; keep.
- Line 584 -- section-header comment above validate_theme mentions "re-validate the THEME_MAPPING table in reference/fallback.md when v1 ships its load_client_theme fix." This is dead history: THEME_MAPPING no longer exists, brand.yml is now ground truth, and there is no load_client_theme bug to wait for. Recommend deleting roughly lines 582-588 in a cleanup pass -- does not block.

No function body reads ("extracted", "all_colors", "dk2") or any other slot tuple. Salvage path is fully closed.

### A3. Font-stack composition -- correct?

Yes. Lines 488-496:

    font_heading = (brand.get("font_heading", "") or "").strip()
    font_body    = (brand.get("font_body", "") or "").strip()
    family_parts: list[str] = []
    if font_body:
        family_parts.append(f"\"{font_body}\"")
    if font_heading and font_heading != font_body:
        family_parts.append(f"\"{font_heading}\"")
    family_parts.extend(["Helvetica", "Arial", "sans-serif"])
    font_family = ", ".join(family_parts)

Order is body, then heading, then Helvetica/Arial/sans-serif. Body-first is correct for Mermaid since the dominant text use is body weight (node labels); headings are the exception (cluster titles). The de-dup guard font_heading != font_body prevents redundant entries when v1's register_template.py writes the same family to both slots (common for single-typeface brands like FedEx Sans). Quoting families with "..." is necessary for multi-word names (e.g. "Helvetica Neue", "FedEx Sans").

### A4. Hex validation -- sufficient?

Mostly yes, with one caveat. The inline _hex helper at lines 479-483 normalizes via .strip().upper() and validates with re.fullmatch(r"[0-9A-F]{6}", v). Malformed input (e.g., "#FF6600" with a leading #, "FF66", "red", or None) falls back to the hardcoded defaults (#4D148C / #FF6600).

The caveat: the fallback is FedEx-shaped, and silent at this layer. If brand.primary_hex is malformed on a non-FedEx template, the user gets FedEx purple without any console warning at theme-write time. This IS partially caught downstream -- validate_theme() (line 637) sanity-checks the resolved theme; the KNOWN_CLIENT_HUE_RANGES entry for fedex (line 596) catches mismatches when the path contains a recognized client name. But for unregistered/new clients, the structural checks (saturation, luminance, primary != accent) wont catch FedEx-fallback contamination since FedEx purple is chromatic and clearly distinct from FedEx orange.

Note: load_brand_sidecar itself runs _normalize_hex (v1 lines 201-203) which strips # and uppercases -- so by the time _compute_theme_variables runs, hexes are already clean. The inline _hex belt-and-braces is correct defensive coding; the silent-fallback contamination is the residual risk. Minor cleanup: consider appending a slots_using_fallback entry from _hex parallel to the existing entries at lines 544-549. Not blocking -- validate_theme covers the practical FedEx-named case.

### A5. load_brand_sidecar vs load_client_theme -- defensible?

Yes, and arguably better than the alternative for v2's Mermaid use case. Reading v1's code:

- load_brand_sidecar (v1 line 145) returns a plain dict with the brand.yml fields plus a SHA validation against theme.json. Cheap. No Presentation() open.
- load_client_theme (v1 line 398) calls load_brand_sidecar AND opens the .pptx with python-pptx to extract raw theme1.xml (dk1/lt1/accent1-6), builds a ClientTheme dataclass, and provides color_map() for shape-XML remapping.

For v2's Mermaid theme generation, none of the raw theme1.xml palette or the color_map() machinery is needed -- Mermaid only consumes brand primary/accent/fonts. Calling load_client_theme would force a python-pptx open per build_deck.py invocation for zero benefit, and would couple v2 to a chunkier API surface.

Semantic divergence check: the brand fields v2 reads (primary_hex, accent_hex, font_heading, font_body) come from the same source -- brand.yml -- in both functions. One small divergence to acknowledge: load_client_theme falls back to theme1.xml's major_font/minor_font at v1 lines 425-426 when brand.yml's fonts are empty. v2's _compute_theme_variables does NOT -- it jumps straight to Helvetica, Arial, sans-serif. This is a deliberate simplification consistent with avoiding the .pptx open; Mermaid renders consistently with Helvetica when fonts arent specified. Acceptable divergence; does not affect any case where register_template.py populated font_body/font_heading correctly.

### A6. Call-site signature -- correct?

Yes. main() at lines 1055-1057:

    client_slug = detect_client_slug(args.template, args.client_name)
    brand = load_brand_sidecar(args.template)
    theme_path, fallbacks_used = generate_mermaid_theme(client_slug, brand)

Matches generate_mermaid_theme(client_slug: str, brand: dict) at line 529 exactly. Return-type destructuring (theme_path, fallbacks_used) matches the function's tuple[Path, list[str]] annotation. Single call site, no orphans.

Additionally, stage1_sanity_check at line 956 calls load_brand_sidecar(template_path) proactively for the existence check, so by the time main() reaches line 1056 we already know the sidecar loads cleanly -- the second call is a re-load to get the dict, not a re-validation. Cheap (YAML+JSON read, no .pptx open). Slightly redundant but defensible since stage-1 returns nothing and main() needs the dict.

### A7. Other patch correctness issues across Diffs 1-8?

1. Stale comment block at lines 582-588 (already flagged in A2). References retired THEME_MAPPING and "v1's load_client_theme fix." Both obsolete since brand.yml became ground truth. Remove in cleanup.
2. validate_theme signature carries template_json_path: Path | None (line 640) marked "kept for signature compat; no longer used". Acceptable for one cycle; the single call at line 1071 passes None, so it's actively unused. Drop in next patch wave.
3. detect_client_slug skip list (line 450) excludes "templates", "claude projects", "documents" but not "_templates". The name.startswith("_") check at line 450 catches "_templates" correctly, so the FedEx example path .../FedEx/_templates/Template2.pptx resolves to fedex as documented. Confirmed by re-reading the loop.
4. Universal neutrals are hardcoded (lines 509-522). By-design and called out in the docstring (line 514, "# Universal neutrals (no slot-position guessing)"). Reasonable for v2's Mermaid path since Mermaid never renders cover chrome or master backgrounds -- it's diagram-only output.
5. _comment_brand_source metadata (line 554) writes "brand.yml via twins.client_theme.load_brand_sidecar (v1 canonical)" into the generated theme JSON. Good -- debugging breadcrumb that survives in the artifact.

None of these block the patch.

## Biggest concern

The silent FedEx-shaped fallback in _hex (A4) combined with the dead comment block at lines 582-588 (A2) creates a mild reviewer-confusion risk for the next person who lands in this file. A future agent reading the comment block might think the THEME_MAPPING bug is still active and look for a slot walker, then waste cycles finding nothing. Cleanup pass should:

1. Delete lines ~570-589 (the entire "v2-side guard against the shared v1 client_theme loader bug" preamble) -- replace with a short note that brand.yml is ground truth and validate_theme does structural checks only.
2. Append fallback entries from _hex to slots_using_fallback so malformed-hex cases surface in dispatch_plan.md instead of silently going FedEx-purple.
3. Drop the unused template_json_path parameter from validate_theme.

None are correctness bugs in this patch; they are debt for a follow-up. The patch as written ships the spec correctly.
