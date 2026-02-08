# steps/A_capture/step.py

from pathlib import Path
from typing import List

from config.settings import settings
from utils.path import pastikan_folder, baca_teks_rapi

from .config import CaptureConfig
from .service import CaptureService, HasilCapture


def jalankan_step_A_capture() -> List[HasilCapture]:
    folder_hari_ini: Path = settings.folder_tanggal_hari_ini()
    pastikan_folder(folder_hari_ini)

    kode_pc_path = settings.ROOT_DIR / "config" / "kode_pc.txt"
    kode_pc = baca_teks_rapi(kode_pc_path, default="pc1")

    jam = settings.jam_sekarang()

    cfg = CaptureConfig()
    svc = CaptureService(output_dir=folder_hari_ini, ext=cfg.ext)

    hasil = svc.capture_semua_monitor(
        kode_pc=kode_pc,
        ts=jam,
        monitor_aktif=settings.MONITOR_AKTIF
    )

    return hasil

