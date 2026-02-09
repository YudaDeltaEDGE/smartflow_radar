# steps/C_harga/step.py

from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import csv

from PIL import Image

from config.settings import settings
from utils.path import pastikan_folder
from utils.waktu import tanggal_str, waktu_str

from pipeline.types import Context, HargaItem
from .config import HargaConfig
from .service import HargaOcrService, HargaRow

import pytesseract


def _parse_emiten_from_filename(filename: str) -> str:
    """
    Contoh nama file Step B header harga:
    pc1_m1_03-11-34_DCII_harga.png
    -> emiten = DCII
    """
    stem = Path(filename).stem
    parts = stem.split("_")

    # cari token 'harga' lalu ambil token sebelumnya
    try:
        idx = parts.index("harga")
        if idx - 1 >= 0:
            return parts[idx - 1].upper()
    except ValueError:
        pass

    # fallback: cari token huruf paling masuk akal
    for p in reversed(parts):
        if p.isalpha() and 2 <= len(p) <= 6:
            return p.upper()

    return stem.upper()


def _fallback_load_harga_items_from_header(header_dir: Path) -> List[HargaItem]:
    items: List[HargaItem] = []
    if not header_dir.exists():
        return items

    for p in sorted(header_dir.glob("*_harga.*")):
        emiten = _parse_emiten_from_filename(p.name)
        img = Image.open(p).convert("RGB")
        items.append(HargaItem(emiten=emiten, image=img))

    return items


def _tulis_csv(rows: List[HargaRow], csv_path: Path) -> None:
    pastikan_folder(csv_path.parent)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["emiten", "harga"])
        for r in rows:
            w.writerow([r.emiten, "" if r.harga is None else r.harga])


def jalankan_step_C_harga(ctx: Context) -> Context:
    """
    Step C_harga:
    - Ambil harga_items dari Context (mode produksi)
    - Fallback: baca dari folder Header/*_harga.png (mode sekarang)
    - OCR harga (angka putih besar) max 6 digit
    - Output: csv_harga
    """
    cfg = HargaConfig()

    # Set path tesseract kalau dibutuhkan
    if cfg.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = cfg.tesseract_cmd

    tanggal_folder = tanggal_str(settings.DATE_FOLDER_FORMAT)
    base_img_dir = settings.IMAGES_DIR / tanggal_folder
    header_dir = base_img_dir / "Header"

    # Output CSV
    csv_dir = settings.OUTPUT_DIR / "csv" / tanggal_folder
    pastikan_folder(csv_dir)
    ts = waktu_str(settings.TIME_FILENAME_FORMAT)
    csv_path = csv_dir / f"csv_harga_{ts}.csv"

    # 1) ambil dari context dulu
    items = list(ctx.harga_items)

    # 2) fallback kalau context kosong
    if not items:
        items = _fallback_load_harga_items_from_header(header_dir)

    svc = HargaOcrService(max_digits=cfg.max_digits)

    rows = svc.run([(it.emiten, it.image) for it in items])

    _tulis_csv(rows, csv_path)

    ctx.csv_harga_path = str(csv_path)
    return ctx
