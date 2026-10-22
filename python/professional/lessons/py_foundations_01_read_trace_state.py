"""python-foundations-01: Read a Program, Trace Its State, and Predict Its Output.

Read ../companion-guides/py_foundations_01_read_trace_state.md before attempting the exercises.
The example runs. Complete the numbered experiments in your own working copy.
Keep solutions separate until you have attempted and checked the contract.
"""

# A worked example: predict both lines before running.
boxes = 2
items_per_box = 3
items = boxes * items_per_box
boxes = 4
print("Stored items:", items)
print("Recalculated items:", boxes * items_per_box)
print("TODO: complete the eight numbered exercises below in your working copy")

# Add your predictions, traces, and runnable attempts below.
# Keep each experiment small and run the file from a fresh process.

# Exercise 1. Trace a reassignment
# Prompt: Trace `apples = 2; pears = apples + 3; apples = 9` as three separate lines. Do not
# run until your trace is complete. State both final values.
# Verify: `apples` equals 9 and `pears` equals 5; the trace records pears being calculated
# before apples changes.

# Exercise 2. Separate calculation from display
# Prompt: Create `boxes = 4`, `items_per_box = 6`, and a calculated `items`. Display a
# human-readable label followed by the value. Repeat with zero boxes.
# Verify: The terminal contains totals 24 and 0 in the two runs; changing the label does not
# change either calculated number.

# Exercise 3. Predict text joining
# Prompt: Predict the output of `"3" + "7"` and of `3 + 7`. Explain how you can prove the
# difference if the output alone is confusing.
# Verify: The first value equals the string `"37"`; the second equals integer 10. Inspection
# reports `str` and `int` respectively.

# Exercise 4. Find the first invalid line
# Prompt: In a fresh script, put `print(balance)` before `balance = 10`. Capture the final
# exception line, then make the smallest ordering change that permits a run.
# Verify: Before repair the exception class is `NameError`; after repair a fresh run prints 10
# exactly once.

# Exercise 5. Test a stale calculation
# Prompt: Calculate `total = 2 * 5`, change the quantity to 3 under a separate name, and
# compare the old total with a new calculation. Do not edit the expected values to hide a
# disagreement.
# Verify: Your trace contains an old total of 10 and a recomputed total of 15, and identifies
# the line that recalculates the result.

# Exercise 6. Distinguish comments from actions
# Prompt: Add a comment that predicts a total of 100 beside code that actually calculates `4 *
# 5`. Run the file, then repair the comment while preserving correct code.
# Verify: The output remains 20 before and after the comment repair; your observation names
# the multiplication as the executed operation.

# Exercise 7. Make a minimal reproduction
# Prompt: Copy just the three statements needed to show that `copied = original` for an
# integer keeps its old value after `original` is reassigned. Use original values 8 and 11.
# Verify: The new script prints original 11 and copied 8, with no dependency on previous
# interactive commands.

# Exercise 8. Transfer the trace to a receipt
# Prompt: Starting with three tickets at seven units each and a two-unit discount on the whole
# order, calculate the payable amount. Then test no tickets and no discount. Use clear names.
# Verify: The normal payable value is 19; the empty-order value is 0. A written trace explains
# why the discount is applied once to the order.
