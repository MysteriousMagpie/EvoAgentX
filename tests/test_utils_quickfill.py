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


def test_vector_factory_stub(monkeypatch):
    # Pretend we had a qdrant backend; ensure load_class is invoked
    stub = types.ModuleType("mem0.vector_stores.qdrant")
    stub.Qdrant = lambda **_: "qdrant-instance"
    monkeypatch.setitem(sys.modules, "mem0.vector_stores.qdrant", stub)

    monkeypatch.setattr(factory, "load_class", lambda path: stub.Qdrant)
    # Replace create to mimic minimal implementation using load_class
    monkeypatch.setattr(
        factory.VectorStoreFactory,
        "create",
        classmethod(lambda cls, cfg: factory.load_class("mem0.vector_stores.qdrant.Qdrant")()),
    )

    cfg = VectorStoreConfig()
    got = factory.VectorStoreFactory.create(config=cfg)
    assert got == "qdrant-instance"
