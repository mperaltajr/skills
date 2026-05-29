"""Test 2: Picker UI has sw-dark + JS parses + picks-JSON includes dark fields."""
import re, subprocess, tempfile, sys
from pathlib import Path

REG_HTML = Path(r"C:\Users\m.a.peralta\OneDrive - Accenture\Library\FedEx\OTC\OTC Opportunity.register.html")

print("=" * 70)
print("TEST 2 — Picker UI carries dark_bg_slot")
print("=" * 70)

html = REG_HTML.read_text(encoding="utf-8")

# 2a. sw-dark element present
has_sw_dark = 'id="sw-dark"' in html
print(f"[2a] HTML has sw-dark element: {has_sw_dark}")
assert has_sw_dark

# 2b. Picks JSON preview includes dark_bg_slot and dark_bg_hex
has_dark_slot_in_payload = "dark_bg_slot:  state.dark_bg_slot" in html
has_dark_hex_in_payload = "dark_bg_hex:   state.dark_bg_hex" in html
print(f"[2b] Picks JSON payload has dark_bg_slot: {has_dark_slot_in_payload}")
print(f"[2b] Picks JSON payload has dark_bg_hex: {has_dark_hex_in_payload}")
assert has_dark_slot_in_payload
assert has_dark_hex_in_payload

# 2c. Extract <script> content and run node --check
# Multiple script tags possible; concat them
scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, re.DOTALL)
print(f"[2c] Found {len(scripts)} <script> blocks")
combined = "\n;\n".join(scripts)

with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
    f.write(combined)
    js_path = f.name

try:
    result = subprocess.run(
        ["node", "--check", js_path],
        capture_output=True, text=True, timeout=30,
    )
    print(f"[2c] node --check return code: {result.returncode}")
    if result.returncode != 0:
        print(f"[2c] stderr: {result.stderr[:500]}")
    assert result.returncode == 0, f"JS parse failed: {result.stderr}"
except FileNotFoundError:
    print("[2c] node not found — falling back to crude JS sanity check")
    # Crude check: balanced braces, no obvious syntax errors
    open_braces = combined.count("{")
    close_braces = combined.count("}")
    print(f"[2c] brace balance: {{={open_braces} }}={close_braces}")
    assert open_braces == close_braces

print("\nTEST 2: PASS")
