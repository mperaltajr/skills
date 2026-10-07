"""_e2e_harness.py — drive the real pipeline on the bundled test template.

Shared by the end-to-end smokes. Every other smoke calls a script's functions
with hand-built state; this runs the scripts themselves (prep, a worker-shaped
option script per slide, finalize, review, compile), so a change to how the
stages talk to each other is exercised the way a real build exercises it.

Nothing here is a production path. It stands in for the worker agent with a
deliberately plain slide so the test is about the plumbing, not the design.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCRIPTS = SKILL / "scripts"
TEMPLATE = HERE / "fixtures" / "layout_diverse_template.pptx"

BRIEF = """---
deck_type: client-pitch
audience: "Test audience"
governing_thought: "The test deck proves the pipeline records what really happened."
storyline_gate_passed: true
default_layout: body_canonical_light
---

# Pipeline test

## Governing thought (the whole deck)
The test deck proves the pipeline records what really happened.
{slides}"""

SLIDE = """
### Slide {n} — Claim number {n} is stated plainly here

**Slide type:** Content
**Governing thought (the claim):** Claim number {n} is stated plainly here.
**The takeaway:** Takeaway {n}.
**Evidence / content:**
- Point one for slide {n}
- Point two for slide {n}
- Point three for slide {n}
"""

OPTION_SCRIPT = '''# Slide {n} option {L} — pattern: text column (test harness)
# Variant: plain
# Brief fidelity check: test fixture
import sys
from pathlib import Path
sys.path.insert(0, r"{skill}")
from twins.helpers import new_slide, add_text


def build():
    prs, slide = new_slide()
    add_text(slide, "body", "Point one\\nPoint two\\nPoint three",
             80, 260, 700, 200, font_size_pt=18)
    return prs


if __name__ == "__main__":
    prs = build()
    prs.save(str(Path(__file__).resolve().parent / "option_{L}.pptx"))
'''


def env(**extra) -> dict:
    e = {**os.environ, "PYTHONIOENCODING": "utf-8",
         "SLIDE_LAB_OPTIONS_PER_SLIDE": "1",
         "SLIDE_LAB_NO_OPEN": "1",
         # Never let a test write into the user's real template pick-list.
         "SLIDE_LAB_REGISTRY": str(Path(tempfile.gettempdir()) / "slidelab_test_registry.json")}
    e.update({k: str(v) for k, v in extra.items()})
    return e


def run(script: str, *args, **env_extra) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True, env=env(**env_extra),
                          encoding="utf-8", errors="replace")


def new_build(n_slides: int = 2) -> tuple[Path, Path]:
    """Prep a build. Returns (tmp_root, out_dir)."""
    tmp = Path(tempfile.mkdtemp(prefix="slidelab_e2e_"))
    brief = tmp / "brief.md"
    brief.write_text(BRIEF.format(slides="".join(
        SLIDE.format(n=i) for i in range(1, n_slides + 1))), encoding="utf-8")
    # The gate passed (this is a test brief); seal it the way storyline-helper does.
    r = run("seal_brief.py", "--brief", brief, "--accepted", "test brief")
    assert r.returncode == 0, r.stdout + r.stderr
    out = tmp / "out"
    r = run("build_deck.py", "--brief", brief, "--template", TEMPLATE,
            "--out", out, "--pattern", "direct", "--confirm-template")
    assert r.returncode == 0, f"prep failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    return tmp, out


def write_option(out: Path, n: int, letter: str = "A", body: str | None = None) -> Path:
    """Stand in for the worker: write one option script for slide n."""
    p = out / f"slide_{n:02d}" / f"option_{letter}.py"
    p.write_text(body if body is not None else
                 OPTION_SCRIPT.format(n=n, L=letter, skill=str(SKILL)),
                 encoding="utf-8")
    return p


SKETCH_WITH_FALLBACK = (
    '<html><body style="margin:0"><div class="slide-canvas" style="position:relative;'
    'width:1280px;height:720px;font-family:Arial">'
    '<div data-shape-id="box" style="position:absolute;left:100px;top:220px;width:300px;'
    'height:120px;background:#1f4e79"></div>'
    '<p data-shape-id="note" style="position:absolute;left:100px;top:380px;margin:0;'
    'font-size:16px">{text}</p>'
    # rotated text: the script cannot draw it, so it goes to the translator agent
    '<div data-shape-id="tag" style="position:absolute;left:700px;top:300px;'
    'transform:rotate(-20deg);font-size:16px">Rotated tag</div>'
    '</div></body></html>')

AGENT_BLOCK = (
    "    from pptx.util import Emu\n"
    "    from pptx.enum.shapes import MSO_SHAPE\n"
    "    _m = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(700 * 9525), Emu(290 * 9525),\n"
    "                                Emu(140 * 9525), Emu(40 * 9525))\n"
    "    _m.name = \"agent-drawn-mark\"\n")


def write_sketch(out: Path, n: int, letter: str = "A", text: str = "A short note.") -> Path:
    """Stand in for a sketch-path worker: a design with one element only the
    translator agent can draw."""
    p = out / f"slide_{n:02d}" / f"option_{letter}.html"
    p.write_text(SKETCH_WITH_FALLBACK.format(text=text), encoding="utf-8")
    return p


def agent_finishes(native_py: Path) -> str:
    """Stand in for slide-builder-translator in FALLBACK MODE: draw between the
    markers and mark the script done. Returns the finished script text."""
    import re
    src = native_py.read_text(encoding="utf-8")
    assert "# FALLBACK_PENDING:" in src, "nothing was waiting on the agent"
    src = re.sub(r"^# FALLBACK_PENDING:.*$", "# FALLBACK_DONE: drew the rotated tag",
                 src, count=1, flags=re.M)
    src = src.replace("    # (none)\n", AGENT_BLOCK, 1)
    native_py.write_text(src, encoding="utf-8")
    return src


def finalize(out: Path, *extra) -> subprocess.CompletedProcess:
    return run("finalize_deck.py", "--out", out, "--template", TEMPLATE, *extra)


def cleanup(tmp: Path) -> None:
    shutil.rmtree(tmp, ignore_errors=True)
