#!/usr/bin/env python3
"""Render SVG files to PNG with headless Chrome (no ImageMagick/librsvg needed).

Usage: scripts/render_svg.py assets/architecture.svg [more.svg ...]
Writes <name>.png next to each input.
"""
import os, re, subprocess, sys, tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if not os.path.exists(CHROME):
    sys.exit(f"Chrome not found at {CHROME}")

for path in sys.argv[1:]:
    svg = open(path).read()
    w = re.search(r'width="(\d+)"', svg)
    h = re.search(r'height="(\d+)"', svg)
    if not (w and h):
        sys.exit(f"{path}: needs explicit width/height attributes")
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as fh:
        fh.write("<!doctype html><meta charset=utf-8>"
                 "<style>html,body{margin:0;background:#070d16}</style>" + svg)
        html = fh.name
    png = os.path.splitext(path)[0] + ".png"
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=2",
        f"--window-size={w.group(1)},{h.group(1)}",
        f"--screenshot={png}", f"file://{html}",
    ], capture_output=True)
    os.unlink(html)
    print(f"{png}  {w.group(1)}x{h.group(1)}  {os.path.getsize(png)//1024}KB")
