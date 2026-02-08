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

    # ===== STEP A (Crop Raw) =====
    CAPTURE_CROP_TOP_PX: int = 92
    CAPTURE_CROP_BOTTOM_PX: int = 36
    CAPTURE_CROP_LEFT_PX: int = 0
    CAPTURE_CROP_RIGHT_PX: int = 4

    # Monitor aktif (sementara 1 saja)
    ACTIVE_MONITORS: Tuple[int, ...] = (1,)

    # ===== STEP B (ROI Tiles) =====
    TILE_COLS: int = 3
    TILE_ROWS: int = 8


settings = Settings()
