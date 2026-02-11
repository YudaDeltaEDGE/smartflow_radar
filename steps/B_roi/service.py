# steps/B_roi/service.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

from PIL import Image

from pipeline.types import HargaItem, FooterCekItem, TotalBuyLot5mnt
from .roi.harga import crop_harga
from .roi.footer_cek import crop_footer_cek
from .roi.total_buy_lot_5mnt import crop_total_buy_lot_5mnt


@dataclass(frozen=True)
class TileResult:
    emiten: str
    row: int
    col: int
    path_file: Optional[Path]  # None kalau production mode (tidak simpan)


class RoiService:
    def __init__(self, cols: int, rows: int):
        if cols <= 0 or rows <= 0:
            raise ValueError("cols/rows harus > 0")
        self.cols = cols
        self.rows = rows

    def _grid_bounds(self, total: int, parts: int) -> List[Tuple[int, int]]:
        base = total // parts
        bounds: List[Tuple[int, int]] = []
        start = 0
        for i in range(parts):
            end = start + base
            if i == parts - 1:
                end = total
            bounds.append((start, end))
            start = end
        return bounds

    def potong_24_tile_to_items(
        self,
        raw_image_path: Path,
        emiten_list_24: List[str],
        *,
        debug_save: bool = False,
        debug_save_tiles: bool = True,
        debug_save_harga_crop: bool = True,
        debug_save_footer_cek_crop: bool = True,
        debug_save_total_buy_lot_5mnt_crop: bool = True,
        tiles_dir: Optional[Path] = None,
        header_dir: Optional[Path] = None,
        footer_dir: Optional[Path] = None,
        body_dir: Optional[Path] = None,
        out_ext: str = "png",
    ) -> Tuple[List[TileResult], List[HargaItem], List[FooterCekItem], List[TotalBuyLot5mnt]]:
        """
        Output utama (in-memory):
        - harga_items: untuk Step C_harga
        - footer_cek_items: untuk Step D_footer_cek
        - total_buy_lot_5mnt: untuk Step E_buy_lot nanti

        Debug save (optional):
        - Tiles
        - Header (harga crop)
        - Footer (footer_cek crop)
        - Body (total_buy_lot_5mnt crop)
        """
        img = Image.open(raw_image_path).convert("RGB")
        w, h = img.size

        x_bounds = self._grid_bounds(w, self.cols)
        y_bounds = self._grid_bounds(h, self.rows)

        base_stem = raw_image_path.stem

        tiles_out: List[TileResult] = []
        harga_items: List[HargaItem] = []
        footer_items: List[FooterCekItem] = []
        buy5_items: List[TotalBuyLot5mnt] = []

        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if idx >= len(emiten_list_24):
                    break

                emiten = emiten_list_24[idx].strip().upper()

                x0_tile, x1_tile = x_bounds[c]
                y0_tile, y1_tile = y_bounds[r]
                tile = img.crop((x0_tile, y0_tile, x1_tile, y1_tile))

                # --- HARGA (stabil) ---
                harga_img = crop_harga(tile)
                harga_items.append(HargaItem(emiten=emiten, image=harga_img))

                # --- FOOTER CEK (crop only) ---
                footer_img = crop_footer_cek(tile)
                footer_items.append(FooterCekItem(emiten=emiten, image=footer_img))

                # --- TOTAL BUY LOT 5mnt (NEW crop) ---
                buy5_img = crop_total_buy_lot_5mnt(tile)
                buy5_items.append(TotalBuyLot5mnt(emiten=emiten, image=buy5_img))

                saved_tile_path: Optional[Path] = None

                if debug_save:
                    if debug_save_tiles:
                        if tiles_dir is None:
                            raise ValueError("tiles_dir wajib jika debug_save_tiles=True")
                        tile_name = f"{base_stem}_{emiten}.{out_ext}"
                        saved_tile_path = tiles_dir / tile_name
                        tile.save(saved_tile_path)

                    if debug_save_harga_crop:
                        if header_dir is None:
                            raise ValueError("header_dir wajib jika debug_save_harga_crop=True")
                        harga_name = f"{base_stem}_{emiten}_harga.{out_ext}"
                        harga_img.save(header_dir / harga_name)

                    if debug_save_footer_cek_crop:
                        if footer_dir is None:
                            raise ValueError("footer_dir wajib jika debug_save_footer_cek_crop=True")
                        footer_name = f"{base_stem}_{emiten}_footer_cek.{out_ext}"
                        footer_img.save(footer_dir / footer_name)

                    if debug_save_total_buy_lot_5mnt_crop:
                        if body_dir is None:
                            raise ValueError("body_dir wajib jika debug_save_total_buy_lot_5mnt_crop=True")
                        buy5_name = f"{base_stem}_{emiten}_total_buy_lot_5mnt.{out_ext}"
                        buy5_img.save(body_dir / buy5_name)

                tiles_out.append(
                    TileResult(
                        emiten=emiten,
                        row=r + 1,
                        col=c + 1,
                        path_file=saved_tile_path,
                    )
                )

                idx += 1

        return tiles_out, harga_items, footer_items, buy5_items
