#!/usr/bin/env python3
"""Smoke test: a slide's last field stops at the slide divider.

storyline-helper ends each slide block with **Chart type:** (and sometimes
**Chart data:**), then a `---` divider; the last slide is followed by the
brief's Flags section. The field reader used to run past the divider, so
"none" came back as "none\\n\\n---" (and, on the last slide, with the Flags
text attached), never matched, and every slide was forecast as a chart.

Run:  py -3 slide-builder/tests/run_brief_parse_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import build_deck as b  # noqa: E402

BLOCK_1 = """### Slide 1 — Market doubles by 2030

**Governing thought (the claim):** The market doubles by 2030.

**Chart type:** bar

**Chart data:**

| Year | $B |
|---|---|
| 2024 | 2.1 |
| 2030 | 4.2 |

Callout on the 2030 bar.

---
"""

BLOCK_2 = """### Slide 2 — Approve the funding

**Governing thought (the claim):** Approve $12M by November.

**What this slide is NOT:** Not a recap.

**Chart type:** none

---

## Flags — live issues, not historical notes
- **Issue:** something the reader must not see in a field.
"""


def main() -> int:
    v = b.extract_field(BLOCK_2, b.FIELD_LABELS["chart_type"])
    assert v == "none", repr(v)
    v = b.extract_field(BLOCK_2, b.FIELD_LABELS["not_this_slide"])
    assert v == "Not a recap.", repr(v)
    data = b.extract_field(BLOCK_1, b.FIELD_LABELS["chart_data"])
    assert "|---|---|" in data and data.rstrip().endswith("Callout on the 2030 bar."), repr(data)
    assert b.extract_field(BLOCK_1, b.FIELD_LABELS["chart_type"]) == "bar"
    assert b.forecast_pattern({"chart_type": "none", "title": "Approve"}) != b.PATTERNS["chart"]
    print("    ok: last field stops at the divider; table rows inside chart data kept")
    print("SMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
