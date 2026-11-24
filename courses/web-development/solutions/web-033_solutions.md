# web-033: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-033.md`.

## Exercise 1: Predict 125 cents times three units.

**Expected answer:** The result is 375 cents.

**Approach:** Multiply the integer unit price in cents by the integer quantity, which keeps the whole calculation in exact integer arithmetic.

**Why:** 125 × 3 is 375 cents; keeping integer minor units avoids binary floating-point rounding.

**Plausible wrong approach:** Computing 1.25 times 3 as floats and then multiplying by 100 fails because float rounding can produce a value just under 375.

**How to verify:** `var_export($unitCents * $quantity)` prints 375 with no decimal point. Printing `get_debug_type` of the product shows int, confirming no float entered the calculation.

## Exercise 2: Add a fixed 50-cent fee with a named intermediate value.

**Expected evidence:** The new total is 425 cents and the unit remains explicit.

**Approach:** Store the fee in `$feeCents = 50`, add it to the subtotal in a separate named line, and keep every variable name ending in Cents.

**Why:** A named intermediate keeps the unit visible: 375 + 50 = 425 cents.

**Plausible wrong approach:** Adding 0.5 for the fee fails because it mixes dollars and cents and turns the total into a float with the wrong scale.

**How to verify:** The program prints 425 for the total and every intermediate value is an int in `get_debug_type`.

## Exercise 3: Implement a bounded quantity calculation and cents formatter.

**Expected evidence:** Valid quantities produce exact integer totals and two-digit fractional display.

**Approach:** Validate the quantity as an integer within bounds, multiply in cents, then format with `intdiv`, `%` and `str_pad` to two digits.

**Why:** intdiv gives whole units and % gives the remainder, which str_pad formats as two digits.

**Plausible wrong approach:** Formatting with `$total / 100` fails because division produces a float and 305 cents may print as 3.05 or as 3.0499999.

**How to verify:** Totals of 375, 305 and 5 cents format as 3.75, 3.05 and 0.05.

## Exercise 4: Diagnose a concatenation expression that hides arithmetic grouping.

**Expected answer:** Use parentheses or intermediate variables to express the intended computation.

**Approach:** Wrap the arithmetic in parentheses or compute it into a named variable before concatenating it with the label text.

**Why:** Since PHP 8, + and - bind tighter than ., but explicit parentheses or an intermediate variable still make the intended grouping obvious to readers.

**Plausible wrong approach:** Relying on readers to know that `+` binds tighter than `.` in `'Total: ' . $a + $b` fails because the grouping is invisible and differed in PHP 7.

**How to verify:** The repaired line prints Total: followed by the sum, and a reader can see the grouping without operator tables.

## Exercise 5: Reject a negative quantity and test zero.

**Expected evidence:** Invalid negative input is rejected; zero follows the declared contract.

**Approach:** Check `$quantity < 0` before multiplying and throw a clear exception, while letting 0 produce a 0 cent subtotal.

**Why:** A negative quantity has no meaning for a purchase, while zero is a valid empty order unless the contract says otherwise.

**Plausible wrong approach:** Using `abs($quantity)` to fix negatives fails because a refund or a typo is silently turned into a valid purchase.

**How to verify:** Quantity -1 raises the declared error and quantity 0 prints 0.00 as the subtotal. A quantity of 2 still prints 2.50 for a 125 cent unit price.

## Exercise 6: Explain when integer cents are insufficient.

**Expected answer:** Different currency scales, huge ranges, exchange rates or fractional-unit pricing require an explicit broader numeric policy.

**Approach:** Name the cases integers cannot cover alone: three decimal currencies, exchange rates, very large totals and prices below one cent.

**Why:** Currencies with three decimal places, exchange rates and fractional unit prices need an explicit scale or a decimal library.

**Plausible wrong approach:** Assuming every currency uses two decimal places fails because some use zero or three, so a fixed 100 divisor is wrong.

**How to verify:** Your answer lists at least one currency scale other than two and explains which extra rule it needs.

## Reference comparison

Open `courses/web-development/solutions/web-033_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
