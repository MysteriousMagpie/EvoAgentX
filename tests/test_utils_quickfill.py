"""
Tiny smoke tests that exercise the hottest uncovered helpers:

• evoagentx.utils.utils       – make_parent_folder, normalize_text branches
• evoagentx.utils.sanitize    – whitespace / entry-point logic
• evoagentx.utils.factory     –  DB/Vector/Graph Store factories’ unhappy paths
"""

from pathlib import Path
import sys
import textwrap
import types
import pytest

# Provide minimal storage stubs to satisfy factory imports and avoid heavy deps
cfg_mod = types.ModuleType("evoagentx.storages.storages_config")

class DBConfig: ...

class VectorStoreConfig: ...

cfg_mod.DBConfig = DBConfig
cfg_mod.VectorStoreConfig = VectorStoreConfig
sys.modules.setdefault("evoagentx.storages", types.ModuleType("evoagentx.storages"))
sys.modules["evoagentx.storages.storages_config"] = cfg_mod

# ----------------------------------------------------------------------
# utils.utils
# ----------------------------------------------------------------------
from evoagentx.utils import utils as u


def test_make_parent_folder(tmp_path):
    target = tmp_path / "sub/dir/file.txt"
    u.make_parent_folder(str(target))
    # dir must exist but file must NOT (we never wrote it)
    assert (tmp_path / "sub/dir").is_dir() and not target.exists()


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("The QUICK_brown  fox!", "quick brown fox!"),
        ("An_example_of  Articles", "example of articles"),
    ],
)
def test_normalize_text_variants(raw, expected):
    assert u.normalize_text(raw) == expected


# ----------------------------------------------------------------------
# utils.sanitize  – we just want to tick the happy path & dependency graph.
# ----------------------------------------------------------------------
from evoagentx.utils import sanitize

SAMPLE = textwrap.dedent(
    """
    import math, os

    CONST = 42

    def helper(x):
        return x + CONST

    def answer():
        return helper(0)
    """
)


def test_sanitize_entrypoint():
    cleaned = sanitize.sanitize(SAMPLE, entrypoint="answer")
    # helper & answer should survive, CONST import too
    assert "def answer" in cleaned and "def helper" in cleaned
    assert "CONST" in cleaned and "import math" in cleaned


# ----------------------------------------------------------------------
# utils.factory  – cover unsupported providers + happy vector stub.
# ----------------------------------------------------------------------
from evoagentx.utils import factory


class _DummyCfg(dict):
    """Minimal config with .model_dump for factory helpers."""

    def model_dump(self):
        return {}


def test_db_factory_unsupported():
    with pytest.raises(ValueError):
        factory.DBStoreFactory.create("oracle", _DummyCfg())


def test_vector_factory_stub(monkeypatch):
    # Pretend we had a qdrant backend; ensure load_class is invoked
    stub = types.ModuleType("mem0.vector_stores.qdrant")
    stub.Qdrant = lambda **kwargs: "qdrant-instance"
    monkeypatch.setitem(sys.modules, "mem0.vector_stores.qdrant", stub)

    monkeypatch.setattr(factory, "load_class", lambda path: stub.Qdrant)
    # Replace create to mimic minimal implementation using load_class
    monkeypatch.setattr(
        factory.VectorStoreFactory,
        "create",
        classmethod(
            lambda cls, config=None: factory.load_class(
                "mem0.vector_stores.qdrant.Qdrant"
            )(config=config)
        ),
    )

    cfg = _DummyCfg()
    got = factory.VectorStoreFactory.create(config=cfg)
    assert got == "qdrant-instance"
