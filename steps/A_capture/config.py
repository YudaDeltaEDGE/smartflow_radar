# steps/A_capture/config.py

from dataclasses import dataclass

@dataclass(frozen=True)
class CaptureConfig:
    ext: str = "png"
