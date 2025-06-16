from evoagentx.benchmark import TextGenBenchmark


def test_textgen_loads():
    bench = TextGenBenchmark(path="data/textgen")
    assert len(bench.get_train_data()) == 1
    assert len(bench.get_dev_data()) == 1
    assert len(bench.get_test_data()) == 1
