"""Hive source stays readable while its native grammar boundary remains explicit."""

from pathlib import Path

import pytest

from ds60sqlpy.curriculum_framework import RUNNER_SOURCE_SUFFIXES, TEXT_ARTIFACT_SUFFIXES
from ds60sqlpy.lesson_reader import render_artifact
from scripts.format_repo import exclusion, language_for, load_policy

ROOT = Path(__file__).resolve().parents[1]


def test_hive_source_is_highlighted_escaped_and_identifies_its_owned_runtime(
    tmp_path: Path,
) -> None:
    source = tmp_path / "example.hql"
    source.write_text("CREATE EXTERNAL TABLE sample (value STRING); -- <script>literal</script>\n")
    document = render_artifact(source, repo_root=tmp_path, targets={})
    assert "separately prepared owned Hive project" in document
    assert "syntax-keyword" in document
    assert "&lt;script&gt;" in document and "<script>literal" not in document
    assert ".hql" in TEXT_ARTIFACT_SUFFIXES
    assert ".hql" not in RUNNER_SOURCE_SUFFIXES["sql"]


@pytest.mark.parametrize("name", ["initialize.hql", "iceberg.hql"])
def test_owned_hive_dialect_is_preserved_with_a_native_verification_reason(name: str) -> None:
    path = "courses/apache-data-platforms/projects/hive/" + name
    assert language_for(path) is None
    reason = exclusion(path, load_policy(ROOT))
    assert reason is not None and "Hive SQL" in reason and "native lifecycle" in reason
    assert exclusion("courses/unreviewed/arbitrary.hql", load_policy(ROOT)) is None
