#!/usr/bin/env python3
"""
render_mermaid.py — Mermaid CLI wrapper for the v2 fallback path.

Renders a .mmd Mermaid spec to a PNG via mmdc (the Mermaid CLI), with a brand
theme override so the output matches the deck's brand colors.

Used by the fallback path for the four v0-supported curved-container diagrams
(hub-spoke, Porter's Five Forces, ecosystem map, free-form network). Fishbone
and concentric rings are SKELETON_REJECTED in v0 — see reference/fallback.md.

The per-slide agent writes the .mmd file; finalize_deck.py invokes this
script; the PNG gets embedded in the slide body zone.

Prerequisites:
    Tested with mmdc 11.4.0. Install the pinned version:
        npm install -g @mermaid-js/mermaid-cli@11.4.0

    Verify:
        mmdc --version
        # Expected: 11.4.0

    If mmdc reports a different major version, output may differ. Revisit
    the pin in v0.1 if a newer version offers material improvements.

Render dimensions:
    Defaults to 1240x540 (body zone size). The slide body zone occupies
    y~110 to y~650 inside the 1280x720 canvas (title block at top, footer
    at bottom). Rendering at body-zone size avoids scaling artifacts when
    finalize_deck.py embeds the PNG.

Invocation:
    py -3 render_mermaid.py \\
        --input  <path-to-option_X.mmd> \\
        --output <path-to-option_X-mermaid.png> \\
        --theme  <path-to-theme.json> \\
        --width  1240 \\
        --height 540

Note for finalize_deck.py callers: invoke this script via sys.executable,
not the literal string "py -3". On non-Windows runners the launcher is
absent; sys.executable is the cross-platform handle for the current Python.

Exit codes:
    0  Success — output PNG produced and non-empty.
    1  mmdc not installed or not on PATH.
    2  Input .mmd file missing or empty.
    3  Theme file missing.
    4  mmdc invocation failed (syntax error in .mmd, etc.).
    5  Output file not produced or zero bytes.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _find_mmdc() -> str | None:
    """Locate the mmdc executable.

    Checks PATH first, then common npm-global install locations on Windows.
    Returns the full path to mmdc (or mmdc.cmd on Windows) or None if missing.
    """
    mmdc = shutil.which("mmdc")
    if mmdc:
        return mmdc

    # Windows npm-global fallback locations
    if os.name == "nt":
        for candidate in [
            Path(os.environ.get("APPDATA", "")) / "npm" / "mmdc.cmd",
            Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Roaming" / "npm" / "mmdc.cmd",
            Path("C:/Program Files/nodejs/mmdc.cmd"),
        ]:
            if candidate.exists():
                return str(candidate)

    return None


def render(
    input_path: Path,
    output_path: Path,
    theme_path: Path,
    width: int = 1280,
    height: int = 720,
    background: str = "white",
    verbose: bool = False,
) -> int:
    """Render a Mermaid .mmd file to PNG via mmdc.

    Returns one of the exit codes documented in the module docstring.
    """
    # 1. Locate mmdc
    mmdc = _find_mmdc()
    if not mmdc:
        sys.stderr.write(
            "ERROR: mmdc (Mermaid CLI) not found on PATH.\n"
            "Install the pinned version with:\n"
            "    npm install -g @mermaid-js/mermaid-cli@11.4.0\n"
            "Verify with:\n"
            "    mmdc --version   # expected: 11.4.0\n"
        )
        return 1

    # 2. Validate input
    if not input_path.exists():
        sys.stderr.write(f"ERROR: input .mmd file does not exist: {input_path}\n")
        return 2
    if input_path.stat().st_size == 0:
        sys.stderr.write(f"ERROR: input .mmd file is empty: {input_path}\n")
        return 2

    # 3. Validate theme
    if not theme_path.exists():
        sys.stderr.write(f"ERROR: theme file does not exist: {theme_path}\n")
        return 3

    # 4. Ensure output dir exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 5. Build mmdc command
    cmd = [
        mmdc,
        "-i", str(input_path),
        "-o", str(output_path),
        "-c", str(theme_path),
        "-w", str(width),
        "-H", str(height),
        "-b", background,
    ]
    if verbose:
        cmd.append("--verbose")
        sys.stderr.write(f"Running: {' '.join(cmd)}\n")

    # 6. Invoke mmdc
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        sys.stderr.write(
            f"ERROR: mmdc timed out after 60 seconds rendering {input_path.name}\n"
        )
        return 4
    except FileNotFoundError as exc:
        sys.stderr.write(f"ERROR: failed to invoke mmdc — {exc}\n")
        return 1

    if result.returncode != 0:
        sys.stderr.write(
            f"ERROR: mmdc failed with exit code {result.returncode}\n"
            f"---- mmdc stderr ----\n{result.stderr}\n"
            f"---- mmdc stdout ----\n{result.stdout}\n"
        )
        return 4

    # 7. Verify output
    if not output_path.exists():
        sys.stderr.write(
            f"ERROR: mmdc reported success but output file is missing: {output_path}\n"
            f"Rerun with --verbose for full mmdc output.\n"
        )
        return 5
    if output_path.stat().st_size == 0:
        sys.stderr.write(
            f"ERROR: mmdc reported success but output file is empty: {output_path}\n"
        )
        return 5

    if verbose:
        sys.stderr.write(
            f"Rendered {input_path.name} -> {output_path.name} "
            f"({output_path.stat().st_size} bytes)\n"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render a Mermaid .mmd file to PNG with v2 brand theme.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to .mmd input file")
    parser.add_argument("--output", required=True, type=Path, help="Path to .png output file")
    parser.add_argument(
        "--theme",
        type=Path,
        required=True,
        help="Path to Mermaid config JSON (per-client brand theme). "
        "Required — no generic fallback exists. Pass the per-deck override "
        "written by build_deck.py from the client brand.yml.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1240,
        help="Output width in pixels (default: 1240 — body zone width with 20px padding)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=540,
        help="Output height in pixels (default: 540 — body zone height between title block and footer)",
    )
    parser.add_argument(
        "--background",
        default="white",
        help="Background color (default: white). 'transparent' also supported.",
    )
    parser.add_argument("--verbose", action="store_true", help="Print mmdc output and timing info")

    args = parser.parse_args()
    return render(
        input_path=args.input,
        output_path=args.output,
        theme_path=args.theme,
        width=args.width,
        height=args.height,
        background=args.background,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    sys.exit(main())
