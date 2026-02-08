# steps/B_roi/config.py

'''from dataclasses import dataclass
from typing import Tuple

Box = Tuple[int, int, int, int]  # (left, top, right, bottom)

@dataclass(frozen=True)
class RoiConfig:
    # Grid tile per monitor
    cols: int = 3
    rows: int = 8

    # Margin area tradebook di dalam screenshot monitor (pixel)
    margin_left: int = 0
    margin_top: int = 0
    margin_right: int = 0
    margin_bottom: int = 0

    # Jarak antar tile (pixel)
    gap_x: int = 0
    gap_y: int = 0

    # Sub-crop relatif terhadap tile (pixel)
    # Kamu isi berdasarkan hasil ukur (Paint / screenshot)
    # Format: (left, top, right, bottom) relatif dari (0,0) tile
    crop_harga: Box = (0, 0, 0, 0)
    crop_footer_cek: Box = (0, 0, 0, 0)
    crop_total_buy_lot: Box = (0, 0, 0, 0)
    crop_total_sell_lot: Box = (0, 0, 0, 0)'''
