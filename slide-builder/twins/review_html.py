"""
Per-deck options review HTML.

Port of `_pattern-library/REVIEW.html` structure — same dark UI, same card
layout, same decision-button pattern, same localStorage persistence, same
"Copy to Claude" output flow. Only the data model is adapted: instead of
one card per LIBRARY PATTERN with Approve/Tweak/Reject decisions, it's one
card per DECK SLIDE with three options (A/B/C) plus a fourth "None work —
show me more" path and a feedback textarea.

For each slide, the orchestrator emits:
- The slide's brief (governing thought + so-what + editorial emphasis)
- 3 candidate twin thumbnails (rendered with the user's actual content +
  client template's theme + fonts)

The user picks A/B/C or NONE on each slide, optionally leaves feedback in
the textarea, then clicks "Copy → paste to Claude". Claude reads the
picks + feedback and either composes the deck (if every slide has a pick)
or re-runs the selector on slides marked NONE with the feedback as input.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from html import escape

from twins.build_with_options import prepare_deck_specs
from twins.themed_thumbnails import ensure_themed_thumbnail
from twins.brief_qc import check_brief


def _png_uri(path: Optional[Path]) -> str:
    if path is None:
        return ""
    return "file:///" + str(Path(path)).replace("\\", "/")


def _render_brief_qc_banner(qc_report: Dict[str, Any]) -> str:
    """Render the brief-time QC report as a collapsible HTML banner.
    Blocking issues are open by default; warnings start collapsed so they
    don't crowd the page. Returns empty string when there are no findings.

    TODO: render-time QC — once slide-qc is wired in for per-option PNG
    inspection, attach per-option QC badges to each option card. For now
    only brief-time issues are surfaced.
    """
    blocking = qc_report.get("blocking") or []
    warnings = qc_report.get("warnings") or []
    if not blocking and not warnings:
        return ""

    def _lis(items):
        return "".join(f'<li>{escape(s)}</li>' for s in items)

    sections = []
    if blocking:
        # Open by default — these need user action.
        sections.append(
            f'<details class="qc-brief-section qc-brief-blocking" open>'
            f'<summary>'
            f'<span class="qc-brief-icon">!</span>BLOCKING · {len(blocking)} issue(s)'
            f'</summary>'
            f'<ul>{_lis(blocking)}</ul>'
            f'</details>'
        )
    if warnings:
        # Collapsed by default — informational, not action-required.
        sections.append(
            f'<details class="qc-brief-section qc-brief-warning">'
            f'<summary>'
            f'<span class="qc-brief-icon">~</span>WARNING · {len(warnings)} issue(s) — click to expand'
            f'</summary>'
            f'<ul>{_lis(warnings)}</ul>'
            f'</details>'
        )
    return (
        '<div class="qc-brief-banner">'
        '<div class="qc-brief-banner-title">Brief-time QC report</div>'
        + "".join(sections) +
        '</div>'
    )


def narrative_slide_to_overrides(narrative_slide: Dict[str, Any]) -> Dict[str, str]:
    """DEPRECATED — use twins.overrides_resolver.pattern_aware_overrides instead.

    Legacy fan-out broadcaster. Kept for callers that don't know which pattern
    they're targeting yet (e.g., the legacy single-call-per-slide path in
    write_review_html). When the picked pattern is known, prefer
    `pattern_aware_overrides(narrative_slide, pattern_entry)` — it produces
    a smaller, targeted overrides dict keyed by the shape IDs the pattern
    actually uses (no wasted broadcasts; no silent misses on patterns whose
    shape IDs aren't in this fan-out list).

    Map narrative-helper slide fields onto canonical shape IDs across ALL
    relevant pattern families. For each piece of content, emit overrides for
    every shape ID that any candidate pattern might use to render that
    content. The composer's find-or-skip drops unknown IDs silently, so
    multi-mapping is safe.
    """
    overrides: Dict[str, str] = {}
    content = narrative_slide.get("content") or {}
    gov = narrative_slide.get("governing_thought") or ""
    sw = narrative_slide.get("so_what")

    # Accept simpler narrative form: `content.title` / `content.subtitle` /
    # `content.tagline` / `content.presenter` directly (without nesting under
    # `cover`). Promote them to overrides for both cover and non-cover patterns.
    flat_title = content.get("title")
    flat_subtitle = content.get("subtitle")
    flat_tagline = content.get("tagline")
    flat_presenter = content.get("presenter") or content.get("presented_by")
    if flat_title:
        for k in (
            "cover-deck-title", "cover-title", "cover-wordmark", "title",
            "hero-statement", "headline", "key-question", "anchor-statement",
        ):
            overrides[k] = flat_title
    if flat_subtitle:
        for k in (
            "cover-subtitle", "subtitle",
            "hero-context", "hero-attribution",
        ):
            overrides[k] = flat_subtitle
    if flat_tagline:
        for k in ("cover-tagline", "tagline", "subtitle", "cover-subtitle"):
            overrides.setdefault(k, flat_tagline)
    if flat_presenter:
        for k in ("cover-presenter", "cover-presented-name", "cover-meta-1", "cover-meta-N"):
            overrides[k] = flat_presenter

    cover = content.get("cover")
    if cover and isinstance(cover, dict):
        title = cover.get("title") or cover.get("deck_title")
        tagline = cover.get("tagline")
        presenter = cover.get("presented_by") or cover.get("presenter")
        client = cover.get("client") or cover.get("audience")
        date = cover.get("date")
        eyebrow = cover.get("eyebrow") or cover.get("pre_label")
        meta = cover.get("meta")
        if title:
            for k in ("cover-deck-title", "cover-title", "cover-wordmark", "title"):
                overrides[k] = title
        if tagline:
            for k in ("cover-tagline", "tagline"):
                overrides[k] = tagline
            overrides.setdefault("cover-subtitle", tagline)
        if presenter:
            for k in ("cover-presented-name", "cover-presenter", "cover-brand-name"):
                overrides[k] = presenter
            overrides.setdefault("cover-presented-label", "PRESENTED BY")
        if client:
            for k in ("cover-client-name", "cover-meta-1-value", "cover-meta-1"):
                overrides[k] = client
            overrides.setdefault("cover-meta-1-label", "PREPARED FOR")
        if date:
            for k in ("cover-date", "cover-meta-2-value", "cover-meta-2"):
                overrides[k] = date
            overrides.setdefault("cover-meta-2-label", "DATE")
        if eyebrow:
            for k in ("cover-eyebrow", "cover-pre-label", "eyebrow"):
                overrides[k] = eyebrow
        if meta:
            overrides["cover-meta"] = meta
    else:
        if gov and not gov.startswith("["):
            for k in ("title", "hero-statement", "headline", "key-question", "anchor-statement"):
                overrides[k] = gov
        if sw:
            for k in ("subtitle", "hero-context", "hero-attribution", "convergence"):
                overrides[k] = sw

    # Cards → broadcast to all common card/panel/column/option naming conventions
    cards_list = content.get("cards") or []
    columns_list = content.get("columns") or []
    # Treat `columns` as cards too for broadcasting (two-column patterns)
    combined_cards = cards_list if cards_list else columns_list
    for i, c in enumerate(combined_cards or [], 1):
        if not isinstance(c, dict): continue
        heading = c.get("heading") or c.get("title") or c.get("name")
        body = c.get("body") or c.get("description") or c.get("desc")
        label = c.get("label") or c.get("eyebrow")
        if heading:
            for key in (
                f"card-{i}-heading", f"panel-{i}-heading", f"column-{i}-heading",
                f"option-{i}-name", f"step-{i}-heading", f"step-{i}-name",
                f"col-{i}-heading", f"bucket-{i}-heading",
            ):
                overrides[key] = heading
            # 2-column patterns sometimes use before-panel / after-panel
            if len(combined_cards) == 2:
                key = "before-panel-heading" if i == 1 else "after-panel-heading"
                overrides[key] = heading
        if body:
            for key in (
                f"card-{i}-body", f"panel-{i}-body", f"column-{i}-body",
                f"step-{i}-body", f"col-{i}-body", f"bucket-{i}-body",
            ):
                overrides[key] = body
            if len(combined_cards) == 2:
                key = "before-panel-body" if i == 1 else "after-panel-body"
                overrides[key] = body
        if label:
            for key in (
                f"card-{i}-label", f"panel-{i}-label", f"column-{i}-label",
                f"step-{i}-label",
            ):
                overrides[key] = label

    # Pillars (Think/Argue/Build style)
    for i, p in enumerate(content.get("pillars") or [], 1):
        if isinstance(p, dict):
            name = p.get("name") or p.get("heading") or p.get("title")
            body = p.get("body") or p.get("description") or p.get("desc")
            if name:
                for key in (
                    f"pillar-{i}-name", f"pillar-{i}-heading",
                    f"column-{i}-heading", f"col-{i}-heading",
                    f"option-{i}-name", f"card-{i}-heading",
                ):
                    overrides[key] = name
            if body:
                for key in (
                    f"pillar-{i}-body", f"column-{i}-body",
                    f"col-{i}-body", f"card-{i}-body",
                ):
                    overrides[key] = body
    for i, m in enumerate(content.get("metrics") or [], 1):
        if isinstance(m, dict):
            if m.get("label"): overrides[f"metric-{i}-label"] = m["label"]
            if m.get("value"): overrides[f"metric-{i}-value"] = str(m["value"])
            if m.get("delta"): overrides[f"metric-{i}-delta"] = m["delta"]
    for i, s in enumerate(content.get("steps") or [], 1):
        if isinstance(s, dict):
            if s.get("name"): overrides[f"step-{i}-name"] = s["name"]
            if s.get("body"): overrides[f"step-{i}-body"] = s["body"]
    for i, a in enumerate(content.get("sub_asks") or [], 1):
        if isinstance(a, dict):
            if a.get("label"): overrides[f"sub-ask-{i}-label"] = a["label"]
            if a.get("body"): overrides[f"sub-ask-{i}-body"] = a["body"]
    if content.get("primary_ask"):
        overrides["primary-ask-text"] = content["primary_ask"]
    return overrides


def _derive_feedback_sections(narrative_slide: Dict[str, Any]) -> List[Dict[str, str]]:
    """For a slide, return the list of section-level feedback fields that
    match the brief's actual content.

    Each section becomes its own labeled textarea in the review UI — easier
    to leave targeted feedback (eg. on the title alone, or just the chart)
    than writing one long paragraph.
    """
    content = narrative_slide.get("content") or {}
    gov = narrative_slide.get("governing_thought") or ""
    sections: List[Dict[str, str]] = []

    is_cover = (narrative_slide.get("slide_num") == 1) or bool(content.get("cover"))
    _em_raw = narrative_slide.get("editorial_emphasis") or ""
    _em_text = " ".join(_em_raw) if isinstance(_em_raw, list) else str(_em_raw)
    is_screenshot = "screenshot" in _em_text.lower() or "screenshot" in gov.lower()

    if is_cover:
        sections.append({"id": "cover-title", "label": "Cover title", "placeholder": "Tweak to the deck title?"})
        sections.append({"id": "cover-tagline", "label": "Tagline", "placeholder": "Tweak to the tagline?"})
        sections.append({"id": "cover-presenter", "label": "Presenter / meta", "placeholder": "Presenter name, date, audience?"})
    else:
        if gov and not gov.startswith("["):
            sections.append({"id": "headline", "label": "Headline / title", "placeholder": "Anything to change about the action title?"})
        if narrative_slide.get("so_what"):
            sections.append({"id": "so-what", "label": "So-what / subtitle", "placeholder": "Change the so-what?"})

    if content.get("cards"):
        sections.append({"id": "cards", "label": f"Cards ({len(content['cards'])})", "placeholder": "Add/remove/reorder cards? Card text changes?"})
    if content.get("pillars"):
        sections.append({"id": "pillars", "label": f"Pillars ({len(content['pillars'])})", "placeholder": "Pillar names, body text, ordering?"})
    if content.get("metrics"):
        sections.append({"id": "metrics", "label": f"Metrics ({len(content['metrics'])})", "placeholder": "KPI labels, values, deltas?"})
    if content.get("steps"):
        sections.append({"id": "steps", "label": f"Steps ({len(content['steps'])})", "placeholder": "Step names, descriptions, count?"})
    if content.get("panels"):
        sections.append({"id": "panels", "label": "Panels", "placeholder": "Panel labels and content?"})
    if narrative_slide.get("chart_type") and narrative_slide["chart_type"] != "none":
        sections.append({"id": "chart", "label": f"Chart ({narrative_slide['chart_type']})", "placeholder": "Chart type, data, callouts?"})
    if is_screenshot:
        sections.append({"id": "screenshot", "label": "Screenshot", "placeholder": "What's in the screenshot? Caption?"})
    if content.get("sub_asks") or content.get("primary_ask"):
        sections.append({"id": "ask", "label": "Ask / CTA", "placeholder": "Primary ask, sub-asks, conditions?"})

    # Always-on sections
    sections.append({"id": "layout", "label": "Layout / structure", "placeholder": "Spacing, hierarchy, layout choice — what to nudge?"})
    sections.append({"id": "other", "label": "Other notes", "placeholder": "Anything else (eg. wrong pattern picked, content missing)"})
    return sections


def _render_dot_dash_section(brief_text: Optional[str]) -> tuple[str, str]:
    """If brief_text is provided, render a collapsible dot-dash section for
    the top of the page. Returns (html_fragment, extra_css).

    Returns empty strings if brief_text is None or storyline-helper isn't
    importable.
    """
    if not brief_text:
        return ("", "")
    try:
        helper_scripts = Path(__file__).resolve().parents[2] / "storyline-helper" / "scripts"
        import sys
        sys.path.insert(0, str(helper_scripts))
        from emit_dot_dash import (
            parse_brief_for_dot_dash, render_dot_dash_html, dot_dash_css,
        )
    except Exception as e:
        print(f"  warning: dot-dash embed skipped ({type(e).__name__}: {e})")
        return ("", "")

    try:
        data = parse_brief_for_dot_dash(brief_text)
        fragment = render_dot_dash_html(data, standalone=False)
        css = dot_dash_css()
    except Exception as e:
        print(f"  warning: dot-dash render failed ({type(e).__name__}: {e})")
        return ("", "")

    # Wrap in collapsible <details>. Default closed so option cards stay
    # above the fold; reviewer expands to see the storyline.
    section = (
        '<details class="storyline-section">'
        '<summary><span class="storyline-summary-text">Storyline (dot-dash) — click to expand</span></summary>'
        '<div class="storyline-body">'
        f'{fragment}'
        '</div>'
        '</details>'
    )
    # Plus a few rules to style the wrapper itself
    wrapper_css = """
.storyline-section { background: var(--panel); border-bottom: 1px solid var(--border); padding: 8px 24px 12px; }
.storyline-section summary { font-size: 11px; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 1.5px; cursor: pointer; padding: 8px 0; outline: none; user-select: none; }
.storyline-section summary:hover .storyline-summary-text { color: var(--text); }
.storyline-section[open] summary { border-bottom: 1px solid var(--border); margin-bottom: 12px; }
.storyline-body { max-width: 1200px; margin: 0 auto; padding: 8px 0; }
"""
    return (section, wrapper_css + css)


def write_review_html(narrative: List[Dict[str, Any]], out_path: str,
                      deck_type: Optional[str] = None,
                      deck_title: str = "Deck options review",
                      top_n: int = 3,
                      client_template: Optional[str] = None,
                      workers: int = 6,
                      brief_text: Optional[str] = None) -> Path:
    """Generate the per-deck options review HTML.

    Renders themed thumbnails (in parallel) for every candidate option using
    the user's actual brief content + client template's theme, then writes a
    REVIEW.html-style page where each slide has 3 options + a None button +
    feedback textarea.

    Runs `check_brief` at the start and surfaces blocking/warning issues in
    a banner near the top of the page so the user sees them before picking.
    """
    # Brief-time QC — run first so issues surface BEFORE the user picks options.
    qc_report = check_brief(narrative)
    if qc_report["blocking"]:
        print(f"BRIEF QC BLOCKING ({len(qc_report['blocking'])}):")
        for issue in qc_report["blocking"]:
            print(f"  ! {issue}")
    if qc_report["warnings"]:
        print(f"BRIEF QC WARNINGS ({len(qc_report['warnings'])}):")
        for issue in qc_report["warnings"]:
            print(f"  ~ {issue}")

    specs = prepare_deck_specs(narrative, top_n=top_n, deck_type=deck_type)
    narrative_by_num = {s.get("slide_num"): s for s in narrative}

    # Pattern-aware overrides — each option gets a targeted overrides dict
    # generated from its own shape_role_map. Falls back to the legacy fan-out
    # broadcaster if the picked pattern has no role_map (older catalog entries).
    from twins.overrides_resolver import pattern_aware_overrides

    # Themed thumbnails — parallel render, with per-option render-time QC.
    qc_results: Dict = {}
    if client_template:
        from twins.themed_thumbnails import _render_one_with_qc
        from concurrent.futures import ThreadPoolExecutor, as_completed
        jobs = []
        for spec in specs:
            ns = narrative_by_num.get(spec["slide_num"]) or {}
            for opt in spec["options"]:
                pattern_entry = opt.get("entry") or {}
                if pattern_entry.get("shape_role_map"):
                    ovs = pattern_aware_overrides(ns, pattern_entry)
                else:
                    # Catalog entry pre-dates shape_role_map; use legacy fan-out
                    ovs = narrative_slide_to_overrides(ns)
                jobs.append((spec["slide_num"], opt["pattern"], ovs))
        print(f"Rendering {len(jobs)} themed thumbnails ({workers} workers)...")
        results: Dict = {}
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_render_one_with_qc, p, client_template, ovs, 100): (sn, p)
                       for (sn, p, ovs) in jobs}
            done = 0
            total = len(futures)
            for fut in as_completed(futures):
                sn, p = futures[fut]
                try:
                    png_path, qc = fut.result()
                    results[(sn, p)] = png_path
                    qc_results[(sn, p)] = qc
                except Exception as e:
                    results[(sn, p)] = None
                    qc_results[(sn, p)] = {"verdict": "critical",
                                           "issues": [{"severity": "critical",
                                                       "msg": f"worker error: {e}"}]}
                    print(f"  worker error {sn}/{p}: {e}")
                done += 1
                if done % 5 == 0 or done == total:
                    print(f"  {done}/{total}")
        for spec in specs:
            for opt in spec["options"]:
                opt["thumbnail"] = results.get((spec["slide_num"], opt["pattern"]))
                opt["render_qc"] = qc_results.get(
                    (spec["slide_num"], opt["pattern"]),
                    {"verdict": "clean", "issues": []},
                )

    # Build SLIDES JSON for the page's JS
    slides_data = []
    for spec in specs:
        sn = spec["slide_num"]
        ns = narrative_by_num.get(sn) or {}
        content = ns.get("content") or {}
        options_data = []
        for opt in spec.get("options", []):
            entry = opt.get("entry") or {}
            qc = opt.get("render_qc") or {"verdict": "clean", "issues": []}
            options_data.append({
                "pattern": opt["pattern"],
                "thumbnail": _png_uri(opt.get("thumbnail")),
                "family": entry.get("family", ""),
                "layout": entry.get("layout", ""),
                "intent_tags": (entry.get("intent_tags") or [])[:3],
                "score": opt.get("score", 0),
                "qc_verdict": qc.get("verdict", "clean"),
                "qc_issues": [str(i.get("msg", "")) for i in (qc.get("issues") or [])],
            })

        # Derive the per-section feedback fields based on what content the
        # brief actually has for this slide. Each section gets its own
        # textarea so the user can leave targeted feedback without writing
        # a paragraph.
        feedback_sections = _derive_feedback_sections(ns)

        slides_data.append({
            "slide_num": sn,
            "governing_thought": ns.get("governing_thought", ""),
            "so_what": ns.get("so_what", ""),
            "editorial_emphasis": ns.get("editorial_emphasis", ""),
            "options": options_data,
            "feedback_sections": feedback_sections,
        })

    # CSS — ported verbatim from _pattern-library/REVIEW.html, minor tweaks
    # for 3-thumbnail row instead of single iframe preview.
    css = """
:root {
  --bg: #0F172A;
  --panel: #1E293B;
  --panel-2: #273448;
  --text: #E2E8F0;
  --text-dim: #94A3B8;
  --accent: #A100FF;
  --approve: #16A34A;
  --tweak: #CA8A04;
  --reject: #DC2626;
  --pending: #64748B;
  --border: #334155;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); }
body { padding: 0; }
.topbar { position: sticky; top: 0; z-index: 100; background: var(--panel); border-bottom: 2px solid var(--border); padding: 14px 24px; display: flex; align-items: center; gap: 18px; }
.title { font-size: 17px; font-weight: 700; }
.title-sub { font-size: 11px; color: var(--text-dim); font-weight: 400; margin-top: 2px; }
.summary { display: flex; gap: 10px; flex: 1; margin-left: 16px; align-items: center; flex-wrap: wrap; }
.pill { padding: 5px 12px; border-radius: 14px; font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; gap: 5px; }
.pill .num { font-weight: 800; font-variant-numeric: tabular-nums; }
.pill.approve { background: rgba(22,163,74,0.15); color: var(--approve); border: 1px solid var(--approve); }
.pill.tweak { background: rgba(202,138,4,0.15); color: var(--tweak); border: 1px solid var(--tweak); }
.pill.reject { background: rgba(220,38,38,0.15); color: var(--reject); border: 1px solid var(--reject); }
.pill.pending { background: rgba(100,116,139,0.15); color: var(--text-dim); border: 1px solid var(--pending); }
button { font-family: inherit; cursor: pointer; border: none; padding: 7px 14px; font-size: 12px; font-weight: 600; border-radius: 6px; transition: all 0.15s; }
.btn-primary { background: var(--accent); color: white; }
.btn-primary:hover { filter: brightness(1.15); }
.btn-secondary { background: var(--panel-2); color: var(--text); border: 1px solid var(--border); }
.btn-secondary:hover { background: var(--border); }
.topbar-actions { display: flex; gap: 6px; }

.filter-bar { background: var(--panel-2); padding: 10px 24px; border-bottom: 1px solid var(--border); display: flex; gap: 10px; align-items: center; }
.filter-bar label { font-size: 11px; color: var(--text-dim); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.filter-bar select { background: var(--panel); color: var(--text); border: 1px solid var(--border); padding: 4px 8px; font-family: inherit; font-size: 12px; border-radius: 4px; }
.filter-bar input[type="search"] { background: var(--panel); color: var(--text); border: 1px solid var(--border); padding: 4px 10px; font-family: inherit; font-size: 12px; border-radius: 4px; min-width: 200px; }

.qc-banner { background: linear-gradient(135deg, #1E293B, #2D1B4E); border-bottom: 1px solid var(--border); padding: 12px 24px; }
.qc-banner-title { font-size: 10px; font-weight: 800; color: var(--accent); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; }
.qc-banner-list { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; counter-reset: qc-counter; }
.qc-banner-item { font-size: 10px; color: var(--text); line-height: 1.35; padding-left: 14px; position: relative; }
.qc-banner-item::before { content: counter(qc-counter); counter-increment: qc-counter; position: absolute; left: 0; top: 0; color: var(--accent); font-weight: 800; }

/* Brief-time QC banner — dynamic, only renders when check_brief finds issues */
.qc-brief-banner { background: var(--panel-2); border-bottom: 1px solid var(--border); padding: 12px 24px; }
.qc-brief-banner-title { font-size: 10px; font-weight: 800; color: var(--text); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
.qc-brief-section { margin-top: 6px; padding: 8px 12px; border-radius: 4px; border-left: 3px solid; font-size: 11px; line-height: 1.5; }
.qc-brief-blocking { background: rgba(220,38,38,0.08); border-color: var(--reject); }
.qc-brief-warning { background: rgba(202,138,4,0.08); border-color: var(--tweak); }
.qc-brief-section summary { font-weight: 800; cursor: pointer; outline: none; user-select: none; display: flex; align-items: center; gap: 6px; padding: 2px 0; list-style: none; }
.qc-brief-section summary::-webkit-details-marker { display: none; }
.qc-brief-section[open] summary { margin-bottom: 6px; }
.qc-brief-blocking summary { color: var(--reject); }
.qc-brief-warning summary { color: var(--tweak); }
.qc-brief-warning summary:hover { color: #FCD34D; }
.qc-brief-icon { display: inline-block; width: 16px; height: 16px; border-radius: 50%; text-align: center; line-height: 16px; font-weight: 800; }
.qc-brief-blocking .qc-brief-icon { background: var(--reject); color: white; }
.qc-brief-warning .qc-brief-icon { background: var(--tweak); color: white; }
.qc-brief-section ul { list-style: none; margin: 0; padding: 0; }
.qc-brief-section li { padding-left: 12px; position: relative; color: var(--text-dim); }
.qc-brief-section li::before { content: '•'; position: absolute; left: 0; color: currentColor; }

.cards { padding: 20px; display: flex; flex-direction: column; gap: 20px; max-width: 1880px; margin: 0 auto; }
.card { background: var(--panel); border-radius: 8px; border: 1px solid var(--border); overflow: hidden; }
.card.hidden { display: none; }
.card-header-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; padding: 14px 20px 10px; border-bottom: 1px solid var(--border); }
.card-num { font-size: 11px; color: var(--text-dim); font-weight: 700; letter-spacing: 1px; }
.card-name { font-size: 16px; font-weight: 700; margin-top: 3px; }
.card-targets { font-size: 12px; color: var(--text-dim); margin-top: 3px; font-style: italic; }
.card-eyebrow { font-size: 11px; color: var(--text-dim); margin-top: 4px; }
.card-eyebrow strong { color: var(--accent); }
.status-badge { padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; align-self: flex-start; }
.status-badge.pending { background: var(--pending); color: white; }
.status-badge.picked { background: var(--approve); color: white; }
.status-badge.none { background: var(--reject); color: white; }

.options-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; padding: 14px 20px; }
.option {
  background: var(--panel-2); border: 2px solid var(--border); border-radius: 6px;
  padding: 0; cursor: pointer; transition: all 0.15s; overflow: hidden;
  display: flex; flex-direction: column;
}
.option:hover { border-color: var(--accent); }
.option.picked { border-color: var(--approve); background: rgba(22,163,74,0.10); box-shadow: 0 0 0 3px rgba(22,163,74,0.18); }
.option-frame { background: #000; aspect-ratio: 16 / 9; position: relative; }
.option-frame img { width: 100%; height: 100%; object-fit: contain; background: white; display: block; }
.option-frame .missing { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: var(--text-dim); font-size: 11px; background: var(--panel-2); }
.option-meta { padding: 8px 10px 10px; font-size: 11px; }
.option-letter { font-size: 11px; font-weight: 800; color: var(--accent); letter-spacing: 1px; text-transform: uppercase; }
.option-score { font-size: 10px; color: var(--text-dim); font-family: monospace; margin-left: 6px; }
.option-pat { color: var(--text); font-family: monospace; font-size: 10px; font-weight: 700; word-break: break-all; margin-top: 4px; line-height: 1.3; }
.option-taxon { color: var(--text-dim); margin-top: 2px; font-size: 10px; }
.option-tags { color: var(--text-dim); margin-top: 2px; font-family: monospace; font-size: 9px; }

/* Render-time QC badges (clean / warning / critical). The badge sits inline
   in the option-meta header next to the score; the option itself gets a
   border color and (for critical) is greyed out + unclickable. */
.qc-badge { display: inline-block; margin-left: 6px; padding: 1px 6px; font-size: 10px; font-weight: 800; border-radius: 8px; vertical-align: middle; cursor: help; }
.qc-badge.qc-clean { background: rgba(22,163,74,0.20); color: var(--approve); border: 1px solid var(--approve); }
.qc-badge.qc-warning { background: rgba(202,138,4,0.20); color: var(--tweak); border: 1px solid var(--tweak); }
.qc-badge.qc-critical { background: rgba(220,38,38,0.20); color: var(--reject); border: 1px solid var(--reject); }
.option.qc-warning { border-color: var(--tweak); }
.option.qc-critical { border-color: var(--reject); opacity: 0.55; filter: grayscale(0.4); }
.option.qc-critical:hover { box-shadow: none; transform: none; }
.option.qc-critical .option-frame::after {
  content: 'BLOCKED'; position: absolute; top: 8px; right: 8px; background: var(--reject);
  color: white; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 4px;
  letter-spacing: 1px; pointer-events: none;
}

.card-controls { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 14px 20px 18px; border-top: 1px solid var(--border); }
.decision-buttons { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 6px; }
.decision-buttons button { padding: 11px 6px; font-size: 11px; font-weight: 700; border-radius: 5px; border: 2px solid transparent; background: var(--panel-2); color: var(--text-dim); transition: all 0.15s; }
.decision-buttons button:hover { filter: brightness(1.15); }
.decision-buttons button.active.pick { background: var(--approve); color: white; border-color: var(--approve); }
.decision-buttons button.active.none { background: var(--reject); color: white; border-color: var(--reject); }
.decision-buttons button:not(.active).pick:hover { border-color: var(--approve); color: var(--approve); }
.decision-buttons button:not(.active).none:hover { border-color: var(--reject); color: var(--reject); }

textarea { width: 100%; min-height: 44px; background: var(--panel-2); color: var(--text); border: 1px solid var(--border); border-radius: 5px; padding: 7px 10px; font-family: inherit; font-size: 12px; line-height: 1.4; resize: vertical; }
textarea:focus { outline: none; border-color: var(--accent); }
.field-label { font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px; }
.hint-text { font-size: 11px; color: var(--text-dim); margin-bottom: 10px; font-style: italic; }
.feedback-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 14px; }
.feedback-field label { display: block; font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; margin-bottom: 4px; }
.feedback-field textarea { min-height: 38px; }

.output-section { padding: 20px; max-width: 1880px; margin: 0 auto; }
.output-section h2 { font-size: 13px; font-weight: 700; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
.output-box { background: #0B1424; border: 1px solid var(--border); border-radius: 6px; padding: 16px 20px; font-family: 'SF Mono', Monaco, Consolas, monospace; font-size: 12px; line-height: 1.5; color: var(--text); white-space: pre-wrap; max-height: 400px; overflow: auto; }
.output-section .actions { display: flex; gap: 8px; margin-top: 12px; }
.toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--approve); color: white; padding: 10px 22px; border-radius: 5px; font-weight: 600; opacity: 0; pointer-events: none; transition: opacity 0.2s; z-index: 200; }
.toast.show { opacity: 1; }
"""

    # Optional: render the dot-dash storyline as a collapsible section
    # at the top of the page. Only present when brief_text is passed in.
    storyline_html, storyline_css = _render_dot_dash_section(brief_text)
    css = css + "\n" + storyline_css

    # JS — ported pattern from REVIEW.html (localStorage, decision setters,
    # filters, output, toast) adapted for the slide-options data model.
    slides_js_data = json.dumps(slides_data, ensure_ascii=False)
    deck_meta_js = json.dumps({"title": deck_title, "client_template": Path(client_template).name if client_template else None}, ensure_ascii=False)

    js = """
const SLIDES = __SLIDES__;
const DECK_META = __DECK_META__;
const STORAGE_KEY = "slide-lab-options-review-" + (DECK_META.title || "deck");
const STATES = {};

function ensureState(sn) {
  if (!STATES[sn]) STATES[sn] = { decision: "pending", pick: null, feedback: {} };
  if (typeof STATES[sn].feedback !== "object" || STATES[sn].feedback === null) {
    // Migrate old single-string feedback to object form
    const old = STATES[sn].feedback;
    STATES[sn].feedback = old && typeof old === "string" ? { other: old } : {};
  }
  return STATES[sn];
}

function renderCards() {
  const root = document.getElementById("cards");
  root.innerHTML = "";
  for (const sl of SLIDES) {
    const s = ensureState(sl.slide_num);
    const card = document.createElement("div");
    card.className = "card";
    card.dataset.slideNum = sl.slide_num;
    card.dataset.gt = (sl.governing_thought || "").toLowerCase();

    const optionsHtml = sl.options.map((o, i) => {
      const letter = String.fromCharCode(65 + i);  // A, B, C
      const isPicked = s.pick === o.pattern;
      const thumb = o.thumbnail
        ? `<img src="${o.thumbnail}" alt="${o.pattern}">`
        : `<div class="missing">no thumbnail</div>`;
      // Render-time QC badge — clean/warning/critical with hover tooltip
      const verdict = o.qc_verdict || 'clean';
      const issues = (o.qc_issues || []).join('\\n');
      const verdictGlyph = verdict === 'critical' ? '✗' : (verdict === 'warning' ? '!' : '✓');
      const isCritical = verdict === 'critical';
      const clickHandler = isCritical
        ? `onclick="event.preventDefault(); alert('This option has critical QC issues and is blocked from selection:\\\\n\\\\n${issues.replace(/'/g, '&#39;').replace(/\\n/g, '\\\\n')}')"`
        : `onclick="pickOption(${sl.slide_num}, '${o.pattern}', '${letter}')"`;
      const qcBadge = `<span class="qc-badge qc-${verdict}" title="${escapeHtml(issues || 'no issues')}">${verdictGlyph}</span>`;
      return `
        <div class="option ${isPicked ? 'picked' : ''} qc-${verdict}" data-pattern="${o.pattern}" data-letter="${letter}" ${clickHandler}>
          <div class="option-frame">${thumb}</div>
          <div class="option-meta">
            <span class="option-letter">Option ${letter}</span><span class="option-score">fit ${o.score}</span>${qcBadge}
            <div class="option-pat">${o.pattern}</div>
            <div class="option-taxon">${o.family} · ${o.layout}</div>
            <div class="option-tags">${(o.intent_tags || []).join(', ')}</div>
          </div>
        </div>
      `;
    }).join("");

    const buttons = sl.options.map((o, i) => {
      const letter = String.fromCharCode(65 + i);
      return `<button class="pick ${s.pick === o.pattern ? 'active' : ''}" onclick="pickOption(${sl.slide_num}, '${o.pattern}', '${letter}')">PICK ${letter}</button>`;
    }).join("");

    card.innerHTML = `
      <div class="card-header-row">
        <div style="flex: 1;">
          <div class="card-num">SLIDE ${sl.slide_num}</div>
          <div class="card-name">${escapeHtml(sl.governing_thought || '(no governing thought)')}</div>
          ${sl.so_what ? `<div class="card-targets">So-what: ${escapeHtml(sl.so_what)}</div>` : ''}
          ${sl.editorial_emphasis ? `<div class="card-eyebrow"><strong>Editorial:</strong> ${escapeHtml(sl.editorial_emphasis)}</div>` : ''}
        </div>
        <div class="status-badge ${s.decision}" id="badge-${sl.slide_num}">${s.decision.toUpperCase()}</div>
      </div>

      <div class="options-row">${optionsHtml}</div>

      <div class="card-controls">
        <div>
          <div class="field-label">Decision</div>
          <div class="decision-buttons" id="buttons-${sl.slide_num}">
            ${buttons}
            <button class="none ${s.decision === 'none' ? 'active' : ''}" onclick="pickNone(${sl.slide_num})">✗ NONE — TRY AGAIN</button>
          </div>
          <div class="field-label" style="margin-top: 14px;">Section-level feedback</div>
          <div class="hint-text">Leave feedback on any section. Skip what doesn't apply.</div>
        </div>
        <div class="feedback-grid">
          ${(sl.feedback_sections || []).map(sec => `
            <div class="feedback-field">
              <label for="fb-${sl.slide_num}-${sec.id}">${escapeHtml(sec.label)}</label>
              <textarea id="fb-${sl.slide_num}-${sec.id}"
                        placeholder="${escapeHtml(sec.placeholder || '')}"
                        oninput="setFeedback(${sl.slide_num}, '${sec.id}', this.value)">${escapeHtml((s.feedback || {})[sec.id] || '')}</textarea>
            </div>
          `).join("")}
        </div>
      </div>
    `;
    root.appendChild(card);
  }
  applyFilters();
  updateOutput();
}

function pickOption(sn, pattern, letter) {
  const s = ensureState(sn);
  s.pick = pattern;
  s.pick_letter = letter;
  s.decision = "picked";
  saveState();
  renderCards();
}

function pickNone(sn) {
  const s = ensureState(sn);
  s.pick = null;
  s.pick_letter = null;
  s.decision = "none";
  saveState();
  renderCards();
}

function setFeedback(sn, sectionId, val) {
  const s = ensureState(sn);
  if (typeof s.feedback !== "object" || s.feedback === null) s.feedback = {};
  if (val.trim()) s.feedback[sectionId] = val;
  else delete s.feedback[sectionId];
  saveState();
  updateOutput();
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function updateOutput() {
  let picked = 0, none = 0, pending = 0;
  const lines = [`# ${DECK_META.title} — picks`, `# Client template: ${DECK_META.client_template || '(none)'}`, ""];
  lines.push("slides:");
  for (const sl of SLIDES) {
    const s = ensureState(sl.slide_num);
    if (s.decision === "picked") picked++;
    else if (s.decision === "none") none++;
    else pending++;
    lines.push(`  - slide_num: ${sl.slide_num}`);
    lines.push(`    decision: ${s.decision}`);
    if (s.pick) lines.push(`    pattern: ${s.pick}`);
    const fb = s.feedback || {};
    const keys = Object.keys(fb).filter(k => (fb[k] || "").trim());
    if (keys.length) {
      lines.push(`    feedback:`);
      for (const k of keys) {
        const v = fb[k].trim();
        // YAML-safe: if multi-line, use block scalar; else inline-quoted
        if (v.includes("\\n")) {
          lines.push(`      ${k}: |`);
          for (const ln of v.split(/\\r?\\n/)) lines.push(`        ${ln}`);
        } else {
          const esc = v.replace(/"/g, '\\\\"');
          lines.push(`      ${k}: "${esc}"`);
        }
      }
    }
  }
  lines.push("");
  lines.push(`# ${picked} picked · ${none} rejected · ${pending} pending (of ${SLIDES.length})`);
  document.getElementById("count-picked").textContent = picked;
  document.getElementById("count-none").textContent = none;
  document.getElementById("count-pending").textContent = pending;
  document.getElementById("output-box").textContent = lines.join("\\n");
}

function applyFilters() {
  const status = document.getElementById("filter-status").value;
  const text = document.getElementById("filter-text").value.toLowerCase().trim();
  let shown = 0;
  for (const card of document.querySelectorAll(".card")) {
    const sn = parseInt(card.dataset.slideNum);
    const s = ensureState(sn);
    let visible = true;
    if (status !== "all" && s.decision !== status) visible = false;
    if (text && !card.dataset.gt.includes(text) && !String(sn).includes(text)) visible = false;
    card.classList.toggle("hidden", !visible);
    if (visible) shown++;
  }
  document.getElementById("shown-count").textContent = `${shown} of ${SLIDES.length} shown`;
}

function saveState() { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(STATES)); } catch (e) {} }
function loadState() {
  try {
    const s = localStorage.getItem(STORAGE_KEY);
    if (s) Object.assign(STATES, JSON.parse(s));
  } catch (e) {}
}
function resetAll() {
  if (!confirm("Reset all picks and feedback?")) return;
  for (const k of Object.keys(STATES)) delete STATES[k];
  saveState();
  renderCards();
}
function copyOutput() {
  const txt = document.getElementById("output-box").textContent;
  navigator.clipboard.writeText(txt).then(() => showToast("Copied to clipboard"));
}
function downloadOutput() {
  const txt = document.getElementById("output-box").textContent;
  const blob = new Blob([txt], { type: "text/yaml" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "deck-picks.yaml"; a.click();
  URL.revokeObjectURL(url);
}
function showToast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 1800);
}

loadState();
renderCards();
"""
    js = js.replace("__SLIDES__", slides_js_data).replace("__DECK_META__", deck_meta_js)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{escape(deck_title)} · Options Review</title>
<style>{css}</style>
</head>
<body>

<div class="topbar">
  <div>
    <div class="title">{escape(deck_title)} · OPTIONS REVIEW · {len(specs)} slides</div>
    <div class="title-sub">Client template: {escape(Path(client_template).name) if client_template else '(none)'} · Pick A/B/C per slide or mark NONE to try again. Decisions persist via localStorage.</div>
  </div>
  <div class="summary">
    <div class="pill approve">✓ <span class="num" id="count-picked">0</span></div>
    <div class="pill reject">✗ <span class="num" id="count-none">0</span></div>
    <div class="pill pending">○ <span class="num" id="count-pending">0</span></div>
  </div>
  <div class="topbar-actions">
    <button class="btn-secondary" onclick="resetAll()">Reset</button>
    <button class="btn-primary" onclick="copyOutput()">Copy → paste to Claude</button>
  </div>
</div>

{storyline_html}

<div class="filter-bar">
  <label>Filter:</label>
  <select id="filter-status" onchange="applyFilters()">
    <option value="all">All slides</option>
    <option value="pending">Pending only</option>
    <option value="picked">Picked only</option>
    <option value="none">Rejected only</option>
  </select>
  <input type="search" id="filter-text" placeholder="Search slide title…" oninput="applyFilters()">
  <span style="margin-left: auto; font-size: 11px; color: var(--text-dim);" id="shown-count"></span>
</div>

<div class="qc-banner">
  <div class="qc-banner-title">Standing QC checklist · every slide must satisfy all six</div>
  <div class="qc-banner-list">
    <div class="qc-banner-item">Visual hierarchy clear</div>
    <div class="qc-banner-item">Single focal point</div>
    <div class="qc-banner-item">Margins consistent</div>
    <div class="qc-banner-item">Whitespace intentional</div>
    <div class="qc-banner-item">Grid alignment</div>
    <div class="qc-banner-item">Page balanced</div>
  </div>
</div>

{_render_brief_qc_banner(qc_report)}

<div class="cards" id="cards"></div>

<div class="output-section">
  <h2>Output (live)</h2>
  <div class="output-box" id="output-box">Loading…</div>
  <div class="actions">
    <button class="btn-primary" onclick="copyOutput()">Copy to clipboard</button>
    <button class="btn-secondary" onclick="downloadOutput()">Download as .yaml</button>
  </div>
</div>

<div class="toast" id="toast">Copied to clipboard</div>

<script>{js}</script>
</body>
</html>
"""

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return out_path


if __name__ == "__main__":
    import sys
    NARRATIVE = [
        {"slide_num": 1, "governing_thought": "[Cover slide]",
         "editorial_emphasis": "Title, tagline, and presenter name only.",
         "content": {
             "cover": {
                 "title": "Slide Lab",
                 "tagline": "Think. Argue. Build.",
                 "presented_by": "Mario Peralta · Strategy Manager",
                 "client": "Accenture MDs & SMDs",
                 "date": "May 2026",
                 "eyebrow": "INTERNAL DECK · 2026",
                 "meta": "CONFIDENTIAL · ACCENTURE INTERNAL · MAY 2026",
             }
         }},
        {"slide_num": 2, "governing_thought": "Consultants rarely lack ideas — they struggle to cut through them.",
         "so_what": "Not a knowledge gap. Not a skill deficit. A structural problem — and structural problems have structural solutions.",
         "editorial_emphasis": "the contrast",
         "content": {"cards": [
             {"heading": "Too much to say", "body": "Knowing what to cut is harder than knowing what to include. Every workstream produces legitimate findings."},
             {"heading": "Too many cooks", "body": "Every collaborator has a view on what belongs on the page. More opinions mean harder choices, not a richer argument."},
             {"heading": "The audience needs what's next", "body": "They don't need to understand all the work. They need to understand the next step."},
         ]}},
        {"slide_num": 3, "governing_thought": "Every other tool skips the hard part: challenging the argument before the slide gets built.",
         "so_what": "Any tool is only as good as the thinking behind it. Slide Lab is the only one built to fix the thinking first.",
         "editorial_emphasis": "the contrast",
         "content": {"cards": [
             {"heading": "The training gap", "body": "Most consultants never learned the rigor. Pages get made repeatedly without knowing the underlying message."},
             {"heading": "The GenAI gap", "body": "Generic AI does what you say. No pushback, no conflict detection, no standard."},
             {"heading": "The result", "body": "Subpar page. Subpar message. Manual fixes at the end."},
         ]}},
        {"slide_num": 4, "governing_thought": "The argument comes first. The page follows.",
         "so_what": "Better argument. Sharper page. Every time.",
         "editorial_emphasis": "the conclusion",
         "content": {"cards": [
             {"heading": "Meets you where you are", "body": "Whether you're a BA learning to build an argument or an MD filtering through noise."},
             {"heading": "Thought partner, not slide machine", "body": "It works with you, not instead of you. The coaching IS the product."},
             {"heading": "Quality scales with thinking", "body": "Output quality scales directly with quality of thinking — and Slide Lab is built to raise it."},
         ]}},
        {"slide_num": 5, "governing_thought": "Three skill domains — connected, not stacked.",
         "so_what": "A complete toolkit — every stage of the argument has a partner built for it.",
         "editorial_emphasis": "the contrast",
         "content": {"pillars": [
             {"name": "Think", "body": "Collect and organize ideas. Deck type selection. Narrative framework matching. Foundation check."},
             {"name": "Argue", "body": "Storyline Helper. 5-part quality gate. Language quality pass. RFP & Feedback tools."},
             {"name": "Build", "body": "3 design options per slide. Brand template integration. 9 chart types. Post-build QC reviewer."},
         ]}},
        {"slide_num": 6, "governing_thought": "Same data, same scenario — the difference between unguided AI and Slide Lab is the argument.",
         "so_what": "The data didn't change. The thinking did. That's what Slide Lab does.",
         "editorial_emphasis": "the contrast",
         "chart_type": "waterfall"},
        {"slide_num": 7, "governing_thought": "[Screenshot — Think & Argue in action]",
         "editorial_emphasis": "Storyline Helper UI screenshot."},
        {"slide_num": 8, "governing_thought": "[Screenshot — Build in action]",
         "editorial_emphasis": "Slide Builder UI + output screenshot."},
        {"slide_num": 9, "governing_thought": "Slide Lab raises the quality of your argument and your deck — and gets better every time someone uses it on real work.",
         "so_what": "Try it on something real. What breaks makes it better.",
         "editorial_emphasis": "the contrast",
         "content": {"panels": [
             {"label": "Works well today",
              "body": "Argument-driven text. Data callouts. Comparisons. Complex charts via Excel/ThinkCell. Simple tables, agendas, title slides."},
             {"label": "Still growing",
              "body": "Process flows. Org charts. Highly bespoke layouts that deviate from the client template."}
         ]}},
        {"slide_num": 10, "governing_thought": "One real deck is all it takes — try it, and if it lands, pass it on.",
         "so_what": "The door is open. Walk through it.",
         "editorial_emphasis": "the ask"},
    ]
    # Usage: python -m twins.review_html <output-review.html> <client-template.pptx>
    if len(sys.argv) < 3:
        print("Usage: python -m twins.review_html <output-review.html> <client-template.pptx>")
        sys.exit(1)
    out = sys.argv[1]
    client_template = sys.argv[2]
    p = write_review_html(NARRATIVE, out, deck_type="capability-pitch",
                          deck_title="Intro to Slide Lab",
                          client_template=client_template, workers=6)
    print(f"\nWrote {p}")
