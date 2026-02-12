# steps/B_roi/config.py
from dataclasses import dataclass


@dataclass(frozen=True)
class RoiConfig:
    ext: str = "png"

    # PRODUKSI: default False (tidak simpan crop/tile)
    debug_save: bool = True  # sementara True untuk tuning ROI

    # Kalau debug_save=True, kamu bisa pilih simpan apa saja
    debug_save_tiles: bool = True
    debug_save_harga_crop: bool = True
    debug_save_footer_cek_crop: bool = True

    # NEW: simpan crop total buy lot 5mnt ke Body/
    debug_save_total_buy_lot_5mnt_crop: bool = True

    # NEW: simpan crop total sell lot 5mnt ke Body/
    debug_save_total_sell_lot_5mnt_crop: bool = True
