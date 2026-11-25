"""Authored, lesson-specific teaching text for the Java guides and solutions.

teaching.txt holds one block per lesson. A block starts with ``== java-NNN`` and has one
line per field: ``run``, ``predict``, ``pitfalls``, ``retrieval``, ``after`` and
``hint1`` to ``hint6``. render.py combines these fields with specs.py; the routine that
is the same in every lesson lives once in ../STUDY-GUIDE.md.

Each hint is a three-rung ladder. The classroom splits a hint that starts with "First"
at sentences starting with Then, Next, Finally, Second, Third, Lastly or After that, so
a hint must contain exactly the rungs "First", "Then" and "Finally," and no other
sentence may start with one of those words.
"""

import re
from pathlib import Path

PATH = Path(__file__).resolve().with_name("teaching.txt")
HINTS = tuple(f"hint{i}" for i in range(1, 7))
FIELDS = ("run", "predict", "pitfalls", "retrieval", "after", *HINTS)
RUNG = re.compile(r"(?<=[.!?])\s+(?=(?:Then|Next|Finally|Second|Third|Lastly|After that)\b)")


def _ladder(where, hint):
    rungs = RUNG.split(hint)
    starts = [rung.split(" ", 1)[0] for rung in rungs]
    if starts != ["First", "Then", "Finally,"]:
        raise ValueError(f"{where}: hint rungs start with {starts}, not First/Then/Finally,")


def load(path=PATH):
    lessons = {}
    current = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        where = f"{path.name}:{number}"
        if not line.strip() or line.startswith("#"):
            continue
        if line.startswith("== "):
            ident = line[3:].strip()
            if ident in lessons:
                raise ValueError(f"{where}: duplicate lesson {ident}")
            current = lessons[ident] = {}
            continue
        key, sep, value = line.partition(": ")
        if current is None or not sep or key not in FIELDS or key in current:
            raise ValueError(f"{where}: expected one new 'field: text' line inside a lesson")
        current[key] = value.strip()
    teaching = {}
    for ident, fields in lessons.items():
        missing = [field for field in FIELDS if field not in fields]
        if missing:
            raise ValueError(f"{ident} is missing {', '.join(missing)}")
        for field in HINTS:
            _ladder(f"{ident} {field}", fields[field])
        teaching[ident] = {field: fields[field] for field in FIELDS[:5]}
        teaching[ident]["hints"] = [fields[field] for field in HINTS]
    return teaching


TEACHING = load()
