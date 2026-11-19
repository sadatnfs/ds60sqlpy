# web-033: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-033.md`.

## Exercise 1: Predict 125 cents times three units.

**Expected answer:** The result is 375 cents.

**Why:** 125 × 3 is 375 cents; keeping integer minor units avoids binary floating-point rounding.

## Exercise 2: Add a fixed 50-cent fee with a named intermediate value.

**Expected evidence:** The new total is 425 cents and the unit remains explicit.

**Why:** A named intermediate keeps the unit visible: 375 + 50 = 425 cents.

## Exercise 3: Implement a bounded quantity calculation and cents formatter.

**Expected evidence:** Valid quantities produce exact integer totals and two-digit fractional display.

**Why:** intdiv gives whole units and % gives the remainder, which str_pad formats as two digits.

## Exercise 4: Diagnose a concatenation expression that hides arithmetic grouping.

**Expected answer:** Use parentheses or intermediate variables to express the intended computation.

**Why:** Since PHP 8, + and - bind tighter than ., but explicit parentheses or an intermediate variable still make the intended grouping obvious to readers.

## Exercise 5: Reject a negative quantity and test zero.

**Expected evidence:** Invalid negative input is rejected; zero follows the declared contract.

**Why:** A negative quantity has no meaning for a purchase, while zero is a valid empty order unless the contract says otherwise.

## Exercise 6: Explain when integer cents are insufficient.

**Expected answer:** Different currency scales, huge ranges, exchange rates or fractional-unit pricing require an explicit broader numeric policy.

**Why:** Currencies with three decimal places, exchange rates and fractional unit prices need an explicit scale or a decimal library.

## Reference comparison

Open `courses/web-development/solutions/web-033_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
