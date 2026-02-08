# steps/A_capture/step.py

from __future__ import annotations

from pathlib import Path
from typing import List, Dict

from config.settings import settings
from utils.path import pastikan_folder, baca_teks_rapi
from utils.waktu import tanggal_str, waktu_str

from .config import CaptureConfig
from .service import CaptureService, HasilCapture

def jalankan_step_A_capture() -> List[HasilCapture]:
    # kode pc dari config/kode_pc.txt (pc1/pc2/...)
    kode_pc_path: Path = settings.ROOT_DIR / "config" / "kode_pc.txt"
    kode_pc = baca_teks_rapi(kode_pc_path, default="pc1")

    # Folder tanggal: output/images/YYYY-MM-DD/
    tanggal_folder = tanggal_str(settings.DATE_FOLDER_FORMAT)
    base_dir = settings.IMAGES_DIR / tanggal_folder

    # Subfolder sesuai permintaan
    raw_dir = base_dir / "Raw"
    tiles_dir = base_dir / "Tiles"
    header_dir = base_dir / "Header"
    footer_dir = base_dir / "Footer"

    for d in (raw_dir, tiles_dir, header_dir, footer_dir):
        pastikan_folder(d)

    # timestamp nama file: 08-17-36
    ts_file = waktu_str(settings.TIME_FILENAME_FORMAT)

    cfg = CaptureConfig()
    svc = CaptureService(
        raw_dir=raw_dir,
        ext=cfg.ext,
        crop_top=settings.CAPTURE_CROP_TOP_PX,
        crop_bottom=settings.CAPTURE_CROP_BOTTOM_PX,
        crop_left=settings.CAPTURE_CROP_LEFT_PX,
        crop_right=settings.CAPTURE_CROP_RIGHT_PX,
    )

    hasil = svc.capture_semua_monitor(kode_pc=kode_pc, ts=ts_file)
    return hasil