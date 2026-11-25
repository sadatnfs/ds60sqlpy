# web-034: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-034.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Trace the accumulator after each iteration.

**Expected answer:** It progresses through 20, 50 and 65.

**Approach:** Write a row per iteration with the current value and the running total, adding each element to the previous total.

**Why:** The accumulator adds each element in turn, so it holds 20, 50 and then 65.

**Plausible wrong approach:** Writing only the final total fails because a wrong intermediate step, such as starting at 20 instead of 0, is then invisible.

**How to verify:** Echoing `$total` inside the loop prints 20, 50 and 65 on three lines.

## Exercise 2: Add a guard against negative durations.

**Expected evidence:** Invalid values fail before they enter the total.

**Approach:** Inside the loop, check `$minutes < 0` before adding and throw an exception that names the offending value.

**Why:** Validating inside the loop stops one bad value from silently corrupting the total.

**Plausible wrong approach:** Using `continue` to skip negatives fails because the total then looks valid while silently hiding a data problem.

**How to verify:** An input of [20, -5] stops with the error message, and no total is printed for it. An input of [20, 30] still prints 50, so the guard rejects only invalid values.

## Exercise 3: Build a bounded weekly-duration summary with a route label.

**Expected evidence:** The total and label follow the declared cases and terminate predictably.

**Approach:** Sum validated durations with `foreach`, then map the level to a label with `match`, adding a default arm only if unknown levels are allowed.

**Why:** foreach always terminates over a finite array, and match maps each declared case to one label.

**Plausible wrong approach:** Using `while (true)` with a manual break fails because a missing exit condition makes the worker run until its time limit.

**How to verify:** The summary prints the expected total and label for each level, and an unknown level follows the declared rule.

## Exercise 4: Diagnose a while loop whose condition never changes.

**Expected answer:** Identify the missing progress step and replace it with a bounded iteration where possible.

**Approach:** Find the variable in the `while` condition and look for the statement that should change it on each pass.

**Why:** A loop whose condition never changes never ends; foreach or a counter with a fixed bound guarantees progress.

**Plausible wrong approach:** Adding a counter that breaks after 1000 passes fails because it hides the missing update and returns a wrong partial result.

**How to verify:** After adding the update, the loop runs exactly as many times as the input requires and then stops. Adding an echo of the loop variable shows it changing on every pass until the condition becomes false.

## Exercise 5: Test an empty collection.

**Expected evidence:** The total is zero without a special invalid array access.

**Approach:** Run the summary with `[]` and confirm the loop body never executes while the total stays at its starting value of 0.

**Why:** foreach over an empty array runs zero times, so the total keeps its initial value of 0.

**Plausible wrong approach:** Reading `$durations[0]` before the loop fails because an empty array has no first element and PHP emits a warning.

**How to verify:** The program prints a total of 0 for an empty list and emits no warnings.

## Exercise 6: Explain match versus switch for a typed mapping.

**Expected answer:** Match returns a value and compares strictly; switch has different comparison and fall-through rules.

**Approach:** Compare the two forms on '0' and on false: `match` uses identity and returns a value, while `switch` compares loosely and can fall through.

**Why:** match compares with === and throws UnhandledMatchError for an unmatched value, while switch compares loosely and falls through without break.

**Plausible wrong approach:** Treating them as interchangeable fails because `switch` matches '0' against `case false`, while `match` does not.

**How to verify:** Running the contrast case prints switch: false branch and match: string arm. Removing the string arm makes the `match` call throw an UnhandledMatchError for '0'.

## Reference comparison

The reference requires the accumulated total to equal 65 and prints the label with the minutes. That catches an accumulator reset inside the loop or a skipped element. It does not test the negative guard, the empty week or the unknown-label path, so run each of those inputs yourself.

Open `courses/web-development/solutions/web-034_solution.php` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
