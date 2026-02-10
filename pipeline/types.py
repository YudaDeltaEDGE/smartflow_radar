# pipeline/types.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from PIL import Image


@dataclass(frozen=True)
class HargaItem:
    emiten: str
    image: Image.Image


@dataclass(frozen=True)
class FooterCekItem:
    emiten: str
    image: Image.Image


@dataclass
class Context:
    harga_items: List[HargaItem] = field(default_factory=list)
    footer_cek_items: List[FooterCekItem] = field(default_factory=list)

    # optional outputs
    csv_harga_path: Optional[str] = None
