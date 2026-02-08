# steps/A_capture/service.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

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
        active_monitors: Sequence[int] = (1,),
    ):
        self.raw_dir = raw_dir
        self.ext = ext.lower().lstrip(".")
        self.crop_top = max(0, int(crop_top))
        self.crop_bottom = max(0, int(crop_bottom))
        self.crop_left = max(0, int(crop_left))
        self.crop_right = max(0, int(crop_right))

        # Simpan monitor aktif sebagai set untuk lookup cepat
        self.active_monitors = {int(m) for m in active_monitors if int(m) > 0}

    def _nama_file(self, kode_pc: str, monitor_ke: int, ts: str) -> str:
        return f"{kode_pc}_m{monitor_ke}_{ts}.{self.ext}"

    def _apply_crop(self, img: Image.Image) -> Image.Image:
        w, h = img.size
        left = min(max(self.crop_left, 0), w)
        top = min(max(self.crop_top, 0), h)
        right = min(max(w - self.crop_right, 0), w)
        bottom = min(max(h - self.crop_bottom, 0), h)

        if right <= left or bottom <= top:
            return img
        return img.crop((left, top, right, bottom))

    def capture_monitor_terpilih(self, kode_pc: str, ts: str) -> List[HasilCapture]:
        hasil: List[HasilCapture] = []

        with mss.mss() as sct:
            monitors = sct.monitors  # [0]=virtual, [1..N]=monitor

            max_idx = len(monitors) - 1
            target = [m for m in sorted(self.active_monitors) if 1 <= m <= max_idx]

            for idx in target:
                mon = monitors[idx]
                out_name = self._nama_file(kode_pc, idx, ts)
                out_path = self.raw_dir / out_name

                shot = sct.grab(mon)
                img = Image.frombytes("RGB", shot.size, shot.rgb)
                img = self._apply_crop(img)
                img.save(out_path)

                hasil.append(HasilCapture(monitor_index=idx, path_file=out_path))

        return hasil

