# steps/B_roi/roi/harga.py
from __future__ import annotations

from PIL import Image


def crop_harga(tile_img: Image.Image) -> Image.Image:
    """
    Crop area harga (sub-header) dari 1 tile.
    Koordinat persentase agar fleksibel terhadap resolusi.

    NOTE:
    Angka ini mengikuti versi stabil yang sudah kamu pakai:
      x: 25% -> 65%
      y:  2% -> 15%
    """
    w, h = tile_img.size
    x0 = int(w * 0.25)
    x1 = int(w * 0.65)
    y0 = int(h * 0.02)
    y1 = int(h * 0.15)
    return tile_img.crop((x0, y0, x1, y1))
