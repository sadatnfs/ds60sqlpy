"""python-foundations-04: Build Your First Auditable Data Investigation.

Read ../companion-guides/py_foundations_04_first_investigation.md before attempting the exercises.
The example runs; unfinished exercise functions raise NotImplementedError.
Keep solutions separate until you have attempted and checked the contract.
"""

from __future__ import annotations

import csv
from pathlib import Path

FIXTURE = Path("python") / "professional" / "fixtures" / "data" / "beginner_orders.csv"


def load_rows(path: Path) -> list[dict[str, str]]:
    """TODO: validate the exact CSV header and return raw dictionaries."""
    raise NotImplementedError("complete load_rows")


def analyze_rows(rows: list[dict[str, str]]) -> dict[str, object]:
    """TODO: return counts, grouped quantities, total, and rejected evidence."""
    raise NotImplementedError("complete analyze_rows")


def write_report(report: dict[str, object], path: Path) -> None:
    """TODO: save inspectable UTF-8 JSON beneath a chosen learner-local path."""
    raise NotImplementedError("complete write_report")


if __name__ == "__main__":
    with FIXTURE.open(encoding="utf-8", newline="") as handle:
        worked_rows = list(csv.DictReader(handle))
    print("Worked source-row count:", len(worked_rows))
    print("TODO: complete three functions and eight project checkpoints")

# Exercise 1. Write a project charter
# Prompt: Write five sentences naming the regional-units question, tracked input,
# first-valid-id policy, output fields, and a limitation about rejected records.
# Verify: The charter names the three columns and explicitly avoids claiming that accepted units
# equal true demand or that absent regions had zero demand.

# Exercise 2. Load the tracked CSV
# Prompt: Implement `load_rows(path)` using DictReader, UTF-8, and newline handling. Require
# the header sequence id, region, quantity.
# Verify: The tracked file loads seven dictionaries in source order; a header lacking region
# raises ValueError before analysis.

# Exercise 3. Validate and retain rejection evidence
# Prompt: Implement `analyze_rows` with nonempty id/region text, nonnegative integer quantity,
# and first-valid-id wins. Preserve inputs.
# Verify: The fixture has four accepted rows and rejects source rows 4, 5, and 6. Raw records
# remain byte-for-byte equivalent as string values.

# Exercise 4. Aggregate to one result per region
# Prompt: Add by_region and total_quantity to the report. Keep valid zero-quantity regions and
# sort region keys for display.
# Verify: The mapping equals north 7, south 0, west 4; the total is 11. No duplicate record
# contributes three extra units.

# Exercise 5. Add independent checks
# Prompt: Write tests for count reconciliation, sum-of-groups reconciliation, and the tiny
# fixture manual total. Add empty input and one all-invalid batch.
# Verify: The fixture checks are 7 = 4 + 3 and 11 = 7 + 0 + 4; empty input has all counts zero
# and an empty mapping.

# Exercise 6. Write and read a local report
# Prompt: Implement `write_report` to UTF-8 JSON at a supplied learner-local path, then load
# it and compare content with the in-memory report.
# Verify: The JSON round trip preserves counts, grouped totals, and rejected row numbers; no
# tracked source file changes.

# Exercise 7. Challenge the duplicate policy
# Prompt: Analyze two valid rows with the same id but different quantities, then reverse them.
# Explain the effect without claiming a bug in summation.
# Verify: For duplicate id A with quantities 2 then 5, assert total_quantity 2; reversal yields
# 5. Both results report rejected_count 1, proving the order-sensitive policy.

# Exercise 8. Present a reproducible conclusion
# Prompt: Run your own script from a new process, record its command and checks, and write a
# short conclusion with result, quality counts, and one unanswered question.
# Verify: The conclusion states 11 accepted units, four accepted rows, three rejected rows, and
# the inability to establish actual demand from this source alone.
