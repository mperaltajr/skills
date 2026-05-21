"""
Split REVIEW-N.html into chunks of <=25 slides each so the browser doesn't choke.

For each input REVIEW-N.html:
  1. Parse the MOCKUPS = [...]; array
  2. Compute even-sized chunks (each <= max_per_chunk, last one no smaller than the rest)
  3. Write REVIEW-N-1.html, REVIEW-N-2.html, ... — each is a full copy of the source HTML
     with the MOCKUPS array replaced by the chunk's slice and the STORAGE_KEY +
     <title> made unique per chunk.

Run: python _split_review.py
"""
from pathlib import Path
import re
import math

MAX_PER_CHUNK = 25
HERE = Path(__file__).resolve().parent
SOURCES = ["REVIEW-2.html", "REVIEW-3.html", "REVIEW-4.html"]


def split_file(src_path: Path):
    text = src_path.read_text(encoding="utf-8")

    # Locate MOCKUPS array
    m_start = re.search(r"const MOCKUPS\s*=\s*\[", text)
    if not m_start:
        print(f"  no MOCKUPS in {src_path.name}; skip")
        return
    array_start = m_start.end()
    # Find matching closing `];` after array_start
    m_end = re.search(r"\n\];", text[array_start:])
    if not m_end:
        print(f"  no array close in {src_path.name}; skip")
        return
    array_end = array_start + m_end.start()

    body = text[array_start:array_end]  # the array body (without brackets)
    entries = [ln.strip() for ln in body.split("\n") if ln.strip().startswith("{")]
    if not entries:
        print(f"  no entries parsed in {src_path.name}; skip")
        return

    n_total = len(entries)
    n_chunks = math.ceil(n_total / MAX_PER_CHUNK)
    chunk_size = math.ceil(n_total / n_chunks)  # even-ish

    # Locate storage key + title for rewrite
    src_stem = src_path.stem  # e.g. "REVIEW-2"
    sk_re = re.compile(r'(const STORAGE_KEY\s*=\s*")([^"]+)(")')
    title_re = re.compile(r"(<title>)([^<]*)(</title>)")

    print(f"\n{src_path.name}: {n_total} slides -> {n_chunks} chunks of ~{chunk_size}")

    for i in range(n_chunks):
        slice_entries = entries[i * chunk_size:(i + 1) * chunk_size]
        if not slice_entries:
            break
        first_id = slice_entries[0].split('"')[1] if '"' in slice_entries[0] else "?"
        last_id = slice_entries[-1].split('"')[1] if '"' in slice_entries[-1] else "?"

        # Build new MOCKUPS body
        new_body = "\n  " + "\n  ".join(slice_entries) + "\n"
        new_text = text[:array_start] + new_body + text[array_end:]

        # Rewrite STORAGE_KEY so each chunk has its own localStorage
        new_key = f"pattern-{src_stem.lower()}-{i + 1}"
        new_text = sk_re.sub(rf'\g<1>{new_key}\g<3>', new_text, count=1)

        # Rewrite title
        new_title = f"{src_stem} Part {i + 1}/{n_chunks} · Patterns {first_id}-{last_id} · {len(slice_entries)} slides"
        new_text = title_re.sub(rf'\g<1>{new_title}\g<3>', new_text, count=1)

        out_path = HERE / f"{src_stem}-{i + 1}.html"
        out_path.write_text(new_text, encoding="utf-8")
        print(f"  wrote {out_path.name} ({len(slice_entries)} slides, ids {first_id}..{last_id})")


def main():
    for s in SOURCES:
        p = HERE / s
        if not p.exists():
            print(f"missing {s}")
            continue
        split_file(p)


if __name__ == "__main__":
    main()
