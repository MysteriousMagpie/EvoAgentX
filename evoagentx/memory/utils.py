"""Helper utilities for memory initialization."""

from typing import Optional, Union, Dict, Any

from .long_term_memory import LongTermMemory
from .memory_manager import MemoryManager
from ..storages.base import StorageHandler


def create_long_term_memory(
    storage_handler: StorageHandler,
    memory: Optional[Union[LongTermMemory, Dict[str, Any]]] = None,
) -> LongTermMemory:
    """Return a ``LongTermMemory`` instance bound to ``storage_handler``.

    If ``memory`` is ``None`` a new instance will be created. If ``memory`` is a
    dictionary it will be used to construct the object. Existing instances will
    be returned unchanged, except that their ``storage`` attribute is populated
    when missing.
    """
    if memory is None:
        return LongTermMemory(storage=storage_handler)
    if isinstance(memory, dict):
        memory.setdefault("storage", storage_handler)
        return LongTermMemory(**memory)
    if getattr(memory, "storage", None) is None:
        memory.storage = storage_handler
    return memory


def create_memory_manager(
    storage_handler: StorageHandler,
    memory_manager: Optional[Union[MemoryManager, Dict[str, Any]]] = None,
    memory: Optional[Union[LongTermMemory, Dict[str, Any]]] = None,
) -> MemoryManager:
    """Return a ``MemoryManager`` instance bound to ``storage_handler``.

    ``memory_manager`` and ``memory`` may be provided as instances or dictionaries.
    Existing objects are reused and never replaced.
    """
    if isinstance(memory_manager, dict):
        memory_manager.setdefault("storage_handler", storage_handler)
        if "memory" in memory_manager:
            mm_memory = create_long_term_memory(storage_handler, memory_manager["memory"])
        else:
            mm_memory = create_long_term_memory(storage_handler, memory)
        memory_manager["memory"] = mm_memory
        return MemoryManager(**memory_manager)

    if memory_manager is None:
        mm_memory = create_long_term_memory(storage_handler, memory)
        return MemoryManager(storage_handler=storage_handler, memory=mm_memory)

    # existing manager instance
    if getattr(memory_manager, "storage_handler", None) is None:
        memory_manager.storage_handler = storage_handler
    if getattr(memory_manager, "memory", None) is None:
        memory_manager.memory = create_long_term_memory(storage_handler, memory)
    else:
        memory_manager.memory = create_long_term_memory(storage_handler, memory_manager.memory)
    return memory_manager

