from steps.A_capture.step import jalankan_step_A_capture

def main() -> None:
    hasil = jalankan_step_A_capture()
    print("=== STEP A CAPTURE SELESAI ===")
    for h in hasil:
        print(f"monitor m{h.monitor_index} -> {h.path_file}")

if __name__ == "__main__":
    main()
