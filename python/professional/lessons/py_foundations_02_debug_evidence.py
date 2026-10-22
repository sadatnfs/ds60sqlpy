"""python-foundations-02: Debug from Evidence Instead of Guessing.

Read ../companion-guides/py_foundations_02_debug_evidence.md before attempting the exercises.
The example runs. Complete the numbered experiments in your own working copy.
Keep solutions separate until you have attempted and checked the contract.
"""

# Worked example: exact boundary and direct evidence.
quantity = 0
if quantity > 0:  # noqa: SIM108 - explicit branches are the current learning objective.
    status = "ready"
else:
    status = "empty"
print("Worked status:", status)
assert status == "empty"
print("TODO: investigate the eight cases below in separate saved attempts")

# Place only one deliberate failing experiment in a script at a time.
# Preserve expected and observed values in comments or your investigation log.

# Exercise 1. Classify three failures
# Prompt: Create separate tiny scripts containing a missing closing parenthesis, `1 / 0`, and
# `total = 3 + 4` where the intended rule is multiplication. Classify each before running.
# Verify: Your log records `SyntaxError`, `ZeroDivisionError`, and a normal run with wrong
# value 7 instead of 12, respectively.

# Exercise 2. Inspect the raw input
# Prompt: Inspect `raw = " 08 "` with `repr` and `type`, convert it deliberately, and
# calculate its successor. Then try `"eight"` in a separate run.
# Verify: The valid parsed value is 8 and successor is 9; invalid text raises `ValueError` and
# is not converted to zero.

# Exercise 3. Repair the boundary
# Prompt: A free-shipping rule says orders costing at least 20 qualify. The implementation
# uses `amount > 20`. Predict values 19, 20, and 21, then repair one comparison.
# Verify: A three-row observation table reports False, True, True after the change; the before
# table differs only at 20.

# Exercise 4. Read an exception precisely
# Prompt: Run `int("4.5")` in a fresh file. Capture the exception class and the failing line.
# State whether the input is invalid integer text or a missing package.
# Verify: The recorded class is `ValueError`; no installation command is used, and the report
# identifies the text `"4.5"` as the failing input.

# Exercise 5. Reduce a wrong result
# Prompt: A receipt with price 7, quantity 3, and a whole-order discount 2 uses `price *
# (quantity - discount)`. Strip unrelated output and repair only the arithmetic grouping.
# Verify: The failing result is 7 and repaired result is 19. With discount zero, both formulas
# yield 21, showing why that case alone missed the bug.

# Exercise 6. Keep the failure visible
# Prompt: Write a try/except around `int("unknown")` that records the conversion failure by
# setting a status string. Avoid an empty except block and do not return a fake successful
# amount.
# Verify: The terminal reports status `invalid quantity`; a valid `"4"` reports `accepted` and
# quantity 4.

# Exercise 7. Disprove a hypothesis
# Prompt: Investigate `"2" + "3"` yielding `"23"`. Test the hypothesis that Python added the
# numbers incorrectly by inspecting types and repeating the operation on integers.
# Verify: Your log records string operands and integer result 5 in the control experiment,
# rejecting the arithmetic-bug hypothesis.

# Exercise 8. Write a regression note
# Prompt: Choose the shipping or receipt defect. Save a four-part note containing contract,
# smallest failing input, repaired observation, and one nearby boundary case. Add executable
# checks.
# Verify: The note names concrete input 20 for shipping or (7, 3, 2) for the receipt, and
# assertions fail if you reintroduce the original operator.
