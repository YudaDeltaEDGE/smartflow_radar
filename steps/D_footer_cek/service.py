# steps/D_footer_cek/service.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from PIL import Image


@dataclass(frozen=True)
class FooterCekRaw:
    """
    Output mentah dari evaluasi OCR footer_cek untuk 1 emiten.
    """
    emiten: str
    has_percent: bool
    is_not_available: bool
    raw_text: str


class FooterCekService:
    """
    Step D Service:
    - OCR ringan pada crop footer_cek
    - Tentukan: ada '%' atau tidak
    - Jika tidak ada '%', cek apakah mengandung 'not available' (variasi)

    Catatan:
    - Ini sengaja sederhana & robust, karena Step D hanya gate/validasi.
    """

    def __init__(self, bin_threshold: int = 170):
        self.bin_threshold = int(bin_threshold)

    def _ocr_text(self, img: Image.Image) -> str:
        """
        OCR tesseract yang ringan untuk membaca footer_cek.
        Fail-safe: kalau dependency belum ada, return "".
        """
        try:
            import pytesseract  # type: ignore
            import numpy as np  # type: ignore
            import cv2  # type: ignore
        except Exception:
            return ""

        rgb = np.array(img.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

        # Perbesar agar karakter lebih terbaca
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Ambil area terang
        _, th = cv2.threshold(gray, self.bin_threshold, 255, cv2.THRESH_BINARY)

        # Invert (tesseract sering lebih stabil)
        th = 255 - th

        # psm 7: asumsi satu baris teks (cukup untuk footer cek)
        text = pytesseract.image_to_string(th, config="--psm 7")
        return (text or "").strip()

    def evaluate(self, emiten: str, footer_img: Image.Image) -> FooterCekRaw:
        text = self._ocr_text(footer_img)
        low = text.lower()

        has_percent = "%" in text

        # variasi penulisan yang umum
        is_not_available = ("not available" in low) or ("is not available" in low)

        return FooterCekRaw(
            emiten=emiten,
            has_percent=has_percent,
            is_not_available=is_not_available,
            raw_text=text,
        )

    def run(self, items) -> List[FooterCekRaw]:
        """
        items: iterable berisi object yang punya .emiten dan .image
        (FooterCekItem dari Context).
        """
        out: List[FooterCekRaw] = []
        for it in items:
            out.append(self.evaluate(it.emiten, it.image))
        return out
