# steps/B_roi/step.py
from __future__ import annotations

from pathlib import Path
from typing import List

from config.settings import settings
from utils.path import pastikan_folder
from utils.waktu import tanggal_str
from pipeline.types import Context

from .config import RoiConfig
from .service import RoiService


def _baca_emiten_map(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"File emiten_map.txt tidak ditemukan: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip()]


def jalankan_step_B_roi(ctx: Context) -> Context:
    """
    STEP B - ROI (CROP ONLY)
    - Ambil 1 RAW TERBARU dari folder Raw
    - Potong menjadi 24 tile (3x8)
    - Crop area harga -> ctx.harga_items
    - Crop footer_cek -> ctx.footer_cek_items
    - Crop total buy lot 5mnt -> ctx.total_buy_lot_5mnt
    - Crop total sell lot 5mnt -> ctx.total_sell_lot_5mnt
    - Tidak melakukan pengecekan '%' (itu Step D)
    """

    tanggal_folder = tanggal_str(settings.DATE_FOLDER_FORMAT)
    base_dir = settings.IMAGES_DIR / tanggal_folder
    raw_dir = base_dir / "Raw"

    tiles_dir = base_dir / "Tiles"
    header_dir = base_dir / "Header"
    footer_dir = base_dir / "Footer"
    body_dir = base_dir / "Body"  # untuk debug buy/sell lot

    emiten_map_path = settings.ROOT_DIR / "config" / "emiten_map.txt"
    emiten_all = _baca_emiten_map(emiten_map_path)

    total_tile = settings.TILE_ROWS * settings.TILE_COLS
    emiten_24 = emiten_all[:total_tile]

    raw_candidates = (
        list(raw_dir.glob("*.png"))
        + list(raw_dir.glob("*.jpg"))
        + list(raw_dir.glob("*.jpeg"))
    )
    if not raw_candidates:
        raise FileNotFoundError(f"Tidak ada file Raw di: {raw_dir}")

    raw_latest = max(raw_candidates, key=lambda p: p.stat().st_mtime)
    print(f"[B_roi] Proses raw terbaru: {raw_latest.name}")

    cfg = RoiConfig()
    svc = RoiService(cols=settings.TILE_COLS, rows=settings.TILE_ROWS)

    if cfg.debug_save:
        if cfg.debug_save_tiles:
            pastikan_folder(tiles_dir)
        if cfg.debug_save_harga_crop:
            pastikan_folder(header_dir)
        if cfg.debug_save_footer_cek_crop:
            pastikan_folder(footer_dir)
        if cfg.debug_save_total_buy_lot_5mnt_crop:
            pastikan_folder(body_dir)
        if cfg.debug_save_total_sell_lot_5mnt_crop:
            pastikan_folder(body_dir)

    tiles_out, harga_items, footer_items, buy5_items, sell5_items = svc.potong_24_tile_to_items(
        raw_image_path=raw_latest,
        emiten_list_24=emiten_24,
        debug_save=cfg.debug_save,
        debug_save_tiles=cfg.debug_save_tiles,
        debug_save_harga_crop=cfg.debug_save_harga_crop,
        debug_save_footer_cek_crop=cfg.debug_save_footer_cek_crop,
        debug_save_total_buy_lot_5mnt_crop=cfg.debug_save_total_buy_lot_5mnt_crop,
        debug_save_total_sell_lot_5mnt_crop=cfg.debug_save_total_sell_lot_5mnt_crop,
        tiles_dir=tiles_dir if (cfg.debug_save and cfg.debug_save_tiles) else None,
        header_dir=header_dir if (cfg.debug_save and cfg.debug_save_harga_crop) else None,
        footer_dir=footer_dir if (cfg.debug_save and cfg.debug_save_footer_cek_crop) else None,
        body_dir=body_dir if (
            cfg.debug_save and (cfg.debug_save_total_buy_lot_5mnt_crop or cfg.debug_save_total_sell_lot_5mnt_crop)
        ) else None,
        out_ext=cfg.ext,
    )

    ctx.harga_items = harga_items
    ctx.footer_cek_items = footer_items
    ctx.total_buy_lot_5mnt = buy5_items
    ctx.total_sell_lot_5mnt = sell5_items

    print(f"[B_roi] Total harga_items: {len(ctx.harga_items)}")
    print(f"[B_roi] Total footer_cek_items: {len(ctx.footer_cek_items)}")
    print(f"[B_roi] Total total_buy_lot_5mnt: {len(ctx.total_buy_lot_5mnt)}")
    print(f"[B_roi] Total total_sell_lot_5mnt: {len(ctx.total_sell_lot_5mnt)}")

    return ctx
