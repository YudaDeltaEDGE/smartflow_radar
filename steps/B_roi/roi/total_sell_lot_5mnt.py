# steps/B_roi/roi/total_sell_lot_5mnt.py
from __future__ import annotations
from PIL import Image


def crop_total_sell_lot_5mnt(tile_img: Image.Image) -> Image.Image:
    """
    Crop area Total Sell Lot (5 menit) dari 1 tile.

    Layout (sesuai dokumen):
        [%]   [SELL LOT]
    Jadi angka sell lot biasanya ada di sisi kanan area bawah.

    Strategi tuning:
    - Mulai dari area bawah-kanan yang cukup aman (angka pasti masuk)
    - Setelah kelihatan hasil debug, sempitkan pelan-pelan.

    Cara geser:
    - Geser ke kiri   : kecilkan x0 dan x1
    - Geser ke kanan  : besarkan x0 dan x1
    - Geser ke atas   : kecilkan y0 dan y1
    - Geser ke bawah  : besarkan y0 dan y1
    - Perlebar area   : kecilkan x0, besarkan x1
    - Perbesar tinggi : kecilkan y0, besarkan y1
    """
    w, h = tile_img.size

    # PRESET A (awal, cukup aman di area bawah-kanan)
    x0 = int(w * 0.45)
    x1 = int(w * 0.80) #0.76 pas bumi
    y0 = int(h * 0.87)
    y1 = int(h * 0.98)

    return tile_img.crop((x0, y0, x1, y1))
