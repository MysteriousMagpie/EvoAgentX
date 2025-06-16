import sqlite3
import json
from pathlib import Path
from typing import Iterable

from .store import MemoryStore
from .memory_object import MemoryObject


class SQLiteStore(MemoryStore):
    """SQLite-backed implementation of ``MemoryStore``."""

    def __init__(self, path: str | Path = "memory.db"):
        self._path = Path(path)
        self._conn = sqlite3.connect(self._path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, data TEXT)"
        )

    def save(self, obj: MemoryObject) -> None:
        data = json.dumps(obj.to_dict())
        self._conn.execute(
            "REPLACE INTO memory (id, data) VALUES (?, ?)", (obj.id, data)
        )
        self._conn.commit()

    def load(self, obj_id: str) -> MemoryObject | None:
        row = self._conn.execute(
            "SELECT data FROM memory WHERE id = ?", (obj_id,)
        ).fetchone()
        return MemoryObject.from_dict(json.loads(row[0])) if row else None

    def delete(self, obj_id: str) -> None:
        self._conn.execute("DELETE FROM memory WHERE id = ?", (obj_id,))
        self._conn.commit()

    def all(self) -> Iterable[MemoryObject]:
        rows = self._conn.execute("SELECT data FROM memory").fetchall()
        return [MemoryObject.from_dict(json.loads(r[0])) for r in rows]
