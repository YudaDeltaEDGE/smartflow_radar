# steps/B_roi/roi/total_buy_lot_5mnt.py
from __future__ import annotations
from PIL import Image


def crop_total_buy_lot_5mnt(tile_img: Image.Image) -> Image.Image:
    """
    Crop area Total Buy Lot (5 menit) dari 1 tile.

    Strategi tuning:
    - Mulai dari area bawah yang cukup lebar (biar angka pasti masuk)
    - Setelah terlihat hasilnya, sempitkan pelan-pelan.

    Cara geser:
    - Geser ke kiri   : kecilkan x0 dan x1
    - Geser ke kanan  : besarkan x0 dan x1
    - Geser ke atas   : kecilkan y0 dan y1
    - Geser ke bawah  : besarkan y0 dan y1
    - Perlebar area   : kecilkan x0, besarkan x1
    - Perbesar tinggi : kecilkan y0, besarkan y1
    """
    w, h = tile_img.size

    # PRESET A (awal, cukup lebar di area bawah-kiri)
    x0 = int(w * 0.12)
    x1 = int(w * 0.40)
    y0 = int(h * 0.87)
    y1 = int(h * 0.98)

    return tile_img.crop((x0, y0, x1, y1))
