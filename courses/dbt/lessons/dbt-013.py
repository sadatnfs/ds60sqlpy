"""dbt-013: worked starting point; complete the guide's six changes."""

import os
import tempfile
from pathlib import Path

import yaml


def project(directory, models=None, seeds=None, schema=None, snapshots=None, macros=None):
    os.environ["DBT_SEND_ANONYMOUS_USAGE_STATS"] = "false"
    os.environ["DBT_USE_COLORS"] = "false"
    os.environ["DO_NOT_TRACK"] = "true"
    root = Path(directory) / "project"
    root.mkdir(parents=True)
    for folder in ("models", "seeds", "snapshots", "macros"):
        (root / folder).mkdir()
    config = {
        "name": "classroom",
        "version": "1.0",
        "config-version": 2,
        "profile": "classroom",
        "model-paths": ["models"],
        "seed-paths": ["seeds"],
        "snapshot-paths": ["snapshots"],
        "macro-paths": ["macros"],
    }
    (root / "dbt_project.yml").write_text(yaml.safe_dump(config))
    output = {
        "type": "duckdb",
        "path": str(root / "warehouse.duckdb"),
        "schema": "main",
        "threads": 1,
        "settings": {"threads": 2, "memory_limit": "256MB"},
    }
    (root / "profiles.yml").write_text(
        yaml.safe_dump({"classroom": {"target": "dev", "outputs": {"dev": output}}})
    )
    for name, sql in (models or {"answer": "select 42::integer as answer"}).items():
        (root / "models" / (name + ".sql")).write_text(sql)
    for name, csv in (seeds or {}).items():
        (root / "seeds" / (name + ".csv")).write_text(csv)
    if schema:
        (root / "models/schema.yml").write_text(yaml.safe_dump({"version": 2, **schema}))
    if snapshots:
        (root / "snapshots/snapshots.yml").write_text(
            yaml.safe_dump({"version": 2, "snapshots": snapshots})
        )
    for name, sql in (macros or {}).items():
        (root / "macros" / (name + ".sql")).write_text(sql)
    return root


def invoke(root, *arguments, succeeds=True):
    from dbt.cli.main import dbtRunner

    result = dbtRunner().invoke(
        [
            "--quiet",
            "--no-use-colors",
            "--no-send-anonymous-usage-stats",
            *arguments,
            "--project-dir",
            str(root),
            "--profiles-dir",
            str(root),
            "--no-partial-parse",
        ]
    )
    if succeeds:
        assert result.success, str(result.exception)
    else:
        assert not result.success, "The deliberately invalid fixture was accepted."
    return result


def names(result):
    return [str(value) for value in result.result]


def example_one():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d,
            models={
                "base": "{{ config(tags=['feature']) }} select 1 as x",
                "child": "select x+1 as x from {{ ref('base') }}",
                "unrelated": "select 9 as x",
            },
        )
        invoke(p, "parse")
        selected = names(
            invoke(
                p, "ls", "--select", "tag:feature+", "--resource-type", "model", "--output", "name"
            )
        )
        assert set(selected) == {"base", "child"}, selected
        return {"selected_models": sorted(selected)}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Select tag:feature without the plus suffix.
# TODO 2: Edit the unrelated model and inspect state selection.
# TODO 3: Store prior manifest data outside target/.
# TODO 4: Explain why new source rows can matter without a model-file edit.
# TODO 5: Include tests and examine the resource types returned.
# TODO 6: List the evidence needed to justify a reduced build.
