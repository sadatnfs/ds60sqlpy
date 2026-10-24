import tf
import llm
from render import write_all

write_all()

# Textbook prose is applied after generated guides; executable programs are preserved.
from pathlib import Path
import runpy

_textbook = runpy.run_path(
    str(Path(__file__).resolve().parents[2] / "llm-theory/authoring/apply_textbook.py")
)
_textbook["apply"]({f"llm-{number:03}" for number in range(1, 43)})
