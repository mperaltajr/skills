"""
Render themed thumbnails of pattern twins.

When the user is building a deck for FedEx (or any client), the preview
thumbnails should already be in the client's brand — not generic Accenture
purple. This module composes single-slide PPTX files for each candidate
pattern on the chosen client template, applies the client theme (colors +
fonts), renders to PNG, and caches by (pattern, template_name) so repeat
reviews are instant.

Cache layout:
  _renders/twins/_pngs_themed/<template_stem>/<pattern_stem>/slide_01.png

Usage:
  from twins.themed_thumbnails import ensure_themed_thumbnail
  png = ensure_themed_thumbnail(
      pattern="01_anchor-with-cards-icons",
      client_template=r"C:\path\to\Moving Forward PPT Template.pptx",
      overrides={"title": "...", "card-1-heading": "..."},
  )
  # → Path to themed PNG, rendered on demand if missing

If `overrides` is None, the pattern's default placeholder text is kept.
Passing overrides re-renders (because the content is different), so the
cache key for content-rendered thumbnails includes a content hash.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from twins.composer import compose_deck
from twins.selector import pattern_to_pptx_stem


PNG_THEMED_ROOT = Path(__file__).resolve().parent.parent / "_renders" / "twins" / "_pngs_themed"


def _content_hash(overrides: Optional[Dict[str, Any]]) -> str:
    """Stable short hash of the overrides dict, or '' if none."""
    if not overrides:
        return ""
    blob = json.dumps(overrides, sort_keys=True, default=str)
    return "_" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:10]


def ensure_themed_thumbnail(pattern: str, client_template: str,
                             overrides: Optional[Dict[str, Any]] = None,
                             dpi: int = 100, force: bool = False,
                             return_qc: bool = False):
    """Return the themed thumbnail PNG path. Renders on demand if missing.

    Returns None if the underlying twin PPTX doesn't exist or rendering fails.

    When `return_qc=True`, returns a tuple (png_path, qc_dict) where qc_dict
    is the render_qc.check_composed_pptx result for the composed PPTX (verdict
    + issues). Callers in the REVIEW.html flow use this to attach per-option
    QC badges in the picker.
    """
    pattern_on_disk = pattern_to_pptx_stem(pattern)
    template_stem = Path(client_template).stem

    cache_dir = PNG_THEMED_ROOT / template_stem / (pattern_on_disk + _content_hash(overrides))
    png = cache_dir / "slide_01.png"
    cached_pptx = cache_dir / "_thumbnail.pptx"

    def _maybe_qc(result):
        if not return_qc:
            return result
        if result is None:
            return (None, {"verdict": "critical", "issues": [{"severity": "critical", "msg": "render failed"}]})
        try:
            from twins.render_qc import check_composed_pptx
            qc = check_composed_pptx(str(cached_pptx)) if cached_pptx.exists() else \
                 {"verdict": "clean", "issues": []}
        except Exception as e:
            qc = {"verdict": "warning", "issues": [{"severity": "warning", "msg": f"qc error: {e}"}]}
        return (result, qc)

    if png.exists() and not force:
        return _maybe_qc(png)

    # Compose a single-slide PPTX from this pattern on the client template.
    tmp_pptx = cache_dir / "_thumbnail.pptx"
    cache_dir.mkdir(parents=True, exist_ok=True)
    try:
        compose_deck(
            out_path=str(tmp_pptx),
            slides=[{"pattern": pattern_on_disk, "overrides": overrides or {}}],
            client_template=client_template,
            verbose=False,
        )
    except FileNotFoundError:
        return _maybe_qc(None)
    except Exception as e:
        print(f"  themed-thumbnail compose error for {pattern}: {e}", file=sys.stderr)
        return _maybe_qc(None)

    # Render to PNG via LibreOffice with retries on failure. LibreOffice
    # headless + pypdfium2 occasionally crash under concurrent load; the
    # pdfium lock in render_slides.py covers the in-process race, and we
    # retry up to 3x with exponential backoff to cover transient LO crashes
    # and Windows OS-level resource contention.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slide-qc" / "scripts"))
    try:
        from render_slides import render_libre
    except Exception as e:
        print(f"  themed-thumbnail render import error for {pattern}: {e}", file=sys.stderr)
        return _maybe_qc(None)

    last_err = None
    backoffs = [0.5, 2.0, 6.0]
    for attempt, backoff in enumerate(backoffs, 1):
        try:
            render_libre(tmp_pptx, cache_dir, dpi=dpi)
            if png.exists():
                return _maybe_qc(png)
        except Exception as e:
            last_err = e
            print(
                f"  themed-thumbnail render attempt {attempt}/{len(backoffs)} "
                f"failed for {pattern}: {type(e).__name__}: {e}",
                file=sys.stderr,
            )
        if attempt < len(backoffs):
            import time
            time.sleep(backoff)

    print(
        f"  themed-thumbnail render FINAL fail for {pattern} after "
        f"{len(backoffs)} attempts: {last_err}",
        file=sys.stderr,
    )
    return _maybe_qc(None)


def batch_render(patterns: list, client_template: str, dpi: int = 100,
                 overrides_per_pattern: Optional[Dict[str, Dict[str, Any]]] = None,
                 workers: int = 6) -> Dict[str, Optional[Path]]:
    """Render themed thumbnails for a list of patterns on a single template.

    Parallelized with `workers` concurrent processes (LibreOffice instances each
    spawn their own isolated user profile, so they don't fight).

    Returns dict mapping pattern stem -> PNG path (or None on failure).
    """
    from concurrent.futures import ProcessPoolExecutor, as_completed
    overrides_per_pattern = overrides_per_pattern or {}
    # Deduplicate jobs by (pattern, content_hash) — content-identical entries
    # share a render.
    jobs = []
    seen = set()
    for p in patterns:
        ov = overrides_per_pattern.get(p)
        key = (p, _content_hash(ov))
        if key in seen:
            continue
        seen.add(key)
        jobs.append((p, ov))

    out: Dict[str, Optional[Path]] = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_render_one, p, client_template, ov, dpi): p
            for p, ov in jobs
        }
        done = 0
        total = len(futures)
        for fut in as_completed(futures):
            pat = futures[fut]
            try:
                out[pat] = fut.result()
            except Exception as e:
                out[pat] = None
                print(f"  worker error for {pat}: {e}")
            done += 1
            if done % 3 == 0 or done == total:
                print(f"  {done}/{total} themed thumbnails")
    return out


def _render_one(pattern: str, client_template: str, overrides: Optional[Dict[str, Any]], dpi: int):
    """Worker entrypoint — runs in a subprocess (or thread) so multiple LO
    instances coexist. Returns just the PNG path (legacy callers expect that).
    """
    return ensure_themed_thumbnail(pattern, client_template, overrides=overrides, dpi=dpi)


def _render_one_with_qc(pattern: str, client_template: str,
                         overrides: Optional[Dict[str, Any]], dpi: int):
    """Variant of _render_one that also returns a render-QC verdict per option
    via render_qc.check_composed_pptx. Used by the REVIEW.html pipeline so
    each option gets a clean/warning/critical badge.
    """
    return ensure_themed_thumbnail(pattern, client_template, overrides=overrides,
                                    dpi=dpi, return_qc=True)


if __name__ == "__main__":
    # Smoke test — usage: python -m twins.themed_thumbnails <client-template.pptx>
    import sys as _sys
    if len(_sys.argv) < 2:
        print("Usage: python -m twins.themed_thumbnails <path-to-client-template.pptx>")
        _sys.exit(1)
    template = _sys.argv[1]
    test_patterns = ["01_anchor-with-cards-icons", "02_three-pillars-icons-outputs", "38_statement-hero-text"]
    for p in test_patterns:
        png = ensure_themed_thumbnail(p, template)
        print(f"{p}: {png}")
