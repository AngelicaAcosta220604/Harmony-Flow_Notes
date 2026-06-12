# utils/local_time.py

import time

def now_local_iso() -> str:
    """Возвращает текущее локальное время в ISO-формате"""
    return time.strftime("%Y-%m-%dT%H:%M:%S")