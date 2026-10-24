# Debug from Evidence Instead of Guessing: solution reasoning

Stable ID: `python-foundations-02`.

Read the [guide](../companion-guides/py_foundations_02_debug_evidence.md) and attempt the [learner artifact](../lessons/py_foundations_02_debug_evidence.py) first. The [executable solution](py_foundations_02_debug_evidence_solution.py) is a comparison implementation. It does not certify your changed program merely because its own demonstration succeeds. Copy the acceptance cases into your attempt, then change one input without changing the intended policy.

The reference keeps deliberate errors inside narrow demonstrations or
describes them without crashing the entire module. Your original reproduction
should still preserve the real failure. The central test is whether a check
would detect the old defect. When a test passes both the broken and repaired
program, it may document useful behavior but cannot prove that repair.

```python
amount = 20
qualifies = amount >= 20
assert qualifies is True
```

This assertion checks the exact change point. An amount of 21 would pass both
the original and repaired comparison and therefore provides weaker evidence.

## Exercise 1. Classify three failures

A missing closing parenthesis is a syntax failure: Python cannot finish parsing the statement. Dividing one by zero is a runtime failure, because the expression is grammatical but the operation has no defined numeric result here. Adding three and four is valid and returns seven; it becomes a logic failure only when the independent requirement says to multiply. Preserve the requirement alongside the input so another reader can judge the result. The interpreter cannot infer the business rule from a syntactically valid formula.

## Exercise 2. Inspect the raw input

Inspecting `repr(raw)` reveals the spaces and quotes; inspecting its type reveals str. Integer conversion returns 8, after which adding one gives 9. Leading zero and whitespace do not make this particular representation invalid. Replacing the word eight with zero would erase the distinction between an invalid record and a real quantity of zero. The reference catches ValueError only to demonstrate the rejected case, with a visible failure marker. It does not claim to support words as numeric input or silently expand the accepted language.

## Exercise 3. Repair the boundary

The phrase at least includes equality, so the repaired predicate is amount greater than or equal to twenty. Testing 19, 20, and 21 distinguishes the nonqualifying side, the exact boundary, and the qualifying side. The original operator produces false at twenty and true only above it. The changed observation at exactly twenty is evidence for this repair. Retain that case even if a later application uses much larger typical order amounts. A threshold is a policy, so document the units and meaning of the number.

## Exercise 4. Read an exception precisely

`int("4.5")` raises ValueError because the text is not an integer literal accepted by that conversion. Nothing about the symptom suggests a missing package. Converting first to float and then int would truncate, which is a new policy with possible data loss. Rejecting the value is a valid policy when quantities must be exact integers. Record the exception class and the expression without unnecessary machine-specific path details. That gives another learner enough information to reproduce the failure in a fresh process.

## Exercise 5. Reduce a wrong result

The wrong expression subtracts the order discount from the item count. With three items, a discount of two leaves one item, multiplied by seven for a result of seven. The intended calculation multiplies quantity and unit price first, then subtracts two once, producing nineteen. Both formulas yield twenty-one when the discount is zero. This is a useful example of an apparently sensible test that cannot expose the defect. Keep a nonzero-discount regression case and explain why that condition reaches the policy difference.

## Exercise 6. Keep the failure visible

Use a narrow try around conversion and catch ValueError. Assign or print a clear invalid-quantity status on failure. On successful conversion, use the accepted status and keep the parsed numeric quantity. This separates failure reporting from numeric output. An empty except block leaves the caller unable to distinguish a failure from no work. Catching Exception would also hide unrelated programming mistakes, such as a misspelled name. The reference demonstrates only this conversion boundary and does not pretend to implement a complete interactive input workflow.

## Exercise 7. Disprove a hypothesis

The control experiment compares the same visible digits as strings and as integers. The string operation joins characters and produces "23", while integer addition gives five. The observations reject the hypothesis that Python's integer addition is faulty. A better explanation is that the input values belong to a different type than expected. This style of experiment matters in larger programs too: inspect the boundary where data enters, then test a minimal operation with a controlled value before modifying downstream arithmetic or installing unrelated tools.

## Exercise 8. Write a regression note

The regression note supplies the rule, input, incorrect observation, and corrected observation. For shipping, amount twenty is the essential sentinel. For the receipt, seven times three with discount two is the essential sentinel. Add a nearby normal case to avoid fixing the special input with a constant. Temporarily restoring the old operator should make the sentinel assertion fail. Restore the real repair afterward. That deliberate failure is evidence that the test is sensitive to the original defect, not just evidence that the repaired file can run.

## Compare and transfer

Apply the same method to a temperature alarm that triggers below zero and to one that triggers at or below zero. Both may be legitimate contracts, but they need different expected results at zero. Explain which written requirement you implemented and show the case that would distinguish them. Debugging ends with evidence for a policy, not with the disappearance of red text.
