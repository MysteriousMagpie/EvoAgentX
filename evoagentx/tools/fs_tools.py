from pathlib import Path

SANDBOX_ROOT = Path(__file__).resolve().parents[3]  # repo root

def _safe(path: str) -> Path:
    p = (SANDBOX_ROOT / path).resolve()
    if SANDBOX_ROOT not in p.parents:
        raise ValueError("Access outside repo forbidden")
    return p

class FileTools:
    """Expose read/write/append for agents."""

    @staticmethod
    def read(path: str) -> str:
        return _safe(path).read_text()

    @staticmethod
    def write(path: str, content: str) -> str:
        _safe(path).write_text(content)
        return "✅ wrote file"

    @staticmethod
    def append(path: str, content: str) -> str:
        with _safe(path).open("a") as fh:
            fh.write(content)
        return "✅ appended file"
