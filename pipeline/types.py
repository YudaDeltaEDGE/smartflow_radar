# pipeline/types.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
from PIL import Image

@dataclass(frozen=True)
class HargaItem:
    emiten: str
    image: Image.Image

@dataclass(frozen=True)
class FooterCekItem:
    emiten: str
    image: Image.Image

class FooterGate(str, Enum):
    OK = "OK"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    WRONG_TAB = "WRONG_TAB"
    UNKNOWN = "UNKNOWN"

@dataclass(frozen=True)
class FooterDecision:
    gate: FooterGate
    raw_text: str = ""

@dataclass
class Context:
    harga_items: List[HargaItem] = field(default_factory=list)
    footer_cek_items: List[FooterCekItem] = field(default_factory=list)

    # hasil step C
    csv_harga_path: Optional[str] = None

    # hasil step D (flag yang kamu mau)
    footer_decisions: Dict[str, FooterDecision] = field(default_factory=dict)

    # info global layar (optional tapi berguna)
    screen_mode: Optional[str] = None  # e.g. "time_ok" / "wrong_tab"
    capture_attempt: int = 0
