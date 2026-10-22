"""python-data-02: Exact Values, Unicode Identity, and Calendar Boundaries.

Read ../companion-guides/py_data_02_exact_values_time_text.md before attempting the exercises.
The example runs; unfinished exercise functions raise NotImplementedError.
Keep solutions separate until you have attempted and checked the contract.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal


def parse_money(raw: object) -> Decimal:
    """TODO: bounded nonnegative ASCII decimal text, at most two fractional digits."""
    raise NotImplementedError("complete parse_money")


def canonical_label(raw: str) -> str:
    """TODO: trim, NFC, casefold, NFC; reject empty labels."""
    raise NotImplementedError("complete canonical_label")


def collision_groups(labels: list[str]) -> dict[str, list[str]]:
    """TODO: report canonical keys with multiple distinct raw spellings."""
    raise NotImplementedError("complete collision_groups")


def parse_instant(raw: str) -> datetime:
    """TODO: parse an offset-aware ISO timestamp and return UTC."""
    raise NotImplementedError("complete parse_instant")


def in_window(instant: datetime, start: datetime, end: datetime) -> bool:
    """TODO: validate aware instants and a positive half-open interval."""
    raise NotImplementedError("complete in_window")


def window_total(
    records: list[dict[str, str]], start: datetime, end: datetime
) -> tuple[int, Decimal]:
    """TODO: validate every source record, then sum selected exact cents."""
    raise NotImplementedError("complete window_total")


if __name__ == "__main__":
    print("Worked exact total:", Decimal("0.10") + Decimal("0.20"))
    print(
        "Worked UTC conversion:",
        datetime.fromisoformat("2026-01-02T00:30:00+02:00").astimezone(UTC),
    )
    print("TODO: complete six boundaries and eight exercises")

# Exercise 1. Parse exact cents
# Prompt: Implement `parse_money`. Accept `" 12.3 "` as Decimal 12.30 and zero as Decimal
# 0.00. Preserve the two-decimal exponent.
# Verify: The accepted values have exponent -2 and integer-cent values 1230 and 0; `"0.10"` plus
# `"0.20"` totals exactly 0.30.

# Exercise 2. Reject ambiguous numeric forms
# Prompt: Probe `"1.005"`, `"NaN"`, `"Infinity"`, `"1e2"`, `"-1"`, an empty string, a float,
# and a thirteen-digit integer string.
# Verify: Every probe raises ValueError. A two-digit fractional amount `"1.00"` still succeeds,
# showing the check is not blanket rejection.

# Exercise 3. Expose Unicode collisions
# Prompt: Implement `canonical_label` using trim, NFC, casefold, then NFC. Implement
# collision_groups that retains distinct raw spellings for shared canonical values.
# Verify: Assert equal canonical values for `"Café"` and `"Cafe\u0301"`; collision output maps
# `strasse` to two raw spellings. Identical repeated raw text produces an empty collision
# mapping.

# Exercise 4. Parse and convert an instant
# Prompt: Implement `parse_instant` to require an aware parsed timestamp and return UTC.
# Compare `2026-01-02T00:30:00+02:00` with its UTC equivalent.
# Verify: Both representations produce equal datetimes at 2026-01-01 22:30 UTC; a timestamp
# without any offset raises ValueError.

# Exercise 5. Own an exact boundary once
# Prompt: Implement a window membership function that requires aware ordered bounds. Test
# start, one middle instant, end, and an empty or reversed window.
# Verify: Membership assertions return True for start/middle and False for end; tests capture
# ValueError for nonpositive windows. Adjacent-window boundary membership sums to exactly 1.

# Exercise 6. Reconcile a window total
# Prompt: Implement `window_total` over records with amount and occurred_at text. Include two
# in-window values 0.10 and 0.20 and an exact-end value 9.00.
# Verify: The result is count 2 and Decimal total 0.30; an independent integer sum gives 30
# cents. The 9.00 record is excluded.

# Exercise 7. Prevent filter-hidden invalid data
# Prompt: Add an out-of-window record with amount `"bad"`. Explain whether filtering is
# permitted to conceal the malformed source value.
# Verify: A test captures ValueError for the bad amount and confirms that no total is returned,
# even with the malformed record outside the selected window.

# Exercise 8. Transfer to local-day reporting
# Prompt: Write a policy note for a source that asks for a city-local business day instead of
# a UTC day. State what additional metadata and tests are needed without inventing a zone
# conversion.
# Verify: The note requires a named zone and rules/version, tests a seasonal offset change and
# ambiguous local time, and distinguishes a local day from a fixed 24-hour UTC window.
