import os
from typing import Any

from .benchmark import Benchmark
from .measures import exact_match_score
from ..core.logging import logger
from ..core.module_utils import load_json


TEXTGEN_FILES_MAP = {"train": "train.jsonl", "dev": "dev.jsonl", "test": "test.jsonl"}


class TextGenBenchmark(Benchmark):
    """Simple text generation benchmark for sanity checks."""

    def __init__(self, path: str | None = None, mode: str = "all", **kwargs):
        path = os.path.expanduser(path or "~/.evoagentx/data/textgen")
        super().__init__(name=type(self).__name__, path=path, mode=mode, **kwargs)

    def _load_data_from_file(self, file_name: str):
        if file_name is None:
            return None
        file_path = os.path.join(self.path, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found")
        logger.info(f"loading TextGen data from {file_path} ...")
        return load_json(path=file_path, type="jsonl")

    def _load_data(self):
        if self.mode in ("train", "all"):
            self._train_data = self._load_data_from_file(TEXTGEN_FILES_MAP["train"])
        if self.mode in ("dev", "all"):
            self._dev_data = self._load_data_from_file(TEXTGEN_FILES_MAP["dev"])
        if self.mode in ("test", "all"):
            self._test_data = self._load_data_from_file(TEXTGEN_FILES_MAP["test"])

    def _get_label(self, example: Any) -> Any:
        return example["target"]

    def _get_id(self, example: Any) -> Any:
        return example["task_id"]

    def evaluate(self, prediction: Any, label: Any) -> dict:
        em = exact_match_score(prediction=str(prediction), ground_truth=str(label))
        return {"em": em}
