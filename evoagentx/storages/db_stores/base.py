from abc import ABC, abstractmethod
from typing import Optional, Literal, Any, Dict, List


# Abstract base class for database store implementations
class DBStoreBase(ABC):
    """
    Abstract base class defining the interface for database storage operations.
    Subclasses must implement methods for inserting, deleting, updating, and retrieving metadata.
    """

    @abstractmethod
    def insert(self, metadata, store_type: Optional[Literal["memory", "agent", "workflow", "history"]], table=None) -> None:
        """
        Insert metadata into a specified table.
        """
        pass

    @abstractmethod
    def insert_memory(self, metadata, store_type: Optional[Literal["memory", "agent", "workflow", "history"]], table=None) -> None:
        """
        Insert memory metadata into a specified table.
        """
        pass

    @abstractmethod
    def insert_agent(self, metadata, store_type: Optional[Literal["memory", "agent", "workflow", "history"]], table=None) -> None:
        """
        Insert agent metadata into a specified table.
        """
        pass

    @abstractmethod
    def insert_workflow(self, metadata, store_type: Optional[Literal["memory", "agent", "workflow", "history"]], table=None) -> None:
        """
        Insert workflow metadata into a specified table.
        """
        pass

    @abstractmethod
    def insert_history(self, metadata, store_type: Optional[Literal["memory", "agent", "workflow", "history"]], table=None) -> None:
        """
        Insert history metadata into a specified table.
        """
        pass

    @abstractmethod
    def delete(self, metadata_id, store_type: Optional[Literal["memory", "agent", "workflow", "history"]], table=None) -> bool:
        """
        Delete metadata by its ID from a specified table.
        Returns True if deletion was successful, False otherwise.
        """
        pass

    @abstractmethod
    def update(self, metadata_id, new_metadata=None, 
               store_type: Optional[Literal["memory", "agent", "workflow", "history"]]=None, table=None) -> bool:
        """
        Update metadata by its ID in a specified table.
        Returns True if update was successful, False otherwise.
        """
        pass

    @abstractmethod
    def get_by_id(self, metadata_id, store_type: Optional[Literal["memory", "agent", "workflow", "history"]], table=None) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata by its ID from a specified table.
        Returns a dictionary if found, or None.
        """
        pass

    @abstractmethod
    def col_info(self) -> List[Dict[str, Any]]:
        """
        Retrieve information about the database collections (tables).
        Returns a list of dictionaries with table and column info.
        """
        pass