#!/usr/bin/env python3
"""Smoke test: registration picks the brand font's faces from the fonts' own data.

Registration used to guess the font file from the family's name. One family
shipped its narrow ("condensed") face as the bare <Family>.ttf, so that face
was bundled, and every sketch and every title-fit check was drawn about a
quarter narrower than the finished slide (2026-10-08).

On a made-up font folder where the bare file name is the condensed face:
  - the regular face picked is the normal-width one, by its name table; the
    bold face is picked too (file names that no name guess would find)
  - registration's bundling copies both into the template's folder, records
    them and the theme's own face names in brand.yml, and prints the faces
  - a folder with only the condensed face gives that face plus a warning
  - bold_ttf_for() finds the bundled bold face from the regular one
  - title-fit measurement uses the bold face when the theme's heading face is
    bold, and the normal-width face measures wider than the condensed one

Run:  py -3 slide-builder/tests/run_font_pick_smoke.py
Prints "SMOKE PASSED." on success; raises AssertionError otherwise.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(HERE))

from _fake_fonts import make_font  # noqa: E402
import _chrome_schema as CS  # noqa: E402
import register_template as RT  # noqa: E402


def _family_folder(d: Path, *, with_normal: bool = True) -> None:
    # The trap: the bare family file name holds the CONDENSED face.
    make_font(d / "FictSans.ttf", family="Fict Sans Condensed", style="Regular",
              typo_family="Fict Sans", typo_style="Condensed", width=3, scale=0.75)
    make_font(d / "FictSans-CondBold.ttf", family="Fict Sans Condensed", style="Bold",
              typo_family="Fict Sans", typo_style="Condensed Bold", weight=700, width=3,
              scale=0.75)
    if with_normal:
        make_font(d / "FS_Rg_0.ttf", family="Fict Sans", style="Regular", width=5)
        make_font(d / "FS_Hv_0.ttf", family="Fict Sans", style="Bold", weight=700, width=5)
        make_font(d / "FS_It_0.ttf", family="Fict Sans", style="Italic", width=5)


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        fonts = td / "fonts"
        _family_folder(fonts)

        print("[1] faces picked from the name tables, not the file names")
        got = CS.pick_family_faces("Fict Sans", [fonts])
        assert Path(got["regular"]).name == "FS_Rg_0.ttf", got["regular"]
        assert Path(got["bold"]).name == "FS_Hv_0.ttf", got["bold"]
        assert not got["warnings"], got["warnings"]
        assert got["regular_face"]["width"] == 5
        print(f"    ok: regular {CS.describe_face(got['regular_face'])}; "
              f"bold {CS.describe_face(got['bold_face'])}")
        # The old guess tried "<Family>.ttf" first: that is the condensed face.
        assert CS._read_face(str(fonts / "FictSans.ttf"))["width"] == 3

        print("[2] registration bundles regular + bold and records the face names")
        sidecar = td / "sidecar"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            bundle = RT._bundle_brand_fonts(sidecar, "Fict Sans", "Fict Sans", dirs=[fonts])
        out = buf.getvalue()
        assert bundle == {"title": "FS_Rg_0.ttf", "title_bold": "FS_Hv_0.ttf",
                          "body": "FS_Rg_0.ttf"}, bundle
        assert (sidecar / "FS_Rg_0.ttf").exists() and (sidecar / "FS_Hv_0.ttf").exists()
        assert not (sidecar / "FictSans.ttf").exists(), "the condensed face was bundled"
        assert "normal width" in out and "bold face" in out, out
        brand = sidecar / "brand.yml"
        RT.write_brand_yml(brand, primary_hex="112233", accent_hex="445566",
                           cover_bg_hex="112233", primary_slot="dk2", accent_slot="accent1",
                           cover_bg_slot="dk2", dark_bg_hex="112233", dark_bg_slot="dk2",
                           font_heading="Fict Sans", font_body="Fict Sans",
                           strip_master_backgrounds=False, sha8="00000000",
                           title_font_ttf_path=bundle["title"],
                           title_font_bold_ttf_path=bundle["title_bold"],
                           body_font_ttf_path=bundle["body"],
                           theme_heading_face="Fict Sans Bold", theme_body_face="Fict Sans")
        import yaml
        y = yaml.safe_load(brand.read_text(encoding="utf-8"))
        assert y["title_font_bold_ttf_path"] == "FS_Hv_0.ttf", y
        assert y["theme_heading_face"] == "Fict Sans Bold", y
        assert y["font_heading"] == "Fict Sans", y
        print("    ok: both faces bundled, brand.yml records them and the theme's faces")

        print("[3] only a condensed face installed: picked, with a warning")
        only = td / "only_cond"
        _family_folder(only, with_normal=False)
        got2 = CS.pick_family_faces("Fict Sans", [only])
        assert Path(got2["regular"]).name == "FictSans.ttf", got2
        assert got2["warnings"] and "condensed" in got2["warnings"][0], got2["warnings"]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            RT._bundle_brand_fonts(td / "sc2", "Fict Sans", "Fict Sans", dirs=[only])
        assert "WARN" in buf.getvalue() and "condensed" in buf.getvalue(), buf.getvalue()
        print("    ok: warns that only the condensed version is installed")

        print("[4] the bundled bold face is found from the regular one")
        b = CS.bold_ttf_for(str(sidecar / "FS_Rg_0.ttf"))
        assert b and Path(b).name == "FS_Hv_0.ttf", b
        print("    ok")

        print("[5] title-fit measurement uses the right face")
        reg, bold = str(sidecar / "FS_Rg_0.ttf"), str(sidecar / "FS_Hv_0.ttf")
        assert CS.title_measure_ttf(reg, bold, heading_face="Fict Sans Bold") == bold
        assert CS.title_measure_ttf(reg, bold, title_bold=True) == bold
        assert CS.title_measure_ttf(reg, bold, heading_face="Fict Sans") == reg
        title = "A headline long enough to wrap in a narrow box on the made-up slide"
        n_cond = CS.count_wrapped_lines(title, str(fonts / "FictSans.ttf"), 28, 950)
        n_norm = CS.count_wrapped_lines(title, reg, 28, 950)
        n_bold = CS.count_wrapped_lines(title, bold, 28, 950)
        assert n_cond < n_norm <= n_bold, (n_cond, n_norm, n_bold)
        print(f"    ok: same title wraps to {n_cond} line(s) condensed, {n_norm} regular, "
              f"{n_bold} bold")

    print("\nSMOKE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
