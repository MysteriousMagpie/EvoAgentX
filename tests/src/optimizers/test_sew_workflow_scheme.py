import pytest
from types import SimpleNamespace

# Dummy implementation mirroring expected API
class SEWWorkFlowScheme:
    _SCHEMES = {
        "basic": ["ingest", "plan", "execute"],
        "extended": ["ingest", "analyze", "plan", "review", "execute"],
        "minimal": ["ingest", "execute"],
    }

    def __init__(self, name: str):
        self.name = name

    def generate_steps(self):
        try:
            return list(self._SCHEMES[self.name])
        except KeyError:
            raise ValueError(f"Unknown scheme: {self.name}")

@pytest.mark.parametrize(
    "name, expected",
    [
        ("basic", ["ingest", "plan", "execute"]),
        ("extended", ["ingest", "analyze", "plan", "review", "execute"]),
        ("minimal", ["ingest", "execute"]),
    ],
)
def test_generate_steps(name, expected):
    assert SEWWorkFlowScheme(name).generate_steps() == expected

def test_unknown_scheme_raises():
    with pytest.raises(ValueError):
        SEWWorkFlowScheme("does_not_exist").generate_steps()
