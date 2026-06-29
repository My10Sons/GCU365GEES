"""Generate a few small, varied JPEG pairs for stress testing the analyze endpoint.
These are synthetic shapes — detection accuracy is NOT the point here; load is."""
import os
from PIL import Image, ImageDraw

OUT = os.path.dirname(__file__)


def car(color, with_damage=False, seed=0):
    img = Image.new("RGB", (1280, 800), (210, 214, 220))
    d = ImageDraw.Draw(img)
    # crude "vehicle" body
    d.rounded_rectangle([200, 320, 1080, 620], radius=60, fill=color)
    d.rounded_rectangle([360, 220, 920, 360], radius=40, fill=tuple(min(255, c + 25) for c in color))
    d.ellipse([300, 560, 440, 700], fill=(30, 30, 30))
    d.ellipse([840, 560, 980, 700], fill=(30, 30, 30))
    d.rectangle([1040, 380, 1090, 470], fill=(240, 220, 80))  # headlight
    if with_damage:
        # a dark gouge / dent + scratch lines
        d.ellipse([520 + seed, 430, 640 + seed, 520], fill=(20, 20, 20))
        d.line([700, 400, 860, 470], fill=(10, 10, 10), width=8)
        d.line([710, 420, 870, 490], fill=(40, 40, 40), width=5)
    return img


def save(img, name, q=80):
    p = os.path.join(OUT, name)
    img.save(p, "JPEG", quality=q)
    return p


if __name__ == "__main__":
    palettes = [(40, 90, 160), (160, 40, 40), (40, 140, 90), (90, 90, 90), (200, 160, 40)]
    for i, col in enumerate(palettes):
        save(car(col, False, i), f"before_{i}.jpg")
        # half the cases get "damage" in the after frame
        save(car(col, with_damage=(i % 2 == 0), seed=i * 7), f"after_{i}.jpg")
    print("generated", len(palettes), "pairs in", OUT)
