import unittest

from evoagentx.agents.agent import Agent
from evoagentx.models.model_configs import LiteLLMConfig
from evoagentx.memory import LongTermMemory, MemoryManager
from evoagentx.storages.base import StorageHandler
from evoagentx.storages.storages_config import StoreConfig, DBConfig


class TestAgentLongTermMemory(unittest.TestCase):
    def _storage(self):
        db_cfg = DBConfig(db_name="sqlite", path=":memory:")
        return StorageHandler(storageConfig=StoreConfig(dbConfig=db_cfg))

    def _llm_cfg(self):
        return LiteLLMConfig(model="gpt-4o-mini", openai_key="xxxxx")

    def test_enable_on_init(self):
        storage = self._storage()
        agent = Agent(
            name="a1",
            description="test",
            llm_config=self._llm_cfg(),
            storage_handler=storage,
            use_long_term_memory=True,
        )
        self.assertIsNotNone(agent.long_term_memory)
        self.assertIsNotNone(agent.long_term_memory_manager)
        self.assertIs(agent.long_term_memory_manager.memory, agent.long_term_memory)
        self.assertIs(agent.long_term_memory_manager.storage_handler, storage)

    def test_enable_later(self):
        storage = self._storage()
        agent = Agent(
            name="a2",
            description="test",
            llm_config=self._llm_cfg(),
            storage_handler=storage,
        )
        self.assertIsNone(agent.long_term_memory)
        agent.use_long_term_memory = True
        agent.init_long_term_memory()
        self.assertIsNotNone(agent.long_term_memory)
        self.assertIsNotNone(agent.long_term_memory_manager)

    def test_preserve_instances(self):
        storage = self._storage()
        mem = LongTermMemory(storage=storage)
        mgr = MemoryManager(storage_handler=storage, memory=mem)
        agent = Agent(
            name="a3",
            description="test",
            llm_config=self._llm_cfg(),
            storage_handler=storage,
            use_long_term_memory=True,
            long_term_memory=mem,
            long_term_memory_manager=mgr,
        )
        self.assertIs(agent.long_term_memory, mem)
        self.assertIs(agent.long_term_memory_manager, mgr)
        # re-init should not replace
        agent.init_long_term_memory()
        self.assertIs(agent.long_term_memory, mem)
        self.assertIs(agent.long_term_memory_manager, mgr)

    def test_existing_memory_no_manager(self):
        storage = self._storage()
        mem = LongTermMemory(storage=storage)
        agent = Agent(
            name="a4",
            description="test",
            llm_config=self._llm_cfg(),
            storage_handler=storage,
            use_long_term_memory=True,
            long_term_memory=mem,
        )
        self.assertIs(agent.long_term_memory_manager.memory, mem)
        self.assertIs(agent.long_term_memory_manager.storage_handler, storage)


if __name__ == "__main__":
    unittest.main()
