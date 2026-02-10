# steps/D_footer_cek/service.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict

from PIL import Image


@dataclass(frozen=True)
class FooterCekResult:
    emiten: str
    has_percent: bool
    is_not_available: bool
    raw_text: str  # hasil OCR untuk debugging


class FooterCekService:
    """
    - Cek tanda '%' via OCR dari crop footer_cek
    - Kalau tidak ada '%', cek apakah mengandung 'is not available' (atau variasinya)
    """

    def __init__(self, bin_threshold: int = 170):
        self.bin_threshold = bin_threshold

    def _ocr_text(self, img: Image.Image) -> str:
        """
        OCR ringan (tesseract). Fail-safe: kalau library tidak ada, return "".
        """
        try:
            import pytesseract  # type: ignore
            import numpy as np  # type: ignore
            import cv2  # type: ignore
        except Exception:
            return ""

        rgb = np.array(img.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        _, th = cv2.threshold(gray, self.bin_threshold, 255, cv2.THRESH_BINARY)
        th = 255 - th  # invert

        text = pytesseract.image_to_string(
            th,
            config="--psm 7"
        )
        return (text or "").strip()

    def evaluate(self, emiten: str, footer_img: Image.Image) -> FooterCekResult:
        text = self._ocr_text(footer_img)
        low = text.lower()

        has_percent = "%" in text

        # variasi penulisan yang umum: "is not available", "not available", dsb.
        is_not_available = ("not available" in low) or ("is not available" in low)

        return FooterCekResult(
            emiten=emiten,
            has_percent=has_percent,
            is_not_available=is_not_available,
            raw_text=text,
        )

    def run(self, items) -> List[FooterCekResult]:
        out: List[FooterCekResult] = []
        for it in items:
            out.append(self.evaluate(it.emiten, it.image))
        return out
