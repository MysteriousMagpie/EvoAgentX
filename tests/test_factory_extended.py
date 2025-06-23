import pytest

from evoagentx.utils import factory



def test_dbstorefactory_create_with_dict(monkeypatch):
    class Dummy:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    monkeypatch.setattr(factory, "load_class", lambda path: Dummy)
    cfg = {"path": ":memory:"}
    obj = factory.DBStoreFactory.create("sqlite", cfg)
    assert isinstance(obj, Dummy)
    assert obj.kwargs["path"] == ":memory:"


def test_vectorstorefactory_create_with_dict(monkeypatch):
    class Dummy:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    monkeypatch.setattr(factory, "load_class", lambda path: Dummy)
    obj = factory.VectorStoreFactory.create({"provider": "qdrant", "foo": "bar"})
    assert isinstance(obj, Dummy)
    assert obj.kwargs["foo"] == "bar"


def test_graphstorefactory_create_with_dict(monkeypatch):
    class Dummy:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    monkeypatch.setattr(factory, "load_class", lambda path: Dummy)
    obj = factory.GraphStoreFactory.create({"provider": "neo4j", "uri": "bolt"})
    assert isinstance(obj, Dummy)
    assert obj.kwargs["uri"] == "bolt"
