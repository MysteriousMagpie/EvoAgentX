from abc import ABC, abstractmethod
from typing import Iterable

class MemoryStore(ABC):
    @abstractmethod
    def save(self, obj: "MemoryObject") -> None: ...

    @abstractmethod
    def load(self, obj_id: str) -> "MemoryObject | None": ...

    @abstractmethod
    def delete(self, obj_id: str) -> None: ...

    @abstractmethod
    def all(self) -> Iterable["MemoryObject"]: ...
