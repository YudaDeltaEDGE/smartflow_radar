# steps/E_buy_lot/step.py

from __future__ import annotations

from pathlib import Path
from typing import Optional
import csv

from config.settings import settings
from utils.path import pastikan_folder
from utils.waktu import tanggal_str, waktu_str

from pipeline.types import Context, FooterGate
from .config import BuyLotConfig
from .service import BuyLotOcrService


def _tulis_csv(emiten_to_val: dict[str, Optional[int]], csv_path: Path) -> None:
    pastikan_folder(csv_path.parent)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["emiten", "total_buy_lot_5mnt"])
        for em in sorted(emiten_to_val.keys()):
            v = emiten_to_val[em]
            w.writerow([em, "" if v is None else v])


def jalankan_step_E_buy_lot(ctx: Context) -> Context:
    """
    Step E (Buy Lot 5mnt)

    Kontrak tegas:
    - Hanya proses emiten gate OK dari Step D
    - Anchor token '%' wajib ada (tanpa fallback)
    - Jika gagal OCR => None (ditangani Step G_guard nanti)
    """

    cfg = BuyLotConfig()

    # NOTE: service versi OTSU sudah tidak pakai bin_threshold
    svc = BuyLotOcrService(
        psm=cfg.psm,
        whitelist=cfg.whitelist,
        upscale=cfg.upscale,
    )

    # Step D wajib ada
    if not ctx.footer_decisions:
        raise RuntimeError("Step E butuh ctx.footer_decisions dari Step D (belum ada).")

    ok_emitens = {
        em for em, dec in (ctx.footer_decisions or {}).items()
        if dec.gate == FooterGate.OK
    }

    items_ok = [it for it in ctx.total_buy_lot_5mnt if it.emiten in ok_emitens]
    results = svc.run(items_ok)

    # simpan ke context
    ctx.total_buy_lot_5mnt_values = {r.emiten: r.value for r in results}

    # tulis CSV debug
    tanggal_folder = tanggal_str(settings.DATE_FOLDER_FORMAT)
    csv_dir = settings.OUTPUT_DIR / "csv" / tanggal_folder
    pastikan_folder(csv_dir)
    ts = waktu_str(settings.TIME_FILENAME_FORMAT)
    csv_path = csv_dir / f"csv_buy_lot_5mnt_{ts}.csv"
    _tulis_csv(ctx.total_buy_lot_5mnt_values, csv_path)
    ctx.csv_buy_lot_5mnt_path = str(csv_path)

    # ringkas log
    ok_total = len(ok_emitens)
    processed = len(items_ok)
    none_count = sum(1 for r in results if r.value is None)
    print(f"[E_buy_lot] gate_OK={ok_total} processed={processed} ocr_none={none_count}")
    if none_count:
        fails = [r for r in results if r.value is None][:10]
        for r in fails:
            print(f"[E_buy_lot][fail] {r.emiten} => None | {r.raw_debug}")

    return ctx
