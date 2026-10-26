"""Original DAX teaching records. These helpers do not parse or execute DAX."""

from __future__ import annotations

from .progression import PREREQUISITES, STARTERS

STAGES = [
    "Models, grain and a first query",
    "Values, BLANK and reusable measures",
    "Row context, filter context and CALCULATE",
    "Filters, iterators and nonadditive totals",
    "Virtual tables, lineage and relationships",
    "Dates, periods and temporal meaning",
    "Analytical patterns and decision units",
    "Reusable logic and calculation scope",
    "Performance interpretation and equivalent rewrites",
    "Security, delivery and integrated capstones",
]

BASE = (
    "DEFINE\n    MEASURE Sales[NetRevenue] = SUM ( "
    "Sales[NetAmount] )\n    MEASURE Sales[QuantitySold] = SUM "
    "( Sales[Quantity] )\n    MEASURE Sales[GrossRevenue] = "
    "SUMX ( Sales, Sales[Quantity] * Sales[UnitPrice] )\n    "
    "MEASURE Sales[OrderCount] = DISTINCTCOUNT ( "
    "Sales[OrderID] )\n"
)


def result(title, query, columns, rows, context, trace, explanation, *, note=""):
    return {
        "title": title,
        "query": query.strip(),
        "columns": [{"name": name, "type": kind} for name, kind in columns],
        "rows": rows,
        "context": context,
        "trace": trace,
        "explanation": explanation,
        "note": note
        or (
            "Hand-derived for the named reference and fixture. Editing "
            "a draft does not recalculate this table."
        ),
    }


def task(question, hint, answer):
    return {"question": question, "hint": hint, "answer": answer}


def lesson(
    number,
    title,
    concepts,
    outcome,
    mechanism,
    anatomy,
    cases,
    practice,
    *,
    defines=BASE,
    model="retail",
    prerequisites=None,
    starter=None,
    sources=None,
    feature=None,
    artifact_kind="query",
    extra="",
):
    assert 2 <= len(cases) <= 6 and len(practice) == 6
    return {
        "id": f"dax-{number:03d}",
        "number": number,
        "stage": (number - 1) // 6 + 1,
        "title": title,
        "concepts": concepts,
        "outcome": outcome,
        "mechanism": mechanism,
        "anatomy": anatomy,
        "cases": cases,
        "practice": practice,
        "defines": defines,
        "model": model,
        "prerequisites": prerequisites
        if prerequisites is not None
        else [f"dax-{item:03d}" for item in PREREQUISITES[number]],
        "starter": starter if starter is not None else STARTERS[number],
        "sources": sources or [],
        "feature": feature,
        "artifact_kind": artifact_kind,
        "extra": extra,
    }
