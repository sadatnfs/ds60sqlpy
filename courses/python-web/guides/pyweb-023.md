# pyweb-023: Flask CLI and versioned schema changes

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-022`.

## Starting point and result

A web application needs operational commands as well as request handlers. Schema initialization, migrations and maintenance should have explicit entrypoints and observable results. This chapter exercises a real Flask CLI command and a real Alembic schema operation against an owned temporary SQLite database.

## Key terms

- **Flask CLI command:** A Click function registered on the application for an operational task such as initialization and invoked by name instead of through HTTP.
- **CLI runner:** Flask's testing helper that invokes a registered command in process and captures its exit code and output.
- **Schema migration:** A controlled change to an existing database schema that preserves existing data, such as adding a column.
- **Server default:** A column default applied by the database, which lets existing rows receive a value when a nonnullable column is added.
- **Revision history:** The ordered Alembic revision files and version table that record which migrations a database has applied.

## Mechanism: commands and migrations have different responsibilities

The `initialize` CLI command creates the initial table if absent. Flask's CLI runner invokes the actual registered command and captures its outcome. Running it twice verifies this specific initialization's idempotent behavior.

A migration changes an existing schema while preserving the intended data contract. The program creates an Alembic MigrationContext and Operations object on a real connection, then adds a nonnullable boolean column with a server default. Existing rows can receive the default without being dropped or reconstructed by unrelated application code.

This is an operation-level probe. A complete Alembic project also maintains revision files, a version table, environment configuration and an ordered revision graph. The owned application workshop supplies that larger lifecycle. Executing one add-column operation does not establish that revision history, upgrade coordination or rollback has been qualified.

## Worked case: repeat a named initialization command

The test runner invokes `initialize` twice and requires both invocations to succeed. It then inserts an existing row through a parameterized statement. The setup is explicit and local; it does not depend on a previous chapter having created a database.

Idempotence should be evaluated for the command's actual effect. A create-if-absent statement does not guarantee that an already existing table has the expected complete schema. A production startup should verify compatibility rather than assuming that an object with the right name has the right columns and constraints.

## Worked case: evolve the schema without losing the row

The migration operation adds `active` with a true default. A subsequent query sees the original title and active value one, and the schema inspector sees the expected three columns. The assertions therefore cover both data preservation and the resulting shape.

Adding a column is not always operationally cheap on every database/version or with every default. Large tables, locks, backfills and rolling deployments need a planned compatibility strategy. SQLite behavior here must not be silently generalized to a live PostgreSQL deployment. The workshop's actual database operations have separate acceptance.

## Worked example: CLI options, exit codes and failure output

```python
import click
from flask import Flask

app = Flask(__name__)
applied = []


@app.cli.command("migrate")
@click.option("--to", "target", type=int, required=True)
def migrate(target):
    current = applied[-1] if applied else 0
    if target < current:
        raise click.ClickException(f"refusing to downgrade from {current} to {target}")
    applied.extend(range(current + 1, target + 1))
    click.echo(f"at revision {target}")


runner = app.test_cli_runner()
for args in (
    ["migrate", "--to", "2"],
    ["migrate", "--to", "2"],
    ["migrate", "--to", "1"],
    ["migrate"],
):
    result = runner.invoke(args=args)
    print(result.exit_code, result.output.strip().splitlines()[-1])
print(applied)
```

Expected output:

```text
0 at revision 2
0 at revision 2
1 Error: refusing to downgrade from 2 to 1
2 Error: Missing option '--to'.
[1, 2]
```

The test runner invoked the registered command in process and captured both the exit code and the text an operator would see. The second run was a safe no-op, the same rerun property the lesson checks with `CREATE TABLE IF NOT EXISTS`. Raising `ClickException` turned the refused downgrade into exit code 1 with a readable message rather than a traceback, and Click itself returned exit code 2 for the missing required option before the function body ran. Deployment scripts rely on those nonzero codes to stop a rollout, so a command that printed an error but exited 0 would let a failed migration go unnoticed. The final list shows revisions 1 and 2 were applied exactly once despite four invocations.

## Failure diagnosis

A command that works manually but fails under the deployment runner may depend on the wrong configuration, working directory or database credentials. A migration that succeeds on an empty test database can still fail against realistic existing values. Include representative old rows and relevant constraints in migration tests.

Avoid running destructive schema resets as a routine error-recovery step. They can hide a migration defect by deleting the evidence and the learner's data. Versioned evolution, explicit ownership and retained backups are more useful than assuming every database is disposable.

## Interview discussion

**Is `create_all` or create-if-absent a migration system?** It can create missing structures in a bounded scenario, but it does not by itself describe every transition between historical schema versions or manage a reviewed revision graph.

**Can a migration have a successful SQL exit and still be unsafe for a rolling deployment?** Yes. Old and new application processes may coexist. Their read/write assumptions must remain compatible during the transition, including any backfill period.

## Next step

Define how the application depends on an upstream HTTP service. Tests should reproduce success, timeout and failure translation without accidentally contacting an uncontrolled external system.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    import tempfile
    from pathlib import Path

    import click
    import sqlalchemy as sa
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from flask import Flask
    from sqlalchemy import create_engine, inspect, text

    with tempfile.TemporaryDirectory(prefix="pyweb-schema-") as temporary:
        engine = create_engine("sqlite+pysqlite:///" + str(Path(temporary) / "app.sqlite3"))
        app = Flask(__name__)

        @app.cli.command("initialize")
        def initialize():
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "CREATE TABLE IF NOT EXISTS items "
                        "(id INTEGER PRIMARY KEY, title TEXT NOT NULL)"
                    )
                )
            click.echo("schema initialized")

        runner = app.test_cli_runner()
        assert runner.invoke(args=["initialize"]).exit_code == 0
        assert runner.invoke(args=["initialize"]).exit_code == 0
        with engine.begin() as connection:
            connection.execute(
                text("INSERT INTO items (id,title) VALUES (:id,:title)"),
                {"id": 1, "title": "kept row"},
            )
            operations = Operations(MigrationContext.configure(connection))
            operations.add_column(
                "items", sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False)
            )
            assert connection.execute(text("SELECT title,active FROM items")).one() == (
                "kept row",
                1,
            )
        columns = [column["name"] for column in inspect(engine).get_columns("items")]
        assert columns == ["id", "title", "active"]
        engine.dispose()
        return {
            "cli_ran_twice": True,
            "migration_preserved_row": True,
            "columns": columns,
            "migration_revision_history": "operation probe; complete revision project is separate",
        }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Flask documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
