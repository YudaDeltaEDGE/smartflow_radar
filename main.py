# main.py

from __future__ import annotations

from steps.A_capture.step import jalankan_step_A_capture
from steps.B_roi.step import jalankan_step_B_roi
from steps.C_harga.step import jalankan_step_C_harga
from steps.D_footer_cek.step import jalankan_step_D_footer_cek
from steps.E_buy_lot.step import jalankan_step_E_buy_lot

from pipeline.types import Context, FooterGate


def main() -> None:
    print("=== STEP A: CAPTURE ===")
    hasil_a = jalankan_step_A_capture()
    for h in hasil_a:
        print(f"Raw: m{h.monitor_index} -> {h.path_file}")

    ctx = Context()

    print("\n=== STEP B: ROI (in-memory) ===")
    ctx = jalankan_step_B_roi(ctx)
    print(f"Total harga_items: {len(ctx.harga_items)}")
    print(f"Total footer_cek_items: {len(ctx.footer_cek_items)}")
    print(f"Total total_buy_lot_5mnt: {len(ctx.total_buy_lot_5mnt)}")

    print("\n=== STEP C: OCR HARGA (Tesseract) ===")
    ctx = jalankan_step_C_harga(ctx)
    print(f"CSV harga tersimpan: {ctx.csv_harga_path}")

    print("\n=== STEP D: FOOTER CEK (GATE) ===")
    ctx = jalankan_step_D_footer_cek(ctx)

    print("\n=== RINGKASAN D_footer_cek (footer_decisions) ===")
    if not ctx.footer_decisions:
        print("footer_decisions kosong. Cek Step B_roi & pipeline/types.py.")
        return

    print(f"screen_mode: {ctx.screen_mode}")

    non_ok = {em: dec for em, dec in ctx.footer_decisions.items() if dec.gate != FooterGate.OK}
    if non_ok:
        for em, dec in non_ok.items():
            print(f"- {em}: {dec.gate.value} | text='{dec.raw_text}'")
    else:
        print("Semua emiten OK (ada %).")

    print("\n=== STEP E: OCR BUY LOT 5mnt (ANCHOR %) ===")
    ctx = jalankan_step_E_buy_lot(ctx)
    print(f"CSV buy lot tersimpan: {ctx.csv_buy_lot_5mnt_path}")

    # contoh ringkasan 10 emiten
    sample = list(sorted(ctx.total_buy_lot_5mnt_values.items()))[:10]
    print("\n=== SAMPLE total_buy_lot_5mnt_values (10) ===")
    for em, v in sample:
        print(f"{em}: {v}")


if __name__ == "__main__":
    main()
