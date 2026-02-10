# steps/B_roi/service.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

from PIL import Image

from pipeline.types import HargaItem


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

    def _crop_harga_saja(self, tile_img: Image.Image) -> Image.Image:
        """
        Crop area harga (sub-header).
        Koordinat persentase agar fleksibel resolusi.
        """
        w, h = tile_img.size

        x0 = int(w * 0.25)
        x1 = int(w * 0.65)

        y0 = int(h * 0.02)
        y1 = int(h * 0.15)

        return tile_img.crop((x0, y0, x1, y1))

    def potong_24_tile_to_harga_items(
        self,
        raw_image_path: Path,
        emiten_list_24: List[str],
        *,
        debug_save: bool = False,
        debug_save_tiles: bool = True,
        debug_save_harga_crop: bool = True,
        tiles_dir: Optional[Path] = None,
        header_dir: Optional[Path] = None,
        out_ext: str = "png",
    ) -> Tuple[List[TileResult], List[HargaItem]]:
        """
        Output utama: List[HargaItem] (in-memory) untuk Step C.
        Output tambahan: List[TileResult] (untuk info/debug; path_file None kalau tidak disimpan).

        Kalau debug_save=True:
          - simpan tile ke tiles_dir (opsional)
          - simpan crop harga ke header_dir (opsional)
        """
        img = Image.open(raw_image_path).convert("RGB")
        w, h = img.size

        x_bounds = self._grid_bounds(w, self.cols)
        y_bounds = self._grid_bounds(h, self.rows)

        base_stem = raw_image_path.stem

        tiles_out: List[TileResult] = []
        harga_items: List[HargaItem] = []

        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if idx >= len(emiten_list_24):
                    break

                emiten = emiten_list_24[idx].strip().upper()

                x0_tile, x1_tile = x_bounds[c]
                y0_tile, y1_tile = y_bounds[r]

                tile = img.crop((x0_tile, y0_tile, x1_tile, y1_tile))

                # crop harga (in-memory)
                harga_img = self._crop_harga_saja(tile)
                harga_items.append(HargaItem(emiten=emiten, image=harga_img))

                saved_tile_path: Optional[Path] = None

                # DEBUG SAVE (optional)
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
                        harga_path = header_dir / harga_name
                        harga_img.save(harga_path)

                tiles_out.append(
                    TileResult(
                        emiten=emiten,
                        row=r + 1,
                        col=c + 1,
                        path_file=saved_tile_path,
                    )
                )

                idx += 1

        return tiles_out, harga_items
