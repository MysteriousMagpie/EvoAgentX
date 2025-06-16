import pytest
import fakeredis

from evoagentx.memory.redis_store import RedisStore
from evoagentx.memory.memory_object import MemoryObject

@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr('evoagentx.memory.redis_store.redis.Redis', lambda **kwargs: fake)
    return fake

def test_save_and_load():
    store = RedisStore()
    obj = MemoryObject(id='a', content={'x': 42})
    store.save(obj)
    loaded = store.load('a')
    assert loaded is not None
    assert loaded.id == 'a'
    assert loaded.content == {'x': 42}

def test_delete():
    store = RedisStore()
    obj = MemoryObject(id='b', content='foo')
    store.save(obj)
    store.delete('b')
    assert store.load('b') is None

def test_all():
    store = RedisStore()
    objs = [MemoryObject(id=str(i), content=i) for i in range(3)]
    for o in objs:
        store.save(o)
    all_objs = store.all()
    assert {o.id for o in all_objs} == {'0','1','2'}

