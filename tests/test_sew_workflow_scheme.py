import pytest
from evoagentx.optimizers.sew_optimizer import SEWWorkFlowScheme, VALID_SCHEMES

class DummyGraph:
    """A minimal stub that SEWWorkFlowScheme accepts."""
    def __init__(self):
        self.nodes = []

@pytest.mark.parametrize("scheme", VALID_SCHEMES)
def test_convert_to_valid_schemes(scheme):
    graph = DummyGraph()
    scheme_str = SEWWorkFlowScheme(graph).convert_to_scheme(scheme)
    # Should return a string representation
    assert isinstance(scheme_str, str)

@pytest.mark.parametrize("bad_scheme", ["", "INVALID", None])
def test_convert_invalid_scheme_raises(bad_scheme):
    graph = DummyGraph()
    with pytest.raises(ValueError) as exc:
        SEWWorkFlowScheme(graph).convert_to_scheme(bad_scheme)
    assert "Invalid scheme" in str(exc.value)
