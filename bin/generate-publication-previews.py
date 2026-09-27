#!/usr/bin/env python3
"""Build lightweight previews at each original aspect ratio; retain original figures for click-to-zoom.

Run from the repository root with Python 3 and ImageMagick installed:
    python3 bin/generate-publication-previews.py
"""
from pathlib import Path
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/img/publication_preview"
OUTPUT = SOURCE / "thumbnails"
WIDTHS = (200, 400, 600)
QUALITY = 82

def main():
    executable = shutil.which("magick") or shutil.which("convert")
    if not executable:
        raise SystemExit("ImageMagick is required (magick or convert).")
    names = sorted(set(re.findall(r"\bpreview\s*=\s*\{([^}]+)\}", (ROOT / "_bibliography/papers.bib").read_text(encoding="utf-8"))))
    OUTPUT.mkdir(exist_ok=True)
    manifest = {}
    for name in names:
        if "://" in name:
            continue
        source = SOURCE / name
        if not source.is_file():
            raise FileNotFoundError(source)
        variants = {}
        for width in WIDTHS:
            output = OUTPUT / f"{source.stem}-{width}.webp"
            subprocess.run([executable, str(source) + "[0]", "-auto-orient", "-colorspace", "sRGB",
                            "-background", "white", "-alpha", "remove", "-alpha", "off",
                            "-filter", "Lanczos", "-resize", f"{width}x", "-strip",
                            "-define", "webp:method=6", "-quality", str(QUALITY), str(output)], check=True)
            variants[str(width)] = "/" + output.relative_to(ROOT).as_posix()
        dimensions = subprocess.check_output([executable, str(output), "-format", "%w %h", "info:"], text=True).split()
        variants["width"], variants["height"] = map(int, dimensions)
        manifest[name] = variants
    (ROOT / "_data/publication_previews.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    originals = sum((SOURCE / name).stat().st_size for name in manifest)
    display = sum((ROOT / variants["400"].lstrip("/")).stat().st_size for variants in manifest.values())
    print(f"{len(manifest)} previews; originals {originals:,} bytes; 400px display variants {display:,} bytes")

if __name__ == "__main__":
    main()
