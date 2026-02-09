# pipeline/types.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from PIL import Image


@dataclass(frozen=True)
class HargaItem:
    """
    Item harga yang dikirim dari Step B_roi -> Step C_harga via Context (in-memory).
    """
    emiten: str
    image: Image.Image  # crop area harga (PIL Image)


@dataclass
class Context:
    """
    Data bus antar step (sesuai arsitektur PSSC).
    Hanya Context yang boleh membawa data dari step ke step.
    """

    # Input untuk Step C_harga (diisi Step B_roi kalau sudah produksi in-memory)
    harga_items: List[HargaItem] = field(default_factory=list)

    # Output Step C_harga
    csv_harga_path: Optional[str] = None
