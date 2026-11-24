# r-033: reference reasoning

Use the [complete reference](r-033_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The lookup adds exactly one category per fact and retains the original line order. Key validation makes the first-match behavior safe for this contract.

The A fact appears twice. A duplicate-key guard would reject the dimension before the incorrect total becomes a report.

## Explained practice

### Exercise 1

Predict the category sequence for fact keys B, A, B.

Home, Paper, Home.

**Approach:** Look up each fact key's position with `match(facts$product, dimension$product)` and index the categories with it.

**Why it holds here:** B is at position 2 and A at position 1, so the index is 2, 1, 2 and the categories are Home, Paper, Home in fact order. The amounts are untouched, so the total stays 60.

**Tempting mistake:** Using merge and then copying its category column back onto facts by position. merge sorts by product, giving Paper, Home, Home, which puts the wrong category on the first two facts.

**Verify:** `identical(result$category, c("Home", "Paper", "Home"))` returns TRUE, and `sum(result$amount)` returns 60.

### Exercise 2

Add an unmatched key C.

The missing index must be rejected or retained under an explicit diagnostic policy.

**Approach:** Stop when any index is NA, or keep the row under a declared policy, such as an explicit unknown category, and count it.

**Why it holds here:** C has no entry in the dimension, so match returns NA for it. lookup's `stopifnot(!anyNA(index))` rejects the batch, so the record cannot vanish or quietly lose its category.

**Tempting mistake:** Indexing `dimension$category[index]` without the check. The C row gets category NA, so a later summary by category files its amount under NA, and an inner merge would drop it.

**Verify:** The tryCatch around the C lookup returns TRUE, showing the unmatched key raised an error.

### Exercise 3

Write a many-to-one join guard.

No duplicated dimension key and no unmatched required fact key are admitted.

**Approach:** Before matching, require the dimension key to have no NA and no duplicates; after matching, require every fact to have a match.

**Why it holds here:** match never adds rows, but with two A entries it silently takes the first one. Adding `dimension[1, ]` again creates that conflict, and the uniqueness check rejects it instead of letting row order decide.

**Tempting mistake:** Trusting match because it cannot multiply facts. If the two A rows carried different categories, the answer would change whenever the dimension was re-sorted, and nothing would report it.

**Verify:** The tryCatch around the duplicated dimension returns TRUE, and `anyDuplicated(dimension$product)` returns 0 for the clean table.

### Exercise 4

Diagnose a total rising after a dimension join.

The join may have multiplied fact records.

**Approach:** Check the dimension's key for duplicates and count matches per key before changing any aggregate.

**Why it holds here:** In the second example A appears twice, so merge produces two rows for the single A fact and the total rises from 30 to 40. The extra 10 is exactly A's amount, which identifies the key.

**Tempting mistake:** Calling `unique()` on the joined rows. The two A rows have different categories, X and Y, so neither is removed and the inflated total remains.

**Verify:** `anyDuplicated(bad_dimension$product)` returns 2, and `nrow(joined)` returns 3 against 2 facts.

### Exercise 5

Join an empty fact table.

No facts or additive amounts should be created.

**Approach:** Run the same lookup on `facts[integer(0), , drop = FALSE]` and return a zero row table with product, amount and category.

**Why it holds here:** match on a zero length key returns `integer(0)`, which has no NA, and assigning a zero length category column keeps the schema. No amounts are created, so the total is 0.

**Tempting mistake:** Returning the empty input unchanged or `data.frame()`. The category column is missing, so binding this batch to a nonempty one fails because the names differ.

**Verify:** `nrow(empty)` returns 0, and `names(empty)` returns "product" "amount" "category".

### Exercise 6

Transfer the checks to SQL or Spark.

Declare join keys, expected matches, unmatched policy and before/after reconciliation.

**Approach:** Write the same contract for the other engine: a unique dimension key, a left join, a count of unmatched facts, and row and amount totals compared before and after.

**Why it holds here:** Cardinality does not depend on the engine. A duplicated key multiplies fact rows in SQL and Spark just as merge did in R, and an unmatched key is dropped by an inner join in all three.

**Tempting mistake:** Relying on a plain JOIN, which is an inner join in SQL. It drops C exactly as merge did, and the total check is the only signal.

**Verify:** A query that groups the dimension by product with `HAVING COUNT(*) > 1` returns zero rows, and the joined amount total returns 60.

## What the checks establish

The reference makes 5 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
