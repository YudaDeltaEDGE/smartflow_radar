# steps/F_sell_lot/config.py
from dataclasses import dataclass


@dataclass(frozen=True)
class SellLotConfig:
    # OCR config
    lang: str = "eng"
    psm: int = 7  # 1-line text
    oem: int = 3

    # whitelist: angka, koma, persen, minus, spasi
    whitelist: str = "0123456789%, -,"  # spasi penting biar bisa split kalau kebaca

    # preprocessing
    fixed_threshold: int = 200  # buat versi binarize "fixed"
