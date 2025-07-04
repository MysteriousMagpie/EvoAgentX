import importlib
from typing import TYPE_CHECKING

from ..storages import storages_config

if TYPE_CHECKING:  # pragma: no cover - only for type checking
    from ..storages.storages_config import DBConfig, VectorStoreConfig, GraphStoreConfig


def load_class(class_type: str):
    """
    Dynamically load a class from a module path.

    Attributes:
        class_type (str): Fully qualified class path (e.g., 'module.submodule.ClassName').

    Returns:
        type: The loaded class.

    Raises:
        ImportError: If the module or class cannot be imported.
        AttributeError: If the class is not found in the module.
    """
    module_path, class_name = class_type.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class DBStoreFactory:
    """
    Factory class for creating database store instances based on provider and configuration.
    Maps provider names to specific database store classes.
    """
    provider_to_class = {
        "sqlite": "evoagentx.storages.db_stores.sqlite.SQLite",
        "postgresql": "evoagentx.storages.db_stores.postgresql.PostgreSQL",
    }

    @classmethod
    def create(cls, provider_name: str, config: 'DBConfig'):
        """
        Create a database store instance for the specified provider.

        Attributes:
            provider_name (str): Name of the database provider (e.g., 'sqlite', 'postgresql').
            config (DBConfig): Configuration for the database store.

        Returns:
            DBStoreBase: An instance of the database store.

        Raises:
            ValueError: If the provider is not supported.
        """
        if isinstance(config, storages_config.DBConfig):
            config_dict = config.model_dump()
        else:
            config_dict = config
        
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            db_store_class = load_class(class_type)
            return db_store_class(**config_dict)
        else:
            raise ValueError(f"Unsupported Database provider: {provider_name}")


class VectorStoreFactory:
    provider_to_class = {
        "qdrant": "mem0.vector_stores.qdrant.Qdrant",
        "chroma": "mem0.vector_stores.chroma.ChromaDB",
        "faiss":  "mem0.vector_stores.faiss.FAISS",
    }

    @classmethod
    def create(cls, config: "VectorStoreConfig | dict"):
        """Create a vector store instance from the provided configuration."""

        if isinstance(config, storages_config.VectorStoreConfig):
            cfg_dict = config.model_dump()
            provider = config.provider
        else:
            cfg_dict = dict(config)
            provider = cfg_dict.get("provider", "")

        class_path = cls.provider_to_class.get(provider)
        if not class_path:
            raise ValueError(f"Unsupported Vector-store provider: {provider}")

        vec_cls = load_class(class_path)
        return vec_cls(**cfg_dict)

# Factory for creating graph store instances
class GraphStoreFactory:
    """Factory for creating graph store instances."""

    provider_to_class = {
        "neo4j": "evoagentx.storages.graph_stores.neo4j.Neo4jGraphStore",
    }

    @classmethod
    def create(cls, config: "GraphStoreConfig | dict"):
        """Create a graph store instance from configuration."""

        if isinstance(config, storages_config.GraphStoreConfig):
            cfg_dict = config.model_dump()
            provider = config.provider
        else:
            cfg_dict = dict(config)
            provider = cfg_dict.get("provider", "")

        class_path = cls.provider_to_class.get(provider)
        if not class_path:
            raise ValueError(f"Unsupported Graph-store provider: {provider}")

        graph_cls = load_class(class_path)
        return graph_cls(**cfg_dict)
