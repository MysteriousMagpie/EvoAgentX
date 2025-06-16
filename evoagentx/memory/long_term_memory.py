
from .memory import BaseMemory
from ..storages.base import StorageHandler


class LongTermMemory(BaseMemory):

    """Long-term persistent memory container.

    This class extends :class:`BaseMemory` and relies on a
    :class:`~evoagentx.storages.base.StorageHandler` instance to save
    and load messages to an external backend such as a database or
    vector store.

    Example:
        >>> handler = StorageHandler(...)
        >>> memory = LongTermMemory(storage=handler)
        >>> memory.add_message(msg)
        >>> handler.save_memory(memory.model_dump())

    Attributes:
        storage: StorageHandler used to persist memory data.
    """

    storage: StorageHandler
    # rag_engine = ...
    pass


