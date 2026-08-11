#!/usr/bin/env python3
"""
Prepare a portrait photo for clean ASCII conversion:
  1. remove the background (rembg with fallback) so the subject is isolated
  2. boost LOCAL contrast (CLAHE) so a flatly-lit face gains highlights and
     shadows -- this turns a dark blob into a sharp, recognizable face
  3. composite the subject onto pure white so the background reads as blank
     (white -> spaces in the ascii ramp)

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
Run once whenever the source photo changes; the ascii SVG itself is static.

    python scripts/prep_photo.py [input.jpg] [output.png]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")


def remove_bg(img_pil):
    try:
        from rembg import remove
        cut = remove(img_pil.convert("RGBA"))
        rgb = np.array(cut.convert("RGB"))
        alpha = np.array(cut.split()[-1])
        return rgb, alpha
    except Exception as e:
        print(f"rembg notice: {e}, using OpenCV GrabCut fallback...", file=sys.stderr)
        # Fallback using OpenCV GrabCut
        img_np = np.array(img_pil.convert("RGB"))
        h, w, _ = img_np.shape
        mask = np.zeros((h, w), np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        rect = (int(w * 0.05), int(h * 0.05), int(w * 0.9), int(h * 0.9))
        cv2.grabCut(img_np, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        alpha = np.where((mask == 2) | (mask == 0), 0, 255).astype(np.uint8)
        return img_np, alpha


def main():
    if not os.path.exists(INP):
        print(f"Error: input file {INP} does not exist", file=sys.stderr)
        sys.exit(1)

    pil_img = Image.open(INP)
    rgb, alpha = remove_bg(pil_img)

    # 2. Local-contrast luminance with CLAHE
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Global lift so face details sit cleanly in the ramp
    gray = cv2.convertScaleAbs(gray, alpha=1.05, beta=18)

    # 3. Paste onto white using smoothed alpha mask
    mask = (alpha.astype(np.float32) / 255.0)
    mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
    out = gray.astype(np.float32) * mask + 255.0 * (1.0 - mask)
    out = np.clip(out, 0, 255).astype(np.uint8)

    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    Image.fromarray(out, mode="L").save(OUT)
    print(f"Wrote prepped image to {OUT} (shape: {out.shape})")


if __name__ == "__main__":
    main()
