# steps/E_buy_lot/service.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Tuple

from PIL import Image
import re


@dataclass(frozen=True)
class BuyLotResult:
    emiten: str
    value: Optional[int]
    raw_debug: str = ""


class BuyLotOcrService:
    """
    Step E: OCR Total Buy Lot 5 menit

    Strategi:
    - OCR pakai image_to_string() (lebih tahan dibanding image_to_data bbox)
    - Parse persen (ideal ada '%', kalau hilang ambil angka 0..100 paling kanan)
    - Parse buy lot:
        - Ambil kandidat angka terbesar (biasanya buy lot > 100)
        - Jika persen terdeteksi dan OCR menempelkan digit persen ke belakang buy lot,
          maka potong trailing digit persen.
          contoh: "57525950%" + pct=50 -> "575259"
                  "4595213652%" + pct=52 -> "45952136"
    """

    def __init__(
        self,
        *,
        psm: int = 7,  # single line
        whitelist: str = "0123456789%.,",
        upscale: float = 3.0,
    ):
        self.psm = int(psm)
        self.whitelist = whitelist
        self.upscale = float(upscale)

    # -----------------------------
    # Preprocess (2 attempts)
    # -----------------------------
    def _preprocess_a(self, img: Image.Image):
        """
        Attempt A:
        - grayscale
        - upscale
        - fixed threshold INV (teks putih jadi hitam di atas putih)
        - close ringan (biar stroke nyambung)
        """
        try:
            import numpy as np  # type: ignore
            import cv2  # type: ignore
        except Exception:
            return None

        rgb = np.array(img.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

        if self.upscale and self.upscale != 1.0:
            gray = cv2.resize(gray, None, fx=self.upscale, fy=self.upscale, interpolation=cv2.INTER_CUBIC)

        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        _, th = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY_INV)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=1)
        return th

    def _preprocess_b(self, img: Image.Image):
        """
        Attempt B:
        - grayscale
        - upscale
        - OTSU INV
        """
        try:
            import numpy as np  # type: ignore
            import cv2  # type: ignore
        except Exception:
            return None

        rgb = np.array(img.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

        if self.upscale and self.upscale != 1.0:
            gray = cv2.resize(gray, None, fx=self.upscale, fy=self.upscale, interpolation=cv2.INTER_CUBIC)

        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=1)
        return th

    # -----------------------------
    # Parsing helpers
    # -----------------------------
    @staticmethod
    def _digits_only(num_str: str) -> str:
        return (num_str or "").strip().replace(",", "").replace(".", "")

    @staticmethod
    def _to_int(num_str: str) -> Optional[int]:
        d = BuyLotOcrService._digits_only(num_str)
        return int(d) if d.isdigit() else None

    @staticmethod
    def _extract_percent(text: str) -> Optional[int]:
        """
        Cari persen: '50%' atau '50 %' atau OCR aneh seperti '50o/o'
        Kalau '%' hilang, ambil angka 0..100 paling kanan.
        """
        if not text:
            return None

        t = text.replace("o/o", "%").replace("O/O", "%").replace("％", "%")

        m = re.search(r"(\d{1,3})\s*%", t)
        if m:
            v = int(m.group(1))
            if 0 <= v <= 100:
                return v

        nums = re.findall(r"\d{1,3}", t)
        for s in reversed(nums):
            v = int(s)
            if 0 <= v <= 100:
                return v

        return None

    @staticmethod
    def _extract_buy_lot(text: str, pct: Optional[int]) -> Optional[int]:
        """
        Ambil buy lot dari string OCR.

        Aturan:
        - Ambil kandidat angka (boleh ada koma/titik)
        - Jika ada pct:
            - jika kandidat digit besar berakhiran digit pct, potong ekornya
        - Pilih nilai terbesar yang >100
        """
        if not text:
            return None

        t = text.replace("％", "%")

        # semua kandidat angka yang mungkin (dengan , .)
        cands = re.findall(r"\d[\d,\.]*", t)
        if not cands:
            return None

        pct_str = str(pct) if pct is not None else None

        vals: List[int] = []
        for c in cands:
            d = BuyLotOcrService._digits_only(c)
            if not d.isdigit():
                continue

            # normal
            v = int(d)

            # fix kasus "buy_lot + pct nempel" -> strip trailing pct
            if pct_str and d.endswith(pct_str) and len(d) > len(pct_str):
                stripped = d[: -len(pct_str)]
                if stripped.isdigit():
                    v_strip = int(stripped)
                    # pilih yang masuk akal sebagai buy lot
                    # (harus >100 supaya bukan persen)
                    if v_strip > 100:
                        v = v_strip

            vals.append(v)

        if not vals:
            return None

        big = [v for v in vals if v > 100]
        if big:
            return max(big)
        return max(vals)

    # -----------------------------
    # OCR core
    # -----------------------------
    def _ocr_text(self, bin_img) -> Tuple[Optional[str], str]:
        try:
            import pytesseract  # type: ignore
        except Exception:
            return None, "pytesseract tidak tersedia"

        cfg = f"--oem 3 --psm {self.psm} -c tessedit_char_whitelist={self.whitelist}"
        try:
            txt = pytesseract.image_to_string(bin_img, config=cfg)
            txt = (txt or "").strip()
            return txt, "ok"
        except Exception as e:
            return None, f"ocr_error: {e}"

    def extract_buy_lot_from_image(self, img: Image.Image) -> Tuple[Optional[int], str]:
        """
        Return (value, debug)
        """
        a = self._preprocess_a(img)
        b = self._preprocess_b(img)

        # Attempt A
        if a is not None:
            txt_a, _ = self._ocr_text(a)
            pct_a = self._extract_percent(txt_a or "")
            val_a = self._extract_buy_lot(txt_a or "", pct_a)
            if val_a is not None:
                return val_a, f"A txt='{txt_a}' pct={pct_a} => {val_a}"

        # Attempt B
        if b is not None:
            txt_b, _ = self._ocr_text(b)
            pct_b = self._extract_percent(txt_b or "")
            val_b = self._extract_buy_lot(txt_b or "", pct_b)
            if val_b is not None:
                return val_b, f"B txt='{txt_b}' pct={pct_b} => {val_b}"

        # gagal total: debug
        dbg = []
        if a is not None:
            txt_a, _ = self._ocr_text(a)
            dbg.append(f"A txt='{txt_a}'")
        else:
            dbg.append("A preprocess None")

        if b is not None:
            txt_b, _ = self._ocr_text(b)
            dbg.append(f"B txt='{txt_b}'")
        else:
            dbg.append("B preprocess None")

        return None, " | ".join(dbg)

    def run(self, items) -> List[BuyLotResult]:
        out: List[BuyLotResult] = []
        for it in items:
            value, dbg = self.extract_buy_lot_from_image(it.image)
            out.append(BuyLotResult(emiten=it.emiten, value=value, raw_debug=dbg))
        return out
