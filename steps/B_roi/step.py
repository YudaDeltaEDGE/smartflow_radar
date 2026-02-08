# steps/B_roi/step.py

from __future__ import annotations

from pathlib import Path
from typing import List

from config.settings import settings
from utils.path import pastikan_folder
from utils.waktu import tanggal_str

from .config import RoiConfig
from .service import RoiService, TileResult


def _baca_emiten_map(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"File emiten_map.txt tidak ditemukan: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip()]


def jalankan_step_B_roi() -> List[TileResult]:
    tanggal_folder = tanggal_str(settings.DATE_FOLDER_FORMAT)
    base_dir = settings.IMAGES_DIR / tanggal_folder

    raw_dir = base_dir / "Raw"
    tiles_dir = base_dir / "Tiles"
    body_dir = base_dir / "Body"

    # Pastikan folder Tiles & Body ada
    for d in (tiles_dir, body_dir):
        pastikan_folder(d)

    # Ambil emiten dari config/emiten_map.txt
    emiten_map_path = settings.ROOT_DIR / "config" / "emiten_map.txt"
    emiten_all = _baca_emiten_map(emiten_map_path)

    # Karena sekarang 1 monitor → ambil 24 pertama
    total_tile = settings.TILE_ROWS * settings.TILE_COLS
    emiten_24 = emiten_all[:total_tile]

    # Ambil semua file Raw
    raw_files = sorted(list(raw_dir.glob("*.png")) +
                       list(raw_dir.glob("*.jpg")) +
                       list(raw_dir.glob("*.jpeg")))

    if not raw_files:
        raise FileNotFoundError(f"Tidak ada file Raw di: {raw_dir}")

    cfg = RoiConfig()
    svc = RoiService(cols=settings.TILE_COLS, rows=settings.TILE_ROWS)

    hasil_semua: List[TileResult] = []

    for raw_path in raw_files:
        hasil = svc.potong_24_tile(
            raw_image_path=raw_path,
            tiles_dir=tiles_dir,
            emiten_list_24=emiten_24,
            out_ext=cfg.ext,
        )
        hasil_semua.extend(hasil)

    return hasil_semua
