# web-034: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-034.md`.

## Exercise 1: Trace the accumulator after each iteration.

**Expected answer:** It progresses through 20, 50 and 65.

**Why:** The accumulator adds each element in turn, so it holds 20, 50 and then 65.

## Exercise 2: Add a guard against negative durations.

**Expected evidence:** Invalid values fail before they enter the total.

**Why:** Validating inside the loop stops one bad value from silently corrupting the total.

## Exercise 3: Build a bounded weekly-duration summary with a route label.

**Expected evidence:** The total and label follow the declared cases and terminate predictably.

**Why:** foreach always terminates over a finite array, and match maps each declared case to one label.

## Exercise 4: Diagnose a while loop whose condition never changes.

**Expected answer:** Identify the missing progress step and replace it with a bounded iteration where possible.

**Why:** A loop whose condition never changes never ends; foreach or a counter with a fixed bound guarantees progress.

## Exercise 5: Test an empty collection.

**Expected evidence:** The total is zero without a special invalid array access.

**Why:** foreach over an empty array runs zero times, so the total keeps its initial value of 0.

## Exercise 6: Explain match versus switch for a typed mapping.

**Expected answer:** Match returns a value and compares strictly; switch has different comparison and fall-through rules.

**Why:** match compares with === and throws UnhandledMatchError for an unmatched value, while switch compares loosely and falls through without break.

## Reference comparison

Open `courses/web-development/solutions/web-034_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
