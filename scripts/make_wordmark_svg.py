#!/usr/bin/env python3
"""
Render "UMANG" as an EXTRUDED 3D wordmark rasterized to ASCII, and emit it as an
SVG that animates on GitHub (SMIL flipbook / oscillating rotation).
"""
import argparse
import html
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DEFAULT = os.path.join(HERE, "..", "wordmark.svg")

# Grid parameters
COLS = int(os.environ.get("WORDMARK_COLS", 52))
ROW_MARGIN = int(os.environ.get("WORDMARK_ROW_MARGIN", 5))
CELL_W = 9.0
CELL_H = 15.5
TEXT = os.environ.get("WORDMARK_TEXT", "UMANG")

MASK_H = 260
TRACKING = 0.12
DEPTH_FRAC = 0.30
TILT_DEG = float(os.environ.get("WORDMARK_TILT", 5.0))

FPS = 12
ROCK_AMPLITUDE_DEG = 12.0
ROCK_PERIOD_SEC = 3.6
SPIN_PERIOD_SEC = 6.0
REST_YAW_DEG = 16.0

PAD = 18
TITLEBAR_H = 30
STATUS_H = 30

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
ACCENT = "#58a6ff"

RAMP = " .`:-=+*cs#%@"


def find_system_font():
    candidates = [
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\consola.ttf",
        "C:\\Windows\\Fonts\\segui_bold.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "/System/Library/Fonts/Futura.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def get_font():
    fp = os.environ.get("WORDMARK_FONT") or find_system_font()
    try:
        if fp and os.path.exists(fp):
            return ImageFont.truetype(fp, MASK_H)
    except Exception:
        pass
    return ImageFont.load_default()


def render_mask(text, font):
    # Render text mask
    dummy = Image.new("L", (10, 10))
    d = ImageDraw.Draw(dummy)
    bbox = d.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0] + 40
    h = bbox[3] - bbox[1] + 40

    img = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(img)
    d.text((20 - bbox[0], 20 - bbox[1]), text, font=font, fill=255)
    return np.array(img) > 128


def rasterize_wordmark_3d(text="UMANG"):
    font = get_font()
    mask = render_mask(text, font)
    mh, mw = mask.shape
    depth = int(mh * DEPTH_FRAC)

    # 3D points
    y_idx, x_idx = np.where(mask)
    pts = []
    # Front and back caps + sides
    for z in range(0, depth, max(1, depth // 12)):
        shade_val = 1.0 - (z / depth) * 0.4
        for x, y in zip(x_idx[::2], y_idx[::2]):
            pts.append((x - mw / 2, y - mh / 2, z - depth / 2, shade_val))

    pts = np.array(pts)
    return pts, mw, mh


def build_wordmark_svg(out_path=OUT_DEFAULT):
    pts, mw, mh = rasterize_wordmark_3d(TEXT)

    # Build ASCII frames for rocking motion
    n_frames = int(FPS * ROCK_PERIOD_SEC)
    frames_ascii = []

    aspect = CELL_H / CELL_W
    rad_tilt = math.radians(TILT_DEG)
    cos_t, sin_t = math.cos(rad_tilt), math.sin(rad_tilt)

    grid_h = 44
    grid_w = COLS

    for fi in range(n_frames):
        t = fi / n_frames
        yaw = REST_YAW_DEG + ROCK_AMPLITUDE_DEG * math.sin(2 * math.pi * t)
        rad_yaw = math.radians(yaw)
        cos_y, sin_y = math.cos(rad_yaw), math.sin(rad_yaw)

        buf = np.zeros((grid_h, grid_w))
        zbuf = np.full((grid_h, grid_w), -1e9)

        # Scale factor
        scale = (grid_w * 0.85) / mw

        for x, y, z, shade in pts:
            # Rotate Y
            rx = x * cos_y + z * sin_y
            rz = -x * sin_y + z * cos_y
            # Rotate X
            ry = y * cos_t - rz * sin_t
            rz = y * sin_t + rz * cos_t

            gx = int(grid_w / 2 + rx * scale)
            gy = int(grid_h / 2 + (ry * scale) / aspect)

            if 0 <= gx < grid_w and 0 <= gy < grid_h:
                if rz > zbuf[gy, gx]:
                    zbuf[gy, gx] = rz
                    buf[gy, gx] = shade

        # Convert to text rows
        lines = []
        for gy in range(grid_h):
            chars = []
            for gx in range(grid_w):
                val = buf[gy, gx]
                if val <= 0:
                    chars.append(" ")
                else:
                    idx = int(val * (len(RAMP) - 1))
                    chars.append(RAMP[min(len(RAMP) - 1, max(0, idx))])
            lines.append("".join(chars))
        frames_ascii.append(lines)

    canvas_w = int(grid_w * CELL_W + PAD * 2)
    canvas_h = int(grid_h * CELL_H + TITLEBAR_H + STATUS_H + PAD)

    dur = ROCK_PERIOD_SEC
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs>',
        f'<linearGradient id="wbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>',
        '</defs>',
        f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#wbg)"/>',
        f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{canvas_w}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    for i, col in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H/2}" r="5" fill="{col}"/>')
    parts.append(f'<text x="{canvas_w/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" text-anchor="middle">umang@github: ~$ ./wordmark.sh --3d</text>')

    art_top = TITLEBAR_H + 10
    font_size = CELL_H * 0.85

    for fi, lines in enumerate(frames_ascii):
        opacities = ["0"] * n_frames
        opacities[fi] = "1"
        vals = ";".join(opacities + [opacities[0]])
        key_times = ";".join(f"{k/n_frames:.3f}" for k in range(n_frames + 1))

        parts.append(f'<g opacity="{"1" if fi == 0 else "0"}">')
        parts.append(
            f'<animate attributeName="opacity" values="{vals}" keyTimes="{key_times}" '
            f'dur="{dur:.2f}s" repeatCount="indefinite" calcMode="discrete"/>'
        )

        for ry, line in enumerate(lines):
            if not line.strip():
                continue
            y = art_top + ry * CELL_H + CELL_H * 0.74
            safe = html.escape(line)
            parts.append(
                f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{ACCENT}" '
                f'font-size="{font_size:.1f}" textLength="{grid_w * CELL_W}" lengthAdjust="spacing">{safe}</text>'
            )
        parts.append('</g>')

    # Footer
    footer_y = canvas_h - 15
    parts.append(f'<line x1="0" y1="{footer_y - 15}" x2="{canvas_w}" y2="{footer_y - 15}" stroke="{FRAME}"/>')
    parts.append(f'<text x="{PAD}" y="{footer_y}" fill="{TITLE_TEXT}" font-size="12">umang@github:~$ <tspan fill="{INK}">3D ASCII Engine</tspan></text>')
    parts.append('</svg>')

    svg = "".join(parts)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote wordmark to {out_path} ({len(svg)} bytes; {canvas_w}x{canvas_h})")


if __name__ == "__main__":
    build_wordmark_svg()
