# Read a Program, Trace Its State, and Predict Its Output: solution reasoning

Stable ID: `python-foundations-01`.

Read the [guide](../companion-guides/py_foundations_01_read_trace_state.md) and attempt the [learner artifact](../lessons/py_foundations_01_read_trace_state.py) first. The [executable solution](py_foundations_01_read_trace_state_solution.py) is a comparison implementation. It does not certify your changed program merely because its own demonstration succeeds. Copy the acceptance cases into your attempt, then change one input without changing the intended policy.

The useful result of this lesson is an accurate model of execution order.
Eight correct terminal values without an explanation would miss that goal.
The runnable solution uses straight-line statements so it works before loops
or user-defined functions have been introduced. Its assertions compare actual
values with independent expected numbers. An assertion is a check that raises
an error when its condition is false; the next lessons will explain its full
testing role. Never change a correct expected value simply to silence it.

```python
apples = 2
pears = apples + 3
apples = 9
assert (apples, pears) == (9, 5)
```

## Exercise 1. Trace a reassignment

After the first line, apples refers to 2. The second line reads that 2, adds 3, and binds pears to 5. The final line replaces apples with 9. Pears remains 5 because there is no later assignment to it. A common false trace writes pears as 12 by treating Python as a spreadsheet. Record the values at the time each statement executes. Compare the observed pair `(9, 5)` with your written prediction and explain the first disagreement rather than only copying the final pair.

## Exercise 2. Separate calculation from display

Use meaningful names for both inputs and keep the calculation separate from its presentation. Four boxes with six items each gives 24; zero boxes gives 0 under the same multiplication rule. `print("Items:", items)` combines display arguments without converting the stored number into text. Replacing the label with another phrase cannot affect multiplication. A useful extra probe changes items per box to one. That distinguishes a real input-based formula from accidentally typing the expected result as a constant.

## Exercise 3. Predict text joining

Quotes create the strings "3" and "7". Joining them produces the two-character string "37". The unquoted integers are added to produce 10. Inspecting type names verifies the operation domain independently of how the terminal renders digits. Do not use the visual appearance of a value as proof that it is numeric. Later, explicit conversion will turn suitable digit strings into numbers. For now, preserve the distinction and explain why adding an integer to a string would need a declared conversion decision.

## Exercise 4. Find the first invalid line

A new script has no earlier balance assignment. The first `print(balance)` therefore raises NameError and stops execution before reaching the assignment below it. Move `balance = 10` above the print, then run the saved file again. The output is 10 once. Moving the print is also valid if it preserves the intended order. An interactive session that already contains balance can hide this defect; a fresh process is the important boundary check. Capture the exception class, not a machine-specific absolute filename.

## Exercise 5. Test a stale calculation

The initial multiplication produces 10. Changing a quantity later changes only that name, so the stored total remains 10. A second multiplication using quantity three and unit price five produces 15. The reference explicitly performs that second calculation and verifies both totals. This behavior is useful when preserving an earlier snapshot, but surprising when expecting a live total. The fix is to decide which state you need and calculate at the correct time. Re-running only a display statement cannot recompute an earlier expression.

## Exercise 6. Distinguish comments from actions

The interpreter ignores the comment. It multiplies four by five and displays 20 regardless of whether the nearby comment incorrectly predicts 100. Repair the explanation to match observed behavior without changing a correct formula. Comments help humans and can become stale independently from code. This exercise teaches two kinds of review: running a check proves what the program did on that input, while reading the explanation checks whether the prose accurately describes it. Neither kind of evidence completely replaces the other.

## Exercise 7. Make a minimal reproduction

Assign original to 8, assign copied from original, and then reassign original to 11. Both assignments initially refer to the integer value 8; the final reassignment changes only original. The comparison result is `(11, 8)`. This is about immutable integer values and rebinding names. Do not generalize it into a claim that assignment deeply copies every Python object. Lists and other mutable containers can share state, a separate topic in the data-structure lessons. A minimal reproduction deliberately excludes irrelevant input or display code.

## Exercise 8. Transfer the trace to a receipt

Three tickets at seven units each costs 21. Subtracting the whole-order discount once gives 19. A line-by-line trace should show a subtotal followed by a payable amount, rather than hiding both operations in an unexplained constant. For no tickets and no discount the same arithmetic gives zero. If a future business rule disallows negative totals, that becomes an explicit branch and boundary test. It is not implied here. State the current input assumptions and avoid adding policies that the exercise did not request.

## Compare and transfer

Change the receipt to four tickets at five units with a three-unit order discount. Predict the subtotal 20 and payable amount 17 before running. Explain which earlier values remain unchanged if you later reassign ticket count. If your script and notebook disagree, use a fresh run as evidence and inspect execution history before changing arithmetic.
