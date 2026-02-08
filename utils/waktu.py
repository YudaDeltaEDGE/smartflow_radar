# utils/waktu.py
from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo

def timestamp_str(fmt: str) -> str:
    # Kamu di Indonesia (Asia/Makassar). Ini bikin timestamp konsisten.
    now = datetime.now(tz=ZoneInfo("Asia/Makassar"))
    return now.strftime(fmt)
