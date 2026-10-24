"""Protocol-level tests for the optional local MCP tutor."""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("mcp", reason="Install the optional mcp extra for protocol tests")

from mcp import ClientSession, StdioServerParameters, stdio_client  # noqa: E402
from mcp.shared.exceptions import MCPError  # noqa: E402
from mcp.types import TextContent, TextResourceContents  # noqa: E402

from ds60sqlpy.catalog import Catalog, Lesson  # noqa: E402
from ds60sqlpy.coaching import CoachingService  # noqa: E402
from ds60sqlpy.mcp_server import TutorAdapter, build_server  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "scripts" / "mcp_server.py"
SECRET_SOLUTION = "OFFICIAL SOLUTION 314159"


@pytest.fixture
def course(tmp_path: Path) -> Catalog:
    root = tmp_path / "test course with spaces"
    (root / "python" / "ds-60day").mkdir(parents=True)
    (root / "sql" / "postgres-60day").mkdir(parents=True)
    (root / "curriculum").mkdir()
    (root / "pyproject.toml").write_text("[project]\nname = 'test-course'\n", encoding="utf-8")
    (root / "guide.md").write_text(
        "# Numbers\n\nPredict the result.\n\n**Hint 1:** Count the terms.\n"
        "**Hint 2:** Evaluate the sum.\n",
        encoding="utf-8",
    )
    (root / "learner.py").write_text("print(2 + 3)\n", encoding="utf-8")
    (root / "solution.md").write_text(SECRET_SOLUTION, encoding="utf-8")
    first = Lesson(
        id="python-01",
        track="python",
        day=1,
        title="Numbers",
        level="beginner",
        phase="foundations",
        estimated_minutes=30,
        prerequisites=(),
        lesson_path="learner.py",
        guide_path="guide.md",
        solution_paths=("solution.md",),
        dependency_group="core",
        network="offline",
    )
    lessons = [
        first,
        replace(first, id="python-02", day=2, title="More numbers", prerequisites=("python-01",)),
    ]
    (root / "curriculum" / "catalog.json").write_text(
        json.dumps({"lessons": [asdict(item) for item in lessons]}), encoding="utf-8"
    )
    return Catalog.load(root)


def adapter(course: Catalog, *, writes: bool = False) -> TutorAdapter:
    return TutorAdapter(CoachingService(course), allow_progress_writes=writes)


def test_default_tools_only_read_and_building_server_does_not_create_progress(
    course: Catalog,
) -> None:
    tutor = adapter(course)
    names = {item["name"] for item in tutor.tools()}
    assert names == {
        "course_paths",
        "course_plan",
        "course_lessons",
        "course_lesson",
        "course_hint",
        "course_solution",
        "course_session",
    }
    assert all(item["annotations"]["readOnlyHint"] for item in tutor.tools())
    build_server(tutor)
    tutor.invoke("course_paths", {})
    assert not (course.repo_root / ".learning").exists()
    with pytest.raises(ValueError, match="disabled"):
        tutor.invoke(
            "course_save_evidence",
            {"lesson_id": "python-01", "phase": "attempt", "note": "I tried."},
        )


def test_search_pagination_preserves_filters_and_avoids_solutions(course: Catalog) -> None:
    tutor = adapter(course)
    first = tutor.invoke("course_lessons", {"query": "numbers", "track": "python", "limit": 1})
    assert first["total"] == 2
    assert [item["id"] for item in first["lessons"]] == ["python-01"]
    second = tutor.invoke(
        "course_lessons",
        {"query": "numbers", "track": "python", "limit": 1, "cursor": first["next_cursor"]},
    )
    assert [item["id"] for item in second["lessons"]] == ["python-02"]
    assert second["next_cursor"] is None
    assert "solution_paths" not in json.dumps(first)
    assert tutor.invoke("course_lessons", {"query": "no matches"})["total"] == 0
    with pytest.raises(ValueError, match="cursor"):
        tutor.invoke("course_lessons", {"query": "changed", "cursor": first["next_cursor"]})
    with pytest.raises(ValueError, match="cursor"):
        tutor.invoke("course_lessons", {"cursor": "invalid"})


@pytest.mark.parametrize(
    "arguments",
    [
        {"lesson_id": "python-01"},
        {"lesson_id": "python-01", "reveal": False},
        {"lesson_id": "python-01", "reveal": "true"},
        {"lesson_id": "python-01", "reveal": 1},
    ],
)
def test_solution_requires_explicit_boolean_reveal(
    course: Catalog, arguments: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match="Invalid tool arguments"):
        adapter(course).invoke("course_solution", arguments)


def test_guides_hints_and_prompts_do_not_read_solution(course: Catalog) -> None:
    tutor = adapter(course)
    # If a normal read tries to open the solution, the missing file makes it fail.
    (course.repo_root / "solution.md").unlink()
    lesson = tutor.invoke("course_lesson", {"lesson_id": "python-01"})
    assert lesson["learner"] == "print(2 + 3)\n"
    assert "solution_paths" not in lesson
    assert tutor.invoke("course_hint", {"lesson_id": "python-01"})["hint"] == "Count the terms."
    assert tutor.read_resource("ds60://course/lesson/python-01")[1] == "text/markdown"
    assert "prediction" in tutor.prompt("python-01")
    assert SECRET_SOLUTION not in json.dumps(lesson)


def test_solution_read_is_catalog_bound_and_resources_reject_arbitrary_paths(
    course: Catalog,
) -> None:
    tutor = adapter(course)
    result = tutor.invoke("course_solution", {"lesson_id": "python-01", "reveal": True})
    assert result["content"] == SECRET_SOLUTION
    for uri in (
        "file:///etc/passwd",
        "ds60://course/lesson/../../solution.md",
        "ds60://course/solution/python-01",
    ):
        with pytest.raises((ValueError, KeyError)):
            tutor.read_resource(uri)
    with pytest.raises(KeyError):
        tutor.invoke("course_lesson", {"lesson_id": "../solution.md"})


def test_invalid_inputs_cannot_trigger_writes(course: Catalog) -> None:
    tutor = adapter(course, writes=True)
    for name, arguments in (
        ("course_lessons", {"limit": 1000}),
        ("course_hint", {"lesson_id": "python-01", "number": 0}),
        ("course_lesson", {"lesson_id": "python-01", "path": "solution.md"}),
        ("course_plan", {"targets": ["python-01"], "weekly_hours": 0}),
        ("course_save_evidence", {"lesson_id": "python-01", "phase": "invalid", "note": "x"}),
    ):
        with pytest.raises(ValueError, match="Invalid tool arguments"):
            tutor.invoke(name, arguments)
    assert not (course.repo_root / ".learning").exists()


def test_json_schema_integer_numbers_are_normalized_before_indexing(course: Catalog) -> None:
    tutor = adapter(course)
    assert len(tutor.invoke("course_lessons", {"limit": 1.0})["lessons"]) == 1
    assert tutor.invoke("course_hint", {"lesson_id": "python-01", "number": 1.0})["number"] == 1


def test_progress_requires_opt_in_saved_evidence_and_prerequisites(course: Catalog) -> None:
    tutor = adapter(course, writes=True)
    with pytest.raises(ValueError, match="predict"):
        tutor.invoke("course_complete", {"lesson_id": "python-01", "confirmed": True})
    for lesson_id in ("python-02", "python-01"):
        for phase in ("predict", "attempt", "explain"):
            tutor.invoke(
                "course_save_evidence",
                {"lesson_id": lesson_id, "phase": phase, "note": f"My {phase} evidence."},
            )
    with pytest.raises(ValueError, match="prerequisite"):
        tutor.invoke("course_complete", {"lesson_id": "python-02", "confirmed": True})
    for lesson_id in ("python-01", "python-02"):
        result = tutor.invoke("course_complete", {"lesson_id": lesson_id, "confirmed": True})
        assert "not automatically graded" in result["evidence_type"]
    assert len(tutor.invoke("course_paths", {})["completed"]) == 2


def test_resource_pages_cover_the_catalog_once(course: Catalog) -> None:
    first = course.get("python-01")
    catalog = Catalog(course.repo_root, [replace(first, id=f"item-{n}", day=n) for n in range(110)])
    tutor = adapter(catalog)
    seen: list[str] = []
    page = tutor.resources()
    while True:
        seen.extend(item["uri"] for item in page["resources"])
        if page["nextCursor"] is None:
            break
        page = tutor.resources(page["nextCursor"])
    assert len(seen) == len(set(seen)) == 111


def test_named_path_expands_into_catalog_ids_before_planning() -> None:
    result = adapter(Catalog.load(ROOT)).invoke("course_plan", {"targets": ["python-foundations"]})
    assert "python-15" in result["targets"]
    assert result["lessons"]
    assert all("solution_paths" not in lesson for lesson in result["lessons"])


@pytest.mark.parametrize("writes", [False, True])
def test_real_stdio_client_initializes_discovers_and_calls_tools_and_resources(
    course: Catalog,
    writes: bool,
) -> None:
    async def exercise() -> None:
        # POSIX audit hooks reject network connects/listeners in the child.
        # Windows asyncio may create an internal socketpair for its event loop,
        # so it runs the same stdio exchange without that platform-specific guard.
        guard = (
            "import runpy,sys; "
            "sys.addaudithook(lambda event,args: "
            "(_ for _ in ()).throw(RuntimeError('network forbidden')) "
            "if event in {'socket.connect','socket.bind'} else None); "
            "sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='__main__')"
        )
        if os.name == "nt":
            guard = (
                "import runpy,sys; sys.argv=sys.argv[1:]; "
                "runpy.run_path(sys.argv[0],run_name='__main__')"
            )
        params = StdioServerParameters(
            command=sys.executable,
            args=["-c", guard, str(ENTRY), "--repo", str(course.repo_root)]
            + (["--allow-progress-writes"] if writes else []),
            cwd=str(course.repo_root.parent),
            env={"PYTHONUTF8": "1"},
        )
        async with (
            stdio_client(params) as (read, write),
            ClientSession(read, write, read_timeout_seconds=15) as session,
        ):
            initialized = await session.initialize()
            assert initialized.server_info.name == "ds60-tutor"
            tools = await session.list_tools()
            names = {tool.name for tool in tools.tools}
            assert "course_lesson" in names
            assert ("course_save_evidence" in names) is writes
            lessons = await session.call_tool("course_lessons", {"limit": 1})
            assert not lessons.is_error
            assert lessons.structured_content["total"] == 2
            bad = await session.call_tool(
                "course_solution", {"lesson_id": "python-01", "reveal": False}
            )
            assert bad.is_error
            disabled = await session.call_tool(
                "course_complete", {"lesson_id": "python-01", "confirmed": True}
            )
            assert disabled.is_error
            if writes:
                for phase in ("predict", "attempt", "explain"):
                    saved = await session.call_tool(
                        "course_save_evidence",
                        {
                            "lesson_id": "python-01",
                            "phase": phase,
                            "note": f"The learner's own {phase} evidence.",
                        },
                    )
                    assert not saved.is_error
                completed = await session.call_tool(
                    "course_complete",
                    {
                        "lesson_id": "python-01",
                        "confirmed": True,
                    },
                )
                assert not completed.is_error
            revealed = await session.call_tool(
                "course_solution",
                {
                    "lesson_id": "python-01",
                    "reveal": True,
                },
            )
            assert not revealed.is_error
            assert SECRET_SOLUTION in revealed.structured_content["content"]
            resources = await session.list_resources()
            assert len(resources.resources) == 3
            resource = await session.read_resource("ds60://course/lesson/python-01")
            assert isinstance(resource.contents[0], TextResourceContents)
            assert "Predict the result" in resource.contents[0].text
            with pytest.raises(MCPError):
                await session.read_resource("file:///etc/passwd")
            prompts = await session.list_prompts()
            assert prompts.prompts[0].name == "coach_lesson"
            prompt = await session.get_prompt("coach_lesson", {"lesson_id": "python-01"})
            assert isinstance(prompt.messages[0].content, TextContent)
            assert "prediction" in prompt.messages[0].content.text
            plan = await session.call_tool("course_plan", {"targets": ["python-02"]})
            assert not plan.is_error
            assert plan.structured_content["ready"] == ["python-02" if writes else "python-01"]
        assert (course.repo_root / ".learning").exists() is writes

    asyncio.run(exercise())


def test_stdio_stdout_contains_only_json_protocol_messages(course: Catalog) -> None:
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "stdout-test", "version": "1"},
        },
    }
    result = subprocess.run(
        [sys.executable, str(ENTRY), "--repo", str(course.repo_root)],
        input=json.dumps(request) + "\n",
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    messages = [json.loads(line) for line in result.stdout.splitlines()]
    assert messages
    assert all(message.get("jsonrpc") == "2.0" for message in messages)


def test_cli_requires_an_explicit_absolute_repository_root(course: Catalog) -> None:
    for args in ([], ["--repo", "."], ["--repo", str(course.repo_root / "python")]):
        result = subprocess.run(
            [sys.executable, str(ENTRY), *args],
            input="",
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        assert result.returncode == 2
        assert result.stdout == ""
