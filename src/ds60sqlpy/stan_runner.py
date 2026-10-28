"""Run a compiled classroom Stan model with fixed bounded sampling settings."""

from __future__ import annotations

import csv
import math
import subprocess
import sys
from pathlib import Path

from ds60sqlpy import plot_artifacts


def read_draws(path: Path) -> list[dict[str, float]]:
    with path.open(encoding="utf-8") as stream:
        rows = csv.DictReader(line for line in stream if not line.startswith("#"))
        result = [{key: float(value) for key, value in row.items()} for row in rows]
    if len(result) != 100 or any(not math.isfinite(v) for row in result for v in row.values()):
        raise ValueError("Stan did not produce the expected finite sampling draws.")
    return result


def capture_diagnostics(summary: Path, chains: list[list[dict[str, float]]]) -> None:
    from ds60sqlpy.plot_artifacts import publish_artifact, publish_table

    with summary.open(encoding="utf-8") as stream:
        rows = [
            row for row in csv.reader(line for line in stream if not line.startswith("#")) if row
        ]
    if not rows or len(rows[0]) > 12 or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("The summary does not fit the saved diagnostic table contract.")
    columns, values = rows[0], rows[1:]
    selected = [row for row in values if not row[0].endswith("__")][:100]

    def finite_number(value: str) -> float | None:
        number = float(value)
        return number if math.isfinite(number) else None

    table = [[row[0], *[finite_number(value) for value in row[1:]]] for row in selected]
    try:
        publish_table(
            columns,
            table,
            description=(
                "Up to 100 Stan quantity summaries. Undefined diagnostics are Missing; "
                "short chains do not establish convergence."
            ),
        )
    except (OSError, ValueError, TypeError, RecursionError) as error:
        print("Diagnostic table capture warning: " + str(error), file=sys.stderr)
    parameter = next((key for key in chains[0][0] if not key.endswith("__")), None)
    if parameter is None:
        return
    traces = [
        {
            "type": "scatter",
            "mode": "lines",
            "name": f"Chain {index}",
            "x": list(range(1, 101)),
            "y": [row[parameter] for row in draws],
        }
        for index, draws in enumerate(chains, 1)
    ]
    sampled_table = [
        [index, number, draw[parameter]]
        for index, draws in enumerate(chains, 1)
        for number, draw in enumerate(draws, 1)
        if number % 2 == 0
    ]
    try:
        publish_artifact(
            {
                "kind": "plotly",
                "figure": {
                    "data": traces,
                    "layout": {
                        "title": {"text": "Draw trace: " + parameter},
                        "xaxis": {"title": {"text": "Retained draw"}},
                        "yaxis": {"title": {"text": parameter}},
                        "meta": {
                            "description": (
                                "Two short sampling chains. The table lists every second draw; "
                                "the chart and downloadable figure retain all draws. "
                                "Review diagnostics and model assumptions before inference."
                            ),
                            "table": {
                                "columns": ["Chain", "Draw", parameter],
                                "rows": sampled_table,
                            },
                        },
                    },
                },
            }
        )
    except (OSError, ValueError, TypeError, RecursionError) as error:
        print("Diagnostic trace capture warning: " + str(error), file=sys.stderr)


def _run() -> int:
    directory = Path.cwd()
    executable = directory / "main"
    files: list[str] = []
    chains: list[list[dict[str, float]]] = []
    for chain in (1, 2):
        target = directory / f"chain-{chain}.csv"
        command = [
            str(executable),
            "sample",
            "num_warmup=100",
            "num_samples=100",
            "adapt",
            "delta=0.9",
            "random",
            f"seed={20261027 + chain}",
            f"id={chain}",
            "output",
            f"file={target}",
            "refresh=0",
        ]
        result = subprocess.run(command, check=False)
        if result.returncode:
            return result.returncode
        draws = read_draws(target)
        chains.append(draws)
        divergences = sum(row.get("divergent__", 0) for row in draws)
        print(
            f"Chain {chain}: {len(draws)} retained draws; divergences={int(divergences)}",
            flush=True,
        )
        files.append(str(target))
    summary = directory / "summary.csv"
    result = subprocess.run(
        ["/opt/cmdstan/bin/stansummary", "--csv_filename", str(summary), *files], check=False
    )
    if result.returncode:
        return result.returncode
    try:
        capture_diagnostics(summary, chains)
    except (OSError, ValueError, TypeError, RecursionError) as error:
        print("Diagnostic capture warning: " + str(error), file=sys.stderr)
    print(
        "Stan sampling completed: 2 chains x 100 draws. "
        "Short chains demonstrate the workflow; review diagnostics before inference.",
        flush=True,
    )
    return 0


def main() -> int:
    with plot_artifacts.output_directory(Path.cwd()):
        return _run()


if __name__ == "__main__":
    raise SystemExit(main())
