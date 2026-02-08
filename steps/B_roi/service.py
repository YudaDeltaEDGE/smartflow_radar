#steps/B_roi/service.py

'''from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from PIL import Image

from .config import RoiConfig, Box


@dataclass(frozen=True)
class HasilRoi:
    tiles: List[Path]
    harga: List[Path]
    footer_cek: List[Path]
    total_buy_lot: List[Path]
    total_sell_lot: List[Path]


def _valid_box(box: Box) -> bool:
    l, t, r, b = box
    return (r > l) and (b > t)


class RoiService:
    def __init__(self, cfg: RoiConfig):
        self.cfg = cfg

    def _hitung_tile_size(self, w: int, h: int) -> Tuple[int, int]:
        cfg = self.cfg
        area_w = w - cfg.margin_left - cfg.margin_right
        area_h = h - cfg.margin_top - cfg.margin_bottom

        if area_w <= 0 or area_h <= 0:
            raise ValueError(
                f"Area ROI tidak valid. Cek margin: "
                f"left={cfg.margin_left}, right={cfg.margin_right}, "
                f"top={cfg.margin_top}, bottom={cfg.margin_bottom}, "
                f"gambar={w}x{h}"
            )

        tile_w = (area_w - cfg.gap_x * (cfg.cols - 1)) // cfg.cols
        tile_h = (area_h - cfg.gap_y * (cfg.rows - 1)) // cfg.rows

        if tile_w <= 0 or tile_h <= 0:
            raise ValueError(
                f"Tile size tidak valid. Hasil tile_w={tile_w}, tile_h={tile_h}. "
                f"Cek margin/gap/cols/rows."
            )

        return tile_w, tile_h

    def _crop_rel(self, img: Image.Image, box: Box) -> Image.Image:
        # box relatif dari tile
        return img.crop(box)

    def proses_satu_gambar_monitor(
        self,
        path_gambar: Path,
        daftar_emiten_urut: List[str],
        out_dir_roi: Path,
    ) -> HasilRoi:
        cfg = self.cfg

        img_full = Image.open(path_gambar).convert("RGB")
        W, H = img_full.size
        tile_w, tile_h = self._hitung_tile_size(W, H)

        # Folder output
        tiles_dir = out_dir_roi / "tiles"
        harga_dir = out_dir_roi / "harga"
        footer_cek_dir = out_dir_roi / "footer_cek"
        buy_dir = out_dir_roi / "total_buy_lot"
        sell_dir = out_dir_roi / "total_sell_lot"

        for d in [tiles_dir, harga_dir, footer_cek_dir, buy_dir, sell_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Nama dasar: ambil dari file capture (tanpa ext)
        base = path_gambar.stem  # contoh: pc1_m1_08-17-36

        total_tiles = cfg.cols * cfg.rows
        if len(daftar_emiten_urut) < total_tiles:
            raise ValueError(
                f"emiten_map.txt kurang baris. Butuh minimal {total_tiles}, "
                f"tapi cuma ada {len(daftar_emiten_urut)}."
            )

        hasil_tiles: List[Path] = []
        hasil_harga: List[Path] = []
        hasil_footer_cek: List[Path] = []
        hasil_buy: List[Path] = []
        hasil_sell: List[Path] = []

        # Urutan crop: baris 1 kolom 1 -> baris 1 kolom 2 -> baris 1 kolom 3 -> ... -> baris 8 kolom 3
        # Ini sesuai dokumen (urut baris dulu, lalu kolom) :contentReference[oaicite:2]{index=2}
        idx = 0
        for r in range(cfg.rows):
            for c in range(cfg.cols):
                emiten = daftar_emiten_urut[idx].strip().upper()
                idx += 1

                left = cfg.margin_left + c * (tile_w + cfg.gap_x)
                top = cfg.margin_top + r * (tile_h + cfg.gap_y)
                right = left + tile_w
                bottom = top + tile_h

                tile = img_full.crop((left, top, right, bottom))

                # 1) Simpan tile
                tile_name = f"{base}_{emiten}.png"
                tile_path = tiles_dir / tile_name
                tile.save(tile_path)
                hasil_tiles.append(tile_path)

                # 2) Turunan crop (kalau box belum diisi benar, kita skip agar ROI tiles tetap jalan)
                if _valid_box(cfg.crop_harga):
                    p = harga_dir / f"{base}_{emiten}_harga.png"
                    self._crop_rel(tile, cfg.crop_harga).save(p)
                    hasil_harga.append(p)

                if _valid_box(cfg.crop_footer_cek):
                    p = footer_cek_dir / f"{base}_{emiten}_footer_cek.png"
                    self._crop_rel(tile, cfg.crop_footer_cek).save(p)
                    hasil_footer_cek.append(p)

                if _valid_box(cfg.crop_total_buy_lot):
                    p = buy_dir / f"{base}_{emiten}_total_buy_lot.png"
                    self._crop_rel(tile, cfg.crop_total_buy_lot).save(p)
                    hasil_buy.append(p)

                if _valid_box(cfg.crop_total_sell_lot):
                    p = sell_dir / f"{base}_{emiten}_total_sell_lot.png"
                    self._crop_rel(tile, cfg.crop_total_sell_lot).save(p)
                    hasil_sell.append(p)

        return HasilRoi(
            tiles=hasil_tiles,
            harga=hasil_harga,
            footer_cek=hasil_footer_cek,
            total_buy_lot=hasil_buy,
            total_sell_lot=hasil_sell,
        )'''

