"""Offline DAX contracts and independent fixture arithmetic, not DAX execution."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, cast

import pytest

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "courses/dax"
AUTHORING = COURSE / "authoring"
spec = importlib.util.spec_from_file_location("dax_authoring_build", AUTHORING / "build.py")
assert spec and spec.loader
build = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(AUTHORING))
spec.loader.exec_module(build)
LESSONS = build.all_lessons()
RECORDS = json.loads((COURSE / "reference-results.json").read_text())["lessons"]


def table(name: str, model: str = "retail") -> list[dict[str, Any]]:
    model_spec = json.loads((COURSE / "models" / model / "model.json").read_text())
    meta = next(t for t in model_spec["tables"] if t["name"] == name)
    with (ROOT / meta["path"]).open(newline="") as stream:
        rows: list[dict[str, Any]] = list(csv.DictReader(stream))
    for row in rows:
        for col in meta["columns"]:
            if col["type"] == "integer":
                row[col["name"]] = int(row[col["name"]])
            elif col["type"] == "number":
                row[col["name"]] = float(row[col["name"]])
    return rows


def rows(number: int, case: int = 0) -> list[list[Any]]:
    return cast(list[list[Any]], RECORDS[number - 1]["cases"][case]["rows"])


def test_complete_route_and_direct_prerequisites() -> None:
    assert [s["id"] for s in LESSONS] == [f"dax-{n:03}" for n in range(1, 61)]
    assert {s["stage"] for s in LESSONS} == set(range(1, 11))
    known: set[str] = set()
    for s in LESSONS:
        assert set(s["prerequisites"]) <= known
        assert len(s["prerequisites"]) == len(set(s["prerequisites"]))
        assert 2 <= len(s["cases"]) <= 6
        assert len(s["practice"]) == 6
        assert len({p["question"] for p in s["practice"]}) == 6
        assert all(p["hint"] and p["answer"] for p in s["practice"])
        assert s["sources"] and all(u.startswith("https://") for u in s["sources"])
        known.add(s["id"])
    assert LESSONS[54]["prerequisites"] == ["dax-004", "dax-031", "dax-052"]
    assert len({s["starter"] for s in LESSONS}) == 60
    admission = json.loads((COURSE / "lessons.json").read_text())
    assert len(admission["lessons"]) == 60
    for lesson in admission["lessons"]:
        assert lesson["runtime_profile"] == "dax-offline"
        assert lesson["language"] == "dax"
        assert lesson["verification_id"] is None


@pytest.mark.parametrize("record", RECORDS, ids=lambda x: x["lesson_id"])
def test_bounded_source_bound_hand_derivations(record: dict[str, Any]) -> None:
    for prefix in ["reference", "model"]:
        path = record[f"{prefix}_path"]
        assert path.startswith("courses/dax/") and ".." not in Path(path).parts
        expected = record["source_sha256" if prefix == "reference" else "model_sha256"]
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    assert record["evidence"] == "hand-derived"
    assert 2 <= len(record["cases"]) <= 6
    for case in record["cases"]:
        assert case["id"].startswith(record["lesson_id"] + "-")
        assert case["context"] and case["note"] and len(case["trace"]) >= 3
        assert 1 <= len(case["columns"]) <= 12
        assert len(case["rows"]) <= 100
        assert len({c["name"] for c in case["columns"]}) == len(case["columns"])
        for row in case["rows"]:
            assert len(row) == len(case["columns"])
            for value, column in zip(row, case["columns"], strict=True):
                kind = column["type"]
                assert kind in {"number", "integer", "text", "boolean", "date"}
                if value is None:
                    continue
                if kind in {"number", "integer"}:
                    assert type(value) in {int, float} and math.isfinite(value)
                    if kind == "integer":
                        assert type(value) is int
                elif kind == "boolean":
                    assert type(value) is bool
                elif kind == "date":
                    assert date.fromisoformat(value).isoformat() == value
                else:
                    assert isinstance(value, str)


@pytest.mark.parametrize("model_id", ["retail", "unknown-member", "analytics"])
def test_model_bytes_keys_and_declared_relationships(model_id: str) -> None:
    model = json.loads((COURSE / "models" / model_id / "model.json").read_text())
    tables = {}
    for meta in model["tables"]:
        content = (ROOT / meta["path"]).read_bytes()
        assert hashlib.sha256(content).hexdigest() == meta["sha256"]
        records = table(meta["name"], model_id)
        assert len(records) == meta["row_count"]
        assert len({tuple(r[k] for k in meta["key"]) for r in records}) == len(records)
        assert list(records[0]) == [c["name"] for c in meta["columns"]]
        tables[meta["name"]] = records
    for relation in model["relationships"]:
        one = {r[relation["from_column"]] for r in tables[relation["from_table"]]}
        many = {r[relation["to_column"]] for r in tables[relation["to_table"]]}
        unmatched = many - one
        expected = (
            {999} if model_id == "unknown-member" and relation["from_table"] == "Product" else set()
        )
        assert unmatched == expected
        assert relation["filter_direction"] == "from_to"
    days = [date.fromisoformat(r["Date"]) for r in tables["Date"]]
    assert days == [date(2024, 1, 1) + timedelta(days=i) for i in range(731)]


def test_retail_arithmetic_and_filter_populations() -> None:
    sales = table("Sales")
    products = {r["ProductKey"]: r for r in table("Product")}
    customers = {r["CustomerKey"]: r for r in table("Customer")}
    total = sum(s["NetAmount"] for s in sales)
    assert total == 187 == rows(1)[0][0]
    assert all(s["Quantity"] * s["UnitPrice"] - s["Discount"] == s["NetAmount"] for s in sales)
    assert rows(2)[0] == [len(sales), len({s["OrderID"] for s in sales}), total]
    paper = [s for s in sales if products[s["ProductKey"]]["Category"] == "Paper"]
    north = [s for s in sales if customers[s["CustomerKey"]]["Region"] == "North"]
    blue = [s for s in sales if products[s["ProductKey"]]["Color"] == "Blue"]
    assert rows(3)[0][0] == sum(s["NetAmount"] for s in paper) == 91
    assert rows(3, 1)[0][0] == sum(s["NetAmount"] for s in paper if s in north) == 71
    assert sum(s["NetAmount"] for s in blue) == 163
    assert rows(11)[0] == [total, sum(s["Quantity"] for s in sales), 11]
    assert rows(21)[0] == [sum(s["Quantity"] * s["UnitPrice"] for s in sales), total]
    cost = sum(s["Quantity"] * products[s["ProductKey"]]["UnitCost"] for s in sales)
    assert rows(43)[0] == [total, cost, total - cost, (total - cost) / total]
    for region, expected in [("North", rows(60)[0]), ("South", rows(60, 1)[0])]:
        selected = [s for s in sales if customers[s["CustomerKey"]]["Region"] == region]
        revenue = sum(s["NetAmount"] for s in selected)
        amount = sum(s["Quantity"] * products[s["ProductKey"]]["UnitCost"] for s in selected)
        assert expected == [revenue, amount, amount, revenue]


def test_unknown_member_and_context_specific_blank_are_explicit() -> None:
    sales = table("Sales", "unknown-member")
    known = {r["ProductKey"] for r in table("Product")}
    assert rows(25)[0] == [len(known) + 1, len(known)]
    assert rows(25, 1)[0] == [
        sum(s["NetAmount"] for s in sales if s["ProductKey"] not in known),
        sum(s["NetAmount"] for s in sales),
    ]
    assert rows(8, 1)[0] == [1, None, None, 0]
    assert rows(57, 1)[0] == [None, None, False]
    assert "not tests of real RLS enforcement" in LESSONS[55]["feature"]


def test_date_roles_windows_and_inventory() -> None:
    sales = table("Sales")
    for month, case in [("2025-01", 0), ("2025-02", 1)]:
        assert rows(29, case)[0] == [
            sum(s["NetAmount"] for s in sales if s["OrderDate"].startswith(month)),
            sum(s["NetAmount"] for s in sales if s["ShipDate"].startswith(month)),
        ]
    rolling = [s for s in sales if "2025-02-01" <= s["OrderDate"] <= "2025-02-03"]
    amount = sum(s["NetAmount"] for s in rolling)
    assert rows(34)[0] == [3, amount, amount / 3]
    assert rows(34, 1)[0] == [amount / len({s["OrderDate"] for s in rolling}), amount / 3]
    assert rows(38, 2) == [[sales[0]["SaleID"], sales[0]["NetAmount"]]]
    assert rows(38, 3) == [[sales[2]["SaleID"]]]
    inventory = table("Inventory", "analytics")
    closing = max(r["SnapshotDate"] for r in inventory)
    assert rows(39)[0] == [
        sum(r["Units"] for r in inventory),
        sum(r["Units"] for r in inventory if r["SnapshotDate"] == closing),
    ]
    assert rows(39, 1)[0][0] == sum(
        r["Units"]
        for r in inventory
        if r["SnapshotDate"] == "2025-01-31" and r["ProductKey"] in {1, 3}
    )


def test_cohorts_budget_currency_and_returns() -> None:
    members = table("CohortMember", "analytics")
    activities = table("Activity", "analytics")
    for month, case in [(202501, 0), (202502, 1)]:
        eligible = {r["MemberKey"] for r in members if r["CohortMonth"] == month}
        active = {r["MemberKey"] for r in activities if r["MonthKey"] == month} & eligible
        assert rows(40, case)[0][:2] == [len(eligible), len(active)]
    sales = table("Sales")
    paper = {r["ProductKey"] for r in table("Product") if r["Category"] == "Paper"}
    actual = sum(
        r["NetAmount"]
        for r in sales
        if r["OrderDate"].startswith("2025-01") and r["ProductKey"] in paper
    )
    budget = next(
        r["Amount"]
        for r in table("Budget", "analytics")
        if r["MonthKey"] == 202501 and r["Category"] == "Paper"
    )
    assert rows(41)[0] == [actual, budget, actual - budget]
    rates = {
        (r["RateDate"], r["Currency"]): r["USDPerUnit"] for r in table("ExchangeRate", "analytics")
    }
    converted = sum(
        r["LocalAmount"] * rates[r["SaleDate"], r["Currency"]]
        for r in table("ForeignSales", "analytics")
    )
    assert converted == pytest.approx(rows(42)[0][0])
    assert rows(58)[0] == [
        187,
        sum(r["Refund"] for r in table("Returns", "analytics")),
        174,
        converted,
    ]


def test_experimental_units_and_supplied_wilson_intervals() -> None:
    assignments = table("Assignments", "analytics")
    outcomes = {r["UnitID"]: r for r in table("Outcomes", "analytics")}
    exposures = table("Exposures", "analytics")
    for arm, expected, interval in zip(
        ["Control", "Treatment"], rows(59), rows(59, 1), strict=True
    ):
        units = {r["UnitID"] for r in assignments if r["Arm"] == arm}
        events = [r for r in exposures if r["UnitID"] in units]
        k, n = sum(outcomes[u]["Converted"] for u in units), len(units)
        assert expected == [arm, n, k, len({r["UnitID"] for r in events}), len(events), k / n]
        p, z = k / n, 1.959963984540054
        center = (p + z * z / (2 * n)) / (1 + z * z / n)
        half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        assert interval[1:] == pytest.approx([p, max(0, center - half), min(1, center + half)])


def test_owned_generation_drift_and_literal_safety() -> None:
    for path, expected in build.artifacts().items():
        assert (ROOT / path).read_text() == expected, path
        assert "\u2014" not in expected
        assert "PROTECTEDTOKEN" not in expected
        assert not any(ord(c) < 32 and c not in "\n\t\r" for c in expected), path
    assert "\\frac" in LESSONS[58]["extra"]
    for s in LESSONS:
        reference = build.reference_source(s)
        assert "TODO" not in reference
        assert reference != build.starter_source(s)
        assert "have not been executed" in reference
        assert "Worked tables describe" in build.guide(s)
    assert "synthetic timing data" in RECORDS[52]["cases"][0]["note"]


def test_qualified_reference_names_belong_to_the_named_model() -> None:
    # This checks naming consistency, not DAX grammar or execution semantics.
    pattern = re.compile(r"(?:'([^']+)'|(\b\w+))\[([^\]]+)\]")
    declarations = re.compile(r"MEASURE\s+(?:'([^']+)'|(\w+))\[([^\]]+)\]")
    for record in RECORDS:
        model = json.loads((ROOT / record["model_path"]).read_text())
        columns = {
            table["name"]: {c["name"] for c in table["columns"]} for table in model["tables"]
        }
        source = (ROOT / record["reference_path"]).read_text()
        measures = {
            (quoted or bare, column) for quoted, bare, column in declarations.findall(source)
        }
        for quoted, bare, column in pattern.findall(source):
            name = quoted or bare
            assert column in columns.get(name, set()) or (name, column) in measures, (
                record["lesson_id"],
                name,
                column,
            )
