from __future__ import annotations

import sqlite3
import time
from pathlib import Path

import requests


DEFAULT_CACHE_DB = Path('.cache/safe_lyrics_checker.sqlite')
DEFAULT_TTL_SECONDS = 7 * 24 * 60 * 60


class HttpCache:
    def __init__(self, db_path: Path = DEFAULT_CACHE_DB, ttl_seconds: int = DEFAULT_TTL_SECONDS):
        self.db_path = db_path
        self.ttl_seconds = ttl_seconds
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS http_cache (
                    url TEXT PRIMARY KEY,
                    fetched_at INTEGER NOT NULL,
                    body TEXT NOT NULL
                )
                """
            )

    def get_text(self, url: str) -> str:
        now = int(time.time())
        with self._connect() as conn:
            row = conn.execute(
                "SELECT fetched_at, body FROM http_cache WHERE url = ?", (url,)
            ).fetchone()
            if row is not None:
                fetched_at, body = row
                if now - int(fetched_at) <= self.ttl_seconds:
                    return str(body)

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        body = response.text

        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO http_cache (url, fetched_at, body) VALUES (?, ?, ?)",
                (url, now, body),
            )

        return body
