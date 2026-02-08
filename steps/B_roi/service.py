#steps/B_roi/service.py

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
        """
        Bagi ukuran total menjadi 'parts' segmen.
        Kalau ada sisa pixel, ditaruh di segmen terakhir (biar tidak hilang).
        """
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

    def potong_24_tile(
        self,
        raw_image_path: Path,
        tiles_dir: Path,
        emiten_list_24: List[str],
        out_ext: str = "png",
    ) -> List[TileResult]:
        img = Image.open(raw_image_path).convert("RGB")
        w, h = img.size

        x_bounds = self._grid_bounds(w, self.cols)  # 3 kolom
        y_bounds = self._grid_bounds(h, self.rows)  # 8 baris

        # Nama dasar file raw: pc1_m1_08-17-36 (tanpa ext)
        base_stem = raw_image_path.stem

        hasil: List[TileResult] = []

        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if idx >= len(emiten_list_24):
                    break

                emiten = emiten_list_24[idx].strip().upper()
                x0, x1 = x_bounds[c]
                y0, y1 = y_bounds[r]

                tile = img.crop((x0, y0, x1, y1))

                # contoh: pc1_m1_08-17-36_RATU.png
                out_name = f"{base_stem}_{emiten}.{out_ext}"
                out_path = tiles_dir / out_name

                tile.save(out_path)

                hasil.append(TileResult(emiten=emiten, row=r + 1, col=c + 1, path_file=out_path))
                idx += 1

        return hasil


