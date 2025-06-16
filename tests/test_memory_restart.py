from evoagentx.memory.sqlite_store import SQLiteStore
from evoagentx.memory.memory_object import MemoryObject


def test_state_persists(tmp_path):
    path = tmp_path / "mem.db"
    store1 = SQLiteStore(path=path)
    store1.save(MemoryObject(id="foo", content="bar"))

    store2 = SQLiteStore(path=path)
    reloaded = store2.load("foo")

    assert reloaded is not None
    assert reloaded.content == "bar"
