"""Structured exercises, progressive hints and explicitly revealed solutions."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.classroom import ClassroomService
from ds60sqlpy.exercises import (
    REVEAL_MESSAGE,
    exercise_solution,
    is_standalone,
    parse_guide,
    python_free_names,
    solution_sections,
    sql_solution_blocks,
)
from ds60sqlpy.module_service import ModuleService

Services = tuple[ClassroomService, ModuleService]
SHARDS = 8
LEAK_MARKERS = ("Learner contract", "**Reasoning:**", "Reference answer", "Expected answer")


@pytest.fixture(scope="session")
def services(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Services]:
    catalog = Catalog.load()
    state = tmp_path_factory.mktemp("exercise-services")
    modules = ModuleService(catalog, state / "modules")
    classroom = ClassroomService(
        catalog, modules.action, modules.targets, runs_directory=state / "runs"
    )
    try:
        yield classroom, modules
    finally:
        modules.close()


def exercises(service: ClassroomService, lesson_id: str) -> dict[str, Any]:
    return service.action({"action": "classroom-exercises", "lesson_id": lesson_id})


def solution(service: ClassroomService, lesson_id: str, number: int) -> dict[str, Any]:
    return service.action(
        {
            "action": "classroom-exercise-solution",
            "lesson_id": lesson_id,
            "number": number,
            "reveal": True,
        }
    )


def programs(service: ClassroomService, lesson_id: str) -> list[dict[str, Any]]:
    result = service.action(
        {"action": "classroom-reference-program", "lesson_id": lesson_id, "reveal": True}
    )
    return list(result["programs"])


def test_python_05_list_items_mastery_hints_and_shared_implementations(
    services: Services,
) -> None:
    service, _ = services
    data = exercises(service, "python-05")
    assert data["lesson_id"] == "python-05" and data["language"] == "python"
    items = data["exercises"]
    assert [item["number"] for item in items] == list(range(1, 9))
    assert [item["title"] for item in items] == [
        "Exercise 1",
        "Exercise 2",
        "Exercise 3",
        "Prediction",
        "Tracing",
        "Implementation",
        "Debugging",
        "Edge case and explanation",
    ]
    first = items[0]
    assert first["prompt_html"].startswith(
        "<p>Implement <code>describe(values: list[float]) -&gt; tuple[float, float]</code>"
    )
    assert [detail["label"] for detail in first["details"]] == [
        "Input",
        "Expected result",
        "Constraints",
        "Verify",
    ]
    assert first["details"][1]["html"] == "<p><code>(5.0, 2.0)</code>.</p>"
    assert [item["hints"] for item in items[:3]] == [[], [], []]
    assert items[3]["hints"] == [
        "<p>Default objects are created once when <code>def</code> executes.</p>"
    ]
    assert all(len(item["hints"]) == 1 and not item["hints_shared"] for item in items[3:])
    assert all(item["has_solution"] for item in items)
    assert "Before opening the reference solution" in data["intro_html"]
    assert data["reference_program"] is True

    one = solution(service, "python-05", 1)
    assert one["number"] == 1 and "population standard deviation" in one["html"]
    assert [(entry["language"], entry["standalone"]) for entry in one["code"]] == [("python", True)]
    # Exercise 2 reuses describe() from exercise 1, so it cannot run alone.
    two = solution(service, "python-05", 2)
    assert [(entry["language"], entry["standalone"]) for entry in two["code"]] == [
        ("python", False)
    ]
    four = solution(service, "python-05", 4)
    assert "Shared implementation for Exercise 4" in four["html"]
    assert [entry["text"].split("(")[0] for entry in four["code"]] == ["def collect_faulty"]
    for number in range(5, 9):
        shared = solution(service, "python-05", number)
        assert "Shared implementation for Exercises 5-8" in shared["html"]
        assert any("def weighted_mean(" in entry["text"] for entry in shared["code"])
        assert "collect_faulty" not in shared["html"]


def test_sql_29_query_exercises_hints_details_and_code(services: Services) -> None:
    service, _ = services
    data = exercises(service, "sql-29")
    assert data["language"] == "sql"
    items = data["exercises"]
    assert [item["title"] for item in items] == [
        "Query writing",
        "Query writing",
        "Query writing",
        "Prediction",
        "Debugging",
        "Extension",
    ]
    assert all(len(item["hints"]) == 1 for item in items)
    assert all(
        [detail["label"] for detail in item["details"]] == ["Input", "Expected result", "Verify"]
        for item in items
    )
    assert items[0]["prompt_html"] == (
        "<p>Find customer names beginning with <code>Customer 1</code> case-insensitively.</p>"
    )
    assert items[0]["hints"] == [
        "<p><code>ILIKE &#x27;Customer 1%&#x27;</code> uses <code>%</code> for any suffix.</p>"
    ]
    assert all(item["has_solution"] for item in items)
    assert "Clause-by-clause" not in json.dumps(data)

    answer = solution(service, "sql-29", 1)
    assert answer["code"] == [
        {
            "language": "sql",
            "text": "SELECT\n  c.customer_id,\n  c.full_name\nFROM\n  customers AS c\n"
            "WHERE\n  c.full_name ILIKE 'Customer 1%'\nORDER BY\n  c.customer_id;",
            "standalone": True,
        }
    ]
    assert answer["joined_standalone"] is True
    assert 'id="exercise-sql-29-1--solution--reasoning-and-verification"' in answer["html"]


def test_sql_companion_supplies_code_when_markdown_has_none(tmp_path: Path) -> None:
    markdown = tmp_path / "day99_solutions.md"
    markdown.write_text("# Solutions\n\n## Exercise 1: Count rows\n\nCount each row once.\n")
    companion = tmp_path / "day99_solutions.sql"
    companion.write_text(
        "BEGIN;\n-- ----------\n-- Exercise 1: Count rows\n-- Prompt: Count rows.\n"
        "SELECT count(*) FROM orders;\n\n-- ----------\n-- Exercise 2: Meta-command\n"
        "\\echo checking\nSELECT 1;\n\nROLLBACK;\n"
    )
    paths = [markdown, companion]
    first = exercise_solution(
        lesson_id="sql-99",
        number=1,
        language="sql",
        solutions=paths,
        repo_root=tmp_path,
        targets={},
    )
    assert first["code"] == [
        {"language": "sql", "text": "SELECT count(*) FROM orders;", "standalone": True}
    ]
    assert "Count each row once." in first["html"]
    second = exercise_solution(
        lesson_id="sql-99",
        number=2,
        language="sql",
        solutions=paths,
        repo_root=tmp_path,
        targets={},
    )
    assert second["code"] == [
        {"language": "sql", "text": "\\echo checking\nSELECT 1;", "standalone": False}
    ]
    assert second["html"].startswith('<pre class="highlighted-code">')
    assert second["joined_standalone"] is False


def test_sql_professional_hint_ladder_leaves_verify(services: Services) -> None:
    service, _ = services
    items = exercises(service, "sql-ext-01")["exercises"]
    assert len(items) == 14
    assert items[0]["title"] == "Capability matrix"
    assert items[9]["title"] == "PostGIS nearest"
    assert items[0]["hints"] == [
        "<p>Start from the requested list and LEFT JOIN catalogs, otherwise unavailable names "
        "disappear.</p>"
    ]
    verify = next(detail for detail in items[0]["details"] if detail["label"] == "Verify")
    assert "Hint ladder" not in verify["html"]
    assert verify["html"].endswith("availability does not grant permission.</p>")
    assert all(item["has_solution"] and len(item["hints"]) == 1 for item in items)


def test_bridge_03_nested_bullet_fields_and_practice_contract(services: Services) -> None:
    service, _ = services
    data = exercises(service, "bridge-03")
    items = data["exercises"]
    assert [item["number"] for item in items] == list(range(1, 11))
    assert items[0]["title"] == "SQL implementation"
    assert items[9]["title"] == "Optional integration"
    assert items[0]["prompt_html"] == (
        "<p>Write <code>FIND_CUSTOMERS_SQL</code> for customer ID, name, and lifetime order "
        "value by country and minimum total with deterministic ordering.</p>"
    )
    assert items[0]["hints"] == [
        "<p>Left join orders, aggregate at customer grain, and keep two <code>%s</code> "
        "placeholders unquoted.</p>"
    ]
    assert [detail["label"] for detail in items[0]["details"]] == ["Verify"]
    assert "Practice contract" in data["intro_html"]
    assert "Before opening the solution" in data["intro_html"]
    answer = solution(service, "bridge-03", 1)
    assert "Group customers after a left join" in answer["html"]
    assert answer["code"] == [] and answer["joined_standalone"] is False
    assert [
        (p["path"], p["language"], p["standalone"]) for p in programs(service, "bridge-03")
    ] == [("bridge/solutions/day03_solution.py", "python", True)]


def test_go_001_investigation_hints_and_numbered_solutions(services: Services) -> None:
    service, _ = services
    data = exercises(service, "go-001")
    assert data["language"] == "go"
    items = data["exercises"]
    assert [item["title"] for item in items] == [
        "Predict a first value: change one input",
        "Compute before formatting: debug a regression",
        "Trace statement order",
        "Distinguish zero initialization",
        "Repair a naming assumption",
        "Transfer to a receipt",
    ]
    assert all(len(item["hints"]) == 3 and not item["hints_shared"] for item in items)
    assert items[0]["hints"][0] == (
        "<p>Restate the expected observation: greeting equals Hello, Go.</p>"
    )
    assert all(item["has_solution"] for item in items)
    # The section's closing guidance is not part of the last exercise.
    assert "answer-free learner source" in data["intro_html"]
    assert "answer-free" not in json.dumps(items)
    answer = solution(service, "go-001", 1)
    assert answer["code"] == [
        {
            "language": "go",
            "text": 'greeting := "Hello, Go"\ncheck(greeting == "Hello, Go", "greeting")',
            "standalone": False,
        }
    ]
    assert answer["html"].startswith("<p>Copy worked example 1")


def test_practice_layout_for_dbt_and_polars(services: Services) -> None:
    service, _ = services
    expected = {
        "dbt-001": [
            "Locate the project",
            "Change the expression",
            "Introduce invalid SQL",
            "Inspect the manifest",
            "Inspect run results",
            "State the runtime boundary",
        ],
        "polars-001": [
            "Predict a new order",
            "Choose a projection",
            "Explain an aggregate",
            "Keep raw state",
            "State an empty policy",
            "Validate identifiers",
        ],
    }
    for lesson_id, titles in expected.items():
        items = exercises(service, lesson_id)["exercises"]
        assert [item["title"] for item in items] == titles
        assert all([detail["label"] for detail in item["details"]] == ["Check"] for item in items)
        assert all(len(item["hints"]) == 1 and item["has_solution"] for item in items)
    first = exercises(service, "dbt-001")["exercises"][0]
    assert first["prompt_html"] == (
        "<p>Identify the model, project and profile files created by the wrapper.</p>"
    )
    assert first["details"][0]["html"] == "<p>Each file has a distinct responsibility.</p>"
    assert first["hints"] == ["<p>Read the project helper before the model.</p>"]
    assert "The model states SQL logic" in solution(service, "dbt-001", 1)["html"]


def test_other_module_families(services: Services) -> None:
    service, _ = services
    csharp = exercises(service, "csharp-001")["exercises"]
    assert [item["title"] for item in csharp][:2] == ["Predict and explain", "Guided modification"]
    assert all(item["hints_shared"] and len(item["hints"]) == 3 for item in csharp)
    assert "Task 3" in solution(service, "csharp-001", 3)["html"]

    julia = exercises(service, "julia-001")["exercises"]
    assert julia[0]["title"] == "Change a count"
    assert julia[0]["prompt_html"] == "<p>Use accepted 20 and rejected 3.</p>"
    assert julia[0]["details"] == [{"label": "Expected result", "html": "<p>The total is 23.</p>"}]
    assert julia[0]["hints"] == ["<p>Change one input and recompute the arithmetic.</p>"]

    java = exercises(service, "java-001")["exercises"]
    assert [hint.split(" ", 1)[0] for hint in java[1]["hints"]] == [
        "<p>First",
        "<p>Then",
        "<p>Finally,",
    ]

    cuda = exercises(service, "cuda-070")["exercises"]
    assert cuda[1]["hints"] == [
        "<p>Change one assumption in worked example 2 while preserving the declared contract: "
        "reuse a free block.</p>"
    ]
    assert not any(item["hints_shared"] for item in cuda)

    kubernetes = exercises(service, "k8s-008")["exercises"]
    assert kubernetes[0]["hints"] == [
        "<p>separate phase from readiness</p>",
        "<p>inspect endpoint conditions, not only addresses</p>",
        "<p>check whether old ready Pods still match the Service before predicting zero.</p>",
    ]
    assert "Hints:" not in kubernetes[0]["prompt_html"]


def test_python_standalone_rule_finds_names_from_other_exercises() -> None:
    assert python_free_names("print(df.head())") == frozenset({"df"})
    assert is_standalone("python", "print(df.head())") is False
    assert is_standalone("python", "import pandas as pd\nframe = pd.DataFrame()\nprint(frame)")
    assert python_free_names("def total(values):\n    return helper(values)\n") == frozenset(
        {"helper"}
    )
    bound = (
        "counter = 0\n\ndef bump():\n    global counter\n    counter += 1\n\n"
        "for item in range(2):\n    bump()\nwith open(__file__) as handle:\n    pass\n"
        "try:\n    pass\nexcept ValueError as error:\n    print(error)\n"
        "if (size := len([1])):\n    print(size, counter)\n"
    )
    assert is_standalone("python", bound) is True
    assert is_standalone("python", "def broken(:\n    pass\n") is False


def test_python_standalone_rule_hoists_future_imports() -> None:
    source = '"""Notes."""\nlimit: int = 3\nfrom __future__ import annotations\nprint(limit)\n'
    with pytest.raises(SyntaxError):
        compile(source, "main.py", "exec")
    assert is_standalone("python", source) is True


def test_sql_and_compiled_language_standalone_rules() -> None:
    assert is_standalone("sql", "SELECT 1;") is True
    assert is_standalone("sql", "\\set ON_ERROR_STOP on\nSELECT 1;") is False
    assert is_standalone("postgresql", "SELECT 1;\n  \\echo done") is False
    fragment = 'total := 2 + 3\ncheck(total == 5, "total")'
    program = 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("ok")\n}\n'
    assert is_standalone("go", fragment) is False
    assert is_standalone("go", program) is True
    assert is_standalone("cpp", "int main() { return 0; }") is True
    assert is_standalone("c", "int total = 1;") is False
    assert is_standalone("php", "<?php echo 1;") is True
    assert is_standalone("javascript", "console.log(1);") is False


def test_reference_programs_for_go_sql_python_and_none(services: Services) -> None:
    service, _ = services
    root = service.catalog.repo_root
    go = programs(service, "go-001")
    assert [(p["path"], p["language"], p["standalone"]) for p in go] == [
        ("courses/go/solutions/go-001_solution.go", "go", True)
    ]
    assert go[0]["text"] == (root / go[0]["path"]).read_text(encoding="utf-8")
    sql = programs(service, "sql-29")
    assert [(p["path"], p["language"], p["standalone"]) for p in sql] == [
        ("sql/postgres-60day/solutions/day29_solutions.sql", "sql", True)
    ]
    notebook_path = "python/ds-60day/solutions/day05_functions_type_hints/day05_solutions.ipynb"
    notebook = programs(service, "python-05")
    assert [(p["path"], p["language"], p["standalone"]) for p in notebook] == [
        (notebook_path, "python", True)
    ]
    cells = json.loads((root / notebook_path).read_text(encoding="utf-8"))["cells"]
    sources = ["".join(cell["source"]) for cell in cells if cell["cell_type"] == "code"]
    assert notebook[0]["text"] == "\n\n".join(
        source.rstrip("\n") for source in sources if source.strip()
    )
    for lesson_id in ("asm-001", "k8s-001"):
        assert programs(service, lesson_id) == []
        assert exercises(service, lesson_id)["reference_program"] is False
    assert exercises(service, "go-001")["reference_program"] is True
    assert exercises(service, "asm-001")["exercises"] == []


@pytest.mark.parametrize("lesson_id", ["sql-29", "go-001"])
@pytest.mark.parametrize("action", ["classroom-exercise-solution", "classroom-reference-program"])
def test_reveal_guard_and_number_validation(
    services: Services, lesson_id: str, action: str
) -> None:
    service, _ = services
    for reveal in (None, False, "true", 1):
        payload: dict[str, Any] = {"action": action, "lesson_id": lesson_id, "number": 1}
        if reveal is not None:
            payload["reveal"] = reveal
        with pytest.raises(ValueError, match=re.escape(REVEAL_MESSAGE)):
            service.action(payload)
    if action == "classroom-exercise-solution":
        for number in (True, 0, "1", 1.0, 1000):
            with pytest.raises(ValueError, match="Choose an exercise number"):
                solution(service, lesson_id, number)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="Exercise 99 has no separate written solution"):
            solution(service, lesson_id, 99)


@pytest.mark.parametrize("shard", range(SHARDS))
def test_every_lesson_renders_safely_without_solution_leakage(
    services: Services, shard: int
) -> None:
    service, modules = services
    catalog = service.catalog
    lessons = [
        (
            lesson.id,
            catalog.resolve(lesson.guide_path),
            [catalog.resolve(path) for path in lesson.solution_paths],
        )
        for lesson in catalog
    ] + [
        (
            lesson.id,
            modules.catalog.content_path(lesson.guide_path),
            [modules.catalog.content_path(path) for path in lesson.solution_paths],
        )
        for lesson in modules.catalog.lessons.values()
    ]
    guarded = False
    for lesson_id, guide, solutions in sorted(lessons)[shard::SHARDS]:
        data = exercises(service, lesson_id)
        assert "<script" not in json.dumps(data).lower()
        parsed = parse_guide(guide)
        assert bool(parsed.exercises) or not parsed.has_exercise_section, lesson_id
        numbers = [item["number"] for item in data["exercises"]]
        assert numbers == [exercise.number for exercise in parsed.exercises]
        assert len(numbers) == len(set(numbers))
        sections = solution_sections(solutions)
        solved = set(sections) | set(sql_solution_blocks(solutions))
        if sections:
            assert set(numbers) <= solved, lesson_id
        guide_text = " ".join(guide.read_text(encoding="utf-8").split())
        for item, exercise in zip(data["exercises"], parsed.exercises, strict=True):
            assert 0 < len(item["title"]) <= 120
            assert "**" not in item["title"] and "`" not in item["title"]
            assert item["prompt_html"]
            visible = " ".join(
                [
                    exercise.prompt,
                    *(detail.markdown for detail in exercise.details),
                    *exercise.hints,
                ]
            )
            visible = " ".join(visible.split())
            assert not any(marker in visible for marker in LEAK_MARKERS), lesson_id
            for line in sections.get(exercise.number, "").split("\n"):
                flat = " ".join(line.split())
                if len(flat) >= 40 and flat not in guide_text:
                    assert flat not in visible, (lesson_id, exercise.number)
            if not item["has_solution"]:
                continue
            answer = solution(service, lesson_id, item["number"])
            assert answer["number"] == item["number"] and answer["html"]
            assert "<script" not in answer["html"].lower()
            assert all(set(entry) == {"language", "text", "standalone"} for entry in answer["code"])
            if not guarded:
                with pytest.raises(ValueError, match=re.escape(REVEAL_MESSAGE)):
                    service.action(
                        {
                            "action": "classroom-exercise-solution",
                            "lesson_id": lesson_id,
                            "number": item["number"],
                        }
                    )
                guarded = True
        references = programs(service, lesson_id)
        assert bool(references) is data["reference_program"]
        assert all(entry["text"] and "<script" not in entry["path"] for entry in references)
