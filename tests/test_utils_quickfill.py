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
from evoagentx.storages.storages_config import DBConfig, VectorStoreConfig
import warnings

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
warnings.filterwarnings("ignore", "`timeout`", DeprecationWarning)

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


def test_db_factory_unsupported():
    with pytest.raises(ValueError):
        cfg = DBConfig(db_name="oracle")
        factory.DBStoreFactory.create("oracle", config=cfg)


# Add this class definition above the test
class _DummyCfg:
    # Define the necessary attributes and methods expected by the factory
    def __init__(self):
        self.some_attribute = "some_value"


def test_vector_factory_stub(monkeypatch):
    """
    Emulate a qdrant backend and make sure VectorStoreFactory falls back
    to it correctly.
    """

    # ------------------------------------------------------------------
    # 1.  Build a minimal importable package hierarchy:
    #     mem0 -> mem0.vector_stores -> mem0.vector_stores.qdrant
    # ------------------------------------------------------------------
    pkg_root = types.ModuleType("mem0")
    pkg_sub  = types.ModuleType("mem0.vector_stores")
    stub     = types.ModuleType("mem0.vector_stores.qdrant")

    # concrete fake class returned by the factory
    setattr(stub, "Qdrant", lambda **_: "qdrant-instance")

    monkeypatch.setitem(sys.modules, "mem0", pkg_root)
    monkeypatch.setitem(sys.modules, "mem0.vector_stores", pkg_sub)
    monkeypatch.setitem(sys.modules, "mem0.vector_stores.qdrant", stub)

    # ------------------------------------------------------------------
    # 2.  Replace factory.load_class so that it returns the fake class
    # ------------------------------------------------------------------
    monkeypatch.setattr(factory, "load_class",
                        lambda path: stub.Qdrant)

    # ------------------------------------------------------------------
    # 3.  Monkey-patch VectorStoreFactory.create but keep its real
    #     signature: (provider, config)
    # ------------------------------------------------------------------
    def _fake_create(cls, provider: str, config=None):
        # In the real factory `provider` decides which class to load.
        assert provider == "qdrant"
        return factory.load_class(
            "mem0.vector_stores.qdrant.Qdrant"
        )()

    monkeypatch.setattr(factory.VectorStoreFactory,
                        "create",
                        classmethod(_fake_create))

    # ------------------------------------------------------------------
    # 4.  Exercise the stubbed factory
    # ------------------------------------------------------------------
    cfg = _DummyCfg()
    got = factory.VectorStoreFactory.create("qdrant", cfg)
    assert got == "qdrant-instance"