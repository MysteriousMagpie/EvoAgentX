from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class MemoryObject:
    """Simple serializable memory unit."""

    id: str
    content: Any

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "content": self.content}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryObject":
        return cls(id=data["id"], content=data["content"])
