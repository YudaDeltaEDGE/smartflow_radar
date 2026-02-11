# steps/E_buy_lot/config.py

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class BuyLotConfig:
    """
    Step E (OCR Total Buy Lot 5 menit)
    """

    debug_save: bool = False

    # PSM untuk image_to_data (umumnya 6 cocok untuk blok kecil)
    psm: int = 6

    # whitelist supaya fokus angka + % + separator
    whitelist: str = "0123456789%.,"

    # upscale untuk memperjelas token kecil
    upscale: float = 3.0

    # threshold untuk biner (angka putih / teks terang)
    bin_threshold: int = 180
