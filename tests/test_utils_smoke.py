import json
import warnings

from evoagentx.utils.utils import safe_remove, generate_dynamic_class_name, normalize_text
from evoagentx.utils.sanitize import syntax_check
import evoagentx.utils.aflow_utils.data_utils as du
from evoagentx.utils.factory import load_class

setattr(du.test_case_2_test_function, "__test__", False)
warnings.filterwarnings("ignore", "`timeout`", DeprecationWarning)


def test_utils_smoke():
    lst = [1, 2, 3]
    safe_remove(lst, 2)
    assert lst == [1, 3]

    assert generate_dynamic_class_name("hello world") == "HelloWorld"
    assert normalize_text("The_quick") == "quick"

    cls = load_class("json.JSONDecoder")
    assert cls is json.JSONDecoder

    assert syntax_check("def f():\n    return 1")
    assert not syntax_check("def f(:\n    pass")

    snippet = du.test_case_2_test_function("def foo(): pass", "assert True", "foo()")
    assert "def check" in snippet
