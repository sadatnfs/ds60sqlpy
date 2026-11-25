from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_guide_examples", ROOT / "scripts/check_guide_examples.py"
)
assert SPEC is not None and SPEC.loader is not None
harness = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = harness
SPEC.loader.exec_module(harness)


def block(text: str, **fields: Any) -> Any:
    values: dict[str, Any] = {
        "guide": "guides/demo.md",
        "lesson": "demo",
        "track": "python-core",
        "runtime": "python",
        "index": 1,
        "line": 1,
        "tag": "python",
        "language": "python",
        "flags": frozenset(),
        "text": text,
    }
    values.update(fields)
    return harness.Block(**values)


def test_failed_sql_block_passes_only_as_a_verbatim_lesson_excerpt(tmp_path: Path) -> None:
    lesson = tmp_path / "lessons/demo.sql"
    lesson.parent.mkdir()
    lesson.write_text(
        "CREATE TEMP TABLE t (id int);\nSELECT id,   -- the key\n  count(*) FROM t GROUP BY id;\n",
        encoding="utf-8",
    )
    postgres = harness.Postgres("psql", "postgres", tmp_path)
    error = 'ERROR:  relation "t" does not exist'
    excerpt = block("SELECT id, count(*)\nFROM t GROUP BY id;", lesson_path="lessons/demo.sql")
    widened = block("SELECT id, count(*) FROM t GROUP BY idx;", lesson_path="lessons/demo.sql")
    for item in (excerpt, widened):
        item.settle(False, error)
        postgres.excerpt(item)

    assert (excerpt.kind, excerpt.status) == ("sql-excerpt", "passed")
    assert "lessons/demo.sql" in excerpt.detail and error in excerpt.detail
    assert widened.status == "failed"


def test_fence_tokens_set_flags_and_a_repository_prelude(tmp_path: Path) -> None:
    (tmp_path / "guides").mkdir()
    (tmp_path / "guides/setup.py").write_text("VALUE = 1\n", encoding="utf-8")
    guide = "guides/demo.md"

    assert harness._prelude(tmp_path, guide, ["prelude=setup.py"]) == ("VALUE = 1\n", "")
    assert "only one" in harness._prelude(tmp_path, guide, ["prelude=a", "prelude=b"])[1]
    assert "inside the repository" in harness._prelude(tmp_path, guide, ["prelude=../../x"])[1]

    fence = chr(96) * 3
    markdown = f"{fence}sql fragment\nGROUP BY a\n{fence}\n\n{fence}python external\nx\n{fence}\n"
    infos = [info for _line, info, _code in harness.fenced_blocks(markdown)]
    assert infos == ["sql fragment", "python external"]


def test_classify_skips_flagged_blocks_and_rejects_unsupported_preludes() -> None:
    fragment = block("x", flags=frozenset({"fragment"}))
    external = block("x", flags=frozenset({"external"}))
    js_prelude = block("x", tag="javascript", language="javascript", prelude="var v = 1;")
    harness.classify([fragment, external, js_prelude], ROOT)

    assert (fragment.status, fragment.detail) == ("skipped", "marked fragment")
    assert (external.status, external.detail) == ("skipped", "marked external")
    assert js_prelude.status == "failed" and "only for Python, R and Scala" in js_prelude.detail


def test_a_fence_profile_overrides_the_lesson_runtime() -> None:
    assert harness._fence_profile(["fragment", "profile=python-core"]) == ("python-core", "")
    assert "only one" in harness._fence_profile(["profile=go", "profile=julia"])[1]
    assert "unknown worker profile" in harness._fence_profile(["profile=nope"])[1]

    routed = block("import pandas", runtime="spark-local-python", fence_profile="python-core")
    wrong = block("x", tag="scala", language="scala", fence_profile="python-core")
    harness.classify([routed, wrong], ROOT)

    assert (routed.kind, routed.profile) == ("session", "python-core")
    assert wrong.status == "failed" and "does not run 'scala'" in wrong.detail


def test_r_prelude_runs_as_its_own_step_before_the_block() -> None:
    item = block("y <- x + 1", tag="r", language="r", index=4, prelude="x <- 1")
    source = harness.build_session("r", [], [item])

    prelude = f'list(4L, "{b"x <- 1".hex()}", NA)'
    recorded = f'list(4L, "{b"y <- x + 1".hex()}", TRUE)'
    assert prelude in source and recorded in source
    assert source.index(prelude) < source.index(recorded)


def test_spark_python_sessions_build_the_spark_session_first() -> None:
    item = block("spark.range(3).count()", profile="spark-local-python")
    spark = harness.build_session("python", [], [item], "spark-local-python")
    plain = harness.build_session("python", [], [item], "python-core")

    assert "getOrCreate()" in spark and "owned_root = None" in spark
    assert "SparkSession" not in plain


def test_spark_scala_blocks_run_after_the_earlier_blocks_of_their_guide() -> None:
    prelude = "import java.util.UUID\nobject Main {\n  def helper(): Int = 1\n}\n"
    first = block("val raw = spark.range(3)", tag="scala", language="scala", index=1)
    second = block(
        "val total = raw.count() + helper()",
        tag="scala",
        language="scala",
        index=2,
        prelude=prelude,
    )
    whole = block("object Main extends App { println(1) }", tag="scala", language="scala", index=3)
    for item in (first, second, whole):
        item.profile = "spark-local-scala"

    sources = harness.scala_sources([first, second, whole])

    assert "val spark = SparkSession.builder()" in sources[1]
    assert "object Ds60Prelude" not in sources[1]
    assert sources[2].index("val raw") < sources[2].index("val total")
    assert "object Ds60Prelude {" in sources[2] and "import Ds60Prelude._" in sources[2]
    assert sources[2].count("object Main") == 1
    assert sources[3] == whole.text


def test_track_images_put_a_track_in_its_own_lane() -> None:
    tmb = block("x <- 1", tag="r", language="r", track="tmb-modeling", kind="session")
    other = block("x <- 2", tag="r", language="r", guide="guides/other.md", kind="session")
    for item in (tmb, other):
        item.profile = "r-statistics"

    jobs = {job.blocks[0].track: job for job in harness.build_jobs([tmb, other], {"tmb-modeling"})}

    assert jobs["tmb-modeling"].key == "r-statistics@tmb-modeling"
    assert jobs["tmb-modeling"].profile == "r-statistics"
    assert jobs["python-core"].key == "r-statistics"


def test_a_track_that_needs_its_own_image_is_skipped_without_one() -> None:
    def blocks() -> list[Any]:
        return [
            block("x <- 1", tag="r", language="r", track="tmb-modeling", kind="session"),
            block("bash -n x", tag="bash", language="bash", track="tmb-modeling", kind="static"),
            block("x <- 2", tag="r", language="r", track="r-statistics", kind="session"),
        ]

    without = blocks()
    kept = harness.skip_missing_track_images(without, ())
    assert [item.track for item in kept] == ["tmb-modeling", "r-statistics"]
    assert without[0].status == "skipped"
    assert "--track-image tmb-modeling=IMAGE" in without[0].detail

    assert len(harness.skip_missing_track_images(blocks(), {"tmb-modeling"})) == 3


def test_a_crashed_worker_fails_its_blocks_instead_of_the_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def crash(*_args: Any) -> dict[str, dict[str, Any]]:
        raise FileNotFoundError("no interpreter")

    monkeypatch.setattr(harness, "run_host", crash)
    first = block("x = 1", index=1, kind="session")
    first.profile = "python-core"

    harness.run_workers(
        harness.build_jobs([first]), {"python-core": "host:" + sys.executable}, 1, 1e12
    )

    assert first.status == "failed"
    assert "worker crashed: FileNotFoundError" in first.detail


def test_isolated_session_blocks_start_their_own_session() -> None:
    first = block("x = 1", index=1, kind="session")
    second = block("y = x", index=2, kind="session")
    alone = block("z = 3", index=3, kind="session", flags=frozenset({"isolated"}))
    for item in (first, second, alone):
        item.profile = "python-core"

    jobs = harness.build_jobs([first, second, alone])

    assert sorted(len(job.blocks) for job in jobs) == [1, 2]
    assert next(job for job in jobs if len(job.blocks) == 1).blocks == [alone]


@pytest.mark.parametrize(
    ("text", "language"),
    [("%timeit sum(range(3))", "text"), ("best = %timeit -o 1", "text"), ("x = 1", "python")],
)
def test_ipython_blocks_with_magics_are_not_run_as_python(text: str, language: str) -> None:
    item = block(text, tag="ipython")
    harness.classify([item], ROOT)
    assert item.language == language


def run_session(blocks: list[Any]) -> list[tuple[str, str, str]]:
    source = harness.build_session("python", [], blocks)
    done = subprocess.run(
        [sys.executable, "-c", source], capture_output=True, text=True, timeout=60, check=True
    )
    return [
        (number, status, bytes.fromhex(detail).decode())
        for number, status, detail in harness.MARKER.findall(done.stdout)
    ]


def test_python_prelude_defines_names_and_reports_its_own_failure() -> None:
    prelude = (
        "from __future__ import annotations\n"
        "from dataclasses import dataclass\n\n"
        "@dataclass\nclass Point:\n    x: int\n\n"
        "if __name__ == '__main__':\n    raise SystemExit('entry point must not run')\n"
    )
    good = block("assert Point(2).x == 2", prelude=prelude)
    broken = block("print(Missing)", index=2, prelude="raise RuntimeError('boom')")
    broken_prelude_only = block("print('fine')", index=3, prelude="raise RuntimeError('boom')")

    results = run_session([good, broken, broken_prelude_only])

    assert results[0] == ("1", "passed", "")
    assert results[1][1] == "failed"
    assert results[1][2].startswith("the prelude failed: line 4: RuntimeError: boom; then")
    assert "NameError" in results[1][2]
    assert results[2] == ("3", "passed", "")


def test_docker_command_shares_only_the_database_container_network() -> None:
    database = harness.Database.__new__(harness.Database)
    database.container = "ds60-guide-db"
    database.url = "postgresql://postgres@127.0.0.1:5432/advanced_sql_training"

    isolated = harness.docker_command("image", "job")
    shared = harness.docker_command("image", "job", database)

    assert isolated[isolated.index("--network") + 1] == "none"
    assert shared[shared.index("--network") + 1] == "container:ds60-guide-db"
    assert f"{harness.DATABASE_ENV}={database.url}" in shared
    assert not any(item.startswith(harness.DATABASE_ENV) for item in isolated)


def test_lab_environment_forwards_only_the_course_database_url(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("ds60sqlpy.worker_operations")
    namespace: dict[str, Any] = {}
    exec(harness.DRIVER.split("\ndef stanc(")[0], namespace)
    lab_environment = namespace["lab_environment"]
    base = {"PATH": os.defpath, "PYTHONPATH": "/worker", harness.DATABASE_ENV: "ignored"}

    monkeypatch.delenv(harness.DATABASE_ENV, raising=False)
    plain = lab_environment(tmp_path, base)
    monkeypatch.setenv(harness.DATABASE_ENV, "postgresql://postgres@127.0.0.1/db")
    database = lab_environment(tmp_path, base)

    assert harness.DATABASE_ENV not in plain
    assert database[harness.DATABASE_ENV] == "postgresql://postgres@127.0.0.1/db"
    assert "PYTHONPATH" not in database
