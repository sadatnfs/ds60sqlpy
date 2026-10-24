"""SQL formatting preserves SQL values, psql controls and executable meaning."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts import sql_formatting as sql_style

PROTECTED_SQL = (
    "SELECT 'literal -- not comment \\gset :hidden', \"Odd.Identifier\";\n"
    "SELECT E'line\\nquote\\'end', 'apostrophe''kept';\n"
    "DO $body$ BEGIN RAISE NOTICE 'unchanged :value \\if'; END $body$;\n"
    "/* outer 'quoted' /* inner \\gexec */ still outer */\n"
    "-- untouched 'comment' \\if :value\n"
    "SELECT :'literal_variable', :\"identifier_variable\", :raw_variable \\gset result_\n"
    "\\if :enabled\n"
    "\\ir 'fixture with spaces.sql'\n"
    "\\endif\n"
)


def test_protect_restore_roundtrip_keeps_all_sql_and_psql_bytes() -> None:
    protected, replacements = sql_style.protect_sql(PROTECTED_SQL)
    assert replacements
    assert sql_style.restore_sql(protected, replacements) == PROTECTED_SQL
    assert "literal -- not comment" not in protected
    assert "BEGIN RAISE NOTICE" not in protected
    assert "Odd.Identifier" not in protected


def test_escape_backslash_literals_are_hidden_and_restore_exactly_twice() -> None:
    source = "SELECT 'x' LIKE 'x' ESCAPE '\\';\nSELECT 'y' LIKE 'y' ESCAPE '\\';\n"
    protected, replacements = sql_style.protect_sql(source)
    assert "ESCAPE '\\'" not in protected
    assert sql_style.restore_sql(protected, replacements) == source
    assert source.count("ESCAPE '\\'") == 2


@pytest.mark.parametrize(
    "source",
    [
        "SELECT E'escaped\\'quote';\n",
        "SELECT 'first''second';\n",
        'SELECT "A""B" FROM "odd.table";\n',
        "DO $$ BEGIN RAISE NOTICE 'do not format this body'; END $$;\n",
        "DO $tag$ BEGIN /* nested */ RAISE NOTICE ':var \\gexec'; END $tag$;\n",
        "/* outside /* inner 'quoted' */ still outside */ SELECT 1;\n",
    ],
)
def test_literal_and_nested_comment_variants_roundtrip(source: str) -> None:
    protected, replacements = sql_style.protect_sql(source)
    assert sql_style.restore_sql(protected, replacements) == source


def test_psql_controls_and_variables_roundtrip_without_evaluation() -> None:
    source = (
        "\\set ON_ERROR_STOP on\n"
        "SELECT :'input', :\"column_name\", :value AS value \\gset prefix_\n"
        "\\if :{?input}\n"
        "\\ir path-that-does-not-exist.sql\n"
        "\\else\n"
        "SELECT 1 \\gexec\n"
        "\\endif\n"
    )
    protected, replacements = sql_style.protect_sql(source)
    assert sql_style.restore_sql(protected, replacements) == source
    parser_source = sql_style.sql_for_parser(source)
    assert "path-that-does-not-exist" not in parser_source
    assert "\\gset" not in parser_source and "\\gexec" not in parser_source


def test_new_placeholders_never_collide_with_existing_source_text() -> None:
    _protected, replacements = sql_style.protect_sql("SELECT 'original';\n")
    marker = replacements[0][0]
    source = f"SELECT {marker}, 'another value';\n"
    protected, replacements = sql_style.protect_sql(source)
    assert all(placeholder not in source for placeholder, _value in replacements)
    assert sql_style.restore_sql(protected, replacements) == source


@pytest.mark.parametrize("corruption", ["missing", "duplicate"])
def test_restore_rejects_lost_or_duplicated_placeholders(corruption: str) -> None:
    protected, replacements = sql_style.protect_sql("SELECT 'important';\n")
    marker = replacements[0][0]
    if corruption == "missing":
        protected = protected.replace(marker, "not_the_placeholder", 1)
    else:
        protected += marker
    with pytest.raises(sql_style.SQLFormatError):
        sql_style.restore_sql(protected, replacements)


def fake_formatter(monkeypatch: pytest.MonkeyPatch, transform: Any, status: int = 0) -> list[bytes]:
    observed: list[bytes] = []

    def run(command: list[str], **kwargs: Any) -> Any:
        assert command[0] == "pg_format" and "--no-rcfile" in command
        raw = kwargs["input"]
        value = raw.encode() if isinstance(raw, str) else raw
        observed.append(value)
        formatted = transform(value)
        if isinstance(raw, str):
            return subprocess.CompletedProcess(
                command, status, stdout=formatted.decode(), stderr="formatter diagnostic"
            )
        return subprocess.CompletedProcess(
            command, status, stdout=formatted, stderr=b"formatter diagnostic"
        )

    monkeypatch.setattr(subprocess, "run", run)
    return observed


def test_formatter_never_sees_escape_literals_or_dollar_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = (
        b"SELECT 'x' LIKE 'x' ESCAPE '\\';\n"
        b"SELECT 'y' LIKE 'y' ESCAPE '\\';\n"
        b"DO $body$ BEGIN RAISE NOTICE 'literal \\gset :variable'; END $body$;\n"
    )
    observed = fake_formatter(monkeypatch, lambda value: value)
    assert sql_style.format_sql_bytes(source) == source
    assert len(observed) == 1
    assert b"ESCAPE '\\'" not in observed[0]
    assert b"BEGIN RAISE NOTICE" not in observed[0]


def test_sql_formatter_rejects_semantic_change_in_unprotected_expression(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_formatter(monkeypatch, lambda value: value.replace(b"1 + 2", b"1 - 2"))
    with pytest.raises(sql_style.SQLFormatError):
        sql_style.format_sql_bytes(b"SELECT 1 + 2;\n")


def test_sql_formatter_keeps_psql_controls_outside_external_formatter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = b"SELECT :'input' AS value \\gset result_\n"
    observed = fake_formatter(monkeypatch, lambda value: value)
    formatted = sql_style.format_sql_bytes(source)
    assert formatted.count(b"\\gset result_\n") == 1
    assert observed and all(b"\\gset" not in value for value in observed)
    assert all(b":'input'" not in value for value in observed)
    fake_formatter(monkeypatch, lambda _value: b"SELECT 1;\n")
    with pytest.raises(sql_style.SQLFormatError):
        sql_style.format_sql_bytes(source)


def test_formatting_failure_and_invalid_sql_never_overwrite_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "lesson.sql"
    original = b"SELECT 1;\n"
    path.write_bytes(original)
    fake_formatter(monkeypatch, lambda _value: b"partial output", status=1)
    assert not sql_style.format_sql_paths([path.name], tmp_path, check=False)
    assert path.read_bytes() == original
    path.write_bytes(b"SELECT FROM;\n")
    fake_formatter(monkeypatch, lambda value: value)
    assert not sql_style.format_sql_paths([path.name], tmp_path, check=False)
    assert path.read_bytes() == b"SELECT FROM;\n"


def test_semantic_guard_failure_does_not_overwrite_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "lesson.sql"
    original = b"SELECT 1 + 2;\n"
    path.write_bytes(original)
    fake_formatter(monkeypatch, lambda value: value.replace(b"1 + 2", b"1 - 2"))
    assert not sql_style.format_sql_paths([path.name], tmp_path, check=False)
    assert path.read_bytes() == original


def test_readonly_check_reports_drift_and_write_mode_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "lesson.sql"
    original = b"  SELECT 1;  \n"
    path.write_bytes(original)
    fake_formatter(monkeypatch, lambda value: value.strip() + b"\n")
    assert not sql_style.format_sql_paths([path.name], tmp_path, check=True)
    assert path.read_bytes() == original
    assert sql_style.format_sql_paths([path.name], tmp_path, check=False)
    assert path.read_bytes() == b"SELECT 1;\n"
    assert sql_style.format_sql_paths([path.name], tmp_path, check=True)
    assert sql_style.format_sql_bytes(path.read_bytes()) == path.read_bytes()


def test_unicode_literals_identifiers_and_later_tokens_remain_exact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = "SELECT 'café 🐍' AS \"café名\", 42, 'final';\n".encode()
    fake_formatter(monkeypatch, lambda value: value.strip() + b"\n")
    assert sql_style.format_sql_bytes(source) == source


def test_extra_statement_terminator_before_psql_gset_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = b"SELECT 1 AS answer \\gset result_\n"
    fake_formatter(monkeypatch, lambda value: value.rstrip() + b";\n")
    with pytest.raises(sql_style.SQLFormatError):
        sql_style.format_sql_bytes(source)
