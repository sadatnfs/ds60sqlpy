"""python-foundations-03: Turn Messy Text into Trustworthy Records.

Read ../companion-guides/py_foundations_03_clean_records.md before attempting the exercises.
The example runs; unfinished exercise functions raise NotImplementedError.
Keep solutions separate until you have attempted and checked the contract.
"""

from __future__ import annotations


def parse_quantity(raw: object) -> int:
    """TODO: accept nonnegative integer text; reject missing or invalid values."""
    raise NotImplementedError("complete parse_quantity")


def normalize_record(raw: dict[str, object]) -> dict[str, object]:
    """TODO: return a new canonical id/quantity record; do not mutate raw."""
    raise NotImplementedError("complete normalize_record")


def clean_rows(
    rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """TODO: retain source order and report rejected row number/reason/raw data."""
    raise NotImplementedError("complete clean_rows")


if __name__ == "__main__":
    raw_example = {"id": " A ", "quantity": "2"}
    worked_copy = {"id": raw_example["id"].strip(), "quantity": int(raw_example["quantity"])}
    print("Worked non-mutating normalization:", raw_example, worked_copy)
    print("TODO: complete three functions and eight exercises")

# Exercise 1. Define the policy before coding
# Prompt: Write a five-row policy table for `"0"`, `""`, `" 4 "`, `"4.5"`, and `"-1"`. For
# each, state accepted integer or rejection reason. Implement `parse_quantity`.
# Verify: Accepted results are 0 and 4. The other three inputs raise ValueError, with missing,
# non-integer, and negative reasons respectively.

# Exercise 2. Keep raw records unchanged
# Prompt: Implement `normalize_record` for string id and quantity fields. Given `{"id": " A ",
# "quantity": "2"}`, return canonical fields without mutating the input.
# Verify: The result equals `{"id": "A", "quantity": 2}` while the original id still contains
# both surrounding spaces.

# Exercise 3. Make missing identity visible
# Prompt: Test an absent id, an empty id, and an all-space id. Decide whether `"A"` and `"a"`
# collide under the declared case-sensitive policy.
# Verify: Tests capture ValueError for each missing identity and assert that normalized ids `A`
# and `a` remain unequal strings.

# Exercise 4. Account for every row
# Prompt: Implement `clean_rows` returning accepted and rejected lists. Feed ids A, B, C with
# quantities 2, many, and 0.
# Verify: Three inputs produce two accepted records with total quantity 2 and one rejection at
# one-based row 2; count reconciliation equals 3.

# Exercise 5. Enforce first valid wins
# Prompt: Feed A/many, A/2, and A/3 in that order. Add duplicate detection after validation
# and preserve rejection evidence.
# Verify: Only A/2 is accepted; rows 1 and 3 are rejected for non-integer quantity and duplicate
# id. The first invalid row does not reserve A.

# Exercise 6. Reject wrong field types
# Prompt: Test `{"id": "A", "quantity": None}` and `{"id": 3, "quantity": "2"}`. Avoid
# converting arbitrary objects with `str`.
# Verify: Both records appear in rejected output with ValueError-derived reasons, and neither
# becomes an accepted zero or identifier `"3"`.

# Exercise 7. Check empty and all-invalid batches
# Prompt: Run `clean_rows` with no rows, then with two invalid quantity rows. Summarize
# accepted quantities with an explicit zero start.
# Verify: The empty batch returns two empty lists and total 0. The invalid batch has accepted
# count 0, rejected count 2, and total 0.

# Exercise 8. Transfer to stock adjustments
# Prompt: Describe a second contract where negative counts represent returns. Keep the
# original parser unchanged and write boundary cases for a separate signed parser.
# Verify: Your policy note records signed-parser output -1, the original parser's ValueError for
# the same text, and rejection tests for empty and decimal text in both contracts.
