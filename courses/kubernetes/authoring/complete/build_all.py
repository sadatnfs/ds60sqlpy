"""Regenerate only the owned Kubernetes bridge and advanced content."""

from pathlib import Path
import runpy, sys

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
runpy.run_path(str(BASE.parents[1] / "fixtures/secret-observer/render.py"), run_name="__main__")
for name in (
    "batch04_07.py",
    "batch09_14.py",
    "batch15_20.py",
    "batch21_28.py",
    "batch29_32.py",
    "batch33_35.py",
    "batch36_39.py",
    "batch40_42.py",
    "enhance.py",
):
    runpy.run_path(str(BASE / name), run_name="__main__")
from author import BASE as COURSE

(COURSE / "host-labs.md").write_text((BASE / "host-labs.md.in").read_text())
runpy.run_path(str(BASE / "normalize_prose.py"), run_name="__main__")
runpy.run_path(str(BASE.parent / "networking/build.py"), run_name="__main__")
