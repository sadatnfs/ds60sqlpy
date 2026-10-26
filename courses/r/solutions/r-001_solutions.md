# r-001: reference reasoning

Use the [complete reference](r-001_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

Both inputs are present in the script. The printed 18 is the computed total, while stopifnot states the expected arithmetic result.

total contains the earlier result. Changing quantity does not convert total into a spreadsheet formula that reevaluates itself.

## Explained practice

### Exercise 1

Predict 4 * 7 before running it.

The result is 28.

**Expected evidence:** The result is 28.

### Exercise 2

Change the invoice quantity to five.

The result is 30 at unit price six.

**Expected evidence:** The result is 30 at unit price six.

### Exercise 3

Construct a script for subtotal 20 plus fee 3.

The printed total is 23.

**Expected evidence:** The printed total is 23.

### Exercise 4

Diagnose why changing quantity after total leaves total unchanged.

Reevaluate the arithmetic to obtain the new total.

**Expected evidence:** Reevaluate the arithmetic to obtain the new total.

### Exercise 5

Check an invoice with zero quantity.

The total is zero, with no missing input.

**Expected evidence:** The total is zero, with no missing input.

### Exercise 6

Separate a saved draft from a checked result.

Saving retains source; running evaluates it; assertions check declared properties.

**Expected evidence:** Saving retains source; running evaluates it; assertions check declared properties.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
