"""Execute one dbt SQL/Jinja model in a fixed local teaching project."""

from __future__ import annotations

import datetime
import decimal
import importlib
import json
import math
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ds60sqlpy import plot_artifacts
from ds60sqlpy.plot_artifacts import publish_report, publish_table

ORDERS = (
    "id,customer_id,amount,status,updated_at\n"
    "1,10,100,paid,2024-01-01\n"
    "2,20,50,paid,2024-01-02\n"
    "3,10,25,refunded,2024-01-03\n"
    "4,30,80,pending,2024-01-04\n"
    "5,20,120,paid,2024-01-05\n"
)
CUSTOMERS = "customer_id,name,region\n10,Ada,north\n20,Ben,south\n30,Cy,north\n"


def cell(value: Any) -> str | int | float | bool | None:
    if value is None:
        return None
    if isinstance(value, (str, bool)):
        return value
    if isinstance(value, int):
        return value if abs(value) <= 9_007_199_254_740_991 else str(value)
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, decimal.Decimal):
        return str(value)
    return json.dumps(value, default=str, ensure_ascii=False)


def capture(function: Callable[..., None], *args: Any, **kwargs: Any) -> None:
    try:
        function(*args, **kwargs)
    except (OSError, ValueError, TypeError, RecursionError) as error:
        print("Result capture warning: " + str(error), file=sys.stderr)


def prepare(directory: Path, source: str) -> Path:
    yaml = importlib.import_module("yaml")
    root = directory / "dbt-project"
    root.mkdir()
    for name in ("models", "seeds"):
        (root / name).mkdir()
    (root / "models/lesson_model.sql").write_text(source, "utf-8")
    (root / "seeds/raw_orders.csv").write_text(ORDERS, "utf-8")
    (root / "seeds/customers.csv").write_text(CUSTOMERS, "utf-8")
    config = {
        "name": "classroom",
        "version": "1.0",
        "config-version": 2,
        "profile": "classroom",
        "model-paths": ["models"],
        "seed-paths": ["seeds"],
        "models": {"classroom": {"+materialized": "table"}},
        "vars": {"report_date": "2024-01-06", "status": "paid"},
    }
    (root / "dbt_project.yml").write_text(yaml.safe_dump(config), "utf-8")
    settings = {
        "type": "duckdb",
        "path": str(root / "warehouse.duckdb"),
        "schema": "main",
        "threads": 1,
        "settings": {"threads": 2, "memory_limit": "256MB"},
    }
    (root / "profiles.yml").write_text(
        yaml.safe_dump({"classroom": {"target": "dev", "outputs": {"dev": settings}}}), "utf-8"
    )
    schema = {
        "version": 2,
        "sources": [
            {
                "name": "raw",
                "schema": "main",
                "tables": [{"name": "orders", "identifier": "raw_orders"}],
            }
        ],
    }
    (root / "models/sources.yml").write_text(yaml.safe_dump(schema), "utf-8")
    return root


def _run() -> int:
    duckdb = importlib.import_module("duckdb")
    dbt_runner = importlib.import_module("dbt.cli.main").dbtRunner
    directory = Path.cwd()
    root = prepare(directory, (directory / "model.sql").read_text("utf-8"))
    results = []
    for command in ("seed", "build"):
        result = dbt_runner().invoke(
            [
                "--no-use-colors",
                "--no-send-anonymous-usage-stats",
                command,
                "--project-dir",
                str(root),
                "--profiles-dir",
                str(root),
                "--no-partial-parse",
            ]
        )
        results.append({"command": command, "success": result.success})
        if not result.success:
            errors = []
            result_path = root / "target/run_results.json"
            if result_path.is_file():
                raw = json.loads(result_path.read_text("utf-8"))
                errors = [
                    {
                        "node": item.get("unique_id"),
                        "status": item.get("status"),
                        "message": str(item.get("message", ""))[:4000],
                    }
                    for item in raw.get("results", [])[:10]
                    if item.get("status") not in {"success", "pass"}
                ]
            capture(
                publish_report,
                {
                    "commands": results,
                    "exception": str(result.exception)[:4000]
                    if result.exception is not None
                    else None,
                    "node_failures": errors,
                },
                description=(
                    "dbt execution failed; inspect the compilation or database diagnostics."
                ),
            )
            return 1
    manifest = json.loads((root / "target/manifest.json").read_text("utf-8"))
    node = manifest["nodes"]["model.classroom.lesson_model"]
    with duckdb.connect(str(root / "warehouse.duckdb"), read_only=False) as connection:
        schema = node["schema"].replace('"', '""')
        alias = node["alias"].replace('"', '""')
        relation = f'"{schema}"."{alias}"'
        count = connection.execute(f"select count(*) from {relation}").fetchone()[0]
        query = connection.execute(f"select * from {relation} limit 100")
        columns = [item[0] for item in query.description]
        types = [str(item[1]) for item in query.description]
        rows = [[cell(value) for value in row[:12]] for row in query.fetchall()]
    capture(
        publish_table,
        columns[:12],
        rows,
        description=(
            f"Actual dbt model result: first {len(rows)} of {count} rows and "
            f"{min(12, len(columns))} of {len(columns)} columns. "
            "Model tables have no ordering guarantee; compare rows by their keys."
        ),
    )
    capture(
        publish_report,
        {
            "commands": results,
            "model": node["unique_id"],
            "materialization": node["config"]["materialized"],
            "dependencies": node["depends_on"]["nodes"],
            "compiled_sql": node.get("compiled_code", ""),
            "columns": columns,
            "types": types,
            "row_count": count,
            "value_representation": (
                "Decimals, dates, large integers and nonfinite values use explicit strings."
            ),
        },
        description="dbt compilation and run metadata from the actual local project",
    )
    print("dbt model built successfully", flush=True)
    return 0


def main() -> int:
    with plot_artifacts.output_directory(Path.cwd()):
        return _run()


if __name__ == "__main__":
    raise SystemExit(main())
