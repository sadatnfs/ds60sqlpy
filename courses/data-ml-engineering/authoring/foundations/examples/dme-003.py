"""Values have units, missingness policies and explicit time interpretation."""

from datetime import UTC, datetime
from decimal import Decimal


def example_one():
    local = datetime.fromisoformat("2024-01-01T10:00:00+02:00")
    utc = datetime.fromisoformat("2024-01-01T08:00:00+00:00")
    assert local.astimezone(UTC) == utc
    distances = [Decimal("1.20"), Decimal("2.30"), None]
    known = [value for value in distances if value is not None]
    measured = sum(known, Decimal("0"))
    assert measured == Decimal("3.50") and len(known) == 2
    return {
        "same_instant": local == utc,
        "known_kilometers": str(measured),
        "known_rows": len(known),
        "all_rows": len(distances),
        "mean_known_km": str(measured / len(known)),
    }


def example_two():
    naive = datetime.fromisoformat("2024-01-01T10:00:00")
    assert naive.tzinfo is None
    try:
        if naive.tzinfo is None:
            raise ValueError("A producer timezone or UTC offset is required")
    except ValueError:
        rejected_naive = True
    values = [Decimal("1.20"), Decimal("2.30"), None]
    known_mean = sum(value for value in values if value is not None) / 2
    assumed_zero_mean = sum(value if value is not None else Decimal("0") for value in values) / 3
    assert known_mean == Decimal("1.75") and known_mean != assumed_zero_mean
    return {
        "naive_time_rejected": rejected_naive,
        "known_mean_km": str(known_mean),
        "zero_imputed_mean_km": str(assumed_zero_mean),
        "different_denominators": [2, 3],
    }


def main():
    print("Explicit units and clocks:", example_one())
    print("Missing meaning cannot be guessed:", example_two())


if __name__ == "__main__":
    main()
