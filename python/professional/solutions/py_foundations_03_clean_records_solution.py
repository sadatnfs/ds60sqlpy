"""Non-mutating text-record boundaries for python-foundations-03."""

from __future__ import annotations


def parse_quantity(raw: object) -> int:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("quantity is missing or not text")
    try:
        quantity = int(raw.strip())
    except ValueError as exc:
        raise ValueError("quantity is not an integer") from exc
    if quantity < 0:
        raise ValueError("quantity is negative")
    return quantity


def normalize_record(raw: dict[str, object]) -> dict[str, object]:
    identifier = raw.get("id")
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("id is missing or not text")
    return {"id": identifier.strip(), "quantity": parse_quantity(raw.get("quantity"))}


def clean_rows(
    rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    accepted: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    seen: set[str] = set()
    for row_number, raw in enumerate(rows, start=1):
        try:
            cleaned = normalize_record(raw)
            identifier = str(cleaned["id"])
            if identifier in seen:
                raise ValueError("duplicate id")
            seen.add(identifier)
            accepted.append(cleaned)
        except ValueError as exc:
            rejected.append({"row_number": row_number, "reason": str(exc), "raw": raw.copy()})
    assert len(rows) == len(accepted) + len(rejected)
    return accepted, rejected


if __name__ == "__main__":
    sample: list[dict[str, object]] = [
        {"id": "A", "quantity": "many"},
        {"id": " A ", "quantity": "2"},
        {"id": "A", "quantity": "3"},
        {"id": "B", "quantity": "0"},
    ]
    accepted, rejected = clean_rows(sample)
    assert accepted == [{"id": "A", "quantity": 2}, {"id": "B", "quantity": 0}]
    assert [r["row_number"] for r in rejected] == [1, 3]
    assert sample[1]["id"] == " A "
    print({"accepted": accepted, "rejected": rejected})
