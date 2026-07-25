"""Validate the bridge artifact contract without a database or network."""

from __future__ import annotations

import ast
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

BRIDGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = BRIDGE_ROOT.parent
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
REQUIRED_GUIDE_HEADINGS = (
    "## Objectives",
    "## Vocabulary",
    "## Worked example",
    "## Exercises",
    "## Self-check",
    "## Common pitfalls",
    "## Next step",
)


@dataclass(frozen=True)
class LessonContract:
    day: int
    stem: str
    prerequisites: tuple[str, ...]
    level: str

    @property
    def lesson_id(self) -> str:
        return f"bridge-{self.day:02d}"


LESSONS: tuple[LessonContract, ...] = (
    LessonContract(1, "config_logging_cli", ("python-15", "sql-15"), "intermediate"),
    LessonContract(2, "protocols_context_decorators", ("bridge-01",), "intermediate"),
    LessonContract(3, "safe_psycopg_queries", ("bridge-02",), "intermediate"),
    LessonContract(4, "transactions_idempotency_retries", ("bridge-03",), "intermediate"),
    LessonContract(5, "db_testing_fixtures_doubles", ("bridge-04",), "intermediate"),
    LessonContract(6, "bulk_etl_validation", ("bridge-05",), "advanced"),
    LessonContract(7, "async_bounded_concurrency", ("bridge-06",), "advanced"),
    LessonContract(8, "production_capstone", ("bridge-07",), "advanced"),
)


def _assignments(tree: ast.Module) -> dict[str, object]:
    values: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            values[target.id] = ast.literal_eval(node.value)
        except (TypeError, ValueError):
            continue
    return values


def _validate_lesson(contract: LessonContract) -> list[str]:
    errors: list[str] = []
    day = f"day{contract.day:02d}"
    learner = BRIDGE_ROOT / "lessons" / f"{day}_{contract.stem}.py"
    guide = BRIDGE_ROOT / "companion-guides" / f"{day}_{contract.stem}.md"
    solution_code = BRIDGE_ROOT / "solutions" / f"{day}_solution.py"
    solution_notes = BRIDGE_ROOT / "solutions" / f"{day}_solutions.md"

    for path in (learner, guide, solution_code, solution_notes):
        if not path.is_file():
            errors.append(f"missing required artifact: {path.relative_to(REPOSITORY_ROOT)}")
    if errors:
        return errors

    for path in (learner, solution_code):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: {exc}")
            continue
        if path == learner:
            values = _assignments(tree)
            if values.get("LESSON_ID") != contract.lesson_id:
                errors.append(f"{learner.name}: incorrect LESSON_ID")
            if values.get("PREREQUISITES") != contract.prerequisites:
                errors.append(f"{learner.name}: incorrect PREREQUISITES")
            if values.get("LEVEL") != contract.level:
                errors.append(f"{learner.name}: incorrect LEVEL")
            source = learner.read_text(encoding="utf-8")
            if "bridge.solutions" in source:
                errors.append(f"{learner.name}: learner file imports a solution")

    guide_text = guide.read_text(encoding="utf-8")
    for heading in REQUIRED_GUIDE_HEADINGS:
        if heading not in guide_text:
            errors.append(f"{guide.name}: missing {heading!r}")
    if "**Prerequisite" not in guide_text:
        errors.append(f"{guide.name}: missing prerequisite declaration")

    notes_text = solution_notes.read_text(encoding="utf-8")
    if "## Tradeoffs" not in notes_text:
        errors.append(f"{solution_notes.name}: missing tradeoff discussion")
    return errors


def _local_markdown_links(markdown_paths: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    for path in markdown_paths:
        text = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            local_target = target.split("#", 1)[0]
            if local_target and not (path.parent / local_target).resolve().exists():
                relative_path = path.relative_to(REPOSITORY_ROOT)
                errors.append(f"{relative_path}: broken local link {target!r}")
    return errors


def validate() -> list[str]:
    """Return all bridge contract violations."""

    errors = [error for contract in LESSONS for error in _validate_lesson(contract)]
    errors.extend(_local_markdown_links(BRIDGE_ROOT.rglob("*.md")))

    # Split the literals so this validator does not flag its own source.
    forbidden = (
        "/" + "Users/",
        "\\" + "Users\\",
        "postgresql://" + "postgres:",
    )
    for path in BRIDGE_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".py", ".md"}:
            continue
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                errors.append(
                    f"{path.relative_to(REPOSITORY_ROOT)}: forbidden local/credential marker"
                )
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Bridge validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Bridge validation passed: {len(LESSONS)} complete lessons.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
