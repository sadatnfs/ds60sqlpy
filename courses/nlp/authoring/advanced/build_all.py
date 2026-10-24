"""Regenerate only authored NLP005-024 content and their canonical registrations."""
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for name in ("batch05_08.py", "batch09_12.py", "batch13_16.py", "batch17_20.py", "batch21_24.py", "enhance.py"):
    runpy.run_path(str(HERE / name), run_name="__main__")
