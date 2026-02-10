# main.py

from __future__ import annotations

from steps.A_capture.step import jalankan_step_A_capture
from steps.B_roi.step import jalankan_step_B_roi
from steps.C_harga.step import jalankan_step_C_harga
from steps.D_footer_cek.step import jalankan_step_D_footer_cek

from pipeline.types import Context, FooterGate


def main() -> None:
    print("=== STEP A: CAPTURE ===")
    hasil_a = jalankan_step_A_capture()
    for h in hasil_a:
        print(f"Raw: m{h.monitor_index} -> {h.path_file}")

    ctx = Context()

    print("\n=== STEP B: ROI (in-memory harga_items + footer_cek_items) ===")
    ctx = jalankan_step_B_roi(ctx)
    print(f"Total harga_items: {len(ctx.harga_items)}")
    print(f"Total footer_cek_items: {len(ctx.footer_cek_items)}")

    print("\n=== STEP C: OCR HARGA (Tesseract) ===")
    ctx = jalankan_step_C_harga(ctx)
    print(f"CSV harga tersimpan: {ctx.csv_harga_path}")

    print("\n=== STEP D: FOOTER CEK (GATE) ===")
    ctx = jalankan_step_D_footer_cek(ctx)

    # Ringkasan hasil Step D (biar jelas waktu test)
    print("\n=== RINGKASAN D_footer_cek (footer_decisions) ===")
    if not ctx.footer_decisions:
        print("footer_decisions kosong.")
        print("Cek: pipeline/types.py sudah update (FooterGate, FooterDecision, footer_decisions).")
        print("Cek: Step B_roi mengisi ctx.footer_cek_items.")
        return

    print(f"screen_mode: {ctx.screen_mode}")

    non_ok = {em: dec for em, dec in ctx.footer_decisions.items() if dec.gate != FooterGate.OK}
    if non_ok:
        for em, dec in non_ok.items():
            print(f"- {em}: {dec.gate.value} | text='{dec.raw_text}'")
    else:
        print("Semua emiten OK (ada %).")


if __name__ == "__main__":
    main()
