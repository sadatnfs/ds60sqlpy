"""Preserve generator/evidence contracts while formatting actual authored metadata."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import format_repo as formatting

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "path",
    [
        "courses/advanced-spark-modeling/track.json",
        "courses/advanced-spark-modeling/lessons.json",
        "courses/advanced-spark-modeling/coverage.json",
        "courses/custom-likelihood-pytorch/track.json",
        "courses/custom-likelihood-pytorch/lessons.json",
        "courses/python-web/track.json",
        "courses/python-web/lessons.json",
        "courses/python-web/coverage.json",
        "courses/advanced-spark-modeling/projects/spark-tmb/scala/qualification.json",
        "courses/advanced-spark-modeling/projects/spark-tmb/scala/qualification-history/earlier.json",
        "examples/native-ad-core/qualification.json",
    ],
)
def test_generated_metadata_and_exact_receipts_remain_preserved(path: str) -> None:
    assert formatting.exclusion(path, formatting.load_policy(ROOT))


@pytest.mark.parametrize(
    "path",
    [
        "courses/advanced-spark-modeling/authoring/units.json",
        "courses/advanced-spark-modeling/authoring/coverage.json",
        "courses/custom-likelihood-pytorch/authoring/units.json",
        "courses/custom-likelihood-pytorch/coverage.json",
        "courses/python-web/authoring/units.json",
        "courses/python-web/authoring/coverage.json",
        "courses/tmb-modeling/track.json",
        "courses/tmb-modeling/lessons.json",
        "courses/tmb-modeling/cpp-api-families.json",
        "courses/advanced-spark-modeling/examples/asm-001.py",
        "courses/custom-likelihood-pytorch/examples/clp-001.py",
        "courses/python-web/examples/pyweb-001.py",
        "courses/advanced-spark-modeling/projects/spark-tmb/scala/src/main/scala/ds60/spark/tmb/TMBDataFrame.scala",
        "examples/native-ad-core/tmbad_probe.cpp",
        "docker/ci-profile-groups.json",
        "docker/ci-scientific-projects.json",
    ],
)
def test_authored_metadata_and_runtime_sources_remain_formatter_eligible(path: str) -> None:
    assert (ROOT / path).is_file()
    assert formatting.exclusion(path, formatting.load_policy(ROOT)) is None
