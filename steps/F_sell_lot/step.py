# steps/F_sell_lot/step.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from config.settings import settings
from pipeline.types import Context, FooterGate
from utils.path import pastikan_folder
from utils.waktu import tanggal_str, waktu_str

from .config import SellLotConfig
from .service import SellLotService


def _tulis_csv(values: Dict[str, Optional[int]], csv_path: Path) -> None:
    lines = ["emiten,total_sell_lot_5mnt"]
    for em in sorted(values.keys()):
        v = values[em]
        lines.append(f"{em},{'' if v is None else v}")
    csv_path.write_text("\n".join(lines), encoding="utf-8")


def jalankan_step_F_sell_lot(ctx: Context) -> Context:
    """
    STEP F - OCR SELL LOT 5mnt (ANCHOR %)

    - Wajib menunggu Step D (footer_decisions)
    - Hanya proses emiten gate OK
    - OCR + parsing hasil ke ctx.total_sell_lot_5mnt_values
    - Tulis csv debug: csv_sell_lot_5mnt_<ts>.csv
    """

    # Step D wajib ada
    if not ctx.footer_decisions:
        raise RuntimeError("Step F butuh ctx.footer_decisions dari Step D (belum ada).")

    ok_emitens = {em for em, dec in ctx.footer_decisions.items() if dec.gate == FooterGate.OK}

    # hanya item yang OK
    items_ok = [it for it in ctx.total_sell_lot_5mnt if it.emiten in ok_emitens]

    cfg = SellLotConfig()
    svc = SellLotService(cfg)
    results = svc.run(items_ok)

    # simpan ke context
    ctx.total_sell_lot_5mnt_values = {r.emiten: r.value for r in results}

    # tulis CSV debug
    tanggal_folder = tanggal_str(settings.DATE_FOLDER_FORMAT)
    csv_dir = settings.OUTPUT_DIR / "csv" / tanggal_folder
    pastikan_folder(csv_dir)

    ts = waktu_str(settings.TIME_FILENAME_FORMAT)
    csv_path = csv_dir / f"csv_sell_lot_5mnt_{ts}.csv"
    _tulis_csv(ctx.total_sell_lot_5mnt_values, csv_path)
    ctx.csv_sell_lot_5mnt_path = str(csv_path)

    # ringkas log
    ok_total = len(ok_emitens)
    processed = len(items_ok)
    none_count = sum(1 for r in results if r.value is None)
    print(f"[F_sell_lot] gate_OK={ok_total} processed={processed} ocr_none={none_count}")
    if none_count:
        fails = [r for r in results if r.value is None][:10]
        for r in fails:
            print(f"[F_sell_lot][fail] {r.emiten} => None | {r.raw_debug}")

    return ctx
