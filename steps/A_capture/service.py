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
    def __init__(self, output_dir: Path, ext: str = "png"):
        self.output_dir = output_dir
        self.ext = ext.lower().lstrip(".")

    def _nama_file(self, kode_pc: str, monitor_ke: int, ts: str) -> str:
        return f"{kode_pc}_m{monitor_ke}_{ts}.{self.ext}"

    def capture_semua_monitor(
        self,
        kode_pc: str,
        ts: str,
        monitor_aktif: int | None = None
    ) -> List[HasilCapture]:

        hasil: List[HasilCapture] = []

        with mss.mss() as sct:
            monitors = sct.monitors[1:]  # skip virtual monitor

            # Jika hanya 1 monitor yang ingin dicapture
            if monitor_aktif is not None:
                if monitor_aktif < 1 or monitor_aktif > len(monitors):
                    raise ValueError("Monitor tidak tersedia.")
                monitors = [monitors[monitor_aktif - 1]]

            for idx, mon in enumerate(
                monitors,
                start=1 if monitor_aktif is None else monitor_aktif
            ):
                out_name = self._nama_file(
                    kode_pc=kode_pc,
                    monitor_ke=idx,
                    ts=ts
                )

                out_path = self.output_dir / out_name

                shot = sct.grab(mon)
                img = Image.frombytes("RGB", shot.size, shot.rgb)
                img.save(out_path)

                hasil.append(
                    HasilCapture(
                        monitor_index=idx,
                        path_file=out_path
                    )
                )

        return hasil

