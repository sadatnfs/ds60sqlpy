"""Synthetic course fixtures. Generation is deterministic and entirely offline."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import date, timedelta


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def csv_text(headers, rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return stream.getvalue()


def artifacts():
    files = {}
    tables = {}

    def add(name, columns, rows, grain, key, *, folder="retail"):
        path = f"courses/dax/models/{folder}/{name}.csv"
        text = csv_text([c[0] for c in columns], rows)
        files[path] = text
        record = {
            "name": name,
            "path": path,
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
            "grain": grain,
            "key": key,
            "row_count": len(rows),
            "columns": [{"name": n, "type": t} for n, t in columns],
        }
        tables[name] = record
        return record

    add(
        "Product",
        [
            ("ProductKey", "integer"),
            ("Product", "text"),
            ("Category", "text"),
            ("Color", "text"),
            ("UnitCost", "number"),
        ],
        [
            [1, "Notebook", "Paper", "Blue", 2],
            [2, "Pen", "Paper", "Red", 1],
            [3, "Mug", "Home", "Blue", 5],
            [4, "Bag", "Travel", "Green", 10],
        ],
        "one row per product",
        ["ProductKey"],
    )
    add(
        "Customer",
        [("CustomerKey", "integer"), ("Customer", "text"), ("Region", "text"), ("Segment", "text")],
        [
            [10, "Ada", "North", "Retail"],
            [20, "Bo", "South", "Retail"],
            [30, "Cy", "North", "Trade"],
            [40, "Di", "West", "Retail"],
        ],
        "one row per customer",
        ["CustomerKey"],
    )
    sale_columns = [
        ("SaleID", "text"),
        ("OrderID", "integer"),
        ("ProductKey", "integer"),
        ("CustomerKey", "integer"),
        ("OrderDate", "date"),
        ("ShipDate", "date"),
        ("Quantity", "integer"),
        ("UnitPrice", "number"),
        ("Discount", "number"),
        ("NetAmount", "number"),
    ]
    sale_rows = [
        ["S1", 101, 1, 10, "2024-01-02", "2024-01-04", 2, 10, 0, 20],
        ["S2", 101, 2, 10, "2024-01-02", "2024-01-04", 1, 5, 1, 4],
        ["S3", 102, 3, 20, "2024-01-03", "2024-01-05", 2, 20, 0, 40],
        ["S4", 201, 1, 10, "2025-01-02", "2025-01-04", 3, 10, 3, 27],
        ["S5", 202, 2, 30, "2025-01-03", "2025-01-08", 4, 5, 0, 20],
        ["S6", 203, 3, 20, "2025-01-05", "2025-02-01", 1, 20, 0, 20],
        ["S7", 204, 1, 20, "2025-02-02", "2025-02-03", 2, 10, 0, 20],
        ["S8", 205, 3, 30, "2025-02-03", "2025-02-04", 2, 20, 4, 36],
    ]
    add("Sales", sale_columns, sale_rows, "one order line; OrderID can repeat", ["SaleID"])
    days = []
    current = date(2024, 1, 1)
    while current <= date(2025, 12, 31):
        days.append(
            [
                current.isoformat(),
                current.year,
                current.month,
                current.year * 100 + current.month,
                current.strftime("%Y-%m"),
                current.day,
                current.year + (current.month >= 7),
                current.year + (current.month >= 2),
            ]
        )
        current += timedelta(days=1)
    add(
        "Date",
        [
            ("Date", "date"),
            ("Year", "integer"),
            ("MonthNumber", "integer"),
            ("MonthKey", "integer"),
            ("YearMonth", "text"),
            ("DayOfMonth", "integer"),
            ("FiscalYear", "integer"),
            ("RetailYear", "integer"),
        ],
        days,
        "one calendar day, complete 2024 and 2025",
        ["Date"],
    )
    relationships = [
        {
            "from_table": "Product",
            "from_column": "ProductKey",
            "to_table": "Sales",
            "to_column": "ProductKey",
            "cardinality": "one-to-many",
            "filter_direction": "from_to",
            "active": True,
        },
        {
            "from_table": "Customer",
            "from_column": "CustomerKey",
            "to_table": "Sales",
            "to_column": "CustomerKey",
            "cardinality": "one-to-many",
            "filter_direction": "from_to",
            "active": True,
        },
        {
            "from_table": "Date",
            "from_column": "Date",
            "to_table": "Sales",
            "to_column": "OrderDate",
            "cardinality": "one-to-many",
            "filter_direction": "from_to",
            "active": True,
        },
        {
            "from_table": "Date",
            "from_column": "Date",
            "to_table": "Sales",
            "to_column": "ShipDate",
            "cardinality": "one-to-many",
            "filter_direction": "from_to",
            "active": False,
        },
    ]
    core = list(tables.values())
    model = {
        "schema_version": 1,
        "id": "retail",
        "title": "Eight-line retail model",
        "description": (
            "Original synthetic USD sales. NetAmount = Quantity * "
            "UnitPrice - line Discount. No tax or returns are included "
            "in NetAmount."
        ),
        "tables": core,
        "relationships": relationships,
        "observation_end": "2025-02-28",
        "calendar_definitions": [
            {
                "name": "RetailCalendar",
                "table": "Date",
                "status": "offline specification only; calendar-based time intelligence preview",
                "tags": {"Day": "Date", "Year": "RetailYear", "Month": "YearMonth"},
                "year_starts": "February 1",
            }
        ],
        "date_table": {"table": "Date", "column": "Date", "marked": True},
        "assumptions": [
            "Dates have no time component.",
            "All ordinary retail amounts are USD.",
            "The one side is unique; normal foreign keys are complete.",
            (
                "Relationships are regular Import-style relationships for "
                "hand reasoning, not live engine metadata."
            ),
            (
                "The Date table contains 731 dates; guides show relevant "
                "slices rather than hide unselected dates."
            ),
        ],
    }
    files["courses/dax/models/retail/model.json"] = dump(model)
    missing = add(
        "Sales",
        sale_columns,
        sale_rows + [["S9", 206, 999, 10, "2025-02-03", "2025-02-04", 1, 7, 0, 7]],
        "one sales line; S9 has a deliberately unmatched product",
        ["SaleID"],
        folder="unknown-member",
    )
    unknown = {
        **model,
        "id": "unknown-member",
        "title": "Deliberately unmatched product model",
        "tables": [missing if t["name"] == "Sales" else t for t in core],
        "assumptions": model["assumptions"][:2]
        + [
            (
                "S9 ProductKey 999 is deliberately absent from Product. A "
                "regular relationship's synthetic blank member is required "
                "in the reference reasoning."
            )
        ],
    }
    files["courses/dax/models/unknown-member/model.json"] = dump(unknown)
    tables = {t["name"]: t for t in core}
    add(
        "Returns",
        [("ReturnID", "text"), ("SaleID", "text"), ("Refund", "number")],
        [["R1", "S2", 4], ["R2", "S4", 9]],
        "one return event; multiple returns per sale could exist",
        ["ReturnID"],
        folder="analytics",
    )
    add(
        "Budget",
        [("MonthKey", "integer"), ("Category", "text"), ("Amount", "number")],
        [[202501, "Paper", 60], [202501, "Home", 30], [202502, "Paper", 25], [202502, "Home", 50]],
        "one month and category",
        ["MonthKey", "Category"],
        folder="analytics",
    )
    add(
        "Inventory",
        [("SnapshotDate", "date"), ("ProductKey", "integer"), ("Units", "integer")],
        [
            ["2025-01-31", 1, 10],
            ["2025-01-31", 2, 20],
            ["2025-01-31", 3, 5],
            ["2025-02-28", 1, 8],
            ["2025-02-28", 2, 15],
            ["2025-02-28", 3, 7],
        ],
        "one product at an end-of-day snapshot",
        ["SnapshotDate", "ProductKey"],
        folder="analytics",
    )
    add(
        "ForeignSales",
        [
            ("ForeignID", "text"),
            ("SaleDate", "date"),
            ("Currency", "text"),
            ("LocalAmount", "number"),
        ],
        [
            ["F1", "2025-01-02", "USD", 100],
            ["F2", "2025-01-02", "EUR", 100],
            ["F3", "2025-02-03", "EUR", 50],
        ],
        "one foreign-currency transaction",
        ["ForeignID"],
        folder="analytics",
    )
    add(
        "ExchangeRate",
        [("RateDate", "date"), ("Currency", "text"), ("USDPerUnit", "number")],
        [["2025-01-02", "USD", 1], ["2025-01-02", "EUR", 1.1], ["2025-02-03", "EUR", 1.2]],
        "one currency rate per date, expressed as USD per local currency unit",
        ["RateDate", "Currency"],
        folder="analytics",
    )
    add(
        "CohortMember",
        [("MemberKey", "integer"), ("CohortMonth", "integer")],
        [[100, 202501], [200, 202501], [300, 202502], [400, 202502]],
        "one enrolled member",
        ["MemberKey"],
        folder="analytics",
    )
    add(
        "Activity",
        [("ActivityID", "text"), ("MemberKey", "integer"), ("MonthKey", "integer")],
        [["A1", 100, 202501], ["A2", 100, 202502], ["A3", 200, 202501], ["A4", 300, 202502]],
        "one observed member-month activity in this small fixture",
        ["ActivityID"],
        folder="analytics",
    )
    add(
        "Assignments",
        [("UnitID", "text"), ("Arm", "text")],
        [["U1", "Control"], ["U2", "Control"], ["U3", "Treatment"], ["U4", "Treatment"]],
        "one assigned experimental unit",
        ["UnitID"],
        folder="analytics",
    )
    add(
        "Outcomes",
        [("UnitID", "text"), ("Converted", "integer"), ("Revenue", "number")],
        [["U1", 0, 0], ["U2", 1, 20], ["U3", 1, 30], ["U4", 1, 10]],
        "one finalized outcome per assigned unit",
        ["UnitID"],
        folder="analytics",
    )
    add(
        "Exposures",
        [("ExposureID", "text"), ("UnitID", "text")],
        [["E1", "U1"], ["E2", "U2"], ["E3", "U3"], ["E4", "U3"]],
        "one exposure event; repeat events are not independent assigned units",
        ["ExposureID"],
        folder="analytics",
    )
    add(
        "Audience",
        [("GroupKey", "integer"), ("Audience", "text")],
        [[1, "Newsletter"], [2, "Prospects"]],
        "one named customer audience",
        ["GroupKey"],
        folder="analytics",
    )
    add(
        "GroupMembership",
        [("GroupKey", "integer"), ("CustomerKey", "integer")],
        [[1, 10], [1, 20], [2, 20], [2, 30]],
        "one customer membership in one audience",
        ["GroupKey", "CustomerKey"],
        folder="analytics",
    )
    add(
        "Access",
        [("Principal", "text"), ("Region", "text")],
        [["north.learner@example.test", "North"], ["south.learner@example.test", "South"]],
        "one allowed region per synthetic principal in this tiny fixture",
        ["Principal", "Region"],
        folder="analytics",
    )
    add(
        "ExperimentSummary",
        [
            ("Arm", "text"),
            ("Assigned", "integer"),
            ("Converted", "integer"),
            ("Rate", "number"),
            ("WilsonLower", "number"),
            ("WilsonUpper", "number"),
        ],
        [
            ["Control", 2, 1, 0.5, 0.09453120573423074, 0.9054687942657693],
            ["Treatment", 2, 2, 1, 0.34238022750665303, 1],
        ],
        (
            "one supplied statistical summary per experimental arm; "
            "marginal95percent Wilson score intervals"
        ),
        ["Arm"],
        folder="analytics",
    )
    extra = [
        {
            "from_table": "Sales",
            "from_column": "SaleID",
            "to_table": "Returns",
            "to_column": "SaleID",
            "cardinality": "one-to-many",
            "filter_direction": "from_to",
            "active": True,
        },
        {
            "from_table": "Product",
            "from_column": "ProductKey",
            "to_table": "Inventory",
            "to_column": "ProductKey",
            "cardinality": "one-to-many",
            "filter_direction": "from_to",
            "active": True,
        },
        {
            "from_table": "Date",
            "from_column": "Date",
            "to_table": "Inventory",
            "to_column": "SnapshotDate",
            "cardinality": "one-to-many",
            "filter_direction": "from_to",
            "active": True,
        },
        {
            "from_table": "CohortMember",
            "from_column": "MemberKey",
            "to_table": "Activity",
            "to_column": "MemberKey",
            "cardinality": "one-to-many",
            "filter_direction": "from_to",
            "active": True,
        },
        {
            "from_table": "Assignments",
            "from_column": "UnitID",
            "to_table": "Outcomes",
            "to_column": "UnitID",
            "cardinality": "one-to-many",
            "filter_direction": "from_to",
            "active": True,
        },
        {
            "from_table": "Assignments",
            "from_column": "UnitID",
            "to_table": "Exposures",
            "to_column": "UnitID",
            "cardinality": "one-to-many",
            "filter_direction": "from_to",
            "active": True,
        },
    ]
    extra += [
        {
            "from_table": "Audience",
            "from_column": "GroupKey",
            "to_table": "GroupMembership",
            "to_column": "GroupKey",
            "cardinality": "one-to-many",
            "filter_direction": "from_to",
            "active": True,
        },
        {
            "from_table": "Customer",
            "from_column": "CustomerKey",
            "to_table": "GroupMembership",
            "to_column": "CustomerKey",
            "cardinality": "one-to-many",
            "filter_direction": "from_to",
            "active": True,
        },
    ]
    analytics = {
        **model,
        "id": "analytics",
        "title": "Retail and analytical extensions",
        "tables": list(tables.values()),
        "relationships": relationships + extra,
        "assumptions": model["assumptions"]
        + [
            (
                "Budget, ForeignSales and ExchangeRate are disconnected; "
                "formulas explicitly transfer keys or look up a unique "
                "rate."
            ),
            (
                "Cohorts and experiments are independent synthetic "
                "populations, not renamed retail customers."
            ),
            (
                "Outcome data are complete for all four assignments; "
                "exposure is a separate event stream."
            ),
        ],
    }
    analytics["security_specification"] = {
        "status": "offline policy specification, not installed or tested security",
        "scope": "regular Import-style model; role-restricted Viewer context",
        "static_roles": {
            "NorthViewer": 'Customer[Region] = "North"',
            "SouthViewer": 'Customer[Region] = "South"',
        },
        "dynamic_customer_rule": (
            "Customer[Region] IN SELECTCOLUMNS(FILTER(Access, "
            "Access[Principal] = USERPRINCIPALNAME()), "
            '"AllowedRegion", Access[Region])'
        ),
        "unknown_principal": "no allowed Customer rows",
        "limits": [
            "Ordinary report filters are not security enforcement.",
            ("Workspace Admin/Member/Contributor behavior must not be inferred from Viewer tests."),
            ("The Access mapping itself requires appropriate visibility controls in a real model."),
        ],
    }
    files["courses/dax/models/analytics/model.json"] = dump(analytics)
    return files
