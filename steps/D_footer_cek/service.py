# steps/D_footer_cek/service.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from PIL import Image


@dataclass(frozen=True)
class FooterCekRaw:
    emiten: str
    has_percent: bool
    is_not_available: bool
    raw_text: str


class FooterCekService:
    def __init__(self, bin_threshold: int = 170):
        self.bin_threshold = int(bin_threshold)

    def _contains_not_available(self, text: str) -> bool:
        """
        Toleran terhadap typo OCR (avaliable/availble, dll).
        Kita pakai kunci 'data' + 'avail' sebagai sinyal kuat.
        """
        low = (text or "").lower().replace("\n", " ").replace("|", " ").strip()
        if ("data" in low and "avail" in low):
            return True
        return (
            "data is not available" in low
            or "not available" in low
            or "is not available" in low
            or "not avaliable" in low
            or "not availble" in low
        )

    def _ocr_text_footer(self, img: Image.Image) -> str:
        """
        OCR untuk crop footer_cek.

        Masalah yang kamu alami:
        - kasus 'Data is not available' (teks abu-abu di bg gelap)
          sering gagal jika pakai threshold tetap + invert + psm 7.
        Solusi:
        - multi-attempt preprocessing (fixed threshold, Otsu, adaptive)
        - coba psm 6 (block text) selain psm 7
        - pilih hasil terbaik via scoring sederhana
        """
        try:
            import pytesseract  # type: ignore
            import numpy as np  # type: ignore
            import cv2  # type: ignore
        except Exception:
            return ""

        rgb = np.array(img.convert("RGB"))
        gray0 = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        gray0 = cv2.resize(gray0, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
        gray0 = cv2.GaussianBlur(gray0, (3, 3), 0)

        variants = []

        # A) fixed threshold + invert (biasanya cocok untuk '%' / teks putih)
        _, th_a = cv2.threshold(gray0, self.bin_threshold, 255, cv2.THRESH_BINARY)
        th_a = 255 - th_a
        variants.append(("A", th_a, "--psm 7 -l eng"))

        # B) Otsu + invert
        _, th_b = cv2.threshold(gray0, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        th_b = 255 - th_b
        variants.append(("B", th_b, "--psm 6 -l eng"))

        # C) Adaptive + invert (sering cocok untuk teks abu 'Data is not available')
        th_c = cv2.adaptiveThreshold(
            gray0,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            9,
        )
        th_c = 255 - th_c
        variants.append(("C", th_c, "--psm 6 -l eng"))

        # D) Adaptive tanpa invert (kadang lebih pas tergantung kontras)
        th_d = cv2.adaptiveThreshold(
            gray0,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            9,
        )
        variants.append(("D", th_d, "--psm 6 -l eng"))

        def score(text: str) -> int:
            t = (text or "").strip()
            low = t.lower()
            s = len(t)
            # bonus keyword yang kita cari
            if "data" in low:
                s += 10
            if "avail" in low:
                s += 10
            if "%" in t:
                s += 10
            return s

        best_text = ""
        best_score = -1

        for _name, mat, cfg in variants:
            txt = pytesseract.image_to_string(mat, config=cfg) or ""
            txt = txt.strip()
            sc = score(txt)
            if sc > best_score:
                best_score = sc
                best_text = txt

        return best_text

    def _ocr_text_tile_not_available(self, tile_img: Image.Image) -> str:
        """
        OCR fokus teks 'Data is not available' di area bawah tile.
        Ini dipakai hanya kalau Step D punya akses ke file Tiles.
        (Saat ini ctx.raw_path belum ada, jadi tidak kepanggil.)
        """
        try:
            import pytesseract  # type: ignore
            import numpy as np  # type: ignore
            import cv2  # type: ignore
        except Exception:
            return ""

        w, h = tile_img.size

        x0 = int(w * 0.12)
        x1 = int(w * 0.88)
        y0 = int(h * 0.58)
        y1 = int(h * 0.93)
        crop = tile_img.crop((x0, y0, x1, y1))

        rgb = np.array(crop.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        gray = cv2.resize(gray, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        th = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            9,
        )
        th = 255 - th

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=1)

        cfg = "--oem 3 --psm 6 -l eng"
        text = pytesseract.image_to_string(th, config=cfg)
        return (text or "").strip()

    def evaluate(self, emiten: str, footer_img: Image.Image) -> FooterCekRaw:
        text = self._ocr_text_footer(footer_img)
        has_percent = "%" in (text or "")
        is_not_available = self._contains_not_available(text)
        return FooterCekRaw(
            emiten=emiten,
            has_percent=has_percent,
            is_not_available=is_not_available,
            raw_text=(text or ""),
        )

    def detect_not_available_from_tile_path(self, tile_path: Path, return_text: bool = False):
        try:
            img = Image.open(tile_path).convert("RGB")
        except Exception:
            return (False, "") if return_text else False

        text = self._ocr_text_tile_not_available(img)
        ok = self._contains_not_available(text)
        return (ok, text) if return_text else ok

    def run(self, items) -> List[FooterCekRaw]:
        out: List[FooterCekRaw] = []
        for it in items:
            out.append(self.evaluate(it.emiten, it.image))
        return out
