# steps/A_capture/config.py
from dataclasses import dataclass

@dataclass(frozen=True)
class CaptureConfig:
    # Kalau mau save sebagai PNG (lossless, aman untuk OCR/angka)
    ext: str = "png"
