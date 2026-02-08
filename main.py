# main.py

from steps.A_capture.step import jalankan_step_A_capture
from steps.B_roi.step import jalankan_step_B_roi

def main() -> None:
    print("=== STEP A: CAPTURE ===")
    hasil_a = jalankan_step_A_capture()
    for h in hasil_a:
        print(f"Raw: m{h.monitor_index} -> {h.path_file}")

    print("\n=== STEP B: ROI (24 Tiles) ===")
    hasil_b = jalankan_step_B_roi()
    print(f"Total tiles dibuat: {len(hasil_b)}")
    for t in hasil_b[:5]:
        print(f"Tile contoh: {t.emiten} (r{t.row} c{t.col}) -> {t.path_file}")

if __name__ == "__main__":
    main()
