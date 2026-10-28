"""dbt-005: worked starting point; complete the guide's six changes."""

import json
import os
import tempfile
from datetime import UTC, datetime, timedelta
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


def artifact(root, name):
    return json.loads((root / "target" / name).read_text())


def freshness_case(stale):
    with tempfile.TemporaryDirectory() as d:
        stamp = datetime.now(UTC) - timedelta(days=2 if stale else 0)
        schema = {
            "sources": [
                {
                    "name": "landing",
                    "schema": "main",
                    "tables": [
                        {
                            "name": "events",
                            "identifier": "raw_events",
                            "config": {
                                "loaded_at_field": "loaded_at",
                                "freshness": {"error_after": {"count": 1, "period": "hour"}},
                            },
                        }
                    ],
                }
            ]
        }
        p = project(
            d,
            models={"events": "select * from {{ source('landing', 'events') }}"},
            seeds={"raw_events": f"id,loaded_at\n1,{stamp.isoformat()}\n"},
            schema=schema,
        )
        invoke(p, "seed")
        invoke(p, "source", "freshness", succeeds=not stale)
        status = artifact(p, "sources.json")["results"][0]["status"]
        assert status == ("error" if stale else "pass"), status
        return {"stale": stale, "status": status}


def example_one():
    return freshness_case(False)


if __name__ == "__main__":
    print(example_one())

# TODO 1: Allow three days for the deliberately old source.
# TODO 2: Describe how a future loaded_at value can mislead an age check.
# TODO 3: Give an old event a recent ingestion timestamp.
# TODO 4: Read sources.json and identify the tested source.
# TODO 5: Explain why one recent row cannot prove a complete batch.
# TODO 6: Specify what happens when freshness fails.
