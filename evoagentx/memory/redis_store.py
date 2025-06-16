import json
from typing import Iterable
import redis

from .store import MemoryStore
from .memory_object import MemoryObject

class RedisStore(MemoryStore):
    """Redis-backed implementation of ``MemoryStore``.

    Args:
        host: Redis host (default ``'localhost'``)
        port: Redis port (default ``6379``)
        db: Redis database number (default ``0``)
    """

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self._client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def save(self, obj: MemoryObject) -> None:
        data = json.dumps(obj.to_dict())
        self._client.set(obj.id, data)

    def load(self, obj_id: str) -> MemoryObject | None:
        raw = self._client.get(obj_id)
        return MemoryObject.from_dict(json.loads(raw)) if raw is not None else None

    def delete(self, obj_id: str) -> None:
        self._client.delete(obj_id)

    def all(self) -> Iterable[MemoryObject]:
        keys = self._client.keys()
        objects = []
        for k in keys:
            raw = self._client.get(k)
            if raw:
                objects.append(MemoryObject.from_dict(json.loads(raw)))
        return objects
