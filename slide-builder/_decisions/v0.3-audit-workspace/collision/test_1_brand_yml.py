"""Test 1: brand.yml round-trip — dark_bg_hex / dark_bg_slot present + back-compat."""
import sys, json, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = Path(r"C:\Users\m.a.peralta\.claude\skills\.claude\worktrees\agent-abaae9e70ed8f6544\slide-builder")
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))

from twins.client_theme import load_brand_sidecar, load_client_theme

TEMPLATE = Path(r"C:\Users\m.a.peralta\OneDrive - Accenture\Library\FedEx\OTC\OTC Opportunity.pptx")
BRAND_YML = Path(r"C:\Users\m.a.peralta\OneDrive - Accenture\Library\FedEx\OTC\OTC Opportunity.brand.yml")

print("=" * 70)
print("TEST 1 — brand.yml round-trip")
print("=" * 70)

# 1a. Raw YAML check
txt = BRAND_YML.read_text(encoding="utf-8")
has_dark_hex = "dark_bg_hex" in txt
has_dark_slot = "dark_bg_slot" in txt
print(f"[1a] raw YAML has dark_bg_hex: {has_dark_hex}")
print(f"[1a] raw YAML has dark_bg_slot: {has_dark_slot}")

# 1b. Sidecar loader
d = load_brand_sidecar(TEMPLATE)
print(f"[1b] load_brand_sidecar returned dark_bg_hex: {d.get('dark_bg_hex')!r}")
print(f"[1b] load_brand_sidecar returned dark_bg_slot: {d.get('dark_bg_slot')!r}")
assert d.get("dark_bg_hex") == "4D148C", f"expected 4D148C, got {d.get('dark_bg_hex')!r}"
assert d.get("dark_bg_slot") == "dk2", f"expected dk2, got {d.get('dark_bg_slot')!r}"

# 1c. ClientTheme exposes dark_bg_hex
ct = load_client_theme(str(TEMPLATE))
print(f"[1c] ClientTheme.dark_bg_hex = {ct.dark_bg_hex!r}")
assert ct.dark_bg_hex == "4D148C"

# 1d. Back-compat: synthesize v0.2-style brand.yml + theme.json with NO dark_bg_hex
# Reuse the actual template SHA for the theme.json.
import hashlib, shutil
h = hashlib.sha256()
with open(str(TEMPLATE), "rb") as f:
    for chunk in iter(lambda: f.read(65536), b""):
        h.update(chunk)
sha = h.hexdigest()

with tempfile.TemporaryDirectory() as td:
    td_p = Path(td)
    fake_tpl = td_p / "Fake.pptx"
    shutil.copy(str(TEMPLATE), str(fake_tpl))
    # v0.2 brand.yml — no dark_bg_hex / dark_bg_slot
    (td_p / "Fake.brand.yml").write_text(
        'primary_hex: "#AB1234"\n'
        'accent_hex: "#001122"\n'
        'cover_bg_hex: "#AB1234"\n'
        'primary_slot: dk2\n'
        'accent_slot: lt2\n'
        'cover_bg_slot: dk2\n'
        'font_heading: "Inter"\n'
        'font_body: "Inter"\n'
        'strip_master_backgrounds: true\n',
        encoding="utf-8",
    )
    actual_sha = hashlib.sha256(fake_tpl.read_bytes()).hexdigest()
    (td_p / "Fake.theme.json").write_text(
        json.dumps({"template_sha": actual_sha, "registered_at": "2026-01-01"}, indent=2),
        encoding="utf-8",
    )
    d2 = load_brand_sidecar(fake_tpl)
    print(f"[1d] back-compat default dark_bg_hex: {d2.get('dark_bg_hex')!r}")
    print(f"[1d] back-compat default dark_bg_slot: {d2.get('dark_bg_slot')!r}")
    assert d2.get("dark_bg_hex") == "AB1234", f"back-compat broken: {d2.get('dark_bg_hex')!r}"
    assert d2.get("dark_bg_slot") == "dk2", f"back-compat slot: {d2.get('dark_bg_slot')!r}"

print("\nTEST 1: PASS")
