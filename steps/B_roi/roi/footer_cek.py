# steps/B_roi/roi/footer_cek.py
from __future__ import annotations
from PIL import Image


def crop_footer_cek(tile_img: Image.Image) -> Image.Image:
    """
    Crop area footer_cek (bagian yang memuat perubahan + '%' atau indikator).
    Ini baseline awal. Kita akan fine-tune berdasarkan hasil debug crop.

    Target: area yang berisi % harus selalu masuk.
    """
    w, h = tile_img.size

    '''
    Geser ke kiri	kecilkan x0 dan x1
    Geser ke kanan	besarkan x0 dan x1
    Geser ke atas	kecilkan y0 dan y1
    Geser ke bawah	besarkan y0 dan y1
    Perlebar area	kecilkan x0, besarkan x1
    Perbesar tinggi	kecilkan y0, besarkan y1
    '''
    x0 = int(w * 0.25)
    x1 = int(w * 0.80)
    y0 = int(h * 0.75)
    y1 = int(h * 0.98)

    return tile_img.crop((x0, y0, x1, y1))
