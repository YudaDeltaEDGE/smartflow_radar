# main.py

from steps.A_capture.step import jalankan_step_A_capture
from steps.B_roi.step import jalankan_step_B_roi
from steps.C_harga.step import jalankan_step_C_harga

from pipeline.types import Context


def main() -> None:
    print("=== STEP A: CAPTURE ===")
    hasil_a = jalankan_step_A_capture()
    for h in hasil_a:
        print(f"Raw: m{h.monitor_index} -> {h.path_file}")

    ctx = Context()

    print("\n=== STEP B: ROI (in-memory harga_items) ===")
    ctx = jalankan_step_B_roi(ctx)
    print(f"Total harga_items: {len(ctx.harga_items)}")

    print("\n=== STEP C: OCR HARGA (Tesseract) ===")
    ctx = jalankan_step_C_harga(ctx)
    print(f"CSV harga tersimpan: {ctx.csv_harga_path}")


if __name__ == "__main__":
    main()
