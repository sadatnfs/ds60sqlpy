# dbt-013: explained reference

Construct and inspect a reproducible selection against an explicit baseline.

The reference parses the project and reads model names from `dbt ls` output for `tag:feature+` and for `state:modified+` against a copied manifest. It proves which nodes each selector expands to for this graph; it does not build or test them. See [how these answers are laid out](../STUDY-GUIDE.md#answers-and-references).


## 1. Remove graph expansion

Use graph operators deliberately and inspect the returned set. A tag on one model does not automatically label every downstream consumer.

**Why it holds here:** tag:feature matches only base, the one model with the tag. The plus suffix adds descendants, which is why example_one returns base and child.

**Plausible wrong approach:** Assuming that child inherits the tag because it reads from base would leave child out of a run that needs it, or include it in an audit list incorrectly.

**How to verify:** Run dbt ls --select tag:feature --resource-type model --output name and expect only base.

**Expected:** Only the explicitly tagged model is selected.

## 2. Add an unrelated change

Record the baseline revision and exact selection expression. The expected scope should be reviewed rather than inferred from a successful command.

**Why it holds here:** state:modified compares the current manifest to the stored copy. Editing unrelated adds it to the modified set, while unrelated has no children to add with the plus.

**Plausible wrong approach:** Assuming a command that ran successfully selected what was intended skips the check of the actual returned names.

**How to verify:** Edit unrelated.sql to select 10 as x and run ls with --state previous_state --select state:modified+; expect unrelated in the list alongside any other edited models.

**Expected:** The changed node appears under the matching state selector.

## 3. Protect the baseline

Use a dedicated state directory or immutable CI artifact. A self-overwritten baseline can incorrectly make changes appear absent.

**Why it holds here:** The reference copies target/manifest.json into previous_state before editing base. If the baseline lived in target/, the next parse would overwrite it with the new manifest.

**Plausible wrong approach:** Pointing --state at target itself compares a manifest to itself and returns no modified nodes, which looks like nothing changed.

**How to verify:** Run parse again after the edit, then check that previous_state/manifest.json still has base's original checksum and the state selection still returns base and child.

**Expected:** The next invocation does not overwrite it.

## 4. Change only data

Use the selection appropriate to the data update and validate relevant outputs. Definition comparison alone cannot establish that existing materializations are current.

**Why it holds here:** state:modified compares definitions like SQL text and config. New rows in a seed or source change the data but not the definition.

**Plausible wrong approach:** Running only modified models after a data load would skip models that depend on the new data and leave their tables out of date.

**How to verify:** Append a row to a seed without editing any SQL, run state:modified+, and observe that no model is selected even though downstream results would change.

**Expected:** The answer distinguishes definitions from data state.

## 5. Inspect selected tests

Review indirect-selection policy and the actual result list. An empty test selection must not be reported as a successful validation suite.

**Why it holds here:** Dropping --resource-type model and adding a test on base lets ls return tests attached to selected models. This depends on the indirect selection mode.

**Plausible wrong approach:** Running dbt test --select state:modified when no tests are attached returns success with zero tests, which is not a validation.

**How to verify:** Add a not_null test on base.x, run ls --select state:modified+ without the resource filter, and expect the test node next to base and child.

**Expected:** The intended tests are visible in the selection.

## 6. Record a CI decision

Keep the source revision, manifest identity, selected node set, commands and actual outcomes. Use a broader gate when the change affects shared semantics or operational assumptions.

**Why it holds here:** A reduced build is justified only when the baseline, selection expression, selected nodes and actual outcomes are all recorded together.

**Plausible wrong approach:** Recording only that CI passed hides which models were skipped and why.

**How to verify:** Store the baseline manifest hash, the exact command, the ls output and run_results statuses, and check that a reviewer can rebuild the same list.

**Expected:** It includes baseline, selection, dependencies and executed results.

## Complete reference

```python
"""dbt-013: actual local dbt and DuckDB reference."""

import os
import shutil
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
                "child": "select x + 1 as x from {{ ref('base') }}",
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


def example_two():
    with tempfile.TemporaryDirectory() as d:
        p = project(
            d, models={"base": "select 1 as x", "child": "select x + 1 as x from {{ ref('base') }}"}
        )
        invoke(p, "parse")
        state = p / "previous_state"
        state.mkdir()
        shutil.copyfile(p / "target/manifest.json", state / "manifest.json")
        (p / "models/base.sql").write_text("select 2 as x")
        selected = names(
            invoke(
                p,
                "ls",
                "--state",
                str(state),
                "--select",
                "state:modified+",
                "--resource-type",
                "model",
                "--output",
                "name",
            )
        )
        assert set(selected) == {"base", "child"}, selected
        return {
            "changed_and_downstream": sorted(selected),
            "state_is_not_a_quality_certificate": True,
        }


def main():
    print(example_one())
    print(example_two())
    print("dbt-013 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Explain which dependencies and tests are included and which data changes are outside the comparison. The later CI lessons connect that selection to real execution and deferral.
