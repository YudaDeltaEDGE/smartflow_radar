# steps/F_sell_lot/service.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple
import re

import numpy as np
from PIL import Image, ImageOps

import pytesseract

from pipeline.types import TotalSellLot5mnt
from .config import SellLotConfig


@dataclass(frozen=True)
class SellLotOcrResult:
    emiten: str
    value: Optional[int]
    raw_text: str
    raw_debug: str


class SellLotService:
    def __init__(self, cfg: SellLotConfig | None = None):
        self.cfg = cfg or SellLotConfig()

    # ---------- preprocessing ----------
    def _to_gray(self, img: Image.Image) -> Image.Image:
        if img.mode != "L":
            img = img.convert("L")
        return ImageOps.autocontrast(img)

    def _resize(self, img: Image.Image, scale: int) -> Image.Image:
        if scale == 1:
            return img
        w, h = img.size
        return img.resize((w * scale, h * scale), Image.Resampling.BICUBIC)

    def _binarize_fixed(self, img_gray: Image.Image, thr: int) -> Image.Image:
        arr = np.array(img_gray)
        bw = (arr > thr).astype(np.uint8) * 255
        return Image.fromarray(bw, mode="L")

    def _otsu_threshold(self, arr: np.ndarray) -> int:
        hist = np.bincount(arr.ravel(), minlength=256).astype(np.float64)
        total = arr.size
        sum_total = np.dot(np.arange(256), hist)

        sum_b = 0.0
        w_b = 0.0
        max_var = 0.0
        threshold = 0

        for t in range(256):
            w_b += hist[t]
            if w_b == 0:
                continue
            w_f = total - w_b
            if w_f == 0:
                break

            sum_b += t * hist[t]
            m_b = sum_b / w_b
            m_f = (sum_total - sum_b) / w_f
            var_between = w_b * w_f * (m_b - m_f) ** 2

            if var_between > max_var:
                max_var = var_between
                threshold = t

        return int(threshold)

    def _binarize_otsu(self, img_gray: Image.Image) -> Image.Image:
        arr = np.array(img_gray).astype(np.uint8)
        thr = self._otsu_threshold(arr)
        bw = (arr > thr).astype(np.uint8) * 255
        return Image.fromarray(bw, mode="L")

    # ---------- OCR ----------
    def _tess_config(self) -> str:
        # whitelist sengaja longgar: digit, koma, persen, minus, spasi
        # spasi tidak masuk whitelist tesseract, tapi tesseract tetap bisa output spasi dari layout
        wl = "0123456789%,.-,"
        return f'--oem {self.cfg.oem} --psm {self.cfg.psm} -c tessedit_char_whitelist={wl}'

    def _ocr_once(self, img_bw: Image.Image) -> str:
        txt = pytesseract.image_to_string(img_bw, lang=self.cfg.lang, config=self._tess_config())
        txt = txt.replace("\n", " ").strip()
        txt = re.sub(r"\s+", " ", txt)
        return txt

    # ---------- parsing ----------
    def _after_percent(self, s: str) -> str:
        if "%" not in s:
            return s
        return s.split("%", 1)[1].strip()

    def _parse_sell_lot(self, after_percent: str) -> Tuple[Optional[int], str]:
        """
        Return (value, reason)
        Reason dipakai buat scoring.
        """
        if not after_percent:
            return None, "empty"

        if "-" in after_percent and re.fullmatch(r"[-\s]+", after_percent):
            return 0, "dash_only"

        cleaned = re.sub(r"[^0-9,\s-]", "", after_percent).strip()

        # 1) ambil koma-group valid terpanjang (paling stabil utk angka besar)
        comma_matches = re.findall(r"\d{1,3}(?:,\d{3})+", cleaned)
        if comma_matches:
            best = sorted(comma_matches, key=len, reverse=True)[0]
            try:
                return int(best.replace(",", "")), "comma_group"
            except ValueError:
                pass

        # 2) kalau spasi kebaca: ambil token digit TERPANJANG (sell lot biasanya lebih panjang)
        tokens = re.findall(r"\d+", cleaned)
        if len(tokens) >= 2:
            best = sorted(tokens, key=len, reverse=True)[0]
            return int(best), "multi_token"

        # 3) kalau nempel semua: split tail 1..4 digit (angka kanan biasanya kecil/<=5000)
        if len(tokens) == 1:
            digits = tokens[0]
            n = len(digits)
            if n <= 3:
                return int(digits), "single_short"

            for tail_len in (4, 3, 2, 1):
                if n - tail_len <= 0:
                    continue
                sell = int(digits[:-tail_len])
                tail = int(digits[-tail_len:])
                if tail <= 5000:
                    return sell, f"split_tail_{tail_len}"

            return int(digits), "single_all"

        return None, "no_digits"

    def _score(self, value: Optional[int], reason: str, raw: str) -> int:
        if value is None:
            return -10

        score = 50

        # reason priority
        if reason == "comma_group":
            score += 40
        elif reason == "multi_token":
            score += 25
        elif reason.startswith("split_tail_"):
            score += 15
        else:
            score += 0

        # penalti angka absurd (merge parah)
        if value >= 200_000_000:
            score -= 40
        elif value >= 50_000_000:
            score -= 10

        # bonus kalau raw mengandung koma (indikasi grouping benar)
        if "," in raw:
            score += 5

        return score

    # ---------- public ----------
    def run(self, items: List[TotalSellLot5mnt]) -> List[SellLotOcrResult]:
        out: List[SellLotOcrResult] = []

        for it in items:
            gray = self._to_gray(it.image)

            # variants: scale 1 & 3, fixed & otsu
            variants: List[Tuple[str, Image.Image]] = []
            for scale in (1, 3):
                g = self._resize(gray, scale)
                variants.append((f"s{scale}_fixed", self._binarize_fixed(g, self.cfg.fixed_threshold)))
                variants.append((f"s{scale}_otsu", self._binarize_otsu(g)))

            cand = []
            for name, bw in variants:
                txt = self._ocr_once(bw)
                aft = self._after_percent(txt)
                val, reason = self._parse_sell_lot(aft)
                sc = self._score(val, reason, txt)
                cand.append((sc, name, txt, aft, val, reason))

            cand.sort(key=lambda x: x[0], reverse=True)
            best = cand[0]

            debug = " | ".join(
                [f"{n}:sc={s},reason={r},txt='{t}',after%='{a}',val={v}"
                 for (s, n, t, a, v, r) in cand]
            )

            out.append(
                SellLotOcrResult(
                    emiten=it.emiten,
                    value=best[4],
                    raw_text=best[2],
                    raw_debug=f"best={best[1]} sc={best[0]} reason={best[5]} || {debug}",
                )
            )

        return out
