"""Slide Lab deck orchestrator — Part B: execute agent .py, graft, theme remap, render.

Inputs:
  --out PATH       output dir from build_deck.py
  --template PATH  client PPTX template (same one used in Part A)
  --skip-build     skip executing option_X.py (use existing option_X.pptx)
  --skip-render    skip rendering PNGs

Pipeline:
  1. For each <out>/slide_NN/option_X.py, run via subprocess to produce option_X.pptx.
  2. Graft each option_X.pptx onto the client template + apply theme remap:
       <out>/themed/slide_NN/option_X.pptx
  3. Render each themed .pptx to PNG (LibreOffice headless, parallel x4):
       <out>/themed/slide_NN/option_X.png
  4. Run a deterministic per-option QC self-check, writing option_X.qc.json
       next to each themed PPTX.
  5. Write <out>/RESULT.md with per-slide status table.

Adapted from `graft_all_to_fedex.py` (the validated graft script).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import traceback
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

SKILL_ROOT = Path(__file__).resolve().parents[1]
QC_SCRIPTS = SKILL_ROOT.parent / "slide-qc" / "scripts"
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(QC_SCRIPTS))

from pptx import Presentation  # noqa: E402
from pptx.util import Pt  # noqa: E402
from twins.client_theme import load_client_theme, apply_theme_to_shape_xml  # noqa: E402
from twins.composer import (  # noqa: E402
    _clear_existing_slides,
    _find_blank_layout,
    _strip_layout_placeholders,
)


# ---------------------------------------------------------------------------
# Per-option render-QC self-check
# ---------------------------------------------------------------------------
_SRGB_RE = re.compile(r'srgbClr\s+val="([0-9A-Fa-f]{6})"')

_PLACEHOLDER_PATTERNS = (
    "Click to add",
    "Lorem ipsum",
    "Proceed with Option B",
)
# Intentional twin slot markers — never flag these as leaks.
_PLACEHOLDER_ALLOWED = (
    "[add footnote here or delete]",
    "[add source here or delete]",
)
_FOOTNOTE_NAME_PREFIXES = ("footnote", "source", "page-number")
_FOOTER_NUM_RE = re.compile(r"^\d+$")
_BODY_FONT_FLOOR_PT = 10.5


def _expected_palette_for_theme(theme) -> set:
    """Build the allowlist of hex codes for palette compliance.

    Includes every value the theme's color_map emits, the 10 raw theme attrs
    (dk1/lt1/dk2/lt2/accent1-6), and FFFFFF / 000000. All uppercase, no '#'.
    """
    palette: set = set()
    try:
        for v in theme.color_map().values():
            if isinstance(v, str) and len(v) == 6:
                palette.add(v.upper())
    except Exception:
        pass
    for attr in ("dk1", "lt1", "dk2", "lt2",
                 "accent1", "accent2", "accent3", "accent4", "accent5", "accent6"):
        v = getattr(theme, attr, None)
        if isinstance(v, str) and len(v) == 6:
            palette.add(v.upper())
    palette.add("FFFFFF")
    palette.add("000000")
    return palette


def _hex_codes_in_pptx(path: Path) -> set:
    """Extract every srgbClr val=... hex from every slide XML in a .pptx."""
    hexes: set = set()
    try:
        with zipfile.ZipFile(str(path), "r") as zf:
            for name in zf.namelist():
                if name.startswith("ppt/slides/") and name.endswith(".xml"):
                    try:
                        data = zf.read(name).decode("utf-8", errors="ignore")
                    except Exception:
                        continue
                    for m in _SRGB_RE.finditer(data):
                        hexes.add(m.group(1).upper())
    except Exception:
        pass
    return hexes


def _is_footnote_like_name(name: str) -> bool:
    n = (name or "").strip().lower()
    return any(n.startswith(p) for p in _FOOTNOTE_NAME_PREFIXES)


def run_option_qc(themed_pptx_path: Path, png_path: Path, expected_palette: set) -> dict:
    """Run 7 deterministic checks on a themed option. Return a dict with
    a list of per-check results + a summary count by severity."""
    checks: list = []

    # --- 1. png_render_ok ---
    png_ok = False
    png_detail = ""
    if not png_path.exists():
        png_detail = "PNG not found"
    else:
        try:
            sz = png_path.stat().st_size
            if sz <= 50 * 1024:
                png_detail = f"PNG too small ({sz} bytes; floor 50KB)"
            else:
                png_ok = True
                png_detail = f"{sz} bytes"
        except Exception as e:
            png_detail = f"stat failed: {e}"
    checks.append({
        "check": "png_render_ok",
        "pass": png_ok,
        "severity": "block",
        "detail": png_detail,
    })

    # --- 2. palette_compliance ---
    hexes = _hex_codes_in_pptx(themed_pptx_path)
    orphans = sorted(h for h in hexes if h not in expected_palette)
    if not orphans:
        pal_detail = f"all {len(hexes)} hex codes in palette"
        pal_ok = True
    else:
        sample = ", ".join(orphans[:8])
        more = "" if len(orphans) <= 8 else f" (+{len(orphans) - 8} more)"
        pal_detail = f"{len(orphans)} off-palette: {sample}{more}"
        pal_ok = False
    checks.append({
        "check": "palette_compliance",
        "pass": pal_ok,
        "severity": "warn",
        "detail": pal_detail,
    })

    # Walk the PPTX for the remaining shape/run-level checks.
    title_ok = False
    title_detail = ""
    footer_ok = False
    footer_detail = ""
    body_ok = True
    body_offenders: list = []
    leak_ok = True
    leak_offenders: list = []
    shape_count = 0
    shape_count_ok = False
    shape_count_detail = ""
    open_err = ""
    try:
        prs = Presentation(str(themed_pptx_path))
        slide = prs.slides[0]
        shapes = list(slide.shapes)
        shape_count = len(shapes)

        title_threshold = Pt(28)
        for shape in shapes:
            name = ""
            try:
                name = (shape.name or "").strip()
            except Exception:
                pass
            name_lower = name.lower()

            if not title_ok and name_lower.startswith("title"):
                title_ok = True
                title_detail = f"shape name '{name}' matches title*"

            if not footer_ok and name_lower == "page-number":
                footer_ok = True
                footer_detail = f"shape name '{name}' matches page-number"

            if not shape.has_text_frame:
                continue
            is_footnote_like = _is_footnote_like_name(name)
            tf = shape.text_frame
            try:
                shape_text = (tf.text or "").strip()
            except Exception:
                shape_text = ""
            if not footer_ok and shape_text and _FOOTER_NUM_RE.match(shape_text):
                footer_ok = True
                footer_detail = f"shape text '{shape_text}' is a page-number"

            for para in tf.paragraphs:
                for run in para.runs:
                    text = run.text or ""
                    sz = None
                    try:
                        sz = run.font.size
                    except Exception:
                        sz = None

                    if not title_ok and sz is not None and sz > title_threshold:
                        title_ok = True
                        title_detail = (
                            f"run > 28pt found (name='{name}', size={sz.pt:.1f}pt)"
                        )

                    if body_ok and not is_footnote_like:
                        if sz is not None and sz.pt < _BODY_FONT_FLOOR_PT:
                            body_ok = False
                            body_offenders.append(
                                f"{name or '<unnamed>'} @ {sz.pt:.1f}pt: {text[:40]!r}"
                            )

                    if text:
                        if not any(allowed in text for allowed in _PLACEHOLDER_ALLOWED):
                            for pat in _PLACEHOLDER_PATTERNS:
                                if pat in text:
                                    leak_ok = False
                                    leak_offenders.append(
                                        f"'{pat}' in {name or '<unnamed>'}: {text[:60]!r}"
                                    )
                                    break

        if 5 <= shape_count <= 80:
            shape_count_ok = True
            shape_count_detail = f"{shape_count} shapes"
        else:
            shape_count_detail = f"{shape_count} shapes (expected 5..80)"

    except Exception as e:
        open_err = f"{type(e).__name__}: {e}"

    if open_err:
        title_detail = title_detail or f"could not open: {open_err}"
        footer_detail = footer_detail or f"could not open: {open_err}"
        shape_count_detail = shape_count_detail or f"could not open: {open_err}"

    if not title_detail:
        title_detail = "no title* shape and no run > 28pt"
    if not footer_detail:
        footer_detail = "no shape named page-number and no bare-integer text"

    checks.append({
        "check": "title_present",
        "pass": title_ok,
        "severity": "warn",
        "detail": title_detail,
    })
    checks.append({
        "check": "footer_present",
        "pass": footer_ok,
        "severity": "warn",
        "detail": footer_detail,
    })
    checks.append({
        "check": "body_font_floor",
        "pass": body_ok,
        "severity": "warn",
        "detail": (
            "all runs >= 10.5pt (excluding footnote/source/page-number)"
            if body_ok
            else f"{len(body_offenders)} sub-floor runs: "
            + "; ".join(body_offenders[:4])
            + ("" if len(body_offenders) <= 4 else f" (+{len(body_offenders) - 4} more)")
        ),
    })
    checks.append({
        "check": "placeholder_leak",
        "pass": leak_ok,
        "severity": "block",
        "detail": (
            "no placeholder strings found"
            if leak_ok
            else f"{len(leak_offenders)} leak(s): "
            + "; ".join(leak_offenders[:3])
            + ("" if len(leak_offenders) <= 3 else f" (+{len(leak_offenders) - 3} more)")
        ),
    })
    checks.append({
        "check": "shape_count_sanity",
        "pass": shape_count_ok,
        "severity": "warn",
        "detail": shape_count_detail,
    })

    summary = {"pass": 0, "warn": 0, "block": 0}
    for c in checks:
        if c["pass"]:
            summary["pass"] += 1
        elif c["severity"] == "block":
            summary["block"] += 1
        else:
            summary["warn"] += 1

    return {"checks": checks, "summary": summary}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class OptionStatus:
    slide_n: int
    letter: str
    py_path: Path
    pptx_path: Path
    themed_pptx_path: Path
    themed_png_path: Path
    built: Optional[bool] = None
    themed: Optional[bool] = None
    rendered: Optional[bool] = None
    n_shapes: int = 0
    n_subs: int = 0
    error: str = ""


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------
def discover_options(out_dir: Path) -> list:
    """Find every <out>/slide_NN/option_X.py and create a status row."""
    statuses: list = []
    for py in sorted(out_dir.glob("slide_*/option_*.py")):
        slide_n = int(py.parent.name.split("_")[1])
        letter = py.stem.split("_")[1]
        themed_dir = out_dir / "themed" / py.parent.name
        statuses.append(OptionStatus(
            slide_n=slide_n,
            letter=letter,
            py_path=py,
            pptx_path=py.with_suffix(".pptx"),
            themed_pptx_path=themed_dir / f"option_{letter}.pptx",
            themed_png_path=themed_dir / f"option_{letter}.png",
        ))
    return statuses


# ---------------------------------------------------------------------------
# Step 1: execute option_X.py -> option_X.pptx
# ---------------------------------------------------------------------------
def _run_subprocess(st: OptionStatus):
    """Try executing the .py via subprocess. Returns (ok, error)."""
    try:
        result = subprocess.run(
            [sys.executable, str(st.py_path)],
            capture_output=True, text=True, timeout=120,
            cwd=str(st.py_path.parent),
        )
        if result.returncode != 0:
            return False, (result.stderr or result.stdout or "non-zero exit")[-400:]
        if not st.pptx_path.exists():
            return False, "script ran but no .pptx produced"
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "timeout (120s)"
    except Exception as e:
        return False, f"subprocess: {type(e).__name__}: {e}"


def _run_runpy(st: OptionStatus):
    """Fall-back: execute the .py in-process via runpy. Slower module-state risk
    is acceptable because each .py is self-contained and importable side-effect free."""
    saved_cwd = os.getcwd()
    saved_argv = sys.argv[:]
    try:
        os.chdir(str(st.py_path.parent))
        sys.argv = [str(st.py_path)]
        runpy.run_path(str(st.py_path), run_name="__main__")
        if not st.pptx_path.exists():
            return False, "runpy: script ran but no .pptx produced"
        return True, ""
    except SystemExit as e:
        if e.code in (0, None) and st.pptx_path.exists():
            return True, ""
        return False, f"runpy SystemExit({e.code})"
    except Exception as e:
        tb_last = traceback.format_exc().strip().splitlines()[-1] if traceback else ""
        return False, f"runpy: {type(e).__name__}: {e} | {tb_last}"
    finally:
        os.chdir(saved_cwd)
        sys.argv = saved_argv


def build_pptx(st: OptionStatus, prefer_runpy: bool = False) -> None:
    """Execute the .py to produce a .pptx. Tries subprocess first (clean isolation),
    falls back to runpy if subprocess is blocked by the host (e.g. sandboxed envs)."""
    if st.pptx_path.exists():
        try:
            st.pptx_path.unlink()
        except Exception:
            pass

    if not prefer_runpy:
        ok, err = _run_subprocess(st)
        if ok:
            st.built = True
            return
        sandbox_signals = ("WinError 5", "Access is denied", "PermissionError")
        if not any(sig in err for sig in sandbox_signals):
            st.built = False
            st.error = err
            return

    ok, err = _run_runpy(st)
    if ok:
        st.built = True
    else:
        st.built = False
        st.error = err


# ---------------------------------------------------------------------------
# Step 2: graft + theme remap
# ---------------------------------------------------------------------------
def graft_and_theme(st: OptionStatus, template_path: Path, theme, color_map) -> None:
    try:
        src_prs = Presentation(str(st.pptx_path))
        src_slide = src_prs.slides[0]
        st.n_shapes = len(src_slide.shapes)

        prs = Presentation(str(template_path))
        _clear_existing_slides(prs)
        blank = _find_blank_layout(prs)
        new_slide = prs.slides.add_slide(blank)
        _strip_layout_placeholders(new_slide)

        sp_tree = new_slide.shapes._spTree
        for shape in src_slide.shapes:
            sp_tree.append(deepcopy(shape.element))

        subs = 0
        for shape in new_slide.shapes:
            subs += apply_theme_to_shape_xml(
                shape.element, color_map,
                major_font=theme.major_font, minor_font=theme.minor_font,
            )
        st.n_subs = subs

        st.themed_pptx_path.parent.mkdir(parents=True, exist_ok=True)
        prs.save(str(st.themed_pptx_path))
        st.themed = True
    except Exception as e:
        st.themed = False
        st.error = f"graft: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Step 3: render to PNG
# ---------------------------------------------------------------------------
def render_one(st: OptionStatus) -> OptionStatus:
    from render_slides import render_libre  # imported here so failures localized
    pptx = st.themed_pptx_path
    tmp = pptx.parent / "_render_tmp" / pptx.stem
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        render_libre(pptx, tmp, dpi=120)
        src_png = tmp / "slide_01.png"
        if src_png.exists():
            src_png.replace(st.themed_png_path)
            st.rendered = True
        else:
            st.rendered = False
            st.error = "render: no png produced"
    except Exception as e:
        st.rendered = False
        st.error = f"render: {type(e).__name__}: {e}"
    return st


# ---------------------------------------------------------------------------
# Step 4: RESULT.md
# ---------------------------------------------------------------------------
RESULT_TEMPLATE = """# Slide Lab deck — finalize result

Generated: {ts}

Out: `{out}`
Template: `{template}`

## Counts

- Built (.py -> .pptx): **{built_ok} / {total}**
- Themed (graft + remap): **{themed_ok} / {total}**
- Rendered (.png): **{rendered_ok} / {total}**

## Per-option status

| Slide | Option | Built | Themed | Rendered | Shapes | Subs | Error |
|-------|--------|-------|--------|----------|--------|------|-------|
{rows}

## Outputs

- Source PPTX (Slide-Lab palette): `<out>/slide_NN/option_X.pptx`
- Themed PPTX (client palette): `<out>/themed/slide_NN/option_X.pptx`
- PNG thumbnails: `<out>/themed/slide_NN/option_X.png`
- QC self-check: `<out>/themed/slide_NN/option_X.qc.json`

## Failures

{failures}
"""


def _mark(ok):
    if ok is True:
        return "ok"
    if ok is False:
        return "FAIL"
    return "-"


def write_result(out_dir: Path, template_path: Path, statuses: list) -> Path:
    rows = []
    for st in statuses:
        rows.append(
            f"| {st.slide_n:>2} | {st.letter} | {_mark(st.built)} | {_mark(st.themed)} "
            f"| {_mark(st.rendered)} | {st.n_shapes} | {st.n_subs} | "
            f"{(st.error[:80] + '...') if len(st.error) > 80 else st.error} |"
        )

    failures = [
        f"- **slide {st.slide_n:02d} option {st.letter}**: {st.error}"
        for st in statuses if st.error
    ]

    total = len(statuses)
    content = RESULT_TEMPLATE.format(
        ts=datetime.now().isoformat(timespec="seconds"),
        out=out_dir,
        template=template_path,
        total=total,
        built_ok=sum(1 for s in statuses if s.built),
        themed_ok=sum(1 for s in statuses if s.themed),
        rendered_ok=sum(1 for s in statuses if s.rendered),
        rows="\n".join(rows) if rows else "| (no options found) |",
        failures="\n".join(failures) if failures else "(none)",
    )
    target = out_dir / "RESULT.md"
    target.write_text(content, encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Slide Lab deck orchestrator — Part B (finalize)")
    ap.add_argument("--out", required=True, type=Path, help="Output dir from Part A")
    ap.add_argument("--template", required=True, type=Path, help="Client PPTX template")
    ap.add_argument("--skip-build", action="store_true", help="Skip executing option_X.py")
    ap.add_argument("--skip-render", action="store_true", help="Skip PNG rendering")
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")

    if not args.out.exists():
        print(f"ERROR: out dir not found: {args.out}")
        return 2
    if not args.template.exists():
        print(f"ERROR: template not found: {args.template}")
        return 2

    print("=" * 72)
    print("Slide Lab deck orchestrator — Part B (finalize)")
    print(f"  out      : {args.out}")
    print(f"  template : {args.template}")
    print("=" * 72)

    print("\n[1] Discover option_X.py files")
    statuses = discover_options(args.out)
    print(f"  found {len(statuses)} option scripts across "
          f"{len({s.slide_n for s in statuses})} slides")
    if not statuses:
        print("  nothing to do.")
        write_result(args.out, args.template, statuses)
        return 0

    print("\n[2] Execute option_X.py -> option_X.pptx (serial, subprocess-isolated)")
    for i, st in enumerate(statuses, 1):
        if args.skip_build and st.pptx_path.exists():
            st.built = True
            print(f"  [{i:>3}/{len(statuses)}] slide_{st.slide_n:02d}/option_{st.letter}  skip-build (exists)")
            continue
        build_pptx(st)
        flag = "ok" if st.built else f"FAIL ({st.error[:50]})"
        print(f"  [{i:>3}/{len(statuses)}] slide_{st.slide_n:02d}/option_{st.letter}  {flag}")

    built_statuses = [s for s in statuses if s.built]
    print(f"  built: {len(built_statuses)} / {len(statuses)}")

    print("\n[3] Load client theme")
    theme = load_client_theme(str(args.template))
    color_map = theme.color_map()
    expected_palette = _expected_palette_for_theme(theme)
    print(f"  dk2={theme.dk2}  lt2={theme.lt2}  font={theme.minor_font}")
    print(f"  color_map entries: {len(color_map)}")
    print(f"  expected palette  : {len(expected_palette)} hex codes")

    print("\n[4] Graft + theme remap (serial — python-pptx not thread-safe)")
    for i, st in enumerate(built_statuses, 1):
        graft_and_theme(st, args.template, theme, color_map)
        flag = f"ok (shapes={st.n_shapes} subs={st.n_subs})" if st.themed else f"FAIL ({st.error[:50]})"
        print(f"  [{i:>3}/{len(built_statuses)}] slide_{st.slide_n:02d}/option_{st.letter}  {flag}")

    themed_statuses = [s for s in built_statuses if s.themed]
    print(f"  themed: {len(themed_statuses)} / {len(built_statuses)}")

    if not args.skip_render:
        print(f"\n[5] Render themed .pptx -> .png (parallel x4)")
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(render_one, st): st for st in themed_statuses}
            done = 0
            for fut in as_completed(futures):
                st = fut.result()
                done += 1
                flag = "ok" if st.rendered else f"FAIL ({st.error[:50]})"
                print(f"  [{done:>3}/{len(themed_statuses)}] slide_{st.slide_n:02d}/option_{st.letter}  {flag}")

        for tmp in (args.out / "themed").glob("slide_*/_render_tmp"):
            shutil.rmtree(tmp, ignore_errors=True)
    else:
        print("\n[5] Render skipped (--skip-render)")

    # ----- Step 5.5: per-option QC self-check -----
    print("\n[5b] Per-option QC self-check (palette / title / footer / fonts / leaks)")
    qc_counts = {"all_ok": 0, "warn_only": 0, "block": 0}
    for st in themed_statuses:
        try:
            result = run_option_qc(st.themed_pptx_path, st.themed_png_path, expected_palette)
            qc_path = st.themed_pptx_path.with_suffix("")
            qc_path = qc_path.parent / (qc_path.name + ".qc.json")
            qc_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
            summ = result["summary"]
            if summ["block"] > 0:
                qc_counts["block"] += 1
                flag = f"BLOCK ({summ['block']}b/{summ['warn']}w)"
            elif summ["warn"] > 0:
                qc_counts["warn_only"] += 1
                flag = f"warn ({summ['warn']}w)"
            else:
                qc_counts["all_ok"] += 1
                flag = "ok"
            print(f"  slide_{st.slide_n:02d}/option_{st.letter}  {flag}")
        except Exception as e:
            print(f"  slide_{st.slide_n:02d}/option_{st.letter}  qc-FAIL ({type(e).__name__}: {e})")
    print(f"  QC totals: all-ok={qc_counts['all_ok']}  warn-only={qc_counts['warn_only']}  block={qc_counts['block']}")

    print("\n[6] Write RESULT.md")
    result_path = write_result(args.out, args.template, statuses)
    print(f"  {result_path}")

    print("\n" + "=" * 72)
    print("DONE — Part B complete.")
    print(f"  Built   : {sum(1 for s in statuses if s.built)} / {len(statuses)}")
    print(f"  Themed  : {sum(1 for s in statuses if s.themed)} / {len(statuses)}")
    print(f"  Rendered: {sum(1 for s in statuses if s.rendered)} / {len(statuses)}")
    print(f"  Report  : {result_path}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())