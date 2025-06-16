import numpy as np
import pytest

from evoagentx.utils.aflow_utils.data_utils import DataUtils
from evoagentx.utils.aflow_utils.convergence_utils import ConvergenceUtils


def test_compute_probabilities_basic():
    du = DataUtils(root_path=".")
    probs = du._compute_probabilities([10, 20, 30])
    assert pytest.approx(probs.sum()) == 1.0
    assert probs[2] > probs[1] > probs[0]


def test_compute_probabilities_empty():
    du = DataUtils(root_path=".")
    with pytest.raises(ValueError):
        du._compute_probabilities([])


def test_select_round(monkeypatch):
    du = DataUtils(root_path=".")
    items = [
        {"round": 0, "score": 0.1},
        {"round": 1, "score": 0.9},
        {"round": 2, "score": 0.2},
    ]
    monkeypatch.setattr(du, "_compute_probabilities", lambda scores: np.array([0.0, 1.0, 0.0]))
    monkeypatch.setattr(np.random, "choice", lambda n, p: 1)
    selected = du.select_round(items)
    assert selected["round"] == 2


def test_convergence_detection(monkeypatch):
    data = [{"round": i, "score": 1.0} for i in range(6)]
    cu = ConvergenceUtils(root_path=".")
    monkeypatch.setattr(cu, "load_data", lambda root_path=None: data)
    converged, start, end = cu.check_convergence(top_k=1, z=0, consecutive_rounds=3)
    assert converged is True and (start, end) == (1, 3)


def test_convergence_insufficient_data(monkeypatch):
    data = [{"round": 0, "score": 1.0}, {"round": 1, "score": 1.0}]
    cu = ConvergenceUtils(root_path=".")
    monkeypatch.setattr(cu, "load_data", lambda root_path=None: data)
    converged, start, end = cu.check_convergence(top_k=3, consecutive_rounds=2)
    assert (converged, start, end) == (False, None, None)
