# steps/B_roi/step.py
from __future__ import annotations

from pathlib import Path
from typing import List

from config.settings import settings
from utils.path import pastikan_folder
from utils.waktu import tanggal_str
from pipeline.types import Context

from .config import RoiConfig
from .service import RoiService, TileResult


def _baca_emiten_map(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"File emiten_map.txt tidak ditemukan: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip()]


def jalankan_step_B_roi(ctx: Context) -> Context:
    """
    STEP B - ROI (PRODUCTION MODE)
    - Ambil 1 RAW TERBARU dari folder Raw
    - Potong menjadi 24 tile (3x8)
    - Crop area harga dari tiap tile
    - Masukkan ke ctx.harga_items (IN-MEMORY)
    - Tidak simpan tile/crop ke disk kecuali debug mode
    """
    tanggal_folder = tanggal_str(settings.DATE_FOLDER_FORMAT)
    base_dir = settings.IMAGES_DIR / tanggal_folder
    raw_dir = base_dir / "Raw"

    # folder debug (dipakai hanya kalau debug_save=True)
    tiles_dir = base_dir / "Tiles"
    header_dir = base_dir / "Header"

    # Ambil emiten dari config/emiten_map.txt
    emiten_map_path = settings.ROOT_DIR / "config" / "emiten_map.txt"
    emiten_all = _baca_emiten_map(emiten_map_path)

    total_tile = settings.TILE_ROWS * settings.TILE_COLS
    emiten_24 = emiten_all[:total_tile]

    # ===============================
    # AMBIL 1 RAW TERBARU SAJA
    # ===============================
    raw_candidates = (
        list(raw_dir.glob("*.png"))
        + list(raw_dir.glob("*.jpg"))
        + list(raw_dir.glob("*.jpeg"))
    )
    if not raw_candidates:
        raise FileNotFoundError(f"Tidak ada file Raw di: {raw_dir}")

    # pilih berdasarkan modified time (paling aman untuk produksi)
    raw_latest = max(raw_candidates, key=lambda p: p.stat().st_mtime)
    raw_files = [raw_latest]

    print(f"[B_roi] Proses raw terbaru: {raw_latest.name}")

    # ===============================
    # INISIALISASI SERVICE
    # ===============================
    cfg = RoiConfig()
    svc = RoiService(cols=settings.TILE_COLS, rows=settings.TILE_ROWS)

    # kalau debug, pastikan foldernya ada
    if cfg.debug_save:
        if cfg.debug_save_tiles:
            pastikan_folder(tiles_dir)
        if cfg.debug_save_harga_crop:
            pastikan_folder(header_dir)

    semua_harga_items = []
    semua_tiles: List[TileResult] = []

    # ===============================
    # PROSES 1 RAW TERBARU
    # ===============================
    for raw_path in raw_files:
        tiles_out, harga_items = svc.potong_24_tile_to_harga_items(
            raw_image_path=raw_path,
            emiten_list_24=emiten_24,
            debug_save=cfg.debug_save,
            debug_save_tiles=cfg.debug_save_tiles,
            debug_save_harga_crop=cfg.debug_save_harga_crop,
            tiles_dir=tiles_dir if cfg.debug_save_tiles else None,
            header_dir=header_dir if cfg.debug_save_harga_crop else None,
            out_ext=cfg.ext,
        )
        semua_tiles.extend(tiles_out)
        semua_harga_items.extend(harga_items)

    # ===============================
    # SIMPAN KE CONTEXT (IN-MEMORY)
    # ===============================
    ctx.harga_items = semua_harga_items
    print(f"[B_roi] Total harga_items (24 expected): {len(ctx.harga_items)}")

    return ctx
