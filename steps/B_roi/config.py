# steps/B_roi/config.py
from dataclasses import dataclass


@dataclass(frozen=True)
class RoiConfig:
    ext: str = "png"

    # PRODUKSI: default False (tidak simpan crop/tile)
    debug_save: bool = False

    # Kalau debug_save=True, kamu bisa pilih simpan apa saja
    debug_save_tiles: bool = True
    debug_save_harga_crop: bool = True
