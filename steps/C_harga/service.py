# steps/C_harga/service.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import re

import cv2
import numpy as np
from PIL import Image
import pytesseract


@dataclass(frozen=True)
class HargaRow:
    emiten: str
    harga: Optional[int]


class HargaOcrService:
    """
    Versi stabil:
    - Fokus area putih
    - OCR satu baris penuh
    - Ambil angka terpanjang
    - Max 6 digit
    """

    def __init__(self, max_digits: int = 6):
        self.max_digits = max_digits

    def _preprocess(self, img: Image.Image) -> np.ndarray:
        rgb = np.array(img.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

        # Resize dulu supaya digit besar
        gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

        # Ambil area terang (angka putih)
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

        # Bersihkan noise kecil
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

        # Invert supaya hitam di atas putih (lebih mudah untuk Tesseract)
        thresh = 255 - thresh

        return thresh

    def _extract_price(self, text: str) -> Optional[int]:
        text = text.strip()

        # Ambil semua kandidat angka (boleh ada koma/titik)
        candidates = re.findall(r"[0-9][0-9,\.]*", text)
        if not candidates:
            return None

        cleaned = []

        for c in candidates:
            n = c.replace(",", "").replace(".", "")
            if n.isdigit():
                cleaned.append(n)

        if not cleaned:
            return None

        # Ambil yang paling panjang
        cleaned.sort(key=lambda s: len(s), reverse=True)
        best = cleaned[0]

        # Validasi max digit
        if len(best) > self.max_digits:
            return None

        return int(best)

    def run(self, items) -> List[HargaRow]:
        results: List[HargaRow] = []

        for emiten, image in items:
            proc = self._preprocess(image)

            text = pytesseract.image_to_string(
                proc,
                config="--psm 7 -c tessedit_char_whitelist=0123456789,."
            )

            harga = self._extract_price(text)

            results.append(
                HargaRow(
                    emiten=emiten,
                    harga=harga
                )
            )

        return results
