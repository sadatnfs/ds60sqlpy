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
