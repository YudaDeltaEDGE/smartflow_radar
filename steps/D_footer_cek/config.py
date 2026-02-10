# steps/D_footer_cek/config.py
from dataclasses import dataclass


@dataclass(frozen=True)
class FooterCekConfig:
    """
    Konfigurasi Step D_footer_cek (gate).

    - bin_threshold: threshold untuk ambil teks terang (angka/teks putih)
      dari crop footer_cek (kasus normal: ada '%').
    - debug_save: reserved (kalau nanti mau simpan preprocess).
    """
    debug_save: bool = False
    bin_threshold: int = 170
