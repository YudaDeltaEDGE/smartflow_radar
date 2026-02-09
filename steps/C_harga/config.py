# steps/C_harga/config.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HargaConfig:
    """
    Konfigurasi Step C_harga (OCR harga).
    Kriteria:
    - Ambil angka putih yang ukurannya paling besar
    - Max 6 digit
    """

    # Set ini kalau pytesseract tidak bisa menemukan tesseract.exe
    # contoh:
    # r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    tesseract_cmd: str | None = None

    # Maks digit harga (sesuai aturan kamu)
    max_digits: int = 6

    # Jika True: simpan debug image (opsional) nanti bisa dipakai troubleshooting
    debug_save: bool = False
