# steps/D_footer_cek/config.py
from dataclasses import dataclass


@dataclass(frozen=True)
class FooterCekConfig:
    # kalau True: simpan debug image preprocessed
    debug_save: bool = False

    # threshold untuk ambil teks putih (kadang perlu tweak)
    bin_threshold: int = 170
