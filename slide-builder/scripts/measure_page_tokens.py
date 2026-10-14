#!/usr/bin/env python3
"""measure_page_tokens.py: builder tokens and time per page, designed vs copied.

The measurement the owner approved on 2026-10-14 (speed verdict Q3, item 5)
for the next deck with sections: log tokens and wall time per page, split by
pages built from scratch and pages copied by script (clone_pages.py), in one
common token unit. Target: at least 20% fewer builder tokens than the same
deck with every page designed, and no new QC finding on the copied pages.

Common unit (same as the verdict): input x1, cache read x0.1, cache write
x1.25, output x5.

  py -3 scripts/measure_page_tokens.py --out <build> --transcripts <folder>

<folder> is the session's subagents folder, for example
  %USERPROFILE%\\.claude\\projects\\<project>\\<session id>\\subagents
Each worker run there is matched to a slide by the slide_NN path in its first
message. Prints one row per slide and the totals; --json writes them too.
Pages copied by script have no agent run: their cost is what a designed page
costs (the median of this deck's designed pages), which is the saving.
Exit: 0 | 2 bad usage
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from datetime import datetime
from pathlib import Path

WEIGHTS = {"input_tokens": 1.0, "cache_read_input_tokens": 0.1,
           "cache_creation_input_tokens": 1.25, "output_tokens": 5.0}


def runs(folder: Path) -> list[dict]:
    """One row per worker or translator run: agent type, slide, tokens, seconds."""
    out = []
    for meta in sorted(folder.glob("*.meta.json")):
        try:
            m = json.loads(meta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        agent = m.get("agentType") or "?"
        if not agent.startswith("slide-builder-"):
            continue
        jl = meta.with_name(meta.name.replace(".meta.json", ".jsonl"))
        if not jl.exists():
            continue
        first, stamps, by_msg = None, [], {}
        for line in jl.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("timestamp"):
                stamps.append(e["timestamp"])
            if first is None and e.get("type") == "user":
                c = e["message"]["content"]
                first = c if isinstance(c, str) else json.dumps(c)[:2000]
            if e.get("type") == "assistant":
                u = e["message"].get("usage") or {}
                mid = e["message"].get("id")
                prev = by_msg.get(mid, {})
                by_msg[mid] = {k: max(prev.get(k, 0), u.get(k, 0) or 0) for k in WEIGHTS}
        units = sum(v[k] * w for v in by_msg.values() for k, w in WEIGHTS.items())
        secs = 0.0
        if stamps:
            t = [datetime.fromisoformat(x.replace("Z", "+00:00")) for x in stamps]
            secs = (max(t) - min(t)).total_seconds()
        sm = re.search(r"slide_(\d+)", first or "")
        out.append({"agent": agent, "slide": int(sm.group(1)) if sm else None,
                    "edit_mode": "_edit_request" in (first or ""),
                    "units": round(units), "seconds": round(secs)})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Builder tokens per page, designed vs copied.")
    ap.add_argument("--out", required=True, type=Path, help="the build folder")
    ap.add_argument("--transcripts", required=True, type=Path,
                    help="the session's subagents folder")
    ap.add_argument("--json", type=Path, default=None, help="also write the rows here")
    args = ap.parse_args(argv)
    try:
        meta = json.loads((args.out / "_meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        print(f"ERROR: no readable _meta.json in {args.out}.")
        return 2
    if not args.transcripts.is_dir():
        print(f"ERROR: {args.transcripts} is not a folder.")
        return 2
    how = {}
    for s in meta.get("slides") or []:
        pc = s.get("page_copy") or {}
        how[s["n"]] = {"copy": "copied by script", "pinned": "copied page, text edit",
                       "master": "designed once (copied)"}.get(pc.get("role"), "designed")
    rs = runs(args.transcripts)
    rows = []
    for n in sorted(how):
        mine = [r for r in rs if r["slide"] == n]
        rows.append({"slide": n, "how": how[n], "runs": len(mine),
                     "units": sum(r["units"] for r in mine),
                     "seconds": sum(r["seconds"] for r in mine)})
    designed = [r["units"] for r in rows if r["how"] == "designed" and r["units"]]
    typical = statistics.median(designed) if designed else 0
    spent = sum(r["units"] for r in rows)
    saved = typical * sum(1 for r in rows if r["how"] == "copied by script")
    saved += sum(max(0, typical - r["units"]) for r in rows if r["how"] == "copied page, text edit")
    print(f"{'slide':>5}  {'how':<26} {'runs':>4} {'tokens (common unit)':>21} {'seconds':>8}")
    for r in rows:
        print(f"{r['slide']:>5}  {r['how']:<26} {r['runs']:>4} {r['units']:>21,} {r['seconds']:>8}")
    print(f"\nbuilder tokens spent: {spent:,}")
    if typical:
        base = spent + saved
        pct = 100 * saved / base if base else 0
        print(f"typical designed page: {typical:,.0f}; the same deck with every page designed: "
              f"about {base:,.0f}; saved about {saved:,.0f} ({pct:.0f}%). Target: 20% or more, "
              "and no new QC finding on the copied pages (check the slide-qc report).")
    else:
        print("no designed page with a matched worker run: check --transcripts is the "
              "session's subagents folder.")
    if args.json:
        args.json.write_text(json.dumps({"rows": rows, "spent": spent, "saved": saved},
                                        indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
