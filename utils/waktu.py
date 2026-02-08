# utils/waktu.py

from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Makassar")

def tanggal_str(fmt: str) -> str:
    return datetime.now(tz=TZ).strftime(fmt)

def waktu_str(fmt: str) -> str:
    return datetime.now(tz=TZ).strftime(fmt)

