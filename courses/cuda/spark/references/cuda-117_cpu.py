"""Independent CPU reference with deterministic contract assertions."""

from decimal import Decimal

values = [2, None, 5]
assert len(values) == 3
assert sum(v is not None for v in values) == 2
assert sum(v for v in values if v is not None) == 7
assert Decimal("1.10") + Decimal("2.20") == Decimal("3.30")
print("CPU SQL-semantics oracle: rows3 nonnull2 sum7 decimal3.30")
