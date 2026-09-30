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
         "SLIDE_LAB_OPTIONS_PER_SLIDE": "1"}
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


def finalize(out: Path, *extra) -> subprocess.CompletedProcess:
    return run("finalize_deck.py", "--out", out, "--template", TEMPLATE, *extra)


def cleanup(tmp: Path) -> None:
    shutil.rmtree(tmp, ignore_errors=True)
