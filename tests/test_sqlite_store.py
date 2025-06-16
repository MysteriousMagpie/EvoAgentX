import pytest
from evoagentx.memory.sqlite_store import SQLiteStore
from evoagentx.memory.memory_object import MemoryObject


@pytest.mark.parametrize(
    "case,obj_id,expected",
    [
        ("delete", "one", {"two"}),
        ("all", None, {"one", "two"}),
        ("load_missing", "ghost", None),
    ],
)
def test_sqlite_store_edge_cases(tmp_path, case, obj_id, expected):
    path = tmp_path / "mem.db"
    store = SQLiteStore(path=path)
    store.save(MemoryObject(id="one", content=1))
    store.save(MemoryObject(id="two", content=2))

    if case == "delete":
        store.delete(obj_id)
        # reopen to ensure persistence
        store = SQLiteStore(path=path)
        assert store.load(obj_id) is None
        assert {o.id for o in store.all()} == expected
    elif case == "all":
        # reload to ensure results come from DB
        store = SQLiteStore(path=path)
        assert {o.id for o in store.all()} == expected
    elif case == "load_missing":
        assert store.load(obj_id) is expected
