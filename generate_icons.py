"""
generate_icons.py — Creates PNG icons for the Chrome Extension
Run once: python generate_icons.py
Requires: pip install Pillow
"""

import os
from PIL import Image, ImageDraw

ICONS_DIR = os.path.join(os.path.dirname(__file__), "extension", "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

SIZES = [16, 48, 128]

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

BG      = hex_to_rgb("0f0f1a")
PURPLE1 = hex_to_rgb("7c3aed")
PURPLE2 = hex_to_rgb("a855f7")
TEAL    = hex_to_rgb("22d3a5")
WHITE   = (255, 255, 255)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def make_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle with gradient-like fill
    margin = max(1, size // 10)
    circle_bbox = [margin, margin, size - margin, size - margin]
    draw.ellipse(circle_bbox, fill=PURPLE1 + (255,))

    # Inner highlight
    inner_margin = margin + max(1, size // 8)
    inner_bbox = [inner_margin, inner_margin, size - inner_margin, size - inner_margin]
    draw.ellipse(inner_bbox, fill=PURPLE2 + (180,))

    # Draw 3 sentiment bars (positive=teal, neutral=blue, negative=red)
    bar_w = max(1, size // 8)
    bar_spacing = max(2, size // 6)
    bar_heights = [0.55, 0.35, 0.2]  # positive, neutral, negative
    bar_colors  = [TEAL, (96, 165, 250), (248, 113, 113)]
    center_x = size // 2
    start_x = center_x - bar_spacing

    for i, (bh, bc) in enumerate(zip(bar_heights, bar_colors)):
        x = start_x + i * bar_spacing
        bar_height = max(2, int(size * bh * 0.5))
        y_bottom = size - margin - max(2, size // 6)
        y_top = y_bottom - bar_height
        bx = x - bar_w // 2
        draw.rounded_rectangle(
            [bx, y_top, bx + bar_w, y_bottom],
            radius=max(1, bar_w // 3),
            fill=bc + (240,)
        )

    return img

for sz in SIZES:
    icon = make_icon(sz)
    path = os.path.join(ICONS_DIR, f"icon{sz}.png")
    icon.save(path, "PNG")
    print(f"Created {path}")

print("Icons generated successfully!")
