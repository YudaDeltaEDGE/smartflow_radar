# utils/path.py

from __future__ import annotations
from pathlib import Path

def pastikan_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def baca_teks_rapi(path: Path, default: str = "pc1") -> str:
    try:
        teks = path.read_text(encoding="utf-8").strip()
        return teks if teks else default
    except FileNotFoundError:
        return default

