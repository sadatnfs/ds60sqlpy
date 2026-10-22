"""Explicit money, Unicode, and instant boundaries for python-data-02."""

from __future__ import annotations

import re
import unicodedata
from datetime import UTC, datetime
from decimal import Decimal, localcontext

MONEY = re.compile(r"[0-9]{1,12}(?:\.[0-9]{1,2})?")


def parse_money(raw: object) -> Decimal:
    if not isinstance(raw, str) or MONEY.fullmatch(raw.strip()) is None:
        raise ValueError(
            "expected nonnegative decimal text with at most "
            "12 integer digits and 2 fractional digits"
        )
    with localcontext() as context:
        context.prec = 32
        return Decimal(raw.strip()).quantize(Decimal("0.01"))


def canonical_label(raw: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("label must be nonempty text")
    return unicodedata.normalize("NFC", unicodedata.normalize("NFC", raw.strip()).casefold())


def collision_groups(labels: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for raw in labels:
        group = groups.setdefault(canonical_label(raw), [])
        if raw not in group:
            group.append(raw)
    return {key: values for key, values in groups.items() if len(values) > 1}


def _as_utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("timestamp must have an explicit UTC offset")
    return value.astimezone(UTC)


def parse_instant(raw: str) -> datetime:
    if not isinstance(raw, str):
        raise ValueError("timestamp must be text")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError("invalid ISO timestamp") from exc
    return _as_utc(parsed)


def in_window(instant: datetime, start: datetime, end: datetime) -> bool:
    start, end, instant = _as_utc(start), _as_utc(end), _as_utc(instant)
    if end <= start:
        raise ValueError("window end must follow start")
    return start <= instant < end


def window_total(
    records: list[dict[str, str]], start: datetime, end: datetime
) -> tuple[int, Decimal]:
    # Validate the bounds even when there are no source records.
    in_window(start, start, end)
    parsed = [
        (parse_money(record["amount"]), parse_instant(record["occurred_at"])) for record in records
    ]
    cents = 0
    count = 0
    with localcontext() as context:
        context.prec = 32
        for amount, instant in parsed:
            if in_window(instant, start, end):
                cents += int(amount * 100)
                count += 1
        context.prec = max(32, len(str(abs(cents))) + 4)
        total = Decimal(cents).scaleb(-2).quantize(Decimal("0.01"))
    return count, total


if __name__ == "__main__":
    start = parse_instant("2026-01-01T00:00:00+00:00")
    end = parse_instant("2026-01-02T00:00:00+00:00")
    rows = [
        {"amount": "0.10", "occurred_at": start.isoformat()},
        {"amount": "0.20", "occurred_at": "2026-01-01T12:00:00+00:00"},
        {"amount": "9.00", "occurred_at": end.isoformat()},
    ]
    assert window_total(rows, start, end) == (2, Decimal("0.30"))
    assert canonical_label("Café") == canonical_label("Cafe\u0301")
    print("Exact window total:", window_total(rows, start, end))
    print("Raw collision evidence:", collision_groups(["Straße", "STRASSE"]))
