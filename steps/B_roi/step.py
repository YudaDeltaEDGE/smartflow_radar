# steps/B_roi/step.py

'''from __future__ import annotations

from pathlib import Path
from typing import List

from config.settings import settings
from utils.path import baca_teks_rapi

from .config import RoiConfig
from .service import RoiService, HasilRoi


def _baca_emiten_map(path: Path) -> List[str]:
    teks = path.read_text(encoding="utf-8").strip().splitlines()
    emiten = [x.strip() for x in teks if x.strip()]
    return emiten


def jalankan_step_B_roi() -> List[HasilRoi]:
    folder_hari_ini = settings.folder_tanggal_hari_ini()

    # Input: semua PNG di folder tanggal hari ini (yang berasal dari Step A)
    gambar_monitor = sorted([p for p in folder_hari_ini.glob("*.png")])

    if not gambar_monitor:
        raise FileNotFoundError(
            f"Tidak ada gambar PNG di {folder_hari_ini}. "
            f"Jalankan Step A dulu."
        )

    # Emiten map
    emiten_map_path = settings.ROOT_DIR / "config" / "emiten_map.txt"
    daftar_emiten = _baca_emiten_map(emiten_map_path)

    # Output ROI folder
    out_roi = folder_hari_ini / "roi"
    out_roi.mkdir(parents=True, exist_ok=True)

    # Config ROI (isi margin/gap sesuai kondisi kamu)
    cfg = RoiConfig(
        cols=3,
        rows=8,

        # TODO: ISI INI (awal: coba 0 semua, nanti kita tuning)
        margin_left=0,
        margin_top=0,
        margin_right=0,
        margin_bottom=0,
        gap_x=0,
        gap_y=0,

        # Sub-crop boleh kosong dulu (0,0,0,0) => akan di-skip
        crop_harga=(0, 0, 0, 0),
        crop_footer_cek=(0, 0, 0, 0),
        crop_total_buy_lot=(0, 0, 0, 0),
        crop_total_sell_lot=(0, 0, 0, 0),
    )

    svc = RoiService(cfg)

    semua_hasil: List[HasilRoi] = []
    for img_path in gambar_monitor:
        hasil = svc.proses_satu_gambar_monitor(
            path_gambar=img_path,
            daftar_emiten_urut=daftar_emiten,
            out_dir_roi=out_roi,
        )
        semua_hasil.append(hasil)

    return semua_hasil
'''
