# steps/A_capture/service.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import mss
from PIL import Image

@dataclass(frozen=True)
class HasilCapture:
    monitor_index: int
    path_file: Path

class CaptureService:
    def __init__(
        self,
        raw_dir: Path,
        ext: str = "png",
        crop_top: int = 0,
        crop_bottom: int = 0,
        crop_left: int = 0,
        crop_right: int = 0,
    ):
        self.raw_dir = raw_dir
        self.ext = ext.lower().lstrip(".")
        self.crop_top = max(0, int(crop_top))
        self.crop_bottom = max(0, int(crop_bottom))
        self.crop_left = max(0, int(crop_left))
        self.crop_right = max(0, int(crop_right))

    def _nama_file(self, kode_pc: str, monitor_ke: int, ts: str) -> str:
        # contoh: pc1_m1_08-17-36.png
        return f"{kode_pc}_m{monitor_ke}_{ts}.{self.ext}"

    def _apply_crop(self, img: Image.Image) -> Image.Image:
        w, h = img.size

        left = self.crop_left
        top = self.crop_top
        right = w - self.crop_right
        bottom = h - self.crop_bottom

        # safety clamp
        left = min(max(left, 0), w)
        right = min(max(right, 0), w)
        top = min(max(top, 0), h)
        bottom = min(max(bottom, 0), h)

        # Pastikan area valid
        if right <= left or bottom <= top:
            # Kalau setting crop kebesaran, jangan crash; fallback ke original
            return img

        return img.crop((left, top, right, bottom))

    def capture_semua_monitor(self, kode_pc: str, ts: str) -> List[HasilCapture]:
        hasil: List[HasilCapture] = []

        with mss.mss() as sct:
            monitors = sct.monitors[1:]  # monitor 1..N

            for idx, mon in enumerate(monitors, start=1):
                out_name = self._nama_file(kode_pc, idx, ts)
                out_path = self.raw_dir / out_name

                shot = sct.grab(mon)
                img = Image.frombytes("RGB", shot.size, shot.rgb)

                # Crop sesuai kebutuhan (buang atas/bawah, opsional kiri/kanan)
                img = self._apply_crop(img)

                img.save(out_path)
                hasil.append(HasilCapture(monitor_index=idx, path_file=out_path))

        return hasil
