"""Read-only linting checks real syntax without running lesson programs."""

from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts import lint_repo as linting


def put(root: Path, name: str, source: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    return path


def test_sql_projection_preserves_quotes_comments_and_procedure_bodies() -> None:
    protected = (
        "SELECT ':variable', '\\if :keep', E'escaped\\'quote', \"quoted:name\";\n"
        "-- \\gexec :keep\n"
        "/* outer :keep /* nested */ \\if */\n"
        "DO $body$ BEGIN RAISE NOTICE ':keep \\echo'; END $body$;\n"
        "SELECT 1::integer;\n"
    )
    assert linting.sql_for_parser(protected) == protected


def test_sql_projection_separates_psql_without_resolving_variables_or_includes() -> None:
    source = (
        "\\set ON_ERROR_STOP on\n"
        "SELECT current_database() AS name \\gset\n"
        "\\if :enabled\n"
        "\\ir nonexistent-fixture.sql\n"
        "SELECT :'literal', :\"identifier\", :raw, 1::integer;\n"
        "\\endif\n"
    )
    projected = linting.sql_for_parser(source)
    assert projected.count("\n") == source.count("\n")
    assert "SELECT current_database() AS name ;" in projected
    assert "nonexistent-fixture" not in projected
    assert "'psql_value'" in projected and '"psql_value"' in projected
    assert "1::integer" in projected
    assert ":raw" not in projected and "\\gset" not in projected


@pytest.mark.parametrize(
    "source",
    ["SELECT 'unterminated", "DO $body$ BEGIN;", "/* unclosed", "\\unknown_command\n"],
)
def test_sql_projection_rejects_unsupported_or_incomplete_input(source: str) -> None:
    with pytest.raises(ValueError):
        linting.sql_for_parser(source)


def test_postgresql_parser_accepts_psql_and_rejects_bad_statement(tmp_path: Path) -> None:
    pytest.importorskip("pglast")
    path = put(tmp_path, "lesson.sql", "\\set ON_ERROR_STOP on\nSELECT 1 AS count \\gset\n")
    assert linting.syntax_errors(path.name, tmp_path, "sql") == []
    path.write_text("SELECT FROM;\n")
    assert linting.syntax_errors(path.name, tmp_path, "sql")
    assert path.read_text() == "SELECT FROM;\n"


def test_python_syntax_check_never_executes_valid_source(tmp_path: Path) -> None:
    path = put(tmp_path, "lesson.py", "raise RuntimeError('this program must not run')\n")
    assert linting.syntax_errors(path.name, tmp_path, "python") == []
    path.write_text("def broken(:\n")
    assert linting.syntax_errors(path.name, tmp_path, "python")


def test_notebook_validation_preserves_magic_cells_and_rejects_bad_shape(tmp_path: Path) -> None:
    notebook: dict[str, Any] = {
        "cells": [{"cell_type": "code", "source": ["%%sql\n", "SELECT 1;\n"]}],
        "metadata": {},
    }
    path = put(tmp_path, "lesson.ipynb", json.dumps(notebook))
    original = path.read_bytes()
    assert linting.syntax_errors(path.name, tmp_path, "python") == []
    assert path.read_bytes() == original
    notebook["cells"][0]["source"] = [123]
    path.write_text(json.dumps(notebook))
    assert linting.syntax_errors(path.name, tmp_path, "python")


@pytest.mark.parametrize(
    "name,language,good,bad",
    [
        ("data.json", "web", '{"value": 1}', '{"value": }'),
        ("project.toml", "toml", "value = 1", "value = ["),
        ("project.csproj", "xml", "<Project />", "<Project>"),
        ("compose.yaml", "web", "ports: !override [8080]\n", "ports: [\n"),
    ],
)
def test_data_syntax_checks_accept_supported_formats_and_report_errors(
    tmp_path: Path, name: str, language: str, good: str, bad: str
) -> None:
    if name.endswith("yaml"):
        pytest.importorskip("yaml")
    path = put(tmp_path, name, good)
    assert linting.syntax_errors(name, tmp_path, language) == []
    path.write_text(bad)
    assert linting.syntax_errors(name, tmp_path, language)
    assert path.read_text() == bad


@pytest.mark.parametrize(
    "name,language,good,bad",
    [
        ("main.c", "c", "int main(void) { return 0; }", "int main( {"),
        ("main.cpp", "cpp", "int main() { return 0; }", "int main( {"),
        ("Main.java", "java", "class Main { int n = 1; }", "class Main { int = ;"),
        ("Program.cs", "csharp", "class Main { int n = 1; }", "class Main { int = ;"),
        ("main.go", "go", "package main\nfunc main() {}\n", "package main\nfunc main( {"),
        ("main.rs", "rust", "fn main() {}", "fn main( {"),
        ("main.swift", "swift", 'print("Hello")', "func broken( {"),
        ("main.ts", "web", "const count: number = 1;", "const count: = ;"),
        ("main.js", "web", "const count = 1;", "const = ;"),
    ],
)
def test_bundled_language_grammars_accept_programs_and_report_invalid_syntax(
    tmp_path: Path, name: str, language: str, good: str, bad: str
) -> None:
    pytest.importorskip("tree_sitter_language_pack")
    path = put(tmp_path, name, good)
    assert linting.syntax_errors(name, tmp_path, language) == []
    path.write_text(bad)
    assert linting.syntax_errors(name, tmp_path, language)
    assert path.read_text() == bad


def test_c_linkage_header_projection_keeps_declarations_visible() -> None:
    pytest.importorskip("tree_sitter_language_pack")
    source = (
        b'#ifdef __cplusplus\nextern "C" {\n#endif\n'
        b"int add(int a, int b);\n"
        b"#ifdef __cplusplus\n}\n#endif\n"
    )
    assert linting.grammar_errors("api.h", source, "c") == []
    broken = source.replace(b"int add(int a, int b);", b"int add(;")
    assert linting.grammar_errors("api.h", broken, "c")


def test_missing_parser_dependency_is_a_failure_not_a_skip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    put(tmp_path, "main.rs", "fn main() {}")

    def missing(_name: str) -> Any:
        raise ImportError("grammar unavailable")

    monkeypatch.setattr(importlib, "import_module", missing)
    errors = linting.syntax_errors("main.rs", tmp_path, "rust")
    assert errors and "grammar unavailable" in errors[0]


def test_ruff_quality_rules_do_not_apply_to_unfinished_lesson_pads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    put(tmp_path, "src/app.py", "answer = 42\n")
    put(tmp_path, "courses/demo/lesson.py", "answer = TODO\n")
    put(
        tmp_path,
        "python/lesson.ipynb",
        '{"cells": [{"cell_type": "code", "source": "%sql SELECT 1"}]}',
    )
    commands: list[list[str]] = []

    def record(command: list[str], root: Path) -> bool:
        assert root == tmp_path
        commands.append(command)
        return True

    monkeypatch.setattr(linting, "run", record)
    assert linting.lint_group(
        "python", ["src/app.py", "courses/demo/lesson.py", "python/lesson.ipynb"], tmp_path
    )
    notebook = next(command for command in commands if "./python/lesson.ipynb" in command)
    assert "--isolated" in notebook and "E9" in notebook
    quality = next(command for command in commands if "./src/app.py" in command)
    assert "--config" in quality
    assert all("./courses/demo/lesson.py" not in command for command in commands)
    assert all("--fix" not in command for command in commands)


def test_scala_uses_actual_parser_stdout_without_changing_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = put(
        tmp_path, "main.scala", "object Main { val xs = List(1).map { x => val key = x; key } }\n"
    )
    original = path.read_bytes()

    def record(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        assert command[0] == "scalafmt" and "--stdin" in command and "--stdout" in command
        assert kwargs["input"] == original
        return subprocess.CompletedProcess(command, 0, stdout=b"formatted display\n", stderr=b"")

    monkeypatch.setattr(subprocess, "run", record)
    assert linting.lint_group("scala", [path.name], tmp_path)
    assert path.read_bytes() == original


def test_lint_list_never_runs_checks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    put(tmp_path, "scripts/format-policy.json", '{"exclude": [], "preserve": []}')
    put(tmp_path, "main.py", "not valid Python")
    monkeypatch.setattr(linting, "ROOT", tmp_path)
    monkeypatch.setattr(linting, "lint_group", lambda *_args: pytest.fail("List ran lint"))
    assert linting.main(["--list"]) == 0


def test_lint_language_selection_reports_failure_without_touching_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    put(tmp_path, "scripts/format-policy.json", '{"exclude": [], "preserve": []}')
    source = put(tmp_path, "main.py", "def bad(:\n")
    put(tmp_path, "other.js", "also invalid")
    monkeypatch.setattr(linting, "ROOT", tmp_path)
    assert linting.main(["--language", "python"]) == 1
    assert source.read_text() == "def bad(:\n"


def test_swift_uses_real_parser_for_result_builders_without_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = put(tmp_path, "main.swift", "@resultBuilder enum Builder {}\n")
    original = path.read_bytes()

    def record(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        assert command[:2] == ["swift-format", "format"]
        assert "--in-place" not in command and kwargs["input"] == original
        return subprocess.CompletedProcess(command, 0, stdout=b"formatted display\n", stderr=b"")

    monkeypatch.setattr(subprocess, "run", record)
    assert linting.lint_group("swift", [path.name], tmp_path)
    assert path.read_bytes() == original


TMB_ATOMIC_FIXTURE = (
    b"#include <TMB.hpp>\n"
    b"TMB_ATOMIC_VECTOR_FUNCTION(original, 1,\n"
    b"  ty[0] = helper(tx[0], Type(2));\n"
    b"  , px[0] = Type(4) * tx[0] * py[0];)\n"
    b"int after() { return 3; }\n"
)


def test_tmb_projection_preserves_comments_literals_body_and_lines() -> None:
    protected = (
        b"// SIMULATE { and TMB_ATOMIC_VECTOR_FUNCTION(a,2,b,c)\n"
        b"/* SIMULATE { */\n"
        b'const char* message = "SIMULATE { a,b( )";\n'
        b'const char* raw = u8R"tag(TMB_ATOMIC_VECTOR_FUNCTION(\n'
        b'bad,1,unparsed,body) SIMULATE {)tag";\n'
    )
    source = (
        b"#include <TMB.hpp>\n"
        + protected
        + (b"void model() { SIMULATE /* keep this comment */ { value = 42; } }\n")
    )
    projected = linting.tmb_grammar_source(source)
    assert protected in projected
    assert b"if(true) /* keep this comment */ { value = 42; }" in projected
    assert projected.count(b"\n") == source.count(b"\n")
    atomic = linting.tmb_grammar_source(TMB_ATOMIC_FIXTURE)
    assert b"ty[0] = helper(tx[0], Type(2));" in atomic
    assert b"px[0] = Type(4) * tx[0] * py[0];" in atomic
    assert b"int after() { return 3; }" in atomic
    assert atomic.count(b"\n") == TMB_ATOMIC_FIXTURE.count(b"\n")


@pytest.mark.parametrize(
    "prefix",
    [
        b"// #include <TMB.hpp>\n",
        b'const char* fake = "#include <TMB.hpp>";\n',
        b'const char* fake = R"tag(\n#include <TMB.hpp>\n)tag";\n',
    ],
)
def test_fake_tmb_include_does_not_activate_projection(prefix: bytes) -> None:
    source = prefix + b"void f(){ SIMULATE { value = 1; } }\n"
    assert linting.tmb_grammar_source(source) == source


@pytest.mark.parametrize(
    "body",
    [
        b"TMB_ATOMIC_VECTOR_FUNCTION(name, 1, body;)",
        b"TMB_ATOMIC_VECTOR_FUNCTION(name, 1, one;, two;, third;)",
        b"TMB_ATOMIC_VECTOR_FUNCTION(name, count(), one;, two;)",
        b'TMB_ATOMIC_VECTOR_FUNCTION("bad name", 1, one;, two;)',
        b"TMB_ATOMIC_VECTOR_FUNCTION(name, 1, one;, two;",
        b"SIMULATE(value);",
        b"#define SIMULATE broken\nvoid f(){SIMULATE {}}",
        b"#undef TMB_ATOMIC_VECTOR_FUNCTION\n",
    ],
)
def test_unsupported_tmb_macro_forms_fail_visibly(body: bytes) -> None:
    with pytest.raises(ValueError):
        linting.tmb_grammar_source(b"#include <TMB.hpp>\n" + body)


def test_tmb_atomic_projection_keeps_string_commas_and_digit_separators() -> None:
    source = TMB_ATOMIC_FIXTURE.replace(
        b"ty[0] = helper(tx[0], Type(2));",
        b"""const char* text = "a,b,( )\\\"";
           const char* raw = R"raw(, ) SIMULATE { } )raw";
           auto count = 1'000;
           ty[0] = helper(tx[0], Type(2));""",
    )
    projected = linting.tmb_grammar_source(source)
    assert b'const char* raw = R"raw(, ) SIMULATE { } )raw";' in projected
    assert b"auto count = 1'000;" in projected
    assert source.count(b"\n") == projected.count(b"\n")


def test_real_tmb_models_parse_with_prepared_grammar() -> None:
    pytest.importorskip("tree_sitter_language_pack")
    root = Path(__file__).resolve().parents[1]
    for relative in (
        "courses/tmb-modeling/projects/tmb-local/models/normal_mean.cpp",
        "courses/advanced-spark-modeling/projects/spark-tmb/models/normal_mean.cpp",
        "courses/tmb-modeling/projects/tmb-cpp-api/models/atomic_quartic.cpp",
    ):
        source = (root / relative).read_bytes()
        assert linting.grammar_errors(relative, source, "cpp") == []
        assert (root / relative).read_bytes() == source


@pytest.mark.parametrize(
    "source,line",
    [
        (TMB_ATOMIC_FIXTURE.replace(b"helper(tx[0], Type(2))", b""), 3),
        (TMB_ATOMIC_FIXTURE.replace(b"Type(4) * tx[0] * py[0]", b""), 4),
        (TMB_ATOMIC_FIXTURE.replace(b"return 3;", b"return ( ;"), 5),
        (b"#include <TMB.hpp>\nvoid model() {\nSIMULATE { value = ; }\n}\n", 3),
    ],
)
def test_tmb_projection_does_not_hide_body_or_surrounding_errors(source: bytes, line: int) -> None:
    pytest.importorskip("tree_sitter_language_pack")
    errors = linting.grammar_errors("model.cpp", source, "cpp")
    assert errors and any(f"model.cpp:{line}:" in error for error in errors)


def test_tmb_projection_retains_valid_nested_control_flow() -> None:
    pytest.importorskip("tree_sitter_language_pack")
    source = TMB_ATOMIC_FIXTURE.replace(
        b"ty[0] = helper(tx[0], Type(2));",
        b"if (tx[0] > 0) { ty[0] = helper(tx[0], Type(2)); } else { ty[0] = 0; }",
    )
    assert linting.grammar_errors("model.cpp", source, "cpp") == []
    broken = source.replace(b"if (tx[0] > 0)", b"if (tx[0] > )")
    assert linting.grammar_errors("model.cpp", broken, "cpp")
