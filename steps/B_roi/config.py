# steps/B_roi/config.py

from dataclasses import dataclass

@dataclass(frozen=True)
class RoiConfig:
    ext: str = "png"

