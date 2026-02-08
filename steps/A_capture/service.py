# steps/A_capture/service.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import mss
from PIL import Image

@dataclass(frozen=True)
class HasilCapture:
    monitor_index: int   # 1..N (mengikuti mss)
    path_file: Path

class CaptureService:
    def __init__(self, output_dir: Path, ext: str = "png"):
        self.output_dir = output_dir
        self.ext = ext.lower().lstrip(".")

    def _nama_file(self, kode_pc: str, monitor_ke: int, ts: str) -> str:
        # Syarat dokumen: mengandung pc1, m1, timestamp :contentReference[oaicite:2]{index=2}
        # Format: pc1_m1_2026-02-08_01-23-45.png
        return f"{kode_pc}_m{monitor_ke}_{ts}.{self.ext}"

    def capture_semua_monitor(self, kode_pc: str, ts: str) -> List[HasilCapture]:
        hasil: List[HasilCapture] = []
        with mss.mss() as sct:
            # mss.monitors[0] = gabungan semua monitor (virtual screen)
            # mss.monitors[1:] = monitor 1..N
            monitors = sct.monitors[1:]

            for idx, mon in enumerate(monitors, start=1):
                out_name = self._nama_file(kode_pc=kode_pc, monitor_ke=idx, ts=ts)
                out_path = self.output_dir / out_name

                shot = sct.grab(mon)  # raw BGRA
                img = Image.frombytes("RGB", shot.size, shot.rgb)
                img.save(out_path)

                hasil.append(HasilCapture(monitor_index=idx, path_file=out_path))

        return hasil
