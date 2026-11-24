# r-001: reference reasoning

Use the [complete reference](r-001_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

Both inputs are present in the script. The printed 18 is the computed total, while stopifnot states the expected arithmetic result.

total contains the earlier result. Changing quantity does not convert total into a spreadsheet formula that reevaluates itself.

## Explained practice

### Exercise 1

Predict 4 * 7 before running it.

The result is 28.

**Approach:** Write the prediction, 28, in a comment or your notes before running anything, then evaluate `4 * 7` and compare. The reference turns that comparison into `stopifnot(4 * 7 == 28)` so the expectation lives in the script instead of in memory.

**Why it holds here:** Both operands are small whole numbers stored as doubles, and 28 is represented exactly, so plain `==` is a fair check here and no tolerance is needed.

**Tempting mistake:** Running first and then copying the printed 28 into the prediction removes the evidence the task exists to collect. A typo such as `4 + 7` would print 11, and only a prediction made beforehand exposes that the operator, not the arithmetic, was wrong.

**Verify:** `print(4 * 7)` shows `[1] 28`. Temporarily change the assertion to `== 27` and the run stops with `4 * 7 == 27 is not TRUE`, which shows the check is live rather than decorative.

### Exercise 2

Change the invoice quantity to five.

The result is 30 at unit price six.

**Approach:** Edit the input line to `quantity <- 5` above the line that computes total, then rerun so `total <- quantity * unit_price` sees the new binding. The reference asserts `total == 30`.

**Why it holds here:** unit_price stays 6, so the product is 5 times 6, or 30. Because each Run is a fresh process evaluated top to bottom, the edited line is the only quantity R knows about on that run.

**Tempting mistake:** Adding `quantity <- 5` after total was already computed leaves total at the old 3 times 6 product, 18. That is the exact trap shown in Example 2: the input changed but the stored result did not.

**Verify:** `print(total)` shows `[1] 30`. As a second probe, set unit_price to 7 and confirm the printed total becomes 35, which proves both inputs flow into the result.

### Exercise 3

Construct a script for subtotal 20 plus fee 3.

The printed total is 23.

**Approach:** Bind `subtotal <- 20` and `fee <- 3` as separate named inputs, add them, print the sum and assert it. The reference checks `subtotal + fee == 23`.

**Why it holds here:** Naming both inputs keeps the script self-contained: anyone reading it can see the 23 came from 20 and 3 in this run, not from a value typed into yesterday's console.

**Tempting mistake:** Writing `print(23)` or `print("23")` shows the right digits without performing the addition. The second is also a character string, so `"23" + 1` fails with a non-numeric argument error the moment later code treats it as a number.

**Verify:** The run prints `[1] 23` and the stopifnot line passes. Change fee to 4 and the output should become 24; if it stays 23, the print is not reading the computed sum.

### Exercise 4

Diagnose why changing quantity after total leaves total unchanged.

Reevaluate the arithmetic to obtain the new total.

**Approach:** Read the script from the top and locate the line that created total. That line bound total to the product of the inputs at that moment; later lines that rebind quantity change only quantity.

**Why it holds here:** R stores the value an expression produced, not the expression. In the reference, quantity moves from 5 to 8 after total was computed, and `stopifnot(total == 30, quantity * unit_price == 48)` asserts the stale 30 and the fresh 48 side by side.

**Tempting mistake:** Treating total like a spreadsheet cell that references quantity. A learner who adds a second `print(total)` and sees 30 again may suspect the print is stale, but the binding is what stayed fixed.

**Verify:** Re-evaluate `total <- quantity * unit_price` after the change and print it: total becomes 48 for quantity 8, and the old assertion `total == 30` would now fail.

### Exercise 5

Check an invoice with zero quantity.

The total is zero, with no missing input.

**Approach:** Set `quantity <- 0` and compute `quantity * unit_price`. The reference asserts the product is 0 and then prints it as current_total.

**Why it holds here:** Zero is a measured count here, meaning nothing was ordered, so 0 times 6 equals 0 is the correct invoice total. It is an ordinary number, and no value is missing.

**Tempting mistake:** Recording the empty order as `NA` changes its meaning to unknown. `NA * 6` is `NA`, and `stopifnot(NA * 6 == 0)` stops the script because the comparison is NA instead of TRUE, so an empty order would look like a broken run.

**Verify:** The reference's final print shows current_total 0 beside total_from_prior_calculation 30, and the run still reaches `r-001 reference checks passed`.

### Exercise 6

Separate a saved draft from a checked result.

Saving retains source; running evaluates it; assertions check declared properties.

**Approach:** Save the pad without running it, then run it, and compare what each action produced. Saving stores source text; only a Run evaluates that text, prints output and reaches the marker line.

**Why it holds here:** Each Run starts a fresh R process, so the saved file is the complete input to the next run. The five stopifnot calls in this reference are the declared properties a run actually checks.

**Tempting mistake:** Treating a saved file, or output left over from an earlier run, as proof the current source works. If you change unit_price after your last run, the old printed 18 describes code that no longer exists in the pad.

**Verify:** Change one input, save without running and confirm no new output appears. Then run and confirm `r-001 reference checks passed` prints only when all five assertions hold.

## What the checks establish

The reference makes 5 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
