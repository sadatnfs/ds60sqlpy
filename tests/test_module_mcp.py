"""Read-only authored-module tutoring boundaries and real stdio discovery."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("mcp", reason="Install the optional MCP extra for tutor protocol tests")
from mcp import ClientSession, StdioServerParameters, stdio_client  # noqa: E402

from ds60sqlpy.catalog import Catalog, Lesson  # noqa: E402
from ds60sqlpy.coaching import CoachingService  # noqa: E402
from ds60sqlpy.mcp_server import (  # noqa: E402
    MAX_MODULE_DOCUMENT_BYTES,
    MAX_MODULE_RESPONSE_BYTES,
    MODULE_TOOLS,
    TutorAdapter,
)
from ds60sqlpy.modules import ModuleCatalog  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SECRET = "OFFICIAL MODULE SOLUTION 271828"


@pytest.fixture
def legacy(tmp_path: Path) -> Catalog:
    for name in ("python/ds-60day", "sql/postgres-60day", "curriculum"):
        (tmp_path / name).mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text('[project]\nname="fixture"\n')
    (tmp_path / "guide.md").write_text("# Legacy guide\nPredict one value.\n")
    (tmp_path / "learner.py").write_text("raise AssertionError('source must never run')\n")
    (tmp_path / "solution.md").write_text("Legacy separate solution\n")
    lesson = Lesson(
        "python-01",
        "python",
        1,
        "Legacy lesson",
        "beginner",
        "foundations",
        30,
        (),
        "learner.py",
        "guide.md",
        ("solution.md",),
        "core",
        "offline",
    )
    (tmp_path / "curriculum/catalog.json").write_text(json.dumps({"lessons": [asdict(lesson)]}))
    return Catalog.load(tmp_path)


@pytest.fixture
def tutor(legacy: Catalog, monkeypatch: pytest.MonkeyPatch) -> TutorAdapter:
    root = legacy.repo_root
    plans = root / "docs/expansion/plans"
    plans.mkdir(parents=True)
    (plans / "cpp.json").write_text("{}")
    planned = [
        {
            "id": "cpp-009",
            "title": "Owned values",
            "level": "beginner",
            "minutes": 90,
            "prerequisites": [],
            "runtime": "cpp20",
            "outcome": "Explain a copy",
            "lab": "Compare independent values",
            "verification": "Changed source preserves copy",
            "concepts": ["ownership"],
        },
        {
            "id": "cpp-010",
            "title": "Planned structures",
            "level": "beginner",
            "minutes": 90,
            "prerequisites": ["cpp-009"],
            "runtime": "cpp20",
            "outcome": "Describe a structure",
            "lab": "Future lab",
            "verification": "Future typed check",
            "concepts": ["structure"],
        },
    ]
    plan = {
        "id": "cpp",
        "title": "C++",
        "summary": "Separate ownership and lifetime",
        "stages": [],
        "pilot": {"lesson_id": "cpp-009"},
        "lessons": planned,
    }
    monkeypatch.setattr("ds60sqlpy.modules.load_designs", lambda _root: [plan])
    base = root / "courses/cpp"
    (base / "solutions").mkdir(parents=True)
    for filename, text in {
        "guide.md": "# Guide\nPredict first. Use one hint.\n",
        "learner.cpp": "THIS_IS_LEARNER_SOURCE_NOT_EXECUTABLE\n",
        "learner.py": "raise AssertionError('module source must never execute')\n",
        "solutions/reference.cpp": SECRET,
        "solutions/reference.py": SECRET,
        "solutions/explanation.md": SECRET,
    }.items():
        (base / filename).write_text(text)
    item = {
        "id": "cpp-009",
        "status": "authored",
        "language": "cpp",
        "runtime_profile": "cpp20",
        "guide_path": "courses/cpp/guide.md",
        "source_path": "courses/cpp/learner.cpp",
        "solution_paths": [
            "courses/cpp/solutions/reference.cpp",
            "courses/cpp/solutions/explanation.md",
        ],
        "verification_id": "cpp-ownership-v1",
        "variants": [
            {
                "id": "python",
                "title": "Python comparison",
                "language": "python",
                "runtime_profile": "python-core",
                "source_path": "courses/cpp/learner.py",
                "solution_paths": [
                    "courses/cpp/solutions/reference.py",
                    "courses/cpp/solutions/explanation.md",
                ],
                "verification_id": None,
            }
        ],
    }
    (base / "lessons.json").write_text(
        json.dumps({"schema_version": 1, "track_id": "cpp", "lessons": [item]})
    )
    return TutorAdapter(CoachingService(legacy))


def test_module_discovery_is_read_only_and_does_not_inflate_variant_counts(
    tutor: TutorAdapter,
) -> None:
    specs = {tool["name"]: tool for tool in tutor.tools()}
    assert specs.keys() >= MODULE_TOOLS
    assert all(specs[name]["annotations"]["readOnlyHint"] for name in MODULE_TOOLS)
    assert all(specs[name]["inputSchema"]["additionalProperties"] is False for name in MODULE_TOOLS)
    result = tutor.invoke("module_subjects", {})
    assert result["authored_count"] == 1 and result["planned_count"] == 2
    assert result["unwritten_count"] == 1 and result["additional_variants"] == 1
    assert result["runtime_status"] == "not_probed"
    page = tutor.invoke("module_lessons", {})
    assert page["total"] == 1 and page["lessons"][0]["id"] == "cpp-009"
    assert page["lessons"][0]["variants"][1]["id"] == "cpp-009@python"
    assert "solution_paths" not in json.dumps(page) and SECRET not in json.dumps(result)
    assert not (tutor.service.catalog.repo_root / ".learning").exists()


def test_planned_metadata_requires_an_explicit_filter_and_cannot_be_opened(
    tutor: TutorAdapter,
) -> None:
    result = tutor.invoke("module_lessons", {"status": "planned"})
    assert [item["id"] for item in result["lessons"]] == ["cpp-010"]
    assert result["lessons"][0]["status"] == "planned"
    assert "source_path" not in json.dumps(result) and "solution" not in json.dumps(result)
    with pytest.raises(ValueError, match="authored"):
        tutor.invoke("module_lesson", {"lesson_id": "cpp-010"})


def test_module_pagination_binds_filters_and_excludes_legacy_cursors(tutor: TutorAdapter) -> None:
    first = tutor.invoke("module_lessons", {"status": "all", "limit": 1})
    second = tutor.invoke(
        "module_lessons", {"status": "all", "limit": 1, "cursor": first["next_cursor"]}
    )
    assert [item["id"] for item in second["lessons"]] == ["cpp-010"]
    assert second["next_cursor"] is None
    with pytest.raises(ValueError, match="cursor"):
        tutor.invoke(
            "module_lessons", {"status": "authored", "limit": 1, "cursor": first["next_cursor"]}
        )
    assert tutor.invoke("module_lessons", {"query": "no matching concept"})["total"] == 0


@pytest.mark.parametrize(
    "name,arguments",
    [
        ("module_subjects", {"worker_url": "http://remote.example"}),
        ("module_lessons", {"status": "published"}),
        ("module_lessons", {"limit": 0}),
        ("module_lessons", {"subject": "shell"}),
        ("module_lesson", {"lesson_id": "../../secret"}),
        ("module_lesson", {"lesson_id": "cpp-009", "path": "solution.md"}),
        ("module_solution", {"lesson_id": "cpp-009"}),
        ("module_solution", {"lesson_id": "cpp-009", "reveal": False}),
        ("module_solution", {"lesson_id": "cpp-009", "reveal": "true"}),
        ("module_solution", {"lesson_id": "cpp-009", "reveal": 1}),
    ],
)
def test_module_schemas_reject_paths_execution_and_implicit_solutions(
    tutor: TutorAdapter,
    name: str,
    arguments: dict[str, Any],
) -> None:
    with pytest.raises(ValueError, match="Invalid tool arguments"):
        tutor.invoke(name, arguments)


def test_guide_and_variant_reads_never_open_official_solution_files(
    tutor: TutorAdapter,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tutor.invoke("module_subjects", {})
    original = Path.open

    def guarded(path: Path, *args: Any, **kwargs: Any) -> Any:
        if "solutions" in path.parts:
            raise AssertionError("A normal read touched official solutions")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded)
    normal = tutor.invoke("module_lesson", {"lesson_id": "cpp-009"})
    variant = tutor.invoke("module_lesson", {"lesson_id": "cpp-009@python"})
    assert normal["language"] == "cpp" and "LEARNER_SOURCE" in normal["learner"]["text"]
    assert variant["language"] == "python" and variant["base_id"] == "cpp-009"
    assert "must never execute" in variant["learner"]["text"]
    assert SECRET not in json.dumps(normal) and "solution_paths" not in json.dumps(variant)


def test_explicit_solution_read_is_curated_and_bounded(tutor: TutorAdapter) -> None:
    result = tutor.invoke("module_solution", {"lesson_id": "cpp-009@python", "reveal": True})
    assert result["revealed"] is True and len(result["documents"]) == 2
    assert all(SECRET in document["text"] for document in result["documents"])
    assert len(json.dumps(result).encode()) < MAX_MODULE_RESPONSE_BYTES


@pytest.mark.parametrize("field", ["guide_path", "source_path", "solution_paths"])
def test_mutable_authored_links_are_rejected_at_read_time(
    tutor: TutorAdapter,
    tmp_path: Path,
    field: str,
) -> None:
    tutor.invoke("module_subjects", {})
    lesson = tutor._modules().get("cpp-009")
    relative = lesson.solution_paths[0] if field == "solution_paths" else getattr(lesson, field)
    path = tutor.service.catalog.repo_root / relative
    outside = tmp_path / "outside-private.txt"
    outside.write_text("OUTSIDE_PRIVATE_SENTINEL")
    path.unlink()
    try:
        path.symlink_to(outside)
    except OSError:
        pytest.skip("This host cannot create a symlink without extra privileges.")
    name = "module_solution" if field == "solution_paths" else "module_lesson"
    arguments = {"lesson_id": "cpp-009", **({"reveal": True} if name == "module_solution" else {})}
    with pytest.raises(ValueError):
        tutor.invoke(name, arguments)


def test_module_document_size_limits_do_not_silently_truncate(tutor: TutorAdapter) -> None:
    tutor.invoke("module_subjects", {})
    guide = tutor.service.catalog.repo_root / "courses/cpp/guide.md"
    guide.write_text("x" * (MAX_MODULE_DOCUMENT_BYTES + 1))
    with pytest.raises(ValueError, match="size limit"):
        tutor.invoke("module_lesson", {"lesson_id": "cpp-009"})


def test_legacy_checkout_keeps_original_tools_when_modules_are_absent(legacy: Catalog) -> None:
    adapter = TutorAdapter(CoachingService(legacy))
    assert not MODULE_TOOLS.intersection(tool["name"] for tool in adapter.tools())
    assert adapter.invoke("course_lessons", {})["total"] == 1
    with pytest.raises(ValueError, match="unavailable"):
        adapter.invoke("module_subjects", {})
    assert not (legacy.repo_root / ".learning").exists()


def test_module_reads_never_construct_services_jobs_or_probe_workers(
    tutor: TutorAdapter,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Read-only MCP attempted a runtime operation")

    monkeypatch.setattr("ds60sqlpy.module_service.ModuleService.__init__", forbidden)
    monkeypatch.setattr("ds60sqlpy.module_jobs.ModuleJobs.__init__", forbidden)
    monkeypatch.setattr("ds60sqlpy.module_jobs.WorkerClient.__init__", forbidden)
    monkeypatch.setattr("ds60sqlpy.worker_operations.probe_profile", forbidden)
    before = set(tutor.service.catalog.repo_root.rglob("*"))
    tutor.invoke("module_subjects", {})
    tutor.invoke("module_lessons", {})
    tutor.invoke("module_lesson", {"lesson_id": "cpp-009"})
    tutor.invoke("module_solution", {"lesson_id": "cpp-009", "reveal": True})
    assert set(tutor.service.catalog.repo_root.rglob("*")) == before


def test_real_stdio_discovers_modules_without_network_processes_or_progress(tmp_path: Path) -> None:
    async def exchange() -> None:
        guard = (
            "import runpy,sys; "
            "sys.addaudithook(lambda event,args: "
            "(_ for _ in ()).throw(RuntimeError('runtime forbidden')) "
            "if event in {'socket.connect','socket.bind','subprocess.Popen','os.system'} "
            "or event=='open' and '.learning' in str(args[0]).replace('\\\\','/').split('/') "
            "else None); sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='__main__')"
        )
        if os.name == "nt":
            # Windows asyncio uses an internal socket pair, not a worker/listener.
            guard = guard.replace("'socket.connect','socket.bind',", "")
        params = StdioServerParameters(
            command=sys.executable,
            args=["-c", guard, str(ROOT / "scripts/mcp_server.py"), "--repo", str(ROOT)],
            cwd=str(tmp_path),
            env={
                "PYTHONPATH": str(ROOT / "src"),
                "PYTHONUTF8": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
            },
        )
        # The first tools/list validates every authored module path in the real
        # corpus. Four parallel workers can make its filesystem traversal exceed
        # 20 seconds. Keep a bounded protocol deadline without relaxing any audit
        # restriction on network, child processes, or learner-state access.
        async with (
            stdio_client(params) as (read, write),
            ClientSession(read, write, read_timeout_seconds=60) as session,
        ):
            await session.initialize()
            names = {tool.name for tool in (await session.list_tools()).tools}
            assert names >= MODULE_TOOLS and "course_lesson" in names
            subjects = await session.call_tool("module_subjects", {})
            assert not subjects.is_error
            assert {s["id"] for s in subjects.structured_content["subjects"]} == {
                p["id"] for p in ModuleCatalog(ROOT).plans
            }
            page = await session.call_tool("module_lessons", {"subject": "scala-spark"})
            assert not page.is_error and all(
                item["status"] == "authored" for item in page.structured_content["lessons"]
            )
            lesson = await session.call_tool("module_lesson", {"lesson_id": "spark-013@pyspark"})
            assert not lesson.is_error and lesson.structured_content["language"] == "python"
            assert lesson.structured_content["runtime_status"] == "not_probed"
            bad = await session.call_tool(
                "module_solution", {"lesson_id": "cpp-009", "reveal": False}
            )
            assert bad.is_error
            legacy_page = await session.call_tool("course_lessons", {"limit": 1})
            assert not legacy_page.is_error

    asyncio.run(exchange())
