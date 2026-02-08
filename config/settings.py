# config/settings.py

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

@dataclass(frozen=True)
class Settings:
    ROOT_DIR: Path = Path(__file__).resolve().parents[1]
    OUTPUT_DIR: Path = ROOT_DIR / "output"
    IMAGES_DIR: Path = OUTPUT_DIR / "images"

    DATE_FOLDER_FORMAT: str = "%Y-%m-%d"
    TIME_FILENAME_FORMAT: str = "%H-%M-%S"

    # ====== STEP A CAPTURE: CROP ======
    CAPTURE_CROP_TOP_PX: int = 92
    CAPTURE_CROP_BOTTOM_PX: int = 36
    CAPTURE_CROP_LEFT_PX: int = 0
    CAPTURE_CROP_RIGHT_PX: int = 4

    # ====== STEP A CAPTURE: MONITOR AKTIF ======
    # Sekarang: capture monitor 1 saja.
    # Nanti kalau sudah siap: ubah jadi (1,2,3,4)
    ACTIVE_MONITORS: Tuple[int, ...] = (1,)


settings = Settings()


