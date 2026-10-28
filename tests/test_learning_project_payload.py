"""Generated project state must stay outside distributable learning sources."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.course_payload import ignore_private_files


def test_dbt_project_outputs_are_private_but_seed_sources_remain(tmp_path: Path) -> None:
    (tmp_path / "dbt_project.yml").write_text("name: example\n")
    names = ["target", "logs", "dbt_packages", "warehouse.duckdb.tmp", "seeds"]
    for name in names:
        (tmp_path / name).mkdir()
    (tmp_path / "warehouse.duckdb").write_bytes(b"private database")
    (tmp_path / "warehouse.duckdb.wal").write_bytes(b"private write log")
    (tmp_path / "models.sql").write_text("select 42")
    (tmp_path / ".user.yml").write_text("id: synthetic-local-user\n")
    actual = ignore_private_files(
        str(tmp_path),
        names + ["warehouse.duckdb", "warehouse.duckdb.wal", "models.sql", ".user.yml"],
    )
    assert actual == {
        "target",
        "logs",
        "dbt_packages",
        "warehouse.duckdb.tmp",
        "warehouse.duckdb",
        "warehouse.duckdb.wal",
        ".user.yml",
    }


def test_legitimate_target_state_and_database_are_not_globally_excluded(tmp_path: Path) -> None:
    for name in ("target", "state"):
        (tmp_path / name).mkdir()
    (tmp_path / "sample.duckdb").write_bytes(b"public fixture")
    (tmp_path / ".user.yml").write_text("example: public-fixture\n")
    assert (
        ignore_private_files(str(tmp_path), ["target", "state", "sample.duckdb", ".user.yml"])
        == set()
    )


def test_owned_ml_marker_excludes_only_its_generated_state(tmp_path: Path) -> None:
    (tmp_path / "state").mkdir()
    (tmp_path / "models").mkdir()
    marker = tmp_path / ".ds60-ml-project.json"
    marker.write_text(json.dumps({"schema_version": 1, "kind": "local-ml-service"}))
    assert ignore_private_files(str(tmp_path), ["state", "models"]) == {"state"}
    marker.write_text(json.dumps({"schema_version": True, "kind": "local-ml-service"}))
    with pytest.raises(ValueError, match="marker"):
        ignore_private_files(str(tmp_path), ["state"])


def test_dbt_cookie_exclusion_rejects_linked_project_marker(tmp_path: Path) -> None:
    manifest = tmp_path / "public-fixture.yml"
    manifest.write_text("name: synthetic\n")
    (tmp_path / "dbt_project.yml").symlink_to(manifest)
    (tmp_path / ".user.yml").write_text("id: synthetic-local-user\n")
    with pytest.raises(ValueError, match="dbt project marker must not be a link"):
        ignore_private_files(str(tmp_path), [".user.yml"])


def test_private_workshop_models_and_events_do_not_enter_portable_source(tmp_path: Path) -> None:
    from scripts import format_repo
    from scripts.check_public_release import scan
    from scripts.course_payload import stage_course

    root = tmp_path / "source"
    project = root / "courses" / "example" / "projects" / "inference"
    private = project / ".workshop"
    private.mkdir(parents=True)
    (private / "token").write_text("synthetic-private-value")
    (private / "events.json").write_text('{"prompt":"synthetic learner input"}')
    (private / "model.npz").write_bytes(b"synthetic learned parameters")
    (project / "server.py").write_text("print('public source')\n")
    (project / "workshop").write_text("#!/usr/bin/env bash\n")
    staged = tmp_path / "staged"
    stage_course(staged, source_root=root)
    assert not (staged / "courses/example/projects/inference/.workshop").exists()
    assert (staged / "courses/example/projects/inference/server.py").is_file()
    assert (staged / "courses/example/projects/inference/workshop").is_file()
    findings, _ = scan(root, payload=True)
    assert any(item.category == "private directory in distribution" for item in findings)
    assert ".workshop" in format_repo.IGNORED_DIRS


def test_data_product_source_and_fixtures_ship_without_any_private_state(tmp_path: Path) -> None:
    from scripts.course_payload import stage_course

    root = tmp_path / "source"
    project = root / "courses/data-ml-engineering/projects/data-product"
    (project / "product").mkdir(parents=True)
    (project / "fixtures").mkdir()
    (project / "product/server.py").write_text("# Public HTTP source\n")
    (project / "product/publication.py").write_text("# Public publication source\n")
    (project / "fixtures/baseline.json").write_text('{"synthetic": true}\n')
    (project / "run.sh").write_text("#!/usr/bin/env bash\n")
    for directory, name in (
        ("raw", "snapshots.sqlite"),
        ("published", "active.json"),
        ("control", "publications.sqlite"),
        ("private", "token"),
    ):
        target = project / ".workshop" / directory
        target.mkdir(parents=True)
        (target / name).write_bytes(b"synthetic private state")
    staged = tmp_path / "staged"
    stage_course(staged, source_root=root)
    output = staged / "courses/data-ml-engineering/projects/data-product"
    assert not (output / ".workshop").exists()
    for name in ("product/server.py", "product/publication.py", "fixtures/baseline.json", "run.sh"):
        assert (output / name).is_file()
