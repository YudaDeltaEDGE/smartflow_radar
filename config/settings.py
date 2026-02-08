# config/settings.py

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class Settings:
    ROOT_DIR: Path = Path(__file__).resolve().parents[1]
    OUTPUT_DIR: Path = ROOT_DIR / "output"
    IMAGES_DIR: Path = OUTPUT_DIR / "images"

    TZ: str = "Asia/Makassar"

    # ======================================
    # MONITOR SETTING
    # ======================================
    # None  -> capture semua monitor
    # 1     -> hanya monitor 1
    # 2     -> hanya monitor 2
    # 3     -> dst
    MONITOR_AKTIF: int | None = 1
    # ======================================

    def folder_tanggal_hari_ini(self) -> Path:
        today = datetime.now(ZoneInfo(self.TZ)).strftime("%Y-%m-%d")
        return self.IMAGES_DIR / today

    def jam_sekarang(self) -> str:
        return datetime.now(ZoneInfo(self.TZ)).strftime("%H-%M-%S")


settings = Settings()
