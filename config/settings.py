# config/settings.py

from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    # Root project (folder yang sama dengan main.py)
    ROOT_DIR: Path = Path(__file__).resolve().parents[1]

    # Output utama
    OUTPUT_DIR: Path = ROOT_DIR / "output"

    # Output baru sesuai permintaan:
    # output/images/YYYY-MM-DD/{Raw,Tiles,Header,Footer}
    IMAGES_DIR: Path = OUTPUT_DIR / "images"

    # Format folder tanggal
    DATE_FOLDER_FORMAT: str = "%Y-%m-%d"

    # Format timestamp untuk nama file (sesuai contoh kamu: 08-17-36)
    TIME_FILENAME_FORMAT: str = "%H-%M-%S"

    # ====== STEP A CAPTURE: CROP VERTIKAL ======
    # Buang piksel dari atas (di atas baris 1)
    CAPTURE_CROP_TOP_PX: int = 92

    # Buang piksel dari bawah (di bawah baris 8)
    CAPTURE_CROP_BOTTOM_PX: int = 36

    # Jika suatu saat kamu ingin crop kiri/kanan juga:
    CAPTURE_CROP_LEFT_PX: int = 0
    CAPTURE_CROP_RIGHT_PX: int = 4


settings = Settings()

