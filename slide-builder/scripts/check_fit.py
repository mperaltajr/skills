#!/usr/bin/env python3
"""check_fit.py: does every piece of text on an option fit as PowerPoint sets it?

Workers run it on each option before finishing (owner's decision, 2026-10-09):

  py -3 scripts/check_fit.py <out>/slide_NN/option_X.pptx

It measures every text box, table cell and placeholder with the client
template's own fonts (brand.yml), without opening PowerPoint or any renderer,
so it takes well under a second. The template and the slide's layout are read
from the build's _meta.json (pass --template to name a template yourself).

What it reports (the same check finalize runs on the finished slide):
  STOP   a word wider than its box: PowerPoint breaks it in the middle
  STOP   a table whose rows grow into other content, past the body area or
         off the page
  FLAG   one-line text using more than 92% of its box width (PowerPoint may
         wrap it; the last line of wrapped text from 98%),
         a label of two words or fewer that wraps, a table row that grows

Run it on the raw option the script just saved: Slide Lab's own fonts are
swapped for the template's when it is finished, so the raw file's fonts do not
matter; this measures with the template's. Finalize measures the finished
slide again, and a STOP there refuses the build.

Exit: 0 nothing stops (flags may be listed) | 1 something stops | 2 bad usage
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))


def _build_context(option: Path, template_arg: str | None):
    """(template path or None, layout name or '') from the build's _meta.json."""
    out_dir = option.resolve().parent.parent
    meta = {}
    try:
        meta = json.loads((out_dir / "_meta.json").read_text(encoding="utf-8"))
    except Exception:
        meta = {}
    template = template_arg or meta.get("template") or ""
    layout = ""
    try:
        n = int(option.resolve().parent.name.split("_")[1])
        for s in meta.get("slides", []):
            if s.get("n") == n:
                layout = (s.get("layout") or "").strip()
    except Exception:
        pass
    return (Path(template) if template else None), layout


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Text-fit check for one option (no renderer).")
    ap.add_argument("option", type=Path, help="option_X.pptx (raw or finished)")
    ap.add_argument("--template", default=None, help="client template .pptx (default: from _meta.json)")
    ap.add_argument("--json", action="store_true", help="print the findings as JSON")
    args = ap.parse_args(argv)
    if not args.option.exists():
        print(f"ERROR: {args.option} not found")
        return 2
    import _chrome_schema as CS
    from pptx import Presentation

    template, layout = _build_context(args.option, args.template)
    fonts, body_bottom = None, None
    if template is not None and template.exists():
        try:
            from twins.client_theme import load_client_theme
            theme = load_client_theme(str(template))
            fonts = CS.fit_fonts(heading=theme.major_font or "", body=theme.minor_font or "",
                                 heading_ttf=theme.title_font_ttf_path or "",
                                 heading_bold_ttf=theme.title_font_bold_ttf_path or "",
                                 body_ttf=theme.body_font_ttf_path or "")
        except Exception as exc:
            print(f"WARN: could not read the template's fonts ({type(exc).__name__}: {exc})")
        try:
            import _paths as _p
            spec = CS.load_chrome_yml(_p.chrome_yml(template))
            lc = spec.layouts.get(layout) if layout else None
            body_bottom = getattr(lc, "body_bottom_y_px", None) if lc else None
        except Exception:
            body_bottom = None
    if fonts is None or not fonts.get("body_regular"):
        print("ERROR: the template's font files could not be found, so nothing was measured. "
              "Pass --template <client template.pptx>, or re-register the template so "
              "brand.yml records its fonts.")
        return 2

    prs = Presentation(str(args.option))
    res = CS.fit_findings(prs.slides[0], fonts, body_bottom_px=body_bottom)
    stops = [f for f in res["findings"] if f["stop"]]
    flags = [f for f in res["findings"] if not f["stop"]]
    if args.json:
        print(json.dumps(res, indent=1))
    else:
        print(f"{args.option.name}: {res['measured']} paragraph(s) measured with "
              f"{Path(fonts['body_regular']).name}"
              + (f" ({res['unmeasured']} not measured: font file missing)" if res["unmeasured"] else ""))
        for f in stops:
            print("  STOP  " + CS.fit_problem_line(f))
        for f in flags:
            print("  FLAG  " + CS.fit_problem_line(f))
        if not stops and not flags:
            print("  OK: every line fits.")
        elif not stops:
            print("  Nothing stops the build. Fix the flags where you can (widen the box, "
                  "shorten the text), or leave them if the design needs it.")
        else:
            print("  Fix every STOP before finishing: finalize refuses the build otherwise.")
    return 1 if stops else 0


if __name__ == "__main__":
    sys.exit(main())
