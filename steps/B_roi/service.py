# steps/B_roi/service.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from PIL import Image


@dataclass(frozen=True)
class TileResult:
    emiten: str
    row: int
    col: int
    path_file: Path


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
        Crop hanya area harga (seperti kotak kuning).
        Koordinat berbasis persentase agar fleksibel resolusi.
        """

        w, h = tile_img.size

        x0 = int(w * 0.25)
        x1 = int(w * 0.65) # jika 0.75 lebih lebar ke kanan

        y0 = int(h * 0.02) # jika 0.05 memepet dengan angka bagian atas
        y1 = int(h * 0.15) # jika 0.28 maka tab time terlihat 

        return tile_img.crop((x0, y0, x1, y1))


    def potong_24_tile(
        self,
        raw_image_path: Path,
        tiles_dir: Path,
        header_dir: Path,
        emiten_list_24: List[str],
        out_ext: str = "png",
    ) -> List[TileResult]:

        img = Image.open(raw_image_path).convert("RGB")
        w, h = img.size

        x_bounds = self._grid_bounds(w, self.cols)
        y_bounds = self._grid_bounds(h, self.rows)

        base_stem = raw_image_path.stem
        hasil: List[TileResult] = []

        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):

                if idx >= len(emiten_list_24):
                    break

                emiten = emiten_list_24[idx].strip().upper()

                x0_tile, x1_tile = x_bounds[c]
                y0_tile, y1_tile = y_bounds[r]

                tile = img.crop((x0_tile, y0_tile, x1_tile, y1_tile))

                # === SAVE TILE ===
                tile_name = f"{base_stem}_{emiten}.{out_ext}"
                tile_path = tiles_dir / tile_name
                tile.save(tile_path)

                # === CROP HARGA SAJA ===
                harga_img = self._crop_harga_saja(tile)
                harga_name = f"{base_stem}_{emiten}_harga.{out_ext}"
                harga_path = header_dir / harga_name
                harga_img.save(harga_path)

                hasil.append(
                    TileResult(
                        emiten=emiten,
                        row=r + 1,
                        col=c + 1,
                        path_file=tile_path,
                    )
                )

                idx += 1

        return hasil
