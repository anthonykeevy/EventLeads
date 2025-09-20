from __future__ import annotations

import threading
import time
from typing import Optional, Dict, Tuple

from sqlalchemy import text
from app.core.db import SessionLocal


class _SettingsCache:
    def __init__(self, ttl_seconds: int = 300) -> None:
        self._ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        # key -> (value, expires_at_epoch)
        self._cache: Dict[str, Tuple[Optional[str], float]] = {}

    def get(self, key: str) -> Optional[str]:
        now = time.time()
        with self._lock:
            if key in self._cache:
                value, expires_at = self._cache[key]
                if now < expires_at:
                    return value
                # expired
                self._cache.pop(key, None)
        return None

    def set(self, key: str, value: Optional[str]) -> None:
        with self._lock:
            self._cache[key] = (value, time.time() + self._ttl_seconds)

    def invalidate(self, key: Optional[str] = None) -> None:
        with self._lock:
            if key is None:
                self._cache.clear()
            else:
                self._cache.pop(key, None)


class SettingsService:
    """Loads global settings from the database with a simple in-memory TTL cache.

    Schema: GlobalSetting(SettingKey/Key, SettingValue/Value, ValueType, Scope)
    """

    def __init__(self, cache_ttl_seconds: int = 300) -> None:
        self._cache = _SettingsCache(ttl_seconds=cache_ttl_seconds)

    def _load_from_db(self, key: str) -> Optional[str]:
        with SessionLocal() as session:
            row = session.execute(
                text(
                    "SELECT COALESCE(SettingValue, [Value]) as V "
                    "FROM GlobalSetting WHERE COALESCE(SettingKey, [Key]) = :k"
                ),
                {"k": key},
            ).first()
            return row[0] if row and row[0] is not None else None

    def get_string(self, key: str, default: Optional[str] = None) -> Optional[str]:
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        value = self._load_from_db(key)
        # cache even when None to avoid hot loops on missing keys
        self._cache.set(key, value)
        return value if value is not None else default

    def get_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        value = self.get_string(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def get_bool(self, key: str, default: Optional[bool] = None) -> Optional[bool]:
        value = (self.get_string(key) or "").strip().lower()
        if value in {"1", "true", "yes", "on"}:
            return True
        if value in {"0", "false", "no", "off"}:
            return False
        return default

    def invalidate(self, key: Optional[str] = None) -> None:
        self._cache.invalidate(key)

    # Convenience accessors
    def get_invite_token_ttl_hours(self) -> int:
        return int(self.get_int("invite_token_ttl_hours", default=48) or 48)

    def get_invite_daily_limit(self) -> int:
        return int(self.get_int("invite_daily_limit", default=10) or 10)


# Singleton-like instance for app-wide use
settings_service = SettingsService()
