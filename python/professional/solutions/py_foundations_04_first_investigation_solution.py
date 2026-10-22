"""Small auditable CSV investigation for python-foundations-04."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory

FIXTURE = Path("python") / "professional" / "fixtures" / "data" / "beginner_orders.csv"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["id", "region", "quantity"]:
            raise ValueError("expected header: id,region,quantity")
        rows = list(reader)
    if any(
        set(row) != {"id", "region", "quantity"}
        or any(not isinstance(v, str) for v in row.values())
        for row in rows
    ):
        raise ValueError("CSV row does not match the three-field header")
    return rows


def analyze_rows(rows: list[dict[str, str]]) -> dict[str, object]:
    seen: set[str] = set()
    totals: dict[str, int] = {}
    accepted_count = 0
    rejected: list[dict[str, object]] = []
    for row_number, raw in enumerate(rows, start=1):
        try:
            if not all(
                isinstance(raw.get(key), str) and raw[key].strip()
                for key in ("id", "region", "quantity")
            ):
                raise ValueError("missing or non-text field")
            identifier = raw["id"].strip()
            region = raw["region"].strip()
            try:
                quantity = int(raw["quantity"].strip())
            except ValueError as exc:
                raise ValueError("quantity is not an integer") from exc
            if quantity < 0:
                raise ValueError("quantity is negative")
            if identifier in seen:
                raise ValueError("duplicate id")
            seen.add(identifier)
            accepted_count += 1
            totals[region] = totals.get(region, 0) + quantity
        except ValueError as exc:
            rejected.append({"row_number": row_number, "reason": str(exc), "raw": raw.copy()})
    return {
        "input_count": len(rows),
        "accepted_count": accepted_count,
        "rejected_count": len(rejected),
        "rejected": rejected,
        "total_quantity": sum(totals.values()),
        "by_region": dict(sorted(totals.items())),
        "contract": "nonnegative integer units; case-sensitive id/region; first valid id wins",
    }


def write_report(report: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    result = analyze_rows(load_rows(FIXTURE))
    assert (result["input_count"], result["accepted_count"], result["rejected_count"]) == (7, 4, 3)
    assert result["total_quantity"] == 11
    assert result["by_region"] == {"north": 7, "south": 0, "west": 4}
    with TemporaryDirectory() as directory:
        target = Path(directory) / "report.json"
        write_report(result, target)
        assert json.loads(target.read_text(encoding="utf-8")) == result
    print(json.dumps(result, sort_keys=True))
