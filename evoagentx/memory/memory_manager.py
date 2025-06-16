from ..core.module import BaseModule
from ..storages.base import StorageHandler
from .long_term_memory import LongTermMemory


class MemoryManager(BaseModule):

    """High-level controller for :class:`LongTermMemory`.

    The manager orchestrates saving and loading of persistent memory
    through a :class:`~evoagentx.storages.base.StorageHandler`. In a
    typical setup it holds both a ``StorageHandler`` and a
    ``LongTermMemory`` instance:

    >>> handler = StorageHandler(config)
    >>> manager = MemoryManager(storage_handler=handler,
    ...                         memory=LongTermMemory(storage=handler))

    Attributes:
        storage_handler: Backend interface used for persistence.
        memory: The managed long-term memory instance.
    """

    storage_handler: StorageHandler
    memory: LongTermMemory

